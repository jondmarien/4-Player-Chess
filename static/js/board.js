class ChessBoard {
    constructor(gameId) {
        this.gameId = gameId;
        this.selectedSquare = null;
        this.currentPlayer = 'red';
        this.gameVariant = 'chaturaji'; // Will get from game state
        this.initializeBoard();
    }
    
    initializeBoard() {
        console.log(`🏰 Initializing ${this.gameVariant} board for game: ${this.gameId}`);
        
        // Add click handlers to squares
        document.querySelectorAll('.chess-square').forEach(square => {
            square.addEventListener('click', (e) => this.handleSquareClick(e));
        });
        
        // Add piece interaction
        this.updatePieceInteractions();
    }
    
    updatePieceInteractions() {
        document.querySelectorAll('.chess-piece').forEach(piece => {
            piece.addEventListener('click', (e) => {
                e.stopPropagation();
                this.handlePieceClick(e);
            });
        });
    }
    
    handleSquareClick(e) {
        const square = e.currentTarget;
        const squareId = square.dataset.square;
        
        if (this.selectedSquare) {
            // Try to move piece
            this.makeMove(this.selectedSquare, squareId);
            this.clearSelection();
        } else {
            // Select piece if there's one on this square
            const piece = square.querySelector('.chess-piece');
            if (piece) {
                this.selectSquare(square);
            }
        }
    }
    
    handlePieceClick(e) {
        const piece = e.target;
        const square = piece.closest('.chess-square');
        this.selectSquare(square);
    }
    
    selectSquare(square) {
        this.clearSelection();
        square.classList.add('selected');
        this.selectedSquare = square.dataset.square;
        
        // Show possible moves
        this.highlightValidMoves(square);
        
        console.log(`🎯 Selected piece at ${this.selectedSquare}`);
    }
    
    clearSelection() {
        document.querySelectorAll('.chess-square').forEach(sq => {
            sq.classList.remove('selected', 'valid-move', 'capture-move');
        });
        this.selectedSquare = null;
    }
    
    highlightValidMoves(square) {
        const piece = square.querySelector('.chess-piece');
        if (!piece) return;
        
        const pieceType = piece.dataset.piece || piece.textContent;
        const [col, row] = [square.dataset.square.charCodeAt(0) - 97, parseInt(square.dataset.square[1]) - 1];
        
        // Basic move highlighting - will enhance with proper rules
        const moves = this.getPossibleMoves(pieceType, col, row);
        
        moves.forEach(([newCol, newRow]) => {
            if (newCol >= 0 && newCol < 8 && newRow >= 0 && newRow < 8) {
                const targetSquare = document.querySelector(`[data-square="${String.fromCharCode(97 + newCol)}${newRow + 1}"]`);
                if (targetSquare) {
                    const targetPiece = targetSquare.querySelector('.chess-piece');
                    if (targetPiece) {
                        targetSquare.classList.add('capture-move');
                    } else {
                        targetSquare.classList.add('valid-move');
                    }
                }
            }
        });
    }
    
    getPossibleMoves(piece, col, row) {
        // Basic movement patterns - will expand for each piece type
        const moves = [];
        
        if (piece.includes('♟') || piece.includes('♙')) { // Pawn
            moves.push([col, row + 1], [col, row - 1]); // Basic forward/back
        } else if (piece.includes('♜') || piece.includes('♖')) { // Rook/Boat
            // Rook moves (horizontal/vertical)
            for (let i = 1; i < 8; i++) {
                moves.push([col + i, row], [col - i, row], [col, row + i], [col, row - i]);
            }
        } else if (piece.includes('♞') || piece.includes('♘')) { // Knight/Horse
            // Knight L-shaped moves
            moves.push(
                [col + 2, row + 1], [col + 2, row - 1],
                [col - 2, row + 1], [col - 2, row - 1],
                [col + 1, row + 2], [col + 1, row - 2],
                [col - 1, row + 2], [col - 1, row - 2]
            );
        }
        // Add more piece types...
        
        return moves;
    }
    
    makeMove(fromSquare, toSquare) {
        if (fromSquare === toSquare) return;
        
        console.log(`🎮 Making move: ${fromSquare} → ${toSquare}`);
        
        // Send move via WebSocket
        if (window.gameWebSocket) {
            window.gameWebSocket.send(JSON.stringify({
                type: 'move',
                data: {
                    from: fromSquare,
                    to: toSquare,
                    variant: this.gameVariant,
                    player: 'player1'
                }
            }));
        }
        
        // Visual feedback
        this.showMoveAnimation(fromSquare, toSquare);
    }
    
    showMoveAnimation(from, to) {
        const fromSquare = document.querySelector(`[data-square="${from}"]`);
        const toSquare = document.querySelector(`[data-square="${to}"]`);
        
        if (fromSquare && toSquare) {
            toSquare.classList.add('last-move');
            fromSquare.classList.add('last-move');
            
            setTimeout(() => {
                fromSquare.classList.remove('last-move');
                toSquare.classList.remove('last-move');
            }, 2000);
        }
    }
}

// Initialize enhanced board
document.addEventListener('DOMContentLoaded', function() {
    const gameContainer = document.getElementById('game-container');
    if (gameContainer) {
        const gameId = window.location.pathname.split('/').pop();
        window.chessBoard = new ChessBoard(gameId);
    }
});
