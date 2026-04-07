# Smishing Detection AI Agent

SMS 문자메시지의 스미싱(피싱) 여부를 AI로 분석하는 서비스입니다.

## 주요 기능

- **URL 추출 및 추적**: 문자 내 모든 URL을 감지하고, 단축 URL을 최종 목적지까지 추적
- **Google Web Risk API**: URL의 악성/피싱/멀웨어 여부를 Google 보안 DB로 검증
- **본문 키워드 분석**: 택배사칭, 금융사칭, 정부사칭, 가족사칭 등 알려진 스미싱 패턴 탐지
- **LLM 종합 분석**: OpenAI GPT로 모든 분석 결과를 종합하여 위험도 판정 + 근거 설명
- **위험도 3단계**: HIGH(고위험) / WARNING(위험) / NORMAL(보통)
- **Graceful Degradation**: 외부 API 장애 시 규칙 기반 fallback 판정

## 아키텍처

```
┌─────────────────────────────────────────────────────┐
│                  FastAPI Backend                      │
│                                                      │
│  [1] URL 추출 → [2] 단축URL 추적 → [3] Web Risk    │
│  → [4] 링크 분류 → [5] 키워드 분석 → [6] LLM 분석  │
│  → [7] 결과 집계                                    │
│                                                      │
│  PostgreSQL (이력) + Redis (캐시)                    │
└─────────────────────────────────────────────────────┘
         │                          │
         ▼                          ▼
  OpenAI GPT API          Google Web Risk API
```

## 기술 스택

| 구분 | 기술 |
|------|------|
| Backend | Python 3.10+, FastAPI, SQLAlchemy, Alembic |
| LLM | OpenAI API (gpt-5.4-mini) |
| URL 안전성 | Google Web Risk API |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Frontend | React 18, Vite, Tailwind CSS |
| 컨테이너 | Docker Compose |

## 프로젝트 구조

```
├── src/
│   ├── main.py                     # FastAPI 앱 엔트리포인트
│   ├── core/
│   │   ├── config.py               # 환경변수 설정
│   │   ├── database.py             # PostgreSQL 연결
│   │   ├── cache.py                # Redis 캐시
│   │   └── circuit_breaker.py      # 외부 API 장애 대응
│   ├── pipeline/
│   │   ├── orchestrator.py         # 7-step 분석 파이프라인
│   │   ├── url_extractor.py        # URL 추출
│   │   ├── url_resolver.py         # 단축 URL 추적
│   │   ├── web_risk_checker.py     # Google Web Risk
│   │   ├── link_classifier.py      # 링크 분류
│   │   ├── text_analyzer.py        # 키워드 패턴 분석
│   │   ├── llm_analyzer.py         # LLM 분석 + fallback
│   │   └── result_aggregator.py    # 결과 집계
│   ├── api/v1/
│   │   ├── routes/analyze.py       # POST /api/v1/analyze
│   │   ├── routes/health.py        # GET /api/v1/health
│   │   ├── routes/history.py       # GET /api/v1/history
│   │   └── dependencies.py         # API Key 인증
│   ├── models/analysis.py          # DB 모델
│   ├── repositories/               # 데이터 접근 계층
│   ├── services/                   # 비즈니스 로직
│   └── cli/manage.py               # 관리 CLI 도구
├── frontend/                       # React SPA
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api/client.js
│   │   └── components/             # 분석/이력/상태 탭
│   ├── vite.config.js
│   └── package.json
├── tests/                          # 테스트 (32개)
├── docker-compose.yml              # PostgreSQL + Redis + App
├── Dockerfile
├── requirements.txt
└── .env.example
```

## 빠른 시작

### 1. 인프라 실행

```bash
docker-compose up -d postgres redis
```

### 2. 환경변수 설정

```bash
cp .env.example .env
# .env 파일에 API 키 입력:
#   OPENAI_API_KEY=sk-proj-...
#   GOOGLE_WEB_RISK_API_KEY=...
```

### 3. 백엔드 실행

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001
```

### 4. 프론트엔드 실행

```bash
cd frontend
npm install
npm run dev    # http://localhost:3000
```

### 5. 테스트

```bash
# 단위 테스트 (32개)
pytest tests/ -v

# API 직접 호출
curl -X POST http://localhost:8001/api/v1/analyze \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"message": "[Web발신] 택배 도착 확인: http://bit.ly/3xFake"}'
```

## API

| Method | Endpoint | 설명 | 인증 |
|--------|----------|------|------|
| POST | `/api/v1/analyze` | 스미싱 분석 | API Key 필수 |
| GET | `/api/v1/history` | 분석 이력 조회 | - |
| GET | `/api/v1/history/{id}` | 상세 조회 | - |
| GET | `/api/v1/health` | 서버 상태 | - |

### 분석 응답 예시

```json
{
  "success": true,
  "data": {
    "risk_level": "WARNING",
    "risk_score": 72,
    "summary": "택배 사칭 문구와 단축 URL이 포함된 스미싱 의심 문자입니다.",
    "explanation": "1. 택배사칭 스미싱 패턴과 일치...",
    "urls": [{
      "original_url": "https://myip.kr/DIBMf",
      "resolved_url": "https://m.kbcard.com/SVC/DVIEW/...",
      "redirect_chain": ["https://myip.kr/DIBMf", "https://m.kbcard.com/new/10362", "..."],
      "is_shortened": true,
      "web_risk_result": {"is_safe": true, "source": "web_risk_api"}
    }],
    "text_analysis": {
      "detected_keywords": ["택배", "주소지 미확인"],
      "pattern_categories": ["택배사칭"]
    }
  }
}
```

## CLI 도구

```bash
# API Key 관리
python -m src.cli.manage apikey create my-key
python -m src.cli.manage apikey list
python -m src.cli.manage apikey revoke <key-id>

# 화이트리스트/블랙리스트
python -m src.cli.manage whitelist add naver.com --category portal
python -m src.cli.manage blacklist add evil.xyz --risk HIGH
python -m src.cli.manage whitelist list
```

## 분석 파이프라인

```
입력: 문자메시지
  │
  ├─ [Step 1] URL 추출 (정규표현식, 최대 10개)
  ├─ [Step 2] URL 추적 (HEAD/GET, 병렬, 단축URL→원본)
  ├─ [Step 3] Web Risk 검사 (캐시→화이트리스트→블랙리스트→API)
  ├─ [Step 4] 링크 분류 (광고/앱다운로드/피싱/정상)
  ├─ [Step 5] 키워드 분석 (택배/금융/정부/가족 사칭 등)
  ├─ [Step 6] LLM 분석 (GPT, 장애 시 규칙 기반 fallback)
  └─ [Step 7] 결과 집계
  │
출력: 위험도 + 점수 + 설명 + URL 분석 + 키워드
```
