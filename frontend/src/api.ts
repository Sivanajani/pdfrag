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
  const res = await fetch(`${API}/api/upload-with-text`, { method: 'POST', body: fd });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
