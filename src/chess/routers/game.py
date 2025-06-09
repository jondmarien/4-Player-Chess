from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import HTMLResponse
from typing import Optional, List
import uuid
import json
from datetime import datetime

# Import shared game state
from ..services.game_state import GameStateManager, active_games

router = APIRouter(prefix="/api", tags=["games"])

@router.get("/games/active")
async def get_active_games():
    """Get list of active games with proper player counts"""
    
    # Clean up stale games first
    GameStateManager.cleanup_empty_games()
    
    games = GameStateManager.get_active_games()
    games_html = ""
    
    if not games:
        games_html = """
        <div class="terminal-text" style="text-align: center; padding: 30px;">
            <div style="color: var(--cyber-yellow);">📡 No active games found</div>
            <div style="margin-top: 10px; color: var(--cyber-light-gray);">
                Be the first to create a game!
            </div>
        </div>
        """
    else:
        for game_id, game_data in games.items():
            # Count only connected players
            all_players = game_data.get('players', [])
            connected_players = [p for p in all_players if p.get('connected', True)]
            player_count = len(connected_players)
            
            # Skip games with no players (shouldn't happen after cleanup, but safety check)
            if player_count == 0:
                continue
                
            games_html += f"""
            <div class="cyber-card" style="margin: 10px 0; padding: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: var(--cyber-green);">{game_data.get('name', 'Unknown Game')}</strong>
                        <div style="color: var(--cyber-light-gray); font-size: 0.9rem;">
                            {game_data.get('variant', 'chaturaji').title()} • {player_count}/4 players
                        </div>
                        <div style="color: var(--cyber-blue); font-size: 0.8rem;">
                            Room: {game_id[:6].upper()} • Created: {game_data.get('created_at', 'Unknown')[:16]}
                        </div>
                    </div>
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <button class="cyber-button" 
                                hx-post="/api/games/join" 
                                hx-vals='{{"room_code": "{game_id[:6]}", "player_name": "Player"}}' 
                                hx-target="#toast-container" 
                                hx-swap="afterbegin"
                                {"disabled" if player_count >= 4 else ""}>
                            {"Game Full" if player_count >= 4 else "Join Game"}
                        </button>
                    </div>
                </div>
            </div>
            """
    
    return HTMLResponse(games_html)

@router.post("/games/quick-match")
async def quick_match():
    """Enhanced quick match with proper player management"""
    
    # Clean up stale games first
    GameStateManager.cleanup_empty_games()
    
    # Get or create quick game (this now returns empty player list)
    game_data = GameStateManager.get_or_create_quick_game()
    game_id = game_data['id']
    
    success_html = f"""
    <div class="toast" style="border-color: var(--cyber-blue);">
        🎮 Joining quick match! Variant: Chaturaji<br>
        <strong>Room: {game_id[:6].upper()}</strong><br>
        <button class="cyber-button" onclick="location.href='/game/{game_id}'" style="margin-top: 10px;">
            Enter Game Room
        </button>
    </div>
    <script>
        setTimeout(() => {{
            location.href = '/game/{game_id}';
        }}, 1500);
    </script>
    """
    
    return HTMLResponse(success_html)


@router.post("/games/create")
async def create_game(
    variant: str = Form(...),
    room_name: str = Form(...),
    host_name: str = Form(...),
    time_limit: int = Form(30),
    privacy: str = Form("private"),
    spectators_allowed: bool = Form(False),
    move_hints: bool = Form(True),
    sound_effects: bool = Form(True),
    auto_save: bool = Form(False)
):
    """Create a new game room"""
    
    game_id = str(uuid.uuid4())
    room_code = game_id[:6].upper()
    
    game_data = {
        "id": game_id,
        "name": room_name,
        "variant": variant,
        "host": host_name,
        "created_at": datetime.now().isoformat(),
        "status": "waiting",
        "players": [{"name": host_name, "color": "red", "connected": True}],
        "settings": {
            "time_limit": time_limit,
            "privacy": privacy,
            "spectators_allowed": spectators_allowed,
            "move_hints": move_hints,
            "sound_effects": sound_effects,
            "auto_save": auto_save
        },
        "current_player": 0,
        "scores": {"red": 0, "blue": 0, "yellow": 0, "green": 0}
    }
    
    active_games[game_id] = game_data
    
    # Return success message with room code
    success_html = f"""
    <div class="toast" style="border-color: var(--cyber-green);">
        🎉 Game created successfully!<br>
        <strong>Room Code: {room_code}</strong><br>
        <button class="cyber-button" onclick="location.href='/game/{game_id}'" style="margin-top: 10px;">
            Enter Game Room
        </button>
    </div>
    <script>
        setTimeout(() => {{
            location.href = '/game/{game_id}';
        }}, 2000);
    </script>
    """
    
    return HTMLResponse(success_html)

