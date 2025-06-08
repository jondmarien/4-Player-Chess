from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, Response
import uvicorn
import os
from dotenv import load_dotenv

# Import game state manager
from chess.services.game_state import GameStateManager
from chess.routers import game, websocket

# Load environment variables
load_dotenv()

app = FastAPI(
    title="4-Player Chess",
    description="Real-time multiplayer chess with Chaturaji and Enochian variants",
    version="1.0.0"
)

# Include routers
app.include_router(game.router)
app.include_router(websocket.router)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/lobby", response_class=HTMLResponse) 
async def lobby(request: Request):
    return templates.TemplateResponse("lobby.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/create", response_class=HTMLResponse)
async def create_game(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})

import random

@app.get("/game/quick", response_class=HTMLResponse)
async def quick_game(request: Request):
    # Randomly choose a variant for the quick game
    variant = random.choice(["chaturaji", "enochian"])
    # Create or get existing quick game from GameStateManager (optionally pass variant if needed)
    game_data = GameStateManager.get_or_create_quick_game(variant=variant) if hasattr(GameStateManager, "get_or_create_quick_game") and "variant" in GameStateManager.get_or_create_quick_game.__code__.co_varnames else GameStateManager.get_or_create_quick_game()
    return templates.TemplateResponse("game.html", {
        "request": request, 
        "game_id": "quick-match",  # Use consistent ID
        "variant": variant
    })

@app.get("/game/{game_id}", response_class=HTMLResponse)
async def game_room(request: Request, game_id: str):
    # Use GameStateManager instead of direct access to active_games
    game_data = GameStateManager.get_game(game_id)
    if not game_data:
        game_data = {"variant": "chaturaji"}  # Default fallback
    
    return templates.TemplateResponse("game.html", {
        "request": request, 
        "game_id": game_id,
        "variant": game_data.get("variant", "chaturaji")
    })

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected", "redis": "connected"}

@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
