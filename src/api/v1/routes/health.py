import time
from datetime import datetime, timezone

from fastapi import APIRouter

from src.api.v1.schemas.analysis import HealthResponse
from src.core.config import get_settings

router = APIRouter()

_start_time = time.monotonic()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """서버 및 외부 의존성 상태 확인"""
    settings = get_settings()
    deps = {}

    # PostgreSQL 체크
    try:
        from src.core.database import engine
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        deps["database"] = "connected"
    except Exception:
        deps["database"] = "disconnected"

    # Redis 체크
    try:
        from src.core.cache import get_redis
        r = await get_redis()
        await r.ping()
        deps["redis"] = "connected"
    except Exception:
        deps["redis"] = "disconnected"

    # OpenAI API 체크 (키 존재 여부만)
    deps["openai_api"] = "configured" if settings.openai_api_key else "not_configured"

    # Web Risk API 체크 (키 존재 여부만)
    deps["web_risk_api"] = "configured" if settings.google_web_risk_api_key else "not_configured"

    # 캐시 통계
    cache_stats = None
    try:
        from src.core.cache import get_redis
        r = await get_redis()
        info = await r.info("keyspace")
        db_info = info.get("db0", {})
        cache_stats = {
            "url_cache_size": db_info.get("keys", 0),
        }
    except Exception:
        pass

    all_healthy = deps.get("database") == "connected" and deps.get("redis") == "connected"

    return HealthResponse(
        status="healthy" if all_healthy else "degraded",
        version="1.0.0",
        dependencies=deps,
        cache_stats=cache_stats,
        uptime_seconds=round(time.monotonic() - _start_time, 1),
        timestamp=datetime.now(timezone.utc),
    )
