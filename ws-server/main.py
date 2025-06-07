import asyncio
import os
import json
from typing import Dict, TypedDict

import redis
import websockets

# Constants and configuration
PLAYER_COLOR: str = os.getenv("PLAYER_COLOR", "blue")  # "blue" or "green"
PORT: int = 8000
REDIS_HOST: str = 'redis'

# TypedDict for player data
class PlayerData(TypedDict):
    x: float
    y: float
    color: str

# Initialize Redis client (blocking) for PoC
redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

async def health_check_handler(websocket: websockets.WebSocketServerProtocol, path: str) -> None:
    """
    Simple HTTP GET /health endpoint for Docker healthchecks.
    """
    if path == '/health':
        await websocket.send('OK')
        await websocket.close()

async def player_handler(websocket: websockets.WebSocketServerProtocol, path: str) -> None:
    """
    Main WebSocket handler: receives movement deltas, updates position,
    stores state in Redis, and echoes full players dict.
    """
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
        # On disconnect, remove player from shared state
        pass

    finally:
        redis_client.hdel('players', sid)

async def main() -> None:
    """
    Entry point: starts WebSocket server with two handlers.
    """
    server = await websockets.serve(
        ws_handler=player_handler,
        host="",
        port=PORT,
        ping_interval=None  # disable built-in pings for simplicity
    )

    print(f"WebSocket server ({PLAYER_COLOR}) listening on port {PORT}")
    await asyncio.Future()  # run forever

if __name__ == "__main__":
    # Run the main coroutine
    asyncio.run(main())