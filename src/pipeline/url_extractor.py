import re

from src.core.config import get_settings

URL_PATTERN = re.compile(
    r'(?:https?://|www\.)'
    r'[a-zA-Z0-9\-._~:/?#\[\]@!$&\'()*+,;=%]+'
    r'|'
    r'[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?'
    r'\.[a-zA-Z]{2,}'
    r'(?:/[a-zA-Z0-9\-._~:/?#\[\]@!$&\'()*+,;=%]*)?',
    re.IGNORECASE,
)

KNOWN_SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "v.gd",
    "ow.ly", "buff.ly", "bl.ink", "adf.ly", "rb.gy", "shorturl.at",
    "han.gl", "me2.do", "vo.la", "zrr.kr", "url.kr", "j.mp",
    "myip.kr", "lrl.kr", "buly.kr", "c11.kr", "reduced.to", "durl.me",
}


def extract_urls(message: str) -> list[dict]:
    """메시지에서 URL을 추출하고 단축 URL 여부를 판별한다."""
    settings = get_settings()
    raw_urls = URL_PATTERN.findall(message)

    seen = set()
    results = []
    for raw in raw_urls:
        url = raw.strip().rstrip(".,;:!?)")
        if not url.startswith(("http://", "https://")):
            if url.startswith("www."):
                url = "http://" + url
            else:
                url = "http://" + url

        if url in seen:
            continue
        seen.add(url)

        domain = _extract_domain(url)
        is_shortened = domain.lower() in KNOWN_SHORTENERS

        results.append({
            "original_url": url,
            "domain": domain,
            "is_shortened": is_shortened,
        })

        if len(results) >= settings.max_urls_per_message:
            break

    return results


def _extract_domain(url: str) -> str:
    """URL에서 도메인을 추출한다."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.hostname or ""
    except Exception:
        return ""
