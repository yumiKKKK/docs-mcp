
interface DocumentListProps {
    documents: string[];
    loading: boolean;
}

export default function DocumentList({
                                         documents,
                                         loading,
                                     }: DocumentListProps) {
    return (
        <div className="document-list-panel">
            <div className="document-list-heading">
                <h3>등록된 문서</h3>

                <span className="document-count">
                    {documents.length}개
                </span>
            </div>

            {loading ? (
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
                </div>
            )}
        </div>
    );
}
