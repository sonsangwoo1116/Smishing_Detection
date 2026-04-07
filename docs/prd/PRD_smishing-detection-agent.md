# Smishing Detection AI Agent PRD

> **Version**: 1.1
> **Created**: 2026-04-07
> **Status**: Draft

## 1. Overview

### 1.1 Problem Statement
스미싱(SMS Phishing) 문자가 급증하고 있으나, 일반 사용자가 스미싱 여부를 즉시 판단하기 어렵다. 외부 링크의 실제 안전성을 검증하고, 문자 본문의 사기성을 AI로 분석하여 위험도를 판정하는 Agent가 필요하다.

### 1.2 Goals
- 문자메시지 내 외부 링크 자동 탐지
- **단축 URL 원본 추적** (bit.ly, me2.do 등 → 최종 목적지 URL 해석)
- **Google Web Risk API로 URL 안전성 검증** (악성/피싱/멀웨어 판별)
- 링크 유형 분류 (광고, 앱 다운로드, 피싱 의심 등)
- 문자 본문 컨텍스트 분석 (키워드 필터링 + LLM)
- 스미싱 위험도 3단계(고위험/위험/보통) 분류 및 근거 설명
- OpenAI API(gpt-5.4-mini) 활용 LLM 기반 종합 분석

### 1.3 Non-Goals (Out of Scope)
- 실제 웹페이지 렌더링/크롤링 (JavaScript 실행)
- 악성 APK/앱 바이너리 정적/동적 분석
- 실시간 SMS 수신 연동 (통신사 API)
- 사용자 인증/회원 관리
- 모바일 앱 개발
- VirusTotal API 연동 (비용 과다)

### 1.4 Scope
| 포함 | 제외 |
|------|------|
| 문자메시지 텍스트 입력 및 분석 | 이미지/MMS 분석 |
| URL 추출 + 단축 URL 원본 추적 | JavaScript 기반 리다이렉트 해석 |
| Google Web Risk API URL 안전성 검사 | VirusTotal 연동 |
| LLM 기반 스미싱 판별 + 키워드 분석 | 악성코드 실행/분석 |
| 위험도 분류 및 설명 생성 | 통신사 연동 |
| REST API 서버 제공 | 프론트엔드 UI |
| 분석 이력 저장 + URL 검사 결과 캐싱 | 사용자 인증 시스템 |

## 2. User Stories

### 2.1 Primary User
As a **일반 사용자/보안 관리자**, I want to **의심스러운 문자메시지를 AI에게 분석 요청** so that **스미싱 여부와 위험도를 빠르게 판단할 수 있다**.

### 2.2 Acceptance Criteria (Gherkin)

**Scenario: 단축 URL이 포함된 스미싱 문자 분석**
```
Given 사용자가 "[Web발신] 고객님 택배가 도착했습니다. 확인: http://bit.ly/3xFake" 메시지를 입력
When AI Agent가 분석을 수행
Then 단축 URL "http://bit.ly/3xFake"의 최종 목적지 URL이 추적됨
And 최종 URL이 Google Web Risk API로 안전성 검사됨
And 위험도가 "고위험"으로 판정됨
And "택배 사칭, 단축 URL 사용, Google Web Risk 위협 탐지" 등의 판단 근거가 제공됨
```

**Scenario: 정상 광고 문자 분석**
```
Given 사용자가 "[Web발신] OO마트 주말 특가! 최대 50% 할인 https://www.oomart.co.kr/sale" 메시지를 입력
When AI Agent가 분석을 수행
Then URL "https://www.oomart.co.kr/sale"가 탐지됨
And Google Web Risk API에서 위협 없음 확인됨
And 위험도가 "보통"으로 판정됨
And "공식 도메인, Web Risk 안전, 일반 광고 패턴" 등의 판단 근거가 제공됨
```

**Scenario: 링크 없는 사칭 문자 분석**
```
Given 사용자가 "엄마 나 폰 바꿨어 이 번호로 연락줘" 메시지를 입력
When AI Agent가 분석을 수행
Then 외부 링크가 없음이 확인됨
And 본문 키워드 분석에서 "가족 사칭" 패턴이 탐지됨
And LLM이 "위험"으로 판정
And "가족 사칭 패턴, 번호 변경 유도" 등의 판단 근거가 제공됨
```

**Scenario: 앱 다운로드 유도 문자 분석**
```
Given 사용자가 "보안 강화를 위해 앱을 설치해주세요 http://malicious.com/app.apk" 메시지를 입력
When AI Agent가 분석을 수행
Then URL에서 ".apk" 파일 다운로드 패턴이 탐지됨
And Google Web Risk API 검사 수행됨
And 위험도가 "고위험"으로 판정됨
And "APK 직접 다운로드 유도, 비공식 경로, 보안앱 사칭" 등의 판단 근거가 제공됨
```

## 3. Functional Requirements

