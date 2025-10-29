import { Paper, Stack, Typography } from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'


export default function EmptyState() {
    return (
    <Paper variant="outlined" sx={{ p: 5, textAlign: 'center', borderRadius: 3 }}>
        <Stack spacing={1.5} alignItems="center">
            <SearchIcon />
            <Typography variant="subtitle1">Noch keine Dateien</Typography>
            <Typography variant="body2" color="text.secondary">Lade ein oder mehrere PDFs hoch, um zu starten.</Typography>
        </Stack>
    </Paper>
    )
}