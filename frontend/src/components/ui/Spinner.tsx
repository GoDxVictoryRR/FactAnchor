"use client";

import React from "react";
import { Loader2 } from "lucide-react";
import clsx from "clsx";

interface SpinnerProps {
    size?: number;
    className?: string;
}

export function Spinner({ size = 16, className }: SpinnerProps) {
    return (
        <Loader2
            size={size}
            className={clsx("animate-spin text-blue-400", className)}
        />
    );
}