| ID | Requirement | Priority | Dependencies |
|----|------------|----------|--------------|
| FR-001 | 문자메시지 텍스트를 입력받는 REST API 엔드포인트 | P0 (Must) | - |
| FR-002 | 메시지 내 URL/링크 자동 추출 (정규표현식) | P0 (Must) | FR-001 |
| FR-003 | **단축 URL 원본 추적** (HTTP HEAD redirect following) | P0 (Must) | FR-002 |
| FR-004 | **Google Web Risk API로 URL 안전성 검사** (악성/피싱/멀웨어) | P0 (Must) | FR-003 |
| FR-005 | URL 유형 분류 (광고/앱다운로드/피싱의심/정상) | P0 (Must) | FR-003, FR-004 |
| FR-006 | **본문 키워드 기반 스미싱 패턴 탐지** (택배, 정부지원금, 부고 등) | P0 (Must) | FR-001 |
| FR-007 | **LLM(gpt-5.4-mini) 종합 스미싱 분석** (URL결과 + 본문분석 통합) | P0 (Must) | FR-004, FR-006 |
| FR-008 | 위험도 3단계 분류: 고위험(HIGH)/위험(WARNING)/보통(NORMAL) | P0 (Must) | FR-007 |
| FR-009 | 분류 근거 설명 생성 (한국어) | P0 (Must) | FR-007 |
| FR-010 | **URL 검사 결과 캐싱** (동일 URL 재검사 방지, 비용 절감) | P1 (Should) | FR-004 |
| FR-011 | 분석 이력 저장 (DB) | P1 (Should) | FR-001 |
| FR-012 | 분석 이력 조회 API | P1 (Should) | FR-011 |
| FR-013 | 알려진 스미싱 패턴 DB 관리 (키워드, URL 블랙리스트) | P1 (Should) | - |
| FR-014 | 헬스체크 API 엔드포인트 | P1 (Should) | - |
| FR-015 | **URL 최대 처리 개수 제한** (메시지당 최대 10개, 초과 시 앞 10개만 분석) | P0 (Must) | FR-002 |
| FR-016 | **다수 URL 병렬 처리** (asyncio.gather로 Step 2~4 동시 수행) | P0 (Must) | FR-003, FR-015 |
| FR-017 | **LLM 응답 검증 및 재시도** (JSON 파싱 실패 시 최대 2회 재시도, Structured Outputs 활용) | P0 (Must) | FR-007 |
| FR-018 | 배치 분석 API (최대 10건, 비동기 처리 + 결과 폴링) | P2 (Could) | FR-001 |
| FR-019 | 화이트리스트/블랙리스트 관리 CLI 도구 | P1 (Should) | FR-013 |

## 4. Non-Functional Requirements

### 4.0 Scale Grade (규모 등급)

**선택된 등급: Growth** (1인 운영, 대규모 트래픽 대응)

| 항목 | 값 |
|------|-----|
| 운영 인원 | 1명 |
| 예상 DAU | 10,000 ~ 100,000 |
| 피크 동시접속 | 1,000 ~ 10,000 |
| 예상 데이터량 | 10 ~ 100GB |

> 1인 운영 특성상 **자동화와 모니터링**에 중점. 외부 API 비용 최적화 필수.

### 4.1 Performance SLA

| 지표 | 목표값 |
|------|--------|
| Response Time (p95) | < 5,000ms (URL 추적 + Web Risk + LLM 포함) |
| Response Time (p95, 캐시 히트 시) | < 3,000ms |
| URL 추적 타임아웃 | 5,000ms |
| Google Web Risk API 타임아웃 | 3,000ms |
| LLM API 타임아웃 | 10,000ms |
| Throughput (RPS) | 100 RPS |

### 4.2 Availability SLA

| 항목 | 값 |
|------|-----|
| Uptime 목표 | 99.9% |
| 허용 다운타임(월) | 43.8분 |

### 4.3 Data Requirements

| 항목 | 값 |
|------|-----|
| 현재 데이터량 | 0MB (신규) |
| 월간 증가율 | 분석 건수 기반, 약 1-5GB/월 |
| 데이터 보존 기간 | 6개월 (이후 아카이브) |
| URL 캐시 TTL | 24시간 (Web Risk 결과) |

### 4.4 Recovery

| 항목 | 값 |
|------|-----|
| RTO (복구 시간) | 4시간 |
| RPO (복구 시점) | 1시간 |

### 4.5 Security
- Data encryption: In transit (HTTPS/TLS)
- **OpenAI API Key**: 환경변수 `.env`로 관리, 코드 하드코딩 금지
- **Google Web Risk API Key**: 환경변수 `.env`로 관리
- 입력값 검증: XSS, Injection 방지
- 메시지 길이 제한: 최대 2000 유니코드 코드포인트 (LMS 기준 커버)
- Rate Limiting: IP당 분당 60회 제한
- URL 추적 시 안전장치: HEAD 요청만 사용, body 다운로드 금지
- 로깅 민감정보 마스킹: 발신자번호 뒤 4자리 마스킹, 메시지 원문은 분석 이력 DB에만 저장

### 4.5.1 API Key 관리 정책

**인증 방식**: X-API-Key 헤더 기반

| 항목 | 정책 |
|------|------|
| 키 저장 | SHA-256 해싱 후 DB 저장 (평문 저장 금지) |
| 다중 키 | 클라이언트별 개별 API Key 발급 지원 |
| 키별 Rate Limit | 키 단위 사용량 추적 및 제한 가능 |
| 키 로테이션 | 새 키 발급 → 기존 키 24시간 유예 → 폐기 |
| 긴급 폐기 | 유출 의심 시 즉시 비활성화 (CLI 도구로 실행) |
| 키 메타데이터 | 발급일, 마지막 사용일, 사용량, 만료일(선택) |

