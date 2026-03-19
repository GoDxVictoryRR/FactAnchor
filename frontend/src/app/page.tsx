import React from "react";
import { cookies } from "next/headers";
import Link from "next/link";
import { Navbar } from "@/components/layout/Navbar";
import { UploadPanel } from "@/components/layout/UploadPanel";
import { Badge } from "@/components/ui/Badge";
import type { ReportSummary } from "@/lib/types/api";

async function getRecentReports(): Promise<ReportSummary[] | null> {
    const cookieStore = cookies();
    const token = cookieStore.get("fa_token")?.value;
    if (!token) return null;

    try {
        const baseUrl = process.env.API_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL || "https://factanchor-api.onrender.com";
        const res = await fetch(`${baseUrl}/api/v1/reports?page=1&per_page=10`, {
            headers: { Authorization: `Bearer ${token}` },
            cache: "no-store",
        });
        if (!res.ok) return null;
        const data = await res.json();
        return data.reports ?? data.items ?? [];
    } catch {
        return null;
    }
}

function timeAgo(dateStr: string): string {
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    return `${Math.floor(hrs / 24)}d ago`;
}

export default async function HomePage() {
    const reports = await getRecentReports();

    return (
        <div className="min-h-screen relative flex flex-col">
            <Navbar />
            <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 w-full">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
                    {/* Left: Upload */}
                    <div className="lg:col-span-7">
                        <UploadPanel />
                    </div>

                    {/* Right: Recent Reports */}
                    <div className="lg:col-span-5">
                        <div className="flex items-center justify-between mb-6 px-1">
                            <h2 className="text-sm font-bold text-blue-400 uppercase tracking-[0.2em]">Audit History</h2>
                            <div className="h-px flex-1 bg-white/10 ml-4 opacity-50" />
                        </div>

                        {reports === null ? (
                            <div className="glass-card p-10 text-center border-dashed border-white/5 bg-white/[0.02]">
                                <p className="text-gray-400 text-sm mb-4 font-medium">Authentication required to view history.</p>
                                <Link href="/login" className="inline-block px-6 py-2 bg-blue-600/20 text-blue-400 border border-blue-500/30 rounded-full text-xs font-bold uppercase tracking-wider hover:bg-blue-600/30 transition-all">
                                    Authorise Session
                                </Link>
                            </div>
                        ) : reports.length === 0 ? (
                            <div className="glass-card p-10 text-center border-dashed border-white/5 bg-white/[0.02]">
                                <p className="text-gray-500 text-sm font-medium italic">
                                    Registry empty. Submit document to begin.
                                </p>
                            </div>
                        ) : (
                            <div className="space-y-3">
                                {reports.map((r) => (
                                    <Link
                                        key={r.id}
                                        href={`/report/${r.id}`}
                                        className="group block glass-card p-5 border-white/5 bg-white/[0.03] hover:bg-white/[0.07] hover:border-white/10 transition-all duration-300"
                                    >
                                        <div className="flex items-center justify-between">
                                            <div className="flex-1 min-w-0 pr-4">
                                                <div className="flex items-center gap-2 mb-1.5">
                                                    <div className="w-1.5 h-1.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.8)]" />
                                                    <p className="text-[15px] font-semibold text-white truncate leading-none">
                                                        {r.title || `Audit // ${r.id.slice(0, 8).toUpperCase()}`}
                                                    </p>
                                                </div>
                                                <p className="text-[11px] text-gray-500 font-mono uppercase tracking-wider">{timeAgo(r.created_at)}</p>
                                            </div>
                                            <div className="flex flex-col items-end gap-2">
                                                <Badge status={r.status} size="sm" className="shadow-lg shadow-black/20" />
                                                {r.confidence_score !== null && (
                                                    <span className="text-[10px] font-bold font-mono text-gray-400 bg-black/20 px-1.5 py-0.5 rounded">
                                                        SCORE: {r.confidence_score.toFixed(1)}%
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    </Link>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
}
