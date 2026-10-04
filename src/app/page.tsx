import Link from "next/link";
import { ArrowDownRight, ArrowRight, ArrowUpRight, Boxes, Check, Layers3, Sparkles, UsersRound } from "lucide-react";
import { BrandMark, Eyebrow } from "@/components/workspace-nav";

const steps = [
  { number: "01", title: "Say what you need", copy: "Type it like a message to a friend. English, Hinglish — both feel right.", icon: <UsersRound size={19} /> },
  { number: "02", title: "We sort the details", copy: "AI turns everyday words into a tidy list of items, options, and quantities.", icon: <Sparkles size={19} /> },
  { number: "03", title: "See the whole picture", copy: "Every member’s needs come together in one clear manager view.", icon: <Layers3 size={19} /> },
  { number: "04", title: "Buy better, together", copy: "Spot the shared demand. Place smarter group orders with less guesswork.", icon: <Boxes size={19} /> },
];

export default function Home() {
  return <main className="landing-page">
    <header className="landing-nav"><BrandMark /><nav><a href="#how-it-works">How it works</a><Link href="/login" className="nav-login">Sign in</Link><Link href="/register" className="button button-dark">Join your group <ArrowUpRight size={15} /></Link></nav></header>
    <section className="hero-section">
      <div className="hero-copy"><Eyebrow>GROUP BUYING, MADE SIMPLE</Eyebrow><h1>Better together.<br /><span>By design.</span></h1><p className="hero-subtitle">Turn individual needs into smarter group purchases. One quick message can help your whole community buy better.</p><div className="hero-actions"><Link className="button button-primary button-large" href="/register">Start a shared list <ArrowRight size={17} /></Link><a className="text-link" href="#how-it-works">See how it works <ArrowDownRight size={16} /></a></div><div className="hero-proof"><div className="proof-avatars"><span>A</span><span>R</span><span>P</span><span>+</span></div><p>For classrooms, teams<br />and neighbourhoods.</p></div></div>
      <div className="hero-visual" aria-label="Example of a shared purchase list">
        <div className="visual-glow" />
        <div className="visual-note note-top"><span className="note-dot" /> In the group chat</div>
        <div className="demo-message"><div className="demo-avatar">A</div><div><div className="demo-name">Arpit <span>just now</span></div><p>bhai 2 notebook aur ek blue pen</p></div></div>
        <div className="demo-spark"><Sparkles size={15} /> Structured for you</div>
        <div className="demo-items"><div className="demo-items-head"><span>YOUR REQUIREMENTS</span><span className="mini-status"><Check size={12} /> 2 items</span></div><div className="demo-item"><span className="product-thumb thumb-lilac">N</span><div><strong>Notebook</strong><small>Everyday essentials</small></div><b>× 2</b></div><div className="demo-item"><span className="product-thumb thumb-peach">P</span><div><strong>Pen</strong><small>Blue · ballpoint</small></div><b>× 1</b></div></div>
        <div className="group-total"><div className="total-icon"><Boxes size={17} /></div><div><small>GROUP TOTAL · NOTEBOOKS</small><strong>10 <span>pieces</span></strong></div><div className="total-stack"><span>A</span><span>R</span><span>P</span></div></div>
        <div className="visual-note note-bottom"><UsersRound size={14} /> 3 members already in</div>
      </div>
    </section>
    <section id="how-it-works" className="steps-section"><div className="section-heading"><Eyebrow>THE SIMPLE WAY TO SHARE</Eyebrow><h2>Small asks. <span>Better buys.</span></h2><p>Skip the spreadsheet. Let everyone add their own needs and see what the group can do.</p></div><div className="steps-list">{steps.map((step) => <article className="step-card" key={step.number}><span className="step-number">{step.number}</span><span className="step-icon">{step.icon}</span><h3>{step.title}</h3><p>{step.copy}</p></article>)}</div></section>
    <section className="closing-banner"><div><span className="closing-kicker">LESS SOLO. MORE TOGETHER.</span><h2>Good things add up.</h2><p>Start with what you need. See where the group takes it.</p></div><Link href="/register" className="button button-light">Make your first list <ArrowRight size={16} /></Link></section>
    <footer className="landing-footer"><BrandMark /><p>Good things add up.</p><span>© {new Date().getFullYear()} Buy Together</span></footer>
  </main>;
}