**API Key 테이블**:
```sql
CREATE TABLE api_keys (
    id TEXT PRIMARY KEY,
    key_hash TEXT NOT NULL UNIQUE,          -- SHA-256 해시
    name TEXT NOT NULL,                     -- 키 식별명 (예: "mobile-app-v1")
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit_per_minute INTEGER DEFAULT 60,
    total_usage INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP,                   -- NULL이면 무기한
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.6 Graceful Degradation 정책

외부 API 장애 시 서비스 전체가 마비되지 않도록 단계적 fallback을 적용한다.

#### Google Web Risk API 장애 시
```
정상 모드:  캐시 → 화이트리스트 → 블랙리스트 → Web Risk API
장애 모드:  캐시 → 화이트리스트 → 블랙리스트 → [스킵]
           └→ LLM에 "Web Risk 결과 없음 (API 장애)" context 전달
           └→ 응답에 degraded: true 표시
```
- URL이 캐시/화이트리스트/블랙리스트 어디에도 없으면 → LLM이 URL 패턴만으로 판단
- **Circuit Breaker**: 연속 5회 실패 시 30초간 API 호출 차단, 이후 1건 시도하여 복구 확인

#### OpenAI LLM API 장애 시
```
정상 모드:  키워드 분석 + Web Risk + LLM 종합 판정
장애 모드:  키워드 분석 + Web Risk → 규칙 기반 Fallback 판정
```

**규칙 기반 Fallback 판정 로직**:
| 조건 | Fallback 판정 |
|------|--------------|
| Web Risk 위협 탐지 | → HIGH |
| 블랙리스트 URL 포함 | → HIGH |
| .apk/.exe 다운로드 URL | → HIGH |
| 스미싱 키워드 3개 이상 + 긴급성 표현 | → HIGH |
| 스미싱 키워드 1~2개 또는 단축URL | → WARNING |
| 화이트리스트 URL + 키워드 없음 | → NORMAL |
| 그 외 | → WARNING (안전 측 판단 회피) |

- 응답에 `degraded: true` + `degraded_reason: "LLM API unavailable, rule-based fallback applied"` 표시
- 정확도 저하 가능성을 explanation에 명시
- **Circuit Breaker**: 연속 3회 실패 시 60초간 API 호출 차단

#### 응답 degraded 필드
```json
{
  "success": true,
  "data": {
    "degraded": false,
    "degraded_services": [],
    ...
  }
}
// 장애 시:
{
  "success": true,
  "data": {
    "degraded": true,
    "degraded_services": ["openai_llm"],
    "degraded_reason": "LLM API unavailable, rule-based fallback applied",
    ...
  }
}
```

### 4.7 캐시 전략 (차등 TTL)

| URL 판정 결과 | 캐시 TTL | 근거 |
|--------------|---------|------|
| 위협 탐지 (MALWARE, SOCIAL_ENGINEERING 등) | **1시간** | 위협 해제 시 빠른 반영 필요 |
| 안전 판정 (no threats) | **24시간** | 안전 URL은 변동 가능성 낮음 |
| API 에러/타임아웃 | **캐시 안 함** | 재시도 필요 |

수동 캐시 무효화: CLI 도구로 특정 URL 캐시 즉시 삭제 가능

### 4.8 모니터링 & 알림 체계

1인 운영에서 장애를 빠르게 인지하기 위한 자동 알림 체계.

| 알림 조건 | 임계값 | 채널 |
|----------|--------|------|
| API 에러율 급증 | 5xx 비율 > 5% (5분간) | Slack/Discord Webhook |
| 외부 API 장애 | Circuit Breaker 발동 시 | Slack/Discord Webhook |
| Web Risk API 비용 | 월 호출 80,000건 초과 | Slack/Discord Webhook |
| OpenAI API 비용 | 일일 비용 $10 초과 | Slack/Discord Webhook |
| 응답 지연 | p95 > 10초 (5분간) | Slack/Discord Webhook |
| 디스크/DB 사용량 | 80% 초과 | Slack/Discord Webhook |

**모니터링 도구**: Prometheus + Grafana (자체 호스팅) 또는 Cloud 모니터링 서비스
**에러 추적**: Sentry (무료 티어 활용)

### 4.9 데이터 아카이브 & 개인정보 처리

| 항목 | 정책 |
|------|------|
| 분석 이력 보존 | 활성 DB: 6개월, 이후 아카이브 테이블로 이동 |
| 아카이브 방법 | `analysis_history_archive` 테이블로 이동 (월 1회 자동 배치) |
| 아카이브 데이터 조회 | 조회 불가 (필요 시 수동 복원) |
| 발신자 번호 처리 | 아카이브 시 SHA-256 해싱 (비식별화) |
| 메시지 원문 처리 | 아카이브 시 삭제, 분석 결과(위험도/설명)만 보존 |
| URL 캐시 | TTL 만료 시 자동 삭제 |
| 완전 삭제 | 1년 경과 아카이브 데이터 영구 삭제 |

### 4.10 API 비용 관리

| API | 무료 구간 | 유료 단가 | 월 예상 비용 |
|-----|----------|----------|-------------|
| Google Web Risk API | 100,000건/월 | $0.50/1,000건 | DAU 5만 기준: 무료~$25 |
| OpenAI gpt-5.4-mini | 종량제 | input/output 토큰 기반 | 사용량 비례 |

**비용 절감 전략**:
- URL 검사 결과 24시간 캐싱 (동일 URL 재검사 방지)
- 알려진 안전 도메인 화이트리스트 (google.com, naver.com 등 → API 호출 스킵)
- LLM 프롬프트 최적화 (토큰 최소화)

## 5. Technical Design

### 5.1 기술 스택

| 구분 | 기술 |
|------|------|
| Language | Python 3.11+ |
| Framework | FastAPI |
| LLM | OpenAI API (gpt-5.4-mini) |
| URL 안전성 검사 | Google Web Risk API |
| URL 추적 | httpx (비동기 HTTP HEAD + redirect following) |
| Database | PostgreSQL (Growth 규모 대응, 동시 쓰기 지원) |
| 캐싱 | Redis (URL 검사 결과 캐싱, TTL 관리, 프로세스 간 공유) |
| ORM | SQLAlchemy |
| 환경관리 | python-dotenv |
| 테스트 | pytest |

### 5.2 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client                                │
│                   (REST API 호출)                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Server                             │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                  API Router Layer                       │  │
│  │   POST /api/v1/analyze                                 │  │
│  │   GET  /api/v1/history                                 │  │
│  │   GET  /api/v1/health                                  │  │
│  └──────────────────────┬─────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────▼─────────────────────────────────┐  │
│  │            Smishing Analysis Pipeline                   │  │
│  │                                                         │  │
│  │  [Step 1] URL Extractor (정규표현식)                     │  │
│  │      │                                                  │  │
│  │      ▼                                                  │  │
│  │  [Step 2] URL Resolver (단축 URL → 원본 추적)            │  │
│  │      │    httpx HEAD + redirect following                │  │
│  │      │    알려진 단축서비스 사전 탐지                      │  │
│  │      │    max_redirects=10, timeout=5s                   │  │
│  │      ▼                                                  │  │
│  │  [Step 3] URL Safety Checker                            │  │
│  │      │    ├─ 캐시 조회 (24h TTL)                         │  │
│  │      │    ├─ 화이트리스트 체크                            │  │
│  │      │    ├─ 블랙리스트 체크 (자체 DB)                    │  │
│  │      │    └─ Google Web Risk API 조회                    │  │
│  │      ▼                                                  │  │
│  │  [Step 4] Link Classifier                               │  │
│  │      │    광고 / 앱다운로드 / 피싱의심 / 정상 분류         │  │
│  │      ▼                                                  │  │
│  │  [Step 5] Text Analyzer (본문 분석)                      │  │
│  │      │    키워드 패턴 매칭 (택배, 부고, 지원금 등)         │  │
│  │      │    긴급성/공포 유도 표현 탐지                       │  │
│  │      ▼                                                  │  │
│  │  [Step 6] LLM Analyzer (gpt-5.4-mini)                   │  │
│  │      │    URL 분석결과 + 본문분석 + Web Risk 결과          │  │
│  │      │    → 종합 위험도 판정 + 설명 생성                   │  │
│  │      ▼                                                  │  │
│  │  [Step 7] Result Aggregator                             │  │
│  │         최종 위험도 + 구조화된 응답 생성                   │  │
│  └─────────────────────────────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────▼─────────────────────────────────┐  │
│  │              Database + Cache Layer                      │  │
│  │   ├─ analysis_history (분석 이력)                        │  │
│  │   ├─ known_patterns (스미싱 패턴 DB)                     │  │
│  │   ├─ url_cache (Web Risk 결과 캐시, TTL 24h)             │  │
│  │   └─ safe_domains (화이트리스트)                          │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
          │                              │
          ▼                              ▼
┌──────────────────┐          ┌──────────────────┐
│  OpenAI API      │          │ Google Web Risk   │
│  (gpt-5.4-mini)  │          │ API               │
└──────────────────┘          └──────────────────┘
```

