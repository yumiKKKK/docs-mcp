export type SearchResult = { filename: string; score: number; matched_terms: string[]; snippet: string };
export type SearchResponse = { query: string; total: number; page: number; page_size: number; total_pages: number; has_next: boolean; has_previous: boolean; results: SearchResult[] };
