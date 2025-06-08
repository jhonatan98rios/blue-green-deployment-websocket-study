import asyncio
import json
import sys
import pygame
import websockets
from typing import Dict, Tuple, TypedDict

# --- Constants ---
WIDTH, HEIGHT = 800, 600
PLAYER_SIZE = 20
SPEED = 5
SERVER_URL = "ws://127.0.0.1:58168"

# --- Typing ---
class Player(TypedDict):
    x: float
    y: float
    color: str

PlayerDict = Dict[str, Player]

# --- Utility Functions ---
async def handle_input(keys: Tuple[bool, ...]) -> Dict[str, float]:
    """Translate keyboard input into movement deltas."""
    dx = dy = 0.0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        dx -= SPEED
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        dx += SPEED
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        dy -= SPEED
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        dy += SPEED
    return {"dx": dx, "dy": dy}

def draw_players(screen: pygame.Surface, players: PlayerDict) -> None:
    """Render all players as colored rectangles."""
    for player_data in players.values():
        x = int(player_data["x"])
        y = int(player_data["y"])
        color = (0, 0, 255) if player_data["color"] == "blue" else (0, 255, 0)
        pygame.draw.rect(screen, color, pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE))

async def safe_connect(url: str) -> websockets.WebSocketClientProtocol:
    """Try connecting to the server with retry logic."""
    for attempt in range(5):
        try:
            return await websockets.connect(url)
        except Exception as e:
            print(f"[Attempt {attempt + 1}] Connection failed: {e}")
            await asyncio.sleep(1)
    print("Could not connect to server after multiple attempts.")
    sys.exit(1)

# --- Game Loop ---
async def game_loop() -> None:
    """Main game loop: handles rendering, input, and communication."""
    ws = await safe_connect(SERVER_URL)
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("WebSocket Game")
    clock = pygame.time.Clock()

    players: PlayerDict = {}
    running = True

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    await ws.close()
                    running = False

            keys = pygame.key.get_pressed()
            delta = await handle_input(keys)
            await ws.send(json.dumps(delta))

            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=1)
                raw_data: Dict[str, str] = json.loads(msg)
                players = {
                    sid: json.loads(info)
                    for sid, info in raw_data.items()
                }
            except (asyncio.TimeoutError, websockets.ConnectionClosed) as e:
                print(f"Connection closed: {e}")
                break
            except Exception as e:
                print(f"Error receiving data: {e}")
                continue

            screen.fill((0, 0, 0))  # Clear screen
            draw_players(screen, players)
            pygame.display.flip()
            clock.tick(60)

    finally:
        pygame.quit()

# --- Entrypoint ---
if __name__ == "__main__":
    asyncio.run(game_loop())
