import hashlib
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.analysis import ApiKey


def hash_api_key(key: str) -> str:
    """API Key를 SHA-256으로 해싱한다."""
    return hashlib.sha256(key.encode()).hexdigest()


async def verify_api_key(db: AsyncSession, api_key: str) -> ApiKey | None:
    """API Key를 검증하고 사용량을 업데이트한다."""
    key_hash = hash_api_key(api_key)
    result = await db.execute(
        select(ApiKey).where(ApiKey.key_hash == key_hash, ApiKey.is_active == True)
    )
    record = result.scalar_one_or_none()

    if record is None:
        return None

    # 만료 체크
    if record.expires_at and record.expires_at < datetime.now(timezone.utc):
        return None

    # 사용량 업데이트
    record.total_usage += 1
    record.last_used_at = datetime.now(timezone.utc)
    await db.flush()

    return record


async def create_api_key(db: AsyncSession, name: str, raw_key: str, rate_limit: int = 60) -> ApiKey:
    """새 API Key를 생성한다."""
    record = ApiKey(
        key_hash=hash_api_key(raw_key),
        name=name,
        rate_limit_per_minute=rate_limit,
    )
    db.add(record)
    await db.flush()
    return record


async def seed_initial_api_key(db: AsyncSession, raw_key: str):
    """초기 부트스트랩 API Key를 시딩한다. 이미 존재하면 무시."""
    key_hash = hash_api_key(raw_key)
    result = await db.execute(select(ApiKey).where(ApiKey.key_hash == key_hash))
    if result.scalar_one_or_none() is None:
        await create_api_key(db, "bootstrap-key", raw_key)
