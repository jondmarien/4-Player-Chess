from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict, List
import json
import asyncio
from ..services.websocket_manager import GameManager
from ..services.game_state import GameStateManager

router = APIRouter()

# Global game manager instance
game_manager = GameManager()

@router.websocket("/ws/game/{game_id}")
async def websocket_game_endpoint(websocket: WebSocket, game_id: str, player_id: str = Query(...)):
    """Enhanced WebSocket endpoint with proper disconnect handling"""
    
    await game_manager.connect(websocket, game_id, player_id)
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection_established",
            "player_id": player_id,
            "game_id": game_id,
            "message": f"Connected to game {game_id} as {player_id}"
        })
        
        # Check if this player is the host/creator
        game_data = GameStateManager.get_game(game_id)
        is_host = game_data and game_data.get('host') == player_id
        
        # Send current game state
        if game_data:
            await websocket.send_json({
                "type": "game_state",
                "data": game_data,
                "is_host": is_host
            })
        
        # Notify other players
        await game_manager.broadcast_to_game(game_id, {
            "type": "player_joined",
            "player_id": player_id,
            "is_host": is_host,
            "message": f"{player_id} joined the game"
        }, exclude=websocket)
        
        # Main message loop with enhanced disconnect detection
        while True:
            try:
                # Use asyncio.wait_for to detect stale connections
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
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
                elif message["type"] == "leave_game":
                    # Voluntary leave
                    await handle_player_leave(game_id, player_id, is_host, voluntary=True)
                    break
                    
            except asyncio.TimeoutError:
                # Send ping to check if connection is alive
                try:
                    await websocket.send_json({"type": "ping"})
                except:
                    # Connection is dead, break out of loop
                    print(f"💀 Detected dead connection for {player_id} in game {game_id}")
                    break
                    
    except WebSocketDisconnect as e:
        print(f"🔌 WebSocket disconnect: {player_id} from game {game_id} (code: {e.code})")
        await handle_player_leave(game_id, player_id, is_host, voluntary=False)
        
    except Exception as e:
        print(f"❌ WebSocket error for {player_id}: {e}")
        await handle_player_leave(game_id, player_id, is_host, voluntary=False)
        
    finally:
        await game_manager.disconnect(websocket, game_id, player_id)

async def handle_player_leave(game_id: str, player_id: str, is_host: bool, voluntary: bool):
    """Enhanced player leave handling with host migration"""
    
    game_data = GameStateManager.get_game(game_id)
    if not game_data:
        return
    
    print(f"🚪 Handling leave: {player_id} from game {game_id} (host: {is_host}, voluntary: {voluntary})")
    
    if is_host:
        # Host is leaving - need special handling
        remaining_players = [p for p in game_data.get('players', []) if p.get('name') != player_id]
        
        if len(remaining_players) == 0:
            # No players left, delete the game entirely
            GameStateManager.remove_game(game_id)
            print(f"🗑️ Deleted empty game {game_id} after host left")
            
        elif len(remaining_players) == 1:
            # Only one player left, offer to migrate or end game
            new_host = remaining_players[0]['name']
            game_data['host'] = new_host
            GameStateManager.update_game(game_id, game_data)
            
            await game_manager.broadcast_to_game(game_id, {
                "type": "host_migration",
                "new_host": new_host,
                "old_host": player_id,
                "message": f"{new_host} is now the host"
            })
            print(f"👑 Migrated host from {player_id} to {new_host} in game {game_id}")
            
        else:
            # Multiple players left, migrate to first remaining player
            new_host = remaining_players[0]['name']
            game_data['host'] = new_host
            
            # Remove the leaving player
            game_data['players'] = remaining_players
            GameStateManager.update_game(game_id, game_data)
            
            await game_manager.broadcast_to_game(game_id, {
                "type": "host_migration",
                "new_host": new_host,
                "old_host": player_id,
                "remaining_players": len(remaining_players),
                "message": f"Host {player_id} left. {new_host} is now the host"
            })
            print(f"👑 Host migration: {player_id} → {new_host}, {len(remaining_players)} players remain")
    else:
        # Regular player leaving
        GameStateManager.remove_player_from_game(game_id, player_id)
        
        await game_manager.broadcast_to_game(game_id, {
            "type": "player_left",
            "player_id": player_id,
            "message": f"{player_id} left the game"
        })

async def handle_move(game_id: str, player_id: str, move_data: dict):
    """Handle a chess move with validation"""
    # Basic move validation and processing
    move_result = {
        "type": "move_made",
        "player": player_id,
        "from": move_data.get("from"),
        "to": move_data.get("to"),
        "piece": move_data.get("piece"),
        "timestamp": "now",
        "points": 0  # Calculate based on rules
    }
    
    # Broadcast move to all players
    await game_manager.broadcast_to_game(game_id, move_result)
    
    # Update game state
    game_state = await game_manager.get_game_state(game_id)
    if game_state:
        if "moves" not in game_state:
            game_state["moves"] = []
        game_state["moves"].append(move_result)
        
        # Switch to next player
        current_player = game_state.get("current_player", "red")
        next_players = {"red": "blue", "blue": "yellow", "yellow": "green", "green": "red"}
        game_state["current_player"] = next_players.get(current_player, "red")
        
        await game_manager.set_game_state(game_id, game_state)
