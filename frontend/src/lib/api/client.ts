import type {
    ReportSubmitRequest,
    ReportSubmitResponse,
    ReportDetail,
    PaginatedReports,
    LoginResponse,
} from "@/lib/types/api";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ── Custom Errors ──

export class ApiError extends Error {
    constructor(
        public status: number,
        public code: string,
        message: string
    ) {
        super(message);
        this.name = "ApiError";
    }
}

export class RateLimitError extends Error {
    constructor(public retryAfterSeconds: number) {
        super(`Rate limited. Retry after ${retryAfterSeconds}s`);
        this.name = "RateLimitError";
    }
}

// ── Token management ──

function getToken(): string | null {
    if (typeof document === "undefined") return null;
    const match = document.cookie.match(/(?:^|;\s*)fa_token=([^;]*)/);
    if (match) return decodeURIComponent(match[1]);
    // Dev fallback: localStorage
    return localStorage.getItem("fa_token");
}

function clearToken(): void {
    document.cookie = "fa_token=; Max-Age=0; path=/";
    localStorage.removeItem("fa_token");
}

export function setToken(token: string): void {
    document.cookie = `fa_token=${encodeURIComponent(token)}; path=/; SameSite=Lax; Max-Age=3600`;
    localStorage.setItem("fa_token", token);
}

// ── Core fetch wrapper ──

async function apiFetch<T>(
    path: string,
    options: RequestInit = {},
    retryCount = 0
): Promise<T> {
    const token = getToken();
    const headers: Record<string, string> = {
        "Content-Type": "application/json",
        ...(options.headers as Record<string, string>),
    };
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    // Prevent doubling /api/v1 if it's already in the BASE_URL
    const cleanPath = (BASE_URL.endsWith("/api/v1") && path.startsWith("/api/v1"))
        ? path.replace("/api/v1", "")
        : path;

    const res = await fetch(`${BASE_URL}${cleanPath}`, {
        ...options,
        headers,
    });

    // 401 → clear token, redirect
    if (res.status === 401) {
        clearToken();
        if (typeof window !== "undefined") {
            window.location.href = "/login";
        }
        throw new ApiError(401, "UNAUTHORIZED", "Authentication required");
    }

    // 429 → rate limit
    if (res.status === 429) {
        const retryAfter = parseInt(res.headers.get("Retry-After") || "60", 10);
        throw new RateLimitError(retryAfter);
    }

    // 5xx → retry once
    if (res.status >= 500 && retryCount < 1) {
        await new Promise((r) => setTimeout(r, 1000));
        return apiFetch<T>(path, options, retryCount + 1);
    }

    if (!res.ok) {
        const body = await res.json().catch(() => ({ detail: "Unknown error" }));
        throw new ApiError(res.status, body.error_code || "UNKNOWN", body.detail || res.statusText);
    }

    return res.json() as Promise<T>;
}

// ── Typed API functions ──

export async function submitReport(req: ReportSubmitRequest): Promise<ReportSubmitResponse> {
    return apiFetch<ReportSubmitResponse>("/api/v1/reports", {
        method: "POST",
        body: JSON.stringify(req),
    });
}

export async function getReport(reportId: string): Promise<ReportDetail> {
    return apiFetch<ReportDetail>(`/api/v1/reports/${reportId}`);
}

export async function listReports(page = 1, perPage = 20): Promise<PaginatedReports> {
    return apiFetch<PaginatedReports>(`/api/v1/reports?page=${page}&per_page=${perPage}`);
}

export async function login(email: string, password: string): Promise<LoginResponse> {
    return apiFetch<LoginResponse>("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
    });
}

export async function signup(email: string, password: string): Promise<LoginResponse> {
    return apiFetch<LoginResponse>("/api/v1/auth/signup", {
        method: "POST",
        body: JSON.stringify({ email, password }),
    });
}
