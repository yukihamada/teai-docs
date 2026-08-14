from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.ai_service import AIService
from app.services.billing_service import BillingService
from app.core.deps import get_current_user, get_db
from app.schemas.ai import AIRequest, AIResponse
from typing import List

router = APIRouter()

@router.post("/completion", response_model=AIResponse)
async def create_completion(
    request: AIRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """AI補完リクエストの処理"""
    ai_service = AIService(db)
    billing_service = BillingService(db)
    
    try:
        # 収益性チェック
        profitability = await billing_service.check_profitability(current_user)
        if not profitability["is_profitable"]:
            # 収益性が低い場合は警告を記録
            print(f"Low profitability warning for user {current_user.id}")
        
        # AIリクエストの処理
        response = await ai_service.process_ai_request(
            user=current_user,
            messages=request.messages,
            model=request.model
        )
        
        return AIResponse(
            text=response.choices[0].message.content,
            usage=response.usage,
            model=response.model
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")