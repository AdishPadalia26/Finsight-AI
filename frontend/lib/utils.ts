export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function getGradeColor(grade: string): string {
  const map: Record<string, string> = {
    A: "text-emerald-400",
    B: "text-green-400",
    C: "text-yellow-400",
    D: "text-orange-400",
    F: "text-red-400",
  };
  return map[grade] ?? "text-slate-400";
}

export function getScoreColor(score: number): string {
  if (score >= 80) return "text-emerald-400";
  if (score >= 60) return "text-yellow-400";
  return "text-red-400";
}

export function classNames(...classes: (string | undefined | false)[]): string {
  return classes.filter(Boolean).join(" ");
}