@router.post("/games/join")
async def join_game(
    room_code: str = Form(...),
    player_name: str = Form(...)
):
    """Join an existing game by room code"""
    
    # Find game by room code (first 6 chars of game_id)
    target_game = None
    target_game_id = None
    
    for game_id, game_data in active_games.items():
        if game_id[:6].upper() == room_code.upper():
            target_game = game_data
            target_game_id = game_id
            break
    
    if not target_game:
        error_html = """
        <div class="toast" style="border-color: var(--cyber-red);">
            ❌ Game not found! Check your room code.
        </div>
        """
        return HTMLResponse(error_html)
    
    # Check if game is full
    if len(target_game["players"]) >= 4:
        error_html = """
        <div class="toast" style="border-color: var(--cyber-yellow);">
            ⚠️ Game is full! Try another room.
        </div>
        """
        return HTMLResponse(error_html)
    
    # Add player to game
    colors = ["red", "blue", "yellow", "green"]
    taken_colors = [p["color"] for p in target_game["players"]]
    available_color = next(color for color in colors if color not in taken_colors)
    
    target_game["players"].append({
        "name": player_name,
        "color": available_color,
        "connected": True
    })
    
    success_html = f"""
    <div class="toast" style="border-color: var(--cyber-green);">
        🎮 Joined game as {available_color.title()} player!<br>
        <button class="cyber-button" onclick="location.href='/game/{target_game_id}'" style="margin-top: 10px;">
            Enter Game Room
        </button>
    </div>
    <script>
        setTimeout(() => {{
            location.href = '/game/{target_game_id}';
        }}, 1500);
    </script>
    """
    
    return HTMLResponse(success_html)


@router.get("/board/{game_id}")
async def get_game_board(game_id: str):
    """Get the current game board state based on variant"""
    
    # Handle both regular game IDs and special cases like "quick-match"
    if game_id == "quick-match":
        # Create a temporary Chaturaji game for quick match
        game_data = {"variant": "chaturaji", "id": game_id}
    elif game_id not in active_games:
        return HTMLResponse("""
        <div class="terminal-text" style="text-align: center; padding: 50px;">
            <div style="color: var(--cyber-red);">❌ Game not found</div>
            <button class="cyber-button" onclick="location.href='/lobby'" style="margin-top: 15px;">
                Return to Lobby
            </button>
        </div>
        """)
    else:
        game_data = active_games[game_id]
    
    variant = game_data.get("variant", "chaturaji")
    
    if variant == "enochian":
        return render_enochian_board(game_id, game_data)
    else:
        return render_chaturaji_board(game_id, game_data)

def render_chaturaji_board(game_id: str, game_data: dict):
    """Render authentic Chaturaji with CORRECT orientations based on reference"""
    board_html = '<div class="chess-board-grid chaturaji-board">'
    
    # CORRECT Chaturaji setup based on your reference image
    piece_setup = {
        # BLUE corner (top-left) - arranged VERTICALLY down left edge
        'a8': '♚', 'a7': '♞', 'a6': '♝', 'a5': '♜',  # King, Horse, Elephant, Boat down left column
        'b8': '♟', 'b7': '♟', 'b6': '♟', 'b5': '♟',  # Pawns in column next to pieces
        
        # YELLOW corner (top-right) - arranged HORIZONTALLY across top edge
        'e8': '♚', 'f8': '♞', 'g8': '♝', 'h8': '♜',  # King, Horse, Elephant, Boat across top row
        'e7': '♟', 'f7': '♟', 'g7': '♟', 'h7': '♟',  # Pawns in row below pieces
        
        # RED corner (bottom-left) - arranged HORIZONTALLY across bottom edge  
        'a1': '♔', 'b1': '♘', 'c1': '♗', 'd1': '♖',  # King, Horse, Elephant, Boat across bottom row
        'a2': '♙', 'b2': '♙', 'c2': '♙', 'd2': '♙',  # Pawns in row above pieces
        
        # GREEN corner (bottom-right) - arranged VERTICALLY up right edge
        'h1': '♔', 'h2': '♘', 'h3': '♗', 'h4': '♖',  # King, Horse, Elephant, Boat up right column
        'g1': '♙', 'g2': '♙', 'g3': '♙', 'g4': '♙',  # Pawns in column next to pieces
    }
    
    for row in range(8):
        for col in range(8):
            square_name = f"{chr(97+col)}{8-row}"
            square_class = "chess-square"
            
            # Define territories based on CORRECT orientations
            territory_class = ""
            
            # Blue territory (top-left) - vertical arrangement, left columns
            if (col <= 1 and row <= 3):
                territory_class = " territory-blue"
            # Yellow territory (top-right) - horizontal arrangement, top rows
            elif (col >= 4 and row <= 1):
                territory_class = " territory-yellow"
            # Red territory (bottom-left) - horizontal arrangement, bottom rows
            elif (col <= 3 and row >= 6):
                territory_class = " territory-red"
            # Green territory (bottom-right) - vertical arrangement, right columns
            elif (col >= 6 and row >= 4):
                territory_class = " territory-green"
            
            square_class += territory_class
            
            # Standard alternating colors
            if (row + col) % 2 == 0:
                square_class += " light-square"
            else:
                square_class += " dark-square"
            
            piece = piece_setup.get(square_name, '')
            piece_html = ""
            
            if piece:
                # Color assignment based on correct territories
                if "territory-blue" in square_class:
                    piece_class = "piece-blue"
                elif "territory-yellow" in square_class:
                    piece_class = "piece-yellow"
                elif "territory-red" in square_class:
                    piece_class = "piece-red"
                elif "territory-green" in square_class:
                    piece_class = "piece-green"
                else:
                    piece_class = "piece-yellow"  # fallback
                
                piece_html = f'<div class="chess-piece {piece_class}" draggable="true">{piece}</div>'
            
            board_html += f'''
            <div class="{square_class}" data-square="{square_name}" data-row="{row}" data-col="{col}">
                {piece_html}
            </div>
            '''
    
    board_html += '</div>'
    return HTMLResponse(board_html)


