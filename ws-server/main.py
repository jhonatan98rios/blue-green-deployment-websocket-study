import asyncio
import os
import json
import signal
from typing import Dict, TypedDict

import redis
import websockets
from aiohttp import web 

# Constants and configuration
PLAYER_COLOR: str = os.getenv("PLAYER_COLOR", "green")  # "blue" or "green"
PORT: int = 8000
REDIS_HOST: str = 'redis-master'

# TypedDict for player data
class PlayerData(TypedDict):
    x: float
    y: float
    color: str

# Initialize Redis client (blocking) for PoC
redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

# Global state to track shutdown
is_shutting_down = False
connected_clients = set()

async def player_handler(websocket: websockets.WebSocketServerProtocol, path: str) -> None:
    """
    Main WebSocket handler: receives movement deltas, updates position,
    stores state in Redis, and echoes full players dict.
    """
    global is_shutting_down
    
    if is_shutting_down:
        await websocket.close(code=1001, reason="Server is shutting down")
        return
    
    
    sid: str = str(id(websocket))  # Session ID key--OK for PoC
    x, y = 100.0, 100.0            # Starting position for new players

    # Store initial state in Redis
    initial_data: PlayerData = {'x': x, 'y': y, 'color': PLAYER_COLOR}
    redis_client.hset('players', sid, json.dumps(initial_data))

    try:
        async for message in websocket:
            # Parse movement delta
            data: Dict[str, float] = json.loads(message)
            dx: float = data.get('dx', 0.0)
            dy: float = data.get('dy', 0.0)

            # Compute new position
            x += dx
            y += dy

            # Update Redis state
            player_data: PlayerData = {'x': x, 'y': y, 'color': PLAYER_COLOR}
            redis_client.hset('players', sid, json.dumps(player_data))

            # Fetch all players from Redis
            all_players_raw: Dict[str, str] = redis_client.hgetall('players')
            # Relay to client
            await websocket.send(json.dumps(all_players_raw))

    except websockets.ConnectionClosed:
        print(f"Player {sid} disconnected.")
        
    finally:
        redis_client.hdel('players', sid)
        connected_clients.remove(websocket)
        

async def shutdown(server, runner):
    print("Gracefully shutting down...")

    server.close()
    await server.wait_closed()

    timeout = 3600  # 1 hour

    async def wait_for_clients():
        while connected_clients:
            print(f"Waiting for {len(connected_clients)} clients to disconnect...")
            await asyncio.sleep(5)

    try:
        await asyncio.wait_for(wait_for_clients(), timeout=timeout)
    except asyncio.TimeoutError:
        print("Forcefully shutting down after timeout.")

    await asyncio.gather(*(client.close() for client in connected_clients))
    if runner:
        await runner.cleanup()
    print("Shutdown complete.")


# NEW: health check handler
async def healthz_handler(request):
    if is_shutting_down:
        return web.Response(status=503, text="Shutting down")
    return web.Response(status=200, text="OK")


async def main() -> None:
    """
    Entry point: starts WebSocket server with two handlers.
    """
    
    loop = asyncio.get_event_loop()
    stop_event = asyncio.Event()
    
    def handle_signal():
        global is_shutting_down
        is_shutting_down = True
        stop_event.set()
        
    # Register signal handlers
    loop.add_signal_handler(signal.SIGINT, handle_signal)
    loop.add_signal_handler(signal.SIGTERM, handle_signal)
    
    # Start WebSocket server
    server = await websockets.serve(
        ws_handler=player_handler,
        host="",
        port=PORT,
        ping_interval=None  # disable built-in pings for simplicity
    )
    
    # Start HTTP health check server (on same or separate port)
    app = web.Application()
    app.router.add_get("/healthz", healthz_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT + 1)  # e.g. 8001
    await site.start()

    print(f"WebSocket server ({PLAYER_COLOR}) listening on port {PORT}")
    await stop_event.wait()
    await shutdown(server, runner)
    print("WebSocket server shut down gracefully.")

if __name__ == "__main__":
    # Run the main coroutine
    asyncio.run(main())