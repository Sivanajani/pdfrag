import { createTheme } from '@mui/material/styles'


export const makeTheme = (mode: 'light' | 'dark') => createTheme({
palette: {
mode,
primary: { main: '#2563eb' },
secondary: { main: '#7c3aed' },
},
shape: { borderRadius: 12 },
components: {
MuiPaper: { defaultProps: { elevation: 1 } },
},
})