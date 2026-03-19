from __future__ import annotations

from datetime import date, datetime
from functools import lru_cache
from pathlib import Path
from typing import ClassVar, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator
import yaml

# ---------------------------------------------------------------------------
# Lookup tables — module-level so they're readable and easy to extend
# ---------------------------------------------------------------------------

# DB constraints: drug/drug_type.yml
_DRUG_TYPE: Dict[str, str] = {
    # ── Cytotoxics ───────────────────────────────────────────────────────────
    "actinomycin_d": "actinomycin_d",
    "carboplatin": "carboplatin",
    "cisplatin": "cisplatin",
    "cyclophosphamid": "cyclophosphamid",
    "docetaxel": "docetaxel",
    "doxorubicin": "doxorubicin",
    "liposomal_doxorubicin": "liposomal_doxorubicin",
    "dtic_dacarbazine": "dtic_dacarbazine",
    "eribulin": "eribulin",
    "etoposid": "etoposid",
    "gemcitabine": "gemcitabine",
    "ifosfamie": "ifosfamie",
    "irinotecan": "irinotecan",
    "methotrexate": "methotrexate",
    "navelbine": "navelbine",
    "paclitaxel": "paclitaxel",
    "temozolomid": "temozolomid",
    "trabectedin": "trabectedin",
    "trofosfamid": "trofosfamid",
    "vincristin": "vincristin",
    # ── Immunotherapy ────────────────────────────────────────────────────────
    "atezolizumab_pd_l1": "atezolizumab_pd_l1",
    "avelumab_pd_l1": "avelumab_pd_l1",
    "cemiplimab_pd_l1": "cemiplimab_pd_l1",
    "durvalumab_pd_l1": "durvalumab_pd_l1",
    "nivolumab_pd_1": "nivolumab_pd_1",
    "pembrolizumab_pd_1": "pembrolizumab_pd_1",
    # ── Kinase inhibitors ────────────────────────────────────────────────────
    "alectinib_alk": "alectinib_alk",
    "avapritinib_ayvakit": "avapritinib_ayvakit",
    "axitinib_vegfr": "axitinib_vegfr",
    "binimetinib_mek": "binimetinib_mek",
    "cabozantinib_ros1_met": "cabozantinib_ros1_met",
    "cediranib_vegfr": "cediranib_vegfr",
    "ceritinib_alk_ros1": "ceritinib_alk_ros1",
    "crizotinib_met_ros1": "crizotinib_met_ros1",
    "cobimetinib_mek": "cobimetinib_mek",
    "dasatinib_src_bcr_abl": "dasatinib_src_bcr_abl",
    "encorafenib_braf": "encorafenib_braf",
    "erdafitinib_fgfr": "erdafitinib_fgfr",
    "erlotinib_egfr": "erlotinib_egfr",
    "imatinib_ckit_pdgfr_a_bcr_abl": "imatinib_ckit_pdgfr_a_bcr_abl",
    "infigratinib_fgfr": "infigratinib_fgfr",
    "larotrectinib_ntrk": "larotrectinib_ntrk",
    "lenvatinib_fgfr_pdgfr_a_kit_ret": "lenvatinib_fgfr_pdgfr_a_kit_ret",
    "pazopanib_vegfr_pdgfr_kit": "pazopanib_vegfr_pdgfr_kit",
    "regorafenib": "regorafenib",
    "sorafenib_raf_c_kit_flt_vegfr_pdgfr": "sorafenib_raf_c_kit_flt_vegfr_pdgfr",
    "sunitinib_pdgfr_vegfr_kit_flt3_csf_1r_ret": "sunitinib_pdgfr_vegfr_kit_flt3_csf_1r_ret",
    "tivantinib_mek": "tivantinib_mek",
    "vemurafenib_braf": "vemurafenib_braf",
    # ── mTOR / PARP / VEGF / other targeted ─────────────────────────────────
    "everolimus": "everolimus",
    "nab_sirolimus": "nab_sirolimus",
    "olapatib": "olapatib",
    "bevacizumab": "bevacizumab",
    "ramucirumab": "ramucirumab",
    "denosumab": "denosumab",
    "tazemetostat": "tazemetostat",
    "alpelisib": "alpelisib",
    "nutlins": "nutlins",
    "palbociblib": "palbociblib",
    "ribociclib": "ribociclib",
    "abemaciclib": "abemaciclib",
    # ── Synonyms / trade names / DE spellings ────────────────────────────────
    "adriamycin": "doxorubicin",
    "adriamycin_(doxorubicin)": "doxorubicin",
    "doxorubicin_(adriamycin)": "doxorubicin",
    "liposomales_doxorubicin": "liposomal_doxorubicin",
    "pegyliertes_liposomales_doxorubicin": "liposomal_doxorubicin",
    "caelyx": "liposomal_doxorubicin",
    "cyclophosphamide": "cyclophosphamid",
    "cyclophosphamide_(ctx)": "cyclophosphamid",
    "ctx": "cyclophosphamid",
    "ifosfamide": "ifosfamie",
    "ifex": "ifosfamie",
    "etoposide": "etoposid",
    "vp_16": "etoposid",
    "vp16": "etoposid",
    "vincristine": "vincristin",
    "oncovin": "vincristin",
    "dacarbazine": "dtic_dacarbazine",
    "dtic": "dtic_dacarbazine",
    "dacarbazin": "dtic_dacarbazine",
    "temozolomide": "temozolomid",
    "trofosfamide": "trofosfamid",
    "methotrexat": "methotrexate",
    "mtx": "methotrexate",
    "vinorelbine": "navelbine",
    "vinorelbin": "navelbine",
    "taxol": "paclitaxel",
    "taxotere": "docetaxel",
    "halaven": "eribulin",
    "yondelis": "trabectedin",
    "actinomycin": "actinomycin_d",
    "dactinomycin": "actinomycin_d",
    "act_d": "actinomycin_d",
    "imatinib": "imatinib_ckit_pdgfr_a_bcr_abl",
    "gleevec": "imatinib_ckit_pdgfr_a_bcr_abl",
    "glivec": "imatinib_ckit_pdgfr_a_bcr_abl",
    "pazopanib": "pazopanib_vegfr_pdgfr_kit",
    "votrient": "pazopanib_vegfr_pdgfr_kit",
    "sorafenib": "sorafenib_raf_c_kit_flt_vegfr_pdgfr",
    "nexavar": "sorafenib_raf_c_kit_flt_vegfr_pdgfr",
    "sunitinib": "sunitinib_pdgfr_vegfr_kit_flt3_csf_1r_ret",
    "sutent": "sunitinib_pdgfr_vegfr_kit_flt3_csf_1r_ret",
    "regorafenib_stivarga": "regorafenib",
    "stivarga": "regorafenib",
    "avapritinib": "avapritinib_ayvakit",
    "ayvakit": "avapritinib_ayvakit",
    "larotrectinib": "larotrectinib_ntrk",
    "vitrakvi": "larotrectinib_ntrk",
    "lenvatinib": "lenvatinib_fgfr_pdgfr_a_kit_ret",
    "lenvima": "lenvatinib_fgfr_pdgfr_a_kit_ret",
    "erdafitinib": "erdafitinib_fgfr",
    "balversa": "erdafitinib_fgfr",
    "pembrolizumab": "pembrolizumab_pd_1",
    "keytruda": "pembrolizumab_pd_1",
    "nivolumab": "nivolumab_pd_1",
    "opdivo": "nivolumab_pd_1",
    "atezolizumab": "atezolizumab_pd_l1",
    "tecentriq": "atezolizumab_pd_l1",
    "avelumab": "avelumab_pd_l1",
    "bavencio": "avelumab_pd_l1",
    "durvalumab": "durvalumab_pd_l1",
    "imfinzi": "durvalumab_pd_l1",
    "cemiplimab": "cemiplimab_pd_l1",
    "libtayo": "cemiplimab_pd_l1",
    "palbociclib": "palbociblib",
    "ibrance": "palbociblib",
    "kisqali": "ribociclib",
    "verzenio": "abemaciclib",
    "olaparib": "olapatib",
    "lynparza": "olapatib",
    "xgeva": "denosumab",
    "prolia": "denosumab",
    "afinitor": "everolimus",
    "tazverik": "tazemetostat",
    "piqray": "alpelisib",
}

