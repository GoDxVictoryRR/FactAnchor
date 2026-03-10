"use client";

import React from "react";
import Link from "next/link";
import { useAuth } from "@/lib/hooks/useAuth";
import { Shield, LogOut } from "lucide-react";

export function Navbar() {
    const { isAuthenticated, logout } = useAuth();

    return (
        <header className="bg-white/5 backdrop-blur-md border-b border-white/10 sticky top-0 z-40 transition-all">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    <Link href="/" className="flex items-center gap-3 group">
                        <div className="p-1.5 bg-blue-500/10 rounded-lg group-hover:bg-blue-500/20 transition-all border border-blue-500/10 group-hover:border-blue-500/30 shadow-lg shadow-blue-900/10">
                            <Shield size={20} className="text-blue-400" />
                        </div>
                        <span className="text-xl font-bold text-white tracking-tight group-hover:text-blue-200 transition-colors">
                            FactAnchor
                        </span>
                    </Link>

                    <nav className="flex items-center gap-6">
                        {isAuthenticated() ? (
                            <div className="flex items-center gap-4">
                                <div className="hidden sm:flex flex-col items-end mr-2">
                                    <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest leading-none mb-1">Authenticated Identity</span>
                                    <span className="text-xs font-medium text-blue-400/80 tracking-tight leading-none truncate max-w-[150px]">
                                        {/* Since user email isn't in store yet, we can try to get it from JWT sub or a hook */}
                                        {/* For now, generic placeholder or hook-based email */}
                                        Secure Operator
                                    </span>
                                </div>
                                <div className="h-8 w-px bg-white/10 hidden sm:block" />
                                <button
                                    onClick={logout}
                                    className="flex items-center gap-2 text-sm font-medium text-gray-400 hover:text-white transition-all bg-white/5 hover:bg-white/10 border border-white/5 px-3 py-1.5 rounded-lg group shadow-sm shadow-black"
                                >
                                    <LogOut size={14} className="group-hover:-translate-x-0.5 transition-transform" />
                                    <span className="hidden xs:block font-bold uppercase tracking-tighter text-[11px]">Terminate Session</span>
                                </button>
                            </div>
                        ) : (
                            <Link
                                href="/login"
                                className="text-sm font-bold text-blue-400 hover:text-blue-300 transition-all uppercase tracking-widest bg-blue-400/10 px-4 py-2 rounded-lg border border-blue-400/20 hover:border-blue-400/40"
                            >
                                Verify Identity
                            </Link>
                        )}
                    </nav>
                </div>
            </div>
        </header>
    );
}
