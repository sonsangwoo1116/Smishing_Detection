# Smishing Detection Frontend PRD

> **Version**: 1.1
> **Created**: 2026-04-07
> **Status**: Draft

## 1. Overview

### 1.1 Problem Statement
스미싱 탐지 AI Agent 백엔드 API가 구축되었으나, curl/Swagger로만 접근 가능하다. 일반 사용자와 보안 관리자가 직관적으로 문자를 분석하고 이력을 관리할 수 있는 웹 UI가 필요하다.

### 1.2 Goals
- 문자메시지를 입력하면 스미싱 분석 결과를 시각적으로 표시하는 웹 UI 제공
- 위험도(HIGH/WARNING/NORMAL)를 색상과 게이지로 직관적 표현
- URL 추적 결과, 키워드 분석, LLM 판단 근거를 구조적으로 표시
- 분석 이력 조회/필터링/페이지네이션
- 서버 상태 대시보드 (헬스체크, 의존성 상태)
- 다크 테마, 사이버 보안 미학의 전문적 디자인

### 1.3 Non-Goals (Out of Scope)
- 사용자 로그인/회원가입 UI (API Key로 인증)
- 화이트리스트/블랙리스트 관리 UI (CLI 도구 사용)
- 모바일 네이티브 앱
- SSR (서버 사이드 렌더링)
- 다국어 지원 (한국어 전용)

### 1.4 Scope
| 포함 | 제외 |
|------|------|
| React SPA (Vite + Tailwind CSS) | Next.js SSR |
| 분석, 이력, 상태 3개 탭 | 관리자 CRUD UI |
| API Key 설정 UI | 로그인/회원 시스템 |
| 반응형 (모바일 지원) | 네이티브 앱 |
| 다크 테마 | 라이트 테마 토글 |
| Vite proxy (CORS 우회) | 별도 nginx 설정 |

## 2. User Stories

### 2.1 Primary Users
1. **일반 사용자**: 의심 문자를 받고 스미싱 여부를 확인하고 싶은 사람
2. **보안 관리자**: 다수의 문자를 분석하고 이력을 모니터링하는 담당자

### 2.2 Acceptance Criteria (Gherkin)

**Scenario: 스미싱 문자 분석**
```
Given 사용자가 분석 탭에 있음
When "[Web발신] 택배 도착 확인: http://bit.ly/3xFake" 메시지를 입력하고 "분석하기" 버튼 클릭
Then 로딩 스피너가 표시됨
And 3~5초 후 결과 카드가 표시됨
And 위험도 배지가 색상 코딩으로 표시됨 (HIGH=빨강, WARNING=노랑, NORMAL=초록)
And 위험도 점수가 원형 게이지로 표시됨
And URL 분석 결과 (원본→최종, Web Risk, 위험 요인)가 표시됨
And 탐지 키워드가 태그/배지로 표시됨
And LLM 판단 근거가 접을 수 있는 섹션으로 표시됨
```

**Scenario: degraded 응답 표시**
```
Given LLM API 장애로 degraded=true인 응답이 반환됨
When 결과가 표시됨
Then 노란색 경고 배너가 상단에 표시됨: "일부 분석 서비스가 제한된 상태입니다 (규칙 기반 fallback 적용)"
```

**Scenario: 분석 이력 조회**
```
Given 사용자가 이력 탭으로 이동
When 페이지가 로드됨
Then 최근 분석 이력이 테이블/카드 형태로 표시됨
And 위험도 필터(전체/HIGH/WARNING/NORMAL) 제공
And 페이지네이션으로 이전/다음 페이지 이동 가능
And 항목 클릭 시 상세 결과가 확장/모달로 표시됨
```

**Scenario: API Key 설정**
```
Given 사용자가 처음 접속함
When API Key가 설정되지 않았음
Then API Key 입력 모달/섹션이 표시됨
And 키 입력 후 sessionStorage에 저장됨
And 이후 모든 API 호출에 X-API-Key 헤더로 전송됨
```

