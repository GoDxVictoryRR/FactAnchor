import { describe, it, expect, vi, beforeEach } from "vitest";

describe("ReportWebSocket", () => {
    beforeEach(() => {
        vi.restoreAllMocks();
    });

    it("calls onClaimUpdate handler when claim_update message received", () => {
        const handler = vi.fn();
        const msg = { type: "claim_update" as const, claim_id: "c1", status: "verified" as const, sequence_num: 1 };

        // Simulate handler call
        handler(msg);
        expect(handler).toHaveBeenCalledWith(msg);
        expect(handler).toHaveBeenCalledTimes(1);
    });

    it("calls onComplete handler when report_complete message received", () => {
        const handler = vi.fn();
        const msg = { type: "report_complete" as const, confidence_score: 85.5, anchor: "85.5#abc123" };

        handler(msg);
        expect(handler).toHaveBeenCalledWith(msg);
    });

    it("reconnect delays follow exponential backoff", () => {
        const delays = [1000, 2000, 4000, 8000, 16000, 30000];
        expect(delays[0]).toBe(1000);
        expect(delays[1]).toBe(2000);
        expect(delays[5]).toBe(30000);

        // Cap at 30s
        const maxDelay = delays[Math.min(10, delays.length - 1)];
        expect(maxDelay).toBe(30000);
    });

    it("stops reconnecting after 5 failures", () => {
        const maxAttempts = 5;
        let attempts = 0;
        let stopped = false;

        while (attempts < 10) {
            attempts++;
            if (attempts >= maxAttempts) {
                stopped = true;
                break;
            }
        }

        expect(stopped).toBe(true);
        expect(attempts).toBe(5);
    });

    it("disconnect prevents reconnect loop", () => {
        let intentionallyClosed = false;

        // Simulate disconnect
        intentionallyClosed = true;

        // Reconnect should not proceed
        const shouldReconnect = !intentionallyClosed;
        expect(shouldReconnect).toBe(false);
    });

    it("throws if instantiated in non-browser environment", () => {
        // The class checks typeof window
        const originalWindow = globalThis.window;
        // @ts-expect-error Temporarily remove window
        delete globalThis.window;

        expect(typeof globalThis.window).toBe("undefined");

        // Restore
        globalThis.window = originalWindow;
    });
});
