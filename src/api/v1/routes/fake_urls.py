"""테스트용 가짜 피싱 URL 엔드포인트. 단축 URL → 리다이렉트 → 최종 피싱 페이지 시뮬레이션."""

from fastapi import APIRouter
from fastapi.responses import RedirectResponse, HTMLResponse

router = APIRouter(prefix="/fake", tags=["Test URLs"])

# ============================================================
# 단축 URL 시뮬레이션 (1차 리다이렉트)
# ============================================================

@router.get("/s/cj001")
async def short_cj():
    """CJ택배 사칭 단축 URL → 중간 리다이렉트"""
    return RedirectResponse("/fake/r/delivery-check")

@router.get("/s/health01")
async def short_health():
    """건강보험 사칭 단축 URL"""
    return RedirectResponse("/fake/r/nhis-result")

@router.get("/s/fine01")
async def short_fine():
    """교통범칙금 사칭 단축 URL"""
    return RedirectResponse("/fake/r/traffic-pay")

@router.get("/s/kb01")
async def short_kb():
    """KB카드 사칭 단축 URL"""
    return RedirectResponse("/fake/r/kb-fraud")

@router.get("/s/court01")
async def short_court():
    """법원 사칭 단축 URL"""
    return RedirectResponse("/fake/r/ecourt-case")

@router.get("/s/bank01")
async def short_bank():
    """은행 보안앱 사칭 단축 URL → APK"""
    return RedirectResponse("/fake/r/bank-security")

@router.get("/s/gov01")
async def short_gov():
    """정부지원금 사칭 단축 URL"""
    return RedirectResponse("/fake/r/gov-support")

@router.get("/s/bugo01")
async def short_bugo():
    """부고 사칭 단축 URL"""
    return RedirectResponse("/fake/r/funeral-info")

# ============================================================
# 중간 리다이렉트 (2차 → 최종 피싱 페이지)
# ============================================================

@router.get("/r/delivery-check")
async def redirect_delivery():
    return RedirectResponse("/fake/phish/cjlogis-kr.top/delivery")

@router.get("/r/nhis-result")
async def redirect_nhis():
    return RedirectResponse("/fake/phish/nhis-checkup.xyz/result")

@router.get("/r/traffic-pay")
async def redirect_traffic():
    return RedirectResponse("/fake/phish/efine-police.click/pay")

@router.get("/r/kb-fraud")
async def redirect_kb():
    return RedirectResponse("/fake/phish/kb-card-center.top/fraud")

@router.get("/r/ecourt-case")
async def redirect_court():
    return RedirectResponse("/fake/phish/ecourt-go-kr.xyz/case")

@router.get("/r/bank-security")
async def redirect_bank():
    return RedirectResponse("/fake/phish/wooribank-sec.top/install.apk")

@router.get("/r/gov-support")
async def redirect_gov():
    return RedirectResponse("/fake/phish/gov24-support.xyz/apply")

@router.get("/r/funeral-info")
async def redirect_funeral():
    return RedirectResponse("/fake/phish/memorial-kr.xyz/view")

# ============================================================
# 최종 피싱 페이지 (테스트용 안전한 HTML)
# ============================================================

PHISH_TEMPLATE = """<!DOCTYPE html>
<html><head><title>{title}</title></head>
<body style="background:#1a1a2e;color:#e94560;text-align:center;padding:80px;font-family:sans-serif">
<h1>⚠ 테스트 피싱 페이지</h1>
<h2>{title}</h2>
<p style="color:#aaa">이것은 스미싱 탐지 테스트를 위한 가짜 페이지입니다.</p>
<p style="color:#aaa">실제 피싱 사이트였다면 여기서 개인정보를 탈취했을 것입니다.</p>
<p style="color:#555;margin-top:40px">fake domain: {domain}</p>
</body></html>"""

@router.get("/phish/{domain}/{path:path}")
async def fake_phish_page(domain: str, path: str):
    titles = {
        "cjlogis-kr.top": "CJ대한통운 주소 확인",
        "nhis-checkup.xyz": "국민건강보험 검진 결과",
        "efine-police.click": "교통범칙금 납부",
        "kb-card-center.top": "KB국민카드 해외결제 신고",
        "ecourt-go-kr.xyz": "전자소송 서류 확인",
        "wooribank-sec.top": "우리은행 보안앱 설치",
        "gov24-support.xyz": "정부지원금 신청",
        "memorial-kr.xyz": "부고 / 조화 안내",
    }
    title = titles.get(domain, f"피싱 테스트: {domain}")
    return HTMLResponse(PHISH_TEMPLATE.format(title=title, domain=domain))