**Scenario: 서버 상태 확인**
```
Given 사용자가 상태 탭으로 이동
When 헬스체크 API가 호출됨
Then 서버 상태(healthy/degraded)가 표시됨
And 각 의존성(DB, Redis, OpenAI, Web Risk)의 상태가 아이콘으로 표시됨
And 업타임, 캐시 통계가 표시됨
```

## 3. Functional Requirements

| ID | Requirement | Priority | Dependencies |
|----|------------|----------|--------------|
| FR-001 | 탭 네비게이션 (분석/이력/상태) | P0 (Must) | - |
| FR-002 | 문자 메시지 입력 Textarea (placeholder, 글자수 카운터) | P0 (Must) | FR-001 |
| FR-003 | 발신자 번호 입력 필드 (선택) | P1 (Should) | FR-002 |
| FR-004 | "분석하기" 버튼 + 로딩 스피너 | P0 (Must) | FR-002 |
| FR-005 | 위험도 배지 (HIGH=빨강, WARNING=노랑, NORMAL=초록) | P0 (Must) | FR-004 |
| FR-006 | 위험도 점수 원형 게이지/프로그레스 (0~100) | P0 (Must) | FR-004 |
| FR-007 | 분석 요약(summary) 텍스트 표시 | P0 (Must) | FR-004 |
| FR-008 | 상세 설명(explanation) 접을 수 있는 섹션 | P0 (Must) | FR-004 |
| FR-009 | URL 분석 결과 카드 (원본→최종, 리다이렉트 체인, Web Risk, 카테고리, 위험 요인) | P0 (Must) | FR-004 |
| FR-010 | 탐지 키워드 태그/배지 표시 | P0 (Must) | FR-004 |
| FR-011 | 패턴 카테고리 태그 표시 (택배사칭, 금융사칭 등) | P0 (Must) | FR-004 |
| FR-012 | 긴급성 점수 바 표시 | P1 (Should) | FR-004 |
| FR-013 | degraded 경고 배너 (LLM/Web Risk 장애 시) | P0 (Must) | FR-004 |
| FR-014 | 메타 정보 표시 (처리시간, 모델명, 캐시 히트) | P1 (Should) | FR-004 |
| FR-015 | 분석 이력 테이블/리스트 (이력 탭) | P0 (Must) | FR-001 |
| FR-016 | 위험도 필터 (전체/HIGH/WARNING/NORMAL) | P0 (Must) | FR-015 |
| FR-017 | 페이지네이션 (이전/다음, 페이지 번호) | P0 (Must) | FR-015 |
| FR-018 | 이력 항목 클릭 → 상세 보기 (확장 또는 모달) | P1 (Should) | FR-015 |
| FR-019 | 서버 헬스체크 상태 표시 (상태 탭) | P0 (Must) | FR-001 |
| FR-020 | 의존성 상태 아이콘 (DB, Redis, OpenAI, Web Risk) | P0 (Must) | FR-019 |
| FR-021 | 업타임, 캐시 통계 표시 | P1 (Should) | FR-019 |
| FR-022 | API Key 설정 UI (입력 → sessionStorage 저장) | P0 (Must) | - |
| FR-023 | API Key 미설정 시 안내 모달 | P0 (Must) | FR-022 |
| FR-024 | 에러 상태 표시 (네트워크 오류, 401, 429 등) | P0 (Must) | - |
| FR-025 | 반응형 레이아웃 (모바일 768px 이하) | P1 (Should) | - |
| FR-026 | 예시 문자 버튼 (클릭 시 샘플 문자 자동 입력) | P2 (Could) | FR-002 |
| FR-027 | **중복 요청 방지** (분석 중 버튼 비활성화, AbortController로 이탈 시 취소) | P0 (Must) | FR-004 |
| FR-028 | **이력 날짜 범위 필터** (start_date, end_date) | P1 (Should) | FR-016 |
| FR-029 | **이력 상세 보기 시 getHistoryDetail(id) API 호출** + 로딩 상태 표시 | P0 (Must) | FR-018 |

