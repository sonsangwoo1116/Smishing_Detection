# Task Plan: smishing-detection-agent

> **Generated from**: docs/prd/PRD_smishing-detection-agent.md
> **Created**: 2026-04-07
> **Status**: pending

## Execution Config

| Option | Value | Description |
|--------|-------|-------------|
| `auto_commit` | true | 완료 시 자동 커밋 |
| `commit_per_phase` | true | Phase별 중간 커밋 |
| `quality_gate` | true | /auto-commit 품질 검사 |

## Phases

### Phase 1: MVP - 핵심 분석 파이프라인 + 인프라
- [x] 프로젝트 구조 생성 (FastAPI 기반)
- [x] 환경 설정 (.env.example, config.py, requirements.txt)
- [x] PostgreSQL + Redis 설정 (docker-compose로 로컬 개발환경)
- [x] DB 마이그레이션 (SQLAlchemy + Alembic)
- [x] URL Extractor 모듈 (정규표현식, 최대 10개 제한)
- [x] URL Resolver 모듈 (단축 URL → 원본 추적, httpx HEAD, asyncio.gather 병렬)
- [x] Google Web Risk API 연동 모듈 (URL 안전성 검사)
- [x] Link Classifier 모듈 (광고/앱다운로드/피싱의심 분류)
- [x] Text Analyzer 모듈 (본문 키워드 패턴 매칭)
- [x] LLM Analyzer 모듈 (OpenAI gpt-5.4-mini, Structured Outputs, 재시도)
- [x] Graceful Degradation + 규칙 기반 Fallback 판정 로직
- [x] Result Aggregator (종합 결과, degraded 필드 포함)
- [x] POST /api/v1/analyze 엔드포인트
- [x] GET /api/v1/health 엔드포인트
- [x] 기본 IP 기반 Rate Limiting (slowapi, 60회/분)

### Phase 2: 데이터 & 캐싱 & 인증
- [x] 분석 이력 저장 로직
- [x] Redis URL 검사 결과 캐싱 (차등 TTL: 위협 1h, 안전 24h)
- [x] Circuit Breaker 구현 (Web Risk, OpenAI)
- [x] API Key 인증 미들웨어 (해싱 저장, 다중 키 지원)
- [x] 안전 도메인 화이트리스트 시딩 데이터
- [x] 스미싱 패턴 DB 시딩 데이터
- [x] GET /api/v1/history 엔드포인트
- [x] GET /api/v1/history/{id} 엔드포인트
- [x] 화이트리스트/블랙리스트 관리 CLI 도구

### Phase 3: 안정성 & 테스트
- [x] Rate Limiting 적용 (slowapi, API Key별)
- [x] 입력값 검증 강화 (Pydantic, 2000 코드포인트 제한)
- [x] 에러 핸들링 고도화
- [x] 로깅 민감정보 마스킹
- [x] 단위 테스트 작성
- [x] 통합 테스트 작성

### Phase 4: 운영 & 배포
- [x] 구조화된 로깅 (structlog)
- [x] Docker 컨테이너화 (docker-compose: API + PostgreSQL + Redis)
- [x] Swagger/OpenAPI 문서 자동 생성
- [x] 모니터링 + 알림 설정 (Prometheus/Grafana + Slack Webhook)
- [x] 데이터 아카이브 배치 스크립트

## Progress

| Metric | Value |
|--------|-------|
| Total Tasks | 35/35 |
| Current Phase | - |
| Status | completed |

## Execution Log

| Timestamp | Phase | Task | Status |
|-----------|-------|------|--------|
| - | - | - | - |
