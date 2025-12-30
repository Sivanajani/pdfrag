const API = import.meta.env.VITE_API_URL; 

export type UploadWithTextResponse = {
  id: string;
  filename: string;
  text?: string;
  length?: number;
};

export async function uploadPdfWithText(
  file: File,
  docType: "radiology" | "cardiology" | "sarcoma"
): Promise<UploadWithTextResponse> {
  const fd = new FormData();
  fd.append("file", file);
  fd.append("doc_type", docType);

  const res = await fetch(`${API}/upload-with-text`, {
    method: "POST",
    body: fd,
  });

  if (!res.ok) throw new Error(await res.text());
  return res.json();
}


// --- LLM Extract Types & API ---

export type ExtractedItem = {
  source_type?: string | null;
  body_part?: string | null;
  concept?: string | null;
  value?: number | null;
  unit?: string | null;
  note?: string | null;
};

export type LlmExtractResponse = {
  items: ExtractedItem[];
};

export async function llmExtractByDocId(docId: string): Promise<LlmExtractResponse> {
  const res = await fetch(`${API}/llm/extract`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ doc_id: docId }),
  });

  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export type RadiologyEvent = {
  institution_id?: number | null
  patient_id?: number | null
  exam_date: string
  imaging_timing?: string | null
  imaging_scope?: string | null
  exam_type?: string | null
  interventional_method?: string | null
}


export type RadiologyExtractResponse = {
  events: RadiologyEvent[]
}

export async function llmExtractRadiologyByDocId(docId: string): Promise<RadiologyExtractResponse> {
  const res = await fetch(`${API}/llm/extract-radiology`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ doc_id: docId }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}
