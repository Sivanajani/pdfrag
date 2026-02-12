import { useCallback, useEffect, useRef, useState } from "react";
import {
  Paper, Stack, Typography, Button, TextField, CircularProgress,
  Alert, Box, LinearProgress, Chip, IconButton, MenuItem, Select
} from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import DeleteIcon from "@mui/icons-material/Delete";
import ReplayIcon from "@mui/icons-material/Replay";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";

import {
  uploadPdfWithText,
  classifyDocTypeByText,
  llmExtractRadiologyByText,
  llmExtractRadiotherapyByText,
  llmExtractPathologyByText,
  llmExtractSurgeryByText,
  llmExtractSarcomaBoardByText,
  llmExtractSystemicTherapyByText,
  type DocType,
  type RadiologyEvent,
  type RadiotherapyEvent,
  type PathologyEvent,
  type SurgeryEvent,
  type SarcomaBoardEvent,
  type SystemicTherapyEvent,
} from "../api";

const MAX_FILES = 10;
const PREVIEW_CHARS = 5000;

const DOC_TYPE_OPTIONS: { value: DocType; label: string }[] = [
  { value: "radiology", label: "Radiologie" },
  { value: "radiotherapy", label: "Strahlentherapie" },
  { value: "pathology", label: "Pathologie" },
  { value: "surgery", label: "Chirurgie" },
  { value: "sarcoma_board", label: "Sarkom-Board" },
  { value: "systemic_therapy", label: "Systemische Therapie" },
];

type WizardDoc = {
  file: File;
  hash: string;
  docId?: string;
  extractedText?: string;
  previewText?: string;
  patientId: string;
  docType?: DocType;
  status: "pending" | "extracting" | "ready" | "error";
  error?: string;
};

