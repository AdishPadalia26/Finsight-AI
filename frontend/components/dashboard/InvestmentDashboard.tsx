"use client";

import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";

interface Props {
  investment: Record<string, unknown>;
}

const ALLOCATION_COLORS = [
  "#F59E0B", // amber — equities
  "#06B6D4", // cyan — bonds
  "#6366F1", // indigo — international
  "#10B981", // emerald — cash
  "#8B5CF6", // purple — alternatives
  "#EC4899", // pink — REITs
];

function MarketBadge({
  label,
  value,
  context,
}: {
  label: string;
  value: string;
  context: string;
}) {
  return (
    <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-3">
      <p className="text-[9px] font-jet text-gray-600 tracking-widest">{label}</p>
      <p className="text-base font-jet font-semibold text-white mt-1">{value}</p>
      <p className="text-[10px] text-gray-600 font-ui mt-0.5">{context}</p>
    </div>
  );
}

export default function InvestmentDashboard({ investment }: Props) {
  if (!investment || Object.keys(investment).length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-sm text-gray-600 font-ui">
        Investment data not available
      </div>
    );
  }

  const allocation = (investment.allocation as Record<string, number>) ?? {};
  const riskAlignment = (investment.risk_alignment as string) ?? "—";
  const rationale = (investment.rationale as string) ?? "";
  const accountOptimization = (investment.account_optimization as string) ?? "";
  const marketContext = (investment.market_context as Record<string, unknown>) ?? {};

  const pieData = Object.entries(allocation)
    .filter(([, v]) => typeof v === "number" && v > 0)
    .map(([name, value]) => ({
      name: name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
      value: Math.round((value > 1 ? value : value * 100) * 10) / 10,
    }));

  const totalPct = pieData.reduce((s, d) => s + d.value, 0);

  const riskColor =
    riskAlignment.toLowerCase() === "conservative"
      ? "text-blue-400 bg-blue-500/10 border-blue-500/20"
      : riskAlignment.toLowerCase() === "aggressive"
      ? "text-red-400 bg-red-500/10 border-red-500/20"
      : "text-amber-400 bg-amber-500/10 border-amber-500/20";

  return (
    <div className="space-y-5 animate-fade-in">
      {/* Risk alignment */}
      <div className="flex items-center gap-2">
        <span className="text-[9px] font-jet text-gray-600 tracking-widest">
          RISK ALIGNMENT
        </span>
        <span
          className={`text-[10px] font-jet px-2 py-0.5 rounded border capitalize ${riskColor}`}
        >
          {riskAlignment}
        </span>
      </div>

      {/* Allocation pie */}
      {pieData.length > 0 && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-3">
            PORTFOLIO ALLOCATION
          </p>
          <div className="flex items-center gap-4">
            <ResponsiveContainer width={160} height={160}>
              <PieChart>
                <Pie
                  data={pieData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={48}
                  outerRadius={72}
                  paddingAngle={2}
                >
                  {pieData.map((_, i) => (
                    <Cell key={i} fill={ALLOCATION_COLORS[i % ALLOCATION_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: "#111827",
                    border: "1px solid #1F2937",
                    borderRadius: "8px",
                    fontSize: "11px",
                    fontFamily: "JetBrains Mono",
                  }}
                  formatter={(v) => [`${v}%`, ""]}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex-1 space-y-1.5">
              {pieData.map((item, i) => (
                <div key={i} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span
                      className="w-2.5 h-2.5 rounded-sm"
                      style={{ background: ALLOCATION_COLORS[i % ALLOCATION_COLORS.length] }}
                    />
                    <span className="text-xs text-gray-400 font-ui">{item.name}</span>
                  </div>
                  <span className="text-xs font-jet text-white">{item.value}%</span>
                </div>
              ))}
              {totalPct > 0 && Math.abs(totalPct - 100) > 2 && (
                <div className="flex items-center justify-between border-t border-gray-800 pt-1.5 mt-1.5">
                  <span className="text-[10px] text-gray-600 font-jet">TOTAL</span>
                  <span className="text-[10px] font-jet text-gray-400">{totalPct}%</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Live market context */}
      {marketContext && Object.keys(marketContext).length > 0 && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-3">
            LIVE MARKET CONTEXT
          </p>
          <div className="grid grid-cols-2 gap-2">
            {(marketContext.fed_funds_rate as number) != null && (
              <MarketBadge
                label="FED FUNDS RATE"
                value={`${(marketContext.fed_funds_rate as number).toFixed(2)}%`}
                context="Current rate environment"
              />
            )}
            {(marketContext.inflation_rate as number) != null && (
              <MarketBadge
                label="CPI INFLATION"
                value={`${(marketContext.inflation_rate as number).toFixed(1)}%`}
                context="Year-over-year"
              />
            )}
            {(marketContext.treasury_10yr as number) != null && (
              <MarketBadge
                label="10-YR TREASURY"
                value={`${(marketContext.treasury_10yr as number).toFixed(2)}%`}
                context="Risk-free rate benchmark"
              />
            )}
            {(marketContext.sp500_price as number) != null && (
              <MarketBadge
                label="S&P 500"
                value={`$${(marketContext.sp500_price as number).toLocaleString("en-US", { maximumFractionDigits: 0 })}`}
                context="Real-time via yfinance"
              />
            )}
          </div>
        </div>
      )}

      {/* Rationale */}
      {rationale && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-2">
            STRATEGY RATIONALE
          </p>
          <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-3">
            <p className="text-xs text-gray-400 leading-relaxed font-ui">{rationale}</p>
          </div>
        </div>
      )}

      {/* Account optimization */}
      {accountOptimization && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-2">
            ACCOUNT OPTIMIZATION
          </p>
          <div className="bg-cyan-500/5 border border-cyan-500/15 rounded-xl p-3">
            <p className="text-xs text-cyan-300/80 leading-relaxed font-ui">
              {accountOptimization}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