# DB constraints: drug/dose_unit.yml
_DOSE_UNIT: Dict[str, str] = {
    "mg_m2_per_day": "mg_m2_per_day",
    "mg_kg_per_day": "mg_kg_per_day",
    "auc_per_day": "auc_per_day",
    "absolute_dose_mg_per_day": "absolute_dose_mg_per_day",
    "cumulative_dose_mg_per_day": "cumulative_dose_mg_per_day",
    "units_per_day": "units_per_day",
    "mg/m2": "mg_m2_per_day",
    "mg_m2": "mg_m2_per_day",
    "mg/m²": "mg_m2_per_day",
    "mg_m²": "mg_m2_per_day",
    "mg/kg": "mg_kg_per_day",
    "mg_kg": "mg_kg_per_day",
    "auc": "auc_per_day",
    "mg": "absolute_dose_mg_per_day",
    "mg_absolute": "absolute_dose_mg_per_day",
    "absolute_mg": "absolute_dose_mg_per_day",
    "cumulative_mg": "cumulative_dose_mg_per_day",
    "mg_kumulativ": "cumulative_dose_mg_per_day",
    "units": "units_per_day",
    "einheiten": "units_per_day",
}

# DB constraints: drug/frequency_unit.yml
_FREQUENCY_UNIT: Dict[str, str] = {
    "x_times_per_week": "x_times_per_week",
    "x_times_per_month": "x_times_per_month",
    "daily": "daily",
    "every_other_day": "every_other_day",
    "other": "other",
    "once_daily": "daily",
    "once_a_day": "daily",
    "once_per_day": "daily",
    "qd": "daily",
    "od": "daily",
    "per_day": "daily",
    "täglich": "daily",
    "wöchentlich": "x_times_per_week",
    "weekly": "x_times_per_week",
    "once_weekly": "x_times_per_week",
    "once_a_week": "x_times_per_week",
    "monthly": "x_times_per_month",
    "once_monthly": "x_times_per_month",
    "once_a_month": "x_times_per_month",
    "every_2_days": "every_other_day",
    "every_second_day": "every_other_day",
    "jeden_zweiten_tag": "every_other_day",
    "q2d": "every_other_day",
    "sonstige": "other",
    "andere": "other",
}

