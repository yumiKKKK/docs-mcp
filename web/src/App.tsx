
import { useState } from 'react';

import SearchBar from './components/SearchBar';
import SearchResultList from './components/SearchResultList';
import Pagination from './components/Pagination';

import ManagementSection from './components/management/ManagementSection';

import { useDocumentSearch } from './hooks/useDocumentSearch';
import { useDocumentManagement } from './hooks/useDocumentManagement';

import './styles.css';

type Tab = 'search' | 'management';

export default function App() {
    const [activeTab, setActiveTab] = useState<Tab>('search');

    const search = useDocumentSearch();
    const management = useDocumentManagement();

    return (
        <div className="app-shell">

            {/* Header */}
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

                {/* Navigation */}
                <nav className="app-tabs">
                    <button
                        className={
                            activeTab === 'search'
                                ? 'tab-button active'
                                : 'tab-button'
                        }
                        onClick={() => setActiveTab('search')}
                    >
                        <span>⌕</span>
                        문서 검색
                    </button>

                    <button
                        className={
                            activeTab === 'management'
                                ? 'tab-button active'
                                : 'tab-button'
                        }
                        onClick={() => setActiveTab('management')}
                    >
                        <span>▤</span>
                        문서 관리
                    </button>
                </nav>

                {/* Search Tab */}
                {activeTab === 'search' && (
                    <>
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
                                query={search.query}
                                setQuery={value => {
                                    search.setQuery(value);

                                    if (
                                        value.trim() !== search.submittedQuery
                                    ) {
                                        search.setPageSize(
                                            search.pageSize
                                        );
                                    }
                                }}
                                onSearch={() =>
                                    search.runSearch(search.query, 1)
                                }
                                loading={search.loading}
                            />
                        </section>

                        <section className="results-section">
                            <div className="section-heading">
                                <div>
                                    <h2>검색 결과</h2>
                                    <p>
                                        {search.data
                                            ? search.data.total > 0
                                                ? `${search.data.total.toLocaleString()}개 문서 · ${search.data.page} / ${search.data.total_pages} 페이지`
                                                : '검색 결과 0개 문서'
                                            : '검색어를 입력해 문서를 탐색하세요.'}
                                    </p>
                                </div>

                                {search.data && (
                                    <label className="page-size">
                                        페이지당
                                        <select
                                            value={search.pageSize}
                                            onChange={e => {
                                                const size = Number(
                                                    e.target.value
                                                );

                                                search.setPageSize(size);

                                                search.runSearch(
                                                    search.submittedQuery,
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

                            {search.loading ? (
                                <div className="state-panel">
                                    <span className="spinner" />
                                    <h3>문서를 검색하고 있습니다</h3>
                                    <p>검색 결과를 정리하고 있어요.</p>
                                </div>
                            ) : search.error ? (
                                <div className="state-panel error-state">
                                    <h3>검색할 수 없습니다</h3>
                                    <p>{search.error}</p>

                                    <button
                                        className="secondary-button"
                                        onClick={() =>
                                            search.runSearch(
                                                search.submittedQuery ||
                                                search.query,
                                                search.page
                                            )
                                        }
                                    >
                                        다시 시도
                                    </button>
                                </div>
                            ) : search.data?.results.length ? (
                                <>
                                    <SearchResultList
                                        results={search.data.results}
                                        page={search.data.page}
                                        pageSize={search.data.page_size}
                                    />

                                    <Pagination
                                        page={search.data.page}
                                        totalPages={search.data.total_pages}
                                        hasPrevious={search.data.has_previous}
                                        hasNext={search.data.has_next}
                                        onPage={n =>
                                            search.runSearch(
                                                search.submittedQuery,
                                                n
                                            )
                                        }
                                    />
                                </>
                            ) : (
                                <div className="empty-intro">
                                    <h3>
                                        {search.data
                                            ? '일치하는 문서가 없습니다'
                                            : '문서 탐색을 시작해 보세요'}
                                    </h3>
                                    <p>
                                        키워드를 입력하면 관련 문서와
                                        발췌문을 보여드립니다.
                                    </p>
                                </div>
                            )}
                        </section>
                    </>
                )}

                {/* Management Tab */}
                {activeTab === 'management' && (
                    <ManagementSection
                        {...management}
                        onGetDocuments={management.handleGetDocuments}
                        onSync={management.handleSync}
                        onGetStatistics={management.handleGetStatistics}
                    />
                )}

            </main>

            <footer>
                Docsearch <span>·</span>
                검색 결과는 등록된 문서 내용을 기준으로 제공됩니다.
            </footer>

        </div>
    );
}
