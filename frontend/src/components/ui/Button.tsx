"use client";

import React from "react";
import clsx from "clsx";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "primary" | "secondary" | "ghost";
    size?: "sm" | "md" | "lg";
    loading?: boolean;
}

export function Button({
    variant = "primary",
    size = "md",
    loading = false,
    className,
    children,
    disabled,
    ...props
}: ButtonProps) {
    const base = "inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";

    const variants = {
        primary: "bg-blue-600 text-white hover:bg-blue-500 shadow-lg shadow-blue-900/20 active:scale-95",
        secondary: "bg-white/5 text-gray-200 border border-white/10 hover:bg-white/10 hover:border-white/20 backdrop-blur-md active:scale-95",
        ghost: "text-gray-400 hover:text-white hover:bg-white/5 active:scale-95",
    };

    const sizes = {
        sm: "text-xs px-3 py-1.5 gap-1.5 font-bold uppercase tracking-wider",
        md: "text-sm px-5 py-2.5 gap-2 font-bold uppercase tracking-widest",
        lg: "text-base px-8 py-4 gap-3 font-extrabold uppercase tracking-[0.15em]",
    };

    return (
        <button
            className={clsx(base, variants[variant], sizes[size], className)}
            disabled={disabled || loading}
            {...props}
        >
            {loading && (
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
            )}
            {children}
        </button>
    );
}
