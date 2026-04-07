import math
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.repositories.analysis_repo import get_analysis_history, get_analysis_by_id

router = APIRouter()


@router.get("/history")
async def list_history(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    risk_level: str | None = Query(None),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """분석 이력 조회 (페이지네이션)"""
    sd = datetime.fromisoformat(start_date) if start_date else None
    ed = datetime.fromisoformat(end_date) if end_date else None

    items, total = await get_analysis_history(db, page, size, risk_level, sd, ed)

    return {
        "success": True,
        "data": {
            "items": [
                {
                    "id": item.id,
                    "message_preview": item.message[:50] + "..." if len(item.message) > 50 else item.message,
                    "risk_level": item.risk_level,
                    "risk_score": item.risk_score,
                    "summary": item.summary,
                    "urls_count": len(item.urls) if item.urls else 0,
                    "analyzed_at": item.created_at.isoformat(),
                }
                for item in items
            ],
            "pagination": {
                "page": page,
                "size": size,
                "total_items": total,
                "total_pages": math.ceil(total / size) if total > 0 else 0,
            },
        },
        "meta": {"timestamp": datetime.now(timezone.utc).isoformat()},
    }


@router.get("/history/{analysis_id}")
async def get_history_detail(analysis_id: str, db: AsyncSession = Depends(get_db)):
    """특정 분석 결과 상세 조회"""
    item = await get_analysis_by_id(db, analysis_id)
    if item is None:
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": {"code": "NOT_FOUND", "message": "Analysis result not found", "details": []},
                "meta": {"timestamp": datetime.now(timezone.utc).isoformat()},
            },
        )

    return {
        "success": True,
        "data": {
            "id": item.id,
            "degraded": item.degraded,
            "degraded_services": item.degraded_services or [],
            "risk_level": item.risk_level,
            "risk_score": item.risk_score,
            "summary": item.summary,
            "explanation": item.explanation,
            "urls": item.urls or [],
            "text_analysis": item.text_analysis,
            "patterns_detected": item.patterns or [],
            "analyzed_at": item.created_at.isoformat(),
        },
        "meta": {
            "model": item.model_used,
            "processing_time_ms": item.processing_time_ms,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
