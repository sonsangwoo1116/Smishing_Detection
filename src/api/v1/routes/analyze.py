from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.schemas.analysis import (
    AnalyzeRequest, AnalyzeResponse, AnalysisData, AnalysisMeta,
    UrlResult, TextAnalysisResult,
)
from src.api.v1.dependencies import require_api_key
from src.core.database import get_db
from src.core.config import get_settings
from src.pipeline.orchestrator import run_analysis
from src.repositories.analysis_repo import save_analysis
from src.services.seed_data import load_safe_domains, load_blacklist_domains

router = APIRouter()


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
)
async def analyze_message(
    request: AnalyzeRequest,
    api_key=Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
):
    """문자메시지 스미싱 분석 요청"""
    settings = get_settings()

    if len(request.message) > settings.max_message_length:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": {
                    "code": "MESSAGE_TOO_LONG",
                    "message": f"Message exceeds {settings.max_message_length} unicode codepoints",
                    "details": [],
                },
                "meta": {"timestamp": datetime.now(timezone.utc).isoformat()},
            },
        )

    try:
        safe_domains = await load_safe_domains(db)
        blacklist_domains = await load_blacklist_domains(db)

        result = await run_analysis(
            message=request.message,
            sender=request.sender,
            safe_domains=safe_domains,
            blacklist_domains=blacklist_domains,
        )

        # DB에 분석 결과 저장
        await save_analysis(db, result)

        data = result["data"]
        meta = result["meta"]

        url_results = [
            UrlResult(
                original_url=u["original_url"],
                resolved_url=u.get("resolved_url"),
                redirect_chain=u.get("redirect_chain", []),
                is_shortened=u.get("is_shortened", False),
                resolve_status=u.get("resolve_status", "OK"),
                category=u.get("category", "UNKNOWN"),
                web_risk_result=u.get("web_risk_result"),
                risk_factors=u.get("risk_factors", []),
            )
            for u in data.get("urls", [])
        ]

        ta = data.get("text_analysis", {})
        text_analysis = TextAnalysisResult(
            detected_keywords=ta.get("detected_keywords", []),
            pattern_categories=ta.get("pattern_categories", []),
            urgency_score=ta.get("urgency_score", 0),
        )

        return AnalyzeResponse(
            success=True,
            data=AnalysisData(
                id=result["id"],
                degraded=data.get("degraded", False),
                degraded_services=data.get("degraded_services", []),
                degraded_reason=data.get("degraded_reason"),
                risk_level=data["risk_level"],
                risk_score=data["risk_score"],
                summary=data["summary"],
                explanation=data["explanation"],
                urls=url_results,
                text_analysis=text_analysis,
                patterns_detected=data.get("patterns_detected", []),
                analyzed_at=datetime.fromisoformat(data["analyzed_at"]),
            ),
            meta=AnalysisMeta(
                model=meta["model"],
                processing_time_ms=meta["processing_time_ms"],
                url_resolve_time_ms=meta.get("url_resolve_time_ms", 0),
                web_risk_time_ms=meta.get("web_risk_time_ms", 0),
                llm_time_ms=meta.get("llm_time_ms", 0),
                cache_hit=meta.get("cache_hit", False),
                timestamp=datetime.fromisoformat(meta["timestamp"]),
            ),
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {"code": "INTERNAL_ERROR", "message": str(e), "details": []},
                "meta": {"timestamp": datetime.now(timezone.utc).isoformat()},
            },
        )
