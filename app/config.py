from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    SAFETY_THRESHOLD: float = 0.5
    ENABLE_MASK: bool = True
    ENABLE_CHECK: bool = True
    
    SAFETY_MODEL: str = "ynygljj/Unified_Prompt_Guard"
    MAX_PROMPT_TOKENS: int = 32768
    
    SAFETY_CHECK_TIMEOUT: int = 3
    LLM_PROXY_TIMEOUT: int = 30
    
    FALLBACK_STRATEGY: str = "block"
    
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    class Config:
        env_file = ".env"


settings = Settings()