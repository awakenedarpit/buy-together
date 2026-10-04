"use client";

import { useActionState } from "react";
import { ArrowUpRight, Sparkles } from "lucide-react";
import { addRequirements, type RequirementState } from "@/app/actions/requirements";

export function RequirementForm() {
  const [state, formAction, pending] = useActionState<RequirementState, FormData>(addRequirements, undefined);
  return (
    <form action={formAction} className="composer-form">
      <label className="sr-only" htmlFor="requirements">What do you need?</label>
      <textarea id="requirements" name="message" placeholder="bhai 2 notebook aur ek blue pen" maxLength={1000} required rows={3} />
      <div className="composer-footer">
        <span className="composer-hint"><Sparkles size={14} /> English or Hinglish — just say it naturally</span>
        <button className="button button-primary" type="submit" disabled={pending}>{pending ? "Finding items…" : "Add requirements"}<ArrowUpRight size={16} /></button>
      </div>
      {state?.message && <p className={state.success ? "form-alert success" : "form-alert error"} role="status">{state.message}</p>}
    </form>
  );
}