> **인증 범위 참고**: `POST /api/v1/analyze`만 API Key 필수. `GET /history`, `GET /health`는 현재 백엔드에서 인증 없이 접근 가능 (공개 엔드포인트).

> **API 응답 참고** (모든 응답은 `{success, data, meta}` 표준 envelope로 감싸짐):
> - Analyze: `{success, data: {id, degraded, risk_level, risk_score, summary, explanation, urls[], text_analysis, patterns_detected[], ...}, meta: {model, processing_time_ms, ...}}`
> - History list: `{success, data: {items: [{id, message_preview, risk_level, risk_score, summary, urls_count, analyzed_at}], pagination: {page, size, total_items, total_pages}}, meta: {...}}`
> - History detail: `{success, data: {id, risk_level, risk_score, summary, explanation, urls[], text_analysis, patterns_detected[], ...}, meta: {model, processing_time_ms, ...}}`
> - Health: `{status, version, dependencies: {database: "connected"|"disconnected", redis: "connected"|"disconnected", openai_api: "configured"|"not_configured", web_risk_api: "configured"|"not_configured"}, cache_stats: {url_cache_size}, uptime_seconds}`

## 4. Non-Functional Requirements

### 4.0 Scale Grade

**선택된 등급: Growth** (백엔드와 동일)

프론트엔드는 정적 SPA이므로 CDN 배포 시 Scale Grade에 관계없이 대응 가능.

### 4.1 Performance

| 지표 | 목표값 |
|------|--------|
| 초기 로딩 (FCP) | < 1.5초 |
| 번들 크기 (gzip) | < 300KB |
| 분석 결과 렌더링 | API 응답 후 < 100ms |

### 4.2 브라우저 지원

| 브라우저 | 최소 버전 |
|---------|----------|
| Chrome | 90+ |
| Firefox | 90+ |
| Safari | 14+ |
| Edge | 90+ |
| Mobile Chrome/Safari | 최신 2버전 |

### 4.3 접근성

- 키보드 네비게이션 지원
- 색상 외 아이콘/텍스트로도 위험도 구분 가능
- 적절한 contrast ratio (WCAG AA)

### 4.4 Security (XSS 대책 + API Key 보호)

**C-1 해결: XSS 방어 정책**

| 규칙 | 설명 |
|------|------|
| `dangerouslySetInnerHTML` 사용 금지 | 백엔드 응답은 반드시 텍스트로만 렌더링 |
| CSP 메타 태그 설정 | `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'` |
| 백엔드 응답 데이터 HTML 이스케이프 | JSX의 기본 이스케이프에 의존 (React 기본 동작) |
| 외부 스크립트 로드 금지 | CDN 의존성 없음 (모두 번들링) |

**API Key 저장 정책**:
- `sessionStorage` 사용 (탭 닫으면 삭제, localStorage보다 안전)
- 키 입력 시 마스킹 표시 (`type="password"`)
- 설정 모달에서만 키 확인/변경 가능

### 4.5 프로덕션 배포 전략

**방식: FastAPI static files 서빙 (동일 오리진)**

```
Production:
  FastAPI (port 8001)
    ├── /api/v1/*          → API 엔드포인트
    └── /*                 → frontend/dist/ 정적 파일 서빙

→ 동일 오리진이므로 CORS 불필요
→ Vite build → dist/ → FastAPI StaticFiles mount
```

```python
# src/main.py에 추가 (프로덕션)
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
```

**개발 환경**: Vite dev server (port 3000) + proxy → localhost:8001

## 5. Technical Design

### 5.1 기술 스택

