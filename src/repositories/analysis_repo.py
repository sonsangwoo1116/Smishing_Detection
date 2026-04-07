from datetime import datetime, timezone

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.analysis import AnalysisHistory


async def save_analysis(db: AsyncSession, result: dict) -> AnalysisHistory:
    """분석 결과를 DB에 저장한다."""
    data = result["data"]
    record = AnalysisHistory(
        id=result["id"],
        message=result["original_message"],
        sender=result.get("sender"),
        risk_level=data["risk_level"],
        risk_score=data["risk_score"],
        summary=data["summary"],
        explanation=data["explanation"],
        urls=data.get("urls", []),
        text_analysis=data.get("text_analysis"),
        patterns=data.get("patterns_detected", []),
        degraded=data.get("degraded", False),
        degraded_services=data.get("degraded_services", []),
        model_used=result["meta"]["model"],
        processing_time_ms=result["meta"]["processing_time_ms"],
        metadata_extra=result.get("metadata"),
    )
    db.add(record)
    await db.flush()
    return record


async def get_analysis_by_id(db: AsyncSession, analysis_id: str) -> AnalysisHistory | None:
    result = await db.execute(select(AnalysisHistory).where(AnalysisHistory.id == analysis_id))
    return result.scalar_one_or_none()


async def get_analysis_history(
    db: AsyncSession,
    page: int = 1,
    size: int = 20,
    risk_level: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> tuple[list[AnalysisHistory], int]:
    """분석 이력을 페이지네이션으로 조회한다."""
    query = select(AnalysisHistory)
    count_query = select(func.count(AnalysisHistory.id))

    if risk_level:
        query = query.where(AnalysisHistory.risk_level == risk_level.upper())
        count_query = count_query.where(AnalysisHistory.risk_level == risk_level.upper())

    if start_date:
        query = query.where(AnalysisHistory.created_at >= start_date)
        count_query = count_query.where(AnalysisHistory.created_at >= start_date)

    if end_date:
        query = query.where(AnalysisHistory.created_at <= end_date)
        count_query = count_query.where(AnalysisHistory.created_at <= end_date)

    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(desc(AnalysisHistory.created_at))
    query = query.offset((page - 1) * size).limit(size)

    result = await db.execute(query)
    items = list(result.scalars().all())

    return items, total
