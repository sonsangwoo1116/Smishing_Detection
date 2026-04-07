import asyncio
import time

import httpx

from src.core.config import get_settings

USER_AGENT = "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"


async def resolve_url(url_info: dict) -> dict:
    """모든 URL의 최종 목적지를 추적한다. HEAD 요청 → 실패 시 GET fallback."""
    settings = get_settings()
    result = {
        "original_url": url_info["original_url"],
        "resolved_url": url_info["original_url"],
        "redirect_chain": [],
        "is_shortened": url_info["is_shortened"],
        "resolve_status": "OK",
    }

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            max_redirects=settings.url_max_redirects,
            timeout=settings.url_resolve_timeout,
            headers={"User-Agent": USER_AGENT},
        ) as client:
            # HEAD 시도
            response = await client.head(url_info["original_url"])

            # HEAD가 리다이렉트 없이 끝났으면 GET으로 재시도 (일부 서비스는 HEAD에 리다이렉트 안함)
            if not response.history:
                response = await client.get(url_info["original_url"], follow_redirects=True)

            final_url = str(response.url)
            chain = [str(h.url) for h in response.history]
            if chain:
                chain.append(final_url)

            result["resolved_url"] = final_url
            result["redirect_chain"] = chain

            # 리다이렉트가 발생했으면 is_shortened 보정
            if chain and final_url != url_info["original_url"]:
                result["is_shortened"] = True

    except httpx.TooManyRedirects:
        result["resolve_status"] = "TOO_MANY_REDIRECTS"
    except httpx.TimeoutException:
        result["resolve_status"] = "TIMEOUT"
    except Exception:
        result["resolve_status"] = "FAILED"

    return result


async def resolve_urls_parallel(url_infos: list[dict]) -> tuple[list[dict], int]:
    """여러 URL을 asyncio.gather로 병렬 추적한다. 총 소요시간(ms)도 반환."""
    if not url_infos:
        return [], 0

    settings = get_settings()
    start = time.monotonic()

    try:
        results = await asyncio.wait_for(
            asyncio.gather(*[resolve_url(u) for u in url_infos], return_exceptions=True),
            timeout=settings.url_resolve_total_timeout,
        )
    except asyncio.TimeoutError:
        results = [
            {
                "original_url": u["original_url"],
                "resolved_url": u["original_url"],
                "redirect_chain": [],
                "is_shortened": u["is_shortened"],
                "resolve_status": "TIMEOUT",
            }
            for u in url_infos
        ]

    cleaned = []
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            cleaned.append({
                "original_url": url_infos[i]["original_url"],
                "resolved_url": url_infos[i]["original_url"],
                "redirect_chain": [],
                "is_shortened": url_infos[i]["is_shortened"],
                "resolve_status": "FAILED",
            })
        else:
            cleaned.append(r)

    elapsed_ms = int((time.monotonic() - start) * 1000)
    return cleaned, elapsed_ms
