import Link from "next/link";
import { ArrowLeft, ShieldCheck } from "lucide-react";
import { AuthForm } from "@/components/auth-form";
import { BrandMark } from "@/components/workspace-nav";

export const metadata = { title: "Sign in" };

type SearchParams = Promise<{ next?: string }>;
export default async function LoginPage({ searchParams }: { searchParams: SearchParams }) {
  const { next } = await searchParams;
  const safeNext = next && next.startsWith("/") && !next.startsWith("//") ? next : "/dashboard";
  return <main className="auth-page"><div className="auth-decoration auth-decoration-one" /><div className="auth-decoration auth-decoration-two" /><header className="auth-nav"><BrandMark /><Link href="/" className="back-link"><ArrowLeft size={15} /> Back home</Link></header><section className="auth-layout"><div className="auth-aside"><div className="auth-aside-mark"><ShieldCheck size={22} /></div><span className="section-kicker">YOUR GROUP, IN SYNC</span><h1>Make the little things add up.</h1><p>One shared list turns individual needs into a smarter group buy.</p><div className="auth-aside-note"><span>“</span><div><p>Everyone can add what they need. We get to see the bigger picture.</p><small>BUY TOGETHER · COMMUNITY BUYING</small></div></div></div><div className="auth-card"><span className="page-kicker">YOUR LIST IS WAITING</span><h2>Welcome back.</h2><p>Sign in to see what you need — and what the group can share.</p><AuthForm mode="login" next={safeNext} /></div></section><footer className="auth-footer">Good things add up. <Link href="/register">Create your account <span>→</span></Link></footer></main>;
}
