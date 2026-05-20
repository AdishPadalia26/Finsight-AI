export function displayText(value: unknown): string {
  if (value == null) return "";
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  if (Array.isArray(value)) {
    return value.map(displayText).filter(Boolean).join("; ");
  }
  if (typeof value === "object") {
    const record = value as Record<string, unknown>;
    const main =
      record.action ??
      record.step ??
      record.title ??
      record.name ??
      record.risk ??
      record.description ??
      record.insight ??
      record.recommendation;
    const detail =
      record.rationale ??
      record.mitigation ??
      record.deadline ??
      record.timeframe ??
      record.timeline;
    const mainText = displayText(main);
    const detailText = displayText(detail);
    if (mainText && detailText) return `${mainText} (${detailText})`;
    if (mainText) return mainText;
    return Object.entries(record)
      .map(([key, val]) => `${key.replace(/_/g, " ")}: ${displayText(val)}`)
      .join("; ");
  }
  return String(value);
}
