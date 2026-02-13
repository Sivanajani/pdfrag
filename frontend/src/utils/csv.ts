export function csvValue(val: any, key?: string): string {
  if (val === null || val === undefined) return "";
  if (key === "drugs" && Array.isArray(val)) {
    return val.map((d: any) => `${d.drug_type} ${d.dose ?? ""}${d.dose_unit ?? ""}`).join("; ");
  }
  if (key === "adverse_events" && Array.isArray(val)) {
    return val.map((ae: any) => `${ae.event_type} Grade ${ae.grade}`).join("; ");
  }
  if (Array.isArray(val)) return val.join(", ");
  if (typeof val === "boolean") return val ? "true" : "false";
  return String(val);
}

export function buildCsv(headers: string[], rows: any[]): string {
  const csvRows = rows.map((r) =>
    headers.map((h) => `"${csvValue((r as any)[h], h).replace(/"/g, '""')}"`).join(",")
  );
  return [headers.join(","), ...csvRows].join("\n");
}
