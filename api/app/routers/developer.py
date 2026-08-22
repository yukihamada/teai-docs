from fastapi import APIRouter, HTTPException
from app.schemas.developer import (
    ApiKeyCreate,
    ApiKeyResponse,
    DeveloperProfile,
    DeveloperStats
)
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/api-keys", response_model=ApiKeyResponse)
async def create_api_key(
    request: ApiKeyCreate,
):
    """APIキーの作成（簡素化版）"""
    try:
        # 簡素化されたAPIキー作成
        api_key = f"teai_{uuid.uuid4().hex[:16]}"
        
        return ApiKeyResponse(
            api_key=api_key,
            name=request.name,
            created_at=datetime.utcnow(),
            permissions=request.permissions
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating API key: {str(e)}")

@router.get("/profile", response_model=DeveloperProfile)
async def get_developer_profile():
    """開発者プロフィールの取得"""
    return DeveloperProfile(
        user_id="",
        email="",
        api_keys_count=0,
        total_requests=0,
        total_cost=0.0,
        created_at=datetime.utcnow()
    )

@router.get("/stats", response_model=DeveloperStats)
async def get_developer_stats():
    """開発者統計の取得"""
    return DeveloperStats(
        requests_today=0,
        requests_this_month=0,
        cost_today=0.0,
        cost_this_month=0.0,
        top_models=[],
        error_rate=0.0
    )

@router.post("/invite")
async def invite_developer(
    email: str,
):
    """開発者招待の送信"""
    try:
        # 招待メールの送信（Resend等の外部サービスと連携予定）
        print(f"Invitation sent to {email}")
        return {"status": "invitation_sent", "email": email}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending invitation: {str(e)}")

@router.get("/docs")
async def get_developer_docs():
    """開発者ドキュメントの取得"""
    return {
        "getting_started": {
            "title": "Getting Started with teai.io API",
            "steps": [
                "1. Create an account",
                "2. Generate an API key",
                "3. Make your first API call",
                "4. Monitor usage and costs"
            ]
        },
        "api_reference": {
            "base_url": "https://api.teai.io/v1",
            "authentication": "Bearer token (API key)",
            "rate_limits": "1000 requests per hour",
            "endpoints": {
                "ai_completion": "/ai/completion",
                "billing": "/billing",
                "usage": "/usage",
                "developer_api_keys": "/developer/api-keys",
                "developer_profile": "/developer/profile",
                "developer_stats": "/developer/stats"
            }
        },
        "examples": {
            "python": """
import requests

headers = {
    "Authorization": "Bearer your_api_key_here",
    "Content-Type": "application/json"
}

data = {
    "messages": [{"role": "user", "content": "Hello, world!"}],
    "model": "gpt-4"
}

response = requests.post(
    "https://api.teai.io/v1/ai/completion",
    headers=headers,
    json=data
)

print(response.json())
            """,
            "javascript": """
const response = await fetch('https://api.teai.io/v1/ai/completion', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer your_api_key_here',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        messages: [{role: 'user', content: 'Hello, world!'}],
        model: 'gpt-4'
    })
});

const data = await response.json();
console.log(data);
            """
        }
    }