# DB constraints: drug/administration_day.yml (monday–sunday)
_ADMINISTRATION_DAY: Dict[str, str] = {
    "monday": "monday", "tuesday": "tuesday", "wednesday": "wednesday",
    "thursday": "thursday", "friday": "friday", "saturday": "saturday",
    "sunday": "sunday",
    # DE
    "montag": "monday", "dienstag": "tuesday", "mittwoch": "wednesday",
    "donnerstag": "thursday", "freitag": "friday", "samstag": "saturday",
    "sonntag": "sunday",
    # Abbreviations EN
    "mon": "monday", "tue": "tuesday", "wed": "wednesday",
    "thu": "thursday", "fri": "friday", "sat": "saturday", "sun": "sunday",
    # Abbreviations DE
    "mo": "monday", "di": "tuesday", "mi": "wednesday",
    "do": "thursday", "fr": "friday", "sa": "saturday", "so": "sunday",
}

# DB constraints: drug/route.yml
_ROUTE: Dict[str, str] = {
    "intravenous_iv": "intravenous_iv",
    "subcutaneous_sc": "subcutaneous_sc",
    "per_os_pos": "per_os_pos",
    "intramuscular_im": "intramuscular_im",
    "intraosseous_io": "intraosseous_io",
    "intravenous": "intravenous_iv", "iv": "intravenous_iv",
    "intravenous_(iv)": "intravenous_iv",
    "subcutaneous": "subcutaneous_sc", "sc": "subcutaneous_sc",
    "subcutaneous_(sc)": "subcutaneous_sc",
    "oral": "per_os_pos", "po": "per_os_pos",
    "per_os": "per_os_pos", "per_os_(po)": "per_os_pos",
    "intramuscular": "intramuscular_im", "im": "intramuscular_im",
    "intramuscular_(im)": "intramuscular_im",
    "intraosseous": "intraosseous_io", "io": "intraosseous_io",
    "intraosseous_(io)": "intraosseous_io",
    # DE
    "intravenös": "intravenous_iv", "intravenoes": "intravenous_iv",
    "subkutan": "subcutaneous_sc",
    "oral_per_os": "per_os_pos",
    "intramuskulär": "intramuscular_im", "intramuskulaer": "intramuscular_im",
    "intraossär": "intraosseous_io", "intraossaer": "intraosseous_io",
}

# DB constraints: CTCAE category keys (ctcae.yml top-level)
_MEDICAL_AREA: Dict[str, str] = {
    "blood_and_lymphatic_system_disorders": "blood_and_lymphatic_system_disorders",
    "cardiac_disorders": "cardiac_disorders",
    "congenital_familial_and_genetic_disorders": "congenital_familial_and_genetic_disorders",
    "ear_and_labyrinth_disorders": "ear_and_labyrinth_disorders",
    "endocrine_disorders": "endocrine_disorders",
    "eye_disorders": "eye_disorders",
    "gastrointestinal_disorders": "gastrointestinal_disorders",
    "general_disorders_and_administration_site_conditions": "general_disorders_and_administration_site_conditions",
    "hepatobiliary_disorders": "hepatobiliary_disorders",
    "immune_system_disorders": "immune_system_disorders",
    "infections_and_infestations": "infections_and_infestations",
    "injury_poisoning_and_procedural_complications": "injury_poisoning_and_procedural_complications",
    "investigations": "investigations",
    "metabolism_and_nutrition_disorders": "metabolism_and_nutrition_disorders",
    "musculoskeletal_and_connective_tissue_disorders": "musculoskeletal_and_connective_tissue_disorders",
    "neoplasms_benign_malignant_and_unspecified_incl_cysts_and_polyps": "neoplasms_benign_malignant_and_unspecified_incl_cysts_and_polyps",
    "nervous_system_disorders": "nervous_system_disorders",
    "pregnancy_puerperium_and_perinatal_conditions": "pregnancy_puerperium_and_perinatal_conditions",
    "psychiatric_disorders": "psychiatric_disorders",
    "renal_and_urinary_disorders": "renal_and_urinary_disorders",
    "reproductive_system_and_breast_disorders": "reproductive_system_and_breast_disorders",
    "respiratory_thoracic_and_mediastinal_disorders": "respiratory_thoracic_and_mediastinal_disorders",
    "skin_and_subcutaneous_tissue_disorders": "skin_and_subcutaneous_tissue_disorders",
    "social_circumstances": "social_circumstances",
    "surgical_and_medical_procedures": "surgical_and_medical_procedures",
    "vascular_disorders": "vascular_disorders",
    # EN synonyms
    "hematology": "blood_and_lymphatic_system_disorders",
    "blood": "blood_and_lymphatic_system_disorders",
    "cardiology": "cardiac_disorders",
    "cardiac": "cardiac_disorders",
    "heart": "cardiac_disorders",
    "ear": "ear_and_labyrinth_disorders",
    "endocrine": "endocrine_disorders",
    "endocrinology": "endocrine_disorders",
    "ophthalmology": "eye_disorders",
    "eye": "eye_disorders",
    "gastrointestinal": "gastrointestinal_disorders",
    "gastroenterology": "gastrointestinal_disorders",
    "gi": "gastrointestinal_disorders",
    "general": "general_disorders_and_administration_site_conditions",
    "hepatology": "hepatobiliary_disorders",
    "liver": "hepatobiliary_disorders",
    "immunology": "immune_system_disorders",
    "immune": "immune_system_disorders",
    "infection": "infections_and_infestations",
    "infectious": "infections_and_infestations",
    "injury": "injury_poisoning_and_procedural_complications",
    "laboratory": "investigations",
    "lab": "investigations",
    "metabolism": "metabolism_and_nutrition_disorders",
    "metabolic": "metabolism_and_nutrition_disorders",
    "nutrition": "metabolism_and_nutrition_disorders",
    "musculoskeletal": "musculoskeletal_and_connective_tissue_disorders",
    "neurology": "nervous_system_disorders",
    "neurological": "nervous_system_disorders",
    "nervous system": "nervous_system_disorders",
    "psychiatry": "psychiatric_disorders",
    "psychiatric": "psychiatric_disorders",
    "nephrology": "renal_and_urinary_disorders",
    "renal": "renal_and_urinary_disorders",
    "urinary": "renal_and_urinary_disorders",
    "reproductive": "reproductive_system_and_breast_disorders",
    "pulmonology": "respiratory_thoracic_and_mediastinal_disorders",
    "respiratory": "respiratory_thoracic_and_mediastinal_disorders",
    "dermatology": "skin_and_subcutaneous_tissue_disorders",
    "skin": "skin_and_subcutaneous_tissue_disorders",
    "vascular": "vascular_disorders",
    # DE synonyms
    "hämatologie": "blood_and_lymphatic_system_disorders",
    "hämatologisch": "blood_and_lymphatic_system_disorders",
    "kardiologie": "cardiac_disorders",
    "kardiologisch": "cardiac_disorders",
    "endokrinologie": "endocrine_disorders",
    "augenheilkunde": "eye_disorders",
    "gastroenterologie": "gastrointestinal_disorders",
    "hepatologie": "hepatobiliary_disorders",
    "immunologie": "immune_system_disorders",
    "infektiologie": "infections_and_infestations",
    "infektion": "infections_and_infestations",
    "labor": "investigations",
    "laborwerte": "investigations",
    "metabolismus": "metabolism_and_nutrition_disorders",
    "neurologie": "nervous_system_disorders",
    "nephrologie": "renal_and_urinary_disorders",
    "niere": "renal_and_urinary_disorders",
    "pneumologie": "respiratory_thoracic_and_mediastinal_disorders",
    "lunge": "respiratory_thoracic_and_mediastinal_disorders",
    "dermatologie": "skin_and_subcutaneous_tissue_disorders",
    "haut": "skin_and_subcutaneous_tissue_disorders",
    "gefäße": "vascular_disorders",
    "gefässerkrankungen": "vascular_disorders",
}

