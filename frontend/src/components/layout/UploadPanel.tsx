"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { submitReport, RateLimitError, ApiError } from "@/lib/api/client";
import { Button } from "@/components/ui/Button";
import { FileText } from "lucide-react";

const MAX_CHARS = 100_000;

export function UploadPanel() {
    const router = useRouter();
    const [text, setText] = useState("");
    const [title, setTitle] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [retryCountdown, setRetryCountdown] = useState(0);

    const handleSubmit = async () => {
        if (!text.trim()) return;
        setLoading(true);
        setError(null);

        try {
            const res = await submitReport({ text, title: title || undefined });
            router.push(`/report/${res.report_id}`);
        } catch (e) {
            if (e instanceof RateLimitError) {
                setError(`Rate limited. Please try again in ${e.retryAfterSeconds}s.`);
                setRetryCountdown(e.retryAfterSeconds);
                const interval = setInterval(() => {
                    setRetryCountdown((prev) => {
                        if (prev <= 1) {
                            clearInterval(interval);
                            setError(null);
                            return 0;
                        }
                        return prev - 1;
                    });
                }, 1000);
            } else if (e instanceof ApiError) {
                setError(e.message);
            } else {
                setError("An unexpected error occurred.");
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="glass-card p-6 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-emerald-500 opacity-50" />
            <div className="flex items-center gap-2 mb-5">
                <FileText size={20} className="text-blue-400" />
                <h2 className="text-lg font-semibold text-white tracking-tight">Verify a Document</h2>
            </div>

            <input
                type="text"
                placeholder="Report title (optional)"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500/50 mb-3 transition-all"
            />

            <div className="relative">
                <textarea
                    placeholder="Paste AI-generated text here…"
                    value={text}
                    onChange={(e) => setText(e.target.value.slice(0, MAX_CHARS))}
                    rows={12}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-sm text-gray-200 placeholder-gray-500 resize-none focus:outline-none focus:ring-1 focus:ring-blue-500/50 leading-relaxed transition-all"
                />
                <span className="absolute bottom-3 right-3 text-xs text-gray-500 font-mono">
                    {text.length.toLocaleString()} / {MAX_CHARS.toLocaleString()}
                </span>
            </div>

            {error && (
                <div className="mt-4 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3">
                    {error}
                    {retryCountdown > 0 && ` (${retryCountdown}s)`}
                </div>
            )}

            <Button
                onClick={handleSubmit}
                disabled={!text.trim() || loading}
                loading={loading}
                size="lg"
                className="w-full mt-6 bg-blue-600 hover:bg-blue-500 text-white border-none shadow-lg shadow-blue-900/20"
            >
                Verify Report
            </Button>
        </div>
    );
}
