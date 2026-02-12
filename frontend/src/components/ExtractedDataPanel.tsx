import { Paper, Typography, Stack, Button, Alert, CircularProgress, Box, Table, TableHead, TableRow, TableCell, TableBody } from '@mui/material';
import * as XLSX from 'xlsx';
import type {
  RadiologyEvent,
  RadiotherapyEvent,
  PathologyEvent,
  SurgeryEvent,
  SarcomaBoardEvent,
  SystemicTherapyEvent,
} from '../api';

function csvValue(val: any, key?: string): string {
  if (val === null || val === undefined) return "";
  if (key === "drugs" && Array.isArray(val))
    return val.map((d: any) => `${d.drug_type} ${d.dose ?? ""}${d.dose_unit ?? ""}`).join("; ");
  if (key === "adverse_events" && Array.isArray(val))
    return val.map((ae: any) => `${ae.event_type} Grade ${ae.grade}`).join("; ");
  if (Array.isArray(val)) return val.join(", ");
  if (typeof val === "boolean") return val ? "true" : "false";
  return String(val);
}

function downloadCsv(headers: string[], rows: any[], filename: string) {
  const csvRows = rows.map((r) =>
    headers.map((h) => `"${csvValue((r as any)[h], h).replace(/"/g, '""')}"`).join(",")
  );
  const csv = [headers.join(","), ...csvRows].join("\n");
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
}: {
  loading: boolean;
  error: string | null;
  radiologyEvents?: RadiologyEvent[] | null;
  radiotherapyEvents?: RadiotherapyEvent[] | null;
  pathologyEvents?: PathologyEvent[] | null;
  surgeryEvents?: SurgeryEvent[] | null;
  sarcomaBoardEvents?: SarcomaBoardEvent[] | null;
  systemicTherapyEvents?: SystemicTherapyEvent[] | null;
}) {

  return (
    <Box mt={4}>
      <Typography variant="h6" gutterBottom>
        Extrahierte strukturierte Daten
      </Typography>

      {loading && (
        <Stack direction="row" spacing={1} alignItems="center">
          <CircularProgress size={18} />
          <Typography variant="body2">Extrahiere Daten...</Typography>
        </Stack>
      )}

      {error && <Alert severity="error" sx={{ mt: 1 }}>{error}</Alert>}

      {/* --- RADIOLOGY --- */}
      {radiologyEvents && radiologyEvents.length > 0 && (() => {
        const headers = ["patient_id", "institution_id", "exam_date", "exam_type", "exam_type_comment", "imaging_timing", "imaging_type", "location_of_lesion", "largest_lesion_size_in_mm", "medium_lesion_size_in_mm", "smallest_lesion_size_in_mm", "recist_response", "choi_response", "irecist_response", "pet_response", "local_disease_status", "local_disease_measurable", "local_disease_report_largest_diameter", "local_disease_qualitative_mri_response", "local_disease_radiologist_confidence", "local_disease_pet_metabolic_response", "metastasis_presence", "metastasis", "anatomic_location_of_metastasis", "metastasis_location_lung_count", "metastasis_location_pleura_count", "metastasis_location_bone_count", "metastasis_location_liver_count", "metastasis_location_soft_tissue_count", "metastasis_location_lymph_node_count", "metastasis_location_brain_count", "metastasis_location_other_count", "metastasis_target_lesion_count", "metastasis_longest_diameter_mm", "metastasis_indeterminate_category", "radiology_report", "report_date"];
        return (
          <Paper variant="outlined" sx={{ mt: 3, p: 2, borderRadius: 3 }}>
            <Typography variant="subtitle1" gutterBottom>Radiology</Typography>
            <Box sx={{ overflowX: "auto", maxWidth: "100%" }}>
              <Table size="small" sx={{ minWidth: 3200 }}>
                <TableHead>
                  <TableRow>
                    <TableCell sx={pidHeaderSx}>Patient ID</TableCell>
                    <TableCell sx={{ fontWeight: 'bold', bgcolor: 'action.hover' }}>Institution ID</TableCell>
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
                      <TableCell sx={pidCellSx}>{(e as any).patient_id ?? ""}</TableCell>
                      <TableCell>{e.institution_id ?? ""}</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>{e.exam_date}</TableCell>
                      <TableCell>{e.exam_type ?? ""}</TableCell>
                      <TableCell>{e.exam_type_comment ?? ""}</TableCell>
                      <TableCell>{e.imaging_timing ?? ""}</TableCell>
                      <TableCell>{e.imaging_type ?? ""}</TableCell>
                      <TableCell>{e.location_of_lesion ?? ""}</TableCell>
                      <TableCell>{e.largest_lesion_size_in_mm ?? ""}</TableCell>
                      <TableCell>{e.medium_lesion_size_in_mm ?? ""}</TableCell>
                      <TableCell>{e.smallest_lesion_size_in_mm ?? ""}</TableCell>
                      <TableCell>{e.recist_response ?? ""}</TableCell>
                      <TableCell>{e.choi_response ?? ""}</TableCell>
                      <TableCell>{e.irecist_response ?? ""}</TableCell>
                      <TableCell>{e.pet_response ?? ""}</TableCell>
                      <TableCell>{e.local_disease_status ?? ""}</TableCell>
                      <TableCell>{e.local_disease_measurable ?? ""}</TableCell>
                      <TableCell>{e.local_disease_report_largest_diameter ?? ""}</TableCell>
                      <TableCell>{e.local_disease_qualitative_mri_response ?? ""}</TableCell>
                      <TableCell>{e.local_disease_radiologist_confidence ?? ""}</TableCell>
                      <TableCell>{e.local_disease_pet_metabolic_response ?? ""}</TableCell>
                      <TableCell>{e.metastasis_presence != null ? (e.metastasis_presence ? "Yes" : "No") : ""}</TableCell>
                      <TableCell>{e.metastasis ?? ""}</TableCell>
                      <TableCell>{e.anatomic_location_of_metastasis?.join(", ") ?? ""}</TableCell>
                      <TableCell>{e.metastasis_location_lung_count ?? ""}</TableCell>
                      <TableCell>{e.metastasis_location_pleura_count ?? ""}</TableCell>
                      <TableCell>{e.metastasis_location_bone_count ?? ""}</TableCell>
                      <TableCell>{e.metastasis_location_liver_count ?? ""}</TableCell>
                      <TableCell>{e.metastasis_location_soft_tissue_count ?? ""}</TableCell>
                      <TableCell>{e.metastasis_location_lymph_node_count ?? ""}</TableCell>
                      <TableCell>{e.metastasis_location_brain_count ?? ""}</TableCell>
                      <TableCell>{e.metastasis_location_other_count ?? ""}</TableCell>
                      <TableCell>{e.metastasis_target_lesion_count ?? ""}</TableCell>
                      <TableCell>{e.metastasis_longest_diameter_mm ?? ""}</TableCell>
                      <TableCell>{e.metastasis_indeterminate_category ?? ""}</TableCell>
                      <TableCell sx={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.radiology_report ?? ""}</TableCell>
                      <TableCell>{e.report_date ?? ""}</TableCell>
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
        const headers = ["patient_id", "referral_date", "first_contact_date", "therapy_start_date", "therapy_end_date", "indications", "therapy_types", "total_dose_in_gy", "given_fractions", "ptv_volume_in_cm3", "gtv_volume_in_cm3", "hyperthermia_status", "comments"];
        return (
          <Paper variant="outlined" sx={{ mt: 3, p: 2, borderRadius: 3 }}>
            <Typography variant="subtitle1" gutterBottom>Radiotherapy</Typography>
            <Box sx={{ overflowX: "auto", maxWidth: "100%" }}>
              <Table size="small" sx={{ minWidth: 2000 }}>
                <TableHead>
                  <TableRow>
                    <TableCell sx={pidHeaderSx}>Patient ID</TableCell>
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
                    <TableCell sx={{ bgcolor: 'secondary.light' }}>Hyperthermia</TableCell>
                    <TableCell sx={{ bgcolor: 'secondary.light' }}>Comments</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {radiotherapyEvents.map((e, idx) => (
                    <TableRow key={idx}>
                      <TableCell sx={pidCellSx}>{(e as any).patient_id ?? ""}</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>{e.referral_date ?? ""}</TableCell>
                      <TableCell>{e.first_contact_date ?? ""}</TableCell>
                      <TableCell>{e.therapy_start_date ?? ""}</TableCell>
                      <TableCell>{e.therapy_end_date ?? ""}</TableCell>
                      <TableCell>{e.indications?.join(", ") ?? ""}</TableCell>
                      <TableCell>{e.therapy_types?.join(", ") ?? ""}</TableCell>
                      <TableCell>{e.total_dose_in_gy ?? ""}</TableCell>
                      <TableCell>{e.given_fractions ?? ""}</TableCell>
                      <TableCell>{e.ptv_volume_in_cm3 ?? ""}</TableCell>
                      <TableCell>{e.gtv_volume_in_cm3 ?? ""}</TableCell>
                      <TableCell>{e.hyperthermia_status ?? ""}</TableCell>
                      <TableCell sx={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.comments ?? ""}</TableCell>
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
        const headers = ["patient_id", "biopsy_type", "biopsied_lesion_type", "biopsy_resection_date", "who_diagnosis", "diagnostic_grading", "judgment_of_surgical_margin", "closest_distance_to_margin_mm", "proliferation_index", "mitoses_per_10hpf", "extent_of_necrosis", "eortc_response_grade", "ihc_performed_status", "ihc_result", "fish_performed_status", "fish_result", "rna_performed_status", "rna_result", "dna_performed_status", "dna_result", "report"];
        return (
          <Paper variant="outlined" sx={{ mt: 3, p: 2, borderRadius: 3 }}>
            <Typography variant="subtitle1" gutterBottom>Pathology</Typography>
            <Box sx={{ overflowX: "auto", maxWidth: "100%" }}>
              <Table size="small" sx={{ minWidth: 2700 }}>
                <TableHead>
                  <TableRow>
                    <TableCell sx={pidHeaderSx}>Patient ID</TableCell>
                    <TableCell sx={{ fontWeight: 'bold', bgcolor: 'primary.light', color: 'white' }}>Biopsy Type</TableCell>
                    <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Lesion Type</TableCell>
                    <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Biopsy Date</TableCell>
                    <TableCell sx={{ fontWeight: 'bold', bgcolor: 'warning.light' }}>WHO Diagnosis</TableCell>
                    <TableCell sx={{ bgcolor: 'warning.light' }}>Grading</TableCell>
                    <TableCell sx={{ bgcolor: 'success.light' }}>Surgical Margin</TableCell>
                    <TableCell sx={{ bgcolor: 'success.light' }}>Margin Distance (mm)</TableCell>
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
                      <TableCell sx={pidCellSx}>{(e as any).patient_id ?? ""}</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>{e.biopsy_type ?? ""}</TableCell>
                      <TableCell>{e.biopsied_lesion_type ?? ""}</TableCell>
                      <TableCell>{e.biopsy_resection_date ?? ""}</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>{e.who_diagnosis ?? ""}</TableCell>
                      <TableCell>{e.diagnostic_grading ?? ""}</TableCell>
                      <TableCell>{e.judgment_of_surgical_margin ?? ""}</TableCell>
                      <TableCell>{e.closest_distance_to_margin_mm ?? ""}</TableCell>
                      <TableCell>{e.proliferation_index ?? ""}</TableCell>
                      <TableCell>{e.mitoses_per_10hpf ?? ""}</TableCell>
                      <TableCell>{e.extent_of_necrosis ?? ""}</TableCell>
                      <TableCell>{e.eortc_response_grade ?? ""}</TableCell>
                      <TableCell>{e.ihc_performed_status ?? ""}</TableCell>
                      <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.ihc_result ?? ""}</TableCell>
                      <TableCell>{e.fish_performed_status ?? ""}</TableCell>
                      <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.fish_result ?? ""}</TableCell>
                      <TableCell>{e.rna_performed_status ?? ""}</TableCell>
                      <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.rna_result ?? ""}</TableCell>
                      <TableCell>{e.dna_performed_status ?? ""}</TableCell>
                      <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.dna_result ?? ""}</TableCell>
                      <TableCell sx={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.report ?? ""}</TableCell>
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
                      <TableCell sx={pidCellSx}>{(e as any).patient_id ?? ""}</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>{e.surgery_date ?? ""}</TableCell>
                      <TableCell>{e.indication ?? ""}</TableCell>
                      <TableCell>{e.surgery_side ?? ""}</TableCell>
                      <TableCell>{e.anatomic_region ?? ""}</TableCell>
                      <TableCell>{e.greatest_surgical_tumor_dimension_in_mm ?? ""}</TableCell>
                      <TableCell>{e.had_tumor_spillage != null ? (e.had_tumor_spillage ? "Yes" : "No") : ""}</TableCell>
                      <TableCell>{e.resection?.join(", ") ?? ""}</TableCell>
                      <TableCell>{e.resected_tumor_margin ?? ""}</TableCell>
                      <TableCell>{e.reconstruction ?? ""}</TableCell>
                      <TableCell>{e.amputation ?? ""}</TableCell>
                      <TableCell>{e.participated_disciplines?.join(", ") ?? ""}</TableCell>
                      <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.first_revision_details ?? ""}</TableCell>
                      <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.second_revision_details ?? ""}</TableCell>
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
        const headers = ["patient_id", "presentation_date", "reason_for_presentation", "current_ecog", "status_before_follow_up", "status_after_follow_up", "treatment_before_follow_up", "decision_surgery", "decision_surgery_comment", "decision_radio_therapy", "decision_radio_therapy_comment", "decision_systemic_therapy", "decision_systemic_therapy_comment", "decision_follow_up", "decision_follow_up_comment", "decision_diagnostics", "decision_diagnostics_comment", "decision_palliative_care", "decision_palliative_care_comment", "question", "proposed_procedure", "summary", "summary_radiology", "summary_pathology"];
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
                    <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>ECOG</TableCell>
                    <TableCell sx={{ bgcolor: 'warning.light' }}>Status Before</TableCell>
                    <TableCell sx={{ bgcolor: 'warning.light' }}>Status After</TableCell>
                    <TableCell sx={{ bgcolor: 'warning.light' }}>Treatment Before</TableCell>
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
                    <TableCell sx={{ bgcolor: 'error.light' }}>Question</TableCell>
                    <TableCell sx={{ bgcolor: 'error.light' }}>Proposed Procedure</TableCell>
                    <TableCell sx={{ bgcolor: 'secondary.light' }}>Summary</TableCell>
                    <TableCell sx={{ bgcolor: 'secondary.light' }}>Summary Radiology</TableCell>
                    <TableCell sx={{ bgcolor: 'secondary.light' }}>Summary Pathology</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {sarcomaBoardEvents.map((e, idx) => (
                    <TableRow key={idx}>
                      <TableCell sx={pidCellSx}>{(e as any).patient_id ?? ""}</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>{e.presentation_date ?? ""}</TableCell>
                      <TableCell>{e.reason_for_presentation ?? ""}</TableCell>
                      <TableCell>{e.current_ecog ?? ""}</TableCell>
                      <TableCell>{e.status_before_follow_up ?? ""}</TableCell>
                      <TableCell>{e.status_after_follow_up ?? ""}</TableCell>
                      <TableCell>{e.treatment_before_follow_up ?? ""}</TableCell>
                      <TableCell>{e.decision_surgery ?? ""}</TableCell>
                      <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.decision_surgery_comment ?? ""}</TableCell>
                      <TableCell>{e.decision_radio_therapy ?? ""}</TableCell>
                      <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.decision_radio_therapy_comment ?? ""}</TableCell>
                      <TableCell>{e.decision_systemic_therapy ?? ""}</TableCell>
                      <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.decision_systemic_therapy_comment ?? ""}</TableCell>
                      <TableCell>{e.decision_follow_up ?? ""}</TableCell>
                      <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.decision_follow_up_comment ?? ""}</TableCell>
                      <TableCell>{e.decision_diagnostics ?? ""}</TableCell>
                      <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.decision_diagnostics_comment ?? ""}</TableCell>
                      <TableCell>{e.decision_palliative_care ?? ""}</TableCell>
                      <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.decision_palliative_care_comment ?? ""}</TableCell>
                      <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.question ?? ""}</TableCell>
                      <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.proposed_procedure ?? ""}</TableCell>
                      <TableCell sx={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.summary ?? ""}</TableCell>
                      <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.summary_radiology ?? ""}</TableCell>
                      <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.summary_pathology ?? ""}</TableCell>
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
                      <TableCell sx={pidCellSx}>{(e as any).patient_id ?? ""}</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>{e.reason ?? ""}</TableCell>
                      <TableCell>{e.treatment_line ?? ""}</TableCell>
                      <TableCell>{e.bone_protocol ?? ""}</TableCell>
                      <TableCell>{e.softtissue_protocol ?? ""}</TableCell>
                      <TableCell>{e.cycle_start_date ?? ""}</TableCell>
                      <TableCell>{e.cycle_end_date ?? ""}</TableCell>
                      <TableCell>{e.cycles_executed ?? ""}</TableCell>
                      <TableCell>{e.was_rct_concomittant != null ? (e.was_rct_concomittant ? "Yes" : "No") : ""}</TableCell>
                      <TableCell>{e.hyperthermia_status ?? ""}</TableCell>
                      <TableCell>{e.clinical_trial_inclusion ?? ""}</TableCell>
                      <TableCell>{e.discontinuation_reason ?? ""}</TableCell>
                      <TableCell>{e.patient_type ?? ""}</TableCell>
                      <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.comments ?? ""}</TableCell>
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
          Keine Daten gefunden.
        </Typography>
      )}
    </Box>
  );
}
