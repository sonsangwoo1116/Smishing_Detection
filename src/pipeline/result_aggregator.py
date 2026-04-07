from datetime import datetime, timezone


def aggregate_results(
    url_results: list[dict],
    text_analysis: dict,
    llm_result: dict,
    degraded: bool = False,
    degraded_services: list[str] | None = None,
) -> dict:
    """모든 분석 결과를 구조화된 응답으로 조합한다."""
    patterns_detected = []

    # URL 기반 패턴
    for u in url_results:
        if u.get("is_shortened"):
            patterns_detected.append("단축 URL 사용")
        cat = u.get("category", "")
        if cat == "PHISHING_SUSPECT":
            patterns_detected.append("피싱 의심 URL")
        elif cat == "MALWARE":
            patterns_detected.append("악성코드 URL")
        elif cat == "APP_DOWNLOAD":
            patterns_detected.append("앱 다운로드 유도")
        wr = u.get("web_risk_result", {})
        if not wr.get("is_safe", True):
            patterns_detected.append("Google Web Risk 위협 탐지")

    # 텍스트 기반 패턴
    for cat in text_analysis.get("pattern_categories", []):
        patterns_detected.append(cat)
    if text_analysis.get("urgency_score", 0) >= 50:
        patterns_detected.append("긴급성/공포 유도")

    patterns_detected = list(dict.fromkeys(patterns_detected))

    degraded_reason = None
    if degraded and degraded_services:
        service_names = {"openai_llm": "LLM API", "web_risk": "Web Risk API"}
        names = [service_names.get(s, s) for s in degraded_services]
        degraded_reason = f"{', '.join(names)} unavailable, rule-based fallback applied"

    return {
        "risk_level": llm_result["risk_level"],
        "risk_score": llm_result["risk_score"],
        "summary": llm_result["summary"],
        "explanation": llm_result["explanation"],
        "urls": url_results,
        "text_analysis": text_analysis,
        "patterns_detected": patterns_detected,
        "degraded": degraded,
        "degraded_services": degraded_services or [],
        "degraded_reason": degraded_reason,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }
