# ARCHIVED — この課金コードは旧Python実装。現行課金は nanobot (Rust) が実体。
# 参照先: nanobot/crates/teai-core/src/service/stripe.rs
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, ClassVar

class Settings(BaseSettings):
    PROJECT_NAME: str = "TeAI.io API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # セキュリティ（必須: 環境変数で設定）
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Stripe設定（必須: 環境変数で設定）
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str

    # データベース（必須: 環境変数で設定）
    DATABASE_URL: str

    # LiteLLM設定（必須: 環境変数で設定）
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: Optional[str] = None

    # CORS許可オリジン（カンマ区切りで環境変数から、デフォルトはteai.io）
    ALLOWED_ORIGINS: str = "https://www.teai.io,https://dashboard.teai.io"
    
    # FAX設定（システム共通・teaiクレジット経由用）
    TELNYX_API_KEY: Optional[str] = None
    TELNYX_CONNECTION_ID: Optional[str] = None
    TELNYX_FROM: Optional[str] = None
    
    PHAXIO_API_KEY: Optional[str] = None
    PHAXIO_API_SECRET: Optional[str] = None
    
    # 料金プラン（月額）
    PRICING_PLANS: ClassVar[Dict[str, Dict[str, Any]]] = {
        "free": {
            "price": 0,
            "token_limit": 1000,  # 1日あたり
            "instance_limit": 1,
            "storage_limit": 5,  # GB
            "uptime_limit": 12,  # 時間/日
            "fax_daily_limit": 3,  # 1日3通まで
        },
        "basic": {
            "price": 9800,
            "token_limit": 100000,  # 月あたり
            "instance_limit": 1,
            "storage_limit": 20,
            "uptime_limit": 24,
            "fax_daily_limit": 10,
        },
        "pro": {
            "price": 29800,
            "token_limit": 500000,
            "instance_limit": 2,
            "storage_limit": 50,
            "uptime_limit": 24,
            "fax_daily_limit": 50,
        },
        "enterprise": {
            "price": 98000,
            "token_limit": -1,  # 無制限
            "instance_limit": -1,
            "storage_limit": 100,
            "uptime_limit": 24,
            "fax_daily_limit": -1,  # 無制限
        }
    }
    
    # コスト設定
    AI_COSTS: ClassVar[Dict[str, float]] = {
        "gpt-4": 0.03,  # ドル/1K tokens
        "gpt-3.5-turbo": 0.002,
        "claude-2": 0.008,
    }
    
    # FAXコスト（teaiクレジット）
    FAX_COST_CREDITS: int = 1  # 1通あたり1クレジット

    @property
    def allowed_origins_list(self) -> list[str]:
        """ALLOWED_ORIGINS をリストに変換"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

settings = Settings()