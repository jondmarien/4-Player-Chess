# 🏰 4-Player Chess

```
    ♜ ♞ ♝ ♛ ♚ ♝ ♞ ♜
    ♟ ♟ ♟ ♟ ♟ ♟ ♟ ♟
    · · · · · · · ·
    · · · · · · · ·
    · · · · · · · ·
    · · · · · · · ·
    ♙ ♙ ♙ ♙ ♙ ♙ ♙ ♙
    ♖ ♘ ♗ ♕ ♔ ♗ ♘ ♖

   Real-time 4-Player Chess
  ┌─────────────────────────┐
  │  Chaturaji & Enochian   │
  │      Variants           │
  └─────────────────────────┘
```

A modern, real-time multiplayer implementation of 4-player chess variants including **Chaturaji** (ancient Indian) and **Enochian Chess** (Victorian occult) with WebSocket synchronization and cybersecurity-focused architecture.

## 🚀 Quick Start

```sh
# Clone and setup
git clone <your-repo-url>
cd 4player-chess

# Install dependencies with UV
uv sync

# Start services (PostgreSQL + Redis)
# See setup instructions below

# Run development server
uv run src/main.py

# Open browser
http://localhost:8000
```

## 🎯 Features

### **Game Variants**
- **Chaturaji**: Ancient 4-player variant with scoring system
- **Enochian Chess**: Victorian team-based variant (Blue/Black vs Red/Yellow)

### **Real-time Multiplayer**
- WebSocket-based live gameplay
- Automatic game state synchronization
- Reconnection handling
- Spectator mode

### **Security Features**
- Server-side move validation
- Rate limiting on moves
- Input sanitization
- JWT authentication
- Anti-cheat measures

### **Modern Tech Stack**
- **Backend**: FastAPI + WebSockets + SQLAlchemy
- **Frontend**: HTMX + Vanilla JS + Pico CSS
- **Database**: PostgreSQL + Redis
- **Package Management**: UV (fast Python tooling)

## 🛠️ Technology Stack

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│                 │    │                 │    │                 │
│ HTMX + WebSocket│◄──►│ FastAPI + WS    │◄──►│ PostgreSQL      │
│ Vanilla JS      │    │ SQLAlchemy      │    │ Redis Cache     │
│ Pico CSS        │    │ Pydantic        │    │ Alembic         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
4player-chess/
├── src/
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Global configuration
│   ├── database.py                # Database connection
│   └── chess/
│       ├── routers/               # API endpoints
│       │   ├── game.py            # Game management
│       │   ├── websocket.py       # Real-time communication
│       │   └── auth.py            # Authentication
│       ├── models/                # SQLAlchemy models
│       │   ├── game.py            # Game entities
│       │   ├── user.py            # User management
│       │   └── move.py            # Move history
│       ├── services/              # Business logic
│       │   ├── game_engine.py     # Core chess engine
│       │   ├── chaturaji.py       # Chaturaji rules
│       │   ├── enochian.py        # Enochian rules
│       │   └── websocket_manager.py
│       └── schemas/               # Pydantic schemas
├── templates/                     # Jinja2 HTML templates
├── static/                        # CSS, JS, images
└── tests/                         # Test suite
```

## 🔧 Development Setup

### **Prerequisites**
- Python 3.9+
- PostgreSQL 16+
- Redis 7+
- UV package manager

### **Windows Setup**

**1. Install UV**
```sh
irm https://astral.sh/uv/install.ps1 | iex
```

**2. Install PostgreSQL**
```
# Download from: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
# Install with default settings, remember superuser password
```

**3. Install Redis**
```
# Option 1: WSL (recommended)
wsl --install
wsl sudo apt install redis-server

# Option 2: Windows native
# Download from: https://github.com/tporadowski/redis/releases
```

**4. Setup Project**
```sh
# Clone repository
git clone <your-repo-url>
cd 4player-chess

# Install dependencies
uv sync

# Setup environment
cp .env.example .env
# Edit .env with your database credentials
```

**5. Initialize Database**
```sh
# Create database
createdb -U postgres chess4p

# Run migrations
uv run alembic upgrade head
```

### **Development Commands**

```sh
# Start development server
uv run src/main.py

# Run tests
uv run pytest

# Add new dependency
uv add package-name

