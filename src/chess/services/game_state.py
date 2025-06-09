"""Enhanced game state management with proper cleanup"""
from typing import Dict, Any
from datetime import datetime
import uuid

# Global game storage
active_games: Dict[str, Dict[str, Any]] = {}
game_lobbies: Dict[str, Dict[str, Any]] = {}

class GameStateManager:
    """Enhanced game state manager with cleanup"""
    
    @staticmethod
    def get_active_games() -> Dict[str, Dict[str, Any]]:
        # Clean up games with no players before returning
        GameStateManager.cleanup_empty_games()
        return active_games
    
    @staticmethod
    def cleanup_empty_games():
        """Remove games with no active players"""
        empty_games = []
        for game_id, game_data in active_games.items():
            players = game_data.get('players', [])
            connected_players = [p for p in players if p.get('connected', False)]
            
            if len(connected_players) == 0:
                empty_games.append(game_id)
        
        for game_id in empty_games:
            del active_games[game_id]
            print(f"🗑️ Cleaned up empty game: {game_id}")
    
    @staticmethod
    def get_game(game_id: str) -> Dict[str, Any]:
        return active_games.get(game_id)
    
    @staticmethod
    def create_game(game_data: Dict[str, Any]) -> str:
        game_id = str(uuid.uuid4())
        game_data['id'] = game_id
        game_data['created_at'] = datetime.now().isoformat()
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
            print(f"🗑️ Game {game_id} removed from active games")
    
    @staticmethod
    def remove_player_from_game(game_id: str, player_id: str):
        """Remove specific player from game"""
        if game_id in active_games:
            game_data = active_games[game_id]
            original_players = game_data.get('players', [])
            game_data['players'] = [p for p in original_players if p.get('name') != player_id]
            
            print(f"🔄 Removed player {player_id} from game {game_id}")
            
            # If no players left, remove game
            if len(game_data['players']) == 0:
                GameStateManager.remove_game(game_id)
            else:
                active_games[game_id] = game_data
    
    @staticmethod
    def get_or_create_quick_game() -> Dict[str, Any]:
        """Find existing quick game or create new one with proper cleanup"""
        
        # First, clean up any stale games
        GameStateManager.cleanup_empty_games()
        
        # Look for public games with less than 4 players
        for game_id, game_data in active_games.items():
            players = game_data.get("players", [])
            connected_players = [p for p in players if p.get('connected', True)]
            
            if (len(connected_players) < 4 and 
                game_data.get("settings", {}).get("privacy") == "public"):
                return game_data
        
        # Create new quick game
        game_id = str(uuid.uuid4())
        game_data = {
            "id": game_id,
            "name": "Quick Match - Chaturaji",
            "variant": "chaturaji",
            "host": "System",
            "created_at": datetime.now().isoformat(),
            "status": "waiting",
            "players": [],  # Start with empty players list
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
