"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { ReportWebSocket } from "@/lib/api/websocket";
import { useReportStore } from "@/lib/stores/reportStore";
import type { ReportDetail } from "@/lib/types/api";
import { getReport } from "@/lib/api/client";

type ConnectionState = "connecting" | "connected" | "reconnecting" | "closed";

export function useReportStream(
    reportId: string,
    initialReport: ReportDetail
): {
    connectionState: ConnectionState;
    isComplete: boolean;
} {
    const [connectionState, setConnectionState] = useState<ConnectionState>("closed");
    const updateClaimStatus = useReportStore((s) => s.updateClaimStatus);
    const setComplete = useReportStore((s) => s.setComplete);
    const setReport = useReportStore((s) => s.setReport);
    const reportStatus = useReportStore((s) => s.report?.status);
    const wsRef = useRef<ReportWebSocket | null>(null);

    const isComplete = reportStatus === "complete";

    const handleConnectionChange = useCallback((state: ConnectionState) => {
        setConnectionState(state);
    }, []);

    useEffect(() => {
        // Skip WS if report is already complete
        if (initialReport.status === "complete") return;

        // Read token from cookie
        const match = document.cookie.match(/(?:^|;\s*)fa_token=([^;]*)/);
        const token = match ? decodeURIComponent(match[1]) : localStorage.getItem("fa_token");
        if (!token) return;

        const ws = new ReportWebSocket(reportId, token);
        wsRef.current = ws;

        ws.onClaimUpdate((update) => {
            updateClaimStatus(update.claim_id, update.status);
        });

        ws.onComplete((result) => {
            setComplete(result.confidence_score, result.anchor);
        });

        ws.onConnectionChange(handleConnectionChange);

        ws.onError((error) => {
            console.error("[WS Error]", error.code, error.message);
            setConnectionState("closed");
        });

        ws.connect();

        // 5. Polling fallback (every 5s) to ensure UI updates even if WS is stuck
        const pollInterval = setInterval(async () => {
            if (isComplete) {
                clearInterval(pollInterval);
                return;
            }
            try {
                const updated = await getReport(reportId);
                // Sync store with polled data
                if (updated) {
                    setReport(updated);
                    if (updated.status === "complete") {
                        setComplete(updated.confidence_score || 0, "");
                        clearInterval(pollInterval);
                    }
                }
            } catch (e) {
                console.warn("[Polling Fallback Error]", e);
            }
        }, 5000);

        return () => {
            ws.disconnect();
            wsRef.current = null;
            clearInterval(pollInterval);
        };
    }, [reportId, isComplete, initialReport.status, updateClaimStatus, setComplete, handleConnectionChange]);

    return { connectionState, isComplete };
}
