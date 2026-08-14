from litellm import completion
from app.core.config import settings
from app.models.user import User, UsageRecord
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import asyncio
import json

class AIService:
    def __init__(self, db: Session):
        self.db = db
        
    async def check_usage_limits(self, user: User) -> bool:
        """ユーザーの使用制限をチェック"""
        plan = settings.PRICING_PLANS[user.subscription_plan]
        
        # 日次/月次の使用量を計算
        now = datetime.utcnow()
        if user.subscription_plan == "free":
            # フリープランは日次制限
            start_time = now - timedelta(days=1)
        else:
            # その他のプランは月次制限
            start_time = now - timedelta(days=30)
            
        total_tokens = sum(
            record.tokens_used
            for record in user.usage_records
            if record.timestamp > start_time
        )
        
        return total_tokens < plan["token_limit"]
        
    async def process_ai_request(
        self,
        user: User,
        messages: list,
        model: str = "gpt-3.5-turbo"
    ):
        """AI リクエストの処理"""
        # 使用制限チェック
        if not await self.check_usage_limits(user):
            raise ValueError("Usage limit exceeded")
            
        # コスト最適化のためのモデル選択
        selected_model = self.select_optimal_model(messages, model)
        
        try:
            # LiteLLM を使用してリクエストを処理
            response = await completion(
                model=selected_model,
                messages=messages
            )
            
            # 使用量を記録
            usage_record = UsageRecord(
                user_id=user.id,
                model=selected_model,
                tokens_used=response.usage.total_tokens,
                cost=self.calculate_cost(
                    response.usage.total_tokens,
                    selected_model
                )
            )
            self.db.add(usage_record)
            await self.db.commit()
            
            return response
            
        except Exception as e:
            # エラーログ記録
            print(f"Error processing AI request: {e}")
            raise
            
    def select_optimal_model(self, messages: list, preferred_model: str) -> str:
        """コスト最適化のためのモデル選択"""
        # メッセージの複雑さを評価
        complexity = self.evaluate_complexity(messages)
        
        if complexity < 0.3:
            return "gpt-3.5-turbo"  # 簡単なリクエスト
        elif complexity < 0.7:
            return preferred_model  # ユーザー指定モデル
        else:
            return "gpt-4"  # 複雑なリクエスト
            
    def evaluate_complexity(self, messages: list) -> float:
        """メッセージの複雑さを評価"""
        # 簡単な複雑さ評価ロジック
        total_length = sum(len(m["content"]) for m in messages)
        num_messages = len(messages)
        
        # 長さと対話の複雑さに基づくスコア
        complexity = min(1.0, (total_length / 1000) * 0.5 + (num_messages / 10) * 0.5)
        
        return complexity
        
    def calculate_cost(self, tokens: int, model: str) -> float:
        """トークン使用量からコストを計算"""
        cost_per_1k = settings.AI_COSTS.get(model, 0.002)  # デフォルトはgpt-3.5-turbo
        return (tokens / 1000) * cost_per_1k