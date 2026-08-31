import stripe
from app.core.config import settings
from app.models.user import User, UsageRecord, FaxUsageRecord
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any

stripe.api_key = settings.STRIPE_SECRET_KEY

class BillingService:
    def __init__(self, db: Session):
        self.db = db
        
    async def create_customer(self, user: User, payment_method_id: str = None):
        """Stripeカスタマーの作成"""
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.full_name,
                payment_method=payment_method_id,
                invoice_settings={
                    'default_payment_method': payment_method_id
                } if payment_method_id else None
            )
            
            user.stripe_customer_id = customer.id
            self.db.commit()
            
            return customer
            
        except stripe.error.StripeError as e:
            print(f"Error creating customer: {e}")
            raise
            
    async def create_subscription(
        self,
        user: User,
        plan_id: str,
        payment_method_id: str = None
    ):
        """サブスクリプションの作成"""
        try:
            if not user.stripe_customer_id:
                await self.create_customer(user, payment_method_id)
                
            subscription = stripe.Subscription.create(
                customer=user.stripe_customer_id,
                items=[{'price': plan_id}],
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent'],
            )
            
            return subscription
            
        except stripe.error.StripeError as e:
            print(f"Error creating subscription: {e}")
            raise
            
    async def calculate_usage_costs(self, user: User, days: int = 30) -> Dict[str, float]:
        """使用量ベースのコスト計算"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # AI使用量のコスト
        ai_usage = sum(
            record.cost
            for record in user.usage_records
            if record.timestamp > start_date
        )
        
        # インスタンス使用量のコスト
        instance_costs = self.calculate_instance_costs(user, start_date)
        
        # ストレージコスト
        storage_costs = self.calculate_storage_costs(user)
        
        return {
            "ai_usage": ai_usage,
            "instances": instance_costs,
            "storage": storage_costs,
            "total": ai_usage + instance_costs + storage_costs
        }
        
    def calculate_instance_costs(self, user: User, start_date: datetime) -> float:
        """インスタンスの使用コスト計算"""
        total_cost = 0
        for instance in user.instances:
            if instance.status == "running":
                # インスタンスタイプに基づくコスト計算
                hourly_rate = self.get_instance_hourly_rate(instance.instance_type)
                hours = (datetime.utcnow() - start_date).total_seconds() / 3600
                total_cost += hourly_rate * hours
        return total_cost
        
    def calculate_storage_costs(self, user: User) -> float:
        """ストレージコストの計算"""
        # 簡単な計算例: $0.1 per GB per month
        storage_rate = 0.1
        total_storage = sum(
            self.get_instance_storage(instance)
            for instance in user.instances
        )
        return total_storage * storage_rate
        
    def get_instance_hourly_rate(self, instance_type: str) -> float:
        """インスタンスタイプごとの時間単価"""
        rates = {
            "t3.micro": 0.0104,
            "t3.small": 0.0208,
            "t3.medium": 0.0416,
        }
        return rates.get(instance_type, 0.0208)  # デフォルトはt3.small
        
    def get_instance_storage(self, instance: Any) -> float:
        """インスタンスのストレージ使用量（GB）"""
        # 実際の実装ではインスタンスのストレージ使用量を取得
        return 10.0  # デフォルト値
        
    async def check_profitability(self, user: User) -> Dict[str, Any]:
        """収益性チェック"""
        costs = await self.calculate_usage_costs(user)
        revenue = self.get_monthly_revenue(user)
        
        margin = revenue - costs["total"]
        margin_percentage = (margin / revenue * 100) if revenue > 0 else 0
        
        return {
            "costs": costs,
            "revenue": revenue,
            "margin": margin,
            "margin_percentage": margin_percentage,
            "is_profitable": margin_percentage >= 20  # 20%以上を収益性あり判定
        }
        
    def get_monthly_revenue(self, user: User) -> float:
        """月間収益の計算"""
        plan = settings.PRICING_PLANS.get(user.subscription_plan, settings.PRICING_PLANS["free"])
        return plan["price"]  # 基本料金のみ（追加料金は未実装）

    async def calculate_fax_costs(self, user: User, days: int = 30) -> Dict[str, Any]:
        """FAX使用量のコスト計算（teaiクレジット経由のみ）"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        fax_records = [
            record for record in user.fax_usage_records
            if record.timestamp > start_date
        ]
        
        total_faxes = len(fax_records)
        total_credits = sum(record.cost_credits for record in fax_records)
        
        return {
            "fax_count": total_faxes,
            "total_credits": total_credits,
            "records": [
                {
                    "fax_id": r.fax_id,
                    "provider": r.provider,
                    "to_number": r.to_number,
                    "pages": r.pages,
                    "cost_credits": r.cost_credits,
                    "status": r.status,
                    "timestamp": r.timestamp.isoformat(),
                }
                for r in fax_records
            ]
        }

    async def check_fax_profitability(self, user: User) -> Dict[str, Any]:
        """FAX収益性チェック"""
        fax_costs = await self.calculate_fax_costs(user)
        revenue = self.get_monthly_revenue(user)
        
        # FAXコストをドル換算（1クレジット = $0.01想定）
        fax_cost_usd = fax_costs["total_credits"] * 0.01
        
        margin = revenue - fax_cost_usd
        margin_percentage = (margin / revenue * 100) if revenue > 0 else 0
        
        return {
            "fax_costs": fax_costs,
            "fax_cost_usd": fax_cost_usd,
            "revenue": revenue,
            "margin": margin,
            "margin_percentage": margin_percentage,
            "is_profitable": margin_percentage >= 20,
        }