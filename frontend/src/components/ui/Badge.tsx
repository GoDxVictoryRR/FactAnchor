"use client";

import React from "react";
import {
    CheckCircle2, AlertTriangle, HelpCircle, Clock, XCircle, CircleCheck,
} from "lucide-react";
import clsx from "clsx";
import type { ClaimStatus, ReportStatus } from "@/lib/types/api";

type BadgeStatus = ClaimStatus | ReportStatus;

interface BadgeProps {
    status: BadgeStatus;
    size?: "sm" | "md";
    className?: string;
}

const config: Record<string, { bg: string; text: string; border: string; Icon: React.ElementType; label: string }> = {
    verified: { bg: "bg-emerald-500/10", text: "text-emerald-400", border: "border-emerald-500/20", Icon: CheckCircle2, label: "Verified" },
    flagged: { bg: "bg-red-500/10", text: "text-red-400", border: "border-red-500/20", Icon: AlertTriangle, label: "Flagged" },
    uncertain: { bg: "bg-amber-500/10", text: "text-amber-400", border: "border-amber-500/20", Icon: HelpCircle, label: "Uncertain" },
    pending: { bg: "bg-white/5", text: "text-gray-400", border: "border-white/10", Icon: Clock, label: "Pending" },
    complete: { bg: "bg-blue-500/10", text: "text-blue-400", border: "border-blue-500/20", Icon: CircleCheck, label: "Complete" },
    completed: { bg: "bg-blue-500/10", text: "text-blue-400", border: "border-blue-500/20", Icon: CircleCheck, label: "Complete" },
    error: { bg: "bg-red-900/20", text: "text-red-300", border: "border-red-500/30", Icon: XCircle, label: "Error" },
    extracting: { bg: "bg-white/5", text: "text-gray-400", border: "border-white/10", Icon: Clock, label: "Extracting" },
    verifying: { bg: "bg-blue-500/10", text: "text-blue-400", border: "border-blue-500/20", Icon: Clock, label: "Verifying" },
    failed: { bg: "bg-red-900/20", text: "text-red-300", border: "border-red-500/30", Icon: XCircle, label: "Failed" },
};

export function Badge({ status, size = "sm", className }: BadgeProps) {
    const c = config[status] ?? config.pending;
    const sizeClasses = size === "sm" ? "text-[10px] px-2 py-0.5" : "text-xs px-2.5 py-1";

    return (
        <span
            className={clsx(
                "inline-flex items-center gap-1.5 rounded-full border font-bold uppercase tracking-wider backdrop-blur-sm transition-all duration-300",
                c.bg, c.text, c.border, sizeClasses, className
            )}
        >
            <c.Icon size={size === "sm" ? 10 : 12} />
            {c.label}
        </span>
    );
}
