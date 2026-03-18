import type { ReportDetail, PaginatedReports } from "@/lib/types/api";

const INTERNAL_URL = process.env.API_INTERNAL_URL || "http://localhost:8000";

async function serverFetch<T>(path: string, token: string): Promise<T> {
    const res = await fetch(`${INTERNAL_URL}${path}`, {
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },
        cache: "no-store",
    });

    if (!res.ok) {
        throw new Error(`Server fetch failed: ${res.status} ${res.statusText}`);
    }

    return res.json() as Promise<T>;
}

export async function getReportServer(
    reportId: string,
    token: string
): Promise<ReportDetail> {
    return serverFetch<ReportDetail>(`/api/v1/reports/${reportId}`, token);
}

export async function listReportsServer(
    token: string,
    page = 1
): Promise<PaginatedReports> {
    return serverFetch<PaginatedReports>(`/api/v1/reports?page=${page}`, token);
}
