import hashlib
import time
from datetime import datetime, timezone

from src.core.config import get_settings
from src.core.cache import cache_get, cache_set

SAFE_RESULT = {"is_safe": True, "threat_types": [], "source": ""}
THREAT_TYPES = ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"]


async def check_url_safety(url: str, safe_domains: set[str] | None = None, blacklist_domains: set[str] | None = None) -> tuple[dict, int]:
    """URL 안전성을 검사한다. 캐시 → 화이트리스트 → 블랙리스트 → Web Risk API 순서."""
    settings = get_settings()
    start = time.monotonic()

    url_hash = hashlib.sha256(url.encode()).hexdigest()
    cache_key = f"web_risk:{url_hash}"

    # 1. 캐시 조회
    cached = await cache_get(cache_key)
    if cached:
        cached["source"] = "cache"
        elapsed = int((time.monotonic() - start) * 1000)
        return cached, elapsed

    # 2. 화이트리스트 체크
    domain = _extract_domain(url)
    if safe_domains and domain in safe_domains:
        result = {"is_safe": True, "threat_types": [], "source": "whitelist"}
        await _cache_result(cache_key, result, is_threat=False)
        elapsed = int((time.monotonic() - start) * 1000)
        return result, elapsed

    # 3. 블랙리스트 체크
    if blacklist_domains and domain in blacklist_domains:
        result = {"is_safe": False, "threat_types": ["BLACKLISTED"], "source": "blacklist"}
        await _cache_result(cache_key, result, is_threat=True)
        elapsed = int((time.monotonic() - start) * 1000)
        return result, elapsed

    # 4. Google Web Risk API 호출
    result = await _call_web_risk_api(url)
    if result:
        is_threat = not result["is_safe"]
        await _cache_result(cache_key, result, is_threat=is_threat)
    else:
        result = {"is_safe": True, "threat_types": [], "source": "web_risk_api_error"}

    elapsed = int((time.monotonic() - start) * 1000)
    return result, elapsed


async def _call_web_risk_api(url: str) -> dict | None:
    """Google Web Risk API를 호출한다."""
    settings = get_settings()
    api_key = settings.google_web_risk_api_key

    if not api_key:
        return {"is_safe": True, "threat_types": [], "source": "web_risk_api_no_key"}

    try:
        import httpx
        async with httpx.AsyncClient(timeout=settings.web_risk_timeout) as client:
            response = await client.get(
                "https://webrisk.googleapis.com/v1/uris:search",
                params={
                    "uri": url,
                    "threatTypes": THREAT_TYPES,
                    "key": api_key,
                },
            )

            if response.status_code == 200:
                data = response.json()
                threat = data.get("threat", {})
                threat_types = [t.get("threatTypes", []) for t in threat.get("threatEntries", [])] if threat else []
                flat_threats = [t for sublist in threat_types for t in sublist] if threat_types else []

                if threat and threat.get("threatTypes"):
                    flat_threats = threat["threatTypes"]
                elif not flat_threats and data.get("threat"):
                    flat_threats = ["UNKNOWN_THREAT"]

                is_safe = len(flat_threats) == 0 and not data.get("threat")
                return {"is_safe": is_safe, "threat_types": flat_threats, "source": "web_risk_api"}
            else:
                return None
    except Exception:
        return None


async def _cache_result(cache_key: str, result: dict, is_threat: bool):
    """결과를 캐시에 저장한다. 위협=1시간, 안전=24시간."""
    settings = get_settings()
    ttl = settings.url_cache_threat_ttl_hours * 3600 if is_threat else settings.url_cache_ttl_hours * 3600
    await cache_set(cache_key, result, ttl)


def _extract_domain(url: str) -> str:
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return (parsed.hostname or "").lower()
    except Exception:
        return ""