| 구분 | 기술 |
|------|------|
| Framework | React 18+ |
| Build Tool | Vite 5+ |
| CSS | Tailwind CSS 3+ |
| HTTP Client | fetch API (네이티브) |
| 상태 관리 | React hooks (useState, useEffect) |
| 라우팅 | 탭 전환 (SPA 단일 페이지, react-router 불필요) |
| 차트/게이지 | CSS 기반 원형 프로그레스 (라이브러리 없음) |
| 저장 | sessionStorage (API Key) |
| 개발 포트 | 3000 |
| 프록시 | Vite proxy → http://localhost:8001 |

### 5.2 프로젝트 구조

```
frontend/
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── .env.example                    # VITE_API_URL=http://localhost:8001
├── src/
│   ├── main.jsx                    # 엔트리포인트
│   ├── App.jsx                     # 메인 앱 (탭 네비게이션)
│   ├── api/
│   │   └── client.js               # fetch 래퍼 (API Key 자동 첨부)
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.jsx          # 헤더 (로고, API Key 설정 버튼)
│   │   │   ├── TabNav.jsx          # 탭 네비게이션
│   │   │   └── Footer.jsx          # 푸터
│   │   ├── analyze/
│   │   │   ├── AnalyzeTab.jsx      # 분석 탭 메인
│   │   │   ├── MessageInput.jsx    # 메시지 입력 영역
│   │   │   ├── ResultCard.jsx      # 분석 결과 카드
│   │   │   ├── RiskBadge.jsx       # 위험도 배지
│   │   │   ├── RiskGauge.jsx       # 원형 게이지
│   │   │   ├── UrlAnalysis.jsx     # URL 분석 결과
│   │   │   ├── KeywordTags.jsx     # 키워드 태그
│   │   │   ├── ExplanationSection.jsx  # 접기/펼치기 설명
│   │   │   ├── DegradedBanner.jsx  # degraded 경고
│   │   │   └── MetaInfo.jsx        # 메타 정보
│   │   ├── history/
│   │   │   ├── HistoryTab.jsx      # 이력 탭 메인
│   │   │   ├── HistoryTable.jsx    # 이력 테이블
│   │   │   ├── HistoryFilter.jsx   # 위험도 필터
│   │   │   ├── HistoryDetail.jsx   # 상세 보기 모달
│   │   │   └── Pagination.jsx      # 페이지네이션
│   │   ├── status/
│   │   │   ├── StatusTab.jsx       # 상태 탭 메인
│   │   │   └── DependencyCard.jsx  # 의존성 상태 카드
│   │   ├── settings/
│   │   │   └── ApiKeyModal.jsx     # API Key 설정 모달
│   │   └── common/
│   │       ├── Loading.jsx         # 로딩 스피너
│   │       ├── ErrorAlert.jsx      # 에러 표시
│   │       └── SampleMessages.jsx  # 예시 문자 버튼
│   └── styles/
│       └── index.css               # Tailwind 디렉티브 + 커스텀 CSS
```

### 5.3 API 통신 설계

**API Client (client.js)**:
```javascript
const API_URL = import.meta.env.VITE_API_URL || '';

function getApiKey() {
  return sessionStorage.getItem('smishing_api_key') || '';
}

async function apiCall(endpoint, options = {}) {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': getApiKey(),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw { status: response.status, ...error };
  }

  return response.json();
}
```

**API 호출 목록**:
| 함수 | HTTP | 엔드포인트 | 용도 |
|------|------|-----------|------|
| `analyzeMessage(message, sender?)` | POST | /api/v1/analyze | 스미싱 분석 |
| `getHistory(page, size, risk_level?)` | GET | /api/v1/history | 이력 조회 |
| `getHistoryDetail(id)` | GET | /api/v1/history/{id} | 상세 조회 |
| `getHealth()` | GET | /api/v1/health | 서버 상태 |

### 5.4 디자인 시스템

