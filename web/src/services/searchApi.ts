import type { SearchResponse } from '../types/search';

export async function searchDocuments(query: string, page: number, pageSize: number): Promise<SearchResponse> {
  const params = new URLSearchParams({ query, page: String(page), page_size: String(pageSize) });
  const response = await fetch(`/api/search?${params.toString()}`);
  if (!response.ok) {
    let message = '검색 요청을 처리하지 못했습니다.';
    try { const body = await response.json(); message = body.detail || message; } catch { /* use fallback */ }
    throw new Error(message);
  }
  return response.json() as Promise<SearchResponse>;
}
