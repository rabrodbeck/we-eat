from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PORT: int = 8000
    HOST: str = "127.0.0.1"
    ENVIRONMENT: str = "development"
    OPENAI_API_KEY: str = ""
    DATABASE_URL: str = "sqlite:///./we_eat.db"
    FIREBASE_PROJECT_ID: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()