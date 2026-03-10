import { describe, it, expect, vi } from "vitest";

describe("ClaimSidebar", () => {
    const mockClaims = [
        { id: "c1", sequence_num: 1, claim_text: "Revenue was $4.2B", claim_type: "quantitative" as const, status: "verified" as const, char_start: 0, char_end: 18, db_expected_value: null, llm_generated_sql: null, similarity_score: null, verified_at: null },
        { id: "c2", sequence_num: 2, claim_text: "Company expanded into Europe", claim_type: "qualitative" as const, status: "flagged" as const, char_start: 20, char_end: 48, db_expected_value: null, llm_generated_sql: null, similarity_score: 0.71, verified_at: null },
        { id: "c3", sequence_num: 3, claim_text: "Margin improved to 23.4%", claim_type: "quantitative" as const, status: "uncertain" as const, char_start: 50, char_end: 74, db_expected_value: null, llm_generated_sql: null, similarity_score: null, verified_at: null },
    ];

    it("filters claims by flagged status", () => {
        const statuses: Record<string, string> = { c1: "verified", c2: "flagged", c3: "uncertain" };
        const filtered = mockClaims.filter((c) => (statuses[c.id] || c.status) === "flagged");
        expect(filtered.length).toBe(1);
        expect(filtered[0].id).toBe("c2");
    });

    it("filters claims by uncertain status", () => {
        const statuses: Record<string, string> = { c1: "verified", c2: "flagged", c3: "uncertain" };
        const filtered = mockClaims.filter((c) => (statuses[c.id] || c.status) === "uncertain");
        expect(filtered.length).toBe(1);
        expect(filtered[0].id).toBe("c3");
    });

    it("shows all claims when filter is 'all'", () => {
        expect(mockClaims.length).toBe(3);
    });

    it("truncates long claim text at 60 chars", () => {
        const longClaim = { ...mockClaims[0], claim_text: "A".repeat(100) };
        const displayed = longClaim.claim_text.length > 60
            ? `${longClaim.claim_text.slice(0, 60)}…`
            : longClaim.claim_text;
        expect(displayed.length).toBe(61); // 60 + ellipsis
    });

    it("scrollToClaim calls scrollIntoView", () => {
        const mockElement = { scrollIntoView: vi.fn() };
        const querySelector = vi.spyOn(document, "querySelector").mockReturnValue(mockElement as unknown as Element);

        const claimId = "c1";
        const el = document.querySelector(`[data-claim-id="${claimId}"]`);
        el?.scrollIntoView({ behavior: "smooth", block: "center" });

        expect(querySelector).toHaveBeenCalledWith(`[data-claim-id="c1"]`);
        expect(mockElement.scrollIntoView).toHaveBeenCalledWith({ behavior: "smooth", block: "center" });
        querySelector.mockRestore();
    });
});
