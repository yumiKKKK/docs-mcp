export interface SyncResponse {
    [key: string]: unknown;
}

export interface StatisticsResponse {
    documents: number;
    chunks: number;
    extensions: Record<string, number>;
}

export interface DocumentsResponse {
    documents: string[];
}