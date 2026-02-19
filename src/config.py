from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    API_PORT: int = 8080
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    CACHE_TTL_SECONDS: int = 3600
    DATABASE_URL: str = "sqlite:///./products.db"

settings = Settings()
