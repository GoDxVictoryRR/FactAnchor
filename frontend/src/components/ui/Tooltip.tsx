"use client";

import React from "react";

interface TooltipProps {
    content: string;
    children: React.ReactNode;
}

export function Tooltip({ content, children }: TooltipProps) {
    return (
        <div className="relative group inline-block">
            {children}
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-black/80 backdrop-blur-md border border-white/10 rounded text-[10px] text-white opacity-0 group-hover:opacity-100 transition-opacity z-50 pointer-events-none whitespace-nowrap">
                {content}
            </div>
        </div>
    );
}
