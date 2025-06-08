from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..services.websocket_manager import game_manager
import json

router = APIRouter()

@router.websocket("/ws/game/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    # Get player info from query params
    player_id = websocket.query_params.get("player_id", "anonymous")
    
    await game_manager.connect(websocket, game_id, player_id)
    
    try:
        # Send current game state to new player
        current_state = await game_manager.get_game_state(game_id)
        if current_state:
            await websocket.send_json({
                "type": "game_state",
                "data": current_state
            })
        
        # Listen for messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message["type"] == "move":
                # TODO: Validate and process move
                await game_manager.broadcast_to_game(game_id, {
                    "type": "move_made",
                    "player": player_id,
                    "move": message["data"]
                })
            
    except WebSocketDisconnect:
        await game_manager.disconnect(websocket, game_id, player_id)
        await game_manager.broadcast_to_game(game_id, {
            "type": "player_disconnected",
            "player": player_id
        })
