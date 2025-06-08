import redis.asyncio as redis
import json
import os
from typing import Dict, List, Optional
from fastapi import WebSocket

class GameManager:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.player_connections: Dict[str, Dict[str, WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, game_id: str, player_id: str):
        """Connect a player to a game room"""
        await websocket.accept()
        
        # Add to active connections
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
        self.active_connections[game_id].append(websocket)
        
        # Track player-specific connection
        if game_id not in self.player_connections:
            self.player_connections[game_id] = {}
        self.player_connections[game_id][player_id] = websocket
        
        # Update Redis
        await self.redis_client.hset(f"game:{game_id}:players", player_id, "connected")
        
        print(f"✅ Player {player_id} connected to game {game_id}")
    
    async def disconnect(self, websocket: WebSocket, game_id: str, player_id: str):
        """Disconnect a player from a game room"""
        # Remove from active connections
        if game_id in self.active_connections:
            if websocket in self.active_connections[game_id]:
                self.active_connections[game_id].remove(websocket)
        
        # Remove player connection
        if game_id in self.player_connections:
            if player_id in self.player_connections[game_id]:
                del self.player_connections[game_id][player_id]
        
        # Update Redis
        await self.redis_client.hset(f"game:{game_id}:players", player_id, "disconnected")
        
        print(f"❌ Player {player_id} disconnected from game {game_id}")
    
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