# Supplemental synonyms / aliases for CTCAE leaf codes.
# The complete code list is loaded from db/constraints/adverse_event/ctcae.yml.
_EVENT_TYPE_EXTRA: Dict[str, str] = {
    # Hematology
    "anemia": "anemia", "anaemia": "anemia", "anämie": "anemia",
    "febrile_neutropenia": "febrile_neutropenia",
    "febrile neutropenia": "febrile_neutropenia",
    "febrile neutropenie": "febrile_neutropenia",
    "neutropenia": "neutrophil_count_decreased",
    "neutropenie": "neutrophil_count_decreased",
    "neutrophil_count_decreased": "neutrophil_count_decreased",
    "leukopenia": "white_blood_cell_decreased",
    "leukopenie": "white_blood_cell_decreased",
    "white_blood_cell_decreased": "white_blood_cell_decreased",
    "thrombocytopenia": "platelet_count_decreased",
    "thrombozytopenie": "platelet_count_decreased",
    "platelet_count_decreased": "platelet_count_decreased",
    "lymphopenia": "lymphocyte_count_decreased",
    "lymphopenie": "lymphocyte_count_decreased",
    "lymphocyte_count_decreased": "lymphocyte_count_decreased",
    # Investigations (lab)
    "alanine_aminotransferase_increased": "alanine_aminotransferase_increased",
    "alt erhöht": "alanine_aminotransferase_increased",
    "alt increased": "alanine_aminotransferase_increased",
    "aspartate_aminotransferase_increased": "aspartate_aminotransferase_increased",
    "ast erhöht": "aspartate_aminotransferase_increased",
    "ast increased": "aspartate_aminotransferase_increased",
    "creatinine_increased": "creatinine_increased",
    "kreatinin erhöht": "creatinine_increased",
    "blood_bilirubin_increased": "blood_bilirubin_increased",
    "bilirubin erhöht": "blood_bilirubin_increased",
    "alkaline_phosphatase_increased": "alkaline_phosphatase_increased",
    "alp erhöht": "alkaline_phosphatase_increased",
    "ggt_increased": "ggt_increased",
    "ggt erhöht": "ggt_increased",
    "lipase_increased": "lipase_increased",
    "ejection_fraction_decreased": "ejection_fraction_decreased",
    "weight_loss": "weight_loss", "gewichtsverlust": "weight_loss",
    "weight_gain": "weight_gain",
    # Gastrointestinal
    "diarrhea": "diarrhea", "diarrhoe": "diarrhea",
    "diarrhoea": "diarrhea", "durchfall": "diarrhea",
    "constipation": "constipation", "verstopfung": "constipation",
    "nausea": "nausea", "übelkeit": "nausea",
    "vomiting": "vomiting", "erbrechen": "vomiting",
    "mucositis": "mucositis_oral", "oral mucositis": "mucositis_oral",
    "mucositis_oral": "mucositis_oral", "stomatitis": "mucositis_oral",
    "dysphagia": "dysphagia", "schluckstörung": "dysphagia",
    "abdominal_pain": "abdominal_pain", "bauchschmerzen": "abdominal_pain",
    # Nervous system
    "peripheral_sensory_neuropathy": "peripheral_sensory_neuropathy",
    "sensory neuropathy": "peripheral_sensory_neuropathy",
    "sensorische neuropathie": "peripheral_sensory_neuropathy",
    "peripheral_motor_neuropathy": "peripheral_motor_neuropathy",
    "motor neuropathy": "peripheral_motor_neuropathy",
    "motorische neuropathie": "peripheral_motor_neuropathy",
    "headache": "headache", "kopfschmerzen": "headache",
    "dizziness": "dizziness", "schwindel": "dizziness",
    "fatigue": "fatigue", "müdigkeit": "fatigue", "erschöpfung": "fatigue",
    # Skin
    "alopecia": "alopecia", "alopezie": "alopecia", "haarausfall": "alopecia",
    "rash": "rash_maculo_papular",
    "rash_maculo_papular": "rash_maculo_papular",
    "hautausschlag": "rash_maculo_papular",
    "pruritus": "pruritus", "juckreiz": "pruritus",
    "palmar_plantar_erythrodysesthesia_syndrome": "palmar_plantar_erythrodysesthesia_syndrome",
    "hand foot syndrome": "palmar_plantar_erythrodysesthesia_syndrome",
    "hand-fuß-syndrom": "palmar_plantar_erythrodysesthesia_syndrome",
    # Cardiac
    "heart_failure": "heart_failure", "herzinsuffizienz": "heart_failure",
    "ejection fraction decreased": "ejection_fraction_decreased",
    # Vascular
    "hypertension": "hypertension", "hypertonie": "hypertension",
    "thromboembolic_event": "thromboembolic_event",
    "thrombose": "thromboembolic_event", "thrombosis": "thromboembolic_event",
    "edema_limbs": "edema_limbs", "ödeme": "edema_limbs",
    "lymphedema": "lymphedema", "lymphödem": "lymphedema",
    # Respiratory
    "dyspnea": "dyspnea", "dyspnoea": "dyspnea",
    "atemnot": "dyspnea", "dyspnoe": "dyspnea",
    "pneumonitis": "pneumonitis",
    "cough": "cough", "husten": "cough",
    # Infections
    "sepsis": "sepsis",
    "lung_infection": "lung_infection",
    "pneumonia": "lung_infection", "pneumonie": "lung_infection",
    "urinary_tract_infection": "urinary_tract_infection",
    "harnwegsinfekt": "urinary_tract_infection",
    # Metabolism
    "hyponatremia": "hyponatremia", "hyponatriämie": "hyponatremia",
    "hypokalemia": "hypokalemia", "hypokaliämie": "hypokalemia",
    "hyperglycemia": "hyperglycemia", "hyperglykämie": "hyperglycemia",
    "hypoglycemia": "hypoglycemia", "hypoglykämie": "hypoglycemia",
    "anorexia": "anorexia", "anorexie": "anorexia",
    "dehydration": "dehydration",
    # Musculoskeletal
    "arthralgia": "arthralgia", "arthralgie": "arthralgia",
    "myalgia": "myalgia", "myalgie": "myalgia",
    "bone_pain": "bone_pain", "knochenschmerzen": "bone_pain",
    "back_pain": "back_pain", "rückenschmerzen": "back_pain",
    # Psychiatric
    "depression": "depression",
    "anxiety": "anxiety", "angst": "anxiety",
    "insomnia": "insomnia", "schlaflosigkeit": "insomnia",
}

