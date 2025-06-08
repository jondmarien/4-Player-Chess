from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict, List
import json
import asyncio
from ..services.websocket_manager import GameManager

router = APIRouter()

# Global game manager instance
game_manager = GameManager()

@router.websocket("/ws/game/{game_id}")
async def websocket_game_endpoint(websocket: WebSocket, game_id: str, player_id: str = Query(...)):
    """WebSocket endpoint for real-time game communication"""
    
    await game_manager.connect(websocket, game_id, player_id)
    
    try:
        # Send initial game state
        await websocket.send_json({
            "type": "connection_established",
            "player_id": player_id,
            "game_id": game_id,
            "message": f"Connected to game {game_id} as {player_id}"
        })
        
        # Send current game state if exists
        game_state = await game_manager.get_game_state(game_id)
        if game_state:
            await websocket.send_json({
                "type": "game_state",
                "data": game_state
            })
        else:
            # Initialize new game state
            initial_state = {
                "game_id": game_id,
                "current_player": "red",
                "scores": {"red": 0, "blue": 0, "yellow": 0, "green": 0},
                "board": initialize_board(),
                "moves": [],
                "status": "waiting"
            }
            await game_manager.set_game_state(game_id, initial_state)
            await websocket.send_json({
                "type": "game_state", 
                "data": initial_state
            })
        
        # Notify other players
        await game_manager.broadcast_to_game(game_id, {
            "type": "player_joined",
            "player_id": player_id,
            "message": f"{player_id} joined the game"
        }, exclude=websocket)
        
        # Listen for messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message["type"] == "move":
                await handle_move(game_id, player_id, message["data"])
            elif message["type"] == "chat":
                await game_manager.broadcast_to_game(game_id, {
                    "type": "chat_message",
                    "player": player_id,
                    "message": message["data"]["text"]
                })
            elif message["type"] == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        await game_manager.disconnect(websocket, game_id, player_id)
        await game_manager.broadcast_to_game(game_id, {
            "type": "player_disconnected",
            "player_id": player_id,
            "message": f"{player_id} left the game"
        })
    except Exception as e:
        print(f"WebSocket error: {e}")
        await game_manager.disconnect(websocket, game_id, player_id)

async def handle_move(game_id: str, player_id: str, move_data: dict):
    """Handle a chess move"""
    # Basic move validation and processing
    move_result = {
        "type": "move_made",
        "player": player_id,
        "from": move_data.get("from"),
        "to": move_data.get("to"),
        "piece": move_data.get("piece"),
        "timestamp": json.dumps({"timestamp": "now"}),
        "points": 0  # Calculate based on Chaturaji rules
    }
    
    # Broadcast move to all players
    await game_manager.broadcast_to_game(game_id, move_result)
    
    # Update game state
    game_state = await game_manager.get_game_state(game_id)
    if game_state:
        game_state["moves"].append(move_result)
        # Switch to next player (Red -> Blue -> Yellow -> Green -> Red)
        current_player = game_state.get("current_player", "red")
        next_players = {"red": "blue", "blue": "yellow", "yellow": "green", "green": "red"}
        game_state["current_player"] = next_players.get(current_player, "red")
        
        await game_manager.set_game_state(game_id, game_state)

def initialize_board():
    """Initialize a basic 4-player chess board"""
    return {
        "squares": {
            f"{chr(97+col)}{8-row}": None for row in range(8) for col in range(8)
        },
        "pieces": {
            # Basic piece setup - will enhance later
            "a8": {"type": "rook", "color": "yellow"},
            "h8": {"type": "rook", "color": "yellow"},
            "a1": {"type": "rook", "color": "red"},
            "h1": {"type": "rook", "color": "red"},
        }
    }