### 5.3 Agent 파이프라인 상세

#### Step 1: URL Extractor
```
입력: 문자메시지 원문
처리: 정규표현식으로 URL 추출
  - http://, https:// 프로토콜 URL
  - www. 시작 URL
  - 도메인 패턴 (example.com/path)
출력: URL 목록 (0~N개)
분기: URL 없으면 → Step 5 (본문 분석)로 직행
```

#### Step 2: URL Resolver (단축 URL 원본 추적)
```
입력: 추출된 URL 목록 (최대 10개, 초과 시 앞 10개만 처리)
처리:
  ★ 모든 URL을 asyncio.gather로 병렬 처리 (Step 2~4 통합)
  ★ 전체 URL 처리 타임아웃: 8초 (개별 5초와 별도)

  1. 알려진 단축 URL 서비스 목록과 대조
     - bit.ly, tinyurl.com, t.co, goo.gl, is.gd, v.gd
     - ow.ly, buff.ly, bl.ink, han.gl, me2.do, vo.la, zrr.kr
  2. 단축 URL인 경우 → HTTP HEAD 요청으로 리다이렉트 추적
     - allow_redirects=True
     - max_redirects=10
     - timeout=5초
     - User-Agent 설정 (봇 차단 우회)
  3. 리다이렉트 체인 전체 기록
  4. 최종 목적지 URL 획득

안전장치:
  - HEAD 요청만 사용 (body 다운로드 안 함)
  - 무한 리다이렉트 방어 (max 10회)
  - 타임아웃 5초 (개별), 8초 (전체)
  - 해석 실패 시 → "해석 불가" 플래그 + 위험도 상향

한계 대응:
  - JS 기반 리다이렉트: HEAD로 탐지 불가 → LLM에 "JS redirect 가능성" 전달
  - CAPTCHA 보호 URL: 해석 실패 → 자동 위험 플래그 부여
  - 만료 단축 URL: 404 → "만료된 단축 URL" 표시

출력: {original_url, final_url, redirect_chain[], is_shortened, resolve_status}
```

