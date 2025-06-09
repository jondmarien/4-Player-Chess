import redis.asyncio as redis
import json
import os
from typing import Dict, List, Optional
from fastapi import WebSocket
from ..services.game_state import GameStateManager, active_games

class GameManager:
    def __init__(self):
        try:
            self.redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}")
            self.redis_client = None
        
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.player_connections: Dict[str, Dict[str, WebSocket]] = {}
        
        # Track player-to-game mapping for cleanup
        self.player_game_mapping: Dict[str, str] = {}
    
    async def connect(self, websocket: WebSocket, game_id: str, player_id: str):
        """Connect a player to a game room with proper tracking"""
        await websocket.accept()
        
        # Add to active connections
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
        self.active_connections[game_id].append(websocket)
        
        # Track player-specific connection
        if game_id not in self.player_connections:
            self.player_connections[game_id] = {}
        self.player_connections[game_id][player_id] = websocket
        
        # Track player-to-game mapping for cleanup
        self.player_game_mapping[player_id] = game_id
        
        # Update game state - add player if not already in game
        game_data = GameStateManager.get_game(game_id)
        if game_data:
            existing_player = next((p for p in game_data.get('players', []) if p.get('name') == player_id), None)
            if not existing_player:
                # Add new player to game
                colors = ["red", "blue", "yellow", "green"]
                taken_colors = [p.get("color") for p in game_data.get('players', [])]
                available_colors = [c for c in colors if c not in taken_colors]
                
                if available_colors:
                    new_player = {
                        "name": player_id,
                        "color": available_colors[0],
                        "connected": True
                    }
                    game_data['players'].append(new_player)
                    GameStateManager.update_game(game_id, game_data)
            else:
                # Mark existing player as connected
                existing_player['connected'] = True
                GameStateManager.update_game(game_id, game_data)
        
        # Try to update Redis
        if self.redis_client:
            try:
                await self.redis_client.hset(f"game:{game_id}:players", player_id, "connected")
            except Exception as e:
                print(f"⚠️ Redis write failed: {e}")
        
        print(f"✅ Player {player_id} connected to game {game_id}")
    
    async def disconnect(self, websocket: WebSocket, game_id: str, player_id: str):
        """Properly disconnect player and clean up game state"""
        
        # Remove from active connections
        if game_id in self.active_connections:
            if websocket in self.active_connections[game_id]:
                self.active_connections[game_id].remove(websocket)
            
            # Clean up empty game connections
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]
        
        # Remove player connection
        if game_id in self.player_connections:
            if player_id in self.player_connections[game_id]:
                del self.player_connections[game_id][player_id]
            
            # Clean up empty game player connections
            if not self.player_connections[game_id]:
                del self.player_connections[game_id]
        
        # Remove from player-game mapping
        if player_id in self.player_game_mapping:
            del self.player_game_mapping[player_id]
        
        # CRITICAL: Remove player from game state
        game_data = GameStateManager.get_game(game_id)
        if game_data:
            # Remove player from players list
            original_count = len(game_data.get('players', []))
            game_data['players'] = [p for p in game_data.get('players', []) if p.get('name') != player_id]
            new_count = len(game_data['players'])
            
            print(f"🔄 Player cleanup: {original_count} -> {new_count} players in game {game_id}")
            
            # If no players left, remove the game entirely
            if new_count == 0:
                GameStateManager.remove_game(game_id)
                print(f"🗑️ Removed empty game {game_id}")
            else:
                GameStateManager.update_game(game_id, game_data)
        
        # Update Redis
        if self.redis_client:
            try:
                await self.redis_client.hset(f"game:{game_id}:players", player_id, "disconnected")
            except Exception as e:
                print(f"⚠️ Redis update failed: {e}")
        
        print(f"❌ Player {player_id} disconnected from game {game_id}")
    
    async def cleanup_stale_connections(self):
        """Periodic cleanup of stale connections"""
        for game_id in list(self.active_connections.keys()):
            # Check for broken WebSocket connections
            active_sockets = []
            for ws in self.active_connections[game_id]:
                try:
                    await ws.ping()
                    active_sockets.append(ws)
                except:
                    # WebSocket is dead, don't include it
                    pass
            
            self.active_connections[game_id] = active_sockets
            
            # Clean up empty games
            if not active_sockets:
                del self.active_connections[game_id]
                if game_id in self.player_connections:
                    del self.player_connections[game_id]
    
    async def broadcast_to_game(self, game_id: str, message: dict, exclude: Optional[WebSocket] = None):
        """Broadcast message to all players in a game"""
        if game_id in self.active_connections:
            disconnected = []
            for websocket in self.active_connections[game_id]:
                if websocket != exclude:
                    try:
                        await websocket.send_json(message)
                    except:
                        disconnected.append(websocket)
            
            # Clean up disconnected websockets
            for ws in disconnected:
                if ws in self.active_connections[game_id]:
                    self.active_connections[game_id].remove(ws)
    
    async def send_to_player(self, game_id: str, player_id: str, message: dict):
        """Send message to specific player"""
        if game_id in self.player_connections:
            if player_id in self.player_connections[game_id]:
                try:
                    await self.player_connections[game_id][player_id].send_json(message)
                except:
                    # Connection is dead, remove it
                    del self.player_connections[game_id][player_id]
    
    async def get_game_state(self, game_id: str) -> Optional[dict]:
        """Get current game state from Redis"""
        try:
            game_data = await self.redis_client.hgetall(f"game:{game_id}:state")
            if game_data:
                # Convert bytes to strings and parse JSON where needed
                result = {}
                for key, value in game_data.items():
                    key_str = key.decode() if isinstance(key, bytes) else key
                    value_str = value.decode() if isinstance(value, bytes) else value
                    
                    # Try to parse JSON for complex data
                    try:
                        result[key_str] = json.loads(value_str)
                    except:
                        result[key_str] = value_str
                
                return result
            return None
        except Exception as e:
            print(f"Error getting game state: {e}")
            return None
    
    async def set_game_state(self, game_id: str, game_state: dict):
        """Set game state in Redis"""
        try:
            # Convert complex data to JSON strings
            redis_data = {}
            for key, value in game_state.items():
                if isinstance(value, (dict, list)):
                    redis_data[key] = json.dumps(value)
                else:
                    redis_data[key] = str(value)
            
            await self.redis_client.hset(f"game:{game_id}:state", mapping=redis_data)
        except Exception as e:
            print(f"Error setting game state: {e}")
