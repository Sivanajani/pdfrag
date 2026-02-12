import { Paper, Typography, Stack, Button, Alert, CircularProgress, Box, Table, TableHead, TableRow, TableCell, TableBody } from '@mui/material';
import type {
  RadiologyEvent,
  RadiotherapyEvent,
  PathologyEvent,
  SurgeryEvent,
  SarcomaBoardEvent,
  SystemicTherapyEvent,
} from '../api';

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
        Extrahierte strukturierte Daten (LLM)
      </Typography>

      {loading && (
        <Stack direction="row" spacing={1} alignItems="center">
          <CircularProgress size={18} />
          <Typography variant="body2">Extrahiere Daten…</Typography>
        </Stack>
      )}

      {error && <Alert severity="error" sx={{ mt: 1 }}>{error}</Alert>}

      {/* --- Radiology Tabelle (VOLLSTÄNDIG mit 45+ Feldern) --- */}
      {radiologyEvents && radiologyEvents.length > 0 && (
        <Paper variant="outlined" sx={{ mt: 3, p: 2, borderRadius: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Radiology – Vollständige strukturierte Tabelle (45+ Felder)
          </Typography>
          <Typography variant="caption" color="text.secondary" gutterBottom display="block">
            Horizontal scrollbar verwenden für alle Felder →
          </Typography>

          <Box sx={{ overflowX: "auto", maxWidth: "100%" }}>
            <Table size="small" sx={{ minWidth: 3000 }}>
              <TableHead>
                <TableRow>
                  {/* IDs */}
                  <TableCell sx={{ fontWeight: 'bold', bgcolor: 'action.hover' }}>Institution ID</TableCell>
                  <TableCell sx={{ fontWeight: 'bold', bgcolor: 'action.hover' }}>Patient ID</TableCell>

                  {/* Grundlegende Info */}
                  <TableCell sx={{ fontWeight: 'bold', bgcolor: 'primary.light', color: 'white' }}>Exam Date *</TableCell>
                  <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Exam Type</TableCell>
                  <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Exam Type Comment</TableCell>
                  <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Imaging Timing</TableCell>
                  <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Imaging Type</TableCell>

                  {/* Läsions-Info */}
                  <TableCell sx={{ bgcolor: 'warning.light' }}>Location of Lesion</TableCell>
                  <TableCell sx={{ bgcolor: 'warning.light' }}>Largest Lesion (mm)</TableCell>
                  <TableCell sx={{ bgcolor: 'warning.light' }}>Medium Lesion (mm)</TableCell>
                  <TableCell sx={{ bgcolor: 'warning.light' }}>Smallest Lesion (mm)</TableCell>

                  {/* Response Criteria */}
                  <TableCell sx={{ bgcolor: 'success.light' }}>RECIST Response</TableCell>
                  <TableCell sx={{ bgcolor: 'success.light' }}>Choi Response</TableCell>
                  <TableCell sx={{ bgcolor: 'success.light' }}>iRECIST Response</TableCell>
                  <TableCell sx={{ bgcolor: 'success.light' }}>PET Response</TableCell>

                  {/* Lokale Erkrankung */}
                  <TableCell sx={{ bgcolor: 'info.light' }}>Local Disease Status</TableCell>
                  <TableCell sx={{ bgcolor: 'info.light' }}>Local Disease Measurable</TableCell>
                  <TableCell sx={{ bgcolor: 'info.light' }}>Local Disease Diameter (mm)</TableCell>
                  <TableCell sx={{ bgcolor: 'info.light' }}>Local MRI Response</TableCell>
                  <TableCell sx={{ bgcolor: 'info.light' }}>Radiologist Confidence (1-5)</TableCell>
                  <TableCell sx={{ bgcolor: 'info.light' }}>Local PET Response</TableCell>

                  {/* Metastasen Allgemein */}
                  <TableCell sx={{ bgcolor: 'error.light' }}>Metastasis Presence</TableCell>
                  <TableCell sx={{ bgcolor: 'error.light' }}>Metastasis Status</TableCell>
                  <TableCell sx={{ bgcolor: 'error.light' }}>Anatomic Locations</TableCell>

                  {/* Metastasen Counts */}
                  <TableCell sx={{ bgcolor: 'error.light' }}>Lung Count</TableCell>
                  <TableCell sx={{ bgcolor: 'error.light' }}>Pleura Count</TableCell>
                  <TableCell sx={{ bgcolor: 'error.light' }}>Bone Count</TableCell>
                  <TableCell sx={{ bgcolor: 'error.light' }}>Liver Count</TableCell>
                  <TableCell sx={{ bgcolor: 'error.light' }}>Soft Tissue Count</TableCell>
                  <TableCell sx={{ bgcolor: 'error.light' }}>Lymph Node Count</TableCell>
                  <TableCell sx={{ bgcolor: 'error.light' }}>Brain Count</TableCell>
                  <TableCell sx={{ bgcolor: 'error.light' }}>Other Count</TableCell>

                  {/* Metastasen Messungen */}
                  <TableCell sx={{ bgcolor: 'error.light' }}>Target Lesion Count</TableCell>
                  <TableCell sx={{ bgcolor: 'error.light' }}>Longest Diameter (mm)</TableCell>
                  <TableCell sx={{ bgcolor: 'error.light' }}>Indeterminate Category</TableCell>

                  {/* Befundtext */}
                  <TableCell sx={{ bgcolor: 'secondary.light' }}>Radiology Report</TableCell>
                  <TableCell sx={{ bgcolor: 'secondary.light' }}>Report Date</TableCell>
                </TableRow>
              </TableHead>

              <TableBody>
                {radiologyEvents.map((e, idx) => (
                  <TableRow key={`${e.patient_id}-${e.exam_date}-${idx}`}>
                    {/* IDs */}
                    <TableCell>{e.institution_id ?? ""}</TableCell>
                    <TableCell>{e.patient_id ?? ""}</TableCell>

                    {/* Grundlegende Info */}
                    <TableCell sx={{ fontWeight: 'bold' }}>{e.exam_date}</TableCell>
                    <TableCell>{e.exam_type ?? ""}</TableCell>
                    <TableCell>{e.exam_type_comment ?? ""}</TableCell>
                    <TableCell>{e.imaging_timing ?? ""}</TableCell>
                    <TableCell>{e.imaging_type ?? ""}</TableCell>

                    {/* Läsions-Info */}
                    <TableCell>{e.location_of_lesion ?? ""}</TableCell>
                    <TableCell>{e.largest_lesion_size_in_mm ?? ""}</TableCell>
                    <TableCell>{e.medium_lesion_size_in_mm ?? ""}</TableCell>
                    <TableCell>{e.smallest_lesion_size_in_mm ?? ""}</TableCell>

                    {/* Response Criteria */}
                    <TableCell>{e.recist_response ?? ""}</TableCell>
                    <TableCell>{e.choi_response ?? ""}</TableCell>
                    <TableCell>{e.irecist_response ?? ""}</TableCell>
                    <TableCell>{e.pet_response ?? ""}</TableCell>

                    {/* Lokale Erkrankung */}
                    <TableCell>{e.local_disease_status ?? ""}</TableCell>
                    <TableCell>{e.local_disease_measurable ?? ""}</TableCell>
                    <TableCell>{e.local_disease_report_largest_diameter ?? ""}</TableCell>
                    <TableCell>{e.local_disease_qualitative_mri_response ?? ""}</TableCell>
                    <TableCell>{e.local_disease_radiologist_confidence ?? ""}</TableCell>
                    <TableCell>{e.local_disease_pet_metabolic_response ?? ""}</TableCell>

                    {/* Metastasen Allgemein */}
                    <TableCell>{e.metastasis_presence !== null && e.metastasis_presence !== undefined ? (e.metastasis_presence ? "Yes" : "No") : ""}</TableCell>
                    <TableCell>{e.metastasis ?? ""}</TableCell>
                    <TableCell>{e.anatomic_location_of_metastasis?.join(", ") ?? ""}</TableCell>

                    {/* Metastasen Counts */}
                    <TableCell>{e.metastasis_location_lung_count ?? ""}</TableCell>
                    <TableCell>{e.metastasis_location_pleura_count ?? ""}</TableCell>
                    <TableCell>{e.metastasis_location_bone_count ?? ""}</TableCell>
                    <TableCell>{e.metastasis_location_liver_count ?? ""}</TableCell>
                    <TableCell>{e.metastasis_location_soft_tissue_count ?? ""}</TableCell>
                    <TableCell>{e.metastasis_location_lymph_node_count ?? ""}</TableCell>
                    <TableCell>{e.metastasis_location_brain_count ?? ""}</TableCell>
                    <TableCell>{e.metastasis_location_other_count ?? ""}</TableCell>

                    {/* Metastasen Messungen */}
                    <TableCell>{e.metastasis_target_lesion_count ?? ""}</TableCell>
                    <TableCell>{e.metastasis_longest_diameter_mm ?? ""}</TableCell>
                    <TableCell>{e.metastasis_indeterminate_category ?? ""}</TableCell>

                    {/* Befundtext */}
                    <TableCell sx={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {e.radiology_report ?? ""}
                    </TableCell>
                    <TableCell>{e.report_date ?? ""}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Box>

          <Stack spacing={2} direction="row" justifyContent="flex-end" mt={2}>
            <Button
              variant="outlined"
              size="small"
              onClick={() => {
                const blob = new Blob(
                  [JSON.stringify(radiologyEvents, null, 2)],
                  { type: "application/json" }
                );
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "radiology_events.json";
                a.click();
                URL.revokeObjectURL(url);
              }}
            >
              JSON herunterladen
            </Button>

            <Button
              variant="contained"
              size="small"
              onClick={() => {
                // ALLE Felder in DB-Reihenfolge für CSV
                const headers = [
                  "institution_id",
                  "patient_id",
                  "exam_date",
                  "exam_type",
                  "exam_type_comment",
                  "imaging_timing",
                  "imaging_type",
                  "location_of_lesion",
                  "largest_lesion_size_in_mm",
                  "medium_lesion_size_in_mm",
                  "smallest_lesion_size_in_mm",
                  "recist_response",
                  "choi_response",
                  "irecist_response",
                  "pet_response",
                  "local_disease_status",
                  "local_disease_measurable",
                  "local_disease_report_largest_diameter",
                  "local_disease_qualitative_mri_response",
                  "local_disease_radiologist_confidence",
                  "local_disease_pet_metabolic_response",
                  "metastasis_presence",
                  "metastasis",
                  "anatomic_location_of_metastasis",
                  "metastasis_location_lung_count",
                  "metastasis_location_pleura_count",
                  "metastasis_location_bone_count",
                  "metastasis_location_liver_count",
                  "metastasis_location_soft_tissue_count",
                  "metastasis_location_lymph_node_count",
                  "metastasis_location_brain_count",
                  "metastasis_location_other_count",
                  "metastasis_target_lesion_count",
                  "metastasis_longest_diameter_mm",
                  "metastasis_indeterminate_category",
                  "radiology_report",
                  "report_date",
                ];

                const rows = radiologyEvents.map((r) =>
                  headers.map((h) => {
                    const val = (r as any)[h];
                    let str = "";
                    if (val === null || val === undefined) {
                      str = "";
                    } else if (Array.isArray(val)) {
                      str = val.join(", ");
                    } else if (typeof val === "boolean") {
                      str = val ? "true" : "false";
                    } else {
                      str = String(val);
                    }
                    return `"${str.replace(/"/g, '""')}"`;
                  }).join(",")
                );

                const csv = [headers.join(","), ...rows].join("\n");
                const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "radiology_events.csv";
                a.click();
                URL.revokeObjectURL(url);
              }}
            >
              CSV herunterladen (alle 37 Spalten)
            </Button>
          </Stack>
        </Paper>
      )}

      {/* --- RADIOTHERAPY Tabelle --- */}
      {radiotherapyEvents && radiotherapyEvents.length > 0 && (
        <Paper variant="outlined" sx={{ mt: 3, p: 2, borderRadius: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Radiotherapy – Vollständige strukturierte Tabelle
          </Typography>
          <Typography variant="caption" color="text.secondary" gutterBottom display="block">
            Horizontal scrollbar verwenden für alle Felder →
          </Typography>
          <Box sx={{ overflowX: "auto", maxWidth: "100%" }}>
            <Table size="small" sx={{ minWidth: 1800 }}>
              <TableHead>
                <TableRow>
                  {/* Termine */}
                  <TableCell sx={{ fontWeight: 'bold', bgcolor: 'primary.light', color: 'white' }}>Referral Date</TableCell>
                  <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>First Contact</TableCell>
                  <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Therapy Start</TableCell>
                  <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Therapy End</TableCell>
                  {/* Indikation & Typ */}
                  <TableCell sx={{ bgcolor: 'warning.light' }}>Indications</TableCell>
                  <TableCell sx={{ bgcolor: 'warning.light' }}>Therapy Types</TableCell>
                  {/* Dosierung */}
                  <TableCell sx={{ bgcolor: 'success.light' }}>Total Dose (Gy)</TableCell>
                  <TableCell sx={{ bgcolor: 'success.light' }}>Fractions</TableCell>
                  {/* Volumina */}
                  <TableCell sx={{ bgcolor: 'info.light' }}>PTV (cm³)</TableCell>
                  <TableCell sx={{ bgcolor: 'info.light' }}>GTV (cm³)</TableCell>
                  {/* Sonstiges */}
                  <TableCell sx={{ bgcolor: 'secondary.light' }}>Hyperthermia</TableCell>
                  <TableCell sx={{ bgcolor: 'secondary.light' }}>Comments</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {radiotherapyEvents.map((e, idx) => (
                  <TableRow key={idx}>
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
          <Stack spacing={2} direction="row" justifyContent="flex-end" mt={2}>
            <Button variant="outlined" size="small" onClick={() => {
              const blob = new Blob([JSON.stringify(radiotherapyEvents, null, 2)], { type: "application/json" });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "radiotherapy_events.json";
              a.click();
              URL.revokeObjectURL(url);
            }}>JSON herunterladen</Button>
            <Button variant="contained" size="small" onClick={() => {
              const headers = ["referral_date", "first_contact_date", "therapy_start_date", "therapy_end_date", "indications", "therapy_types", "total_dose_in_gy", "given_fractions", "ptv_volume_in_cm3", "gtv_volume_in_cm3", "hyperthermia_status", "comments"];
              const rows = radiotherapyEvents.map(r => headers.map(h => {
                const val = (r as any)[h];
                let str = val === null || val === undefined ? "" : Array.isArray(val) ? val.join("; ") : String(val);
                return `"${str.replace(/"/g, '""')}"`;
              }).join(","));
              const csv = [headers.join(","), ...rows].join("\n");
              const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "radiotherapy_events.csv";
              a.click();
              URL.revokeObjectURL(url);
            }}>CSV herunterladen</Button>
          </Stack>
        </Paper>
      )}

      {/* --- PATHOLOGY Tabelle --- */}
      {pathologyEvents && pathologyEvents.length > 0 && (
        <Paper variant="outlined" sx={{ mt: 3, p: 2, borderRadius: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Pathology – Vollständige strukturierte Tabelle
          </Typography>
          <Typography variant="caption" color="text.secondary" gutterBottom display="block">
            Horizontal scrollbar verwenden für alle Felder →
          </Typography>
          <Box sx={{ overflowX: "auto", maxWidth: "100%" }}>
            <Table size="small" sx={{ minWidth: 2500 }}>
              <TableHead>
                <TableRow>
                  {/* Biopsie/Resektion */}
                  <TableCell sx={{ fontWeight: 'bold', bgcolor: 'primary.light', color: 'white' }}>Biopsy Type</TableCell>
                  <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Lesion Type</TableCell>
                  <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Biopsy Date</TableCell>
                  {/* Diagnose */}
                  <TableCell sx={{ fontWeight: 'bold', bgcolor: 'warning.light' }}>WHO Diagnosis</TableCell>
                  <TableCell sx={{ bgcolor: 'warning.light' }}>Grading</TableCell>
                  {/* Chirurgischer Rand */}
                  <TableCell sx={{ bgcolor: 'success.light' }}>Surgical Margin</TableCell>
                  <TableCell sx={{ bgcolor: 'success.light' }}>Margin Distance (mm)</TableCell>
                  {/* Tumor-Charakteristika */}
                  <TableCell sx={{ bgcolor: 'info.light' }}>Ki-67</TableCell>
                  <TableCell sx={{ bgcolor: 'info.light' }}>Mitoses/10 HPF</TableCell>
                  <TableCell sx={{ bgcolor: 'info.light' }}>Necrosis</TableCell>
                  <TableCell sx={{ bgcolor: 'info.light' }}>EORTC Grade</TableCell>
                  {/* Molekularpathologie */}
                  <TableCell sx={{ bgcolor: 'error.light' }}>IHC Status</TableCell>
                  <TableCell sx={{ bgcolor: 'error.light' }}>IHC Result</TableCell>
                  <TableCell sx={{ bgcolor: 'error.light' }}>FISH Status</TableCell>
                  <TableCell sx={{ bgcolor: 'error.light' }}>FISH Result</TableCell>
                  <TableCell sx={{ bgcolor: 'error.light' }}>RNA Status</TableCell>
                  <TableCell sx={{ bgcolor: 'error.light' }}>RNA Result</TableCell>
                  <TableCell sx={{ bgcolor: 'error.light' }}>DNA Status</TableCell>
                  <TableCell sx={{ bgcolor: 'error.light' }}>DNA Result</TableCell>
                  {/* Befund */}
                  <TableCell sx={{ bgcolor: 'secondary.light' }}>Report</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {pathologyEvents.map((e, idx) => (
                  <TableRow key={idx}>
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
          <Stack spacing={2} direction="row" justifyContent="flex-end" mt={2}>
            <Button variant="outlined" size="small" onClick={() => {
              const blob = new Blob([JSON.stringify(pathologyEvents, null, 2)], { type: "application/json" });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "pathology_events.json";
              a.click();
              URL.revokeObjectURL(url);
            }}>JSON herunterladen</Button>
            <Button variant="contained" size="small" onClick={() => {
              const headers = ["biopsy_type", "biopsied_lesion_type", "biopsy_resection_date", "who_diagnosis", "diagnostic_grading", "judgment_of_surgical_margin", "closest_distance_to_margin_mm", "proliferation_index", "mitoses_per_10hpf", "extent_of_necrosis", "eortc_response_grade", "ihc_performed_status", "ihc_result", "fish_performed_status", "fish_result", "rna_performed_status", "rna_result", "dna_performed_status", "dna_result", "report"];
              const rows = pathologyEvents.map(r => headers.map(h => {
                const val = (r as any)[h];
                let str = val === null || val === undefined ? "" : String(val);
                return `"${str.replace(/"/g, '""')}"`;
              }).join(","));
              const csv = [headers.join(","), ...rows].join("\n");
              const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "pathology_events.csv";
              a.click();
              URL.revokeObjectURL(url);
            }}>CSV herunterladen</Button>
          </Stack>
        </Paper>
      )}

      {/* --- SURGERY Tabelle --- */}
      {surgeryEvents && surgeryEvents.length > 0 && (
        <Paper variant="outlined" sx={{ mt: 3, p: 2, borderRadius: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Surgery – Vollständige strukturierte Tabelle
          </Typography>
          <Typography variant="caption" color="text.secondary" gutterBottom display="block">
            Horizontal scrollbar verwenden für alle Felder →
          </Typography>
          <Box sx={{ overflowX: "auto", maxWidth: "100%" }}>
            <Table size="small" sx={{ minWidth: 2000 }}>
              <TableHead>
                <TableRow>
                  {/* Grundinfo */}
                  <TableCell sx={{ fontWeight: 'bold', bgcolor: 'primary.light', color: 'white' }}>Surgery Date</TableCell>
                  <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Indication</TableCell>
                  <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Side</TableCell>
                  <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Anatomic Region</TableCell>
                  {/* Tumor */}
                  <TableCell sx={{ bgcolor: 'warning.light' }}>Tumor Size (mm)</TableCell>
                  <TableCell sx={{ bgcolor: 'warning.light' }}>Tumor Spillage</TableCell>
                  {/* Resektion */}
                  <TableCell sx={{ bgcolor: 'success.light' }}>Resection Types</TableCell>
                  <TableCell sx={{ bgcolor: 'success.light' }}>Resected Margin</TableCell>
                  {/* Rekonstruktion */}
                  <TableCell sx={{ bgcolor: 'info.light' }}>Reconstruction</TableCell>
                  <TableCell sx={{ bgcolor: 'info.light' }}>Amputation</TableCell>
                  {/* Team */}
                  <TableCell sx={{ bgcolor: 'secondary.light' }}>Disciplines</TableCell>
                  {/* Revisionen */}
                  <TableCell sx={{ bgcolor: 'error.light' }}>1st Revision</TableCell>
                  <TableCell sx={{ bgcolor: 'error.light' }}>2nd Revision</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {surgeryEvents.map((e, idx) => (
                  <TableRow key={idx}>
                    <TableCell sx={{ fontWeight: 'bold' }}>{e.surgery_date ?? ""}</TableCell>
                    <TableCell>{e.indication ?? ""}</TableCell>
                    <TableCell>{e.surgery_side ?? ""}</TableCell>
                    <TableCell>{e.anatomic_region ?? ""}</TableCell>
                    <TableCell>{e.greatest_surgical_tumor_dimension_in_mm ?? ""}</TableCell>
                    <TableCell>{e.had_tumor_spillage !== null && e.had_tumor_spillage !== undefined ? (e.had_tumor_spillage ? "Yes" : "No") : ""}</TableCell>
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
          <Stack spacing={2} direction="row" justifyContent="flex-end" mt={2}>
            <Button variant="outlined" size="small" onClick={() => {
              const blob = new Blob([JSON.stringify(surgeryEvents, null, 2)], { type: "application/json" });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "surgery_events.json";
              a.click();
              URL.revokeObjectURL(url);
            }}>JSON herunterladen</Button>
            <Button variant="contained" size="small" onClick={() => {
              const headers = ["surgery_date", "indication", "surgery_side", "anatomic_region", "greatest_surgical_tumor_dimension_in_mm", "had_tumor_spillage", "resection", "resected_tumor_margin", "reconstruction", "amputation", "participated_disciplines", "first_revision_details", "second_revision_details"];
              const rows = surgeryEvents.map(r => headers.map(h => {
                const val = (r as any)[h];
                let str = val === null || val === undefined ? "" : Array.isArray(val) ? val.join("; ") : typeof val === "boolean" ? (val ? "true" : "false") : String(val);
                return `"${str.replace(/"/g, '""')}"`;
              }).join(","));
              const csv = [headers.join(","), ...rows].join("\n");
              const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "surgery_events.csv";
              a.click();
              URL.revokeObjectURL(url);
            }}>CSV herunterladen</Button>
          </Stack>
        </Paper>
      )}

      {/* --- SARCOMA BOARD Tabelle --- */}
      {sarcomaBoardEvents && sarcomaBoardEvents.length > 0 && (
        <Paper variant="outlined" sx={{ mt: 3, p: 2, borderRadius: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Sarcoma Board – Vollständige strukturierte Tabelle
          </Typography>
          <Typography variant="caption" color="text.secondary" gutterBottom display="block">
            Horizontal scrollbar verwenden für alle Felder →
          </Typography>
          <Box sx={{ overflowX: "auto", maxWidth: "100%" }}>
            <Table size="small" sx={{ minWidth: 2800 }}>
              <TableHead>
                <TableRow>
                  {/* Grundinfo */}
                  <TableCell sx={{ fontWeight: 'bold', bgcolor: 'primary.light', color: 'white' }}>Presentation Date</TableCell>
                  <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Reason</TableCell>
                  <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>ECOG</TableCell>
                  {/* Status */}
                  <TableCell sx={{ bgcolor: 'warning.light' }}>Status Before</TableCell>
                  <TableCell sx={{ bgcolor: 'warning.light' }}>Status After</TableCell>
                  <TableCell sx={{ bgcolor: 'warning.light' }}>Treatment Before</TableCell>
                  {/* Board-Entscheidungen */}
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
                  {/* Fragestellung & Zusammenfassung */}
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
          <Stack spacing={2} direction="row" justifyContent="flex-end" mt={2}>
            <Button variant="outlined" size="small" onClick={() => {
              const blob = new Blob([JSON.stringify(sarcomaBoardEvents, null, 2)], { type: "application/json" });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "sarcoma_board_events.json";
              a.click();
              URL.revokeObjectURL(url);
            }}>JSON herunterladen</Button>
            <Button variant="contained" size="small" onClick={() => {
              const headers = ["presentation_date", "reason_for_presentation", "current_ecog", "status_before_follow_up", "status_after_follow_up", "treatment_before_follow_up", "decision_surgery", "decision_surgery_comment", "decision_radio_therapy", "decision_radio_therapy_comment", "decision_systemic_therapy", "decision_systemic_therapy_comment", "decision_follow_up", "decision_follow_up_comment", "decision_diagnostics", "decision_diagnostics_comment", "decision_palliative_care", "decision_palliative_care_comment", "question", "proposed_procedure", "summary", "summary_radiology", "summary_pathology"];
              const rows = sarcomaBoardEvents.map(r => headers.map(h => {
                const val = (r as any)[h];
                let str = val === null || val === undefined ? "" : String(val);
                return `"${str.replace(/"/g, '""')}"`;
              }).join(","));
              const csv = [headers.join(","), ...rows].join("\n");
              const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "sarcoma_board_events.csv";
              a.click();
              URL.revokeObjectURL(url);
            }}>CSV herunterladen</Button>
          </Stack>
        </Paper>
      )}

      {/* --- SYSTEMIC THERAPY Tabelle --- */}
      {systemicTherapyEvents && systemicTherapyEvents.length > 0 && (
        <Paper variant="outlined" sx={{ mt: 3, p: 2, borderRadius: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Systemic Therapy – Vollständige strukturierte Tabelle
          </Typography>
          <Typography variant="caption" color="text.secondary" gutterBottom display="block">
            Horizontal scrollbar verwenden für alle Felder →
          </Typography>
          <Box sx={{ overflowX: "auto", maxWidth: "100%" }}>
            <Table size="small" sx={{ minWidth: 2500 }}>
              <TableHead>
                <TableRow>
                  {/* Therapiegrund */}
                  <TableCell sx={{ fontWeight: 'bold', bgcolor: 'primary.light', color: 'white' }}>Reason</TableCell>
                  <TableCell sx={{ bgcolor: 'primary.light', color: 'white' }}>Treatment Line</TableCell>
                  {/* Protokolle */}
                  <TableCell sx={{ bgcolor: 'warning.light' }}>Bone Protocol</TableCell>
                  <TableCell sx={{ bgcolor: 'warning.light' }}>Soft Tissue Protocol</TableCell>
                  {/* Zeitraum */}
                  <TableCell sx={{ bgcolor: 'success.light' }}>Cycle Start</TableCell>
                  <TableCell sx={{ bgcolor: 'success.light' }}>Cycle End</TableCell>
                  <TableCell sx={{ bgcolor: 'success.light' }}>Cycles Executed</TableCell>
                  {/* Begleittherapie */}
                  <TableCell sx={{ bgcolor: 'info.light' }}>RCT Concomitant</TableCell>
                  <TableCell sx={{ bgcolor: 'info.light' }}>Hyperthermia</TableCell>
                  <TableCell sx={{ bgcolor: 'info.light' }}>Clinical Trial</TableCell>
                  {/* Abschluss */}
                  <TableCell sx={{ bgcolor: 'secondary.light' }}>Discontinuation</TableCell>
                  <TableCell sx={{ bgcolor: 'secondary.light' }}>Patient Type</TableCell>
                  <TableCell sx={{ bgcolor: 'secondary.light' }}>Comments</TableCell>
                  {/* Medikamente & AEs */}
                  <TableCell sx={{ bgcolor: 'error.light' }}>Drugs</TableCell>
                  <TableCell sx={{ bgcolor: 'error.light' }}>Adverse Events</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {systemicTherapyEvents.map((e, idx) => (
                  <TableRow key={idx}>
                    <TableCell sx={{ fontWeight: 'bold' }}>{e.reason ?? ""}</TableCell>
                    <TableCell>{e.treatment_line ?? ""}</TableCell>
                    <TableCell>{e.bone_protocol ?? ""}</TableCell>
                    <TableCell>{e.softtissue_protocol ?? ""}</TableCell>
                    <TableCell>{e.cycle_start_date ?? ""}</TableCell>
                    <TableCell>{e.cycle_end_date ?? ""}</TableCell>
                    <TableCell>{e.cycles_executed ?? ""}</TableCell>
                    <TableCell>{e.was_rct_concomittant !== null && e.was_rct_concomittant !== undefined ? (e.was_rct_concomittant ? "Yes" : "No") : ""}</TableCell>
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
          <Stack spacing={2} direction="row" justifyContent="flex-end" mt={2}>
            <Button variant="outlined" size="small" onClick={() => {
              const blob = new Blob([JSON.stringify(systemicTherapyEvents, null, 2)], { type: "application/json" });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "systemic_therapy_events.json";
              a.click();
              URL.revokeObjectURL(url);
            }}>JSON herunterladen</Button>
            <Button variant="contained" size="small" onClick={() => {
              const headers = ["reason", "treatment_line", "bone_protocol", "softtissue_protocol", "cycle_start_date", "cycle_end_date", "cycles_executed", "was_rct_concomittant", "hyperthermia_status", "clinical_trial_inclusion", "discontinuation_reason", "patient_type", "comments", "drugs", "adverse_events"];
              const rows = systemicTherapyEvents.map(r => headers.map(h => {
                const val = (r as any)[h];
                let str = "";
                if (val === null || val === undefined) {
                  str = "";
                } else if (h === "drugs" && Array.isArray(val)) {
                  str = val.map((d: any) => `${d.drug_type} ${d.dose ?? ""}${d.dose_unit ?? ""}`).join("; ");
                } else if (h === "adverse_events" && Array.isArray(val)) {
                  str = val.map((ae: any) => `${ae.event_type} Grade ${ae.grade}`).join("; ");
                } else if (typeof val === "boolean") {
                  str = val ? "true" : "false";
                } else {
                  str = String(val);
                }
                return `"${str.replace(/"/g, '""')}"`;
              }).join(","));
              const csv = [headers.join(","), ...rows].join("\n");
              const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "systemic_therapy_events.csv";
              a.click();
              URL.revokeObjectURL(url);
            }}>CSV herunterladen</Button>
          </Stack>
        </Paper>
      )}


      {!loading && !error && !radiologyEvents && !radiotherapyEvents && !pathologyEvents && !surgeryEvents && !sarcomaBoardEvents && !systemicTherapyEvents && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Keine Daten gefunden.
        </Typography>
      )}
    </Box>
  );
}
