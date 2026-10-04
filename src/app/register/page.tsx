import Link from "next/link";
import { ArrowLeft, UserRoundPlus } from "lucide-react";
import { AuthForm } from "@/components/auth-form";
import { BrandMark } from "@/components/workspace-nav";

export const metadata = { title: "Create your account" };
export default function RegisterPage() {
  return <main className="auth-page"><div className="auth-decoration auth-decoration-one" /><div className="auth-decoration auth-decoration-two" /><header className="auth-nav"><BrandMark /><Link href="/" className="back-link"><ArrowLeft size={15} /> Back home</Link></header><section className="auth-layout"><div className="auth-aside"><div className="auth-aside-mark"><UserRoundPlus size={22} /></div><span className="section-kicker">A BETTER WAY TO STOCK UP</span><h1>Bring your list. Find your people.</h1><p>Join your group and turn “I need this” into “we’ve got this.”</p><div className="auth-aside-note"><span>“</span><div><p>Start with your own needs. Discover the things you can get together.</p><small>BUY TOGETHER · COMMUNITY BUYING</small></div></div></div><div className="auth-card"><span className="page-kicker">GET STARTED</span><h2>Make it a group thing.</h2><p>Create your member account in a moment.</p><AuthForm mode="register" /></div></section><footer className="auth-footer">Already have an account? <Link href="/login">Sign in <span>→</span></Link></footer></main>;
}
