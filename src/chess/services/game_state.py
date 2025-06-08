"""Shared game state management"""
from typing import Dict, Any
from datetime import datetime
import uuid

# Global game storage (will move to Redis later)
active_games: Dict[str, Dict[str, Any]] = {}
game_lobbies: Dict[str, Dict[str, Any]] = {}

class GameStateManager:
    """Manages game state across the application"""
    
    @staticmethod
    def get_active_games() -> Dict[str, Dict[str, Any]]:
        return active_games
    
    @staticmethod
    def get_game(game_id: str) -> Dict[str, Any]:
        return active_games.get(game_id)
    
    @staticmethod
    def create_game(game_data: Dict[str, Any]) -> str:
        game_id = str(uuid.uuid4())
        game_data['id'] = game_id
        active_games[game_id] = game_data
        return game_id
    
    @staticmethod
    def update_game(game_id: str, game_data: Dict[str, Any]):
        if game_id in active_games:
            active_games[game_id].update(game_data)
    
    @staticmethod
    def remove_game(game_id: str):
        if game_id in active_games:
            del active_games[game_id]
    
    @staticmethod
    def get_or_create_quick_game() -> Dict[str, Any]:
        """Find existing quick game or create new one"""
        # Look for public games with less than 4 players
        for game_id, game_data in active_games.items():
            if (len(game_data.get("players", [])) < 4 and 
                game_data.get("settings", {}).get("privacy") == "public"):
                return game_data
        
        # Create new quick game
        game_id = str(uuid.uuid4())
        game_data = {
            "id": game_id,
            "name": "Quick Match - Chaturaji",
            "variant": "chaturaji",
            "host": "Quick Player 1",
            "created_at": datetime.now().isoformat(),
            "status": "waiting",
            "players": [{"name": "Quick Player 1", "color": "red", "connected": True}],
            "settings": {
                "time_limit": 30,
                "privacy": "public",
                "spectators_allowed": True,
                "move_hints": True,
                "sound_effects": True,
                "auto_save": False
            },
            "current_player": 0,
            "scores": {"red": 0, "blue": 0, "yellow": 0, "green": 0}
        }
        active_games[game_id] = game_data
        return game_data

# Initialize with a default quick game
GameStateManager.get_or_create_quick_game()
