import json
from sqlalchemy import create_engine, Column, String, Integer, Text, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

is_sqlite = settings.DATABASE_URL.startswith("sqlite")
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if is_sqlite else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DBFamily(Base):
    __tablename__ = "families"

    id = Column(String, primary_key=True, index=True) # UUID stored as string
    family_name = Column(String, nullable=False)
    created_by = Column(String, nullable=False) # Firebase UID of the head of family

class DBFamilyMember(Base):
    __tablename__ = "family_members"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(String, ForeignKey("families.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, unique=True, index=True, nullable=True) # Mapped when invite accepted
    name = Column(String, index=True, nullable=False)
    dislikes_json = Column(Text, default="[]", nullable=False)
    email = Column(String, nullable=True) # Invite email
    invite_token = Column(String, unique=True, index=True, nullable=True) # Unique invite URL key
    invite_accepted = Column(Boolean, default=False, nullable=False)
    role = Column(String, default="member", nullable=False) # 'head' or 'member'

    @property
    def dislikes(self):
        try:
            return json.loads(self.dislikes_json)
        except Exception:
            return []
        
    @dislikes.setter
    def dislikes(self, value):
        self.dislikes_json = json.dumps(value)

# Automatically create tables (for dev SQLite)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()