import type { Metadata } from "next";
import { DM_Sans, Space_Grotesk } from "next/font/google";
import "./globals.css";

const dmSans = DM_Sans({ variable: "--font-body", subsets: ["latin"] });
const spaceGrotesk = Space_Grotesk({ variable: "--font-display", subsets: ["latin"] });

export const metadata: Metadata = {
  title: { default: "Buy Together — Good things add up", template: "%s | Buy Together" },
  description: "Turn individual needs into smarter group purchases. Share what you need, organize it instantly, and buy better together.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body className={`${dmSans.variable} ${spaceGrotesk.variable}`}>{children}</body></html>;
}
