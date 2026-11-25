
import DocumentList from './DocumentList';
import StatisticsPanel from './StatisticsPanel';

import type {
    StatisticsResponse,
    SyncResponse,
} from '../../types/management';

interface ManagementSectionProps {
    documents: string[];
    loadingDocuments: boolean;
    documentError: string;

    syncing: boolean;
    syncResult: SyncResponse | null;

    statistics: StatisticsResponse | null;
    loadingStatistics: boolean;
    statisticsError: string;

    onGetDocuments: () => void;
    onSync: () => void;
    onGetStatistics: () => void;
}

export default function ManagementSection({
                                              documents,
                                              loadingDocuments,
                                              documentError,
                                              syncing,
                                              syncResult,
                                              statistics,
                                              loadingStatistics,
                                              statisticsError,
                                              onGetDocuments,
                                              onSync,
                                              onGetStatistics,
                                          }: ManagementSectionProps) {
    return (
        <section className="management-section">

            <div className="section-heading">
                <div>
                    <h2>문서 관리</h2>
                    <p>
                        문서 목록과 검색 인덱스 상태를 관리합니다.
                    </p>
                </div>
            </div>

            <div className="management-actions">
                <button
                    className="secondary-button"
                    onClick={onGetDocuments}
                    disabled={loadingDocuments || syncing}
                >
                    {loadingDocuments
                        ? '문서 조회 중...'
                        : '문서 목록 조회'}
                </button>

                <button
                    className="primary-button"
                    onClick={onSync}
                    disabled={syncing || loadingDocuments}
                >
                    {syncing
                        ? '인덱스 동기화 중...'
                        : '인덱스 동기화'}
                </button>
            </div>

            {documentError && (
                <div className="management-error">
                    {documentError}
                </div>
            )}

            {syncResult && (
                <div className="sync-result-panel">
                    <h3>인덱스 동기화 결과</h3>
                    <pre>
                        {JSON.stringify(syncResult, null, 2)}
                    </pre>
                </div>
            )}

            <DocumentList
                documents={documents}
                loading={loadingDocuments}
            />

            <StatisticsPanel
                statistics={statistics}
                loading={loadingStatistics}
                error={statisticsError}
                onRefresh={onGetStatistics}
            />

        </section>
    );
}
