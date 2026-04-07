import json

from openai import AsyncOpenAI

from src.core.config import get_settings

SYSTEM_PROMPT = """당신은 스미싱(SMS 피싱) 탐지 전문 AI입니다.
사용자가 제공한 문자메시지와 사전 분석 결과를 종합하여 스미싱 여부를 최종 판단합니다.

[사전 분석 결과로 제공되는 정보]
- URL 추출 및 단축 URL 추적 결과 (원본 URL → 최종 목적지)
- Google Web Risk API 안전성 검사 결과
- 본문 키워드 패턴 분석 결과

[판단 기준]
1. Google Web Risk API 위협 탐지 여부 (MALWARE, SOCIAL_ENGINEERING, UNWANTED_SOFTWARE)
2. URL의 안전성 (단축 URL, 비공식 도메인, HTTP, 의심 TLD)
3. 메시지 내 긴급성/공포 유도 표현
4. 개인정보/금융정보 요구 여부
5. 알려진 스미싱 패턴 (택배, 정부기관, 금융기관, 가족 사칭 등)
6. 앱 설치(.apk) 유도 여부
7. 발신자 정보의 신뢰성

[위험도 기준]
- HIGH (고위험): Web Risk 위협 탐지, 개인정보 탈취, 악성앱 설치 유도, 금융 사기
- WARNING (위험): 의심 요소가 있으나 확정적이지 않음, Web Risk 안전하나 패턴 의심
- NORMAL (보통): 일반 광고, 정상 알림, Web Risk 안전, 의심 패턴 없음

반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트를 포함하지 마세요:
{
  "risk_level": "HIGH 또는 WARNING 또는 NORMAL",
  "risk_score": 0부터 100 사이의 정수,
  "summary": "1줄 요약 (한국어)",
  "explanation": "상세 판단 근거 (한국어, 번호 목록 형식)"
}"""


def _build_user_prompt(message: str, url_results: list[dict], text_analysis: dict, sender: str | None = None) -> str:
    parts = [f"[문자메시지 원문]\n{message}"]

    if sender:
        parts.append(f"\n[발신자]\n{sender}")

    if url_results:
        url_section = "\n[URL 분석 결과]"
        for i, u in enumerate(url_results, 1):
            url_section += f"\n  URL {i}:"
            url_section += f"\n    원본: {u.get('original_url', '')}"
            if u.get("resolved_url") and u["resolved_url"] != u.get("original_url"):
                url_section += f"\n    최종 목적지: {u['resolved_url']}"
            if u.get("redirect_chain"):
                url_section += f"\n    리다이렉트 체인: {' → '.join(u['redirect_chain'])}"
            url_section += f"\n    단축URL 여부: {u.get('is_shortened', False)}"
            url_section += f"\n    추적 상태: {u.get('resolve_status', 'OK')}"
            if u.get("category"):
                url_section += f"\n    분류: {u['category']}"
            wr = u.get("web_risk_result", {})
            if wr:
                url_section += f"\n    Web Risk 안전: {wr.get('is_safe', 'N/A')}"
                if wr.get("threat_types"):
                    url_section += f"\n    위협 유형: {', '.join(wr['threat_types'])}"
            if u.get("risk_factors"):
                url_section += f"\n    위험 요인: {', '.join(u['risk_factors'])}"
        parts.append(url_section)
    else:
        parts.append("\n[URL 분석 결과]\n  URL 없음")

    ta = text_analysis
    ta_section = "\n[본문 키워드 분석 결과]"
    ta_section += f"\n  탐지 키워드: {', '.join(ta.get('detected_keywords', [])) or '없음'}"
    ta_section += f"\n  패턴 카테고리: {', '.join(ta.get('pattern_categories', [])) or '없음'}"
    ta_section += f"\n  긴급성 점수: {ta.get('urgency_score', 0)}/100"
    parts.append(ta_section)

    return "\n".join(parts)


