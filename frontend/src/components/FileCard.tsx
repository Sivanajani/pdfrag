import { Card, CardContent, CardHeader, CardActions, Typography, IconButton } from '@mui/material'
import DescriptionIcon from '@mui/icons-material/Description'
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline'
import type { UploadedFile } from '../types/files'
import { formatBytes } from '../utils/format'


export default function FileCard({ file, onRemove }: { file: UploadedFile; onRemove: () => void }) {
    return (
    <Card variant="outlined" sx={{ borderRadius: 3 }}>
        <CardHeader
            avatar={<DescriptionIcon />} title={<Typography variant="subtitle1" noWrap title={file.name}>{file.name}</Typography>}
            subheader={<Typography variant="caption" color="text.secondary">{formatBytes(file.size)}</Typography>}
        />
        <CardContent sx={{ pt: 0 }}>
            <Typography variant="body2" color="text.secondary">Bereit zur Verarbeitung.</Typography>
        </CardContent>
        <CardActions sx={{ justifyContent: 'flex-end' }}>
            <IconButton onClick={onRemove} aria-label="Entfernen">
                <DeleteOutlineIcon />
            </IconButton>
        </CardActions>
    </Card>
    )
}