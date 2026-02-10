const API = import.meta.env.VITE_API_URL; 

export type UploadWithTextResponse = {
  id: string;
  filename: string;
  doc_type?: string;
  text?: string;
  length?: number;
};

export type DocType =
  | "radiology"
  | "radiotherapy"
  | "pathology"
  | "surgery"
  | "sarcoma_board"
  | "systemic_therapy";

export async function uploadPdfWithText(
  file: File,
  docType: DocType
): Promise<UploadWithTextResponse> {
  const fd = new FormData();
  fd.append("file", file);
  fd.append("doc_type", docType);

  const res = await fetch(`${API}/upload-with-text`, {
    method: "POST",
    body: fd,
  });

  if (!res.ok) throw new Error(await res.text());
  return res.json();
}


// --- LLM Extract Types & API ---

export type ExtractedItem = {
  source_type?: string | null;
  body_part?: string | null;
  concept?: string | null;
  value?: number | null;
  unit?: string | null;
  note?: string | null;
};

export type LlmExtractResponse = {
  items: ExtractedItem[];
};

export async function llmExtractByDocId(docId: string): Promise<LlmExtractResponse> {
  const res = await fetch(`${API}/llm/extract`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ doc_id: docId }),
  });

  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export type RadiologyEvent = {
  // IDs
  institution_id?: number | null
  patient_id?: number | null

  // Pflichtfeld
  exam_date: string

  // Grundlegende Untersuchungs-Informationen
  exam_type?: string | null
  exam_type_comment?: string | null
  imaging_timing?: string | null
  imaging_type?: string | null

  // Läsions-Informationen
  location_of_lesion?: string | null
  largest_lesion_size_in_mm?: number | null
  medium_lesion_size_in_mm?: number | null
  smallest_lesion_size_in_mm?: number | null

  // Response-Kriterien
  recist_response?: string | null
  choi_response?: string | null
  irecist_response?: string | null
  pet_response?: string | null

  // Lokale Erkrankung
  local_disease_status?: string | null
  local_disease_measurable?: string | null
  local_disease_report_largest_diameter?: number | null
  local_disease_qualitative_mri_response?: string | null
  local_disease_radiologist_confidence?: number | null
  local_disease_pet_metabolic_response?: string | null

  // Metastasen - Allgemein
  metastasis_presence?: boolean | null
  metastasis?: string | null
  anatomic_location_of_metastasis?: string[]

  // Metastasen - Anzahl pro Lokalisation
  metastasis_location_lung_count?: string | null
  metastasis_location_pleura_count?: string | null
  metastasis_location_bone_count?: string | null
  metastasis_location_liver_count?: string | null
  metastasis_location_soft_tissue_count?: string | null
  metastasis_location_lymph_node_count?: string | null
  metastasis_location_brain_count?: string | null
  metastasis_location_other_count?: string | null

  // Metastasen - Messungen
  metastasis_target_lesion_count?: number | null
  metastasis_longest_diameter_mm?: number | null
  metastasis_indeterminate_category?: string | null

  // Befundtext und Datum
  radiology_report?: string | null
  report_date?: string | null
}


export type RadiologyExtractResponse = {
  events: RadiologyEvent[]
}

