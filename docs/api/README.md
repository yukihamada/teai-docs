# API仕様書

## 概要

TeAI.io APIは、OpenHandsホスティングサービスを管理するためのRESTful APIです。

## 基本情報

- ベースURL: `https://api.teai.io/v1`
- 認証: Bearer Token
- レスポンス形式: JSON
- 文字コード: UTF-8

## 認証

### アクセストークンの取得

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password"
}
```

レスポンス:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

## インスタンス管理

### インスタンス一覧の取得

```http
GET /instances
Authorization: Bearer {token}
```

レスポンス:
```json
{
  "instances": [
    {
      "id": "inst-001",
      "name": "production-1",
      "status": "running",
      "type": "t3.small",
      "created_at": "2025-01-01T00:00:00Z",
      "domain": "app1.teai.io"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 10
}
```

### インスタンスの作成

```http
POST /instances
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "production-1",
  "type": "t3.small",
  "storage": 20
}
```

レスポンス:
```json
{
  "id": "inst-001",
  "name": "production-1",
  "status": "creating",
  "type": "t3.small",
  "created_at": "2025-01-01T00:00:00Z",
  "domain": "app1.teai.io"
}
```

### インスタンスの更新

```http
PATCH /instances/{instance_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "type": "t3.medium",
  "storage": 40
}
```

レスポンス:
```json
{
  "id": "inst-001",
  "name": "production-1",
  "status": "updating",
  "type": "t3.medium",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-02T00:00:00Z",
  "domain": "app1.teai.io"
}
```

### インスタンスの削除

```http
DELETE /instances/{instance_id}
Authorization: Bearer {token}
```

レスポンス:
```json
{
  "message": "Instance deletion initiated",
  "status": "deleting"
}
```

## バックアップ管理

### バックアップの作成

```http
POST /instances/{instance_id}/backups
Authorization: Bearer {token}
Content-Type: application/json

{
  "description": "Pre-deployment backup"
}
```

レスポンス:
```json
{
  "id": "bkp-001",
  "instance_id": "inst-001",
  "status": "creating",
  "description": "Pre-deployment backup",
  "created_at": "2025-01-01T00:00:00Z"
}
```

### バックアップの一覧取得

```http
GET /instances/{instance_id}/backups
Authorization: Bearer {token}
```

レスポンス:
```json
{
  "backups": [
    {
      "id": "bkp-001",
      "instance_id": "inst-001",
      "status": "available",
      "description": "Pre-deployment backup",
      "created_at": "2025-01-01T00:00:00Z",
      "size": 10240
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 10
}
```

## モニタリング

### メトリクスの取得

```http
GET /instances/{instance_id}/metrics
Authorization: Bearer {token}
Query Parameters:
  - metric: cpu|memory|disk|network
  - period: 5m|1h|1d
  - start: 2025-01-01T00:00:00Z
  - end: 2025-01-02T00:00:00Z
```

レスポンス:
```json
{
  "metrics": [
    {
      "timestamp": "2025-01-01T00:00:00Z",
      "cpu": 45.2,
      "memory": 78.5,
      "disk": 60.0,
      "network": {
        "in": 1024,
        "out": 2048
      }
    }
  ],
  "period": "5m"
}
```

### アラートの設定

```http
POST /instances/{instance_id}/alerts
Authorization: Bearer {token}
Content-Type: application/json

{
  "metric": "cpu",
  "threshold": 80,
  "period": "5m",
  "actions": [
    {
      "type": "email",
      "target": "admin@example.com"
    }
  ]
}
```

レスポンス:
```json
{
  "id": "alert-001",
  "instance_id": "inst-001",
  "metric": "cpu",
  "threshold": 80,
  "period": "5m",
  "status": "active",
  "created_at": "2025-01-01T00:00:00Z"
}
```

## 課金・請求

### 使用量の取得

```http
GET /billing/usage
Authorization: Bearer {token}
Query Parameters:
  - start: 2025-01-01
  - end: 2025-01-31
```

レスポンス:
```json
{
  "period": {
    "start": "2025-01-01",
    "end": "2025-01-31"
  },
  "usage": {
    "compute": {
      "hours": 744,
      "cost": 15000
    },
    "storage": {
      "gb": 100,
      "cost": 1000
    },
    "transfer": {
      "gb": 500,
      "cost": 5000
    }
  },
  "total": 21000
}
```

### 請求履歴の取得

```http
GET /billing/invoices
Authorization: Bearer {token}
```

レスポンス:
```json
{
  "invoices": [
    {
      "id": "inv-001",
      "period": "2025-01",
      "amount": 21000,
      "status": "paid",
      "paid_at": "2025-02-01T00:00:00Z",
      "url": "https://..."
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 10
}
```

## エラーレスポンス

### 400 Bad Request

```json
{
  "error": {
    "code": "validation_error",
    "message": "Invalid request parameters",
    "details": {
      "name": ["is required"]
    }
  }
}
```

### 401 Unauthorized

```json
{
  "error": {
    "code": "unauthorized",
    "message": "Invalid or expired token"
  }
}
```

### 403 Forbidden

```json
{
  "error": {
    "code": "forbidden",
    "message": "Insufficient permissions"
  }
}
```

### 404 Not Found

```json
{
  "error": {
    "code": "not_found",
    "message": "Resource not found"
  }
}
```

### 429 Too Many Requests

```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Too many requests",
    "retry_after": 60
  }
}
```

### 500 Internal Server Error

```json
{
  "error": {
    "code": "internal_error",
    "message": "Internal server error",
    "request_id": "req-001"
  }
}
```

## レート制限

- デフォルト: 1000 requests/hour
- バースト: 100 requests/minute
- ヘッダー:
  - X-RateLimit-Limit
  - X-RateLimit-Remaining
  - X-RateLimit-Reset

## Webhooks

### イベント通知

エンドポイント設定:
```http
POST /webhooks
Authorization: Bearer {token}
Content-Type: application/json

{
  "url": "https://example.com/webhook",
  "events": ["instance.created", "instance.updated", "instance.deleted"],
  "secret": "webhook-secret"
}
```

通知ペイロード:
```json
{
  "id": "evt-001",
  "type": "instance.created",
  "created_at": "2025-01-01T00:00:00Z",
  "data": {
    "instance_id": "inst-001",
    "name": "production-1",
    "status": "running"
  }
}
```

## SDKs

- Node.js: [@teai/node-sdk](https://github.com/teai-io/node-sdk)
- Python: [teai-python](https://github.com/teai-io/python-sdk)
- Go: [go-teai](https://github.com/teai-io/go-sdk)
- Ruby: [teai-ruby](https://github.com/teai-io/ruby-sdk)