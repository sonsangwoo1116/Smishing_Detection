from datetime import datetime
from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="분석할 문자메시지 텍스트")
    sender: str | None = Field(None, description="발신자 번호/이름")
    metadata: dict | None = Field(None, description="추가 메타데이터")


class UrlResult(BaseModel):
    original_url: str
    resolved_url: str | None = None
    redirect_chain: list[str] = []
    is_shortened: bool = False
    resolve_status: str = "OK"
    category: str = "UNKNOWN"
    web_risk_result: dict | None = None
    risk_factors: list[str] = []


class TextAnalysisResult(BaseModel):
    detected_keywords: list[str] = []
    pattern_categories: list[str] = []
    urgency_score: int = 0


class AnalysisData(BaseModel):
    id: str
    degraded: bool = False
    degraded_services: list[str] = []
    degraded_reason: str | None = None
    risk_level: str
    risk_score: int
    summary: str
    explanation: str
    urls: list[UrlResult] = []
    text_analysis: TextAnalysisResult | None = None
    patterns_detected: list[str] = []
    analyzed_at: datetime


class AnalysisMeta(BaseModel):
    model: str
    processing_time_ms: int
    url_resolve_time_ms: int = 0
    web_risk_time_ms: int = 0
    llm_time_ms: int = 0
    cache_hit: bool = False
    timestamp: datetime


class AnalyzeResponse(BaseModel):
    success: bool = True
    data: AnalysisData
    meta: AnalysisMeta


class HistoryItem(BaseModel):
    id: str
    message_preview: str
    risk_level: str
    risk_score: int
    summary: str
    urls_count: int = 0
    analyzed_at: datetime


class Pagination(BaseModel):
    page: int
    size: int
    total_items: int
    total_pages: int


class HistoryResponse(BaseModel):
    success: bool = True
    data: dict


class ErrorDetail(BaseModel):
    field: str | None = None
    message: str


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] = []


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorBody
    meta: dict


class HealthResponse(BaseModel):
    status: str
    version: str
    dependencies: dict
    cache_stats: dict | None = None
    uptime_seconds: float
    timestamp: datetime
