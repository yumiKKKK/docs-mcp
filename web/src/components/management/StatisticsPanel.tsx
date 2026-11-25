
import type { StatisticsResponse } from '../../types/management';

interface StatisticsPanelProps {
    statistics: StatisticsResponse | null;
    loading: boolean;
    error: string;
    onRefresh: () => void;
}

export default function StatisticsPanel({
                                            statistics,
                                            loading,
                                            error,
                                            onRefresh,
                                        }: StatisticsPanelProps) {

    const extensions = statistics
        ? Object.entries(statistics.extensions)
            .sort((a, b) => b[1] - a[1])
        : [];

    const totalDocuments = statistics?.documents ?? 0;

    return (
        <section className="statistics-section">

            <div className="section-heading">
                <div>
                    <h3>인덱싱 통계</h3>
                    <p>
                        문서, 청크 및 파일 형식별 인덱싱 현황입니다.
                    </p>
                </div>

                <button
                    className="secondary-button"
                    onClick={onRefresh}
                    disabled={loading}
                >
                    {loading ? '조회 중...' : '통계 새로고침'}
                </button>
            </div>

            {error ? (
                <div className="management-error">
                    {error}
                </div>
            ) : loading && !statistics ? (
                <div className="management-empty">
                    인덱싱 통계를 불러오고 있습니다.
                </div>
            ) : statistics ? (
                <>
                    {/* 통계 카드 */}
                    <div className="statistics-grid">

                        <div className="statistics-card">
                            <div className="statistics-icon document-stat">
                                📄
                            </div>

                            <span>전체 문서</span>

                            <strong>
                                {statistics.documents.toLocaleString()}
                            </strong>

                            <small>등록된 문서 개수</small>
                        </div>

                        <div className="statistics-card">
                            <div className="statistics-icon chunk-stat">
                                🧩
                            </div>

                            <span>전체 청크</span>

                            <strong>
                                {statistics.chunks.toLocaleString()}
                            </strong>

                            <small>분할된 문서 데이터 개수</small>
                        </div>

                    </div>

                    {/* 확장자별 통계 */}
                    <div className="extension-panel">

                        <div className="extension-heading">
                            <div>
                                <h4>파일 형식별 문서 현황</h4>
                                <p>
                                    총 {totalDocuments.toLocaleString()}개 문서
                                </p>
                            </div>
                        </div>

                        {extensions.length > 0 ? (
                            <div className="extension-list">

                                {extensions.map(([extension, count]) => {
                                    const percentage =
                                        totalDocuments > 0
                                            ? (count / totalDocuments) * 100
                                            : 0;

                                    return (
                                        <div
                                            className="extension-item"
                                            key={extension}
                                        >
                                            <div className="extension-info">
                                                <span className="extension-name">
                                                    {extension || '확장자 없음'}
                                                </span>

                                                <span className="extension-count">
                                                    {count.toLocaleString()}개
                                                    ({percentage.toFixed(1)}%)
                                                </span>
                                            </div>

                                            <div className="extension-progress">
                                                <div
                                                    className="extension-progress-bar"
                                                    style={{
                                                        width: `${percentage}%`,
                                                    }}
                                                />
                                            </div>
                                        </div>
                                    );
                                })}

                            </div>
                        ) : (
                            <div className="management-empty">
                                확장자별 통계가 없습니다.
                            </div>
                        )}

                    </div>
                </>
            ) : (
                <div className="management-empty">
                    통계 정보가 없습니다.
                    통계 새로고침 버튼을 눌러 확인하세요.
                </div>
            )}

        </section>
    );
}
