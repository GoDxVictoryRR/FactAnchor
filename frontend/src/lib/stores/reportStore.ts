import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import type { ReportDetail, ClaimStatus } from "@/lib/types/api";

interface ReportStore {
    report: ReportDetail | null;
    claimStatuses: Record<string, ClaimStatus>;
    verifiedCount: number;
    flaggedCount: number;
    uncertainCount: number;

    setReport: (report: ReportDetail) => void;
    updateClaimStatus: (claimId: string, status: ClaimStatus) => void;
    setComplete: (confidenceScore: number, anchor: string) => void;
    reset: () => void;
}

export const useReportStore = create<ReportStore>()(
    immer((set) => ({
        report: null,
        claimStatuses: {},
        verifiedCount: 0,
        flaggedCount: 0,
        uncertainCount: 0,

        setReport: (report: ReportDetail) =>
            set((state) => {
                state.report = report;
                state.verifiedCount = report.verified_count;
                state.flaggedCount = report.flagged_count;
                state.uncertainCount = report.uncertain_count;
                // Initialize claim statuses from the report
                state.claimStatuses = {};
                for (const claim of report.claims) {
                    state.claimStatuses[claim.id] = claim.status;
                }
            }),

        updateClaimStatus: (claimId: string, status: ClaimStatus) =>
            set((state) => {
                const prev = state.claimStatuses[claimId];
                state.claimStatuses[claimId] = status;

                // Decrement previous counter
                if (prev === "verified") state.verifiedCount--;
                else if (prev === "flagged") state.flaggedCount--;
                else if (prev === "uncertain") state.uncertainCount--;

                // Increment new counter
                if (status === "verified") state.verifiedCount++;
                else if (status === "flagged") state.flaggedCount++;
                else if (status === "uncertain") state.uncertainCount++;
            }),

        setComplete: (confidenceScore: number, anchor: string) =>
            set((state) => {
                if (state.report) {
                    state.report.status = "complete";
                    state.report.confidence_score = confidenceScore;
                    state.report.confidence_hash = anchor.split("#")[1] || anchor;
                }
            }),

        reset: () =>
            set((state) => {
                state.report = null;
                state.claimStatuses = {};
                state.verifiedCount = 0;
                state.flaggedCount = 0;
                state.uncertainCount = 0;
            }),
    }))
);
