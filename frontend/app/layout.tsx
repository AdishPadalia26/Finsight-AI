import type { Metadata } from "next";
import { DM_Serif_Display, JetBrains_Mono, Sora } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/layout/Navbar";
import MarketDataBar from "@/components/layout/MarketDataBar";

const dmSerif = DM_Serif_Display({
  subsets: ["latin"],
  weight: "400",
  variable: "--font-display",
});

const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jet",
  weight: ["400", "500", "600"],
});

const sora = Sora({
  subsets: ["latin"],
  variable: "--font-ui",
  weight: ["300", "400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "FinSight AI — Multi-Agent Financial Intelligence",
  description:
    "12-agent AI financial planning platform with real-time market data, stress testing, and compliance guardrails.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${dmSerif.variable} ${jetbrains.variable} ${sora.variable} antialiased`}
    >
      <body className="min-h-screen bg-[#0A0F1E] text-white font-ui">
        <MarketDataBar />
        <Navbar />
        {children}
      </body>
    </html>
  );
}
