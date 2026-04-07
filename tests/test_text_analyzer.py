from src.pipeline.text_analyzer import analyze_text


def test_delivery_scam():
    result = analyze_text("[Web발신] 고객님 택배가 도착했습니다. 주소지 미확인으로 배송 불가")
    assert "택배" in result["detected_keywords"]
    assert "택배사칭" in result["pattern_categories"]


def test_finance_scam():
    result = analyze_text("해외결제 승인 완료 987,000원 본인확인 필요")
    assert "금융사칭" in result["pattern_categories"]
    assert result["urgency_score"] > 0


def test_family_scam():
    result = analyze_text("엄마 나 폰 바꿨어 이 번호로 연락줘")
    assert "가족사칭" in result["pattern_categories"]


def test_government_scam():
    result = analyze_text("정부지원금 신청하세요 지금 바로 클릭")
    assert "정부사칭" in result["pattern_categories"]
    assert "지금 바로" in result["detected_keywords"]


def test_urgency_detection():
    result = analyze_text("긴급! 즉시 확인하세요 과태료 부과됩니다")
    assert result["urgency_score"] >= 50


def test_normal_message():
    result = analyze_text("내일 점심 같이 먹을래?")
    assert len(result["detected_keywords"]) == 0
    assert len(result["pattern_categories"]) == 0
    assert result["urgency_score"] == 0


def test_multiple_categories():
    result = analyze_text("경찰입니다 택배에서 마약이 발견되었습니다 즉시 연락바랍니다")
    assert len(result["pattern_categories"]) >= 2
