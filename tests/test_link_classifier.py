from src.pipeline.link_classifier import classify_link


def test_malware_from_web_risk():
    resolved = {"original_url": "http://evil.com", "resolved_url": "http://evil.com", "is_shortened": False, "resolve_status": "OK"}
    wr = {"is_safe": False, "threat_types": ["MALWARE"], "source": "web_risk_api"}
    result = classify_link(resolved, wr)
    assert result["category"] == "MALWARE"
    assert any("MALWARE" in f for f in result["risk_factors"])


def test_phishing_from_web_risk():
    resolved = {"original_url": "http://phish.xyz", "resolved_url": "http://phish.xyz", "is_shortened": False, "resolve_status": "OK"}
    wr = {"is_safe": False, "threat_types": ["SOCIAL_ENGINEERING"], "source": "web_risk_api"}
    result = classify_link(resolved, wr)
    assert result["category"] == "PHISHING_SUSPECT"


def test_apk_download():
    resolved = {"original_url": "http://x.com/app.apk", "resolved_url": "http://x.com/app.apk", "is_shortened": False, "resolve_status": "OK"}
    wr = {"is_safe": True, "threat_types": [], "source": "web_risk_api"}
    result = classify_link(resolved, wr)
    assert result["category"] == "APP_DOWNLOAD"


def test_shortened_url_risk():
    resolved = {"original_url": "http://bit.ly/abc", "resolved_url": "http://example.com", "is_shortened": True, "resolve_status": "OK"}
    wr = {"is_safe": True, "threat_types": [], "source": "web_risk_api"}
    result = classify_link(resolved, wr)
    assert any("단축 URL" in f for f in result["risk_factors"])


def test_http_protocol_risk():
    resolved = {"original_url": "http://example.com", "resolved_url": "http://example.com", "is_shortened": False, "resolve_status": "OK"}
    wr = {"is_safe": True, "threat_types": [], "source": "web_risk_api"}
    result = classify_link(resolved, wr)
    assert any("HTTP" in f for f in result["risk_factors"])


def test_suspicious_tld():
    resolved = {"original_url": "http://evil.xyz", "resolved_url": "http://evil.xyz", "is_shortened": False, "resolve_status": "OK"}
    wr = {"is_safe": True, "threat_types": [], "source": "web_risk_api"}
    result = classify_link(resolved, wr)
    assert result["category"] == "PHISHING_SUSPECT"


def test_normal_safe_url():
    resolved = {"original_url": "https://www.naver.com", "resolved_url": "https://www.naver.com", "is_shortened": False, "resolve_status": "OK"}
    wr = {"is_safe": True, "threat_types": [], "source": "whitelist"}
    result = classify_link(resolved, wr)
    assert result["category"] == "NORMAL"
