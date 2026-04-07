SMISHING_PATTERNS = {
    "택배사칭": ["택배", "배송", "주소지 미확인", "배달 불가", "운송장", "반송", "수취인"],
    "금융사칭": ["결제 완료", "승인", "카드", "출금", "이체", "해외결제", "본인확인", "계좌"],
    "정부사칭": ["정부지원금", "재난지원", "건강검진", "국민연금", "세금", "환급금", "보조금"],
    "가족사칭": ["엄마", "아빠", "폰 바꿨", "번호 변경", "새 번호", "폰이 고장"],
    "기관사칭": ["경찰", "검찰", "법원", "국세청", "금감원", "수사관", "출석요구"],
    "부고사칭": ["부고", "장례", "조의금", "결혼", "청첩장"],
    "대출사칭": ["대출", "저금리", "승인 완료", "한도", "신용등급"],
}

URGENCY_KEYWORDS = [
    "지금 바로", "즉시", "긴급", "과태료", "체포", "소송",
    "24시간 이내", "오늘까지", "마감", "최종", "경고",
    "즉각", "시급", "위반", "벌금", "압류",
]


def analyze_text(message: str) -> dict:
    """메시지 본문의 키워드 패턴을 분석한다."""
    message_lower = message.lower()
    detected_keywords = []
    pattern_categories = []

    for category, keywords in SMISHING_PATTERNS.items():
        for keyword in keywords:
            if keyword in message or keyword.lower() in message_lower:
                if keyword not in detected_keywords:
                    detected_keywords.append(keyword)
                if category not in pattern_categories:
                    pattern_categories.append(category)

    urgency_count = 0
    for keyword in URGENCY_KEYWORDS:
        if keyword in message or keyword.lower() in message_lower:
            if keyword not in detected_keywords:
                detected_keywords.append(keyword)
            urgency_count += 1

    urgency_score = min(100, urgency_count * 25 + len(pattern_categories) * 15)

    return {
        "detected_keywords": detected_keywords,
        "pattern_categories": pattern_categories,
        "urgency_score": urgency_score,
    }
