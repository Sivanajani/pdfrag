import { useMemo, useState } from 'react'
import { CssBaseline, Container, Box, ThemeProvider } from '@mui/material'
import { makeTheme } from './theme'
import { useColorScheme } from './hooks/useColorScheme'
import AppHeader from './components/Header' 
import UploadArea from './components/UploadArea'
import FileCard from './components/FileCard'
import EmptyState from './components/EmptyState'
import type { UploadedFile } from './types/files'
import TextPreviewDialog from './components/TextPreviewDialog'
import ExtractedDataPanel from './components/ExtractedDataPanel'
import {
  llmExtractRadiologyByDocId,
  type RadiologyEvent,
  llmExtractRadiotherapyByDocId,
  type RadiotherapyEvent,
  llmExtractPathologyByDocId,
  type PathologyEvent,
  llmExtractSurgeryByDocId,
  type SurgeryEvent,
  llmExtractSarcomaBoardByDocId,
  type SarcomaBoardEvent,
  llmExtractSystemicTherapyByDocId,
  type SystemicTherapyEvent,
} from "./api";



export default function App() {

  const [llmLoading, setLlmLoading] = useState(false);
  const [llmError, setLlmError] = useState<string | null>(null);



  const { mode, setMode } = useColorScheme()
  const theme = useMemo(() => makeTheme(mode), [mode])
  const [files, setFiles] = useState<UploadedFile[]>([])

  const [previewOpen, setPreviewOpen] = useState(false)
  const [previewTitle, setPreviewTitle] = useState<string | undefined>()
  const [previewText, setPreviewText] = useState<string | undefined>()

  const [radEvents, setRadEvents] = useState<RadiologyEvent[] | null>(null);
  const [radiotherapyEvents, setRadiotherapyEvents] = useState<RadiotherapyEvent[] | null>(null);
  const [pathologyEvents, setPathologyEvents] = useState<PathologyEvent[] | null>(null);
  const [surgeryEvents, setSurgeryEvents] = useState<SurgeryEvent[] | null>(null);
  const [sarcomaBoardEvents, setSarcomaBoardEvents] = useState<SarcomaBoardEvent[] | null>(null);
  const [systemicTherapyEvents, setSystemicTherapyEvents] = useState<SystemicTherapyEvent[] | null>(null);


  const onFilesAdded = (newFiles: UploadedFile[]) => {
    const key = (f: UploadedFile) => `${f.name}_${f.size}_${f.lastModified}`
    const existing = new Set(files.map(key))
    const merged = [...files, ...newFiles.filter((f) => !existing.has(key(f)))]
    setFiles(merged)
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box display="flex" flexDirection="column" minHeight="100vh">
        <AppHeader
          mode={mode}
          onToggleMode={() => setMode(mode === 'dark' ? 'light' : 'dark')}
        />

        <Container maxWidth="lg" sx={{ flex: 1, py: 4 }}>
          <UploadArea
            onFilesAdded={onFilesAdded}
            onTextExtracted={(payload) => {
              setPreviewTitle(payload.filename);
              setPreviewText(payload.text);
              setPreviewOpen(true);

              setLlmError(null);
              setLlmLoading(true);

              const shouldAppend = payload.append === true;

              // Bei erster Datei: Reset alle Event-States
              if (!shouldAppend) {
                setRadEvents(null);
                setRadiotherapyEvents(null);
                setPathologyEvents(null);
                setSurgeryEvents(null);
                setSarcomaBoardEvents(null);
                setSystemicTherapyEvents(null);
              }

              // Document-type specific extraction
              const docType = payload.doc_type || 'radiology';

              if (docType === 'radiology') {
                llmExtractRadiologyByDocId(payload.id)
                  .then((res) => setRadEvents(prev => [...(prev || []), ...res.events]))
                  .catch((err: any) => setLlmError(err?.message ?? 'Extraktion fehlgeschlagen'))
                  .finally(() => setLlmLoading(false));
              } else if (docType === 'radiotherapy') {
                llmExtractRadiotherapyByDocId(payload.id)
                  .then((res) => setRadiotherapyEvents(prev => [...(prev || []), ...res.events]))
                  .catch((err: any) => setLlmError(err?.message ?? 'Extraktion fehlgeschlagen'))
                  .finally(() => setLlmLoading(false));
              } else if (docType === 'pathology') {
                llmExtractPathologyByDocId(payload.id)
                  .then((res) => setPathologyEvents(prev => [...(prev || []), ...res.events]))
                  .catch((err: any) => setLlmError(err?.message ?? 'Extraktion fehlgeschlagen'))
                  .finally(() => setLlmLoading(false));
              } else if (docType === 'surgery') {
                llmExtractSurgeryByDocId(payload.id)
                  .then((res) => setSurgeryEvents(prev => [...(prev || []), ...res.events]))
                  .catch((err: any) => setLlmError(err?.message ?? 'Extraktion fehlgeschlagen'))
                  .finally(() => setLlmLoading(false));
              } else if (docType === 'sarcoma_board') {
                llmExtractSarcomaBoardByDocId(payload.id)
                  .then((res) => setSarcomaBoardEvents(prev => [...(prev || []), ...res.events]))
                  .catch((err: any) => setLlmError(err?.message ?? 'Extraktion fehlgeschlagen'))
                  .finally(() => setLlmLoading(false));
              } else if (docType === 'systemic_therapy') {
                llmExtractSystemicTherapyByDocId(payload.id)
                  .then((res) => setSystemicTherapyEvents(prev => [...(prev || []), ...res.events]))
                  .catch((err: any) => setLlmError(err?.message ?? 'Extraktion fehlgeschlagen'))
                  .finally(() => setLlmLoading(false));
              } else {
                setLlmError(`Unbekannter Dokumenttyp: "${docType}"`);
                setLlmLoading(false);
              }
            }}
          />


          <Box mt={3}>
            {files.length === 0 ? (
              <EmptyState />
            ) : (
              
              <Box
                display="grid"
                gap={2}
                sx={{
                  gridTemplateColumns: {
                    xs: '1fr',
                    sm: '1fr 1fr',
                    md: '1fr 1fr 1fr',
                  },
                }}
              >
                {files.map((f) => (
                  <Box key={`${f.name}_${f.size}_${f.lastModified}`}>
                    <FileCard
                      file={f}
                      onRemove={() =>
                        setFiles((prev) => prev.filter((p) => p !== f))
                      }
                    />
                  </Box>
                ))}
              </Box>
            )}
          </Box>

          <ExtractedDataPanel
          loading={llmLoading}
          error={llmError}
          radiologyEvents={radEvents}
          radiotherapyEvents={radiotherapyEvents}
          pathologyEvents={pathologyEvents}
          surgeryEvents={surgeryEvents}
          sarcomaBoardEvents={sarcomaBoardEvents}
          systemicTherapyEvents={systemicTherapyEvents}
          />
        </Container>

        <Box component="footer" sx={{ borderTop: 1, borderColor: 'divider', py: 2 }}>
          <Container maxWidth="lg" sx={{ fontSize: 12, opacity: 0.7 }}>
            © {new Date().getFullYear()} RAG-MVP · Proof of Concept
          </Container>
        </Box>
      </Box>
      
      <TextPreviewDialog
        open={previewOpen}
        onClose={() => setPreviewOpen(false)}
        title={previewTitle}
        text={previewText}
      />


    </ThemeProvider>
  )
}