async def analyze_with_llm(
    message: str,
    url_results: list[dict],
    text_analysis: dict,
    sender: str | None = None,
) -> tuple[dict | None, int]:
    """LLM으로 스미싱 분석을 수행한다. (결과, 소요시간ms) 반환. 실패시 None."""
    settings = get_settings()

    if not settings.openai_api_key:
        return None, 0

    client = AsyncOpenAI(api_key=settings.openai_api_key, timeout=settings.llm_timeout)
    user_prompt = _build_user_prompt(message, url_results, text_analysis, sender)

    import time
    start = time.monotonic()

    for attempt in range(settings.llm_max_retries):
        try:
            response = await client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_completion_tokens=1000,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            result = json.loads(content)

            # 응답 검증
            if result.get("risk_level") not in ("HIGH", "WARNING", "NORMAL"):
                continue

            score = result.get("risk_score", 50)
            result["risk_score"] = max(0, min(100, int(score)))

            if not result.get("summary") or not result.get("explanation"):
                continue

            # explanation이 리스트로 올 경우 문자열로 변환
            if isinstance(result["explanation"], list):
                result["explanation"] = "\n".join(str(item) for item in result["explanation"])

            elapsed = int((time.monotonic() - start) * 1000)
            return result, elapsed

        except json.JSONDecodeError:
            continue
        except Exception:
            if attempt == settings.llm_max_retries - 1:
                break
            continue

    elapsed = int((time.monotonic() - start) * 1000)
    return None, elapsed


def fallback_rule_based(url_results: list[dict], text_analysis: dict) -> dict:
    """LLM 장애 시 규칙 기반 Fallback 판정."""
    risk_level = "NORMAL"
    risk_score = 20
    reasons = []

    # Web Risk 위협 탐지
    for u in url_results:
        wr = u.get("web_risk_result", {})
        if not wr.get("is_safe", True):
            risk_level = "HIGH"
            risk_score = max(risk_score, 90)
            reasons.append("Google Web Risk에서 위협이 탐지되었습니다.")

    # 앱 다운로드
    for u in url_results:
        if u.get("category") == "APP_DOWNLOAD":
            risk_level = "HIGH"
            risk_score = max(risk_score, 85)
            reasons.append("앱 다운로드(APK 등) 파일 직접 링크가 포함되어 있습니다.")

    # MALWARE
    for u in url_results:
        if u.get("category") == "MALWARE":
            risk_level = "HIGH"
            risk_score = max(risk_score, 95)
            reasons.append("악성코드(MALWARE) URL이 탐지되었습니다.")

    ta = text_analysis
    keywords = ta.get("detected_keywords", [])
    categories = ta.get("pattern_categories", [])
    urgency = ta.get("urgency_score", 0)

    # 스미싱 키워드 3개 이상 + 긴급성
    if len(keywords) >= 3 and urgency >= 50:
        risk_level = "HIGH"
        risk_score = max(risk_score, 80)
        reasons.append(f"스미싱 키워드 {len(keywords)}개 탐지 + 긴급성 표현이 포함되어 있습니다.")
    elif len(keywords) >= 1 or any(u.get("is_shortened") for u in url_results):
        if risk_level == "NORMAL":
            risk_level = "WARNING"
            risk_score = max(risk_score, 50)
            reasons.append("의심스러운 키워드 또는 단축 URL이 포함되어 있습니다.")

    if categories:
        reasons.append(f"탐지된 패턴: {', '.join(categories)}")

    # 모든 URL이 화이트리스트 + 키워드 없음
    all_safe = all(
        u.get("web_risk_result", {}).get("source") == "whitelist"
        for u in url_results
    ) if url_results else True

    if all_safe and not keywords and risk_level == "NORMAL":
        risk_score = 10
        reasons.append("안전 도메인이며 의심 패턴이 없습니다.")

    if not reasons:
        if risk_level == "NORMAL":
            reasons.append("특별한 위험 요소가 발견되지 않았습니다.")
        else:
            reasons.append("의심 요소가 있으나 확정적이지 않습니다. 주의가 필요합니다.")

    summary_map = {
        "HIGH": "고위험 스미싱 의심 문자입니다.",
        "WARNING": "주의가 필요한 의심 문자입니다.",
        "NORMAL": "특별한 위험이 발견되지 않은 문자입니다.",
    }

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "summary": summary_map.get(risk_level, "분석 결과입니다."),
        "explanation": "\n".join(f"{i+1}. {r}" for i, r in enumerate(reasons)),
    }