async function hashFile(file: File): Promise<string> {
  const buf = await file.arrayBuffer();
  const digest = await crypto.subtle.digest("SHA-256", buf);
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

type WizardPhase = "upload" | "wizard" | "summary" | "processing" | "done";

export type ExtractionResults = {
  radiologyEvents: RadiologyEvent[];
  radiotherapyEvents: RadiotherapyEvent[];
  pathologyEvents: PathologyEvent[];
  surgeryEvents: SurgeryEvent[];
  sarcomaBoardEvents: SarcomaBoardEvent[];
  systemicTherapyEvents: SystemicTherapyEvent[];
};

type Props = {
  onResults: (results: ExtractionResults) => void;
};

export default function UploadWizard({ onResults }: Props) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [phase, setPhase] = useState<WizardPhase>("upload");
  const [docs, setDocs] = useState<WizardDoc[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [processingIdx, setProcessingIdx] = useState(-1);
  const [processingError, setProcessingError] = useState<string | null>(null);
  const [isClassifying, setIsClassifying] = useState(false);

  // Ref to always access the latest docs (avoids stale closures in async callbacks)
  const docsRef = useRef(docs);
  docsRef.current = docs;

  // --- Phase: Upload ---

  const addFiles = useCallback(async (fileList: FileList | null) => {
    if (!fileList) return;
    const pdfs = Array.from(fileList).filter(
      (f) => f.type === "application/pdf" || f.name.toLowerCase().endsWith(".pdf")
    );
    if (pdfs.length === 0) return;

    const hashed = await Promise.all(
      pdfs.map(async (file) => ({ file, hash: await hashFile(file) }))
    );

    setDocs((prev) => {
      const existing = new Set(prev.map((d) => d.hash));
      const newDocs: WizardDoc[] = hashed
        .filter(({ hash }) => !existing.has(hash))
        .map(({ file, hash }) => ({ file, hash, patientId: "", status: "pending" as const }));
      const merged = [...prev, ...newDocs].slice(0, MAX_FILES);
      return merged;
    });
  }, []);

  const removeDoc = (idx: number) => {
    setDocs((prev) => prev.filter((_, i) => i !== idx));
  };

  const startWizard = () => {
    if (docs.length === 0) return;
    setCurrentIdx(0);
    setPhase("wizard");
  };

  // --- Phase: Wizard step ---

  const currentDoc = docs[currentIdx];

  // Parameterized extraction — no closure over docs/currentIdx
  const extractTextAt = useCallback(async (idx: number) => {
    const doc = docsRef.current[idx];
    if (!doc || (doc.status !== "pending" && doc.status !== "error")) return;

    setDocs((prev) =>
      prev.map((d, i) => (i === idx ? { ...d, status: "extracting" as const, error: undefined } : d))
    );

    try {
      const res = await uploadPdfWithText(doc.file);
      setDocs((prev) =>
        prev.map((d, i) =>
          i === idx
            ? {
                ...d,
                docId: res.id,
                extractedText: res.text || "",
                previewText: (res.text || "").slice(0, PREVIEW_CHARS),
                status: "ready" as const,
              }
            : d
        )
      );
    } catch (e: any) {
      setDocs((prev) =>
        prev.map((d, i) =>
          i === idx
            ? { ...d, status: "error" as const, error: e?.message ?? "Textextraktion fehlgeschlagen" }
            : d
        )
      );
    }
  }, []);

  // Auto-extract text when entering a wizard step
  useEffect(() => {
    if (phase !== "wizard") return;
    const doc = docsRef.current[currentIdx];
    if (doc && doc.status === "pending") {
      extractTextAt(currentIdx);
    }
  }, [phase, currentIdx, extractTextAt]);

  const confirmAndNext = useCallback(async () => {
    const doc = docsRef.current[currentIdx];
    if (!doc || !doc.patientId.trim() || !doc.extractedText) return;

    // Capture values before async gap
    const idx = currentIdx;
    const text = doc.extractedText;

    // Auto-classify doc type (skip if already set)
    if (!doc.docType) {
      setIsClassifying(true);
      try {
        const classifyRes = await classifyDocTypeByText(text);
        setDocs((prev) =>
          prev.map((d, i) =>
            i === idx ? { ...d, docType: classifyRes.doc_type } : d
          )
        );
      } catch {
        // Classification failed — user can fix it in summary
      } finally {
        setIsClassifying(false);
      }
    }

    // Navigate using fresh docs length from ref (not stale closure)
    const freshLength = docsRef.current.length;
    if (idx < freshLength - 1) {
      setCurrentIdx(idx + 1);
    } else {
      setPhase("summary");
    }
  }, [currentIdx]);

  const updatePatientId = (value: string) => {
    setDocs((prev) =>
      prev.map((d, i) => (i === currentIdx ? { ...d, patientId: value } : d))
    );
  };

  const updateDocType = (idx: number, value: DocType) => {
    setDocs((prev) =>
      prev.map((d, i) => (i === idx ? { ...d, docType: value } : d))
    );
  };

  // --- Phase: Processing ---

  const extractAll = useCallback(async () => {
    setPhase("processing");
    setProcessingError(null);

    const results: ExtractionResults = {
      radiologyEvents: [],
      radiotherapyEvents: [],
      pathologyEvents: [],
      surgeryEvents: [],
      sarcomaBoardEvents: [],
      systemicTherapyEvents: [],
    };

    for (let i = 0; i < docs.length; i++) {
      setProcessingIdx(i);
      const doc = docs[i];
      if (!doc.extractedText || !doc.docType) continue;

      try {
        const pid = doc.patientId.trim();
        const text = doc.extractedText;

        if (doc.docType === "radiology") {
          const res = await llmExtractRadiologyByText(text);
          results.radiologyEvents.push(
            ...res.events.map((e) => ({ ...e, patient_id: pid as any }))
          );
        } else if (doc.docType === "radiotherapy") {
          const res = await llmExtractRadiotherapyByText(text);
          results.radiotherapyEvents.push(
            ...res.events.map((e) => ({ ...e, patient_id: pid as any }))
          );
        } else if (doc.docType === "pathology") {
          const res = await llmExtractPathologyByText(text);
          results.pathologyEvents.push(
            ...res.events.map((e) => ({ ...e, patient_id: pid as any }))
          );
        } else if (doc.docType === "surgery") {
          const res = await llmExtractSurgeryByText(text);
          results.surgeryEvents.push(
            ...res.events.map((e) => ({ ...e, patient_id: pid as any }))
          );
        } else if (doc.docType === "sarcoma_board") {
          const res = await llmExtractSarcomaBoardByText(text);
          results.sarcomaBoardEvents.push(
            ...res.events.map((e) => ({ ...e, patient_id: pid as any }))
          );
        } else if (doc.docType === "systemic_therapy") {
          const res = await llmExtractSystemicTherapyByText(text);
          results.systemicTherapyEvents.push(
            ...res.events.map((e) => ({ ...e, patient_id: pid as any }))
          );
        }
      } catch (e: any) {
        setProcessingError(`Fehler bei "${doc.file.name}": ${e?.message ?? "Unbekannter Fehler"}`);
        // Continue with next document
      }
    }

    setProcessingIdx(-1);
    onResults(results);
    setPhase("done");
  }, [docs, onResults]);

  const resetWizard = () => {
    setDocs([]);
    setCurrentIdx(0);
    setProcessingIdx(-1);
    setProcessingError(null);
    setPhase("upload");
  };

  // --- Render ---

  // Phase: Upload
  if (phase === "upload") {
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
          onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={(e) => { e.preventDefault(); setIsDragOver(false); addFiles(e.dataTransfer.files); }}
        >
          <Stack spacing={2} alignItems="center" maxWidth={520} mx="auto">
            <Paper variant="outlined" sx={{ p: 1.5, borderRadius: 3 }}>
              <CloudUploadIcon />
            </Paper>
            <Typography variant="h6">PDFs hierher ziehen oder auswaehlen</Typography>
            <Typography variant="body2" color="text.secondary">
              Max. {MAX_FILES} Dateien. Es werden nur PDF-Dateien akzeptiert.
            </Typography>

            <Button
              variant="outlined"
              startIcon={<CloudUploadIcon />}
              onClick={() => inputRef.current?.click()}
            >
              Dateien auswaehlen
            </Button>
            <input
              ref={inputRef}
              type="file"
              accept="application/pdf,.pdf"
              multiple
              hidden
              onChange={(e) => { addFiles(e.target.files); if (inputRef.current) inputRef.current.value = ""; }}
            />
          </Stack>
        </Paper>

        {docs.length > 0 && (
          <Paper variant="outlined" sx={{ p: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              {docs.length} Datei(en) ausgewaehlt
            </Typography>
            <Stack spacing={1}>
              {docs.map((doc, idx) => (
                <Stack key={`${doc.file.name}_${idx}`} direction="row" alignItems="center" spacing={1}>
                  <Typography variant="body2" sx={{ flex: 1 }}>{doc.file.name}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {(doc.file.size / 1024).toFixed(0)} KB
                  </Typography>
                  <IconButton size="small" onClick={() => removeDoc(idx)}>
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </Stack>
              ))}
            </Stack>
            <Button
              variant="contained"
              sx={{ mt: 2 }}
              onClick={startWizard}
              disabled={docs.length === 0}
            >
              Wizard starten ({docs.length} Dateien)
            </Button>
          </Paper>
        )}
      </Stack>
    );
  }

  // Phase: Wizard (step by step)
  if (phase === "wizard" && currentDoc) {
    return (
      <Paper variant="outlined" sx={{ p: 3 }}>
        {/* Progress */}
        <Stack direction="row" alignItems="center" spacing={2} mb={2}>
          <Typography variant="h6">
            Dokument {currentIdx + 1} von {docs.length}
          </Typography>
          <Chip label={currentDoc.file.name} size="small" />
        </Stack>
        <LinearProgress
          variant="determinate"
          value={((currentIdx + 1) / docs.length) * 100}
          sx={{ mb: 3, borderRadius: 1 }}
        />

        {/* Text extraction (auto-triggered) */}
        {(currentDoc.status === "pending" || currentDoc.status === "extracting") && (
          <Stack spacing={2} alignItems="center" py={4}>
            <CircularProgress />
            <Typography variant="body2">Extrahiere Text aus PDF...</Typography>
          </Stack>
        )}

        {isClassifying && (
          <Stack spacing={2} alignItems="center" py={4}>
            <CircularProgress />
            <Typography variant="body2">Klassifiziere Dokumenttyp...</Typography>
          </Stack>
        )}

        {currentDoc.status === "error" && (
          <Stack spacing={2} alignItems="center" py={4}>
            <Alert severity="error" icon={<ErrorOutlineIcon />}>
              {currentDoc.error}
            </Alert>
            <Button variant="outlined" startIcon={<ReplayIcon />} onClick={() => extractTextAt(currentIdx)}>
              Erneut versuchen
            </Button>
          </Stack>
        )}

        {(currentDoc.status === "ready" && currentDoc.previewText) && (
          <Stack spacing={2}>
            {/* Text Preview */}
            <Typography variant="subtitle2">Text-Vorschau</Typography>
            <Paper
              variant="outlined"
              sx={{
                p: 2,                
                color: "text.primary",
                maxHeight: 300,
                overflow: "auto",
                bgcolor: "background.default",
                fontFamily: "monospace",
                fontSize: 12,
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
              }}
            >
              {currentDoc.previewText}
              {currentDoc.extractedText && currentDoc.extractedText.length > PREVIEW_CHARS && (
                <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                  ... ({currentDoc.extractedText.length - PREVIEW_CHARS} weitere Zeichen)
                </Typography>
              )}
            </Paper>

            {/* Patient ID Input */}
            <TextField
              label="Patient ID (Pflichtfeld)"
              value={currentDoc.patientId}
              onChange={(e) => updatePatientId(e.target.value)}
              fullWidth
              required
              error={currentDoc.patientId.trim() === ""}
              helperText={currentDoc.patientId.trim() === "" ? "PID darf nicht leer sein" : ""}
              autoFocus
            />

            {/* Navigation */}
            <Stack direction="row" spacing={2} justifyContent="space-between">
              <Button
                startIcon={<ArrowBackIcon />}
                onClick={() => {
                  if (currentIdx > 0) setCurrentIdx(currentIdx - 1);
                  else setPhase("upload");
                }}
              >
                {currentIdx > 0 ? "Zurueck" : "Zur Dateiauswahl"}
              </Button>

              <Button
                variant="contained"
                endIcon={currentIdx < docs.length - 1 ? <ArrowForwardIcon /> : <CheckCircleIcon />}
                onClick={confirmAndNext}
                disabled={!currentDoc.patientId.trim() || isClassifying}
              >
                {currentIdx < docs.length - 1
                  ? "Bestaetigen & Weiter"
                  : "Bestaetigen & Zusammenfassung"}
              </Button>
            </Stack>
          </Stack>
        )}
      </Paper>
    );
  }

  // Phase: Summary
  if (phase === "summary") {
    return (
      <Paper variant="outlined" sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>Zusammenfassung</Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Alle Dokumente wurden vorbereitet. Klicken Sie auf "Jetzt extrahieren" um die Datenextraktion zu starten.
        </Typography>

        <Box sx={{ overflowX: "auto", mt: 2 }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={{ textAlign: "left", padding: "8px", borderBottom: "2px solid #ddd" }}>#</th>
                <th style={{ textAlign: "left", padding: "8px", borderBottom: "2px solid #ddd" }}>Dateiname</th>
                <th style={{ textAlign: "left", padding: "8px", borderBottom: "2px solid #ddd" }}>Patient ID</th>
                <th style={{ textAlign: "left", padding: "8px", borderBottom: "2px solid #ddd" }}>Dokumenttyp</th>
                <th style={{ textAlign: "left", padding: "8px", borderBottom: "2px solid #ddd" }}>Textlaenge</th>
              </tr>
            </thead>
            <tbody>
              {docs.map((doc, idx) => (
                <tr key={idx}>
                  <td style={{ padding: "8px", borderBottom: "1px solid #eee" }}>{idx + 1}</td>
                  <td style={{ padding: "8px", borderBottom: "1px solid #eee" }}>{doc.file.name}</td>
                  <td style={{ padding: "8px", borderBottom: "1px solid #eee" }}>
                    <Chip label={doc.patientId} size="small" color="primary" />
                  </td>
                  <td style={{ padding: "8px", borderBottom: "1px solid #eee" }}>
                    <Select
                      value={doc.docType || ""}
                      size="small"
                      onChange={(e) => updateDocType(idx, e.target.value as DocType)}
                      sx={{ minWidth: 160 }}
                    >
                      {DOC_TYPE_OPTIONS.map((opt) => (
                        <MenuItem key={opt.value} value={opt.value}>
                          {opt.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </td>
                  <td style={{ padding: "8px", borderBottom: "1px solid #eee" }}>
                    {doc.extractedText?.length?.toLocaleString() ?? "–"} Zeichen
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Box>

        {docs.some((d) => !d.docType) && (
          <Alert severity="warning" sx={{ mt: 2 }}>
            Einige Dokumente haben keinen Dokumenttyp. Bitte waehlen Sie den Typ manuell aus, bevor Sie fortfahren.
          </Alert>
        )}

        <Stack direction="row" spacing={2} justifyContent="space-between" mt={3}>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => { setCurrentIdx(docs.length - 1); setPhase("wizard"); }}
          >
            Zurueck zum Wizard
          </Button>
          <Button
            variant="contained"
            size="large"
            onClick={extractAll}
            disabled={docs.some((d) => !d.docType)}
          >
            Jetzt extrahieren ({docs.length} Dokumente)
          </Button>
        </Stack>
      </Paper>
    );
  }

  // Phase: Processing
  if (phase === "processing") {
    return (
      <Paper variant="outlined" sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>Daten werden extrahiert...</Typography>
        <LinearProgress
          variant="determinate"
          value={processingIdx >= 0 ? ((processingIdx + 1) / docs.length) * 100 : 0}
          sx={{ mb: 2, borderRadius: 1 }}
        />

        <Stack spacing={1}>
          {docs.map((doc, idx) => (
            <Stack key={idx} direction="row" alignItems="center" spacing={1}>
              {idx < processingIdx ? (
                <CheckCircleIcon color="success" fontSize="small" />
              ) : idx === processingIdx ? (
                <CircularProgress size={16} />
              ) : (
                <Box sx={{ width: 16, height: 16 }} />
              )}
              <Typography
                variant="body2"
                color={idx === processingIdx ? "primary" : idx < processingIdx ? "text.secondary" : "text.disabled"}
              >
                {doc.file.name} (PID: {doc.patientId}, Typ: {doc.docType})
              </Typography>
            </Stack>
          ))}
        </Stack>

        {processingError && (
          <Alert severity="warning" sx={{ mt: 2 }}>{processingError}</Alert>
        )}
      </Paper>
    );
  }

  // Phase: Done
  if (phase === "done") {
    return (
      <Paper variant="outlined" sx={{ p: 3 }}>
        <Stack spacing={2} alignItems="center">
          <CheckCircleIcon color="success" sx={{ fontSize: 48 }} />
          <Typography variant="h6">Extraktion abgeschlossen</Typography>
          <Typography variant="body2" color="text.secondary">
            {docs.length} Dokument(e) verarbeitet. Ergebnisse werden unten angezeigt.
          </Typography>
          {processingError && (
            <Alert severity="warning" sx={{ width: "100%" }}>{processingError}</Alert>
          )}
          <Button variant="outlined" onClick={resetWizard}>
            Neuen Wizard starten
          </Button>
        </Stack>
      </Paper>
    );
  }

  return null;
}
