import React from "react";

export default function ReportLoading() {
    return (
        <div className="h-screen grid grid-cols-[60%_40%]">
            {/* Left panel skeleton */}
            <div className="p-8 space-y-4">
                <div className="h-8 w-2/3 bg-gray-200 rounded animate-pulse" />
                <div className="space-y-3 mt-6">
                    {Array.from({ length: 8 }).map((_, i) => (
                        <div
                            key={i}
                            className="h-4 bg-gray-200 rounded animate-pulse"
                            style={{ width: `${60 + Math.random() * 40}%` }}
                        />
                    ))}
                </div>
            </div>

            {/* Right panel skeleton */}
            <div className="border-l border-gray-200 bg-white">
                {/* Confidence score skeleton */}
                <div className="p-6 flex flex-col items-center border-b border-gray-200">
                    <div className="w-36 h-36 rounded-full bg-gray-200 animate-pulse" />
                    <div className="h-4 w-24 bg-gray-200 rounded animate-pulse mt-4" />
                </div>

                {/* Claim list skeleton */}
                <div className="p-4 space-y-3">
                    {Array.from({ length: 5 }).map((_, i) => (
                        <div key={i} className="flex items-center gap-3">
                            <div className="w-6 h-4 bg-gray-200 rounded animate-pulse" />
                            <div className="flex-1 h-4 bg-gray-200 rounded animate-pulse" />
                            <div className="w-16 h-5 bg-gray-200 rounded-full animate-pulse" />
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
