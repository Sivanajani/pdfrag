import { Dialog, DialogTitle, DialogContent, Typography } from '@mui/material';

export default function TextPreviewDialog({
  open, onClose, title, text,
}: { open: boolean; onClose: () => void; title?: string; text?: string }) {
  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
      <DialogTitle>{title ?? 'Extrahierter Text'}</DialogTitle>
      <DialogContent dividers>
        <Typography component="pre" sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: 14 }}>
          {text || 'Kein Text gefunden (eventuell gescannt/OCR nötig).'}
        </Typography>
      </DialogContent>
    </Dialog>
  );
}
