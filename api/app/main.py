from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import ai, billing, developer

app = FastAPI(
    title="teai.io API",
    version="1.0.0",
    openapi_url="/v1/openapi.json"
)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(ai.router, prefix="/v1/ai", tags=["ai"])
app.include_router(billing.router, prefix="/v1/billing", tags=["billing"])
app.include_router(developer.router, prefix="/v1/developer", tags=["developer"])

@app.get("/")
def read_root():
    return {
        "service": "teai.io API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "developer_docs": "/v1/developer/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}