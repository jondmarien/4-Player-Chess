import redis.asyncio as redis
import json
import os
from typing import Dict, List
from fastapi import WebSocket

class GameManager:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, game_id: str, player_id: str):
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
        self.active_connections[game_id].append(websocket)
        
        # Store player connection in Redis
        await self.redis_client.hset(f"game:{game_id}:players", player_id, "connected")
    
    async def disconnect(self, websocket: WebSocket, game_id: str, player_id: str):
        if game_id in self.active_connections:
            self.active_connections[game_id].remove(websocket)
        
        # Update Redis
        await self.redis_client.hset(f"game:{game_id}:players", player_id, "disconnected")
    
    async def broadcast_to_game(self, game_id: str, message: dict):
        if game_id in self.active_connections:
            for connection in self.active_connections[game_id]:
                await connection.send_json(message)
    
    async def get_game_state(self, game_id: str):
        game_data = await self.redis_client.hgetall(f"game:{game_id}:state")
        return {k.decode(): v.decode() for k, v in game_data.items()} if game_data else None
    
    async def set_game_state(self, game_id: str, game_state: dict):
        await self.redis_client.hset(f"game:{game_id}:state", mapping={
            k: json.dumps(v) if isinstance(v, (dict, list)) else str(v)
            for k, v in game_state.items()
        })

game_manager = GameManager()
