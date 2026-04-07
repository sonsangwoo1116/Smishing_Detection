from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.analysis import SafeDomain, KnownPattern

SAFE_DOMAINS = [
    ("google.com", "portal"), ("naver.com", "portal"), ("daum.net", "portal"),
    ("kakao.com", "portal"), ("samsung.com", "manufacturer"), ("apple.com", "manufacturer"),
    ("microsoft.com", "tech"), ("github.com", "tech"),
    ("cj.net", "logistics"), ("hanjin.co.kr", "logistics"), ("lotteglogis.com", "logistics"),
    ("epost.go.kr", "logistics"), ("logen.co.kr", "logistics"),
    ("gov.kr", "government"), ("police.go.kr", "government"), ("nts.go.kr", "government"),
    ("kisa.or.kr", "government"), ("mois.go.kr", "government"),
    ("kbstar.com", "finance"), ("shinhan.com", "finance"), ("wooribank.com", "finance"),
    ("hanabank.com", "finance"), ("ibk.co.kr", "finance"), ("nhbank.com", "finance"),
    ("youtube.com", "media"), ("instagram.com", "media"), ("facebook.com", "media"),
]

KNOWN_PATTERNS = [
    # 키워드 패턴
    ("KEYWORD", "무료 쿠폰 받기", "WARNING", "스팸광고", "무료 쿠폰 유도"),
    ("KEYWORD", "당첨되셨습니다", "WARNING", "스팸광고", "허위 당첨"),
    ("KEYWORD", "본인확인 바로가기", "HIGH", "금융사칭", "본인확인 사칭 피싱"),
    ("KEYWORD", "계정이 정지", "HIGH", "기관사칭", "계정 정지 사칭"),
    # 도메인 패턴 (블랙리스트)
    ("DOMAIN", "fake-delivery.xyz", "HIGH", "택배사칭", "알려진 피싱 도메인"),
    ("DOMAIN", "gov-kr.top", "HIGH", "정부사칭", "정부 사칭 도메인"),
]


async def seed_safe_domains(db: AsyncSession):
    """안전 도메인 화이트리스트를 시딩한다."""
    for domain, category in SAFE_DOMAINS:
        result = await db.execute(select(SafeDomain).where(SafeDomain.domain == domain))
        if result.scalar_one_or_none() is None:
            db.add(SafeDomain(domain=domain, category=category))
    await db.flush()


async def seed_known_patterns(db: AsyncSession):
    """알려진 스미싱 패턴을 시딩한다."""
    for pattern_type, value, risk, category, desc in KNOWN_PATTERNS:
        result = await db.execute(
            select(KnownPattern).where(
                KnownPattern.pattern_type == pattern_type,
                KnownPattern.pattern_value == value,
            )
        )
        if result.scalar_one_or_none() is None:
            db.add(KnownPattern(
                pattern_type=pattern_type,
                pattern_value=value,
                risk_level=risk,
                category=category,
                description=desc,
            ))
    await db.flush()


async def load_safe_domains(db: AsyncSession) -> set[str]:
    """활성 안전 도메인 목록을 로드한다."""
    result = await db.execute(select(SafeDomain.domain).where(SafeDomain.is_active == True))
    return {row[0] for row in result.all()}


async def load_blacklist_domains(db: AsyncSession) -> set[str]:
    """블랙리스트 도메인 목록을 로드한다."""
    result = await db.execute(
        select(KnownPattern.pattern_value).where(
            KnownPattern.pattern_type == "DOMAIN",
            KnownPattern.is_active == True,
        )
    )
    return {row[0] for row in result.all()}
