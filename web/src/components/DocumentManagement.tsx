
interface DocumentManagementProps {
    documents: string[];
    loadingDocuments: boolean;
    syncing: boolean;
    syncResult: Record<string, unknown> | null;
    documentError: string;
    onGetDocuments: () => void;
    onSync: () => void;
}

export default function DocumentManagement({
                                               documents,
                                               loadingDocuments,
                                               syncing,
                                               syncResult,
                                               documentError,
                                               onGetDocuments,
                                               onSync,
                                           }: DocumentManagementProps) {
    return (
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

            {syncResult && (
                <div className="sync-result-panel">
                    <h3>인덱스 동기화 결과</h3>
                    <pre>
                        {JSON.stringify(syncResult, null, 2)}
                    </pre>
                </div>
            )}
        </section>
    );
}
