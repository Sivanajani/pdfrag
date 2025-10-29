import { useCallback, useMemo, useRef, useState } from 'react'
import { Paper, Stack, Typography, Button, CircularProgress, Alert } from '@mui/material'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline'
import type { UploadedFile } from '../types/files'
import { uploadPdfWithText, type UploadWithTextResponse } from '../api'   // ⬅️ neu

export default function UploadArea({
  onFilesAdded,
  onTextExtracted,                         // ⬅️ neu
}: {
  onFilesAdded: (files: UploadedFile[]) => void
  onTextExtracted?: (payload: UploadWithTextResponse) => void
}) {
  const inputRef = useRef<HTMLInputElement | null>(null)
  const [isDragOver, setIsDragOver] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const accept = useMemo(() => 'application/pdf,.pdf', [])
  const filterPdfFiles = (files: File[]) =>
    files.filter((f) => f.type === 'application/pdf' || f.name.toLowerCase().endsWith('.pdf')) as UploadedFile[]

  const handleFiles = useCallback(async (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) return
    setError(null); setSuccess(false)

    const files = filterPdfFiles(Array.from(fileList))
    if (files.length === 0) {
      setError('Bitte nur PDF-Dateien hochladen.')
      return
    }

    try {
      setIsUploading(true)
      onFilesAdded(files)

      // 👉 Backend: pro Datei hochladen & Text holen
      // Wir zeigen (nur) das Ergebnis der ersten Datei sofort im Dialog
      const first = files[0]
      const res = await uploadPdfWithText(first)
      onTextExtracted?.(res)

      // (Optional) Weitere Dateien ebenfalls hochladen:
      // for (const f of files.slice(1)) await uploadPdfWithText(f)

      setSuccess(true)
    } catch (e: any) {
      setError(e?.message ?? 'Unbekannter Fehler beim Upload')
    } finally {
      setIsUploading(false)
      if (inputRef.current) inputRef.current.value = ''
    }
  }, [onFilesAdded, onTextExtracted])

  return (
    <Paper
      variant="outlined"
      sx={{
        p: 4, textAlign: 'center', borderStyle: 'dashed',
        borderColor: isDragOver ? 'primary.main' : 'divider',
        bgcolor: isDragOver ? 'action.hover' : 'background.paper',
        transition: 'all .15s ease-in-out',
      }}
      onDragOver={(e) => { e.preventDefault(); setIsDragOver(true) }}
      onDragLeave={() => setIsDragOver(false)}
      onDrop={(e) => { e.preventDefault(); setIsDragOver(false); handleFiles(e.dataTransfer.files) }}
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

        <Stack direction="row" spacing={2} justifyContent="center" pt={1}>
          <Button
            variant="outlined"
            startIcon={isUploading ? <CircularProgress size={16} /> : <CloudUploadIcon />}
            onClick={() => inputRef.current?.click()}
            disabled={isUploading}
          >
            {isUploading ? 'Hochladen…' : 'Dateien auswählen'}
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

        {error && <Alert severity="error" icon={<ErrorOutlineIcon fontSize="small" />} sx={{ mt: 1 }}>{error}</Alert>}
        {success && <Alert severity="success" icon={<CheckCircleIcon fontSize="small" />} sx={{ mt: 1 }}>Dateien hinzugefügt</Alert>}
      </Stack>
    </Paper>
  )
}
