"use client";

import { useEffect, useState } from "react";

interface MarketData {
  sp500_price?: number;
  inflation_rate?: number;
  fed_funds_rate?: number;
  treasury_10yr?: number;
  data_timestamp?: string;
}

function Tick({
  label,
  value,
  positive,
}: {
  label: string;
  value: string;
  positive?: boolean;
}) {
  return (
    <div className="flex items-center gap-1.5 shrink-0">
      <span className="text-[10px] font-jet text-gray-600 tracking-wider">
        {label}
      </span>
      <span
        className={`text-[10px] font-jet ${positive === true ? "text-emerald-400" : positive === false ? "text-red-400" : "text-gray-300"}`}
      >
        {value}
      </span>
    </div>
  );
}

export default function MarketDataBar() {
  const [data, setData] = useState<MarketData | null>(null);
  const [unavailable, setUnavailable] = useState(false);

  useEffect(() => {
    const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    fetch(`${base}/health`, { signal: AbortSignal.timeout(4000) })
      .then((r) => r.json())
      .then((d) => {
        if (d.market_context) setData(d.market_context as MarketData);
        else setUnavailable(true);
      })
      .catch(() => setUnavailable(true));
  }, []);

  return (
    <div className="sticky top-0 z-50 bg-[#0D1425] border-b border-gray-800/80 px-4 py-1.5">
      <div className="max-w-7xl mx-auto flex items-center gap-5 overflow-x-auto scrollbar-none">
        {/* Live pulse */}
        <div className="flex items-center gap-1.5 shrink-0">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-[9px] font-jet text-emerald-500 tracking-[0.2em]">
            LIVE
          </span>
        </div>

        <div className="w-px h-3 bg-gray-800 shrink-0" />

        {unavailable || !data ? (
          <span className="text-[10px] font-jet text-gray-700">
            {unavailable ? "Market data unavailable" : "Loading market data…"}
          </span>
        ) : (
          <>
            <Tick
              label="FED"
              value={`${data.fed_funds_rate?.toFixed(2) ?? "—"}%`}
            />
            <Tick
              label="CPI"
              value={`${data.inflation_rate?.toFixed(1) ?? "—"}%`}
            />
            <Tick
              label="10YR"
              value={`${data.treasury_10yr?.toFixed(2) ?? "—"}%`}
            />
            <Tick
              label="S&P 500"
              value={`$${data.sp500_price?.toLocaleString("en-US", { maximumFractionDigits: 0 }) ?? "—"}`}
              positive={true}
            />
            {data.data_timestamp && (
              <span className="text-[9px] font-jet text-gray-700 ml-auto shrink-0">
                {new Date(data.data_timestamp).toLocaleTimeString("en-US", {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            )}
          </>
        )}
      </div>
    </div>
  );
}
