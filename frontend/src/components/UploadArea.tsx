import { useCallback, useMemo, useRef, useState } from "react";
import { Paper, Stack, Typography, Button, CircularProgress, Alert, FormControlLabel, Switch } from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";
import AutoFixHighIcon from "@mui/icons-material/AutoFixHigh";
import { useTranslation } from "react-i18next";
import type { UploadedFile } from "../types/files";

import {
  uploadPdfWithText,
  classifyDocTypeByDocId,
  type UploadWithTextResponse,
  type DocType,
} from "../api";

export default function UploadArea({
  onFilesAdded,
  onTextExtracted,
}: {
  onFilesAdded: (files: UploadedFile[]) => void;
  onTextExtracted?: (payload: UploadWithTextResponse) => void;
}) {
  const { t } = useTranslation();
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const [docType, setDocType] = useState<DocType>("radiology");
  const [autoDetect, setAutoDetect] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);

  const accept = useMemo(() => "application/pdf,.pdf", []);
  const filterPdfFiles = (files: File[]) =>
    files.filter((f) => f.type === "application/pdf" || f.name.toLowerCase().endsWith(".pdf")) as UploadedFile[];

  const handleFiles = useCallback(
    async (fileList: FileList | null) => {
      if (!fileList || fileList.length === 0) return;

      setError(null);
      setSuccess(false);
      setUploadProgress(null);

      const files = filterPdfFiles(Array.from(fileList));
      if (files.length === 0) {
        setError(t("uploadArea.onlyPdf"));
        return;
      }

      try {
        setIsUploading(true);
        onFilesAdded(files);

        // Alle Dateien sequentiell verarbeiten
        for (let i = 0; i < files.length; i++) {
          const file = files[i];
          const isFirst = i === 0;
          setUploadProgress(t("uploadArea.processingFile", { current: i + 1, total: files.length, name: file.name }));

          let finalDocType = docType;

          if (autoDetect) {
            setIsDetecting(true);
            const uploadRes = await uploadPdfWithText(file, "radiology");

            try {
              const classifyRes = await classifyDocTypeByDocId(uploadRes.id);
              finalDocType = classifyRes.doc_type;
              if (isFirst) setDocType(finalDocType);
            } catch (classifyError: any) {
              console.error("Auto-Detect failed:", classifyError);
            } finally {
              setIsDetecting(false);
            }

            onTextExtracted?.({ ...uploadRes, doc_type: finalDocType, append: !isFirst });
          } else {
            const res = await uploadPdfWithText(file, finalDocType);
            onTextExtracted?.({ ...res, append: !isFirst });
          }
        }

        setSuccess(true);
        setUploadProgress(null);
      } catch (e: any) {
        setError(e?.message ?? t("uploadArea.uploadErrorUnknown"));
      } finally {
        setIsUploading(false);
        setIsDetecting(false);
        setUploadProgress(null);
        if (inputRef.current) inputRef.current.value = "";
      }
    },
    [onFilesAdded, onTextExtracted, docType, autoDetect, t]
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
        aria-label={t("uploadArea.dropTitle")}
      >
        <Stack spacing={2} alignItems="center" maxWidth={520} mx="auto">
          <Paper variant="outlined" sx={{ p: 1.5, borderRadius: 3 }}>
            <CloudUploadIcon />
          </Paper>

          <Typography variant="h6">{t("uploadArea.dropTitle")}</Typography>
          <Typography variant="body2" color="text.secondary">
            {t("uploadArea.dropHint")}
          </Typography>

          <FormControlLabel
            control={
              <Switch
                checked={autoDetect}
                onChange={(e) => setAutoDetect(e.target.checked)}
                disabled={isUploading}
              />
            }
            label={
              <Stack direction="row" spacing={0.5} alignItems="center">
                <AutoFixHighIcon fontSize="small" />
                <Typography variant="body2">{t("uploadArea.autoDetect")}</Typography>
              </Stack>
            }
          />

          {isDetecting && (
            <Alert severity="info" sx={{ mt: 1 }}>
              <Stack direction="row" spacing={1} alignItems="center">
                <CircularProgress size={16} />
                <Typography variant="body2">{t("uploadArea.detecting")}</Typography>
              </Stack>
            </Alert>
          )}

          <Stack direction="row" spacing={1} justifyContent="center" flexWrap="wrap" sx={{ gap: 1 }}>
            <Button
              size="small"
              variant={docType === "radiology" ? "contained" : "outlined"}
              onClick={() => setDocType("radiology")}
              disabled={isUploading}
            >
              {t("docType.radiology")}
            </Button>
            <Button
              size="small"
              variant={docType === "radiotherapy" ? "contained" : "outlined"}
              onClick={() => setDocType("radiotherapy")}
              disabled={isUploading}
            >
              {t("docType.radiotherapy")}
            </Button>
            <Button
              size="small"
              variant={docType === "pathology" ? "contained" : "outlined"}
              onClick={() => setDocType("pathology")}
              disabled={isUploading}
            >
              {t("docType.pathology")}
            </Button>
            <Button
              size="small"
              variant={docType === "surgery" ? "contained" : "outlined"}
              onClick={() => setDocType("surgery")}
              disabled={isUploading}
            >
              {t("docType.surgery")}
            </Button>
            <Button
              size="small"
              variant={docType === "sarcoma_board" ? "contained" : "outlined"}
              onClick={() => setDocType("sarcoma_board")}
              disabled={isUploading}
            >
              {t("docType.sarcoma_board")}
            </Button>
            <Button
              size="small"
              variant={docType === "systemic_therapy" ? "contained" : "outlined"}
              onClick={() => setDocType("systemic_therapy")}
              disabled={isUploading}
            >
              {t("docType.systemic_therapy")}
            </Button>
          </Stack>

          {!autoDetect && (
            <Typography variant="caption" color="text.secondary">
              {t("uploadArea.selected")}: <strong>{t(`docType.${docType}`)}</strong>
            </Typography>
          )}
          {autoDetect && (
            <Typography variant="caption" color="primary">
              {t("uploadArea.autoDetectEnabled")}
            </Typography>
          )}

          <Stack direction="row" spacing={2} justifyContent="center" pt={1}>
            <Button
              variant="outlined"
              startIcon={isUploading ? <CircularProgress size={16} /> : <CloudUploadIcon />}
              onClick={() => inputRef.current?.click()}
              disabled={isUploading}
            >
              {isUploading ? (uploadProgress ?? t("uploadArea.uploading")) : t("uploadArea.chooseFiles")}
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
              {t("uploadArea.added")}
            </Alert>
          )}
        </Stack>
      </Paper>
    </Stack>
  );
}