# DB constraints: grade_1 … grade_5
_GRADE: Dict[str, str] = {
    "grade_1": "grade_1", "grade_2": "grade_2", "grade_3": "grade_3",
    "grade_4": "grade_4", "grade_5": "grade_5",
    "1": "grade_1", "2": "grade_2", "3": "grade_3",
    "4": "grade_4", "5": "grade_5",
    "grade 1": "grade_1", "grade 2": "grade_2", "grade 3": "grade_3",
    "grade 4": "grade_4", "grade 5": "grade_5",
    "grad 1": "grade_1", "grad 2": "grade_2", "grad 3": "grade_3",
    "grad 4": "grade_4", "grad 5": "grade_5",
    "ctcae 1": "grade_1", "ctcae 2": "grade_2", "ctcae 3": "grade_3",
    "ctcae 4": "grade_4", "ctcae 5": "grade_5",
    "ctcae grade 1": "grade_1", "ctcae grade 2": "grade_2",
    "ctcae grade 3": "grade_3", "ctcae grade 4": "grade_4",
    "ctcae grade 5": "grade_5",
}

# DB constraints: systemic_therapies/reason.yml
_REASON: Dict[str, str] = {
    "curative_intent_neoadjuvant": "curative_intent_neoadjuvant",
    "curative_intent_adjuvant": "curative_intent_adjuvant",
    "trial_mandated_systemic_therapy": "trial_mandated_systemic_therapy",
    "oligometastatic_program_partner": "oligometastatic_program_partner",
    "conversion_downstaging": "conversion_downstaging",
    "consolidation": "consolidation",
    "additive_maintenance": "additive_maintenance",
    "symptom_control": "symptom_control",
    "palliative": "palliative",
    "other": "other",
    # EN synonyms
    "neoadjuvant": "curative_intent_neoadjuvant",
    "adjuvant": "curative_intent_adjuvant",
    "curative": "curative_intent_neoadjuvant",
    "palliative (first line)": "palliative",
    "palliative (further line)": "palliative",
    "maintenance": "additive_maintenance",
    # DE synonyms
    "neoadjuvant (kurativ)": "curative_intent_neoadjuvant",
    "adjuvant (kurativ)": "curative_intent_adjuvant",
    "palliativ": "palliative",
    "symptomkontrolle": "symptom_control",
    "konsolidierung": "consolidation",
    "erhaltungstherapie": "additive_maintenance",
    "konversion": "conversion_downstaging",
    "downstaging": "conversion_downstaging",
    "sonstige": "other",
    "andere": "other",
}

