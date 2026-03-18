"use client";

import { useState, useCallback, useRef } from "react";

export function useClipboard(timeout = 2000): {
    copy: (text: string) => Promise<void>;
    copied: boolean;
} {
    const [copied, setCopied] = useState(false);
    const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    const copy = useCallback(
        async (text: string) => {
            if (!navigator.clipboard) {
                console.warn("Clipboard API not available");
                return;
            }
            try {
                await navigator.clipboard.writeText(text);
                setCopied(true);
                if (timerRef.current) clearTimeout(timerRef.current);
                timerRef.current = setTimeout(() => setCopied(false), timeout);
            } catch {
                console.warn("Failed to copy to clipboard");
            }
        },
        [timeout]
    );

    return { copy, copied };
}
