import time
import uuid
from datetime import datetime, timezone

from src.pipeline.url_extractor import extract_urls
from src.pipeline.url_resolver import resolve_urls_parallel
from src.pipeline.web_risk_checker import check_url_safety
from src.pipeline.link_classifier import classify_link
from src.pipeline.text_analyzer import analyze_text
from src.pipeline.llm_analyzer import analyze_with_llm, fallback_rule_based
from src.pipeline.result_aggregator import aggregate_results
from src.core.config import get_settings


async def run_analysis(
    message: str,
    sender: str | None = None,
    safe_domains: set[str] | None = None,
    blacklist_domains: set[str] | None = None,
) -> dict:
    """7-step 스미싱 분석 파이프라인을 실행한다."""
    settings = get_settings()
    start = time.monotonic()
    analysis_id = str(uuid.uuid4())
    degraded = False
    degraded_services = []
    url_resolve_ms = 0
    web_risk_ms = 0
    llm_ms = 0
    cache_hit = False

    # Step 1: URL 추출
    extracted_urls = extract_urls(message)

    # Step 2: URL 추적 (병렬)
    resolved_urls, url_resolve_ms = await resolve_urls_parallel(extracted_urls)

    # Step 3 + 4: URL 안전성 검사 + 링크 분류
    url_results = []
    total_web_risk_ms = 0
    for resolved in resolved_urls:
        check_url = resolved.get("resolved_url") or resolved.get("original_url", "")
        wr_result, wr_ms = await check_url_safety(check_url, safe_domains, blacklist_domains)
        total_web_risk_ms += wr_ms

        if wr_result.get("source") == "cache":
            cache_hit = True

        classification = classify_link(resolved, wr_result)

        url_results.append({
            "original_url": resolved["original_url"],
            "resolved_url": resolved.get("resolved_url"),
            "redirect_chain": resolved.get("redirect_chain", []),
            "is_shortened": resolved.get("is_shortened", False),
            "resolve_status": resolved.get("resolve_status", "OK"),
            "category": classification["category"],
            "web_risk_result": wr_result,
            "risk_factors": classification["risk_factors"],
        })

    web_risk_ms = total_web_risk_ms

    # Step 5: 본문 키워드 분석
    text_analysis = analyze_text(message)

    # Step 6: LLM 분석
    llm_result, llm_ms = await analyze_with_llm(message, url_results, text_analysis, sender)

    if llm_result is None:
        # Graceful Degradation: 규칙 기반 fallback
        llm_result = fallback_rule_based(url_results, text_analysis)
        degraded = True
        degraded_services.append("openai_llm")

    # Step 7: 결과 집계
    result = aggregate_results(
        url_results=url_results,
        text_analysis=text_analysis,
        llm_result=llm_result,
        degraded=degraded,
        degraded_services=degraded_services,
    )

    total_ms = int((time.monotonic() - start) * 1000)

    return {
        "id": analysis_id,
        "data": result,
        "meta": {
            "model": settings.openai_model if not degraded else f"{settings.openai_model} (fallback)",
            "processing_time_ms": total_ms,
            "url_resolve_time_ms": url_resolve_ms,
            "web_risk_time_ms": web_risk_ms,
            "llm_time_ms": llm_ms,
            "cache_hit": cache_hit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        "original_message": message,
        "sender": sender,
    }
