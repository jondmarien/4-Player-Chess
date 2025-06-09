import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# Load environment
load_dotenv()

Base = declarative_base()

class Game(Base):
    __tablename__ = "games"
    
    id = Column(String, primary_key=True, index=True)
    variant = Column(String, nullable=False)  # 'chaturaji' or 'enochian'
    status = Column(String, default="waiting")  # waiting, active, finished
    current_player = Column(Integer, default=0)  # 0-3 for four players
    created_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    
    # Game state as JSON
    board_state = Column(Text)  # JSON string of board
    scores = Column(Text)  # JSON string of scores

class GamePlayer(Base):
    __tablename__ = "game_players"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String, ForeignKey("games.id"))
    player_name = Column(String, nullable=False)
    color = Column(String, nullable=False)  # red, blue, yellow, green
    final_score = Column(Integer, default=0)
    is_connected = Column(Boolean, default=True)

class GameMove(Base):
    __tablename__ = "game_moves"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String, ForeignKey("games.id"))
    move_number = Column(Integer, nullable=False)
    player_color = Column(String, nullable=False)
    from_position = Column(String, nullable=False)  # e.g., "a1"
    to_position = Column(String, nullable=False)    # e.g., "a2"
    piece_type = Column(String, nullable=False)
    captured_piece = Column(String, nullable=True)
    points_earned = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)

if __name__ == "__main__":
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in .env file")
        exit(1)
    
    print(f"Using DATABASE_URL: {DATABASE_URL}")
    
    engine = create_engine(DATABASE_URL)
    
    try:
        # Test connection first
        with engine.connect() as conn:
            print("✅ Database connection successful")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"✅ Tables created: {tables}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
