from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI_Prompt_Safe"
    app_version: str = "1.0.0"
    app_description: str = "AI大模型Prompt安全防护系统"

    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    database_url: str = "sqlite+aiosqlite:///./data/example_db.db"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    max_input_chars: int = 2000
    max_output_chars: int = 4096
    obfuscation_threshold: float = 0.3
    safety_threshold: float = 0.85

    session_max_turns: int = 20
    session_max_duration_minutes: int = 30
    session_idle_timeout_minutes: int = 5
    context_max_tokens: int = 4096

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()