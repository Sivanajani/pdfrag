const API = import.meta.env.VITE_API_URL; // z.B. http://localhost:8000

export type UploadWithTextResponse = {
  id: string;
  filename: string;
  text?: string;
  length?: number;
};

export async function uploadPdfWithText(file: File): Promise<UploadWithTextResponse> {
  const fd = new FormData();
  fd.append('file', file);
  const res = await fetch(`${API}/upload-with-text`, { method: 'POST', body: fd });
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
