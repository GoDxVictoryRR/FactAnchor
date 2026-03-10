"use client";

import React, { useEffect, useRef, useState } from "react";
import type { Claim } from "@/lib/types/api";
import { useReportStore } from "@/lib/stores/reportStore";
import { useClipboard } from "@/lib/hooks/useClipboard";
import { Badge } from "@/components/ui/Badge";
import { X, Copy, Check, ChevronDown, ChevronUp } from "lucide-react";
import clsx from "clsx";

interface ClaimPopoverProps {
    claim: Claim;
    onClose: () => void;
}

export function ClaimPopover({ claim, onClose }: ClaimPopoverProps) {
    const liveStatus = useReportStore((s) => s.claimStatuses[claim.id]) || claim.status;
    const [showSql, setShowSql] = useState(false);
    const { copy, copied } = useClipboard();
    const popoverRef = useRef<HTMLDivElement>(null);

    // Close on Escape
    useEffect(() => {
        const handleKey = (e: KeyboardEvent) => {
            if (e.key === "Escape") onClose();
        };
        document.addEventListener("keydown", handleKey);
        return () => document.removeEventListener("keydown", handleKey);
    }, [onClose]);

    // Close on click outside
    useEffect(() => {
        const handleClick = (e: MouseEvent) => {
            if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
                onClose();
            }
        };
        document.addEventListener("mousedown", handleClick);
        return () => document.removeEventListener("mousedown", handleClick);
    }, [onClose]);

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm animate-fade-in">
            <div
                ref={popoverRef}
                className={clsx(
                    "glass-card w-full max-w-lg p-8 shadow-[0_20px_50px_rgba(0,0,0,0.5)] border-white/20 relative",
                    "animate-slide-up"
                )}
            >
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500/50 via-purple-500/50 to-emerald-500/50" />

                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                        <Badge status={liveStatus} size="md" className="shadow-lg shadow-emerald-900/10" />
                        <span className="text-sm font-mono text-gray-400 tracking-wider">
                            CLAIM // {claim.sequence_num.toString().padStart(3, '0')}
                        </span>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-gray-500 hover:text-white transition-all bg-white/5 p-1.5 rounded-full hover:bg-white/10"
                    >
                        <X size={18} />
                    </button>
                </div>

                {/* Claim text */}
                <div className="bg-white/5 p-5 rounded-xl border border-white/5 mb-6">
                    <p className="text-gray-100 text-base leading-relaxed font-medium italic">
                        &ldquo;{claim.claim_text}&rdquo;
                    </p>
                </div>

                {/* Verification Detail */}
                <div className="space-y-4 text-sm mb-6">
                    <h3 className="text-xs font-bold text-blue-400 uppercase tracking-widest mb-2">
                        System Audit Logs
                    </h3>

                    <div className="flex justify-between items-center border-b border-white/5 pb-2">
                        <span className="text-gray-400 font-medium">Claim Type</span>
                        <span className="font-mono text-gray-200 capitalize bg-white/5 px-2 py-0.5 rounded">{claim.claim_type}</span>
                    </div>

                    <div className="flex justify-between items-center border-b border-white/5 pb-2">
                        <span className="text-gray-400 font-medium">Verification Status</span>
                        <Badge status={liveStatus} size="sm" />
                    </div>

                    {/* Show DB expected value if flagged */}
                    {(liveStatus === "flagged" || liveStatus === "verified") && claim.db_expected_value && (
                        <div className="flex justify-between items-center border-b border-white/5 pb-2">
                            <span className="text-gray-400 font-medium">Database Payload</span>
                            <span className="font-mono text-sm text-emerald-400 bg-emerald-400/10 px-2 py-0.5 rounded">{claim.db_expected_value}</span>
                        </div>
                    )}

                    {/* Show similarity score for qualitative claims */}
                    {claim.claim_type === "qualitative" && claim.similarity_score !== null && (
                        <div className="flex justify-between items-center border-b border-white/5 pb-2">
                            <span className="text-gray-400 font-medium">Vector Confidence</span>
                            <span className="font-mono text-sm text-blue-400 bg-blue-400/10 px-2 py-0.5 rounded">{(claim.similarity_score * 100).toFixed(1)}%</span>
                        </div>
                    )}

                    {/* Verified at */}
                    {claim.verified_at && (
                        <div className="flex justify-between items-center">
                            <span className="text-gray-400 font-medium">Timestamp</span>
                            <span className="text-gray-300 font-mono text-xs">
                                {new Date(claim.verified_at).toLocaleString("en-US", {
                                    dateStyle: "medium",
                                    timeStyle: "short",
                                })}
                            </span>
                        </div>
                    )}
                </div>

                {/* SQL Audit Trail */}
                {claim.llm_generated_sql && (
                    <div className="pt-4 border-t border-white/10">
                        <button
                            onClick={() => setShowSql(!showSql)}
                            className="flex items-center gap-2 text-xs font-bold text-gray-500 uppercase tracking-widest hover:text-blue-400 transition-colors w-full"
                        >
                            {showSql ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                            LLM-Generated SQL Audit
                        </button>
                        {showSql && (
                            <div className="mt-4 relative group">
                                <pre className="bg-black/40 text-blue-300 p-5 rounded-xl text-xs overflow-x-auto font-mono leading-relaxed border border-white/5 custom-scrollbar">
                                    {claim.llm_generated_sql}
                                </pre>
                                <button
                                    onClick={() => copy(claim.llm_generated_sql!)}
                                    className="absolute top-3 right-3 text-gray-500 hover:text-blue-400 transition-colors bg-white/5 p-1 rounded opacity-0 group-hover:opacity-100"
                                    title="Copy SQL"
                                >
                                    {copied ? <Check size={14} /> : <Copy size={14} />}
                                </button>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
