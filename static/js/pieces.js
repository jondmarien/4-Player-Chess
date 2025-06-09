class GameWebSocket {
    constructor(gameId, playerId) {
        this.gameId = gameId;
        this.playerId = playerId;
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.isConnecting = false;
        this.isDestroyed = false;
        this.isHost = false;
        this.voluntaryLeave = false;
        
        this.setupPageVisibilityHandlers();
        this.setupBeforeUnloadHandler();
        this.connect();
    }
    
    setupPageVisibilityHandlers() {
        // Handle tab visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                console.log('👁️ Tab hidden, maintaining connection...');
            } else {
                console.log('👁️ Tab visible, checking connection...');
                this.checkConnection();
            }
        });
    }
    
    setupBeforeUnloadHandler() {
        // Handle page unload/refresh
        window.addEventListener('beforeunload', () => {
            console.log('🚪 Page unloading, disconnecting...');
            this.disconnect();
        });
        
        // Handle page hide (mobile/tablet)
        window.addEventListener('pagehide', () => {
            console.log('🚪 Page hiding, disconnecting...');
            this.disconnect();
        });
    }
    
    checkConnection() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            // Send ping to verify connection
            this.socket.send(JSON.stringify({ type: 'ping' }));
        } else if (!this.isConnecting && !this.isDestroyed) {
            console.log('🔄 Connection lost, attempting to reconnect...');
            this.connect();
        }
    }
    
    connect() {
        if (this.isConnecting || this.isDestroyed || 
           (this.socket && this.socket.readyState === WebSocket.OPEN)) {
            return;
        }
        
        this.isConnecting = true;
        
        try {
            const wsUrl = `ws://localhost:8000/ws/game/${this.gameId}?player_id=${this.playerId}`;
            console.log(`🔌 Connecting to WebSocket: ${wsUrl}`);
            
            this.socket = new WebSocket(wsUrl);
            
            this.socket.onopen = (event) => {
                console.log('✅ WebSocket connected');
                this.reconnectAttempts = 0;
                this.isConnecting = false;
                this.updateConnectionStatus(true);
            };
            
            this.socket.onmessage = (event) => {
                const message = JSON.parse(event.data);
                this.handleMessage(message);
            };
            
            this.socket.onclose = (event) => {
                console.log(`🔌 WebSocket disconnected (code: ${event.code})`);
                this.isConnecting = false;
                this.updateConnectionStatus(false);
                
                // Only attempt reconnect if not intentionally closed
                if (event.code !== 1000 && !this.isDestroyed) {
                    this.attemptReconnect();
                }
            };
            
            this.socket.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                this.isConnecting = false;
                this.updateConnectionStatus(false);
            };
            
        } catch (error) {
            console.error('❌ Failed to create WebSocket:', error);
            this.isConnecting = false;
            this.updateConnectionStatus(false);
        }
    }
    
    disconnect() {
        console.log('🔌 Disconnecting WebSocket...');
        this.isDestroyed = true;
        
        if (this.socket) {
            if (!this.voluntaryLeave) {
                // Send leave message if not already sent
                try {
                    this.socket.send(JSON.stringify({
                        type: 'leave_game',
                        player_id: this.playerId
                    }));
                } catch (e) {
                    console.log('Could not send leave message:', e);
                }
            }
            
            this.socket.close(1000, 'User disconnected');
            this.socket = null;
        }
    }
    
    send(data) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(data);
        } else {
            console.warn('⚠️ WebSocket not connected, cannot send message');
        }
    }
    
    handleMessage(message) {
        console.log('📨 Received message:', message);
        
        switch (message.type) {
            case 'connection_established':
                this.isHost = message.is_host || false;
                this.showToast(`Connected as ${message.player_id}${this.isHost ? ' (Host)' : ''}`, 'success');
                break;
                
            case 'host_migration':
                if (message.new_host === this.playerId) {
                    this.isHost = true;
                    this.showToast('You are now the host!', 'info');
                } else {
                    this.showToast(`${message.new_host} is now the host`, 'info');
                }
                this.updateHostIndicator();
                break;
                
            case 'player_left':
                this.showToast(`${message.player_id} left the game`, 'warning');
                this.updatePlayerCount();
                break;
                
            case 'game_state':
                if (window.chessBoard) {
                    window.chessBoard.updateBoard(message.data);
                }
                this.isHost = message.is_host || false;
                this.updateHostIndicator();
                break;
                
            case 'move_made':
                this.handleMoveUpdate(message);
                this.addMoveToHistory(message);
                break;
                
            case 'player_joined':
                this.showToast(`${message.player_id} joined the game`, 'info');
                this.updatePlayerStatus(message.player_id, 'connected');
                break;
                
            case 'player_disconnected':
                this.showToast(`${message.player_id} left the game`, 'warning');
                this.updatePlayerStatus(message.player_id, 'disconnected');
                break;
                
            case 'chat_message':
                this.addChatMessage(message.player, message.message);
                break;
                
            default:
                // Call original handler for other types
                if (typeof this._originalHandleMessage === 'function') {
                    this._originalHandleMessage(message);
                }
        }
    }
    
    handleMoveUpdate(moveMessage) {
        console.log('♟️ Move update:', moveMessage);
        
        // Visual feedback for move
        const fromSquare = document.querySelector(`[data-square="${moveMessage.from}"]`);
        const toSquare = document.querySelector(`[data-square="${moveMessage.to}"]`);
        
        if (fromSquare && toSquare) {
            fromSquare.classList.add('last-move');
            toSquare.classList.add('last-move');
            
            // Remove highlighting after 2 seconds
            setTimeout(() => {
                fromSquare.classList.remove('last-move');
                toSquare.classList.remove('last-move');
            }, 2000);
        }
    }
    
    addMoveToHistory(moveMessage) {
        const movesList = document.getElementById('moves-list');
        if (movesList) {
            const moveElement = document.createElement('div');
            moveElement.className = 'move-item';
            moveElement.innerHTML = `
                <span class="move-player" style="color: var(--player-${moveMessage.player});">
                    ${moveMessage.player.charAt(0).toUpperCase() + moveMessage.player.slice(1)}
                </span>
                <span class="move-notation">${moveMessage.from}-${moveMessage.to}</span>
                <span style="color: var(--cyber-light-gray);">now</span>
            `;
            movesList.appendChild(moveElement);
            
            // Auto-scroll to bottom
            movesList.scrollTop = movesList.scrollHeight;
        }
    }
    
    updateConnectionStatus(connected) {
        const indicators = document.querySelectorAll('.ws-indicator');
        indicators.forEach(indicator => {
            indicator.classList.toggle('connected', connected);
            indicator.classList.toggle('disconnected', !connected);
        });
        
        const statusText = document.querySelector('.websocket-status span:last-child');
        if (statusText) {
            statusText.textContent = connected ? 'Connected' : 'Disconnected';
        }
    }
    
    updatePlayerStatus(playerId, status) {
        // Update player connection indicators
        const playerPanels = document.querySelectorAll('.player-panel');
        // This would need more sophisticated player mapping
        console.log(`Player ${playerId} is now ${status}`);
    }
    
    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        if (toastContainer) {
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            toast.textContent = message;
            
            toastContainer.appendChild(toast);
            
            // Remove toast after 5 seconds
            setTimeout(() => {
                toast.remove();
            }, 5000);
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔄 Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                this.connect();
            }, 2000 * this.reconnectAttempts); // Exponential backoff
        } else {
            console.error('❌ Max reconnection attempts reached');
            this.showToast('Connection lost. Please refresh the page.', 'error');
        }
    }
    
    updateHostIndicator() {
        // Update UI to show if current player is host
        const hostIndicator = document.getElementById('host-indicator');
        if (hostIndicator) {
            hostIndicator.style.display = this.isHost ? 'block' : 'none';
        }
    }
    
    updatePlayerCount() {
        // Refresh lobby display
        const activeGamesElement = document.getElementById('games-list');
        if (activeGamesElement) {
            // Trigger HTMX refresh
            htmx.trigger(activeGamesElement, 'refresh');
        }
    }
    
    // Add method to voluntarily leave game
    leaveGame() {
        console.log('🚪 Voluntarily leaving game...');
        this.voluntaryLeave = true;
        
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'leave_game',
                player_id: this.playerId
            }));
        }
        
        // Close connection after a brief delay
        setTimeout(() => {
            this.disconnect();
        }, 500);
    }
}

