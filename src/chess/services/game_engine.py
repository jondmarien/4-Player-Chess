import json
from typing import Dict, List, Optional, Tuple
from enum import Enum

class PieceType(Enum):
    KING = "king"
    QUEEN = "queen" 
    BISHOP = "bishop"
    KNIGHT = "knight"
    BOAT = "boat"  # Chaturaji piece
    PAWN = "pawn"

class GameVariant(Enum):
    CHATURAJI = "chaturaji"
    ENOCHIAN = "enochian"

class ChessPiece:
    def __init__(self, piece_type: PieceType, color: str, position: Tuple[int, int]):
        self.type = piece_type
        self.color = color  # red, blue, yellow, green
        self.position = position
        self.is_captured = False

class GameEngine:
    def __init__(self, variant: GameVariant = GameVariant.CHATURAJI):
        self.variant = variant
        self.board = self.initialize_board()
        self.current_player = 0  # 0-3 for four players
        self.scores = {"red": 0, "blue": 0, "yellow": 0, "green": 0}
        self.players = ["red", "blue", "yellow", "green"]
        
    def initialize_board(self) -> List[List[Optional[ChessPiece]]]:
        """Initialize 8x8 board with 4-player setup"""
        board = [[None for _ in range(8)] for _ in range(8)]
        
        # Setup initial pieces for each player
        self.setup_player_pieces(board, "red", 0)    # Bottom
        self.setup_player_pieces(board, "blue", 1)   # Right  
        self.setup_player_pieces(board, "yellow", 2) # Top
        self.setup_player_pieces(board, "green", 3)  # Left
        
        return board
    
    def setup_player_pieces(self, board: List[List], color: str, player_index: int):
        """Setup pieces for one player based on their position (0-3)"""
        if self.variant == GameVariant.CHATURAJI:
            self.setup_chaturaji_pieces(board, color, player_index)
        else:
            self.setup_enochian_pieces(board, color, player_index)
    
    def setup_chaturaji_pieces(self, board: List[List], color: str, player_index: int):
        """Setup Chaturaji pieces for a player"""
        # Each player gets: King, Bishop, Knight, Boat, 4 Pawns
        if player_index == 0:  # Red - bottom
            board[0][3] = ChessPiece(PieceType.KING, color, (0, 3))
            board[0][2] = ChessPiece(PieceType.BISHOP, color, (0, 2))
            board[0][4] = ChessPiece(PieceType.KNIGHT, color, (0, 4))
            board[0][1] = ChessPiece(PieceType.BOAT, color, (0, 1))
            for i in range(4):
                board[1][i + 2] = ChessPiece(PieceType.PAWN, color, (1, i + 2))
        
        # Similar setup for other players rotated around the board
        # ... (implement for other 3 players)
    
    def is_valid_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Validate if a move is legal"""
        piece = self.board[from_pos[0]][from_pos[1]]
        if not piece or piece.color != self.players[self.current_player]:
            return False
        
        # Check piece-specific movement rules
        if piece.type == PieceType.BOAT:
            return self.is_valid_boat_move(from_pos, to_pos)
        # ... implement other piece movement validations
        
        return True
    
    def is_valid_boat_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Boat moves 2 squares diagonally (Chaturaji specific)"""
        dx = abs(to_pos[0] - from_pos[0])
        dy = abs(to_pos[1] - from_pos[1])
        return dx == 2 and dy == 2
    
    def make_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> Dict:
        """Execute a move and return result"""
        if not self.is_valid_move(from_pos, to_pos):
            return {"success": False, "error": "Invalid move"}
        
        piece = self.board[from_pos[0]][from_pos[1]]
        captured_piece = self.board[to_pos[0]][to_pos[1]]
        
        # Calculate points for Chaturaji
        points_earned = 0
        if captured_piece and self.variant == GameVariant.CHATURAJI:
            points_earned = self.calculate_piece_points(captured_piece)
            self.scores[piece.color] += points_earned
        
        # Execute move
        self.board[to_pos[0]][to_pos[1]] = piece
        self.board[from_pos[0]][from_pos[1]] = None
        piece.position = to_pos
        
        # Next player
        self.current_player = (self.current_player + 1) % 4
        
        return {
            "success": True,
            "points_earned": points_earned,
            "captured": captured_piece.type.value if captured_piece else None,
            "current_player": self.players[self.current_player],
            "scores": self.scores.copy()
        }
    
    def calculate_piece_points(self, piece: ChessPiece) -> int:
        """Calculate points for captured piece (Chaturaji)"""
        point_values = {
            PieceType.KING: 3,
            PieceType.KNIGHT: 3,
            PieceType.BISHOP: 5,
            PieceType.BOAT: 5,
            PieceType.PAWN: 1
        }
        return point_values.get(piece.type, 0)
