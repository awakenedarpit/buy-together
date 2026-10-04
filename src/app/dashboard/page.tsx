import Link from "next/link";
import { ArrowUpRight, ClipboardList, PackageCheck, Plus, ShieldCheck } from "lucide-react";
import { getProfile, requireUser, type UserProfile } from "@/lib/auth";
import { hasSupabaseConfig } from "@/lib/supabase/server";
import { RequirementForm } from "@/components/requirement-form";
import { RequirementItem, type RequirementItemView } from "@/components/requirement-item";
import { WorkspaceNav } from "@/components/workspace-nav";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const { supabase, user } = await requireUser();
  const fromDb = await getProfile(supabase, user);
  const profile: UserProfile = fromDb ?? { id: user.id, email: user.email ?? "", name: String(user.user_metadata?.name ?? "Member"), role: "MEMBER" };
  const [{ data: items }, { data: messages }] = await Promise.all([
    supabase.from("request_items").select("id,message_id,name,quantity,unit,variant,created_at").eq("user_id", user.id).order("created_at", { ascending: false }),
    supabase.from("messages").select("id,original_text,created_at").eq("user_id", user.id).order("created_at", { ascending: false }).limit(5),
  ]);
  const requirements = (items ?? []) as RequirementItemView[];
  const messageMap = new Map((messages ?? []).map((message) => [message.id, message]));
  const totalUnits = requirements.reduce((sum, item) => sum + item.quantity, 0);
  const isReady = hasSupabaseConfig();

  return <main className="workspace-page">
    <WorkspaceNav profile={profile} section="member" />
    <div className="workspace-content">
      <div className="page-welcome"><div><span className="page-kicker">YOUR SHARED LIST</span><h1>Good to see you, {profile.name.split(" ")[0]}.</h1><p>What can we add to the group list today?</p></div><span className="date-chip">{new Date().toLocaleDateString("en", { weekday: "short", month: "short", day: "numeric" })}</span></div>
      {!isReady && <div className="config-notice"><strong>Database setup needed.</strong> Add the Supabase settings and apply <code>supabase/schema.sql</code> to enable account data, saving, and sharing.</div>}
      <section className="composer-panel"><div className="panel-heading"><div><span className="section-kicker"><Plus size={14} /> ADD TO YOUR LIST</span><h2>What do you need?</h2><p>Say it naturally. We’ll take care of the tidy-up.</p></div><div className="ai-badge"><span className="pulse-dot" /> AI ready</div></div><RequirementForm /></section>
      <section className="summary-stats"><article className="stat-card"><div className="stat-icon stat-violet"><ClipboardList size={18} /></div><div><span>Items in your list</span><strong>{requirements.length}</strong></div></article><article className="stat-card"><div className="stat-icon stat-mint"><PackageCheck size={18} /></div><div><span>Total pieces requested</span><strong>{totalUnits}</strong></div></article><article className="stat-card manager-stat"><div className="stat-icon stat-sand"><ShieldCheck size={18} /></div><div><span>Buying as a group</span><strong>{profile.role === "MANAGER" ? "Manager" : "Member"}</strong></div>{profile.role === "MANAGER" ? <Link href="/manager" aria-label="Open manager dashboard"><ArrowUpRight size={17} /></Link> : <Link href="/manager/setup" aria-label="Open manager setup"><ArrowUpRight size={17} /></Link>}</article></section>
      <section className="list-section"><div className="list-heading"><div><span className="section-kicker">YOUR REQUESTS</span><h2>Items you’ve added <span className="count-pill">{requirements.length}</span></h2></div><span className="private-label">PRIVATE TO YOU</span></div>
        {!isReady ? <div className="empty-state"><div className="empty-illustration"><ClipboardList size={26} /></div><h3>Connect your list</h3><p>Your own requirements will appear here after Supabase is configured.</p></div> : requirements.length === 0 ? <div className="empty-state"><div className="empty-illustration"><ClipboardList size={26} /></div><h3>Your list starts here</h3><p>Add your first requirement above. Every item stays connected to your account.</p></div> : <div className="items-list">{requirements.map((item) => <div key={item.id}><RequirementItem item={item} />{messageMap.get(item.message_id) && <p className="item-source">From: “{messageMap.get(item.message_id)?.original_text}”</p>}</div>)}</div>}
      </section>
      {profile.role !== "MANAGER" && <p className="manager-footnote">Setting up the demo? <Link href="/manager/setup">Activate a manager account <ArrowUpRight size={13} /></Link></p>}
    </div>
  </main>;
}