#### Step 3: URL Safety Checker (Google Web Risk API)
```
입력: 최종 목적지 URL (resolved URL)
처리 순서:
  1. 캐시 조회 (24시간 TTL) → 히트 시 캐시 결과 반환
  2. 화이트리스트 체크 (google.com, naver.com 등) → 매칭 시 SAFE 반환
  3. 자체 블랙리스트 DB 조회 → 매칭 시 DANGEROUS 반환
  4. Google Web Risk API 호출
     - threatTypes: MALWARE, SOCIAL_ENGINEERING, UNWANTED_SOFTWARE
     - 결과 캐싱 (24h TTL)

비용 절감:
  - 캐시 히트 → API 호출 스킵
  - 화이트리스트 도메인 → API 호출 스킵
  - 월 100,000건 무료 범위 내 운영 목표

출력: {url, threat_type, is_safe, threat_details, source(cache/whitelist/blacklist/web_risk)}
```

#### Step 4: Link Classifier
```
입력: URL + resolved URL + Web Risk 결과
처리:
  - 도메인 분석 (공식 도메인 vs 의심 도메인)
  - 파일 확장자 체크 (.apk, .exe, .ipa → 앱 다운로드)
  - 광고 패턴 매칭 (쇼핑몰, 이벤트 등)
  - Web Risk 위협 여부 반영

출력: category (AD | APP_DOWNLOAD | PHISHING_SUSPECT | MALWARE | NORMAL | UNKNOWN)
```

#### Step 5: Text Analyzer (본문 키워드 분석)
```
입력: 메시지 원문
처리:
  1. 스미싱 키워드 패턴 매칭
     - 택배 사칭: "택배", "배송", "주소지 미확인", "배달 불가"
     - 금융 사칭: "결제 완료", "승인", "카드", "출금", "이체"
     - 정부 사칭: "정부지원금", "재난지원", "건강검진", "국민연금"
     - 가족 사칭: "엄마", "아빠", "폰 바꿨", "번호 변경"
     - 기관 사칭: "경찰", "검찰", "법원", "국세청"
     - 부고/경조사: "부고", "장례", "결혼"
  2. 긴급성/공포 유도 표현 탐지
     - "지금 바로", "즉시", "긴급", "과태료", "체포", "소송"
  3. 패턴 매칭 결과 + 신뢰도 점수 산출

출력: {detected_keywords[], pattern_categories[], urgency_score}
```

#### Step 6: LLM Analyzer (gpt-5.4-mini)
```
입력 (Context):
  - 메시지 원문
  - URL 분석 결과 (추적 결과, Web Risk 결과, 링크 분류)
  - 본문 키워드 분석 결과

처리:
  - 모든 분석 결과를 종합하여 최종 위험도 판정
  - 판단 근거를 한국어로 생성
  - 위험도 점수(0~100) 산출
  - OpenAI Structured Outputs (response_format) 활용하여 JSON 스키마 강제

응답 검증 & 재시도 정책:
  1. JSON 파싱 실패 → 최대 2회 재시도 (총 3회 시도)
  2. risk_level 값 검증: HIGH, WARNING, NORMAL 외 → 재시도
  3. risk_score 범위 검증: 0~100 외 → 클램핑 (0 미만→0, 100 초과→100)
  4. 3회 모두 실패 → 규칙 기반 Fallback 판정 (Section 4.6 참조)
  5. Fallback 적용 시 degraded: true 표시

출력: {risk_level, risk_score, summary, explanation}
```

#### Step 7: Result Aggregator
```
모든 Step의 결과를 구조화된 JSON 응답으로 조합
```

### 5.4 API Specification

---

#### `POST /api/v1/analyze`

**Description**: 문자메시지 스미싱 분석 요청

**Authentication**: API Key (X-API-Key 헤더)

**Headers**:
| Header | Required | Description |
|--------|----------|-------------|
| X-API-Key | Yes | API 인증 키 |
| Content-Type | Yes | application/json |

**Request Body**:
```json
{
  "message": "string (required) - 분석할 문자메시지 텍스트, 최대 2000 유니코드 코드포인트",
  "sender": "string (optional) - 발신자 번호/이름",
  "metadata": {
    "received_at": "string (optional, ISO 8601) - 문자 수신 시각"
  }
}
```

**Request Example**:
```json
{
  "message": "[Web발신] 고객님 택배가 도착했습니다. 확인: http://bit.ly/3xFake",
  "sender": "010-1234-5678",
  "metadata": {
    "received_at": "2026-04-07T10:30:00Z"
  }
}
```

