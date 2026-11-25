
import { useState } from 'react';

import {
    getDocuments,
    syncDocuments,
    getStatistics,
} from '../services/searchApi';

import type {
    SyncResponse,
    StatisticsResponse,
} from '../types/management';

export function useDocumentManagement() {
    // 문서 목록
    const [documents, setDocuments] = useState<string[]>([]);
    const [loadingDocuments, setLoadingDocuments] = useState(false);

    // 인덱스 동기화
    const [syncing, setSyncing] = useState(false);
    const [syncResult, setSyncResult] =
        useState<SyncResponse | null>(null);

    // 인덱스 통계
    const [statistics, setStatistics] =
        useState<StatisticsResponse | null>(null);

    const [loadingStatistics, setLoadingStatistics] =
        useState(false);

    const [statisticsError, setStatisticsError] = useState('');

    // 문서 관리 오류
    const [documentError, setDocumentError] = useState('');

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

    // 인덱스 통계 조회
    async function handleGetStatistics() {
        setLoadingStatistics(true);
        setStatisticsError('');

        try {
            const result = await getStatistics();
            setStatistics(result);

            return true;
        } catch (e) {
            setStatisticsError(
                e instanceof Error
                    ? e.message
                    : '인덱싱 통계를 조회하지 못했습니다.'
            );

            return false;
        } finally {
            setLoadingStatistics(false);
        }
    }

    // 인덱스 동기화
    async function handleSync() {
        if (syncing || loadingDocuments) return;

        setSyncing(true);
        setDocumentError('');
        setSyncResult(null);

        try {
            const result = await syncDocuments();

            setSyncResult(result);

            // 동기화 후 문서 목록과 통계 갱신
            await Promise.all([
                handleGetDocuments(),
                handleGetStatistics(),
            ]);
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

    return {
        documents,
        loadingDocuments,
        documentError,

        statistics,
        loadingStatistics,
        statisticsError,

        syncing,
        syncResult,

        handleGetDocuments,
        handleGetStatistics,
        handleSync,
    };
}
