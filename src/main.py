import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.core.config import get_settings
from src.core.cache import close_redis
from src.core.database import engine, Base, AsyncSessionLocal
from src.models.analysis import (  # noqa: F401
    AnalysisHistory, UrlCache, KnownPattern, SafeDomain, ApiKey
)
from src.api.v1.routes import analyze, health, history, fake_urls
from src.services.seed_data import seed_safe_domains, seed_known_patterns
from src.services.auth_service import seed_initial_api_key

logger = logging.getLogger(__name__)
settings = get_settings()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: DB 테이블 생성 + 시딩
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        await seed_safe_domains(session)
        await seed_known_patterns(session)
        if settings.initial_api_key:
            await seed_initial_api_key(session, settings.initial_api_key)
        await session.commit()

    logger.info("Smishing Detection Agent started")

    yield

    await close_redis()
    await engine.dispose()
    logger.info("Smishing Detection Agent stopped")


app = FastAPI(
    title="Smishing Detection AI Agent",
    description="스미싱(SMS 피싱) 탐지 AI Agent API",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(analyze.router, prefix="/api/v1", tags=["Analysis"])
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(history.router, prefix="/api/v1", tags=["History"])
app.include_router(fake_urls.router, tags=["Test Fake URLs"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host=settings.host, port=settings.port, reload=True)
