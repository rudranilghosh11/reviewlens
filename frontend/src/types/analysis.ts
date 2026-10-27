export interface HealthResponse {
  status: string;
  version: string;
}

export interface AspectSentiment {
  aspect: string;
  pos: number;
  neu: number;
  neg: number;
  mentions: number;
  net: number;
}

export interface Issue {
  aspect: string;
  issue: string;
  mentions: number;
  reviews: number;
  pct_reviews: number;
  severity: number;
  dated: boolean;
  rating_drag: number;
  recent: number;
  prior: number;
  trend: number;
  priority: number;
  quotes: string[];
  owner: string;
  action: string;
}

export interface EmergingAlert {
  brand: string;
  aspect: string;
  recent: number;
  expected: number;
  spike: number;
}

export interface WeeklyTrend {
  week: string;
  aspect: string;
  net: number;
}

export interface RiskSignal {
  category: string;
  reviews: number;
  pct: number;
  color: string;
  example: string;
}

export interface KeyDriver {
  aspect: string;
  reviews_negative: number;
  share_negative: number;
  stars_effect: number;
  gain: number;
}

export interface CoOccurrence {
  a: string;
  b: string;
  reviews: number;
  lift: number;
}

export interface SignalWord {
  word: string;
  complaints: number;
  times_more_common: number;
}

export interface ReviewItem {
  review_id: string;
  brand: string;
  date: string;
  rating: number;
  review_text: string;
  match?: number;
  flagged?: boolean;
}

export interface AnalysisOverview {
  total_reviews: number;
  usable_reviews: number;
  flagged_reviews: number;
  avg_rating: number;
  rating_estimated: boolean;
  has_dates: boolean;
  has_brands: boolean;
  brands: string[];
  products: string[];
  notes: string[];
  date_range: string[];
}

export interface AnalysisResult {
  analysis_id: string;
  overview: AnalysisOverview;
  aspect_summary: AspectSentiment[];
  issues: Issue[];
  emerging_alerts: EmergingAlert[];
  weekly_trends: WeeklyTrend[];
  risk_signals: RiskSignal[];
  key_drivers: KeyDriver[];
  key_drivers_r2: number;
  co_occurrences: CoOccurrence[];
  signal_words: SignalWord[];
  executive_summary: string[];
  discovered_topics: string[];
}

export interface HeatmapData {
  brands: string[];
  aspects: string[];
  matrix: Record<string, Record<string, number | null>>;
}