// Ensure cleanup on page unload
let gameWebSocketInstance = null;

// Initialize WebSocket when DOM loads
document.addEventListener('DOMContentLoaded', function() {
    const gameContainer = document.getElementById('game-container');
    if (gameContainer && !gameWebSocketInstance) {
        const gameId = window.location.pathname.split('/').pop();
        gameWebSocketInstance = new GameWebSocket(gameId, 'player1');
        window.gameWebSocket = gameWebSocketInstance;
    }
    
    // Add leave game button to game pages
    const leaveButton = document.getElementById('leave-game-btn');
    if (leaveButton && window.gameWebSocket) {
        leaveButton.addEventListener('click', function() {
            if (confirm('Are you sure you want to leave this game?')) {
                window.gameWebSocket.leaveGame();
                // Redirect to lobby after leaving
                setTimeout(() => {
                    window.location.href = '/lobby';
                }, 1000);
            }
        });
    }
    
    // Add resign button functionality
    const resignButton = document.getElementById('resign-btn');
    if (resignButton && window.gameWebSocket) {
        resignButton.style.display = '';
        resignButton.addEventListener('click', function() {
            if (confirm('Are you sure you want to resign?')) {
                window.gameWebSocket.send(JSON.stringify({
                    type: 'resign',
                    player_id: window.gameWebSocket.playerId
                }));
                window.gameWebSocket.showToast('You have resigned.', 'warning');
            }
        });
    }

    // Add offer draw button functionality
    const offerDrawButton = document.getElementById('offer-draw');
    if (offerDrawButton && window.gameWebSocket) {
        offerDrawButton.style.display = '';
        offerDrawButton.addEventListener('click', function() {
            window.gameWebSocket.send(JSON.stringify({
                type: 'offer_draw',
                player_id: window.gameWebSocket.playerId
            }));
            window.gameWebSocket.showToast('Draw offer sent.', 'info');
        });
    }
    
    // Handle browser close/refresh
    window.addEventListener('beforeunload', function(e) {
        if (window.gameWebSocket && !window.gameWebSocket.voluntaryLeave) {
            window.gameWebSocket.disconnect();
        }
    });
});
