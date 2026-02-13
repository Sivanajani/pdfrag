import { describe, it, expect } from "vitest";
import { buildCsv } from "./csv";

describe("CSV export", () => {
  it("exports the header row correctly", () => {
    const headers = ["patient_id", "exam_date", "location_of_lesion"];
    const rows = [{ patient_id: 1, exam_date: "2024-01-15", location_of_lesion: "Upper extremity" }];

    const csv = buildCsv(headers, rows);
    const firstLine = csv.split("\n")[0];

    expect(firstLine).toBe("patient_id,exam_date,location_of_lesion");
  });

  it("exports null/undefined as empty (not 'None')", () => {
    const headers = ["patient_id", "note", "comment"];
    const rows = [{ patient_id: 1, note: null, comment: undefined }];

    const csv = buildCsv(headers, rows);
    const secondLine = csv.split("\n")[1];

    expect(secondLine).toBe('"1","",""');
    expect(csv).not.toContain("None");
  });

  it("keeps stable column order based on headers", () => {
    const headers = ["b", "a", "c"];
    const rows = [{ a: "A", b: "B", c: "C" }];

    const csv = buildCsv(headers, rows);
    const secondLine = csv.split("\n")[1];

    expect(secondLine).toBe('"B","A","C"');
  });
});
