from litellm import completion
from app.core.config import settings
from app.models.user import User, UsageRecord
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import asyncio
import json
from functools import lru_cache # Import lru_cache

class AIService:
    def __init__(self, db: Session):
        self.db = db
        # Placeholder for a more comprehensive model registry
        # In a real system, this would be loaded from a config file or database
        self.model_registry = {
            "gpt-3.5-turbo": {"cost_per_1k": 0.002, "capabilities": ["chat", "general"]},
            "gpt-4": {"cost_per_1k": 0.03, "capabilities": ["chat", "advanced"]},
            "claude-haiku": {"cost_per_1k": 0.00025, "capabilities": ["chat", "fast"]},
            "claude-opus": {"cost_per_1k": 0.015, "capabilities": ["chat", "complex"]},
            "kimi-k3": {"cost_per_1k": 0.0015, "capabilities": ["chat", "long_context"]},
            "deepseek-v4-pro": {"cost_per_1k": 0.00023, "capabilities": ["chat", "coding"]},
            # ... many more models would be listed here
        }
        
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
            
    def get_model_capabilities(self, model_name: str) -> list:
        """指定されたモデルの能力を返す"""
        return self.model_registry.get(model_name, {}).get("capabilities", [])

    def get_model_cost(self, model_name: str) -> float:
        """指定されたモデルの1kトークンあたりのコストを返す"""
        return self.model_registry.get(model_name, {}).get("cost_per_1k", 0.0) # Fallback to 0.0 if not found

    @lru_cache(maxsize=128) # Cache the results of model selection
    def _cached_select_optimal_model(self, messages_hash: tuple, preferred_model: str) -> str:
        # Convert messages_hash back to messages list for processing if needed
        # For simplicity, we'll assume messages_hash is sufficient for caching decision
        # In a real implementation, you'd deserialize messages_hash if the full messages are needed
        messages = json.loads(messages_hash[0]) # Assuming messages_hash[0] is JSON string of messages
        
        return self.select_optimal_model_logic(messages, preferred_model)

    def select_optimal_model_logic(self, messages: list, preferred_model: str) -> str:
        """コスト最適化と要件に基づいたモデル選択 (より動的なロジックの骨子)"""
        complexity = self.evaluate_complexity(messages)
        
        # ユーザー指定モデルがレジストリに存在するか確認
        if preferred_model in self.model_registry:
            # 複雑性に応じて、ユーザー指定モデル、またはより安価/強力なモデルを推奨
            if complexity < 0.3: # 簡単なリクエスト
                # 安価なモデルの中から、preferred_modelの能力を満たすものを探す
                candidates = [m for m, data in self.model_registry.items() if self.get_model_cost(m) < self.get_model_cost(preferred_model) and all(cap in data["capabilities"] for cap in self.get_model_capabilities(preferred_model))]
                if candidates: # 暫定的に最も安いものを選択
                    return min(candidates, key=lambda m: self.get_model_cost(m))
                return preferred_model
            elif complexity < 0.7: # 中程度の複雑さ
                return preferred_model
            else: # 複雑なリクエスト
                # より強力なモデルの中から、preferred_modelの能力を満たすものを探す
                candidates = [m for m, data in self.model_registry.items() if "advanced" in data["capabilities"] and all(cap in data["capabilities"] for cap in self.get_model_capabilities(preferred_model))]
                if candidates: # 暫定的に最も強力なものを選択
                    return max(candidates, key=lambda m: self.get_model_cost(m)) # 高コスト＝強力と仮定
                return preferred_model
        
        # ユーザー指定モデルがレジストリにない場合、デフォルトまたはフォールバックロジック
        if complexity < 0.3:
            return "gpt-3.5-turbo"  # 簡単なリクエストのデフォルト
        elif complexity < 0.7:
            return "claude-haiku" # 中程度の複雑さのデフォルト
        else:
            return "gpt-4"  # 複雑なリクエストのデフォルト
            
    def select_optimal_model(self, messages: list, preferred_model: str) -> str:
        # messagesリストをハッシュ可能な形式に変換
        messages_hash = (json.dumps(messages, sort_keys=True),)
        return self._cached_select_optimal_model(messages_hash, preferred_model)

    def evaluate_complexity(self, messages: list) -> float:
        """メッセージの複雑さを評価"""
        # 簡単な複雑さ評価ロジック
        total_length = sum(len(m["content"]) for m in messages)
        num_messages = len(messages)
        
        # 長さと対話の複雑さに基づくスコア
        complexity = min(1.0, (total_length / 1000) * 0.5 + (num_messages / 10) * 0.5)
        
        return complexity

    async def ensemble_models(self, messages: list, models_to_use: list) -> dict:
        """複数のLLMを呼び出し、その応答を統合する骨子"""
        responses = []
        tasks = []

        for model_name in models_to_use:
            # 各モデルへのリクエストを非同期で実行
            tasks.append(completion(model=model_name, messages=messages))
        
        # 全てのモデルからの応答を待機
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for model_name, result in zip(models_to_use, results):
            if isinstance(result, Exception):
                print(f"Error from model {model_name}: {result}")
                responses.append({"model": model_name, "error": str(result)})
            else:
                # ここで結果を統合するロジックを実装
                # 例: 最も長い応答を採用、特定の情報のみ抽出、重み付けなど
                responses.append({"model": model_name, "response": result.choices[0].message.content})
        
        # 統合された最終応答を生成する (簡易的な例)
        if responses:
            # ここでは最初の成功した応答を返す簡易的な例
            for res in responses:
                if "response" in res:
                    return {"ensemble_result": res["response"], "details": responses}
            return {"ensemble_result": "No successful response from ensemble.", "details": responses}
        else:
            return {"ensemble_result": "No models in ensemble.", "details": []}

    # Further down, `process_ai_request` could be modified to call `ensemble_models`
    # based on certain conditions (e.g., if a specific 'ensemble_model' is requested).
