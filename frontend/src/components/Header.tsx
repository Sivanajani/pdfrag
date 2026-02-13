import { AppBar, Toolbar, Typography, Stack, Box, Paper } from '@mui/material'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import ThemeToggle from './ThemeToggle'
import LanguageToggle from './LanguageToggle'
import { useTranslation } from 'react-i18next'

export default function AppHeader({ mode, onToggleMode }: { mode: 'light' | 'dark'; onToggleMode: () => void }) {
    const { t } = useTranslation()
    return (
    <AppBar color="default" position="sticky" elevation={0} sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: 'background.paper', backdropFilter: 'blur(6px)' }}>
        <Toolbar sx={{ justifyContent: 'space-between' }}>
            <Stack direction="row" spacing={2} alignItems="center">
                <Paper variant="outlined" sx={{ p: 1, borderRadius: 2 }}>
                    <CloudUploadIcon fontSize="small" />
                </Paper>
                <Box>
                    <Typography variant="h6" sx={{ lineHeight: 1 }}>RAG-MVP</Typography>
                    <Typography variant="caption" color="text.secondary">{t('appSubtitle')}</Typography>
                </Box>
            </Stack>
            <Stack direction="row" spacing={1} alignItems="center">
                <LanguageToggle />
                <ThemeToggle mode={mode} onToggle={onToggleMode} />
            </Stack>
        </Toolbar>
    </AppBar>
    )
}
