import { useState } from 'react';

import SearchBar from './components/SearchBar';
import SearchResultList from './components/SearchResultList';
import Pagination from './components/Pagination';

import {
    searchDocuments,
    getDocuments,
    syncDocuments,
} from './services/searchApi';

import type { SearchResponse } from './types/search';

import './styles.css';

export default function App() {
    // 검색 상태
    const [query, setQuery] = useState('');
    const [submittedQuery, setSubmittedQuery] = useState('');
    const [page, setPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);
    const [data, setData] = useState<SearchResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    // 문서 관리 상태
    const [documents, setDocuments] = useState<string[]>([]);
    const [loadingDocuments, setLoadingDocuments] = useState(false);
    const [syncing, setSyncing] = useState(false);
    const [syncResult, setSyncResult] =
        useState<Record<string, unknown> | null>(null);
    const [documentError, setDocumentError] = useState('');

    // 검색
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
            setData(
                await searchDocuments(clean, nextPage, nextSize)
            );
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

    // 문서 목록 조회
    async function handleGetDocuments() {
        setLoadingDocuments(true);
        setDocumentError('');

        try {
            const result = await getDocuments();

            setDocuments(result.documents);

            return true;
        } catch (e) {
            setDocumentError(
                e instanceof Error
                    ? e.message
                    : '문서 목록 조회에 실패했습니다.'
            );

            return false;
        } finally {
            setLoadingDocuments(false);
        }
    }

    // 인덱스 동기화
    async function handleSync() {
        if (syncing) return;

        setSyncing(true);
        setDocumentError('');
        setSyncResult(null);

        try {
            const result = await syncDocuments();

            setSyncResult(result);

            const success = await handleGetDocuments();
            if (!success) {
                setDocumentError(
                    '동기화는 완료되었지만 문서 목록을 갱신하지 못했습니다.'
                );
            }
        } catch (e) {
            setDocumentError(
                e instanceof Error
                    ? e.message
                    : '인덱스 동기화 중 오류가 발생했습니다.'
            );
        } finally {
            setSyncing(false);
        }
    }

    return (
        <div className="app-shell">

            {/* 상단 헤더 */}
            <header className="topbar">
                <a className="brand" href="/">
                    <span className="brand-mark">D</span>
                    <span>Docsearch</span>
                </a>

                <span className="topbar-note">
          내부 문서 검색
        </span>
            </header>

            <main className="main-content">

                {/* 검색 영역 */}
                <section className="hero">
                    <div className="eyebrow">
                        <span className="eyebrow-dot" />
                        DOCUMENT WORKSPACE
                    </div>

                    <h1>
                        필요한 문서를 <span>빠르게 찾으세요.</span>
                    </h1>

                    <p>
                        문서의 제목과 내용을 키워드로 검색하고,
                        관련도가 높은 결과부터 확인할 수 있습니다.
                    </p>

                    <SearchBar
                        query={query}
                        setQuery={value => {
                            setQuery(value);

                            if (value.trim() !== submittedQuery) {
                                setPage(1);
                            }
                        }}
                        onSearch={() => runSearch(query, 1)}
                        loading={loading}
                    />

                    <div className="search-hint">
                        Enter 키로 검색 · 키워드는 공백으로 구분할 수 있습니다.
                    </div>
                </section>

                {/* 문서 관리 영역 */}
                <section className="management-section">

                    <div className="section-heading">
                        <div>
                            <h2>문서 관리</h2>
                            <p>
                                등록된 문서를 확인하고 검색 인덱스를 갱신합니다.
                            </p>
                        </div>
                    </div>

                    <div className="management-actions">

                        <button
                            className="secondary-button"
                            onClick={handleGetDocuments}
                            disabled={loadingDocuments || syncing}
                        >
                            {loadingDocuments
                                ? '문서 조회 중...'
                                : '문서 목록 조회'}
                        </button>

                        <button
                            className="primary-button"
                            onClick={handleSync}
                            disabled={syncing || loadingDocuments}
                        >
                            {syncing
                                ? '인덱스 동기화 중...'
                                : '인덱스 동기화'}
                        </button>

                    </div>

                    {/* 문서 관리 오류 */}
                    {documentError && (
                        <div className="management-error">
                            {documentError}
                        </div>
                    )}

                    {/* 문서 목록 */}
                    <div className="document-list-panel">

                        <div className="document-list-heading">
                            <h3>등록된 문서</h3>
                            <span className="document-count">
                {documents.length}개
              </span>
                        </div>

                        {loadingDocuments ? (
                            <div className="management-empty">
                                문서 목록을 불러오고 있습니다.
                            </div>
                        ) : documents.length > 0 ? (
                            <ul className="document-list">
                                {documents.map((document, index) => (
                                    <li key={`${document}-${index}`}>
                    <span className="document-icon">
                      📄
                    </span>
                                        <span>{document}</span>
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            <div className="management-empty">
                                등록된 문서가 없습니다.
                                문서 목록 조회 버튼을 눌러 확인하세요.
                            </div>
                        )}

                    </div>

                    {/* 동기화 결과 */}
                    {syncResult && (
                        <div className="sync-result-panel">
                            <h3>인덱스 동기화 결과</h3>

                            <pre>
                {JSON.stringify(syncResult, null, 2)}
              </pre>
                        </div>
                    )}

                </section>

                {/* 기존 검색 결과 영역 */}
                <section className="results-section">

                    <div className="section-heading">
                        <div>
                            <h2>검색 결과</h2>

                            <p>
                                {data ? (
                                    <>
                                        <strong>
                                            {data.total.toLocaleString()}개
                                        </strong>
                                        {' '}문서 · {' '}

                                        {data.total_pages
                                            ? `${data.page} / ${data.total_pages} 페이지`
                                            : '페이지 없음'}
                                    </>
                                ) : (
                                    '검색어를 입력해 문서를 탐색하세요.'
                                )}
                            </p>
                        </div>

                        {data && (
                            <label className="page-size">
                                페이지당

                                <select
                                    value={pageSize}
                                    onChange={e => {
                                        const size = Number(e.target.value);

                                        setPageSize(size);

                                        runSearch(
                                            submittedQuery,
                                            1,
                                            size
                                        );
                                    }}
                                >
                                    <option value={5}>5개</option>
                                    <option value={10}>10개</option>
                                    <option value={20}>20개</option>
                                    <option value={50}>50개</option>
                                </select>
                            </label>
                        )}
                    </div>

                    {loading ? (
                        <div className="state-panel">
                            <span className="spinner" />
                            <h3>문서를 검색하고 있습니다</h3>
                            <p>검색 결과를 정리하고 있어요.</p>
                        </div>

                    ) : error ? (
                        <div className="state-panel error-state">
                            <span className="state-symbol">!</span>
                            <h3>검색할 수 없습니다</h3>
                            <p>{error}</p>

                            <button
                                className="secondary-button"
                                onClick={() =>
                                    runSearch(submittedQuery || query, page)
                                }
                            >
                                다시 시도
                            </button>
                        </div>

                    ) : data && data.results.length ? (
                        <>
                            <SearchResultList
                                results={data.results}
                                page={data.page}
                                pageSize={data.page_size}
                            />

                            <Pagination
                                page={data.page}
                                totalPages={data.total_pages}
                                hasPrevious={data.has_previous}
                                hasNext={data.has_next}
                                onPage={n =>
                                    runSearch(submittedQuery, n)
                                }
                            />
                        </>

                    ) : data ? (
                        <div className="state-panel">
                            <span className="state-symbol">⌕</span>
                            <h3>일치하는 문서가 없습니다</h3>
                            <p>
                                다른 키워드를 사용하거나 검색어를 짧게 입력해 보세요.
                            </p>
                        </div>

                    ) : (
                        <div className="empty-intro">
                            <div className="empty-illustration">
                                <span>⌕</span>
                                <i />
                                <b />
                            </div>

                            <h3>문서 탐색을 시작해 보세요</h3>

                            <p>
                                키워드를 입력하면 관련 문서와 발췌문을 보여드립니다.
                            </p>
                        </div>
                    )}

                </section>

            </main>

            <footer>
                Docsearch <span>·</span>
                검색 결과는 등록된 문서 내용을 기준으로 제공됩니다.
            </footer>

        </div>
    );
}