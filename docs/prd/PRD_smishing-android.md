# Smishing Detection Android App PRD

> **Version**: 1.0
> **Created**: 2026-04-07
> **Status**: Draft

## 1. Overview

### 1.1 Problem Statement
스미싱 탐지 백엔드 API와 웹 UI가 구축되었으나, 실제 문자 수신 시 자동으로 분석하려면 수동 복붙이 필요하다. Android 앱에서 SMS 수신을 감지하고 자동/수동으로 백엔드 API를 호출하여 스미싱 여부를 판별하는 네이티브 앱이 필요하다.

### 1.2 Goals
- SMS 수신 시 자동으로 스미싱 분석 API 호출
- 위험도에 따른 알림 표시 (HIGH=즉시 경고, WARNING=주의, NORMAL=무시)
- 분석 이력 목록 표시
- 수동 분석 기능 (문자 복붙)
- 백엔드 서버 URL 및 API Key 설정

### 1.3 Non-Goals
- iOS 지원 (Android 전용)
- SMS 차단/삭제 기능
- 전화 수신 분석
- Play Store 배포 (APK 사이드로딩)

### 1.4 Scope
| 포함 | 제외 |
|------|------|
| SMS 수신 자동 감지 | MMS/이미지 분석 |
| 백엔드 API 연동 | 로컬 온디바이스 분석 |
| Push 알림 (위험도별) | FCM 서버 푸시 |
| 분석 이력 목록 | 상세 URL 분석 표시 |
| 서버 URL/API Key 설정 | 사용자 인증 |

## 2. Functional Requirements

| ID | Requirement | Priority |
|----|------------|----------|
| FR-001 | SMS 수신 BroadcastReceiver (백그라운드 감지) | P0 |
| FR-002 | 수신 SMS → POST /api/v1/analyze API 호출 | P0 |
| FR-003 | 분석 결과 기반 알림 (HIGH=빨강 긴급, WARNING=노랑, NORMAL=표시 안함) | P0 |
| FR-004 | 알림 클릭 → 상세 결과 화면 | P0 |
| FR-005 | 메인 화면: 최근 분석 이력 리스트 | P0 |
| FR-006 | 수동 분석: 문자 입력 → 분석 | P1 |
| FR-007 | 설정 화면: 서버 URL, API Key 입력/저장 | P0 |
| FR-008 | 서버 연결 상태 표시 | P1 |
| FR-009 | 분석 on/off 토글 (자동 분석 비활성화 가능) | P1 |
| FR-010 | 배터리 최적화 (Doze 모드 대응, WorkManager) | P1 |

## 3. Technical Design

### 3.1 기술 스택
| 구분 | 기술 |
|------|------|
| Language | Kotlin |
| Min SDK | 26 (Android 8.0) |
| Target SDK | 34 (Android 14) |
| UI | Jetpack Compose + Material 3 |
| HTTP | Retrofit2 + OkHttp |
| 비동기 | Kotlin Coroutines |
| 로컬 저장 | SharedPreferences (설정), Room (이력 캐시) |
| 백그라운드 | BroadcastReceiver + WorkManager |
| DI | Hilt |
| 빌드 | Gradle (Kotlin DSL) |

### 3.2 Architecture
```
┌─────────────────────────────────────────┐
│           Android App                    │
│                                          │
│  SMS 수신 → BroadcastReceiver            │
│      │                                   │
│      ▼                                   │
│  AnalysisWorker (WorkManager)            │
│      │                                   │
│      ▼                                   │
│  SmishingApiService (Retrofit)           │
│      │   POST /api/v1/analyze            │
│      ▼                                   │
│  NotificationManager                     │
│      │   위험도별 알림 표시               │
│      ▼                                   │
│  Room DB (분석 이력 캐시)                │
│                                          │
│  [UI: Jetpack Compose]                   │
│  ├── 이력 목록 화면                      │
│  ├── 상세 결과 화면                      │
│  ├── 수동 분석 화면                      │
│  └── 설정 화면                           │
└─────────────────────────────────────────┘
          │
          ▼
┌─────────────────────┐
│  Backend API         │
│  (FastAPI :8001)     │
└─────────────────────┘
```

### 3.3 권한
```xml
<uses-permission android:name="android.permission.RECEIVE_SMS" />
<uses-permission android:name="android.permission.READ_SMS" />
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
```

### 3.4 알림 정책
| 위험도 | 알림 채널 | 동작 |
|--------|----------|------|
| HIGH | smishing_high (긴급) | 헤드업 알림, 진동, 빨간 아이콘 |
| WARNING | smishing_warning (주의) | 일반 알림, 노란 아이콘 |
| NORMAL | 알림 없음 | 이력에만 기록 |

## 4. Implementation Phases

### Phase 1: MVP
- [ ] Android 프로젝트 생성 (Kotlin, Compose, Gradle KTS)
- [ ] Retrofit API 서비스 (analyze, health)
- [ ] SMS BroadcastReceiver
- [ ] WorkManager 기반 분석 실행
- [ ] 알림 표시 (위험도별 채널)
- [ ] 설정 화면 (서버 URL, API Key)

### Phase 2: UI + 이력
- [ ] 메인 화면 (분석 이력 리스트)
- [ ] 상세 결과 화면
- [ ] 수동 분석 화면
- [ ] Room DB 이력 저장

### Phase 3: 안정성
- [ ] 배터리 최적화
- [ ] 에러 핸들링 (네트워크 끊김 시 재시도)
- [ ] 분석 on/off 토글
- [ ] 부팅 시 자동 시작
