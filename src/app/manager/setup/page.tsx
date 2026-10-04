import Link from "next/link";
import { ArrowLeft, KeyRound, ShieldCheck } from "lucide-react";
import { ManagerSetupForm } from "@/components/manager-setup-form";
import { getProfile, requireUser } from "@/lib/auth";
import { WorkspaceNav } from "@/components/workspace-nav";

export const dynamic = "force-dynamic";
export const metadata = { title: "Manager setup" };

export default async function ManagerSetupPage() {
  const { supabase, user } = await requireUser("/manager/setup");
  const profile = await getProfile(supabase, user);
  const currentProfile = profile ?? { id: user.id, email: user.email ?? "", name: String(user.user_metadata?.name ?? "Member"), role: "MEMBER" as const };
  if (currentProfile.role === "MANAGER") return <main className="workspace-page"><WorkspaceNav profile={currentProfile} section="member" /><div className="workspace-content setup-page"><div className="setup-card"><div className="setup-card-icon"><ShieldCheck size={24} /></div><span className="page-kicker">ALREADY SET UP</span><h1>You have manager access.</h1><p>Your account can already view all group requirements and totals.</p><Link href="/manager" className="button button-primary">Go to manager dashboard <ArrowLeft size={15} className="arrow-flip" /></Link></div></div></main>;
  return <main className="workspace-page"><WorkspaceNav profile={currentProfile} section="member" /><div className="workspace-content setup-page"><div className="setup-card"><div className="setup-card-icon"><KeyRound size={24} /></div><span className="page-kicker">DEMO ADMINISTRATION</span><h1>Manager setup.</h1><p>Promote this signed-in account using the private manager setup key configured by the project owner.</p><ManagerSetupForm /><Link href="/dashboard" className="back-to-list"><ArrowLeft size={14} /> Back to my list</Link><div className="setup-footnote"><ShieldCheck size={15} /> The setup key and service-role credential are verified on the server and never sent to the browser.</div></div></div></main>;
}
