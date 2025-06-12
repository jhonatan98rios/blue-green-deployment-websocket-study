import asyncio
import os
import json
import signal
import time
from typing import Dict, TypedDict, Set

import redis
import websockets
from aiohttp import web


class PlayerData(TypedDict):
    x: float
    y: float
    color: str


class WebSocketServerApp:
    def __init__(self):
        self.player_color: str = os.getenv("PLAYER_COLOR", "green")
        self.port: int = 8000
        self.redis_client = redis.Redis(host='redis-master', port=6379, decode_responses=True)
        self.connected_clients: Set[websockets.WebSocketServerProtocol] = set()
        self.is_shutting_down = False
        self.stop_event = asyncio.Event()

    async def player_handler(self, websocket: websockets.WebSocketServerProtocol, path: str):
        if self.is_shutting_down:
            #await websocket.close(code=1001, reason="Server is shutting down")
            print("Connection refused: server is shutting down.")
            return

        self.connected_clients.add(websocket)
        print(f"[JOIN] Client connected. Total: {len(self.connected_clients)}")

        sid = str(id(websocket))
        x, y = 100.0, 100.0
        initial_data: PlayerData = {'x': x, 'y': y, 'color': self.player_color}
        self.redis_client.hset('players', sid, json.dumps(initial_data))

        try:
            async for message in websocket:
                data: Dict[str, float] = json.loads(message)
                dx = data.get('dx', 0.0)
                dy = data.get('dy', 0.0)
                x += dx
                y += dy

                player_data: PlayerData = {'x': x, 'y': y, 'color': self.player_color}
                self.redis_client.hset('players', sid, json.dumps(player_data))

                all_players_raw = self.redis_client.hgetall('players')
                await websocket.send(json.dumps(all_players_raw))
        except websockets.ConnectionClosed:
            print(f"[LEAVE] Player {sid} disconnected.")
        finally:
            self.redis_client.hdel('players', sid)
            self.connected_clients.remove(websocket)
            print(f"[CLEANUP] Client removed. Total: {len(self.connected_clients)}")

    async def shutdown(self, server, runner):
        print("Gracefully shutting down...")
        print(f"Total players connected: {len(self.connected_clients)}")

        self.is_shutting_down = True

        timeout = 3600
        start_time = time.time()

        while self.connected_clients:
            remaining = len(self.connected_clients)
            elapsed = time.time() - start_time
            print(f"Waiting for {remaining} clients (elapsed: {elapsed:.1f}s)")
            if elapsed > timeout:
                print("Timeout reached - forcing shutdown")
                break
            await asyncio.sleep(5)
            
        server.close()
        await server.wait_closed()

        if runner:
            await runner.cleanup()
        print("Shutdown complete.")

    async def healthz_handler(self, request):
        print("Health check received")
        if self.is_shutting_down:
            return web.Response(status=503, text="Shutting down")
        return web.Response(status=200, text="OK")

    async def shutdown_handler(self, request):
        self.is_shutting_down = True
        return web.Response(status=200, text="Shutdown initiated")

    async def handle_signal(self):
        print("Received termination signal")
        self.is_shutting_down = True
        await asyncio.sleep(30)  # Give time for clients to disconnect
        self.stop_event.set()

    async def main(self):
        loop = asyncio.get_event_loop()
        loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(self.handle_signal()))
        loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(self.handle_signal()))

        server = await websockets.serve(
            lambda ws, path: self.player_handler(ws, path),
            host="",
            port=self.port,
            ping_interval=None
        )

        app = web.Application()
        app.router.add_get("/healthz", self.healthz_handler)
        app.router.add_post("/shutdown", self.shutdown_handler)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host="0.0.0.0", port=self.port + 1)
        await site.start()

        print(f"WebSocket server ({self.player_color}) listening on port {self.port}")
        await self.stop_event.wait()
        await self.shutdown(server, runner)


if __name__ == "__main__":
    app = WebSocketServerApp()
    asyncio.run(app.main())

