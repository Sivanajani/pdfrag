import { useEffect, useState } from 'react'


export function useColorScheme() {
const [mode, setMode] = useState<'light' | 'dark'>(() => {
const saved = localStorage.getItem('color-scheme') as 'light' | 'dark' | null
if (saved) return saved
return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
})


useEffect(() => {
localStorage.setItem('color-scheme', mode)
}, [mode])


return { mode, setMode }
}