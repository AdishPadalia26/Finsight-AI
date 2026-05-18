import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FinSight AI — Multi-Agent Financial Intelligence",
  description:
    "12-agent AI financial planning platform with real-time market data, stress testing, and compliance guardrails.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="antialiased">
      <body className="min-h-screen bg-slate-950 text-white font-sans">{children}</body>
    </html>
  );
}
