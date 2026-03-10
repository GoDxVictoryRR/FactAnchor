"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { login } from "@/lib/api/client";
import { useAuth } from "@/lib/hooks/useAuth";
import { Button } from "@/components/ui/Button";
import { Shield } from "lucide-react";

export default function LoginPage() {
    const router = useRouter();
    const { saveToken } = useAuth();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const res = await login(email, password);
            saveToken(res.access_token);
            router.push("/");
        } catch {
            setError("Invalid email or password.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center px-4 relative">
            <div className="w-full max-w-sm glass-card p-8 shadow-[0_20px_50px_rgba(0,0,0,0.5)] border-white/20">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500/50 to-emerald-500/50" />

                <div className="flex flex-col items-center mb-8">
                    <div className="p-3 bg-blue-500/10 rounded-full mb-4 border border-blue-500/20">
                        <Shield size={32} className="text-blue-400" />
                    </div>
                    <h1 className="text-2xl font-bold text-white tracking-tight">FactAnchor</h1>
                    <p className="text-sm text-gray-400 mt-2 font-medium">Enterprise Trust Protocol</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div>
                        <label htmlFor="email" className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Email Address</label>
                        <input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            placeholder="name@company.com"
                            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:ring-1 focus:ring-blue-500/50 transition-all"
                        />
                    </div>

                    <div>
                        <label htmlFor="password" className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Password</label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            placeholder="••••••••"
                            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:ring-1 focus:ring-blue-500/50 transition-all"
                        />
                    </div>

                    {error && (
                        <div className="text-xs font-medium text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3 animate-shake">
                            {error}
                        </div>
                    )}

                    <Button type="submit" loading={loading} size="lg" className="w-full bg-blue-600 hover:bg-blue-500 text-white border-none shadow-lg shadow-blue-900/20 mt-2">
                        Sign In
                    </Button>
                </form>

                <div className="mt-8 pt-6 border-t border-white/5 text-center">
                    <p className="text-[11px] text-gray-500 font-medium">
                        New to FactAnchor?
                        <Link href="/signup" className="text-blue-400 hover:text-blue-300 ml-1 transition-colors font-bold uppercase tracking-tighter">Initialize Identity</Link>
                    </p>
                </div>
            </div>
        </div>
    );
}
