from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.billing_service import BillingService
from app.core.deps import get_current_user, get_db
from app.schemas.billing import (
    SubscriptionCreate,
    SubscriptionResponse,
    UsageCosts
)
import stripe

router = APIRouter()

@router.post("/subscribe", response_model=SubscriptionResponse)
async def create_subscription(
    subscription: SubscriptionCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """新規サブスクリプションの作成"""
    billing_service = BillingService(db)
    
    try:
        subscription = await billing_service.create_subscription(
            user=current_user,
            plan_id=subscription.plan_id,
            payment_method_id=subscription.payment_method_id
        )
        
        return SubscriptionResponse(
            subscription_id=subscription.id,
            status=subscription.status,
            current_period_end=subscription.current_period_end
        )
        
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/usage-costs", response_model=UsageCosts)
async def get_usage_costs(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """使用量とコストの取得"""
    billing_service = BillingService(db)
    
    try:
        costs = await billing_service.calculate_usage_costs(current_user)
        profitability = await billing_service.check_profitability(current_user)
        
        return UsageCosts(
            ai_usage=costs["ai_usage"],
            instances=costs["instances"],
            storage=costs["storage"],
            total=costs["total"],
            margin_percentage=profitability["margin_percentage"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error calculating usage costs")

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Stripeウェブフックの処理"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        
        # イベントタイプに基づく処理
        if event.type == "invoice.paid":
            await handle_successful_payment(event.data.object, db)
        elif event.type == "invoice.payment_failed":
            await handle_failed_payment(event.data.object, db)
            
        return {"status": "success"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def handle_successful_payment(invoice, db):
    """支払い成功時の処理"""
    user = db.query(User).filter(
        User.stripe_customer_id == invoice.customer
    ).first()
    
    if user:
        # ユーザーの利用制限を更新
        user.subscription_status = "active"
        db.commit()

async def handle_failed_payment(invoice, db):
    """支払い失敗時の処理"""
    user = db.query(User).filter(
        User.stripe_customer_id == invoice.customer
    ).first()
    
    if user:
        # ユーザーに通知を送信
        # 利用制限の適用
        user.subscription_status = "past_due"
        db.commit()