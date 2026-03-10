"use client";

import React, { useState, useMemo } from "react";
import { useReportStore } from "@/lib/stores/reportStore";
import { Badge } from "@/components/ui/Badge";
import type { ClaimStatus } from "@/lib/types/api";
import clsx from "clsx";

type FilterTab = "all" | "flagged" | "uncertain";

export function ClaimSidebar() {
    const report = useReportStore((s) => s.report);
    const claimStatuses = useReportStore((s) => s.claimStatuses);
    const verifiedCount = useReportStore((s) => s.verifiedCount);
    const [activeFilter, setActiveFilter] = useState<FilterTab>("all");

    const claims = report?.claims ?? [];
    const totalClaims = report?.total_claims ?? 0;

    const filteredClaims = useMemo(() => {
        if (activeFilter === "all") return claims;
        return claims.filter((c) => {
            const status = claimStatuses[c.id] || c.status;
            return status === activeFilter;
        });
    }, [claims, claimStatuses, activeFilter]);

    const scrollToClaim = (claimId: string) => {
        const el = document.querySelector(`[data-claim-id="${claimId}"]`);
        el?.scrollIntoView({ behavior: "smooth", block: "center" });
    };

    const tabs: { label: string; value: FilterTab }[] = [
        { label: "All", value: "all" },
        { label: "Flagged", value: "flagged" },
        { label: "Uncertain", value: "uncertain" },
    ];

    return (
        <div className="flex flex-col h-full bg-transparent">
            {/* Sticky header */}
            <div className="sticky top-0 z-10 bg-white/[0.02] backdrop-blur-md border-b border-white/5 px-6 py-5">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-[11px] font-black text-gray-400 uppercase tracking-[0.2em]">
                        Registry Entries // {verifiedCount}/{totalClaims}
                    </h2>
                </div>

                {/* Filter tabs */}
                <div className="flex gap-2">
                    {tabs.map((tab) => (
                        <button
                            key={tab.value}
                            onClick={() => setActiveFilter(tab.value)}
                            className={clsx(
                                "px-4 py-1.5 text-[10px] font-bold uppercase tracking-widest rounded-lg border transition-all active:scale-95",
                                activeFilter === tab.value
                                    ? "bg-blue-600 text-white border-blue-500 shadow-lg shadow-blue-900/20"
                                    : "bg-white/5 text-gray-400 border-white/5 hover:bg-white/10 hover:text-white"
                            )}
                        >
                            {tab.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Claim list */}
            <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
                {filteredClaims.length === 0 ? (
                    <div className="p-10 text-center text-xs font-medium text-gray-500 italic">
                        No entries match current parameters.
                    </div>
                ) : (
                    filteredClaims.map((claim) => {
                        const liveStatus: ClaimStatus = claimStatuses[claim.id] || claim.status;
                        return (
                            <button
                                key={claim.id}
                                onClick={() => scrollToClaim(claim.id)}
                                className="w-full flex items-center gap-4 px-6 py-4 text-left border-b border-white/5 bg-transparent hover:bg-white/[0.03] transition-all group"
                                style={{ contain: "content" }}
                            >
                                <span className="text-[10px] font-mono text-gray-600 w-8 shrink-0 group-hover:text-blue-500 transition-colors">
                                    {String(claim.sequence_num).padStart(3, '0')}
                                </span>
                                <span className="text-[13px] font-medium text-gray-300 truncate flex-1 group-hover:text-white transition-colors">
                                    {claim.claim_text}
                                </span>
                                <Badge status={liveStatus} size="sm" />
                            </button>
                        );
                    })
                )}
            </div>
        </div>
    );
}
