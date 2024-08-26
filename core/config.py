import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    
    # Database
    DATABASE_URL: str = os.getenv('DATABASE_URL')

    # Hugging Face Api
    DATASET_API_URL: str = os.getenv('DATASET_API_URL', 'https://datasets-server.huggingface.co/')
    
    # JWT 
    JWT_SECRET: str = os.getenv('JWT_SECRET')
    JWT_ALGORITHM: str = os.getenv('JWT_ALGORITHM', "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv('JWT_TOKEN_EXPIRE_MINUTES', 120)
    
def get_settings() -> Settings:
    return Settings()