# Database migration
uv run alembic revision --autogenerate -m "Description"
uv run alembic upgrade head

# Code formatting
uv run black src/
uv run ruff check src/
```

## 🎮 Game Rules

### **Chaturaji (Ancient Indian)**
- **Players**: 4 (Red, Blue, Yellow, Green)
- **Objective**: Highest score when all games end
- **Scoring**: King/Horse=3pts, Elephant/Boat=5pts, Pawn=1pt
- **Special Rules**:
  - Boats move 2 squares diagonally (jumping)
  - Multiple king checks earn bonus points
  - Dead armies remain on board but can't move

### **Enochian Chess (Victorian)**
- **Teams**: Blue/Black vs Red/Yellow
- **Objective**: Capture both enemy kings
- **Special Rules**:
  - Queen leaps exactly 2 squares in any direction
  - Throne square double occupancy mechanics
  - Team-based victory conditions

## 🔒 Security Features

```
┌─────────────────────────────────────────┐
│             Security Layer              │
├─────────────────────────────────────────┤
│ -  Server-side move validation           │
│ -  Rate limiting (3 moves/second)        │
│ -  Input sanitization & validation       │
│ -  JWT token authentication             │
│ -  WebSocket connection security         │
│ -  SQL injection prevention             │
│ -  CORS protection                      │
└─────────────────────────────────────────┘
```

## 🌐 API Endpoints

### **REST API**
```
GET  /                          # Landing page
GET  /game/{game_id}            # Game board
POST /api/game/create           # Create new game
POST /api/game/join             # Join existing game
GET  /api/game/{id}/state       # Get game state
POST /api/move                  # Make move
```

### **WebSocket**
```
WS   /ws/game/{game_id}         # Real-time game connection

Events:
- move_made                     # Player moved piece
- game_update                   # Game state changed
- player_joined                 # New player joined
- player_disconnected           # Player left
```

## 🧪 Testing

```sh
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_game_engine.py

# Run with coverage
uv run pytest --cov=src

# Run performance tests
uv run pytest tests/test_performance.py -v
```

## 📊 Database Schema

```
-- Core tables
Users: id, username, email, rating_chaturaji, rating_enochian
Games: id, variant, status, created_at, finished_at, winner_team
GamePlayers: game_id, user_id, color, final_score, position
GameMoves: id, game_id, move_number, player_color, from_pos, to_pos

-- Redis cache keys
game:{game_id}:state           # Current game state
game:{game_id}:connections     # Connected players
player:{player_id}:session     # Player session data
```

## 🚀 Deployment

### **Production Setup**
```sh
# Environment variables
export DATABASE_URL="postgresql://user:pass@localhost/chess4p"
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="your-production-secret-key"

# Run with Gunicorn
pip install gunicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### **Docker Deployment**
```sh
# Dockerfile included
docker build -t chess4p .
docker run -p 8000:8000 chess4p
```

## 🎯 Development Roadmap

### **Phase 1: MVP** ✅
- [x] Basic 4-player board
- [x] Chaturaji scoring system
- [x] Real-time WebSocket communication
- [x] PostgreSQL persistence

### **Phase 2: Enhanced Features**
- [ ] Enochian chess team mechanics
- [ ] Player rating system
- [ ] Game replay functionality
- [ ] Spectator mode

### **Phase 3: Production Ready**
- [ ] Electron desktop app
- [ ] Mobile responsive design
- [ ] Advanced anti-cheat
- [ ] Tournament system

## 🤝 Contributing

```sh
# Setup development environment
git clone <repo>
cd 4player-chess
uv sync
uv run pytest

# Make changes and test
uv run black src/
uv run ruff check src/
uv run pytest

# Submit pull request
```

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Links

- **Documentation**: [Coming Soon]
- **Issues**: [GitHub Issues]
- **Discord**: [Game Development Server]

---

Built with ❤️ by Jon  
Cybersecurity -  Gaming -  Modern Web Tech

## 📚 Chess Variants Resources

### **Chaturaji References**
- Historical rules and scoring system
- Ancient Indian chess manuscripts
- Modern tournament implementations

### **Enochian Chess References**
- Golden Dawn magical system
- Victorian occult chess variants
- Team-based gameplay mechanics

---

*Ready to revolutionize 4-player chess? Let's code! 🚀*