**Response 200 OK**:
```json
{
  "success": true,
  "data": {
    "id": "string - 분석 결과 ID",
    "degraded": "boolean - 외부 API 장애로 품질 저하 여부",
    "degraded_services": ["string - 장애 서비스 목록 (openai_llm, web_risk)"],
    "degraded_reason": "string (optional) - 품질 저하 사유",
    "risk_level": "string - HIGH | WARNING | NORMAL",
    "risk_score": "number - 0~100 위험도 점수",
    "summary": "string - 1줄 요약",
    "explanation": "string - 상세 판단 근거 (한국어)",
    "urls": [
      {
        "original_url": "string - 원본 URL",
        "resolved_url": "string - 최종 목적지 URL (단축 URL 추적 후)",
        "redirect_chain": ["string - 리다이렉트 경로"],
        "is_shortened": "boolean - 단축 URL 여부",
        "resolve_status": "string - OK | FAILED | TIMEOUT | TOO_MANY_REDIRECTS",
        "category": "string - AD | APP_DOWNLOAD | PHISHING_SUSPECT | MALWARE | NORMAL | UNKNOWN",
        "web_risk_result": {
          "is_safe": "boolean",
          "threat_types": ["string - MALWARE | SOCIAL_ENGINEERING | UNWANTED_SOFTWARE"],
          "source": "string - cache | whitelist | blacklist | web_risk_api"
        },
        "risk_factors": ["string - URL 관련 위험 요인 목록"]
      }
    ],
    "text_analysis": {
      "detected_keywords": ["string - 탐지된 스미싱 키워드"],
      "pattern_categories": ["string - 택배사칭 | 금융사칭 | 정부사칭 | 가족사칭 | 기관사칭 | 부고사칭"],
      "urgency_score": "number - 긴급성/공포 유도 점수 (0~100)"
    },
    "patterns_detected": ["string - 탐지된 스미싱 패턴 요약"],
    "analyzed_at": "string (ISO 8601) - 분석 완료 시각"
  },
  "meta": {
    "model": "string - 사용된 LLM 모델명",
    "processing_time_ms": "number - 총 처리 시간(ms)",
    "url_resolve_time_ms": "number - URL 추적 소요 시간(ms)",
    "web_risk_time_ms": "number - Web Risk API 소요 시간(ms)",
    "llm_time_ms": "number - LLM 분석 소요 시간(ms)",
    "cache_hit": "boolean - URL 캐시 히트 여부",
    "timestamp": "string (ISO 8601)"
  }
}
```

**Response Example**:
```json
{
  "success": true,
  "data": {
    "id": "analysis_a1b2c3d4",
    "degraded": false,
    "degraded_services": [],
    "risk_level": "HIGH",
    "risk_score": 95,
    "summary": "택배 사칭 스미싱 의심 문자입니다.",
    "explanation": "이 문자는 다음과 같은 이유로 고위험으로 판정되었습니다:\n1. 택배 도착 알림을 사칭하는 전형적인 스미싱 패턴입니다.\n2. bit.ly 단축 URL을 사용하여 실제 목적지를 숨기고 있습니다.\n3. 단축 URL 추적 결과 최종 목적지가 'http://fake-delivery.xyz/login'으로 확인되었습니다.\n4. Google Web Risk API에서 해당 URL이 SOCIAL_ENGINEERING(피싱) 위협으로 탐지되었습니다.\n5. 공식 택배사는 bit.ly 같은 단축 URL을 사용하지 않습니다.",
    "urls": [
      {
        "original_url": "http://bit.ly/3xFake",
        "resolved_url": "http://fake-delivery.xyz/login",
        "redirect_chain": [
          "http://bit.ly/3xFake",
          "http://redirect1.com/r",
          "http://fake-delivery.xyz/login"
        ],
        "is_shortened": true,
        "resolve_status": "OK",
        "category": "PHISHING_SUSPECT",
        "web_risk_result": {
          "is_safe": false,
          "threat_types": ["SOCIAL_ENGINEERING"],
          "source": "web_risk_api"
        },
        "risk_factors": [
          "단축 URL 사용으로 목적지 은폐",
          "HTTP(비암호화) 프로토콜",
          "Google Web Risk: SOCIAL_ENGINEERING 탐지",
          "택배사 공식 도메인 아님"
        ]
      }
    ],
    "text_analysis": {
      "detected_keywords": ["택배", "도착", "확인"],
      "pattern_categories": ["택배사칭"],
      "urgency_score": 65
    },
    "patterns_detected": [
      "택배 사칭",
      "단축 URL 사용",
      "Google Web Risk 위협 탐지"
    ],
    "analyzed_at": "2026-04-07T10:30:05Z"
  },
  "meta": {
    "model": "gpt-5.4-mini",
    "processing_time_ms": 3200,
    "url_resolve_time_ms": 850,
    "web_risk_time_ms": 420,
    "llm_time_ms": 1800,
    "cache_hit": false,
    "timestamp": "2026-04-07T10:30:05Z"
  }
}
```

**Error Responses**:
| Status | Code | Message | Description |
|--------|------|---------|-------------|
| 400 | INVALID_INPUT | Message is required | 메시지 누락 |
| 400 | MESSAGE_TOO_LONG | Message exceeds 2000 unicode codepoints | 메시지 길이 초과 |
| 401 | UNAUTHORIZED | Invalid API key | API 키 유효하지 않음 |
| 429 | RATE_LIMITED | Too many requests | IP당 60회/분 초과 |
| 500 | INTERNAL_ERROR | Internal server error | 서버 내부 오류 |
| 502 | LLM_ERROR | LLM API call failed | OpenAI API 호출 실패 |
| 502 | WEB_RISK_ERROR | Web Risk API call failed | Google Web Risk API 실패 |
| 504 | LLM_TIMEOUT | LLM API timeout | OpenAI API 타임아웃 |