export async function llmExtractRadiologyByDocId(docId: string): Promise<RadiologyExtractResponse> {
  const res = await fetch(`${API}/llm/extract-radiology`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ doc_id: docId }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export type ClassifyDocTypeResponse = {
  doc_type: DocType
}

export async function classifyDocTypeByDocId(docId: string): Promise<ClassifyDocTypeResponse> {
  const res = await fetch(`${API}/llm/classify-doc-type`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ doc_id: docId }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

// ============================================================================
// RADIOTHERAPY EXTRACTION
// ============================================================================

export type RadiotherapyEvent = {
  institution_id?: number | null
  patient_id?: number | null
  responsible_oncologist_id?: number | null

  // Termine
  referral_date?: string | null
  first_contact_date?: string | null
  therapy_start_date?: string | null
  therapy_end_date?: string | null

  // Indikationen - ARRAY
  indications?: string[]

  // Therapietypen - ARRAY
  therapy_types?: string[]

  // Dosierung
  total_dose_in_gy?: number | null
  given_fractions?: number | null

  // Volumina
  ptv_volume_in_cm3?: number | null
  gtv_volume_in_cm3?: number | null

  // Tumor-Lokalisation
  was_tumor_located_in_radiated_area?: boolean | null
  was_tumor_located_with_pre_existing_lymph_edema?: boolean | null

  // Hyperthermie
  hyperthermia_status?: string | null

  // Kommentare
  comments?: string | null
}

export type RadiotherapyExtractResponse = {
  events: RadiotherapyEvent[]
}

export async function llmExtractRadiotherapyByDocId(docId: string): Promise<RadiotherapyExtractResponse> {
  const res = await fetch(`${API}/llm/extract-radiotherapy`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ doc_id: docId }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

// ============================================================================
// PATHOLOGY EXTRACTION
// ============================================================================

export type PathologyEvent = {
  institution_id?: number | null
  patient_id?: number | null
  responsible_pathologist_id?: number | null

  // Biopsie/Resektion
  biopsy_type?: string | null
  biopsied_lesion_type?: string | null
  biopsy_resection_date?: string | null

  // Befund-Daten
  registrate_date?: string | null
  first_report_date?: string | null
  final_report_date?: string | null
  report_date?: string | null

  // Vorbehandlung
  prior_treatment?: string | null

  // Diagnose
  who_diagnosis?: string | null

  // Grading
  diagnostic_grading?: string | null

  // Chirurgischer Rand
  judgment_of_surgical_margin?: string | null
  closest_distance_to_margin_mm?: number | null
  biological_barrier_to_closest_margin?: string | null
  biological_barrier_to_closest_margin_comment?: string | null

  // Tumor-Charakteristika
  proliferation_index?: string | null
  mitoses_per_10hpf?: string | null
  extent_of_necrosis?: string | null

  // Response
  eortc_response_grade?: string | null

  // Molekularpathologie - IHC
  ihc_performed_status?: string | null
  ihc_result?: string | null

  // FISH
  fish_performed_status?: string | null
  fish_result?: string | null

  // RNA
  rna_performed_status?: string | null
  rna_result?: string | null

  // DNA
  dna_performed_status?: string | null
  dna_result?: string | null

  // Vollständiger Befund
  report?: string | null
}

export type PathologyExtractResponse = {
  events: PathologyEvent[]
}

export async function llmExtractPathologyByDocId(docId: string): Promise<PathologyExtractResponse> {
  const res = await fetch(`${API}/llm/extract-pathology`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ doc_id: docId }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

// ============================================================================
// SURGERY EXTRACTION
// ============================================================================

export type SurgeryEvent = {
  institution_id?: number | null
  patient_id?: number | null
  responsible_surgeon_id?: number | null

  // PFLICHTFELD
  surgery_date: string

  // Operations-Details
  indication?: string | null
  indication_comment?: string | null

  surgery_side?: string | null
  anatomic_region?: string | null

  // Tumor
  greatest_surgical_tumor_dimension_in_mm?: number | null
  had_tumor_spillage?: boolean | null

  // Resektion - ARRAY
  resection?: string[]

  resected_tumor_margin?: string | null

  // Rekonstruktion
  reconstruction?: string | null

  // Amputation
  amputation?: string | null
  hemipelvectomy?: string[]

  // Revisionen
  first_revision_details?: string | null
  second_revision_details?: string | null

  // Beteiligte Disziplinen - ARRAY
  participated_disciplines?: string[]
  participated_disciplines_comment?: string | null
}

export type SurgeryExtractResponse = {
  events: SurgeryEvent[]
}

export async function llmExtractSurgeryByDocId(docId: string): Promise<SurgeryExtractResponse> {
  const res = await fetch(`${API}/llm/extract-surgery`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ doc_id: docId }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

// ============================================================================
// SARCOMA BOARD EXTRACTION
// ============================================================================

export type SarcomaBoardEvent = {
  institution_id?: number | null
  patient_id?: number | null

  // PFLICHTFELD
  presentation_date: string

  // Grund und Status
  reason_for_presentation?: string | null
  status_before_follow_up?: string | null
  status_after_follow_up?: string | null
  status_after_follow_up_comment?: string | null

  // Behandlungsverlauf
  treatment_before_follow_up?: string | null
  follow_up_reason?: string | null
  last_execution?: string | null
  unplanned_excision_date?: string | null

  // Fragestellung
  question?: string | null
  proposed_procedure?: string | null

  // ECOG
  current_ecog?: number | null

  // Board-Entscheidungen
  decision_surgery?: string | null
  decision_surgery_comment?: string | null

  decision_radio_therapy?: string | null
  decision_radio_therapy_comment?: string | null

  decision_systemic_therapy?: string | null
  decision_systemic_therapy_comment?: string | null

  decision_follow_up?: string | null
  decision_follow_up_comment?: string | null

  decision_diagnostics?: string | null
  decision_diagnostics_comment?: string | null

  decision_palliative_care?: string | null
  decision_palliative_care_comment?: string | null

  // Zusammenfassungen
  summary?: string | null
  patient_history?: string | null
  summary_patient_information?: string | null
  summary_radiology?: string | null
  summary_pathology?: string | null
  further_details?: string | null

  // Zusätzlich
  fast_track?: boolean
  whoops_surgery_institution_id?: number | null
  presenting_physician_id?: number | null
}

export type SarcomaBoardExtractResponse = {
  events: SarcomaBoardEvent[]
}

export async function llmExtractSarcomaBoardByDocId(docId: string): Promise<SarcomaBoardExtractResponse> {
  const res = await fetch(`${API}/llm/extract-sarcoma-board`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ doc_id: docId }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

// ============================================================================
// SYSTEMIC THERAPY EXTRACTION
// ============================================================================

export type Drug = {
  drug_type: string
  dose?: number | null
  dose_unit?: string | null
  frequency?: number | null
  frequency_unit?: string | null
  frequency_unit_comment?: string | null
  route?: string | null
  administration_day?: string | null
}

export type AdverseEvent = {
  medical_area: string
  event_type: string
  grade: string
  start_date?: string | null
  end_date?: string | null
  comment?: string | null
}

export type SystemicTherapyEvent = {
  institution_id?: number | null
  patient_id?: number | null
  responsible_oncologist_id?: number | null

  // Therapiegrund
  reason?: string | null
  reason_comment?: string | null
  treatment_line?: number | null

  // Protokolle
  bone_protocol?: string | null
  bone_protocol_comment?: string | null
  softtissue_protocol?: string | null
  softtissue_protocol_comment?: string | null

  // Zeitraum
  cycle_start_date?: string | null
  cycle_end_date?: string | null
  cycles_executed?: string | null

  // Begleittherapie
  was_rct_concomittant?: boolean
  hyperthermia_status?: string | null

  // Studienteilnahme
  clinical_trial_inclusion?: string | null

  // Abbruch
  discontinuation_reason?: string | null

  // Patient-Typ
  patient_type?: string | null

  // Assessment
  assessment_date?: string | null

  // Kommentare
  comments?: string | null

  // Nested Arrays
  drugs?: Drug[]
  adverse_events?: AdverseEvent[]
}

export type SystemicTherapyExtractResponse = {
  events: SystemicTherapyEvent[]
}

export async function llmExtractSystemicTherapyByDocId(docId: string): Promise<SystemicTherapyExtractResponse> {
  const res = await fetch(`${API}/llm/extract-systemic-therapy`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ doc_id: docId }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}
