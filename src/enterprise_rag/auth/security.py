import hmac
from fastapi import Header, HTTPException
from enterprise_rag.config import settings

async def require_auth(x_api_key: str | None = Header(default=None)):
    if not settings.require_api_key:
        return
    if not settings.api_key or settings.api_key == "change-this-for-any-shared-deployment":
        raise HTTPException(status_code=503, detail="API key authentication is required but not securely configured")
    if not x_api_key or not hmac.compare_digest(x_api_key, settings.api_key):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
