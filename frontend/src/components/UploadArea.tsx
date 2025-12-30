import { useCallback, useMemo, useRef, useState } from "react";
import { Paper, Stack, Typography, Button, CircularProgress, Alert } from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";
import type { UploadedFile } from "../types/files";

import {
  uploadPdfWithText,
  type UploadWithTextResponse,
  llmExtractRadiologyByDocId,
  type RadiologyEvent,
} from "../api";

export default function UploadArea({
  onFilesAdded,
  onTextExtracted,
}: {
  onFilesAdded: (files: UploadedFile[]) => void;
  onTextExtracted?: (payload: UploadWithTextResponse) => void;
}) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const [docType, setDocType] = useState<"radiology" | "cardiology" | "sarcoma">("radiology");
  const [radiologyPreview, setRadiologyPreview] = useState<RadiologyEvent[]>([]);

  const accept = useMemo(() => "application/pdf,.pdf", []);
  const filterPdfFiles = (files: File[]) =>
    files.filter((f) => f.type === "application/pdf" || f.name.toLowerCase().endsWith(".pdf")) as UploadedFile[];

  const handleFiles = useCallback(
    async (fileList: FileList | null) => {
      if (!fileList || fileList.length === 0) return;

      setError(null);
      setSuccess(false);
      setRadiologyPreview([]); 

      const files = filterPdfFiles(Array.from(fileList));
      if (files.length === 0) {
        setError("Bitte nur PDF-Dateien hochladen.");
        return;
      }

      try {
        setIsUploading(true);
        onFilesAdded(files);

        const first = files[0];
        const res = await uploadPdfWithText(first, docType);
        onTextExtracted?.(res);

        if (docType === "radiology") {
          const out = await llmExtractRadiologyByDocId(res.id);
          setRadiologyPreview(out.events); 
        }

        setSuccess(true);
      } catch (e: any) {
        setError(e?.message ?? "Unbekannter Fehler beim Upload");
      } finally {
        setIsUploading(false);
        if (inputRef.current) inputRef.current.value = "";
      }
    },
    [onFilesAdded, onTextExtracted, docType]
  );

  return (
    <Stack spacing={2}>
      <Paper
        variant="outlined"
        sx={{
          p: 4,
          textAlign: "center",
          borderStyle: "dashed",
          borderColor: isDragOver ? "primary.main" : "divider",
          bgcolor: isDragOver ? "action.hover" : "background.paper",
          transition: "all .15s ease-in-out",
        }}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragOver(false);
          handleFiles(e.dataTransfer.files);
        }}
        role="region"
        aria-label="PDF Upload Bereich"
      >
        <Stack spacing={2} alignItems="center" maxWidth={520} mx="auto">
          <Paper variant="outlined" sx={{ p: 1.5, borderRadius: 3 }}>
            <CloudUploadIcon />
          </Paper>

          <Typography variant="h6">PDFs hierher ziehen oder auswählen</Typography>
          <Typography variant="body2" color="text.secondary">
            Mehrere Dateien möglich. Es werden nur PDF-Dateien akzeptiert.
          </Typography>

          <Stack direction="row" spacing={1} justifyContent="center" flexWrap="wrap">
            <Button
              size="small"
              variant={docType === "radiology" ? "contained" : "outlined"}
              onClick={() => setDocType("radiology")}
              disabled={isUploading}
            >
              Radiology
            </Button>
            <Button
              size="small"
              variant={docType === "cardiology" ? "contained" : "outlined"}
              onClick={() => setDocType("cardiology")}
              disabled={isUploading}
            >
              Cardiology
            </Button>
            <Button
              size="small"
              variant={docType === "sarcoma" ? "contained" : "outlined"}
              onClick={() => setDocType("sarcoma")}
              disabled={isUploading}
            >
              Sarcoma
            </Button>
          </Stack>

          <Typography variant="caption" color="text.secondary">
            Ausgewählt: <strong>{docType}</strong>
          </Typography>

          <Stack direction="row" spacing={2} justifyContent="center" pt={1}>
            <Button
              variant="outlined"
              startIcon={isUploading ? <CircularProgress size={16} /> : <CloudUploadIcon />}
              onClick={() => inputRef.current?.click()}
              disabled={isUploading}
            >
              {isUploading ? "Hochladen…" : "Dateien auswählen"}
            </Button>

            <input
              ref={inputRef}
              type="file"
              accept={accept}
              multiple
              hidden
              onChange={(e) => handleFiles(e.target.files)}
            />
          </Stack>

          {error && (
            <Alert severity="error" icon={<ErrorOutlineIcon fontSize="small" />} sx={{ mt: 1 }}>
              {error}
            </Alert>
          )}
          {success && (
            <Alert severity="success" icon={<CheckCircleIcon fontSize="small" />} sx={{ mt: 1 }}>
              Dateien hinzugefügt
            </Alert>
          )}
        </Stack>
      </Paper>

      {/* --- Radiology Vorschau Tabelle (Multi-row) --- */}
      {docType === "radiology" && radiologyPreview.length > 0 && (
        <Paper variant="outlined" sx={{ p: 2, borderRadius: 3 }}>
          <Typography variant="subtitle1" sx={{ mb: 1 }}>
            Radiology Vorschau
          </Typography>

          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  {[
                    "Institution",
                    "Patient ID (PID)",
                    "Date of radiology exam",
                    "Timing of imaging",
                    "Type of imaging",
                    "Type of radiology exam",
                    "Interventionell Radiology",
                  ].map((h) => (
                    <th
                      key={h}
                      style={{
                        textAlign: "left",
                        padding: "10px",
                        borderBottom: "1px solid rgba(0,0,0,0.12)",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody>
                {radiologyPreview.map((row, idx) => (
                  <tr key={`${row.patient_id}-${row.exam_date}-${idx}`}>
                    <td style={{ padding: "10px", borderBottom: "1px solid rgba(0,0,0,0.06)" }}>
                      {row.institution_id}
                    </td>
                    <td style={{ padding: "10px", borderBottom: "1px solid rgba(0,0,0,0.06)" }}>
                      {row.patient_id}
                    </td>
                    <td style={{ padding: "10px", borderBottom: "1px solid rgba(0,0,0,0.06)" }}>
                      {row.exam_date}
                    </td>
                    <td style={{ padding: "10px", borderBottom: "1px solid rgba(0,0,0,0.06)" }}>
                      {row.imaging_timing ?? "-"}
                    </td>
                    <td style={{ padding: "10px", borderBottom: "1px solid rgba(0,0,0,0.06)" }}>
                      {row.imaging_scope ?? "-"}
                    </td>
                    <td style={{ padding: "10px", borderBottom: "1px solid rgba(0,0,0,0.06)" }}>
                      {row.exam_type ?? "-"}
                    </td>
                    <td style={{ padding: "10px", borderBottom: "1px solid rgba(0,0,0,0.06)" }}>
                      {row.interventional_method ?? "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Paper>
      )}
    </Stack>
  );
}
