import Link from "next/link";
import { ArrowUpRight, Boxes, LayoutDashboard, LogOut, ShieldCheck, Sparkles } from "lucide-react";
import { logout } from "@/app/actions/auth";
import type { UserProfile } from "@/lib/auth";

export function WorkspaceNav({ profile, section }: { profile: UserProfile; section: "member" | "manager" }) {
  const isManager = profile.role === "MANAGER";
  return (
    <header className="workspace-nav">
      <Link href={isManager ? "/manager" : "/dashboard"} className="brand-lockup" aria-label="Buy Together home">
        <span className="brand-icon"><Boxes size={20} strokeWidth={2.4} /></span>
        <span className="brand-name">buy<span>together</span></span>
      </Link>
      <nav className="workspace-links" aria-label="Main navigation">
        <Link className={section === "member" ? "workspace-link active" : "workspace-link"} href="/dashboard"><LayoutDashboard size={16} /> My list</Link>
        {isManager && <Link className={section === "manager" ? "workspace-link active" : "workspace-link"} href="/manager"><ShieldCheck size={16} /> Manager</Link>}
      </nav>
      <div className="workspace-user">
        <div className="avatar">{(profile.name || profile.email || "M").slice(0, 1).toUpperCase()}</div>
        <div className="user-copy"><strong>{profile.name}</strong><span>{isManager ? "Manager" : "Member"}</span></div>
        <form action={logout}><button className="icon-button logout-button" type="submit" aria-label="Sign out" title="Sign out"><LogOut size={17} /></button></form>
      </div>
    </header>
  );
}

export function BrandMark({ light = false }: { light?: boolean }) {
  return <Link href="/" className={`brand-lockup ${light ? "brand-light" : ""}`}><span className="brand-icon"><Boxes size={20} strokeWidth={2.4} /></span><span className="brand-name">buy<span>together</span></span></Link>;
}

export function Eyebrow({ children }: { children: React.ReactNode }) {
  return <span className="eyebrow"><Sparkles size={13} /> {children}<ArrowUpRight size={13} /></span>;
}
