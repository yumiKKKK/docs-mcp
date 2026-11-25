
import { useState } from 'react';
import { searchDocuments } from '../services/searchApi';
import type { SearchResponse } from '../types/search';

export function useDocumentSearch() {
    const [query, setQuery] = useState('');
    const [submittedQuery, setSubmittedQuery] = useState('');
    const [page, setPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);

    const [data, setData] = useState<SearchResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    async function runSearch(
        nextQuery = query,
        nextPage = 1,
        nextSize = pageSize
    ) {
        const clean = nextQuery.trim();

        if (!clean) {
            setError('검색어를 입력해 주세요.');
            setData(null);
            return;
        }

        setLoading(true);
        setError('');

        setSubmittedQuery(clean);
        setPage(nextPage);

        try {
            const result = await searchDocuments(
                clean,
                nextPage,
                nextSize
            );

            setData(result);
        } catch (e) {
            setData(null);

            setError(
                e instanceof Error
                    ? e.message
                    : '검색 중 오류가 발생했습니다.'
            );
        } finally {
            setLoading(false);
        }
    }

    return {
        query,
        setQuery,
        submittedQuery,
        page,
        pageSize,
        setPageSize,
        data,
        loading,
        error,
        runSearch,
    };
}
