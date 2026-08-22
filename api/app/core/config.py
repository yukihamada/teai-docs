from pydantic_settings import BaseSettings
from typing import Optional, Dict

class Settings(BaseSettings):
    PROJECT_NAME: str = "TeAI.io API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # セキュリティ
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Stripe設定
    STRIPE_SECRET_KEY: str = "your-stripe-secret-key"
    STRIPE_WEBHOOK_SECRET: str = "your-stripe-webhook-secret"
    
    # データベース
    DATABASE_URL: str = "sqlite:///./test.db"
    
    # LiteLLM設定
    OPENAI_API_KEY: str = "your-openai-api-key"
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # 料金プラン（月額）
    PRICING_PLANS: Dict[str, dict] = {
        "free": {
            "price": 0,
            "token_limit": 1000,  # 1日あたり
            "instance_limit": 1,
            "storage_limit": 5,  # GB
            "uptime_limit": 12,  # 時間/日
        },
        "basic": {
            "price": 9800,
            "token_limit": 100000,  # 月あたり
            "instance_limit": 1,
            "storage_limit": 20,
            "uptime_limit": 24,
        },
        "pro": {
            "price": 29800,
            "token_limit": 500000,
            "instance_limit": 2,
            "storage_limit": 50,
            "uptime_limit": 24,
        },
        "enterprise": {
            "price": 98000,
            "token_limit": -1,  # 無制限
            "instance_limit": -1,
            "storage_limit": 100,
            "uptime_limit": 24,
        }
    }
    
    # コスト設定
    AI_COSTS: Dict[str, float] = {
        "gpt-4": 0.03,  # ドル/1K tokens
        "gpt-3.5-turbo": 0.002,
        "claude-2": 0.008,
    }

settings = Settings()