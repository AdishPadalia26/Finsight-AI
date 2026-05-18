"""
Optional API Key Auth Middleware

For the demo, auth is disabled (API_KEY env var not set = open access).
For production cloud deployment: set API_KEY env var to enable key validation.

Usage in route:
    from api.middleware.auth import require_api_key
    @router.post("/analyze", dependencies=[Depends(require_api_key)])
"""

import os
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

_API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
_CONFIGURED_KEY = os.getenv("API_KEY", "")  # empty = auth disabled


async def require_api_key(api_key: str = Security(_API_KEY_HEADER)):
    """
    Dependency that validates the X-API-Key header.
    Skipped entirely if API_KEY env var is not set (demo mode).
    """
    if not _CONFIGURED_KEY:
        return  # auth disabled in demo mode

    if api_key != _CONFIGURED_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )
