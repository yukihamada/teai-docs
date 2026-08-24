from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.fax_service import FaxService
from app.core.deps import get_current_user, get_db
from app.schemas.fax import (
    FaxSendRequest,
    FaxSendResponse,
    FaxStatusResponse,
    FaxLimitCheck,
    FaxProvider,
)

router = APIRouter()


@router.post("/send", response_model=FaxSendResponse)
async def send_fax(
    request: FaxSendRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """FAX送信"""
    fax_service = FaxService(db)
    
    try:
        response = await fax_service.send_fax(current_user, request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/status/{fax_id}", response_model=FaxStatusResponse)
async def get_fax_status(
    fax_id: str,
    provider: FaxProvider = FaxProvider.TELNYX,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """FAX送信ステータス取得"""
    fax_service = FaxService(db)
    
    try:
        response = await fax_service.get_fax_status(current_user, fax_id, provider)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/limit", response_model=FaxLimitCheck)
async def check_fax_limit(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """FAX送信制限チェック"""
    fax_service = FaxService(db)
    
    try:
        response = await fax_service.check_fax_limit(current_user)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")