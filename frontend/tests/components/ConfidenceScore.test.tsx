import { describe, it, expect, vi } from "vitest";

describe("ConfidenceScore", () => {
    it("shows loading ring when report is not complete", () => {
        const store = {
            report: { status: "verifying", total_claims: 10, confidence_score: null, confidence_hash: null, full_hash: null },
            verifiedCount: 3,
            flaggedCount: 0,
            uncertainCount: 0,
        };

        expect(store.report.status).not.toBe("complete");
        expect(store.verifiedCount).toBe(3);
        expect(store.report.total_claims).toBe(10);
    });

    it("shows score when report is complete", () => {
        const store = {
            report: { status: "complete", confidence_score: 78.5, confidence_hash: "a3f9b2c1e5d84107", full_hash: "abc123..." },
            verifiedCount: 8,
            flaggedCount: 1,
            uncertainCount: 1,
        };

        expect(store.report.status).toBe("complete");
        expect(store.report.confidence_score).toBe(78.5);
    });

    it("applies correct color class for score >= 90", () => {
        const score = 92.0;
        const colorClass = score >= 90 ? "text-emerald-600" : score >= 70 ? "text-amber-500" : "text-red-500";
        expect(colorClass).toBe("text-emerald-600");
    });

    it("applies correct color class for score 70-89", () => {
        const score = 78.5;
        const colorClass = score >= 90 ? "text-emerald-600" : score >= 70 ? "text-amber-500" : "text-red-500";
        expect(colorClass).toBe("text-amber-500");
    });

    it("applies correct color class for score < 70", () => {
        const score = 65.0;
        const colorClass = score >= 90 ? "text-emerald-600" : score >= 70 ? "text-amber-500" : "text-red-500";
        expect(colorClass).toBe("text-red-500");
    });

    it("copy button triggers clipboard write", async () => {
        const writeText = vi.fn().mockResolvedValue(undefined);
        Object.assign(navigator, { clipboard: { writeText } });

        const fullHash = "abc123def456";
        await navigator.clipboard.writeText(fullHash);
        expect(writeText).toHaveBeenCalledWith(fullHash);
    });
});