**Error Response Format**:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "Message is required",
    "details": []
  },
  "meta": {
    "timestamp": "2026-04-07T10:30:00Z"
  }
}
```

**Rate Limiting**:
- Limit: 60 requests per minute per IP
- Headers: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset

---

#### `GET /api/v1/history`

**Description**: 분석 이력 조회 (페이지네이션)

**Authentication**: API Key (X-API-Key 헤더)

**Query Parameters**:
| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| page | No | int | 페이지 번호 (default: 1) |
| size | No | int | 페이지 크기 (default: 20, max: 100) |
| risk_level | No | string | 필터: HIGH, WARNING, NORMAL |
| start_date | No | string | 시작일 (ISO 8601) |
| end_date | No | string | 종료일 (ISO 8601) |

**Response 200 OK Example**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "analysis_a1b2c3d4",
        "message_preview": "[Web발신] 고객님 택배가...",
        "risk_level": "HIGH",
        "risk_score": 95,
        "summary": "택배 사칭 스미싱 의심 문자입니다.",
        "urls_count": 1,
        "analyzed_at": "2026-04-07T10:30:05Z"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total_items": 150,
      "total_pages": 8
    }
  },
  "meta": {
    "timestamp": "2026-04-07T10:35:00Z"
  }
}
```

---

#### `GET /api/v1/history/{id}`

**Description**: 특정 분석 결과 상세 조회

**Authentication**: API Key (X-API-Key 헤더)

**Response**: `POST /api/v1/analyze` 응답과 동일한 형식

**Error**: 404 NOT_FOUND - Analysis result not found

---

#### `GET /api/v1/health`

**Description**: 서버 및 외부 의존성 상태 확인

**Authentication**: None

**Response 200 OK**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "dependencies": {
    "database": "connected",
    "openai_api": "reachable",
    "web_risk_api": "reachable"
  },
  "cache_stats": {
    "url_cache_size": 1250,
    "cache_hit_rate": 0.34
  },
  "uptime_seconds": 86400,
  "timestamp": "2026-04-07T10:30:00Z"
}
```

### 5.5 Database Schema

```sql
-- PostgreSQL Schema

