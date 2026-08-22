# API Reference

This document provides an overview of the teai.io API, which is powered by the nanobot backend.

## Base URL

`https://api.teai.io/api/v1`

## Authentication

All API endpoints require authentication using a Bearer token (API Key). You can generate API keys via the `/api/v1/apikeys` endpoint.

## Endpoints

### API Key Management

#### `GET /apikeys`

Lists all API keys associated with your account.

**Request**:

```bash
curl -X GET \
  -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.teai.io/api/v1/apikeys
```

**Response**:

```json
[
  {
    "id": "key_xxxxxxxxxxxx",
    "name": "My first API key",
    "permissions": ["ai:read", "ai:write"],
    "created_at": "2026-08-22T00:00:00Z"
  }
]
```

#### `POST /apikeys`

Creates a new API key.

**Request**:

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "name": "New Key", "permissions": ["ai:read"] }' \
  https://api.teai.io/api/v1/apikeys
```

**Response**:

```json
{
  "id": "key_yyyyyyyyyyyy",
  "name": "New Key",
  "permissions": ["ai:read"],
  "created_at": "2026-08-22T00:00:00Z",
  "secret": "sk_zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"
}
```

#### `DELETE /apikeys/{id}`

Deletes an API key by its ID.

**Request**:

```bash
curl -X DELETE \
  -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.teai.io/api/v1/apikeys/key_xxxxxxxxxxxx
```

**Response**:

```json
{
  "message": "API key deleted successfully"
}
```

### Other Endpoints (Under Development)

- `/chat`: AI chat completions
- `/billing`: Billing information
- `/account`: User account management
- `/orgs`: Organization management

