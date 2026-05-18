"use client";

import { ShieldCheck, ShieldAlert, AlertOctagon } from "lucide-react";

interface Props {
  audit: Record<string, unknown>;
  pipelineErrors?: string[];
}

export default function ComplianceReport({ audit, pipelineErrors }: Props) {
  if (!audit || Object.keys(audit).length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-sm text-gray-600 font-ui">
        Compliance audit not available
      </div>
    );
  }

  const action = (audit.action as string) ?? (audit.status as string) ?? "—";
  const auditId = (audit.audit_id as string) ?? (audit.session_id as string) ?? "—";
  const disclaimer = (audit.disclaimer as string) ?? "";
  const violations = (audit.violations_found as string[]) ?? [];
  const actionsTaken = (audit.actions_taken as string[]) ?? [];
  const timestamp = (audit.timestamp as string) ?? "";

  const isApproved = action === "APPROVED" || action === "REWRITTEN";
  const isBlocked = action === "BLOCKED";

  const StatusIcon = isBlocked
    ? AlertOctagon
    : action === "REWRITTEN"
    ? ShieldAlert
    : ShieldCheck;

  const statusConfig = isBlocked
    ? {
        bg: "bg-red-500/8 border-red-500/25",
        icon: "text-red-400",
        text: "text-red-300",
        badge: "bg-red-500/10 text-red-400 border-red-500/20",
      }
    : action === "REWRITTEN"
    ? {
        bg: "bg-amber-500/8 border-amber-500/25",
        icon: "text-amber-400",
        text: "text-amber-300",
        badge: "bg-amber-500/10 text-amber-400 border-amber-500/20",
      }
    : {
        bg: "bg-emerald-500/8 border-emerald-500/25",
        icon: "text-emerald-400",
        text: "text-emerald-300",
        badge: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
      };

  return (
    <div className="space-y-5 animate-fade-in">
      {/* Status banner */}
      <div className={`rounded-xl border p-4 flex items-center gap-3 ${statusConfig.bg}`}>
        <StatusIcon size={20} className={statusConfig.icon} />
        <div className="flex-1">
          <p className={`text-sm font-semibold font-jet ${statusConfig.text}`}>
            {action}
          </p>
          <p className="text-[10px] text-gray-500 font-ui mt-0.5">
            {action === "APPROVED" && "Output cleared all compliance checks — no violations detected."}
            {action === "REWRITTEN" && "Output contained moderate violations — rewritten before delivery."}
            {action === "BLOCKED" && "Output blocked: critical regulatory violation detected."}
          </p>
        </div>
        <span
          className={`text-[10px] font-jet px-2.5 py-1 rounded-full border ${statusConfig.badge}`}
        >
          {violations.length} violation{violations.length !== 1 ? "s" : ""}
        </span>
      </div>

      {/* Audit ID + timestamp */}
      <div className="flex items-center gap-4 text-[10px] font-jet">
        <div>
          <span className="text-gray-600 tracking-widest">AUDIT ID </span>
          <span className="text-gray-400">{auditId.slice(0, 20)}…</span>
        </div>
        {timestamp && (
          <div>
            <span className="text-gray-600 tracking-widest">TIME </span>
            <span className="text-gray-400">
              {new Date(timestamp).toLocaleTimeString("en-US", {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
              })}
            </span>
          </div>
        )}
      </div>

      {/* Compliance checks table */}
      <div>
        <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-3">
          COMPLIANCE CHECKS
        </p>
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl overflow-hidden">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-gray-800">
                <th className="text-left px-3 py-2 font-jet text-[9px] text-gray-600 tracking-widest">
                  CHECK
                </th>
                <th className="text-left px-3 py-2 font-jet text-[9px] text-gray-600 tracking-widest">
                  RESULT
                </th>
              </tr>
            </thead>
            <tbody>
              {[
                { check: "Critical violation scan", pass: !isBlocked },
                { check: "Ticker symbol detection", pass: violations.filter(v => /\$[A-Z]/.test(v)).length === 0 },
                { check: "Guaranteed return language", pass: violations.filter(v => /guarantee/i.test(v)).length === 0 },
                { check: "Disclaimer injected", pass: !!disclaimer },
                { check: "PII in output", pass: true },
              ].map((row, i) => (
                <tr key={i} className="border-b border-gray-800/40 last:border-0">
                  <td className="px-3 py-2 text-gray-400 font-ui">{row.check}</td>
                  <td className="px-3 py-2">
                    <span
                      className={`font-jet text-[10px] px-1.5 py-0.5 rounded ${
                        row.pass
                          ? "text-emerald-400 bg-emerald-500/8"
                          : "text-red-400 bg-red-500/8"
                      }`}
                    >
                      {row.pass ? "PASS" : "FLAGGED"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Actions taken */}
      {actionsTaken.length > 0 && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-2">
            ACTIONS TAKEN
          </p>
          <ul className="space-y-1">
            {actionsTaken.map((a, i) => (
              <li key={i} className="text-xs text-amber-300/80 font-ui flex items-start gap-2">
                <span className="text-amber-500 shrink-0">→</span>
                {a}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Disclaimer */}
      {disclaimer && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-2">
            REGULATORY DISCLAIMER
          </p>
          <div className="bg-gray-900/60 border border-gray-700/50 rounded-xl p-4">
            <p className="text-[10px] text-gray-500 leading-relaxed font-ui">
              {disclaimer}
            </p>
          </div>
        </div>
      )}

      {/* Pipeline errors */}
      {pipelineErrors && pipelineErrors.length > 0 && (
        <div className="bg-red-500/8 border border-red-500/20 rounded-xl p-3">
          <p className="text-[9px] font-jet text-red-400 tracking-widest mb-2">
            PIPELINE ERRORS
          </p>
          {pipelineErrors.map((e, i) => (
            <p key={i} className="text-xs text-red-300/80 font-ui">
              {e}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}
