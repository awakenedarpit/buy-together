"use client";

import Link from "next/link";
import { useActionState } from "react";
import { ArrowRight, LockKeyhole } from "lucide-react";
import { login, register, type AuthState } from "@/app/actions/auth";

export function AuthForm({ mode, next = "/dashboard" }: { mode: "login" | "register"; next?: string }) {
  const action = mode === "login" ? login : register;
  const [state, formAction, pending] = useActionState<AuthState, FormData>(action, undefined);
  const isRegister = mode === "register";
  return (
    <form action={formAction} className="auth-form">
      {isRegister && <label className="field"><span>Your name</span><input name="name" autoComplete="name" placeholder="e.g. Arpit Sharma" minLength={2} maxLength={80} required /><small>This is how you’ll appear in the group list.</small></label>}
      <label className="field"><span>Email address</span><input name="email" type="email" autoComplete="email" placeholder="you@example.com" required /></label>
      <label className="field"><span>Password</span><div className="password-field"><LockKeyhole size={16} /><input name="password" type="password" autoComplete={isRegister ? "new-password" : "current-password"} placeholder={isRegister ? "At least 8 characters" : "Your password"} minLength={isRegister ? 8 : 1} maxLength={128} required /></div></label>
      <input type="hidden" name="next" value={next} />
      {state?.message && <p className={state.success ? "form-alert success" : "form-alert error"} role="status">{state.message}</p>}
      <button className="button button-primary button-wide" disabled={pending} type="submit">{pending ? "One moment…" : isRegister ? "Create your account" : "Sign in"}<ArrowRight size={17} /></button>
      <p className="auth-switch">{isRegister ? "Already part of the group?" : "New to buying together?"} <Link href={isRegister ? "/login" : "/register"}>{isRegister ? "Sign in" : "Create an account"}</Link></p>
    </form>
  );
}
