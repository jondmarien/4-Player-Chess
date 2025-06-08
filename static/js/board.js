// Chess board interaction and WebSocket handling
class ChessBoard {
    constructor(gameId) {
        this.gameId = gameId;
        this.selectedSquare = null;
        this.currentPlayer = 'red';
        this.initializeBoard();
    }
    
    initializeBoard() {
        console.log(`🏰 Initializing chess board for game: ${this.gameId}`);
        
        // Add click handlers to squares
        document.querySelectorAll('.chess-square').forEach(square => {
            square.addEventListener('click', (e) => this.handleSquareClick(e));
        });
        
        // Add drag handlers to pieces
        document.querySelectorAll('.chess-piece').forEach(piece => {
            piece.addEventListener('dragstart', (e) => this.handleDragStart(e));
            piece.addEventListener('dragend', (e) => this.handleDragEnd(e));
        });
        
        // Add drop handlers to squares
        document.querySelectorAll('.chess-square').forEach(square => {
            square.addEventListener('dragover', (e) => this.handleDragOver(e));
            square.addEventListener('drop', (e) => this.handleDrop(e));
        });
    }
    
    handleSquareClick(e) {
        const square = e.currentTarget;
        const squareId = square.dataset.square;
        
        if (this.selectedSquare) {
            // Try to move piece
            this.makeMove(this.selectedSquare, squareId);
            this.clearSelection();
        } else if (square.querySelector('.chess-piece')) {
            // Select piece
            this.selectSquare(square);
        }
    }
    
    selectSquare(square) {
        this.clearSelection();
        square.classList.add('selected');
        this.selectedSquare = square.dataset.square;
        
        // Highlight possible moves (basic implementation)
        this.highlightPossibleMoves(square);
    }
    
    clearSelection() {
        document.querySelectorAll('.chess-square').forEach(sq => {
            sq.classList.remove('selected', 'valid-move');
        });
        this.selectedSquare = null;
    }
    
    highlightPossibleMoves(square) {
        // Basic move highlighting - will enhance with proper chess rules
        const row = parseInt(square.dataset.row);
        const col = parseInt(square.dataset.col);
        
        // Highlight adjacent squares for now
        for (let r = Math.max(0, row-1); r <= Math.min(7, row+1); r++) {
            for (let c = Math.max(0, col-1); c <= Math.min(7, col+1); c++) {
                if (r !== row || c !== col) {
                    const targetSquare = document.querySelector(`[data-row="${r}"][data-col="${c}"]`);
                    if (targetSquare) {
                        targetSquare.classList.add('valid-move');
                    }
                }
            }
        }
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
                    piece: 'unknown', // Will determine from board
                    player: 'player1' // Will get from game state
                }
            }));
        }
    }
    
    handleDragStart(e) {
        const piece = e.target;
        const square = piece.closest('.chess-square');
        this.selectSquare(square);
        piece.classList.add('dragging');
    }
    
    handleDragEnd(e) {
        e.target.classList.remove('dragging');
        this.clearSelection();
    }
    
    handleDragOver(e) {
        e.preventDefault();
    }
    
    handleDrop(e) {
        e.preventDefault();
        const toSquare = e.currentTarget.dataset.square;
        if (this.selectedSquare) {
            this.makeMove(this.selectedSquare, toSquare);
        }
    }
    
    updateBoard(gameState) {
        console.log('📋 Updating board with game state:', gameState);
        // Update board display based on game state
        if (gameState.current_player) {
            this.currentPlayer = gameState.current_player;
            this.updateCurrentPlayerDisplay();
        }
        
        if (gameState.scores) {
            this.updateScores(gameState.scores);
        }
    }
    
    updateCurrentPlayerDisplay() {
        const currentPlayerElement = document.getElementById('current-player');
        if (currentPlayerElement) {
            currentPlayerElement.textContent = this.currentPlayer.charAt(0).toUpperCase() + this.currentPlayer.slice(1);
            currentPlayerElement.style.color = `var(--player-${this.currentPlayer})`;
        }
    }
    
    updateScores(scores) {
        Object.keys(scores).forEach(color => {
            const scoreElement = document.getElementById(`${color}-score`);
            if (scoreElement) {
                scoreElement.textContent = scores[color];
            }
        });
    }
}

// Initialize board when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const gameContainer = document.getElementById('game-container');
    if (gameContainer) {
        const gameId = new URLSearchParams(window.location.search).get('game_id') || 
                      window.location.pathname.split('/').pop();
        window.chessBoard = new ChessBoard(gameId);
    }
});
