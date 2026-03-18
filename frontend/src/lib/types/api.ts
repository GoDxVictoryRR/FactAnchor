// ── Report submission ──

export interface ReportSubmitRequest {
    text: string;
    title?: string;
}

export interface ReportSubmitResponse {
    report_id: string;
    total_claims: number;
    ws_url: string;
}

// ── Enums ──

export type ClaimStatus = "pending" | "verified" | "flagged" | "uncertain" | "error";
export type ClaimType = "quantitative" | "qualitative";
export type ReportStatus = "pending" | "extracting" | "verifying" | "complete" | "failed";

// ── Report detail ──

export interface Claim {
    id: string;
    sequence_num: number;
    claim_text: string;
    claim_type: ClaimType;
    status: ClaimStatus;
    char_start: number;
    char_end: number;
    db_expected_value: string | null;
    llm_generated_sql: string | null;
    similarity_score: number | null;
    verified_at: string | null;
}

export interface ReportDetail {
    id: string;
    title: string | null;
    raw_text: string;
    status: ReportStatus;
    confidence_score: number | null;
    confidence_hash: string | null;
    full_hash: string | null;
    total_claims: number;
    verified_count: number;
    flagged_count: number;
    uncertain_count: number;
    claims: Claim[];
    created_at: string;
}

export interface ReportSummary {
    id: string;
    title: string | null;
    status: ReportStatus;
    confidence_score: number | null;
    total_claims: number;
    flagged_count: number;
    created_at: string;
}

export interface PaginatedReports {
    items: ReportSummary[];
    total: number;
    page: number;
    per_page: number;
}

// ── WebSocket messages ──

export type WSMessage =
    | { type: "claim_update"; claim_id: string; status: ClaimStatus; sequence_num: number }
    | { type: "report_complete"; confidence_score: number; anchor: string }
    | { type: "error"; code: string; message: string };

// ── Auth ──

export interface LoginResponse {
    access_token: string;
}
