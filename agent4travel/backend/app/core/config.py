from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    
    # LLM API - 支持多种 LLM 提供商
    # 阿里云百炼
    BAILIAN_API_KEY: Optional[str] = None
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    # 默认使用的 LLM 提供商 (bailian 或 openai)
    LLM_PROVIDER: str = "openai"
    
    # 高德地图
    GAODE_WEB_API_KEY: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

