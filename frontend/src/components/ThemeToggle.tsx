import { IconButton, Tooltip } from '@mui/material'
import DarkModeIcon from '@mui/icons-material/DarkMode'
import LightModeIcon from '@mui/icons-material/LightMode'


export default function ThemeToggle({ mode, onToggle }: { mode: 'light' | 'dark'; onToggle: () => void }) {
    const isDark = mode === 'dark'
    return (
    <Tooltip title={isDark ? 'Helles Thema' : 'Dunkles Thema'}>
        <IconButton color="inherit" onClick={onToggle} size="small" sx={{ border: 1, borderColor: 'divider', borderRadius: 2 }}>
            {isDark ? <LightModeIcon fontSize="small" /> : <DarkModeIcon fontSize="small" />}
        </IconButton>
    </Tooltip>
    )
}