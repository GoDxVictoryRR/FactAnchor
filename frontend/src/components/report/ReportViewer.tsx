"use client";

import React, { useMemo, useState } from "react";
import { useReportStore } from "@/lib/stores/reportStore";
import { ClaimPopover } from "./ClaimPopover";
import type { Claim, ClaimStatus } from "@/lib/types/api";
import clsx from "clsx";

interface Segment {
    text: string;
    claim?: Claim;
}

function buildSegments(text: string, claims: Claim[]): Segment[] {
    const safeText = text || "";
    const safeClaims = claims || [];
    const sorted = [...safeClaims].sort((a, b) => (a.char_start || 0) - (b.char_start || 0));
    const segments: Segment[] = [];
    let cursor = 0;

    for (const claim of sorted) {
        const start = claim.char_start || 0;
        const end = claim.char_end || safeText.length;

        if (start > cursor) {
            segments.push({ text: safeText.slice(cursor, start) });
        }
        if (start >= cursor) {
            segments.push({ text: safeText.slice(start, end), claim });
            cursor = end;
        }
    }

    if (cursor < safeText.length) {
        segments.push({ text: safeText.slice(cursor) });
    }

    return segments;
}

const STATUS_CLASSES: Record<ClaimStatus, string> = {
    verified: "bg-emerald-500/20 border-b-2 border-emerald-400 text-emerald-100 cursor-pointer verified-glow",
    flagged: "bg-red-500/20 border-b-2 border-red-400 text-red-100 cursor-pointer",
    uncertain: "bg-amber-500/20 border-b-2 border-amber-400 text-amber-100 cursor-pointer",
    pending: "bg-white/5 border-b border-white/20 text-gray-400 cursor-default animate-pulse",
    error: "bg-red-900/40 border-b border-red-500/50 text-red-200 cursor-pointer opacity-80",
};

export function ReportViewer() {
    const report = useReportStore((s) => s.report);
    const claimStatuses = useReportStore((s) => s.claimStatuses);
    const [selectedClaim, setSelectedClaim] = useState<Claim | null>(null);

    const segments = useMemo(() => {
        if (!report) return [];
        return buildSegments(report.raw_text || "", report.claims || []);
    }, [report]);

    if (!report) return null;

    return (
        <div className="h-full overflow-y-auto p-8 custom-scrollbar relative">
            <div className="max-w-3xl mx-auto glass-card p-10 bg-white/0 shadow-none border-none">
                {report.title && (
                    <h1 className="text-3xl font-bold text-white mb-8 tracking-tight shimmer-text">
                        {report.title}
                    </h1>
                )}
                <div className="text-[17px] leading-[1.8] text-gray-200 whitespace-pre-wrap font-medium">
                    {segments.map((seg, i) => {
                        if (!seg.claim) {
                            return <span key={i} className="opacity-90">{seg.text}</span>;
                        }

                        const liveStatus = claimStatuses[seg.claim.id] || seg.claim.status;
                        return (
                            <span
                                key={i}
                                data-claim-id={seg.claim.id}
                                className={clsx(
                                    "transition-all duration-500 rounded-sm px-1 inline-block",
                                    STATUS_CLASSES[liveStatus]
                                )}
                                onClick={() => setSelectedClaim(seg.claim!)}
                                role="button"
                                tabIndex={0}
                                onKeyDown={(e) => {
                                    if (e.key === "Enter" || e.key === " ") setSelectedClaim(seg.claim!);
                                }}
                            >
                                {seg.text}
                            </span>
                        );
                    })}
                </div>
            </div>

            {selectedClaim && (
                <ClaimPopover
                    claim={selectedClaim}
                    onClose={() => setSelectedClaim(null)}
                />
            )}
        </div>
    );
}
