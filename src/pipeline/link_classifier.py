APP_DOWNLOAD_EXTENSIONS = {".apk", ".exe", ".ipa", ".msi", ".dmg", ".deb", ".rpm"}

AD_DOMAIN_KEYWORDS = {
    "shop", "store", "mall", "market", "deal", "sale", "coupon",
    "event", "promo", "ad", "ads", "click", "offer",
}

SUSPICIOUS_TLDS = {
    ".xyz", ".top", ".club", ".work", ".buzz", ".tk", ".ml",
    ".ga", ".cf", ".gq", ".icu", ".loan", ".click",
}


def classify_link(resolved_info: dict, web_risk_result: dict) -> dict:
    """URL을 분류하고 위험 요인을 식별한다."""
    url = resolved_info.get("resolved_url") or resolved_info.get("original_url", "")
    original_url = resolved_info.get("original_url", "")
    risk_factors = []
    category = "NORMAL"

    # Web Risk 위협 탐지
    if not web_risk_result.get("is_safe", True):
        threat_types = web_risk_result.get("threat_types", [])
        if "MALWARE" in threat_types:
            category = "MALWARE"
            risk_factors.append("Google Web Risk: MALWARE 탐지")
        elif "SOCIAL_ENGINEERING" in threat_types:
            category = "PHISHING_SUSPECT"
            risk_factors.append("Google Web Risk: SOCIAL_ENGINEERING 탐지")
        elif "UNWANTED_SOFTWARE" in threat_types:
            category = "PHISHING_SUSPECT"
            risk_factors.append("Google Web Risk: UNWANTED_SOFTWARE 탐지")
        else:
            category = "PHISHING_SUSPECT"
            risk_factors.append(f"Google Web Risk: 위협 탐지 ({', '.join(threat_types)})")

    # 앱 다운로드 패턴
    url_lower = url.lower()
    for ext in APP_DOWNLOAD_EXTENSIONS:
        if url_lower.endswith(ext) or ext + "?" in url_lower:
            category = "APP_DOWNLOAD"
            risk_factors.append(f"앱 다운로드 파일 ({ext}) 직접 링크")
            break

    # 단축 URL 사용
    if resolved_info.get("is_shortened"):
        risk_factors.append("단축 URL 사용으로 목적지 은폐")

    # 해석 실패
    resolve_status = resolved_info.get("resolve_status", "OK")
    if resolve_status != "OK":
        risk_factors.append(f"URL 추적 실패 ({resolve_status})")

    # HTTP (비암호화)
    if url.startswith("http://"):
        risk_factors.append("HTTP(비암호화) 프로토콜 사용")

    # 의심스러운 TLD
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        for tld in SUSPICIOUS_TLDS:
            if hostname.endswith(tld):
                risk_factors.append(f"의심스러운 도메인 ({tld})")
                if category == "NORMAL":
                    category = "PHISHING_SUSPECT"
                break
    except Exception:
        pass

    # 광고 패턴 (Web Risk 안전 + 위협 아닌 경우만)
    if category == "NORMAL":
        domain = _extract_domain(url)
        for kw in AD_DOMAIN_KEYWORDS:
            if kw in domain:
                category = "AD"
                break

    return {
        "category": category,
        "risk_factors": risk_factors,
    }


def _extract_domain(url: str) -> str:
    try:
        from urllib.parse import urlparse
        return (urlparse(url).hostname or "").lower()
    except Exception:
        return ""
