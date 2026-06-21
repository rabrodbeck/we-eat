import json
from sqlalchemy import create_engine, Column, String, Integer, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Setup engine - connect_args chck is only needed for SQLite multithreading
is_sqlite = settings.DATABASE_URL.startswith("sqlite")
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if is_sqlite else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DBFamilyMember(Base):
    __tablename__ = "family_members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True) # Firebase UID of the owner
    name = Column(String, index=True)
    dislikes_json = Column(Text, default="[]") # List of dislikes stored as JSON string

    @property
    def dislikes(self):
        try:
            return json.loads(self.dislikes_json)
        except Exception:
            return []
        
    @dislikes.setter
    def dislikes(self, value):
        self.dislikes_json = json.dumps(value)

# Automatically create tables (for dev SQLite; production migration handles Supabase)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()