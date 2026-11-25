import type {SearchResponse} from '../types/search';

export interface DocumentListResponse {
  documents: string[];
}
export async function searchDocuments(query: string, page: number, pageSize: number): Promise<SearchResponse> {
    const params = new URLSearchParams({query, page: String(page), page_size: String(pageSize)});
    const response = await fetch(`/api/search?${params.toString()}`);
    if (!response.ok) {
        let message = '검색 요청을 처리하지 못했습니다.';
        try {
            const body = await response.json();
            message = body.detail || message;
        } catch { /* use fallback */
        }
        throw new Error(message);
    }
    return response.json() as Promise<SearchResponse>;
}

export async function getDocuments(): Promise<DocumentListResponse> {
  const response = await fetch('/api/documents');

  if (!response.ok) {
    throw new Error('문서 목록 조회에 실패했습니다.');
  }

  return response.json();
}

export async function syncDocuments(): Promise<Record<string, unknown>> {
  const response = await fetch('/api/index/sync', {
    method: 'POST',
  });

  if (!response.ok) {
    let message = '문서 인덱스 동기화에 실패했습니다.';

    try {
      const body = await response.json();
      message = body.detail || message;
    } catch {
    }

    throw new Error(message);
  }

  return response.json();
}

export async function getStatistics(): Promise<Record<string, unknown>> {
    const response = await fetch('/api/index/statistics');

    if (!response.ok) {
        throw new Error('인덱싱 통계를 조회하지 못했습니다.');
    }

    return response.json();
}