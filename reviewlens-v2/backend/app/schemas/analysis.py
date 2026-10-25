"""Pydantic response models for the analysis API."""
from __future__ import annotations
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "2.0.0"


class ErrorResponse(BaseModel):
    detail: str


class ColumnMapping(BaseModel):
    review_text: str | None = None
    rating: str | None = None
    date: str | None = None
    brand: str | None = None
    review_id: str | None = None
    title: str | None = None


class AspectSentiment(BaseModel):
    aspect: str
    pos: int = 0
    neu: int = 0
    neg: int = 0
    mentions: int = 0
    net: float = 0.0


class Issue(BaseModel):
    aspect: str
    issue: str
    mentions: int
    reviews: int
    pct_reviews: float
    severity: float
    dated: bool
    rating_drag: float
    recent: int
    prior: int
    trend: float
    priority: int
    quotes: list[str]
    owner: str
    action: str


class EmergingAlert(BaseModel):
    brand: str
    aspect: str
    recent: int
    expected: float
    spike: float


class WeeklyTrend(BaseModel):
    week: str
    aspect: str
    net: float


class RiskSignal(BaseModel):
    category: str
    reviews: int
    pct: float
    color: str
    example: str


class KeyDriver(BaseModel):
    aspect: str
    reviews_negative: int
    share_negative: float
    stars_effect: float
    gain: float


class CoOccurrence(BaseModel):
    a: str
    b: str
    reviews: int
    lift: float


class SignalWord(BaseModel):
    word: str
    complaints: int
    times_more_common: float


class ReviewResult(BaseModel):
    review_id: str
    brand: str
    date: str
    rating: int
    review_text: str
    match: float | None = None
    overall: float | None = None
    flagged: bool | None = None


class AnalysisOverview(BaseModel):
    total_reviews: int
    usable_reviews: int
    flagged_reviews: int
    avg_rating: float
    rating_estimated: bool
    has_dates: bool
    has_brands: bool
    brands: list[str]
    notes: list[str]
    date_range: list[str]  # [min_date, max_date]


class AnalysisResult(BaseModel):
    analysis_id: str
    overview: AnalysisOverview
    aspect_summary: list[AspectSentiment]
    issues: list[Issue]
    emerging_alerts: list[EmergingAlert]
    weekly_trends: list[WeeklyTrend]
    risk_signals: list[RiskSignal]
    key_drivers: list[KeyDriver]
    key_drivers_r2: float
    co_occurrences: list[CoOccurrence]
    signal_words: list[SignalWord]
    executive_summary: list[str]
    discovered_topics: list[str]
