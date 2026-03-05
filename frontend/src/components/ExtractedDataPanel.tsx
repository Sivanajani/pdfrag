import { useState, useRef, useEffect } from 'react';
import { Paper, Typography, Stack, Button, Alert, CircularProgress, Box, Table, TableHead, TableRow, TableCell, TableBody, TextField } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import * as XLSX from 'xlsx';
import { csvValue, buildCsv } from '../utils/csv';
import { useTranslation } from 'react-i18next';
import type {
  RadiologyEvent,
  RadiotherapyEvent,
  PathologyEvent,
  SurgeryEvent,
  SarcomaBoardEvent,
  SystemicTherapyEvent,
} from '../api';

function downloadCsv(headers: string[], rows: any[], filename: string) {
  const csv = buildCsv(headers, rows);
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function downloadXlsx(headers: string[], rows: any[], filename: string) {
  const data = rows.map((r) => {
    const obj: Record<string, string> = {};
    headers.forEach((h) => { obj[h] = csvValue((r as any)[h], h); });
    return obj;
  });
  const ws = XLSX.utils.json_to_sheet(data, { header: headers });
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "Data");
  XLSX.writeFile(wb, filename);
}

function downloadJson(data: any, filename: string) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function ExportButtons({ headers, rows, baseName }: { headers: string[]; rows: any[]; baseName: string }) {
  return (
    <Stack spacing={1} direction="row" justifyContent="flex-end" mt={2}>
      <Button variant="outlined" size="small" onClick={() => downloadJson(rows, `${baseName}.json`)}>
        JSON
      </Button>
      <Button variant="outlined" size="small" onClick={() => downloadCsv(headers, rows, `${baseName}.csv`)}>
        CSV
      </Button>
      <Button variant="contained" size="small" onClick={() => downloadXlsx(headers, rows, `${baseName}.xlsx`)}>
        XLSX
      </Button>
    </Stack>
  );
}

// --- EditableCell ---

type EditingCell = { table: string; row: number; field: string } | null;

function EditableCell({
  value,
  tableType,
  rowIdx,
  field,
  editingCell,
  onStartEdit,
  onCommit,
  sx,
}: {
  value: string;
  tableType: string;
  rowIdx: number;
  field: string;
  editingCell: EditingCell;
  onStartEdit: (table: string, row: number, field: string) => void;
  onCommit: (table: string, row: number, field: string, newValue: string) => void;
  sx?: any;
}) {
  const isEditing =
    editingCell?.table === tableType &&
    editingCell?.row === rowIdx &&
    editingCell?.field === field;

  const inputRef = useRef<HTMLInputElement>(null);
  const [draft, setDraft] = useState(value);

  useEffect(() => {
    if (isEditing) {
      setDraft(value);
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  }, [isEditing, value]);

  if (isEditing) {
    return (
      <TableCell sx={{ ...sx, p: 0.5 }}>
        <TextField
          inputRef={inputRef}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              onCommit(tableType, rowIdx, field, draft);
            } else if (e.key === "Escape") {
              onCommit(tableType, rowIdx, field, value); // revert
            }
          }}
          onBlur={() => onCommit(tableType, rowIdx, field, draft)}
          size="small"
          variant="outlined"
          fullWidth
          sx={{ minWidth: 60 }}
        />
      </TableCell>
    );
  }

  return (
    <TableCell
      sx={{
        ...sx,
        cursor: "pointer",
        "&:hover .edit-icon": { opacity: 1 },
      }}
      onClick={() => onStartEdit(tableType, rowIdx, field)}
    >
      <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
        <span style={{ flex: 1 }}>{value}</span>
        <EditIcon
          className="edit-icon"
          sx={{ fontSize: 14, opacity: 0, transition: "opacity 0.15s", color: "action.active" }}
        />
      </Box>
    </TableCell>
  );
}

// Patient ID header cell style
const pidHeaderSx = { fontWeight: 'bold', bgcolor: 'action.hover', position: 'sticky' as const, left: 0, zIndex: 1 };
const pidCellSx = { fontWeight: 'bold', position: 'sticky' as const, left: 0, bgcolor: 'background.paper', zIndex: 1 };

