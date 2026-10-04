import Link from "next/link";
import { ArrowUpRight, Boxes, Filter, Layers3, Search, UsersRound } from "lucide-react";
import { getProfile, requireUser } from "@/lib/auth";
import { WorkspaceNav } from "@/components/workspace-nav";

export const dynamic = "force-dynamic";

type SearchParams = Promise<{ q?: string; member?: string }>;
function amount(quantity: number, unit: string) { return `${quantity} ${quantity === 1 ? unit : `${unit}${unit === "piece" ? "s" : ""}`}`; }

export default async function ManagerPage({ searchParams }: { searchParams: SearchParams }) {
  const [{ q = "", member = "" }, context] = await Promise.all([searchParams, requireUser("/manager")]);
  const profile = await getProfile(context.supabase, context.user);
  if (profile?.role !== "MANAGER") return <main className="workspace-page"><WorkspaceNav profile={profile ?? { id: context.user.id, email: context.user.email ?? "", name: String(context.user.user_metadata?.name ?? "Member"), role: "MEMBER" }} section="member" /><div className="workspace-content access-denied"><span className="page-kicker">MANAGER VIEW</span><h1>This space is for managers.</h1><p>Your member account doesn’t have manager access yet.</p><Link href="/manager/setup" className="button button-primary">Set up manager access <ArrowUpRight size={16} /></Link></div></main>;

  const [{ data: allItems }, { data: profiles }, { data: messages }] = await Promise.all([
    context.supabase.from("request_items").select("id,message_id,user_id,name,quantity,unit,variant,created_at").order("created_at", { ascending: false }),
    context.supabase.from("profiles").select("id,name,email,role").order("name"),
    context.supabase.from("messages").select("id,original_text,created_at"),
  ]);
  const people = profiles ?? [];
  const personById = new Map(people.map((person) => [person.id, person]));
  const messageById = new Map((messages ?? []).map((entry) => [entry.id, entry.original_text]));
  const query = q.trim().toLowerCase();
  const rows = (allItems ?? []).filter((item) => {
    const who = personById.get(item.user_id);
    return (!member || item.user_id === member) && (!query || item.name.toLowerCase().includes(query) || (item.variant ?? "").toLowerCase().includes(query) || (who?.name ?? "").toLowerCase().includes(query));
  });
  const totals = new Map<string, { name: string; variant: string | null; unit: string; quantity: number; members: Set<string> }>();
  for (const item of rows) {
    const key = `${item.name.toLowerCase()}\u0000${(item.variant ?? "").toLowerCase()}\u0000${item.unit.toLowerCase()}`;
    const current = totals.get(key) ?? { name: item.name, variant: item.variant, unit: item.unit, quantity: 0, members: new Set<string>() };
    current.quantity += item.quantity;
    current.members.add(item.user_id);
    totals.set(key, current);
  }
  const aggregate = [...totals.values()].sort((a, b) => b.quantity - a.quantity);
  const memberCount = people.filter((person) => person.role !== "MANAGER").length;
  const totalUnits = rows.reduce((sum, item) => sum + item.quantity, 0);

  return <main className="workspace-page manager-page">
    <WorkspaceNav profile={profile} section="manager" />
    <div className="workspace-content manager-content">
      <div className="page-welcome"><div><span className="page-kicker">GROUP OVERVIEW</span><h1>The bigger picture.</h1><p>One clear view of what everyone is looking for.</p></div><span className="manager-chip"><span className="pulse-dot" /> MANAGER VIEW</span></div>
      <section className="manager-stats"><article className="manager-stat-card"><span className="manager-stat-icon"><UsersRound size={18} /></span><div><small>MEMBERS</small><strong>{memberCount}</strong><span>in the group</span></div></article><article className="manager-stat-card"><span className="manager-stat-icon mint"><Boxes size={18} /></span><div><small>ITEM LINES</small><strong>{rows.length}</strong><span>across the filtered list</span></div></article><article className="manager-stat-card"><span className="manager-stat-icon peach"><Layers3 size={18} /></span><div><small>GROUP QUANTITY</small><strong>{totalUnits}</strong><span>pieces requested</span></div></article></section>
      <section className="aggregate-panel"><div className="aggregate-head"><div><span className="section-kicker"><Layers3 size={14} /> BUILT FROM EVERYONE’S LIST</span><h2>Combined requirements</h2><p>Same item, same option, same unit — added together.</p></div><span className="live-label"><span className="pulse-dot" /> LIVE TOTALS</span></div>
        {aggregate.length === 0 ? <div className="aggregate-empty">No items match these filters yet.</div> : <div className="aggregate-grid">{aggregate.map((entry) => <article className="aggregate-card" key={`${entry.name}-${entry.variant}-${entry.unit}`}><span className="aggregate-icon"><Boxes size={18} /></span><div className="aggregate-copy"><strong>{entry.name}</strong><span>{entry.variant || "Standard"} · {entry.members.size} {entry.members.size === 1 ? "member" : "members"}</span></div><div className="aggregate-amount"><strong>{entry.quantity}</strong><span>{entry.quantity === 1 ? entry.unit : `${entry.unit}${entry.unit === "piece" ? "s" : ""}`}</span></div></article>)}</div>}
      </section>
      <section className="member-requests"><div className="list-heading"><div><span className="section-kicker">EVERYONE’S REQUESTS</span><h2>All member requirements <span className="count-pill">{rows.length}</span></h2></div><span className="private-label">MANAGER ACCESS</span></div>
        <form className="filter-bar" method="get"><label className="search-filter"><Search size={16} /><input name="q" defaultValue={q} placeholder="Search item, option or member" /></label><label className="member-filter"><Filter size={15} /><select name="member" defaultValue={member}><option value="">All members</option>{people.filter((person) => person.role !== "MANAGER").map((person) => <option value={person.id} key={person.id}>{person.name}</option>)}</select></label><button className="button button-dark button-small" type="submit">Filter</button>{(q || member) && <Link className="clear-filter" href="/manager">Clear</Link>}</form>
        <div className="table-wrap"><table className="requests-table"><thead><tr><th>MEMBER</th><th>ITEM</th><th>OPTION</th><th>QUANTITY</th><th>ADDED</th></tr></thead><tbody>{rows.map((item) => <tr key={item.id}><td><span className="table-person"><span className="avatar small-avatar">{(personById.get(item.user_id)?.name ?? "?").slice(0, 1).toUpperCase()}</span><span>{personById.get(item.user_id)?.name ?? "Member"}<small>{personById.get(item.user_id)?.email ?? ""}</small></span></span></td><td><strong className="table-item-name">{item.name}</strong><small className="source-text">“{messageById.get(item.message_id) ?? ""}”</small></td><td>{item.variant || "—"}</td><td><strong>{amount(item.quantity, item.unit)}</strong></td><td>{new Date(item.created_at).toLocaleDateString("en", { month: "short", day: "numeric" })}</td></tr>)}</tbody></table>{rows.length === 0 && <div className="table-empty">No requirements yet. Member requests will appear here.</div>}</div>
      </section>
    </div>
  </main>;
}
