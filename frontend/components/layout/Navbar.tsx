import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="bg-[#0A0F1E] border-b border-gray-800/60 px-6 py-4 sticky top-[36px] z-40">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-7 h-7 rounded bg-amber-500/10 border border-amber-500/30 flex items-center justify-center">
            <span className="text-amber-500 text-xs font-jet font-semibold">FS</span>
          </div>
          <span className="text-white font-display text-lg tracking-wide group-hover:text-amber-500/90 transition-colors">
            FinSight AI
          </span>
        </Link>

        {/* Right */}
        <div className="flex items-center gap-6">
          <Link
            href="/"
            className="text-sm text-gray-500 hover:text-gray-300 transition-colors font-ui hidden sm:block"
          >
            Overview
          </Link>
          <Link
            href="/analyze"
            className="text-sm text-gray-400 hover:text-white transition-colors font-ui"
          >
            Analyze
          </Link>
          <Link
            href="/analyze"
            className="text-sm font-semibold bg-amber-500 hover:bg-amber-400 active:bg-amber-600 text-gray-950 px-4 py-1.5 rounded-lg transition-colors font-ui"
          >
            Run Demo →
          </Link>
        </div>
      </div>
    </nav>
  );
}
