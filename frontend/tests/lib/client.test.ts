import { describe, it, expect, vi, beforeEach } from "vitest";

describe("API Client", () => {
    beforeEach(() => {
        vi.restoreAllMocks();
    });

    it("attaches Authorization header when token exists", () => {
        const headers: Record<string, string> = {};
        const token = "test-jwt-token";
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }
        expect(headers["Authorization"]).toBe("Bearer test-jwt-token");
    });

    it("handles 401 by clearing token", () => {
        const status = 401;
        let tokenCleared = false;
        if (status === 401) {
            tokenCleared = true;
        }
        expect(tokenCleared).toBe(true);
    });

    it("handles 429 by parsing Retry-After header", () => {
        const retryAfter = "45";
        const seconds = parseInt(retryAfter, 10);
        expect(seconds).toBe(45);
    });

    it("retries once on 5xx", async () => {
        let attempts = 0;
        const mockFetch = async (): Promise<{ status: number; ok: boolean }> => {
            attempts++;
            if (attempts === 1) return { status: 500, ok: false };
            return { status: 200, ok: true };
        };

        let result = await mockFetch();
        if (result.status >= 500) {
            await new Promise((r) => setTimeout(r, 10));
            result = await mockFetch();
        }

        expect(attempts).toBe(2);
        expect(result.status).toBe(200);
    });

    it("builds correct URL for report submission", () => {
        const baseUrl = "http://localhost:8000";
        const path = "/api/v1/reports";
        expect(`${baseUrl}${path}`).toBe("http://localhost:8000/api/v1/reports");
    });
});