# DB constraints: systemic_therapies/bone_protocol.yml
_BONE_PROTOCOL: Dict[str, str] = {
    "euramos": "euramos",
    "euroboss": "euroboss",
    "ewing2008": "ewing2008",
    "euroewing_2012_vide": "euroewing_2012_vide",
    "euroewing_2012_vdc_ie": "euroewing_2012_vdc_ie",
    "cws": "cws",
    "other": "other",
    "ewing 2008": "ewing2008",
    "euroewing 2012 vide": "euroewing_2012_vide",
    "euroewing 2012/vide": "euroewing_2012_vide",
    "euroewing 2012 vdc/ie": "euroewing_2012_vdc_ie",
    "euroewing 2012/vdc-ie": "euroewing_2012_vdc_ie",
    "euroewing2012vide": "euroewing_2012_vide",
    "euroewing2012vdcie": "euroewing_2012_vdc_ie",
    # Old enum values without direct DB equivalent
    "map (methotrexate, adriamycin, cisplatin)": "other",
    "map": "other",
    "mapie (map + ifosfamide, etoposide)": "other",
    "mapie": "other",
    "ie (ifosfamide, etoposide)": "other",
    "ie": "other",
    "vai (vincristine, adriamycin, ifosfamide)": "other",
    "vai": "other",
    "andere": "other",
    "sonstige": "other",
}

# DB constraints: systemic_therapies/softtissue_protocol.yml
_SOFTTISSUE_PROTOCOL: Dict[str, str] = {
    "cws": "cws",
    "pazoqol": "pazoqol",
    "napage": "napage",
    "other": "other",
    "pazopanib": "pazoqol",
    "ai (adriamycin, ifosfamide)": "other",
    "ai": "other",
    "maid (mesna, adriamycin, ifosfamide, dacarbazine)": "other",
    "maid": "other",
    "gemcitabine/docetaxel": "other",
    "trabectedin": "other",
    "eribulin": "other",
    "ifosfamide monotherapy": "other",
    "doxorubicin monotherapy": "other",
    "andere": "other",
    "sonstige": "other",
}

# DB constraints: systemic_therapies/discontinuation_reason.yml
_DISCONTINUATION_REASON: Dict[str, str] = {
    "completed": "completed",
    "progressive_disease_radiologic": "progressive_disease_radiologic",
    "progressive_disease_clinical": "progressive_disease_clinical",
    "toxicity": "toxicity",
    "maximum_safe_cumulative_dose": "maximum_safe_cumulative_dose",
    "clinical_deterioration_non_pd": "clinical_deterioration_non_pd",
    "intercurrent_illness": "intercurrent_illness",
    "patient_decision": "patient_decision",
    "definitive_local_therapy": "definitive_local_therapy",
    "switch_to_next_line_or_maintenance": "switch_to_next_line_or_maintenance",
    "treatment_related_mortality": "treatment_related_mortality",
    "lost_to_follow_up_or_administrative": "lost_to_follow_up_or_administrative",
    "death_tumor_related": "death_tumor_related",
    "death_non_tumor_related": "death_non_tumor_related",
    # EN synonyms
    "completion of planned therapy": "completed",
    "progressive disease": "progressive_disease_radiologic",
    "patient refusal": "patient_decision",
    "surgery planned": "definitive_local_therapy",
    "death": "death_tumor_related",
    # DE synonyms
    "abgeschlossen": "completed",
    "therapie abgeschlossen": "completed",
    "progressive erkrankung": "progressive_disease_radiologic",
    "progression": "progressive_disease_radiologic",
    "toxizität": "toxicity",
    "patientenentscheidung": "patient_decision",
    "patient lehnt ab": "patient_decision",
    "operation geplant": "definitive_local_therapy",
    "interkurrente erkrankung": "intercurrent_illness",
    "tod": "death_tumor_related",
    "tod (tumor)": "death_tumor_related",
    "tod (nicht tumor)": "death_non_tumor_related",
    "wechsel therapielinie": "switch_to_next_line_or_maintenance",
}

