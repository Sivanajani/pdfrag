import { useCallback, useMemo, useState } from 'react'
import { CssBaseline, Container, Box, ThemeProvider } from '@mui/material'
import { makeTheme } from './theme'
import { useColorScheme } from './hooks/useColorScheme'
import AppHeader from './components/Header'
import UploadWizard, { type ExtractionResults } from './components/UploadWizard'
import ExtractedDataPanel from './components/ExtractedDataPanel'
import { useTranslation } from 'react-i18next'
import type {
  RadiologyEvent,
  RadiotherapyEvent,
  PathologyEvent,
  SurgeryEvent,
  SarcomaBoardEvent,
  SystemicTherapyEvent,
} from "./api";

export default function App() {
  const { t } = useTranslation()
  const { mode, setMode } = useColorScheme()
  const theme = useMemo(() => makeTheme(mode), [mode])

  const [radEvents, setRadEvents] = useState<RadiologyEvent[] | null>(null);
  const [radiotherapyEvents, setRadiotherapyEvents] = useState<RadiotherapyEvent[] | null>(null);
  const [pathologyEvents, setPathologyEvents] = useState<PathologyEvent[] | null>(null);
  const [surgeryEvents, setSurgeryEvents] = useState<SurgeryEvent[] | null>(null);
  const [sarcomaBoardEvents, setSarcomaBoardEvents] = useState<SarcomaBoardEvent[] | null>(null);
  const [systemicTherapyEvents, setSystemicTherapyEvents] = useState<SystemicTherapyEvent[] | null>(null);

  const handleResults = useCallback((results: ExtractionResults) => {
    setRadEvents(results.radiologyEvents.length > 0 ? results.radiologyEvents : null);
    setRadiotherapyEvents(results.radiotherapyEvents.length > 0 ? results.radiotherapyEvents : null);
    setPathologyEvents(results.pathologyEvents.length > 0 ? results.pathologyEvents : null);
    setSurgeryEvents(results.surgeryEvents.length > 0 ? results.surgeryEvents : null);
    setSarcomaBoardEvents(results.sarcomaBoardEvents.length > 0 ? results.sarcomaBoardEvents : null);
    setSystemicTherapyEvents(results.systemicTherapyEvents.length > 0 ? results.systemicTherapyEvents : null);
  }, []);

  // Generic inline-edit handler factory
  const makeUpdateHandler = <T,>(setter: React.Dispatch<React.SetStateAction<T[] | null>>) =>
    (row: number, field: string, value: string) => {
      setter(prev => prev?.map((e, i) => i === row ? { ...e, [field]: value } : e) ?? null);
    };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box display="flex" flexDirection="column" minHeight="100vh">
        <AppHeader
          mode={mode}
          onToggleMode={() => setMode(mode === 'dark' ? 'light' : 'dark')}
        />

        <Container maxWidth="lg" sx={{ flex: 1, py: 4 }}>
          <UploadWizard onResults={handleResults} />

          <ExtractedDataPanel
            loading={false}
            error={null}
            radiologyEvents={radEvents}
            radiotherapyEvents={radiotherapyEvents}
            pathologyEvents={pathologyEvents}
            surgeryEvents={surgeryEvents}
            sarcomaBoardEvents={sarcomaBoardEvents}
            systemicTherapyEvents={systemicTherapyEvents}
            onUpdateRadiology={makeUpdateHandler<RadiologyEvent>(setRadEvents)}
            onUpdateRadiotherapy={makeUpdateHandler<RadiotherapyEvent>(setRadiotherapyEvents)}
            onUpdatePathology={makeUpdateHandler<PathologyEvent>(setPathologyEvents)}
            onUpdateSurgery={makeUpdateHandler<SurgeryEvent>(setSurgeryEvents)}
            onUpdateSarcomaBoard={makeUpdateHandler<SarcomaBoardEvent>(setSarcomaBoardEvents)}
            onUpdateSystemicTherapy={makeUpdateHandler<SystemicTherapyEvent>(setSystemicTherapyEvents)}
          />
        </Container>

        <Box component="footer" sx={{ borderTop: 1, borderColor: 'divider', py: 2 }}>
          <Container maxWidth="lg" sx={{ fontSize: 12, opacity: 0.7 }}>
            &copy; {new Date().getFullYear()} RAG-MVP &middot; {t('footerPoc')}
          </Container>
        </Box>
      </Box>
    </ThemeProvider>
  )
}
