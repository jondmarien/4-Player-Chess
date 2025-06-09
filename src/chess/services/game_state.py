"""Enhanced game state management with proper cleanup"""
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

# Global game storage
active_games: Dict[str, Dict[str, Any]] = {}
game_lobbies: Dict[str, Dict[str, Any]] = {}

class GameStateManager:
    """Enhanced game state manager with host migration"""
    
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
    def remove_player_from_game(game_id: str, player_id: str) -> Optional[Dict[str, Any]]:
        """Remove specific player from game and return updated game data"""
        if game_id not in active_games:
            return None
            
        game_data = active_games[game_id]
        original_players = game_data.get('players', [])
        
        # Remove the player
        game_data['players'] = [p for p in original_players if p.get('name') != player_id]
        
        print(f"🔄 Removed player {player_id} from game {game_id}")
        print(f"🔢 Players remaining: {len(game_data['players'])}")
        
        # If no players left, remove game entirely
        if len(game_data['players']) == 0:
            del active_games[game_id]
            print(f"🗑️ Game {game_id} deleted - no players remaining")
            return None
        else:
            active_games[game_id] = game_data
            return game_data
    
    @staticmethod
    def migrate_host(game_id: str, old_host: str, new_host: str) -> bool:
        """Migrate host to a new player"""
        if game_id not in active_games:
            return False
            
        game_data = active_games[game_id]
        
        # Verify new host is in the game
        player_names = [p.get('name') for p in game_data.get('players', [])]
        if new_host not in player_names:
            return False
            
        # Update host
        game_data['host'] = new_host
        game_data['host_migrated_at'] = datetime.now().isoformat()
        game_data['previous_host'] = old_host
        
        active_games[game_id] = game_data
        print(f"👑 Host migrated from {old_host} to {new_host} in game {game_id}")
        return True
    
    @staticmethod
    def get_game_host(game_id: str) -> Optional[str]:
        """Get the current host of a game"""
        if game_id in active_games:
            return active_games[game_id].get('host')
        return None
    
    @staticmethod
    def is_player_host(game_id: str, player_id: str) -> bool:
        """Check if player is the host of a game"""
        return GameStateManager.get_game_host(game_id) == player_id
    
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
