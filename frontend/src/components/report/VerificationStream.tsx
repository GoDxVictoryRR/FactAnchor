"use client";

import React, { useEffect } from "react";
import type { ReportDetail } from "@/lib/types/api";
import { useReportStore } from "@/lib/stores/reportStore";
import { useReportStream } from "@/lib/hooks/useReportStream";
import { ReportViewer } from "./ReportViewer";
import { ClaimSidebar } from "./ClaimSidebar";
import { ConfidenceScore } from "./ConfidenceScore";
import { AlertTriangle, RefreshCw } from "lucide-react";

interface VerificationStreamProps {
    reportId: string;
    initialReport: ReportDetail;
}

export function VerificationStream({ reportId, initialReport }: VerificationStreamProps) {
    const setReport = useReportStore((s) => s.setReport);
    const { connectionState, isComplete } = useReportStream(reportId, initialReport);

    // Initialize store with server-fetched report data
    useEffect(() => {
        setReport(initialReport);
    }, [initialReport, setReport]);

    return (
        <div className="relative h-[calc(100vh-64px)] flex flex-col overflow-hidden">
            {/* Reconnection banners */}
            {connectionState === "reconnecting" && (
                <div className="bg-amber-500/10 backdrop-blur-md border-b border-amber-500/20 px-6 py-2.5 flex items-center gap-3 text-xs font-bold uppercase tracking-widest text-amber-400 animate-pulse">
                    <RefreshCw size={14} className="animate-spin" />
                    Synchronising verification stream…
                </div>
            )}
            {connectionState === "closed" && !isComplete && (
                <div className="bg-red-500/10 backdrop-blur-md border-b border-red-500/20 px-6 py-2.5 flex items-center justify-between text-xs font-bold uppercase tracking-widest text-red-400">
                    <div className="flex items-center gap-3">
                        <AlertTriangle size={14} />
                        Stream interrupted. Registry sync required.
                    </div>
                    <button
                        onClick={() => window.location.reload()}
                        className="px-4 py-1.5 bg-red-500/20 hover:bg-red-500/30 border border-red-500/30 rounded-full transition-all active:scale-95"
                    >
                        Re-Authorise
                    </button>
                </div>
            )}

            {/* Main layout */}
            <main className="flex-1 grid grid-cols-1 lg:grid-cols-[1fr_420px] min-h-0 bg-transparent">
                {/* Left panel — Document viewer */}
                <div className="overflow-hidden flex flex-col min-h-0 lg:border-r border-white/5">
                    <ReportViewer />
                </div>

                {/* Right panel — Confidence + Claims */}
                <aside className="hidden lg:flex flex-col bg-white/[0.02] backdrop-blur-xl min-h-0">
                    <div className="border-b border-white/5 bg-white/[0.02]">
                        <ConfidenceScore />
                    </div>
                    <div className="flex-1 min-h-0 overflow-hidden">
                        <ClaimSidebar />
                    </div>
                </aside>
            </main>
        </div>
    );
}
