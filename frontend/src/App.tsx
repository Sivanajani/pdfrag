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
  llmExtractByDocId,
  type LlmExtractResponse,
  llmExtractRadiologyByDocId,
  type RadiologyEvent,
} from "./api";



export default function App() {

  const [llmResult, setLlmResult] = useState<LlmExtractResponse | null>(null);
  const [llmLoading, setLlmLoading] = useState(false);
  const [llmError, setLlmError] = useState<string | null>(null);



  const { mode, setMode } = useColorScheme()
  const theme = useMemo(() => makeTheme(mode), [mode])
  const [files, setFiles] = useState<UploadedFile[]>([])

  const [previewOpen, setPreviewOpen] = useState(false)
  const [previewTitle, setPreviewTitle] = useState<string | undefined>()
  const [previewText, setPreviewText] = useState<string | undefined>()

  const [radEvents, setRadEvents] = useState<RadiologyEvent[] | null>(null);


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
              setLlmResult(null);
              setLlmLoading(true);
              setRadEvents(null);

              llmExtractByDocId(payload.id)
                .then((res) => setLlmResult(res))
                .catch((err: any) => setLlmError(err?.message ?? 'LLM Fehler'))
                .finally(() => setLlmLoading(false));
              
              llmExtractRadiologyByDocId(payload.id)
                .then((res) => setRadEvents(res.events))
                .catch(() => {
                // optional: ignorieren oder eigenes radError machen
                setRadEvents(null);
              });
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
          result={llmResult}
          radiologyEvents={radEvents}
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
