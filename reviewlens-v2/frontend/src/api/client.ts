import type { AnalysisResult, HealthResponse, HeatmapData, ReviewItem } from '../types/analysis';

const BASE_URL = 'http://localhost:8000/api';

export async function checkHealth(): Promise<HealthResponse> {
  const resp = await fetch(`${BASE_URL}/health`);
  if (!resp.ok) {
    throw new Error(`Health check failed with status ${resp.status}`);
  }
  return await resp.json();
}

export async function uploadAndAnalyse(file: File): Promise<AnalysisResult> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${BASE_URL}/analyse`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let errMessage = `Server error (${response.status})`;
    try {
      const data = await response.json();
      if (data.detail) {
        errMessage = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
      }
    } catch (_) {
      const text = await response.text();
      if (text) errMessage = text;
    }
    throw new Error(errMessage);
  }

  return await response.json();
}

export async function searchReviews(
  analysisId: string,
  query: string,
  k = 15
): Promise<ReviewItem[]> {
  const params = new URLSearchParams({ q: query, k: k.toString() });
  const response = await fetch(`${BASE_URL}/search/${analysisId}?${params.toString()}`);
  if (!response.ok) {
    throw new Error(`Search failed: ${response.statusText}`);
  }
  return await response.json();
}

export async function getReviews(
  analysisId: string,
  page = 1,
  perPage = 25,
  brand?: string,
  sentiment?: string
): Promise<{ items: ReviewItem[]; total: number; page: number; pages: number }> {
  const params = new URLSearchParams({
    page: page.toString(),
    per_page: perPage.toString(),
  });
  if (brand && brand !== 'ALL') params.append('brand', brand);
  if (sentiment && sentiment !== 'ALL') params.append('sentiment', sentiment);

  const response = await fetch(`${BASE_URL}/reviews/${analysisId}?${params.toString()}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch reviews: ${response.statusText}`);
  }
  return await response.json();
}

export async function getBrief(analysisId: string): Promise<string> {
  const response = await fetch(`${BASE_URL}/brief/${analysisId}`);
  if (!response.ok) {
    throw new Error(`Failed to generate brief: ${response.statusText}`);
  }
  return await response.text();
}

export async function getHeatmap(analysisId: string): Promise<HeatmapData> {
  const response = await fetch(`${BASE_URL}/heatmap/${analysisId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch heatmap: ${response.statusText}`);
  }
  return await response.json();
}
