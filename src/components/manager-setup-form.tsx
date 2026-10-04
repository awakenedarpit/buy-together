"use client";

import { useActionState } from "react";
import { KeyRound, ShieldCheck } from "lucide-react";
import { setupManager, type ManagerSetupState } from "@/app/actions/manager";

export function ManagerSetupForm() {
  const [state, formAction, pending] = useActionState<ManagerSetupState, FormData>(setupManager, undefined);
  return <form action={formAction} className="setup-form">
    <div className="setup-icon"><ShieldCheck size={20} /></div>
    <div><strong>Set up a manager account</strong><p>Sign in to the account you want to promote, then enter the private setup key provided by the project owner.</p></div>
    <label className="field"><span>Manager setup key</span><div className="password-field"><KeyRound size={16} /><input type="password" name="setupSecret" autoComplete="off" maxLength={256} required placeholder="Your private setup key" /></div></label>
    {state?.message && <p className={state.success ? "form-alert success" : "form-alert error"} role="status">{state.message}</p>}
    <button type="submit" className="button button-primary" disabled={pending}>{pending ? "Verifying…" : "Activate manager access"}</button>
  </form>;
}