-- 분석 이력 테이블
CREATE TABLE analysis_history (
    id TEXT PRIMARY KEY,                   -- UUID
    message TEXT NOT NULL,
    sender TEXT,
    risk_level TEXT NOT NULL,              -- HIGH, WARNING, NORMAL
    risk_score INTEGER NOT NULL,           -- 0~100
    summary TEXT NOT NULL,
    explanation TEXT NOT NULL,
    urls JSONB,                            -- URL 분석 결과
    text_analysis JSONB,                   -- 본문 분석 결과
    patterns JSONB,                        -- 탐지 패턴
    degraded BOOLEAN DEFAULT FALSE,        -- 외부 API 장애 여부
    model_used TEXT NOT NULL,
    processing_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

-- URL 검사 결과 캐시 테이블 (Redis 보조, DB는 영속 백업용)
CREATE TABLE url_cache (
    url_hash TEXT PRIMARY KEY,             -- URL의 SHA-256 해시
    url TEXT NOT NULL,
    is_safe BOOLEAN NOT NULL,
    threat_types JSONB,                    -- 위협 유형
    source TEXT NOT NULL,                  -- web_risk_api, whitelist, blacklist
    checked_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL        -- 차등 TTL: 위협=1h, 안전=24h
);

-- 알려진 스미싱 패턴 테이블
CREATE TABLE known_patterns (
    id SERIAL PRIMARY KEY,
    pattern_type TEXT NOT NULL,            -- KEYWORD, DOMAIN, URL_PATTERN, SENDER
    pattern_value TEXT NOT NULL,
    risk_level TEXT NOT NULL,              -- HIGH, WARNING
    category TEXT,                         -- 택배사칭, 금융사칭, 정부사칭 등
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 안전 도메인 화이트리스트
CREATE TABLE safe_domains (
    id SERIAL PRIMARY KEY,
    domain TEXT NOT NULL UNIQUE,           -- naver.com, google.com 등
    category TEXT,                         -- portal, government, finance 등
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_analysis_risk_level ON analysis_history(risk_level);
CREATE INDEX idx_analysis_created_at ON analysis_history(created_at);
CREATE INDEX idx_analysis_urls ON analysis_history USING GIN(urls);
CREATE INDEX idx_url_cache_expires ON url_cache(expires_at);
CREATE INDEX idx_patterns_type ON known_patterns(pattern_type);
CREATE INDEX idx_patterns_active ON known_patterns(is_active);
CREATE INDEX idx_safe_domains_domain ON safe_domains(domain);
```

### 5.6 LLM Prompt Design

**System Prompt**:
```
당신은 스미싱(SMS 피싱) 탐지 전문 AI입니다.
사용자가 제공한 문자메시지와 사전 분석 결과를 종합하여 스미싱 여부를 최종 판단합니다.

[사전 분석 결과로 제공되는 정보]
- URL 추출 및 단축 URL 추적 결과 (원본 URL → 최종 목적지)
- Google Web Risk API 안전성 검사 결과
- 본문 키워드 패턴 분석 결과

[판단 기준]
1. Google Web Risk API 위협 탐지 여부 (MALWARE, SOCIAL_ENGINEERING, UNWANTED_SOFTWARE)
2. URL의 안전성 (단축 URL, 비공식 도메인, HTTP, 의심 TLD)
3. 메시지 내 긴급성/공포 유도 표현
4. 개인정보/금융정보 요구 여부
5. 알려진 스미싱 패턴 (택배, 정부기관, 금융기관, 가족 사칭 등)
6. 앱 설치(.apk) 유도 여부
7. 발신자 정보의 신뢰성

[위험도 기준]
- HIGH (고위험): Web Risk 위협 탐지, 개인정보 탈취, 악성앱 설치 유도, 금융 사기
- WARNING (위험): 의심 요소가 있으나 확정적이지 않음, Web Risk 안전하나 패턴 의심
- NORMAL (보통): 일반 광고, 정상 알림, Web Risk 안전, 의심 패턴 없음

반드시 아래 JSON 형식으로 응답하세요:
{
  "risk_level": "HIGH | WARNING | NORMAL",
  "risk_score": 0-100,
  "summary": "1줄 요약 (한국어)",
  "explanation": "상세 판단 근거 (한국어, 번호 목록 형식)"
}
```

### 5.7 환경변수 설정 (.env)

```
# OpenAI
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-5.4-mini

# Google Web Risk API
GOOGLE_WEB_RISK_API_KEY=...

# Server
# API Key는 DB에서 관리 (Section 4.5.1 참조)
# 아래는 초기 부트스트랩용 시드 키 (첫 실행 시 DB에 등록됨)
INITIAL_API_KEY=your-bootstrap-api-key
HOST=0.0.0.0
PORT=8000

# Cache (안전 판정 URL의 TTL. 위협 판정은 자동으로 1시간 적용)
URL_CACHE_TTL_HOURS=24

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

## 6. Implementation Phases

### Phase 1: MVP - 핵심 분석 파이프라인 + 인프라
- [ ] 프로젝트 구조 생성 (FastAPI 기반)
- [ ] 환경 설정 (.env.example, config.py, requirements.txt)
- [ ] PostgreSQL + Redis 설정 (docker-compose로 로컬 개발환경)
- [ ] DB 마이그레이션 (SQLAlchemy + Alembic)
- [ ] URL Extractor 모듈 (정규표현식, 최대 10개 제한)
- [ ] URL Resolver 모듈 (단축 URL → 원본 추적, httpx HEAD, asyncio.gather 병렬 처리)
- [ ] Google Web Risk API 연동 모듈 (URL 안전성 검사)
- [ ] Link Classifier 모듈 (광고/앱다운로드/피싱의심 분류)
- [ ] Text Analyzer 모듈 (본문 키워드 패턴 매칭)
- [ ] LLM Analyzer 모듈 (OpenAI gpt-5.4-mini, Structured Outputs, 재시도 로직)
- [ ] Graceful Degradation + 규칙 기반 Fallback 판정 로직
- [ ] Result Aggregator (종합 결과 생성, degraded 필드 포함)
- [ ] `POST /api/v1/analyze` 엔드포인트
- [ ] `GET /api/v1/health` 엔드포인트
- [ ] 기본 IP 기반 Rate Limiting (slowapi, 60회/분 - 외부 API 비용 보호)

**Deliverable**: 문자메시지 입력 → URL 추적 → Web Risk 검사 → LLM 분석 → 결과 반환 (장애 시 fallback + Rate Limit 보호)

### Phase 2: 데이터 & 캐싱 & 인증
- [ ] 분석 이력 저장 로직
- [ ] Redis URL 검사 결과 캐싱 (차등 TTL: 위협 1h, 안전 24h)
- [ ] Circuit Breaker 구현 (Web Risk, OpenAI)
- [ ] API Key 인증 미들웨어 (해싱 저장, 다중 키 지원)
- [ ] 안전 도메인 화이트리스트 시딩
- [ ] 스미싱 패턴 DB 시딩 (키워드, 블랙리스트)
- [ ] `GET /api/v1/history` 엔드포인트
- [ ] `GET /api/v1/history/{id}` 엔드포인트
- [ ] 화이트리스트/블랙리스트 관리 CLI 도구

**Deliverable**: 이력 저장/조회 + 캐싱(비용 절감) + API 인증

### Phase 3: 안정성 & 테스트
- [ ] Rate Limiting 확장 (API Key별 제한 적용, Phase 1의 IP 기반에서 업그레이드)
- [ ] 입력값 검증 강화 (Pydantic, 2000 코드포인트 제한)
- [ ] 에러 핸들링 고도화
- [ ] 로깅 민감정보 마스킹
- [ ] 단위 테스트 작성
- [ ] 통합 테스트 작성 (스미싱/정상 문자 테스트셋)

**Deliverable**: 프로덕션 레디 API

### Phase 4: 운영 & 배포
- [ ] 구조화된 로깅 (structlog)
- [ ] Docker 컨테이너화 (docker-compose: API + PostgreSQL + Redis)
- [ ] Swagger/OpenAPI 문서 자동 생성
- [ ] 모니터링 + 알림 설정 (Prometheus/Grafana + Slack/Discord Webhook)
- [ ] 데이터 아카이브 배치 스크립트 (6개월 경과 데이터 비식별화)

**Deliverable**: 배포 가능한 컨테이너 + 모니터링 + 알림

## 7. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| 스미싱 탐지 정확도 | > 90% | 테스트 데이터셋 기반 평가 |
| 오탐률 (False Positive) | < 10% | 정상 문자를 스미싱으로 판정하는 비율 |
| 미탐률 (False Negative) | < 5% | 스미싱을 정상으로 판정하는 비율 |
| API 응답 시간 (p95) | < 5,000ms | 서버 메트릭 |
| API 응답 시간 (캐시 히트, p95) | < 3,000ms | 서버 메트릭 |
| URL 캐시 히트율 | > 30% | 캐시 통계 |
| Google Web Risk API 월 호출 | < 100,000건 | API 사용량 모니터링 |
| API 가용성 | > 99.9% | 업타임 모니터링 |
