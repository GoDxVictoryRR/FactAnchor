"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { signup } from "@/lib/api/client";
import { useAuth } from "@/lib/hooks/useAuth";
import { Button } from "@/components/ui/Button";
import { Shield, Check, X, AlertCircle } from "lucide-react";

export default function SignupPage() {
    const router = useRouter();
    const { saveToken } = useAuth();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const validatePassword = (pass: string) => {
        const checks = {
            length: pass.length >= 8,
            number: /\d/.test(pass),
            special: /[^A-Za-z0-9]/.test(pass),
        };
        return checks;
    };

    const passwordChecks = validatePassword(password);
    const isPasswordValid = Object.values(passwordChecks).every(Boolean);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        if (!isPasswordValid) {
            setError("Password does not meet requirements.");
            return;
        }

        if (password !== confirmPassword) {
            setError("Passwords do not match.");
            return;
        }

        setLoading(true);
        try {
            const res = await signup(email, password);
            saveToken(res.access_token);
            router.push("/");
        } catch (err: any) {
            setError(err.message || "Signup failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center px-4 relative bg-[#020617]">
            {/* Ambient Background Elements */}
            <div className="absolute top-1/4 -left-20 w-96 h-96 bg-blue-600/10 rounded-full blur-[120px]" />
            <div className="absolute bottom-1/4 -right-20 w-96 h-96 bg-emerald-600/10 rounded-full blur-[120px]" />

            <div className="w-full max-w-md glass-card p-8 shadow-[0_20px_50px_rgba(0,0,0,0.5)] border-white/10 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500/50 via-indigo-500/50 to-emerald-500/50" />

                <div className="flex flex-col items-center mb-8">
                    <div className="p-3 bg-blue-500/10 rounded-full mb-4 border border-blue-500/20">
                        <Shield size={32} className="text-blue-400" />
                    </div>
                    <h1 className="text-2xl font-bold text-white tracking-tight">Create Account</h1>
                    <p className="text-sm text-gray-400 mt-2 font-medium">Join the Enterprise Trust Protocol</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div>
                        <label htmlFor="email" className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2 px-1">Email Address</label>
                        <input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            placeholder="name@company.com"
                            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:ring-1 focus:ring-blue-500/50 transition-all hover:bg-white/[0.07]"
                        />
                    </div>

                    <div className="space-y-3">
                        <label htmlFor="password" className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2 px-1">Password</label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            placeholder="••••••••"
                            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:ring-1 focus:ring-blue-500/50 transition-all hover:bg-white/[0.07]"
                        />

                        {/* Password Requirements Checklist */}
                        <div className="grid grid-cols-1 gap-2 mt-2 px-1">
                            <div className="flex items-center space-x-2">
                                {passwordChecks.length ? <Check size={12} className="text-emerald-400" /> : <AlertCircle size={12} className="text-gray-600" />}
                                <span className={`text-[10px] uppercase tracking-wider font-bold ${passwordChecks.length ? 'text-emerald-400/80' : 'text-gray-600'}`}>Min 8 Characters</span>
                            </div>
                            <div className="flex items-center space-x-2">
                                {passwordChecks.number ? <Check size={12} className="text-emerald-400" /> : <AlertCircle size={12} className="text-gray-600" />}
                                <span className={`text-[10px] uppercase tracking-wider font-bold ${passwordChecks.number ? 'text-emerald-400/80' : 'text-gray-600'}`}>Include a Number</span>
                            </div>
                            <div className="flex items-center space-x-2">
                                {passwordChecks.special ? <Check size={12} className="text-emerald-400" /> : <AlertCircle size={12} className="text-gray-600" />}
                                <span className={`text-[10px] uppercase tracking-wider font-bold ${passwordChecks.special ? 'text-emerald-400/80' : 'text-gray-600'}`}>Special Character</span>
                            </div>
                        </div>
                    </div>

                    <div>
                        <label htmlFor="confirmPassword" className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2 px-1">Confirm Password</label>
                        <input
                            id="confirmPassword"
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                            placeholder="••••••••"
                            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:ring-1 focus:ring-blue-500/50 transition-all hover:bg-white/[0.07]"
                        />
                    </div>

                    {error && (
                        <div className="text-xs font-bold uppercase tracking-tight text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3 flex items-center space-x-2">
                            <X size={14} />
                            <span>{error}</span>
                        </div>
                    )}

                    <Button
                        type="submit"
                        loading={loading}
                        size="lg"
                        disabled={!isPasswordValid || password !== confirmPassword}
                        className="w-full bg-blue-600 hover:bg-blue-500 text-white border-none shadow-lg shadow-blue-900/20 mt-2 font-bold uppercase tracking-widest text-[11px]"
                    >
                        Initialize Identity
                    </Button>
                </form>

                <div className="mt-8 pt-6 border-t border-white/5 text-center">
                    <p className="text-[11px] text-gray-500 font-medium">
                        Already registered?
                        <Link href="/login" className="text-blue-400 hover:text-blue-300 ml-1 transition-colors font-bold uppercase tracking-tighter">Sign In</Link>
                    </p>
                </div>
            </div>
        </div>
    );
}