# DB constraints: systemic_therapies/hyperthermia_status.yml
_HYPERTHERMIA_STATUS: Dict[str, str] = {
    "no": "no",
    "yes_chemotherapy_hyperthermia": "yes_chemotherapy_hyperthermia",
    "none": "no",
    "planned": "yes_chemotherapy_hyperthermia",
    "ongoing": "yes_chemotherapy_hyperthermia",
    "completed": "yes_chemotherapy_hyperthermia",
    "nein": "no", "keine": "no",
    "ja": "yes_chemotherapy_hyperthermia",
    "geplant": "yes_chemotherapy_hyperthermia",
    "laufend": "yes_chemotherapy_hyperthermia",
    "abgeschlossen": "yes_chemotherapy_hyperthermia",
    "hyperthermie": "yes_chemotherapy_hyperthermia",
}

# DB constraints: systemic_therapies/clinical_trial_inclusion.yml
_CLINICAL_TRIAL_INCLUSION: Dict[str, str] = {
    "no": "no",
    "yes_ssn_outcome_prediction": "yes_ssn_outcome_prediction",
    "yes_other": "yes_other",
    "yes": "yes_other",
    "nein": "no",
    "ja": "yes_other",
    "ssn": "yes_ssn_outcome_prediction",
    "ssn outcome prediction": "yes_ssn_outcome_prediction",
    "ssn_outcome_prediction": "yes_ssn_outcome_prediction",
}

# DB constraints: systemic_therapies/patient_type.yml
_PATIENT_TYPE: Dict[str, str] = {
    "outpatient": "outpatient",
    "inpatient": "inpatient",
    "ambulant": "outpatient",
    "stationär": "inpatient",
    "stationaer": "inpatient",
}

# DB constraints: one, two, ..., nine, until_progression
_CYCLES_EXECUTED: Dict[str, str] = {
    "one": "one", "two": "two", "three": "three", "four": "four",
    "five": "five", "six": "six", "seven": "seven", "eight": "eight",
    "nine": "nine", "until_progression": "until_progression",
    "1": "one", "2": "two", "3": "three", "4": "four",
    "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine",
    "until progression": "until_progression",
    "bis progression": "until_progression",
    "bis zur progression": "until_progression",
}


