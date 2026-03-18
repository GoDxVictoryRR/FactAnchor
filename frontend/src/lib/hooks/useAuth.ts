"use client";

import { useCallback } from "react";
import { setToken } from "@/lib/api/client";

export function useAuth() {
    const getToken = useCallback((): string | null => {
        if (typeof document === "undefined") return null;
        const match = document.cookie.match(/(?:^|;\s*)fa_token=([^;]*)/);
        if (match) return decodeURIComponent(match[1]);
        return localStorage.getItem("fa_token");
    }, []);

    const saveToken = useCallback((token: string) => {
        setToken(token);
    }, []);

    const logout = useCallback(() => {
        document.cookie = "fa_token=; Max-Age=0; path=/";
        localStorage.removeItem("fa_token");
        window.location.href = "/login";
    }, []);

    const isAuthenticated = useCallback((): boolean => {
        return getToken() !== null;
    }, [getToken]);

    return { getToken, saveToken, logout, isAuthenticated };
}