**색상 팔레트 (다크 테마)**:
| 용도 | 색상 | Tailwind |
|------|------|---------|
| 배경 (기본) | #0a0e17 | bg-[#0a0e17] |
| 배경 (카드) | #111827 | bg-gray-900 |
| 배경 (카드 내부) | #1f2937 | bg-gray-800 |
| 텍스트 (기본) | #e5e7eb | text-gray-200 |
| 텍스트 (부제목) | #9ca3af | text-gray-400 |
| 액센트 (주요) | #06b6d4 | text-cyan-400 |
| HIGH 위험 | #ef4444 | text-red-500, bg-red-500/10 |
| WARNING 위험 | #f59e0b | text-amber-500, bg-amber-500/10 |
| NORMAL 안전 | #22c55e | text-green-500, bg-green-500/10 |
| 보더 | #374151 | border-gray-700 |

**위험도 배지 디자인**:
```
HIGH:    [████ 고위험] 빨간 배경, 아이콘: 방패 경고
WARNING: [███░ 위험]  노란 배경, 아이콘: 주의 삼각형
NORMAL:  [██░░ 보통]  초록 배경, 아이콘: 체크 방패
```

**원형 게이지 디자인**:
- SVG 기반 원형 프로그레스
- 0~40: 초록, 41~70: 노랑, 71~100: 빨강
- 중앙에 점수 숫자 + "점" 텍스트
- 애니메이션: 0에서 최종 값까지 1초 ease-out

### 5.5 Vite 설정

```javascript
// vite.config.js
export default {
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
    },
  },
}
```

### 5.6 에러 처리

| HTTP Status | UI 동작 |
|-------------|---------|
| 200 | 결과 표시 |
| 400 | "메시지를 입력해주세요" 또는 "메시지가 너무 깁니다" |
| 401 | "API Key가 유효하지 않습니다" + API Key 재설정 유도 |
| 429 | "요청이 너무 많습니다. 잠시 후 다시 시도해주세요" |
| 404 | "해당 분석 결과를 찾을 수 없습니다" |
| 500 | "서버 오류가 발생했습니다" |
| 네트워크 오류 | "서버에 연결할 수 없습니다" |

## 6. Implementation Phases

### Phase 1: MVP - 분석 탭 구현
- [ ] Vite + React + Tailwind 프로젝트 생성
- [ ] API Client (fetch 래퍼 + API Key 관리)
- [ ] 레이아웃 (Header, TabNav, Footer)
- [ ] API Key 설정 모달
- [ ] 메시지 입력 컴포넌트
- [ ] 분석 결과 카드 (위험도 배지, 게이지, 요약, 설명)
- [ ] URL 분석 결과 표시
- [ ] 키워드/패턴 태그
- [ ] degraded 경고 배너
- [ ] 로딩/에러 상태

**Deliverable**: 문자 입력 → 분석 결과 시각화

### Phase 2: 이력 + 상태 탭
- [ ] 이력 탭 (테이블, 필터, 페이지네이션)
- [ ] 이력 상세 보기
- [ ] 상태 탭 (헬스체크, 의존성)
- [ ] 예시 문자 버튼
- [ ] 메타 정보 표시

**Deliverable**: 전체 3탭 완성

### Phase 3: 반응형 + 폴리시
- [ ] 모바일 반응형 레이아웃
- [ ] 애니메이션 (게이지, 탭 전환)
- [ ] 키보드 접근성
- [ ] 빌드 최적화

**Deliverable**: 프로덕션 빌드

## 7. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| 초기 로딩 시간 (FCP) | < 1.5초 | Lighthouse |
| 번들 크기 (gzip) | < 300KB | Vite build |
| Lighthouse 점수 | > 90 | Lighthouse |
| 분석 요청 후 결과 표시 | API 응답 + 100ms 이내 | 수동 측정 |
| 모바일 사용성 | 모든 기능 사용 가능 | 수동 테스트 |
