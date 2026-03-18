"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { ReportWebSocket } from "@/lib/api/websocket";
import { useReportStore } from "@/lib/stores/reportStore";
import type { ReportDetail } from "@/lib/types/api";

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

        return () => {
            ws.disconnect();
            wsRef.current = null;
        };
    }, [reportId, initialReport.status, updateClaimStatus, setComplete, handleConnectionChange]);

    return { connectionState, isComplete };
}