export default function ExtractedDataPanel({
  loading,
  error,
  radiologyEvents,
  radiotherapyEvents,
  pathologyEvents,
  surgeryEvents,
  sarcomaBoardEvents,
  systemicTherapyEvents,
  onUpdateRadiology,
  onUpdateRadiotherapy,
  onUpdatePathology,
  onUpdateSurgery,
  onUpdateSarcomaBoard,
  onUpdateSystemicTherapy,
}: {
  loading: boolean;
  error: string | null;
  radiologyEvents?: RadiologyEvent[] | null;
  radiotherapyEvents?: RadiotherapyEvent[] | null;
  pathologyEvents?: PathologyEvent[] | null;
  surgeryEvents?: SurgeryEvent[] | null;
  sarcomaBoardEvents?: SarcomaBoardEvent[] | null;
  systemicTherapyEvents?: SystemicTherapyEvent[] | null;
  onUpdateRadiology?: (row: number, field: string, value: string) => void;
  onUpdateRadiotherapy?: (row: number, field: string, value: string) => void;
  onUpdatePathology?: (row: number, field: string, value: string) => void;
  onUpdateSurgery?: (row: number, field: string, value: string) => void;
  onUpdateSarcomaBoard?: (row: number, field: string, value: string) => void;
  onUpdateSystemicTherapy?: (row: number, field: string, value: string) => void;
}) {
  const { t } = useTranslation();
  const [editingCell, setEditingCell] = useState<EditingCell>(null);

  const onStartEdit = (table: string, row: number, field: string) => {
    setEditingCell({ table, row, field });
  };

  const onCommit = (table: string, row: number, field: string, newValue: string) => {
    setEditingCell(null);
    const handlers: Record<string, ((row: number, field: string, value: string) => void) | undefined> = {
      radiology: onUpdateRadiology,
      radiotherapy: onUpdateRadiotherapy,
      pathology: onUpdatePathology,
      surgery: onUpdateSurgery,
      sarcomaBoard: onUpdateSarcomaBoard,
      systemicTherapy: onUpdateSystemicTherapy,
    };
    handlers[table]?.(row, field, newValue);
  };

  // Helper to create editable cell props
  const ec = (tableType: string, rowIdx: number, field: string, value: string, sx?: any) => ({
    value,
    tableType,
    rowIdx,
    field,
    editingCell,
    onStartEdit,
    onCommit,
    sx,
  });

  return (
    <Box mt={4}>
      <Typography variant="h6" gutterBottom>
        {t('extractedData.title')}
      </Typography>

      {loading && (
        <Stack direction="row" spacing={1} alignItems="center">
          <CircularProgress size={18} />
          <Typography variant="body2">{t('extractedData.loading')}</Typography>
        </Stack>
      )}

      {error && <Alert severity="error" sx={{ mt: 1 }}>{error}</Alert>}

      {/* --- RADIOLOGY --- */}
      {radiologyEvents && radiologyEvents.length > 0 && (() => {
        const headers = ["patient_id", "exam_date", "exam_type", "exam_type_comment", "imaging_timing", "imaging_type", "location_of_lesion", "largest_lesion_size_in_mm", "medium_lesion_size_in_mm", "smallest_lesion_size_in_mm", "recist_response", "choi_response", "irecist_response", "pet_response", "local_disease_status", "local_disease_measurable", "local_disease_report_largest_diameter", "local_disease_qualitative_mri_response", "local_disease_radiologist_confidence", "local_disease_pet_metabolic_response", "metastasis_presence", "metastasis", "anatomic_location_of_metastasis", "metastasis_location_lung_count", "metastasis_location_pleura_count", "metastasis_location_bone_count", "metastasis_location_liver_count", "metastasis_location_soft_tissue_count", "metastasis_location_lymph_node_count", "metastasis_location_brain_count", "metastasis_location_other_count", "metastasis_target_lesion_count", "metastasis_longest_diameter_mm", "metastasis_indeterminate_category", "radiology_report", "report_date"];
        return (
          <Paper variant="outlined" sx={{ mt: 3, p: 2, borderRadius: 3 }}>
            <Typography variant="subtitle1" gutterBottom>Radiology</Typography>
            <Box sx={{ overflowX: "auto", maxWidth: "100%" }}>
              <Table size="small" sx={{ minWidth: 3200 }}>
                <TableHead>
                  <TableRow>
                    <TableCell sx={pidHeaderSx}>Patient ID</TableCell>
                    <TableCell sx={{ fontWeight: 'bold', bgcolor: 'primary.light', color: 'white' }}>Exam Date *</TableCell>
                    <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Exam Type</TableCell>
                    <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Exam Type Comment</TableCell>
                    <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Imaging Timing</TableCell>
                    <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Imaging Type</TableCell>
                    <TableCell sx={{ bgcolor: 'warning.light' }}>Location of Lesion</TableCell>
                    <TableCell sx={{ bgcolor: 'warning.light' }}>Largest Lesion (mm)</TableCell>
                    <TableCell sx={{ bgcolor: 'warning.light' }}>Medium Lesion (mm)</TableCell>
                    <TableCell sx={{ bgcolor: 'warning.light' }}>Smallest Lesion (mm)</TableCell>
                    <TableCell sx={{ bgcolor: 'success.light' }}>RECIST Response</TableCell>
                    <TableCell sx={{ bgcolor: 'success.light' }}>Choi Response</TableCell>
                    <TableCell sx={{ bgcolor: 'success.light' }}>iRECIST Response</TableCell>
                    <TableCell sx={{ bgcolor: 'success.light' }}>PET Response</TableCell>
                    <TableCell sx={{ bgcolor: 'info.light' }}>Local Disease Status</TableCell>
                    <TableCell sx={{ bgcolor: 'info.light' }}>Local Disease Measurable</TableCell>
                    <TableCell sx={{ bgcolor: 'info.light' }}>Local Disease Diameter (mm)</TableCell>
                    <TableCell sx={{ bgcolor: 'info.light' }}>Local MRI Response</TableCell>
                    <TableCell sx={{ bgcolor: 'info.light' }}>Radiologist Confidence (1-5)</TableCell>
                    <TableCell sx={{ bgcolor: 'info.light' }}>Local PET Response</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>Metastasis Presence</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>Metastasis Status</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>Anatomic Locations</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>Lung Count</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>Pleura Count</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>Bone Count</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>Liver Count</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>Soft Tissue Count</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>Lymph Node Count</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>Brain Count</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>Other Count</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>Target Lesion Count</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>Longest Diameter (mm)</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>Indeterminate Category</TableCell>
                    <TableCell sx={{ bgcolor: 'secondary.light' }}>Radiology Report</TableCell>
                    <TableCell sx={{ bgcolor: 'secondary.light' }}>Report Date</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {radiologyEvents.map((e, idx) => (
                    <TableRow key={idx}>
                      <EditableCell {...ec("radiology", idx, "patient_id", String((e as any).patient_id ?? ""), pidCellSx)} />
                      <EditableCell {...ec("radiology", idx, "exam_date", String(e.exam_date ?? ""), { fontWeight: 'bold' })} />
                      <EditableCell {...ec("radiology", idx, "exam_type", String(e.exam_type ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "exam_type_comment", String(e.exam_type_comment ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "imaging_timing", String(e.imaging_timing ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "imaging_type", String(e.imaging_type ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "location_of_lesion", String(e.location_of_lesion ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "largest_lesion_size_in_mm", String(e.largest_lesion_size_in_mm ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "medium_lesion_size_in_mm", String(e.medium_lesion_size_in_mm ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "smallest_lesion_size_in_mm", String(e.smallest_lesion_size_in_mm ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "recist_response", String(e.recist_response ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "choi_response", String(e.choi_response ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "irecist_response", String(e.irecist_response ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "pet_response", String(e.pet_response ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "local_disease_status", String(e.local_disease_status ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "local_disease_measurable", String(e.local_disease_measurable ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "local_disease_report_largest_diameter", String(e.local_disease_report_largest_diameter ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "local_disease_qualitative_mri_response", String(e.local_disease_qualitative_mri_response ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "local_disease_radiologist_confidence", String(e.local_disease_radiologist_confidence ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "local_disease_pet_metabolic_response", String(e.local_disease_pet_metabolic_response ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "metastasis_presence", e.metastasis_presence != null ? (e.metastasis_presence ? "Yes" : "No") : "")} />
                      <EditableCell {...ec("radiology", idx, "metastasis", String(e.metastasis ?? ""))} />
                      <TableCell>{e.anatomic_location_of_metastasis?.join(", ") ?? ""}</TableCell>
                      <EditableCell {...ec("radiology", idx, "metastasis_location_lung_count", String(e.metastasis_location_lung_count ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "metastasis_location_pleura_count", String(e.metastasis_location_pleura_count ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "metastasis_location_bone_count", String(e.metastasis_location_bone_count ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "metastasis_location_liver_count", String(e.metastasis_location_liver_count ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "metastasis_location_soft_tissue_count", String(e.metastasis_location_soft_tissue_count ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "metastasis_location_lymph_node_count", String(e.metastasis_location_lymph_node_count ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "metastasis_location_brain_count", String(e.metastasis_location_brain_count ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "metastasis_location_other_count", String(e.metastasis_location_other_count ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "metastasis_target_lesion_count", String(e.metastasis_target_lesion_count ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "metastasis_longest_diameter_mm", String(e.metastasis_longest_diameter_mm ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "metastasis_indeterminate_category", String(e.metastasis_indeterminate_category ?? ""))} />
                      <EditableCell {...ec("radiology", idx, "radiology_report", String(e.radiology_report ?? ""), { maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} />
                      <EditableCell {...ec("radiology", idx, "report_date", String(e.report_date ?? ""))} />
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
            <ExportButtons headers={headers} rows={radiologyEvents} baseName="radiology_events" />
          </Paper>
        );
      })()}

      {/* --- RADIOTHERAPY --- */}
      {radiotherapyEvents && radiotherapyEvents.length > 0 && (() => {
        const headers = ["patient_id", "institution_id", "responsible_oncologist_id", "referral_date", "first_contact_date", "therapy_start_date", "therapy_end_date", "indications", "therapy_types", "total_dose_in_gy", "given_fractions", "ptv_volume_in_cm3", "gtv_volume_in_cm3", "was_tumor_located_in_radiated_area", "was_tumor_located_with_pre_existing_lymph_edema", "hyperthermia_status", "comments"];
        return (
          <Paper variant="outlined" sx={{ mt: 3, p: 2, borderRadius: 3 }}>
            <Typography variant="subtitle1" gutterBottom>Radiotherapy</Typography>
            <Box sx={{ overflowX: "auto", maxWidth: "100%" }}>
              <Table size="small" sx={{ minWidth: 2000 }}>
                <TableHead>
                    <TableRow>
                      <TableCell sx={pidHeaderSx}>Patient ID</TableCell>
                      <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Institution ID</TableCell>
                      <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Oncologist ID</TableCell>
                      <TableCell sx={{ fontWeight: 'bold', bgcolor: 'primary.light', color: 'white' }}>Referral Date</TableCell>
                      <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>First Contact</TableCell>
                      <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Therapy Start</TableCell>
                    <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Therapy End</TableCell>
                    <TableCell sx={{ bgcolor: 'warning.light' }}>Indications</TableCell>
                    <TableCell sx={{ bgcolor: 'warning.light' }}>Therapy Types</TableCell>
                    <TableCell sx={{ bgcolor: 'success.light' }}>Total Dose (Gy)</TableCell>
                    <TableCell sx={{ bgcolor: 'success.light' }}>Fractions</TableCell>
                    <TableCell sx={{ bgcolor: 'info.light' }}>PTV (cm3)</TableCell>
                    <TableCell sx={{ bgcolor: 'info.light' }}>GTV (cm3)</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>Tumor in radiated area</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>Pre-existing lymphedema</TableCell>
                    <TableCell sx={{ bgcolor: 'secondary.light' }}>Hyperthermia</TableCell>
                    <TableCell sx={{ bgcolor: 'secondary.light' }}>Comments</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {radiotherapyEvents.map((e, idx) => (
                    <TableRow key={idx}>
                      <EditableCell {...ec("radiotherapy", idx, "patient_id", String((e as any).patient_id ?? ""), pidCellSx)} />
                      <EditableCell {...ec("radiotherapy", idx, "institution_id", String((e as any).institution_id ?? ""))} />
                      <EditableCell {...ec("radiotherapy", idx, "responsible_oncologist_id", String((e as any).responsible_oncologist_id ?? ""))} />
                      <EditableCell {...ec("radiotherapy", idx, "referral_date", String(e.referral_date ?? ""), { fontWeight: 'bold' })} />
                      <EditableCell {...ec("radiotherapy", idx, "first_contact_date", String(e.first_contact_date ?? ""))} />
                      <EditableCell {...ec("radiotherapy", idx, "therapy_start_date", String(e.therapy_start_date ?? ""))} />
                      <EditableCell {...ec("radiotherapy", idx, "therapy_end_date", String(e.therapy_end_date ?? ""))} />
                      <TableCell>{e.indications?.join(", ") ?? ""}</TableCell>
                      <TableCell>{e.therapy_types?.join(", ") ?? ""}</TableCell>
                      <EditableCell {...ec("radiotherapy", idx, "total_dose_in_gy", String(e.total_dose_in_gy ?? ""))} />
                      <EditableCell {...ec("radiotherapy", idx, "given_fractions", String(e.given_fractions ?? ""))} />
                      <EditableCell {...ec("radiotherapy", idx, "ptv_volume_in_cm3", String(e.ptv_volume_in_cm3 ?? ""))} />
                      <EditableCell {...ec("radiotherapy", idx, "gtv_volume_in_cm3", String(e.gtv_volume_in_cm3 ?? ""))} />
                      <EditableCell {...ec("radiotherapy", idx, "was_tumor_located_in_radiated_area", e.was_tumor_located_in_radiated_area == null ? "" : String(e.was_tumor_located_in_radiated_area))} />
                      <EditableCell {...ec("radiotherapy", idx, "was_tumor_located_with_pre_existing_lymph_edema", e.was_tumor_located_with_pre_existing_lymph_edema == null ? "" : String(e.was_tumor_located_with_pre_existing_lymph_edema))} />
                      <EditableCell {...ec("radiotherapy", idx, "hyperthermia_status", String(e.hyperthermia_status ?? ""))} />
                      <EditableCell {...ec("radiotherapy", idx, "comments", String(e.comments ?? ""), { maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} />
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
            <ExportButtons headers={headers} rows={radiotherapyEvents} baseName="radiotherapy_events" />
          </Paper>
        );
      })()}

      {/* --- PATHOLOGY --- */}
      {pathologyEvents && pathologyEvents.length > 0 && (() => {
        const headers = ["patient_id", "institution_id", "responsible_pathologist_id", "biopsy_type", "biopsied_lesion_type", "biopsy_resection_date", "registrate_date", "first_report_date", "final_report_date", "report_date", "prior_treatment", "who_diagnosis", "diagnostic_grading", "judgment_of_surgical_margin", "closest_distance_to_margin_mm", "biological_barrier_to_closest_margin", "biological_barrier_to_closest_margin_comment", "proliferation_index", "mitoses_per_10hpf", "extent_of_necrosis", "eortc_response_grade", "ihc_performed_status", "ihc_result", "fish_performed_status", "fish_result", "rna_performed_status", "rna_result", "dna_performed_status", "dna_result", "report"];
        return (
          <Paper variant="outlined" sx={{ mt: 3, p: 2, borderRadius: 3 }}>
            <Typography variant="subtitle1" gutterBottom>Pathology</Typography>
            <Box sx={{ overflowX: "auto", maxWidth: "100%" }}>
              <Table size="small" sx={{ minWidth: 3500 }}>
                <TableHead>
                  <TableRow>
                    <TableCell sx={pidHeaderSx}>Patient ID</TableCell>
                    <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Institution ID</TableCell>
                    <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Pathologist ID</TableCell>
                    <TableCell sx={{ fontWeight: 'bold', bgcolor: 'primary.light', color: 'white' }}>Biopsy Type</TableCell>
                    <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Lesion Type</TableCell>
                    <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Biopsy Date</TableCell>
                    <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Registrate Date</TableCell>
                    <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>First Report Date</TableCell>
                    <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Final Report Date</TableCell>
                    <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Report Date</TableCell>
                    <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Prior Treatment</TableCell>
                    <TableCell sx={{ fontWeight: 'bold', bgcolor: 'warning.light' }}>WHO Diagnosis</TableCell>
                    <TableCell sx={{ bgcolor: 'warning.light' }}>Grading</TableCell>
                    <TableCell sx={{ bgcolor: 'success.light' }}>Surgical Margin</TableCell>
                    <TableCell sx={{ bgcolor: 'success.light' }}>Margin Distance (mm)</TableCell>
                    <TableCell sx={{ bgcolor: 'success.light' }}>biological_barrier_to_closest_margin</TableCell>
                    <TableCell sx={{ bgcolor: 'success.light' }}>Barrier Comment</TableCell>
                    <TableCell sx={{ bgcolor: 'info.light' }}>Ki-67</TableCell>
                    <TableCell sx={{ bgcolor: 'info.light' }}>Mitoses/10 HPF</TableCell>
                    <TableCell sx={{ bgcolor: 'info.light' }}>Necrosis</TableCell>
                    <TableCell sx={{ bgcolor: 'info.light' }}>EORTC Grade</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>IHC Status</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>IHC Result</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>FISH Status</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>FISH Result</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>RNA Status</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>RNA Result</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>DNA Status</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>DNA Result</TableCell>
                    <TableCell sx={{ bgcolor: 'secondary.light' }}>Report</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {pathologyEvents.map((e, idx) => (
                    <TableRow key={idx}>
                      <EditableCell {...ec("pathology", idx, "patient_id", String((e as any).patient_id ?? ""), pidCellSx)} />
                      <EditableCell {...ec("pathology", idx, "institution_id", String(e.institution_id ?? ""))} />
                      <EditableCell {...ec("pathology", idx, "responsible_pathologist_id", String(e.responsible_pathologist_id ?? ""))} />
                      <EditableCell {...ec("pathology", idx, "biopsy_type", String(e.biopsy_type ?? ""), { fontWeight: 'bold' })} />
                      <EditableCell {...ec("pathology", idx, "biopsied_lesion_type", String(e.biopsied_lesion_type ?? ""))} />
                      <EditableCell {...ec("pathology", idx, "biopsy_resection_date", String(e.biopsy_resection_date ?? ""))} />
                      <EditableCell {...ec("pathology", idx, "registrate_date", String(e.registrate_date ?? ""))} />
                      <EditableCell {...ec("pathology", idx, "first_report_date", String(e.first_report_date ?? ""))} />
                      <EditableCell {...ec("pathology", idx, "final_report_date", String(e.final_report_date ?? ""))} />
                      <EditableCell {...ec("pathology", idx, "report_date", String(e.report_date ?? ""))} />
                      <EditableCell {...ec("pathology", idx, "prior_treatment", String(e.prior_treatment ?? ""))} />
                      <EditableCell {...ec("pathology", idx, "who_diagnosis", String(e.who_diagnosis ?? ""), { fontWeight: 'bold' })} />
                      <EditableCell {...ec("pathology", idx, "diagnostic_grading", String(e.diagnostic_grading ?? ""))} />
                      <EditableCell {...ec("pathology", idx, "judgment_of_surgical_margin", String(e.judgment_of_surgical_margin ?? ""))} />
                      <EditableCell {...ec("pathology", idx, "closest_distance_to_margin_mm", String(e.closest_distance_to_margin_mm ?? ""))} />
                      <EditableCell {...ec("pathology", idx, "biological_barrier_to_closest_margin", String(e.biological_barrier_to_closest_margin ?? ""))} />
                      <EditableCell {...ec("pathology", idx, "biological_barrier_to_closest_margin_comment", String(e.biological_barrier_to_closest_margin_comment ?? ""))} />
                      <EditableCell {...ec("pathology", idx, "proliferation_index", String(e.proliferation_index ?? ""))} />
                      <EditableCell {...ec("pathology", idx, "mitoses_per_10hpf", String(e.mitoses_per_10hpf ?? ""))} />
                      <EditableCell {...ec("pathology", idx, "extent_of_necrosis", String(e.extent_of_necrosis ?? ""))} />
                      <EditableCell {...ec("pathology", idx, "eortc_response_grade", String(e.eortc_response_grade ?? ""))} />
                      <EditableCell {...ec("pathology", idx, "ihc_performed_status", String(e.ihc_performed_status ?? ""))} />
                      <EditableCell {...ec("pathology", idx, "ihc_result", String(e.ihc_result ?? ""), { maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} />
                      <EditableCell {...ec("pathology", idx, "fish_performed_status", String(e.fish_performed_status ?? ""))} />
                      <EditableCell {...ec("pathology", idx, "fish_result", String(e.fish_result ?? ""), { maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} />
                      <EditableCell {...ec("pathology", idx, "rna_performed_status", String(e.rna_performed_status ?? ""))} />
                      <EditableCell {...ec("pathology", idx, "rna_result", String(e.rna_result ?? ""), { maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} />
                      <EditableCell {...ec("pathology", idx, "dna_performed_status", String(e.dna_performed_status ?? ""))} />
                      <EditableCell {...ec("pathology", idx, "dna_result", String(e.dna_result ?? ""), { maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} />
                      <EditableCell {...ec("pathology", idx, "report", String(e.report ?? ""), { maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} />
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
            <ExportButtons headers={headers} rows={pathologyEvents} baseName="pathology_events" />
          </Paper>
        );
      })()}

      {/* --- SURGERY --- */}
      {surgeryEvents && surgeryEvents.length > 0 && (() => {
        const headers = ["patient_id", "surgery_date", "indication", "surgery_side", "anatomic_region", "greatest_surgical_tumor_dimension_in_mm", "had_tumor_spillage", "resection", "resected_tumor_margin", "reconstruction", "amputation", "participated_disciplines", "first_revision_details", "second_revision_details"];
        return (
          <Paper variant="outlined" sx={{ mt: 3, p: 2, borderRadius: 3 }}>
            <Typography variant="subtitle1" gutterBottom>Surgery</Typography>
            <Box sx={{ overflowX: "auto", maxWidth: "100%" }}>
              <Table size="small" sx={{ minWidth: 2200 }}>
                <TableHead>
                  <TableRow>
                    <TableCell sx={pidHeaderSx}>Patient ID</TableCell>
                    <TableCell sx={{ fontWeight: 'bold', bgcolor: 'primary.light', color: 'white' }}>Surgery Date</TableCell>
                    <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Indication</TableCell>
                    <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Side</TableCell>
                    <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Anatomic Region</TableCell>
                    <TableCell sx={{ bgcolor: 'warning.light' }}>Tumor Size (mm)</TableCell>
                    <TableCell sx={{ bgcolor: 'warning.light' }}>Tumor Spillage</TableCell>
                    <TableCell sx={{ bgcolor: 'success.light' }}>Resection Types</TableCell>
                    <TableCell sx={{ bgcolor: 'success.light' }}>Resected Margin</TableCell>
                    <TableCell sx={{ bgcolor: 'info.light' }}>Reconstruction</TableCell>
                    <TableCell sx={{ bgcolor: 'info.light' }}>Amputation</TableCell>
                    <TableCell sx={{ bgcolor: 'secondary.light' }}>Disciplines</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>1st Revision</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>2nd Revision</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {surgeryEvents.map((e, idx) => (
                    <TableRow key={idx}>
                      <EditableCell {...ec("surgery", idx, "patient_id", String((e as any).patient_id ?? ""), pidCellSx)} />
                      <EditableCell {...ec("surgery", idx, "surgery_date", String(e.surgery_date ?? ""), { fontWeight: 'bold' })} />
                      <EditableCell {...ec("surgery", idx, "indication", String(e.indication ?? ""))} />
                      <EditableCell {...ec("surgery", idx, "surgery_side", String(e.surgery_side ?? ""))} />
                      <EditableCell {...ec("surgery", idx, "anatomic_region", String(e.anatomic_region ?? ""))} />
                      <EditableCell {...ec("surgery", idx, "greatest_surgical_tumor_dimension_in_mm", String(e.greatest_surgical_tumor_dimension_in_mm ?? ""))} />
                      <EditableCell {...ec("surgery", idx, "had_tumor_spillage", e.had_tumor_spillage != null ? (e.had_tumor_spillage ? "Yes" : "No") : "")} />
                      <TableCell>{e.resection?.join(", ") ?? ""}</TableCell>
                      <EditableCell {...ec("surgery", idx, "resected_tumor_margin", String(e.resected_tumor_margin ?? ""))} />
                      <EditableCell {...ec("surgery", idx, "reconstruction", String(e.reconstruction ?? ""))} />
                      <EditableCell {...ec("surgery", idx, "amputation", String(e.amputation ?? ""))} />
                      <TableCell>{e.participated_disciplines?.join(", ") ?? ""}</TableCell>
                      <EditableCell {...ec("surgery", idx, "first_revision_details", String(e.first_revision_details ?? ""), { maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} />
                      <EditableCell {...ec("surgery", idx, "second_revision_details", String(e.second_revision_details ?? ""), { maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} />
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
            <ExportButtons headers={headers} rows={surgeryEvents} baseName="surgery_events" />
          </Paper>
        );
      })()}

      {/* --- SARCOMA BOARD --- */}
      {sarcomaBoardEvents && sarcomaBoardEvents.length > 0 && (() => {
        const headers = [
          "patient_id",
          "presentation_date",
          "reason_for_presentation",
          "status_before_follow_up",
          "unplanned_excision_date",
          "status_after_follow_up",
          "status_after_follow_up_comment",
          "treatment_before_follow_up",
          "follow_up_reason",
          "last_execution",
          "question",
          "proposed_procedure",
          "current_ecog",
          "decision_surgery",
          "decision_surgery_comment",
          "decision_radio_therapy",
          "decision_radio_therapy_comment",
          "decision_systemic_surgery",
          "decision_systemic_surgery_comment",
          "decision_follow_up",
          "decision_follow_up_comment",
          "decision_diagnostics",
          "decision_diagnostics_comment",
          "decision_palliative_care",
          "decision_palliative_care_comment",
          "summary",
          "further_details",
          "fast_track",
          "whoops_surgery_institution_id",
          "patient_history",
          "summary_patient_information",
          "summary_radiology",
          "summary_pathology",
          "presenting_physician_id",
        ];
        return (
          <Paper variant="outlined" sx={{ mt: 3, p: 2, borderRadius: 3 }}>
            <Typography variant="subtitle1" gutterBottom>Sarcoma Board</Typography>
            <Box sx={{ overflowX: "auto", maxWidth: "100%" }}>
              <Table size="small" sx={{ minWidth: 3000 }}>
                <TableHead>
                  <TableRow>
                    <TableCell sx={pidHeaderSx}>Patient ID</TableCell>
                    <TableCell sx={{ fontWeight: 'bold', bgcolor: 'primary.light', color: 'white' }}>Presentation Date</TableCell>
                    <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Reason</TableCell>
                    <TableCell sx={{ bgcolor: 'warning.light' }}>Status Before</TableCell>
                    <TableCell sx={{ bgcolor: 'warning.light' }}>Unplanned Excision Date</TableCell>
                    <TableCell sx={{ bgcolor: 'warning.light' }}>Status After</TableCell>
                    <TableCell sx={{ bgcolor: 'warning.light' }}>Status After Comment</TableCell>
                    <TableCell sx={{ bgcolor: 'warning.light' }}>Treatment Before</TableCell>
                    <TableCell sx={{ bgcolor: 'warning.light' }}>Follow-up Reason</TableCell>
                    <TableCell sx={{ bgcolor: 'warning.light' }}>Last Execution</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>Question</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>Proposed Procedure</TableCell>
                    <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>ECOG</TableCell>
                    <TableCell sx={{ bgcolor: 'success.light' }}>Surgery</TableCell>
                    <TableCell sx={{ bgcolor: 'success.light' }}>Surgery Comment</TableCell>
                    <TableCell sx={{ bgcolor: 'success.light' }}>Radio Therapy</TableCell>
                    <TableCell sx={{ bgcolor: 'success.light' }}>Radio Comment</TableCell>
                    <TableCell sx={{ bgcolor: 'success.light' }}>Systemic Therapy</TableCell>
                    <TableCell sx={{ bgcolor: 'success.light' }}>Systemic Comment</TableCell>
                    <TableCell sx={{ bgcolor: 'info.light' }}>Follow-up</TableCell>
                    <TableCell sx={{ bgcolor: 'info.light' }}>Follow-up Comment</TableCell>
                    <TableCell sx={{ bgcolor: 'info.light' }}>Diagnostics</TableCell>
                    <TableCell sx={{ bgcolor: 'info.light' }}>Diagnostics Comment</TableCell>
                    <TableCell sx={{ bgcolor: 'info.light' }}>Palliative Care</TableCell>
                    <TableCell sx={{ bgcolor: 'info.light' }}>Palliative Comment</TableCell>
                    <TableCell sx={{ bgcolor: 'secondary.light' }}>Summary</TableCell>
                    <TableCell sx={{ bgcolor: 'secondary.light' }}>Further Details</TableCell>
                    <TableCell sx={{ bgcolor: 'secondary.light' }}>Fast Track</TableCell>
                    <TableCell sx={{ bgcolor: 'secondary.light' }}>Whoops Institution ID</TableCell>
                    <TableCell sx={{ bgcolor: 'secondary.light' }}>Patient History</TableCell>
                    <TableCell sx={{ bgcolor: 'secondary.light' }}>Summary Patient Information</TableCell>
                    <TableCell sx={{ bgcolor: 'secondary.light' }}>Summary Radiology</TableCell>
                    <TableCell sx={{ bgcolor: 'secondary.light' }}>Summary Pathology</TableCell>
                    <TableCell sx={{ bgcolor: 'secondary.light' }}>Presenting Physician ID</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {sarcomaBoardEvents.map((e, idx) => (
                    <TableRow key={idx}>
                      <EditableCell {...ec("sarcomaBoard", idx, "patient_id", String((e as any).patient_id ?? ""), pidCellSx)} />
                      <EditableCell {...ec("sarcomaBoard", idx, "presentation_date", String(e.presentation_date ?? ""), { fontWeight: 'bold' })} />
                      <EditableCell {...ec("sarcomaBoard", idx, "reason_for_presentation", String(e.reason_for_presentation ?? ""))} />
                      <EditableCell {...ec("sarcomaBoard", idx, "status_before_follow_up", String(e.status_before_follow_up ?? ""))} />
                      <EditableCell {...ec("sarcomaBoard", idx, "unplanned_excision_date", String(e.unplanned_excision_date ?? ""))} />
                      <EditableCell {...ec("sarcomaBoard", idx, "status_after_follow_up", String(e.status_after_follow_up ?? ""))} />
                      <EditableCell {...ec("sarcomaBoard", idx, "status_after_follow_up_comment", String(e.status_after_follow_up_comment ?? ""), { maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} />
                      <EditableCell {...ec("sarcomaBoard", idx, "treatment_before_follow_up", String(e.treatment_before_follow_up ?? ""))} />
                      <EditableCell {...ec("sarcomaBoard", idx, "follow_up_reason", String(e.follow_up_reason ?? ""))} />
                      <EditableCell {...ec("sarcomaBoard", idx, "last_execution", String(e.last_execution ?? ""))} />
                      <EditableCell {...ec("sarcomaBoard", idx, "question", String(e.question ?? ""), { maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} />
                      <EditableCell {...ec("sarcomaBoard", idx, "proposed_procedure", String(e.proposed_procedure ?? ""), { maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} />
                      <EditableCell {...ec("sarcomaBoard", idx, "current_ecog", String(e.current_ecog ?? ""))} />
                      <EditableCell {...ec("sarcomaBoard", idx, "decision_surgery", String(e.decision_surgery ?? ""))} />
                      <EditableCell {...ec("sarcomaBoard", idx, "decision_surgery_comment", String(e.decision_surgery_comment ?? ""), { maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} />
                      <EditableCell {...ec("sarcomaBoard", idx, "decision_radio_therapy", String(e.decision_radio_therapy ?? ""))} />
                      <EditableCell {...ec("sarcomaBoard", idx, "decision_radio_therapy_comment", String(e.decision_radio_therapy_comment ?? ""), { maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} />
                      <EditableCell {...ec("sarcomaBoard", idx, "decision_systemic_surgery", String(e.decision_systemic_surgery ?? ""))} />
                      <EditableCell {...ec("sarcomaBoard", idx, "decision_systemic_surgery_comment", String(e.decision_systemic_surgery_comment ?? ""), { maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} />
                      <EditableCell {...ec("sarcomaBoard", idx, "decision_follow_up", String(e.decision_follow_up ?? ""))} />
                      <EditableCell {...ec("sarcomaBoard", idx, "decision_follow_up_comment", String(e.decision_follow_up_comment ?? ""), { maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} />
                      <EditableCell {...ec("sarcomaBoard", idx, "decision_diagnostics", String(e.decision_diagnostics ?? ""))} />
                      <EditableCell {...ec("sarcomaBoard", idx, "decision_diagnostics_comment", String(e.decision_diagnostics_comment ?? ""), { maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} />
                      <EditableCell {...ec("sarcomaBoard", idx, "decision_palliative_care", String(e.decision_palliative_care ?? ""))} />
                      <EditableCell {...ec("sarcomaBoard", idx, "decision_palliative_care_comment", String(e.decision_palliative_care_comment ?? ""), { maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} />
                      <EditableCell {...ec("sarcomaBoard", idx, "summary", String(e.summary ?? ""), { maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} />
                      <EditableCell {...ec("sarcomaBoard", idx, "further_details", String(e.further_details ?? ""), { maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} />
                      <EditableCell {...ec("sarcomaBoard", idx, "fast_track", e.fast_track == null ? "" : String(e.fast_track))} />
                      <EditableCell {...ec("sarcomaBoard", idx, "whoops_surgery_institution_id", String(e.whoops_surgery_institution_id ?? ""))} />
                      <EditableCell {...ec("sarcomaBoard", idx, "patient_history", String(e.patient_history ?? ""), { maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} />
                      <EditableCell {...ec("sarcomaBoard", idx, "summary_patient_information", String(e.summary_patient_information ?? ""), { maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} />
                      <EditableCell {...ec("sarcomaBoard", idx, "summary_radiology", String(e.summary_radiology ?? ""), { maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} />
                      <EditableCell {...ec("sarcomaBoard", idx, "summary_pathology", String(e.summary_pathology ?? ""), { maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} />
                      <EditableCell {...ec("sarcomaBoard", idx, "presenting_physician_id", String(e.presenting_physician_id ?? ""))} />
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
            <ExportButtons headers={headers} rows={sarcomaBoardEvents} baseName="sarcoma_board_events" />
          </Paper>
        );
      })()}

      {/* --- SYSTEMIC THERAPY --- */}
      {systemicTherapyEvents && systemicTherapyEvents.length > 0 && (() => {
        const headers = ["patient_id", "reason", "treatment_line", "bone_protocol", "softtissue_protocol", "cycle_start_date", "cycle_end_date", "cycles_executed", "was_rct_concomittant", "hyperthermia_status", "clinical_trial_inclusion", "discontinuation_reason", "patient_type", "comments", "drugs", "adverse_events"];
        return (
          <Paper variant="outlined" sx={{ mt: 3, p: 2, borderRadius: 3 }}>
            <Typography variant="subtitle1" gutterBottom>Systemic Therapy</Typography>
            <Box sx={{ overflowX: "auto", maxWidth: "100%" }}>
              <Table size="small" sx={{ minWidth: 2700 }}>
                <TableHead>
                  <TableRow>
                    <TableCell sx={pidHeaderSx}>Patient ID</TableCell>
                    <TableCell sx={{ fontWeight: 'bold', bgcolor: 'primary.light', color: 'white' }}>Reason</TableCell>
                    <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Treatment Line</TableCell>
                    <TableCell sx={{ bgcolor: 'warning.light' }}>Bone Protocol</TableCell>
                    <TableCell sx={{ bgcolor: 'warning.light' }}>Soft Tissue Protocol</TableCell>
                    <TableCell sx={{ bgcolor: 'success.light' }}>Cycle Start</TableCell>
                    <TableCell sx={{ bgcolor: 'success.light' }}>Cycle End</TableCell>
                    <TableCell sx={{ bgcolor: 'success.light' }}>Cycles Executed</TableCell>
                    <TableCell sx={{ bgcolor: 'info.light' }}>RCT Concomitant</TableCell>
                    <TableCell sx={{ bgcolor: 'info.light' }}>Hyperthermia</TableCell>
                    <TableCell sx={{ bgcolor: 'info.light' }}>Clinical Trial</TableCell>
                    <TableCell sx={{ bgcolor: 'secondary.light' }}>Discontinuation</TableCell>
                    <TableCell sx={{ bgcolor: 'secondary.light' }}>Patient Type</TableCell>
                    <TableCell sx={{ bgcolor: 'secondary.light' }}>Comments</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>Drugs</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>Adverse Events</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {systemicTherapyEvents.map((e, idx) => (
                    <TableRow key={idx}>
                      <EditableCell {...ec("systemicTherapy", idx, "patient_id", String((e as any).patient_id ?? ""), pidCellSx)} />
                      <EditableCell {...ec("systemicTherapy", idx, "reason", String(e.reason ?? ""), { fontWeight: 'bold' })} />
                      <EditableCell {...ec("systemicTherapy", idx, "treatment_line", String(e.treatment_line ?? ""))} />
                      <EditableCell {...ec("systemicTherapy", idx, "bone_protocol", String(e.bone_protocol ?? ""))} />
                      <EditableCell {...ec("systemicTherapy", idx, "softtissue_protocol", String(e.softtissue_protocol ?? ""))} />
                      <EditableCell {...ec("systemicTherapy", idx, "cycle_start_date", String(e.cycle_start_date ?? ""))} />
                      <EditableCell {...ec("systemicTherapy", idx, "cycle_end_date", String(e.cycle_end_date ?? ""))} />
                      <EditableCell {...ec("systemicTherapy", idx, "cycles_executed", String(e.cycles_executed ?? ""))} />
                      <EditableCell {...ec("systemicTherapy", idx, "was_rct_concomittant", e.was_rct_concomittant != null ? (e.was_rct_concomittant ? "Yes" : "No") : "")} />
                      <EditableCell {...ec("systemicTherapy", idx, "hyperthermia_status", String(e.hyperthermia_status ?? ""))} />
                      <EditableCell {...ec("systemicTherapy", idx, "clinical_trial_inclusion", String(e.clinical_trial_inclusion ?? ""))} />
                      <EditableCell {...ec("systemicTherapy", idx, "discontinuation_reason", String(e.discontinuation_reason ?? ""))} />
                      <EditableCell {...ec("systemicTherapy", idx, "patient_type", String(e.patient_type ?? ""))} />
                      <EditableCell {...ec("systemicTherapy", idx, "comments", String(e.comments ?? ""), { maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })} />
                      <TableCell sx={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.drugs?.map(d => `${d.drug_type} ${d.dose ?? ""}${d.dose_unit ?? ""}`).join("; ") ?? ""}</TableCell>
                      <TableCell sx={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.adverse_events?.map(ae => `${ae.event_type} (Grade ${ae.grade})`).join("; ") ?? ""}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
            <ExportButtons headers={headers} rows={systemicTherapyEvents} baseName="systemic_therapy_events" />
          </Paper>
        );
      })()}

      {!loading && !error && !radiologyEvents && !radiotherapyEvents && !pathologyEvents && !surgeryEvents && !sarcomaBoardEvents && !systemicTherapyEvents && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          {t('extractedData.noData')}
        </Typography>
      )}
    </Box>
  );
}
