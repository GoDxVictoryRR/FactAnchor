"use client";

import React, { useEffect, useRef, useState } from "react";
import { useReportStore } from "@/lib/stores/reportStore";
import { useClipboard } from "@/lib/hooks/useClipboard";
import { Copy, Check, HelpCircle } from "lucide-react";
import { Tooltip } from "@/components/ui/Tooltip";
import clsx from "clsx";

export function ConfidenceScore() {
    const report = useReportStore((s) => s.report);
    const verifiedCount = useReportStore((s) => s.verifiedCount);
    const flaggedCount = useReportStore((s) => s.flaggedCount);
    const uncertainCount = useReportStore((s) => s.uncertainCount);
    const { copy, copied } = useClipboard();

    const totalClaims = report?.total_claims ?? 0;
    const isComplete = report?.status === "complete";
    const confidenceScore = report?.confidence_score ?? 0;
    const fullHash = report?.full_hash ?? "";

    // Count-up animation
    const [displayScore, setDisplayScore] = useState(0);
    const hasAnimated = useRef(false);

    useEffect(() => {
        if (!isComplete || hasAnimated.current) return;
        hasAnimated.current = true;

        const start = performance.now();
        const duration = 600;
        const target = confidenceScore;

        const animate = (now: number) => {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            // Ease out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            setDisplayScore(eased * target);
            if (progress < 1) requestAnimationFrame(animate);
        };

        requestAnimationFrame(animate);
    }, [isComplete, confidenceScore]);

    // Progress ring calculations
    const radius = 54;
    const circumference = 2 * Math.PI * radius;
    const processedCount = verifiedCount + flaggedCount + uncertainCount;
    const progress = totalClaims > 0 ? processedCount / totalClaims : 0;
    const strokeDashoffset = circumference * (1 - progress);

    const scoreColorClass =
        confidenceScore >= 90
            ? "text-emerald-400 drop-shadow-[0_0_10px_rgba(52,211,153,0.3)]"
            : confidenceScore >= 70
                ? "text-amber-400 drop-shadow-[0_0_10px_rgba(251,191,36,0.3)]"
                : "text-red-400 drop-shadow-[0_0_10px_rgba(248,113,113,0.3)]";

    return (
        <div className="p-8 flex flex-col items-center">
            {!isComplete ? (
                /* Loading state — progress ring */
                <div className="relative w-40 h-40 mb-2">
                    <svg className="w-full h-full -rotate-90 scale-110" viewBox="0 0 120 120">
                        <circle
                            cx="60" cy="60" r={radius}
                            fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="6"
                        />
                        <circle
                            cx="60" cy="60" r={radius}
                            fill="none" stroke="url(#blueGradient)" strokeWidth="6"
                            strokeDasharray={circumference}
                            strokeDashoffset={strokeDashoffset}
                            strokeLinecap="round"
                            className="transition-all duration-700 ease-in-out"
                        />
                        <defs>
                            <linearGradient id="blueGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                <stop offset="0%" stopColor="#60a5fa" />
                                <stop offset="100%" stopColor="#34d399" />
                            </linearGradient>
                        </defs>
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">Verifying</span>
                        <span className="text-2xl font-black text-white font-mono leading-none">
                            {Math.round(progress * 100)}%
                        </span>
                        <span className="text-[10px] text-gray-500 font-medium mt-1">
                            {processedCount}/{totalClaims}
                        </span>
                    </div>
                </div>
            ) : (
                /* Complete state — score display */
                <div className="animate-scale-in flex flex-col items-center mb-2">
                    <div className="flex flex-col items-center justify-center w-40 h-40 rounded-full border border-white/5 bg-white/[0.02] shadow-[inset_0_0_20px_rgba(255,255,255,0.02)]">
                        <span className={clsx("text-5xl font-black font-mono tracking-tighter", scoreColorClass)}>
                            {displayScore.toFixed(1)}
                        </span>
                        <span className="text-[10px] font-bold text-gray-500 uppercase tracking-[0.2em] mt-2">Trust Score</span>
                    </div>

                    <div className="flex items-center gap-2 mt-6 bg-black/20 px-3 py-1.5 rounded-full border border-white/5">
                        <span className="text-[10px] text-gray-400 font-mono tracking-tight">
                            SIG // {report?.confidence_hash?.slice(0, 16).toUpperCase()}
                        </span>
                        <Tooltip content="Copy full hash">
                            <button
                                onClick={() => copy(fullHash)}
                                className="text-gray-500 hover:text-white transition-colors"
                            >
                                {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                            </button>
                        </Tooltip>
                    </div>
                </div>
            )}

            {/* Summary stats */}
            <div className="grid grid-cols-3 gap-6 w-full max-w-xs mt-8 px-4 py-6 border-t border-white/5">
                <div className="flex flex-col items-center">
                    <div className="text-lg font-black text-emerald-400 leading-none mb-1">{verifiedCount}</div>
                    <div className="text-[9px] font-bold text-gray-500 uppercase tracking-widest">Pass</div>
                </div>
                <div className="flex flex-col items-center border-x border-white/5">
                    <div className="text-lg font-black text-red-400 leading-none mb-1">{flaggedCount}</div>
                    <div className="text-[9px] font-bold text-gray-500 uppercase tracking-widest">Fail</div>
                </div>
                <div className="flex flex-col items-center">
                    <div className="text-lg font-black text-amber-400 leading-none mb-1">{uncertainCount}</div>
                    <div className="text-[9px] font-bold text-gray-500 uppercase tracking-widest">Hold</div>
                </div>
            </div>
        </div>
    );
}
