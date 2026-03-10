import React from "react";
import { cookies } from "next/headers";
import { notFound, redirect } from "next/navigation";
import { getReportServer } from "@/lib/api/server";
import { VerificationStream } from "@/components/report/VerificationStream";
import { Navbar } from "@/components/layout/Navbar";

interface ReportPageProps {
    params: { id: string };
}

export async function generateMetadata({ params }: ReportPageProps) {
    const { id } = params;
    try {
        const cookieStore = cookies();
        const token = cookieStore.get("fa_token")?.value;
        if (!token) return { title: `Report ${id.slice(0, 8)}` };
        const report = await getReportServer(id, token);
        return { title: report.title ?? `Report ${id.slice(0, 8)}` };
    } catch {
        return { title: `Report ${id.slice(0, 8)}` };
    }
}

export default async function ReportPage({ params }: ReportPageProps) {
    const { id } = params;
    const cookieStore = cookies();
    const token = cookieStore.get("fa_token")?.value;

    if (!token) {
        redirect("/login");
    }

    let report;
    try {
        report = await getReportServer(id, token);
    } catch (e: unknown) {
        const err = e as { message?: string };
        if (err.message?.includes("403")) {
            redirect("/login");
        }
        notFound();
    }

    return (
        <>
            <Navbar />
            <VerificationStream reportId={id} initialReport={report} />
        </>
    );
}
