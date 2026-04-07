from src.pipeline.llm_analyzer import fallback_rule_based


def test_fallback_web_risk_threat():
    urls = [{"web_risk_result": {"is_safe": False, "threat_types": ["SOCIAL_ENGINEERING"]}, "category": "PHISHING_SUSPECT", "is_shortened": False}]
    ta = {"detected_keywords": [], "pattern_categories": [], "urgency_score": 0}
    result = fallback_rule_based(urls, ta)
    assert result["risk_level"] == "HIGH"
    assert result["risk_score"] >= 90


def test_fallback_app_download():
    urls = [{"web_risk_result": {"is_safe": True}, "category": "APP_DOWNLOAD", "is_shortened": False}]
    ta = {"detected_keywords": [], "pattern_categories": [], "urgency_score": 0}
    result = fallback_rule_based(urls, ta)
    assert result["risk_level"] == "HIGH"


def test_fallback_many_keywords_urgent():
    urls = []
    ta = {"detected_keywords": ["택배", "배송", "주소지 미확인", "긴급"], "pattern_categories": ["택배사칭"], "urgency_score": 65}
    result = fallback_rule_based(urls, ta)
    assert result["risk_level"] == "HIGH"


def test_fallback_some_keywords():
    urls = []
    ta = {"detected_keywords": ["택배"], "pattern_categories": ["택배사칭"], "urgency_score": 15}
    result = fallback_rule_based(urls, ta)
    assert result["risk_level"] == "WARNING"


def test_fallback_shortened_url():
    urls = [{"web_risk_result": {"is_safe": True}, "category": "NORMAL", "is_shortened": True}]
    ta = {"detected_keywords": [], "pattern_categories": [], "urgency_score": 0}
    result = fallback_rule_based(urls, ta)
    assert result["risk_level"] == "WARNING"


def test_fallback_normal():
    urls = [{"web_risk_result": {"is_safe": True, "source": "whitelist"}, "category": "NORMAL", "is_shortened": False}]
    ta = {"detected_keywords": [], "pattern_categories": [], "urgency_score": 0}
    result = fallback_rule_based(urls, ta)
    assert result["risk_level"] == "NORMAL"
    assert result["risk_score"] <= 20


def test_fallback_has_required_fields():
    result = fallback_rule_based([], {"detected_keywords": [], "pattern_categories": [], "urgency_score": 0})
    assert "risk_level" in result
    assert "risk_score" in result
    assert "summary" in result
    assert "explanation" in result
