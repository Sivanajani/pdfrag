import { Paper, Typography, Stack, Button, Alert, CircularProgress, Box, Table, TableHead, TableRow, TableCell, TableBody } from '@mui/material';
import type { LlmExtractResponse } from '../api';

export default function ExtractedDataPanel({
  loading,
  error,
  result,
}: {
  loading: boolean;
  error: string | null;
  result: LlmExtractResponse | null;
}) {

  const downloadJson = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], {
      type: 'application/json;charset=utf-8;',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'extracted_data.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  const itemsToCsv = (items: LlmExtractResponse['items']): string => {
    if (!items.length) return '';
    const headers = Object.keys(items[0]);

    const headerRow = headers.join(',');
    const rows = items.map((item) =>
      headers
        .map((h) => {
          const value = (item as any)[h];
          const str =
            value === null || value === undefined
              ? ''
              : typeof value === 'string'
              ? value
              : String(value);
          const escaped = str.replace(/"/g, '""');
          return `"${escaped}"`;
        })
        .join(',')
    );

    return [headerRow, ...rows].join('\n');
  };

  const downloadCsv = () => {
    if (!result || !result.items.length) return;
    const csv = itemsToCsv(result.items);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'extracted_data.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Box mt={4}>
      <Typography variant="h6" gutterBottom>
        Extrahierte strukturierte Daten (LLM)
      </Typography>

      {loading && (
        <Stack direction="row" spacing={1} alignItems="center">
          <CircularProgress size={18} />
          <Typography variant="body2">Extrahiere Daten…</Typography>
        </Stack>
      )}

      {error && <Alert severity="error" sx={{ mt: 1 }}>{error}</Alert>}

      {result && result.items.length > 0 && (
        <Paper variant="outlined" sx={{ mt: 2, p: 2, borderRadius: 3 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Vorschau der extrahierten Items
          </Typography>

          <Box sx={{ overflowX: 'auto' }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  {Object.keys(result.items[0]).map((key) => (
                    <TableCell key={key}>{key}</TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {result.items.map((item, idx) => (
                  <TableRow key={idx}>
                    {Object.keys(result.items[0]).map((key) => (
                      <TableCell key={key}>
                        {(() => {
                          const value = (item as any)[key];
                          return value === null || value === undefined ? '' : String(value);
                        })()}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Box>

          <Stack spacing={2} direction="row" justifyContent="flex-end" mt={2}>
            <Button variant="outlined" size="small" onClick={downloadJson}>
              JSON herunterladen
            </Button>
            <Button variant="contained" size="small" onClick={downloadCsv}>
              CSV herunterladen
            </Button>
          </Stack>
        </Paper>
      )}

      {result && result.items.length === 0 && !loading && !error && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Keine Daten gefunden.
        </Typography>
      )}
    </Box>
  );
}
