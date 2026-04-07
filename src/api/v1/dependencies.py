from datetime import datetime, timezone

from fastapi import Header, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.services.auth_service import verify_api_key


async def require_api_key(
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
):
    """API Key 인증 미들웨어"""
    record = await verify_api_key(db, x_api_key)
    if record is None:
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error": {"code": "UNAUTHORIZED", "message": "Invalid API key", "details": []},
                "meta": {"timestamp": datetime.now(timezone.utc).isoformat()},
            },
        )
    return record
