import os
import json
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.user import User, FaxUsageRecord
from app.schemas.fax import (
    FaxSendRequest,
    FaxSendResponse,
    FaxStatusResponse,
    FaxProvider,
    FaxLimitCheck,
)
from app.core.config import settings


class FaxService:
    def __init__(self, db: Session):
        self.db = db
        self.daily_limit = 3  # 1日3通まで（teaiクレジット経由）

    def _get_user_telnyx_config(self, user: User) -> Optional[Dict[str, str]]:
        """ユーザーのTelnyx設定を取得（BYOK）"""
        if user.telnyx_api_key is not None and user.telnyx_connection_id is not None and user.telnyx_from is not None:
            return {
                "api_key": str(user.telnyx_api_key),
                "connection_id": str(user.telnyx_connection_id),
                "from_number": str(user.telnyx_from),
            }
        return None

    def _get_user_phaxio_config(self, user: User) -> Optional[Dict[str, str]]:
        """ユーザーのPhaxio設定を取得（BYOK）"""
        if user.phaxio_api_key is not None and user.phaxio_api_secret is not None:
            return {
                "api_key": str(user.phaxio_api_key),
                "api_secret": str(user.phaxio_api_secret),
            }
        return None

    def _get_system_telnyx_config(self) -> Optional[Dict[str, str]]:
        """システム共通のTelnyx設定（teaiクレジット経由）"""
        if settings.TELNYX_API_KEY and settings.TELNYX_CONNECTION_ID and settings.TELNYX_FROM:
            return {
                "api_key": settings.TELNYX_API_KEY,
                "connection_id": settings.TELNYX_CONNECTION_ID,
                "from_number": settings.TELNYX_FROM,
            }
        return None

    def _get_system_phaxio_config(self) -> Optional[Dict[str, str]]:
        """システム共通のPhaxio設定（teaiクレジット経由）"""
        if settings.PHAXIO_API_KEY and settings.PHAXIO_API_SECRET:
            return {
                "api_key": settings.PHAXIO_API_KEY,
                "api_secret": settings.PHAXIO_API_SECRET,
            }
        return None

    async def check_fax_limit(self, user: User) -> FaxLimitCheck:
        """FAX送信可能かチェック（BYOKなら無制限、teai経由なら1日3通）"""
        has_telnyx = bool(self._get_user_telnyx_config(user))
        has_phaxio = bool(self._get_user_phaxio_config(user))
        has_custom_key = has_telnyx or has_phaxio

        if has_custom_key:
            return FaxLimitCheck(
                can_send=True,
                daily_sent=0,
                daily_limit=-1,
                has_custom_key=True,
                message="Custom API key configured - unlimited sending",
            )

        # teaiクレジット経由の場合、今日の送信数をチェック
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        daily_sent = self.db.query(FaxUsageRecord).filter(
            FaxUsageRecord.user_id == user.id,
            FaxUsageRecord.timestamp >= today_start,
        ).count()

        can_send = daily_sent < self.daily_limit

        return FaxLimitCheck(
            can_send=can_send,
            daily_sent=daily_sent,
            daily_limit=self.daily_limit,
            has_custom_key=False,
            message=f"Daily limit: {daily_sent}/{self.daily_limit} faxes sent via teai credits"
            if can_send
            else f"Daily limit reached ({self.daily_limit} faxes/day). Add your own Telnyx/Phaxio key for unlimited.",
        )

    async def send_fax_telnyx(
        self,
        config: Dict[str, str],
        to: str,
        media_url: str,
        quality: str = "high",
        store_media: bool = False,
        monochrome: bool = True,
    ) -> Dict[str, Any]:
        """Telnyx経由でFAX送信"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.telnyx.com/v2/faxes",
                headers={
                    "Authorization": f"Bearer {config['api_key']}",
                    "Content-Type": "application/json",
                },
                json={
                    "connection_id": config["connection_id"],
                    "to": to,
                    "from": config["from_number"],
                    "media_url": media_url,
                    "quality": quality,
                    "store_media": store_media,
                    "monochrome": monochrome,
                },
            )
            response.raise_for_status()
            return response.json()

    async def send_fax_phaxio(
        self,
        config: Dict[str, str],
        to: str,
        media_url: str,
    ) -> Dict[str, Any]:
        """Phaxio経由でFAX送信（multipart/form-data）"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Phaxioはmultipart/form-dataを期待する
            files = {"to": (None, to), "media_url": (None, media_url)}
            auth = (config["api_key"], config["api_secret"])
            response = await client.post(
                "https://api.phaxio.com/v2.1/faxes",
                auth=auth,
                files=files,
            )
            response.raise_for_status()
            return response.json()

    async def poll_fax_telnyx(self, config: Dict[str, str], fax_id: str) -> Dict[str, Any]:
        """Telnyx FAXステータス取得"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"https://api.telnyx.com/v2/faxes/{fax_id}",
                headers={"Authorization": f"Bearer {config['api_key']}"},
            )
            response.raise_for_status()
            return response.json()

    async def poll_fax_phaxio(self, config: Dict[str, str], fax_id: str) -> Dict[str, Any]:
        """Phaxio FAXステータス取得"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            auth = (config["api_key"], config["api_secret"])
            response = await client.get(
                f"https://api.phaxio.com/v2.1/faxes/{fax_id}",
                auth=auth,
            )
            response.raise_for_status()
            return response.json()

    async def send_fax(
        self,
        user: User,
        request: FaxSendRequest,
    ) -> FaxSendResponse:
        """FAX送信のメイン処理"""
        # 制限チェック
        limit_check = await self.check_fax_limit(user)
        if not limit_check.can_send:
            return FaxSendResponse(
                success=False,
                provider=request.provider,
                message=limit_check.message,
            )

        # プロバイダ別の設定取得
        if request.provider == FaxProvider.TELNYX:
            config = self._get_user_telnyx_config(user) or self._get_system_telnyx_config()
            if not config:
                return FaxSendResponse(
                    success=False,
                    provider=request.provider,
                    message="Telnyx configuration not available",
                )
            try:
                result = await self.send_fax_telnyx(
                    config=config,
                    to=request.to,
                    media_url=request.media_url,
                    quality=request.quality,
                    store_media=request.store_media,
                    monochrome=request.monochrome,
                )
                fax_id = result.get("data", {}).get("id")
                status = result.get("data", {}).get("status")
            except httpx.HTTPStatusError as e:
                return FaxSendResponse(
                    success=False,
                    provider=request.provider,
                    message=f"Telnyx API error: {e.response.status_code} - {e.response.text}",
                )
            except Exception as e:
                return FaxSendResponse(
                    success=False,
                    provider=request.provider,
                    message=f"Error sending fax: {str(e)}",
                )

        elif request.provider == FaxProvider.PHAXIO:
            config = self._get_user_phaxio_config(user) or self._get_system_phaxio_config()
            if not config:
                return FaxSendResponse(
                    success=False,
                    provider=request.provider,
                    message="Phaxio configuration not available",
                )
            try:
                result = await self.send_fax_phaxio(
                    config=config,
                    to=request.to,
                    media_url=request.media_url,
                )
                fax_id = result.get("data", {}).get("id")
                status = "queued"
            except httpx.HTTPStatusError as e:
                return FaxSendResponse(
                    success=False,
                    provider=request.provider,
                    message=f"Phaxio API error: {e.response.status_code} - {e.response.text}",
                )
            except Exception as e:
                return FaxSendResponse(
                    success=False,
                    provider=request.provider,
                    message=f"Error sending fax: {str(e)}",
                )

        else:
            return FaxSendResponse(
                success=False,
                provider=request.provider,
                message=f"Unknown provider: {request.provider}",
            )

        # 使用記録を保存（teaiクレジット経由の場合のみ課金）
        uses_credits = not limit_check.has_custom_key
        if uses_credits:
            usage_record = FaxUsageRecord(
                user_id=user.id,
                fax_id=str(fax_id),
                provider=request.provider.value,
                to_number=request.to,
                pages=1,  # 実際にはステータスポーリングで取得
                cost_credits=1,
                status=status or "queued",
                timestamp=datetime.utcnow(),
            )
            self.db.add(usage_record)
            self.db.commit()

        return FaxSendResponse(
            success=True,
            fax_id=str(fax_id) if fax_id else None,
            status=status,
            provider=request.provider,
            message="Fax queued for sending",
            cost_credits=1 if uses_credits else 0,
        )

    async def get_fax_status(
        self,
        user: User,
        fax_id: str,
        provider: FaxProvider,
    ) -> FaxStatusResponse:
        """FAX送信ステータス取得"""
        # ユーザーの設定で試す、なければシステム設定
        if provider == FaxProvider.TELNYX:
            config = self._get_user_telnyx_config(user) or self._get_system_telnyx_config()
            if not config:
                raise ValueError("Telnyx configuration not available")
            result = await self.poll_fax_telnyx(config, fax_id)
            data = result.get("data", {})
            return FaxStatusResponse(
                fax_id=fax_id,
                status=data.get("status", "unknown"),
                provider=provider,
                to=data.get("to", ""),
                from_number=data.get("from"),
                media_url=data.get("media_url"),
                pages=data.get("pages"),
                cost_credits=1,
                created_at=data.get("created_at"),
                completed_at=data.get("updated_at"),
                error_message=data.get("error_message"),
            )
        else:
            config = self._get_user_phaxio_config(user) or self._get_system_phaxio_config()
            if not config:
                raise ValueError("Phaxio configuration not available")
            result = await self.poll_fax_phaxio(config, fax_id)
            data = result.get("data", {})
            return FaxStatusResponse(
                fax_id=fax_id,
                status=data.get("status", "unknown"),
                provider=provider,
                to=data.get("to", ""),
                from_number=None,
                media_url=data.get("media_url"),
                pages=data.get("num_pages"),
                cost_credits=1,
                created_at=data.get("created_at"),
                completed_at=data.get("completed_at"),
                error_message=data.get("error_message"),
            )