@lru_cache(maxsize=1)
def _load_ctcae_event_codes() -> List[str]:
    """Load all CTCAE leaf event codes from constraints YAML."""
    ctcae_path = Path(__file__).resolve().parents[3] / "db" / "constraints" / "adverse_event" / "ctcae.yml"
    try:
        data = yaml.safe_load(ctcae_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(data, dict):
        return []
    codes: List[str] = []
    for items in data.values():
        if isinstance(items, list):
            for item in items:
                if isinstance(item, str) and item:
                    codes.append(item)
    # Deduplicate while preserving order.
    seen = set()
    deduped: List[str] = []
    for code in codes:
        if code not in seen:
            seen.add(code)
            deduped.append(code)
    return deduped


def _build_event_type_lookup() -> Dict[str, str]:
    """Build full event_type lookup: all CTCAE codes + useful aliases."""
    mapping: Dict[str, str] = {}

    # 1) All valid DB codes from YAML (pass-through + common textual variants)
    for code in _load_ctcae_event_codes():
        mapping[code] = code
        mapping[code.replace("_", " ")] = code
        mapping[code.replace("_", "-")] = code

    # 2) Extra aliases / language variants / legacy spellings
    mapping.update(_EVENT_TYPE_EXTRA)
    return mapping


# DB constraints: CTCAE leaf codes (ctcae.yml items) + aliases.
_EVENT_TYPE: Dict[str, str] = _build_event_type_lookup()


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------

def _lookup(mapping: Dict[str, str], value) -> Optional[str]:
    """Normalize a value via mapping.

    Tries the raw lowercased form first, then a compact form where spaces and
    hyphens are replaced by underscores.  Returns None if no match is found or
    if *value* is not a non-empty string.
    """
    if not isinstance(value, str) or not value.strip():
        return None
    s = value.strip().lower()
    result = mapping.get(s)
    if result is None:
        compact = s.replace(" ", "_").replace("-", "_")
        result = mapping.get(compact)
    return result


class _NormalizingModel(BaseModel):
    """Base class that applies field-level normalization before Pydantic validates.

    Subclasses declare a ``_NORMALIZERS`` class variable that maps field names
    to their lookup table.  Fields whose value cannot be normalized are kept as
    received (raw-text fallback — no data loss).
    """

    _NORMALIZERS: ClassVar[Dict[str, Dict[str, str]]] = {}

    @model_validator(mode="before")
    @classmethod
    def _normalize_fields(cls, data):
        if not isinstance(data, dict):
            return data
        for field, mapping in cls._NORMALIZERS.items():
            raw = data.get(field)
            normalized = _lookup(mapping, raw)
            if normalized is not None:
                data[field] = normalized
            elif raw is None or (isinstance(raw, str) and not raw.strip()):
                data[field] = None
            # else: keep raw as-is — kein Datenverlust
        return data


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------

class Drug(_NormalizingModel):
    """Einzelnes Medikament innerhalb einer systemischen Therapie (croms_drugs)."""

    _NORMALIZERS = {
        "drug_type": _DRUG_TYPE,
        "dose_unit": _DOSE_UNIT,
        "frequency_unit": _FREQUENCY_UNIT,
        "route": _ROUTE,
        "administration_day": _ADMINISTRATION_DAY,
    }

    # DB constraints: drug/drug_type.yml
    drug_type: Optional[str] = None
    dose: Optional[float] = Field(default=None, ge=0, description="Dosis")
    dose_unit: Optional[str] = Field(default=None, max_length=50, description="z.B. mg, mg/m², mg/kg")
    frequency: Optional[float] = Field(default=None, ge=0, description="Häufigkeit")
    frequency_unit: Optional[str] = Field(default=None, max_length=50, description="z.B. daily, weekly, q3w")
    frequency_unit_comment: Optional[str] = Field(default=None, max_length=500)
    # DB constraints: route.yml
    route: Optional[str] = Field(default=None, max_length=50)
    # DB constraints: monday–sunday
    administration_day: Optional[str] = Field(default=None, max_length=50)


class AdverseEvent(_NormalizingModel):
    """Unerwünschtes Ereignis während systemischer Therapie (croms_adverse_events)."""

    _NORMALIZERS = {
        "medical_area": _MEDICAL_AREA,
        "event_type": _EVENT_TYPE,
        "grade": _GRADE,
    }

    # DB constraints: CTCAE category keys (ctcae.yml top-level)
    medical_area: Optional[str] = Field(default=None, max_length=200)
    # DB constraints: CTCAE leaf codes (ctcae.yml items)
    event_type: Optional[str] = Field(default=None, max_length=200)
    # DB constraints: grade_1, grade_2, grade_3, grade_4, grade_5
    grade: Optional[str] = Field(default=None, max_length=10, description="CTCAE Grade (1-5)")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    comment: Optional[str] = Field(default=None, max_length=1000)


class SystemicTherapyEvent(_NormalizingModel):
    """Eine Zeile aus croms_systemic_therapies.

    Systemische Therapie = Chemotherapie, Targeted Therapy, Immuntherapie.
    """

    _NORMALIZERS = {
        "reason": _REASON,
        "bone_protocol": _BONE_PROTOCOL,
        "softtissue_protocol": _SOFTTISSUE_PROTOCOL,
        "discontinuation_reason": _DISCONTINUATION_REASON,
        "hyperthermia_status": _HYPERTHERMIA_STATUS,
        "clinical_trial_inclusion": _CLINICAL_TRIAL_INCLUSION,
        "patient_type": _PATIENT_TYPE,
        "cycles_executed": _CYCLES_EXECUTED,
    }

    institution_id: Optional[int] = Field(default=None, ge=0)
    patient_id: Optional[int] = Field(default=None, ge=0)
    responsible_oncologist_id: Optional[int] = Field(default=None, ge=0)

    # DB constraints: curative_intent_neoadjuvant, curative_intent_adjuvant,
    #   trial_mandated_systemic_therapy, oligometastatic_program_partner,
    #   conversion_downstaging, consolidation, additive_maintenance,
    #   symptom_control, palliative, other
    reason: Optional[str] = None
    reason_comment: Optional[str] = Field(default=None, max_length=1000)
    treatment_line: Optional[int] = None

    # DB constraints: euramos, euroboss, ewing2008, euroewing_2012_vide,
    #   euroewing_2012_vdc_ie, cws, other
    bone_protocol: Optional[str] = None
    bone_protocol_comment: Optional[str] = Field(default=None, max_length=1000)
    # DB constraints: cws, pazoqol, napage, other
    softtissue_protocol: Optional[str] = None
    softtissue_protocol_comment: Optional[str] = Field(default=None, max_length=1000)

    cycle_start_date: Optional[date] = None
    cycle_end_date: Optional[date] = None
    # DB constraints: one, two, ..., nine, until_progression
    cycles_executed: Optional[str] = Field(default=None, max_length=50)

    was_rct_concomittant: bool = Field(default=False, description="Gleichzeitige Radiochemotherapie")
    # DB constraints: no, yes_chemotherapy_hyperthermia
    hyperthermia_status: Optional[str] = None

    # DB constraints: no, yes_ssn_outcome_prediction, yes_other
    clinical_trial_inclusion: Optional[str] = None

    # DB constraints: completed, progressive_disease_radiologic,
    #   progressive_disease_clinical, toxicity, maximum_safe_cumulative_dose,
    #   clinical_deterioration_non_pd, intercurrent_illness, patient_decision,
    #   definitive_local_therapy, switch_to_next_line_or_maintenance,
    #   treatment_related_mortality, lost_to_follow_up_or_administrative,
    #   death_tumor_related, death_non_tumor_related
    discontinuation_reason: Optional[str] = None

    # DB constraints: outpatient, inpatient
    patient_type: Optional[str] = None

    assessment_date: Optional[date] = Field(default=None, description="Datum des Response-Assessments")
    comments: Optional[str] = Field(default=None, max_length=2000)

    drugs: List[Drug] = Field(default_factory=list)
    adverse_events: List[AdverseEvent] = Field(default_factory=list)

    @field_validator("cycle_start_date", "cycle_end_date", "assessment_date", mode="before")
    @classmethod
    def parse_dates(cls, v):
        """Parst flexible Datumsformate (DD.MM.YYYY, DD.MM.YY, DD/MM/YYYY, YYYY-MM-DD)."""
        if v is None or (isinstance(v, str) and not v.strip()):
            return None
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            s = v.strip().split(" ")[0]
            for fmt in ("%d.%m.%Y", "%d.%m.%y", "%d/%m/%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(s, fmt).date()
                except ValueError:
                    pass
        return None


class SystemicTherapyEvents(BaseModel):
    """Wrapper für mehrere systemische Therapie-Events aus einem Bericht."""

    events: List[SystemicTherapyEvent]