def render_enochian_board(game_id: str, game_data: dict):
    """Render authentic Enochian Chess with corrected color assignments"""
    board_html = '<div class="chess-board-grid enochian-board">'
    
    # Authentic Enochian with correct corner color assignments
    piece_setup = {
        # Yellow corner (top-left) - Air element
        'a8': '♚♝',  # King & Bishop on throne
        'b8': '♛',   # Queen
        'c8': '♞',   # Knight  
        'd8': '♜',   # Rook
        'a7': '♟', 'b7': '♟', 'c7': '♟', 'd7': '♟',  # Pawns
        
        # Blue corner (top-right) - Water element
        'h8': '♚♝',  # King & Bishop on throne
        'h7': '♛',   # Queen
        'h6': '♞',   # Knight
        'h5': '♜',   # Rook  
        'g8': '♟', 'g7': '♟', 'g6': '♟', 'g5': '♟',  # Pawns
        
        # Red corner (bottom-right) - Fire element
        'h1': '♔♗',  # King & Bishop on throne
        'g1': '♕',   # Queen
        'f1': '♘',   # Knight
        'e1': '♖',   # Rook
        'h2': '♙', 'g2': '♙', 'f2': '♙', 'e2': '♙',  # Pawns
        
        # Black corner (bottom-left) - Earth element
        'a1': '♔♗',  # King & Bishop on throne
        'a2': '♕',   # Queen
        'a3': '♘',   # Knight
        'a4': '♖',   # Rook
        'b1': '♙', 'b2': '♙', 'b3': '♙', 'b4': '♙',  # Pawns
    }
    
    for row in range(8):
        for col in range(8):
            square_name = f"{chr(97+col)}{8-row}"
            square_class = "chess-square"
            
            # Throne squares
            if square_name in ['a1', 'a8', 'h1', 'h8']:
                square_class += " throne-square"
            
            # Standard alternating colors
            if (row + col) % 2 == 0:
                square_class += " light-square"
            else:
                square_class += " dark-square"
            
            piece = piece_setup.get(square_name, '')
            piece_html = ""
            
            if piece:
                # CORRECTED color assignment based on exact corner positions
                if square_name in ['a8', 'b8', 'c8', 'd8', 'a7', 'b7', 'c7', 'd7']:
                    piece_class = "piece-yellow"  # Top-left corner = Yellow
                elif square_name in ['h8', 'h7', 'h6', 'h5', 'g8', 'g7', 'g6', 'g5']:
                    piece_class = "piece-blue"    # Top-right corner = Blue
                elif square_name in ['h1', 'g1', 'f1', 'e1', 'h2', 'g2', 'f2', 'e2']:
                    piece_class = "piece-red"     # Bottom-right corner = Red
                elif square_name in ['a1', 'a2', 'a3', 'a4', 'b1', 'b2', 'b3', 'b4']:
                    piece_class = "piece-black"   # Bottom-left corner = Black
                else:
                    piece_class = "piece-yellow"  # fallback
                
                # Handle double occupancy display
                if len(piece) > 1:
                    piece_html = f'<div class="chess-piece {piece_class} double-piece" title="Double occupancy: {piece}">{piece}</div>'
                else:
                    piece_html = f'<div class="chess-piece {piece_class}" draggable="true">{piece}</div>'
            
            board_html += f'''
            <div class="{square_class}" data-square="{square_name}">
                {piece_html}
            </div>
            '''
    
    board_html += '</div>'
    return HTMLResponse(board_html)

