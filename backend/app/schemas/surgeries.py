from __future__ import annotations

from datetime import date, datetime
from typing import Optional, List
import re

from pydantic import BaseModel, Field, field_validator, model_validator

# Locale label-to-code maps (extracted from db/locales/croms.enums*.yml)
RESECTION_LABELS = {
    "not_applicable": "Not applicable",
    "res_a_1_simple": "resA.1 Simple",
    "res_a_2_muscle_resection": "resA.2 Muscle resection",
    "res_a_3_vessel_dissection": "resA.3 Vessel dissection",
    "res_a_4_nerve_dissection": "resA.4 Nerve dissection",
    "res_a_5_periost_resection": "resA.5 Periost resection",
    "res_a_6_bone_resection": "resA.6 Bone resection",
    "res_a_7_vessel_resection": "resA.7 Vessel resection",
    "res_a_8_nerve_resection": "resA.8 Nerve resection",
    "res_a_9_mr_hifu": "resA.9 MR-HIFU",
    "res_a_10_tendon_resection": "resA.10 Tendon resection",
    "res_a_11_ligament_resection": "resA.11 Ligament resection",
    "res_a_12_resection_of_funiculus_scrotum_genitals": "resA.12 Resection of funiculus; scrotum; genitals",
    "res_a_13_other_sts_resection": "resA.13 Other STS resection (please specify in next field)",
    "res_b_1_simple_curettage": "resB.1 Simple curettage",
    "res_b_2_hemi_cortex_resection": "resB.2 Hemi-cortex resection",
    "res_b_3_complete_whole_bone_res_joint_sparing": "resB.3 Complete / whole bone res. (incl. adj. soft tiss.): joint sparing (outside / preservation of joint)",
    "res_b_4_complete_whole_bone_res_transarticular_resection": "resB.4 Complete / whole bone res. (incl. adj. soft tiss.): transarticular resection (through the joint)",
    "res_b_5_complete_whole_bone_res_extraarticular_joint_resection": "resB.5 Complete / whole bone res. (incl. adj. soft tiss.): extraarticular joint resection",
    "res_b_6_with_3d_patient_specific_cutting_guides": "resB.6 With 3D patient specific cutting guides",
    "res_b_6_1_3d_planning": "resB.6.1 3D planning",
    "res_b_8_radiofrequency_ablation_rfa_cryotherapy_mr_hifu": "resB.8 Radiofrequency ablation (RFA); cryotherapy; MR-HIFU",
    "res_b_9_resection_replantation_upper_extremity": "resB.9 Resection-replantation (upper extremity)",
    "res_b_10_rotationplasty_lower_extremity": "resB.10 Rotationplasty (lower extremity)",
    "res_b_80_tendon_resection": "resB.80 Tendon resection",
    "res_b_81_ligament_resection": "resB.81 Ligament resection",
    "res_b_82_forced_epiphyseolysis_ot_canadell_technique": "resB.82 Forced epiphyseolysis OT (Canadell technique)",
    "res_b_83_extra_articular_scapulo_humeral_resection_tikhoff_linberg": "resB.83 Extra-articular scapulo-humeral resection (Tikhoff-Linberg)",
    "res_b_84_biopsy_gain_of_diagnostic_tissue": "resB.84 Biopsy / gain of diagnostic tissue",
    "res_b_85_removal_of_cement": "resB.85 Removal of cement",
    "res_b_86_other_bone_resection": "resB.86 Other bone resection (please specify in next field)",
    "res_c_1_chest_wall_resection": "resC.1 Chest wall resection",
    "res_c_2_wedge_resection": "resC.2 Wedge resection",
    "res_c_3_segmental_resection": "resC.3 Segmental resection",
    "res_c_4_lobectomy": "resC.4 Lobectomy",
    "res_c_5_bilobectomy_pneumonectomy": "resC.5 Bilobectomy / pneumonectomy",
    "res_c_6_pleuropneumonectomy": "resC.6 Pleuropneumonectomy",
    "res_c_7_thoracic_wall_resection_ribs": "resC.7 Thoracic wall resection / ribs",
    "res_c_10_other_chest_lung_resection": "resC.10 Other chest / lung resection (please specify in next field)",
    "res_c_8_wedge_resection": "resC.8 Wedge resection",
    "res_c_9_lobectomy": "resC.9 Lobectomy",
    "res_d_1_abdominal_wall_resection": "resD.1 Abdominal wall resection",
    "res_d_2_none": "resD.2 None",
    "res_d_3_kidney": "resD.3 Kidney",
    "res_d_4_suprarenal_glands": "resD.4 Suprarenal glands",
    "res_d_5_ureter": "resD.5 Ureter",
    "res_d_6_bladder": "resD.6 Bladder",
    "res_d_7_colon_rectum": "resD.7 Colon / rectum",
    "res_d_8_bowel": "resD.8 Bowel",
    "res_d_9_uterus_ovaries": "resD.9 Uterus / ovaries",
    "res_d_10_spleen": "resD.10 Spleen",
    "res_d_11_liver": "resD.11 Liver",
    "res_d_12_pancreas": "resD.12 Pancreas",
    "res_d_13_gall_bladder": "resD.13 Gall bladder",
    "res_d_14_aorta_cava": "resD.14 Aorta / cava",
    "res_d_15_other_abdominal_resection": "resD.15 Other abdominal resection (please specify in next field)",
    "res_e_5_infection": "resE.5 Infection",
    "res_e_7_wound_healing_failure": "resE.7 Wound healing failure (incl. hematoma)",
    "res_e_8_infection": "resE.8 Infection",
    "res_e_9_osteosynthesis_failure": "resE.9 Osteosynthesis failure",
    "res_e_10_fracture": "resE.10 Fracture",
    "res_e_12_pseudoarthrosis": "resE.12 Pseudoarthrosis",
    "res_e_1_debridement": "resE.1 Debridement",
    "res_e_2_inlay_change": "resE.2 Inlay change",
    "res_e_3_partial_removal_of_prosthesis": "resE.3 Partial removal of prosthesis",
    "res_e_4_complete_removal_of_prosthesis": "resE.4 Complete removal of prosthesis",
    "res_e_11_other": "resE.11 Other (please specify in next field)",
}

RECONSTRUCTION_LABELS = {
    "not_applicable": "Not applicable",
    "skin_mesh_graft": "Skin/mesh graft",
    "rectus_abdominis": "Rectus abdominis",
    "rectus_abdominis_with_skin": "Rectus abdominis (with skin)",
    "gastrocnemius": "Gastrocnemius",
    "gastrocnemius_with_skin": "Gastrocnemius (with skin)",
    "latissimus_dorsi": "Latissimus dorsi",
    "latissimus_dorsi_with_skin": "Latissimus dorsi (with skin)",
    "gracilis": "Gracilis",
    "gracilis_with_skin": "Gracilis (with skin)",
    "sartorius": "Sartorius",
    "sartorius_with_skin": "Sartorius (with skin)",
    "soleus": "Soleus",
    "soleus_with_skin": "Soleus (with skin)",
    "serratus": "Serratus",
    "serratus_with_skin": "Serratus (with skin)",
    "other_muscle_flap": "Other muscle flap (please specify in next field)",
    "alt_pedicled": "ALT",
    "other_perforator_flap_pedicled": "Other perforator flap (please specify in next field)",
    "latissimus_dorsi_free": "Latissimus dorsi",
    "gracilis_free": "Gracilis",
    "other_free_tissue_transfer": "Other free tissue transfer (please specify in next field)",
    "alt_free": "ALT",
    "other_perforator_flap_free": "Other perforator flap (please specify in next field)",
    "autologous_tendon_transfer": "Autologous tendon transfer",
    "allograft_tendon_reconstruction": "Allograft tendon reconstruction",
    "local_tendon_reconstruction": "Local tendon reconstruction",
    "cementation": "Cementation",
    "orif": "ORIF (incl. bone ankers; removal of OS material)",
    "pedicle_screws_rods_cages": "Pedicle screws/rods/cages",
    "artificial_bone_substitute": "Artificial bone substitute (Ca-sulfate etc)",
    "autograft": "Autograft",
    "vascularised_fibula_autograft": "Vascularised fibula autograft (based on fibular artery)",
    "vascularised_epiphyseal_transfer": "Vascularised epiphyseal transfer (based on tibial anterior artery)",
    "non_vascularised_fibula_autograft": "Non-vascularised fibula autograft",
    "pasteurised_autograft": "Pasteurised autograft",
    "allograft_chips": "Allograft chips",
    "bulk_allograft": "Bulk allograft",
    "conventional_prosthesis": "Conventional prosthesis",
    "modular_tumor_prosthesis": "Modular tumor prosthesis",
    "custom_made_prosthesis": "Custom-made prosthesis",
    "growing_prosthesis": "Growing prosthesis",
    "arthrodesis": "Arthrodesis",
    "distraction_osteogenesis": "Distraction osteogenesis",
    "cement_spacer_pseudoarthrosis": "Cement spacer/pseudoarthrosis/flail joint",
    "canadell_distraction_epiphyseolysis": "Canadell distraction epiphyseolysis",
    "other_bone_reconstruction": "Other bone reconstruction (please specify in next field)",
    "pseudarthrosis_intentional": "Pseudarthrosis (intentional)",
    "goretex_mesh_trevira": "Goretex mesh; Trevira etc",
    "artery_complete": "Artery complete",
    "artery_patch": "Artery patch",
    "vein_complete": "Vein complete",
    "vein_patch": "Vein patch",
    "lympho_venous": "Lympho-venous",
    "other_vessel_reconstruction": "Other vessel reconstruction (please specify in next field)",
    "nerve_reconstruction": "Nerve reconstruction (please specify in next field)",
    "neurotisation_local_transfer": "Neurotisation/local transfer",
    "neurotisation_local_transfer_autologous": "Neurotisation/local transfer autologous (please specify in next field)",
    "neurotisation_local_transfer_allograft": "Neurotisation/local transfer allograft",
    "chest_wall_reconstruction": "Chest wall reconstruction",
    "abdominal_wall_reconstruction": "Abdominal wall reconstruction",
    "colon_anastomosis": "Colon anastomosis",
    "stoma": "Stoma",
    "bladder": "Bladder",
    "ureter": "Ureter",
    "other_intraabdominal_reconstruction": "Other intraabdominal reconstruction (please specify in next field)",
    "cement_spacer_implantation": "Cement spacer implantation",
    "partial_implantation_replacement": "Partial implantation/replacement",
    "complete_prosthesis_implantation_replacement": "Complete prosthesis implantation/replacement",
}

AMPUTATION_LABELS = {
    "not_determined": "Not determined",
    "resh_010": "Finger / ray amputation",
    "resh_020": "Trans-metacarpal / partial hand",
    "resh_030": "Wrist disarticulation",
    "resh_040": "Trans-radial (forearm)",
    "resh_050": "Elbow disarticulation",
    "resh_060": "Trans-humeral",
    "resh_070": "Shoulder disarticulation",
    "resh_099": "Other upper-extremity amputation",
    "resh_080": "Fore-quarter without chest wall",
    "resh_081": "Fore-quarter with chest wall",
    "resh_110": "Toe / ray amputation",
    "resh_120": "Trans-metatarsal / forefoot",
    "resh_130": "Mid-foot (Lisfranc / Chopart) amputation",
    "resh_140": "Ankle disarticulation (Syme / Boyd)",
    "resh_150": "Transtibial (below-knee, BKA)",
    "resh_160": "Knee disarticulation",
    "resh_170": "Trans-femoral (above-knee)",
    "resh_180": "Hip disarticulation",
    "resh_199": "Other lower-extremity amputation",
    "resg_080": "External hemipelvectomy (hind-quarter)",
    "ext_ta": "EXT-TA With dissociation of pelvic ring; no hip disarticulation",
    "ext_ti": "EXT-TI Supra-acetabular; extra-articular",
    "ext_ths": "EXT-THS Incl. hemilumbar; without contralateral spinopelvic dissociation",
    "ext_ths_diss": "EXT-THS+DISS Incl. hemilumbar; with contralateral spinopelvic dissociation",
    "ext_hc": "EXT-HC Complete removal including pelvic ring and both lower limbs",
    "ext_bi": "EXT-BI Bilateral resection without complete hemicorporectomy",
    "ext_visc": "EXT-VISC Includes bladder, rectum, or adjacent organs",
}

HEMIPELVECTOMY_LABELS = {
    "not_applicable": "Not applicable",
    "e_i_il_ls_rp": "Type I, extraarticular, ilium, lateral to SIJ, ring preserved",
    "e_i_il_ls_rd": "Type I, extraarticular, ilium, lateral to SIJ, ring disrupted",
    "e_i_is_ms": "Type I–IV, extraarticular, ilium-sacrum, medial to SIJ",
    "e_i_is_f": "Type I–IV, extraarticular, ilium-sacrum, through foramina",
    "e_i_is_mf": "Type I–IV, extraarticular, ilium-sacrum, medial to foramina/midline",
    "e_ix_il_ls": "Type I, transarticular, ilium, lateral to SIJ",
    "e_ix_is_ms": "Type I–IV, transarticular, ilium-sacrum, medial to SIJ, lateral to foramina",
    "e_ix_is_f": "Type I–IV, transarticular, ilium-sacrum, through foramina",
    "e_ix_is_mf": "Type I–IV, transarticular, ilium-sacrum, medial to foramina/midline",
    "e_iip_a_sy": "partial, acetabulum, superior part of Y (ilium)",
    "e_iip_p_my": "partial, pubis, medial part of Y (pubis)",
    "e_iip_i_py": "partial, ischium, posterior part of Y (ischium)",
    "e_iix_pi_c": "complete, transarticular, pubis/ischium",
    "e_ii_a_rd": "complete, extraarticular, ring disrupted",
    "e_ii_a_rp": "complete, extraarticular, ring preserved",
    "e_iii_p_sr": "superior ramus only",
    "e_iii_p_ir_rp": "inferior ramus only, tuber spared, ring preserved",
    "e_iii_p_ir_rd": "inferior ramus only, tuber spared, ring disrupted",
    "e_iii_p_irt": "inferior ramus only, tuber resected",
    "e_iii_p_sir": "superior + inferior ramus, tuber spared",
    "e_iii_p_sirt": "superior + inferior ramus, tuber resected",
    "e_iii_p_bsr": "bilateral superior ramus",
    "e_iii_p_bsir": "bilateral superior + inferior rami, tuber spared",
    "e_iii_p_bsirt": "bilateral superior + inferior rami, tuber resected",
    "e_iii_p_birt": "bilateral inferior ramus only, tuber resected (rare)",
    "e_iv_s_ls_h": "low sacrectomy (below S2), hemi/unilateral, no SIJ involvement",
    "e_iv_s_ls_b": "low sacrectomy (below S2), complete/bilateral, no SIJ involvement",
    "e_iv_s_hs_u": "high sacrectomy (incl. S1&2), unilateral, SIJ preserved, no LP-diss",
    "e_iv_s_hs_b": "high sacrectomy (incl. S1&2), bilateral, SIJ preserved, no LP-diss",
    "e_iv_s_hs_l": "high sacrectomy (incl. S1&2), lateral to SIJ, through ilium, no LP-diss",
    "e_iv_s_hs_ld": "high sacrectomy (incl. S1&2), lateral to SIJ, through ilium, with LP-diss",
    "e_iv_s_hslp_p": "high sacrectomy (incl. S1&2) + partial lumbar resection, no LP-diss",
    "e_iv_s_hslp_c": "high sacrectomy (incl. S1&2) + cL5 and above resection, with LP-diss",
    "e_ix_ii_ls": "partial hip joint, transarticular, lateral to SIJ (ilium only)",
    "e_i_ii_ls": "complete hip joint, extraarticular, supracetabular, lateral to SIJ (ilium only)",
    "e_iix_iii_sr": "superior ramus only, partial hip joint, transarticular",
    "e_iix_iii_ist": "ischium only, tuber spared, partial hip joint, transarticular",
    "e_iix_iii_irt": "inferior ramus only, tuber resected, partial hip joint, transarticular",
    "e_iix_iii_sirt": "through symphysis; superior + inferior ramus, tuber spared, partial hip joint",
    "e_iix_iii_sirtx": "through symphysis; superior + inferior ramus, tuber resected, partial hip joint",
    "e_iix_iii_bsr": "bilateral superior ramus, partial hip joint, transarticular",
    "e_iix_iii_bsir": "bilateral superior + inferior rami, tuber spared, partial hip joint",
    "e_iix_iii_bsirt": "bilateral superior + inferior rami, tuber resected, partial hip joint",
    "e_ii_iii_sr": "superior ramus only, complete hip joint, extraarticular supracetabular",
    "e_ii_iii_ist": "ischium only, tuber spared, complete hip joint, extraarticular",
    "e_ii_iii_irt": "inferior ramus only, tuber resected, complete hip joint, extraarticular",
    "e_ii_iii_sirt": "through symphysis; superior + inferior ramus, tuber spared, complete hip joint",
    "e_ii_iii_sirtx": "through symphysis; superior + inferior ramus, tuber resected, complete hip joint",
    "e_ii_iii_bsr": "bilateral superior ramus, complete hip joint, extraarticular",
    "e_ii_iii_bsir": "bilateral superior + inferior rami, tuber spared, complete hip joint",
    "e_ii_iii_bsirt": "bilateral superior + inferior rami, tuber resected, complete hip joint",
    "e_ix_iix_iii_sr": "superior ramus only, partial hip joint, lateral to SIJ",
    "e_ix_iix_iii_ist": "ischium only, tuber spared, partial hip joint",
    "e_ix_iix_iii_irt": "inferior ramus only, tuber resected, partial hip joint",
    "e_ix_iix_iii_sirt": "through symphysis; superior + inferior ramus, tuber spared, partial hip joint",
    "e_ix_iix_iii_sirtx": "through symphysis; superior + inferior ramus, tuber resected, partial hip joint",
    "e_ix_iix_iii_bsr": "bilateral superior ramus, partial hip joint",
    "e_ix_iix_iii_bsir": "bilateral superior + inferior rami, tuber spared, partial hip joint",
    "e_ix_iix_iii_bsirt": "bilateral superior + inferior rami, tuber resected, partial hip joint",
    "e_iii_iv_l_lsi_m_sa_s_nd": "lateral to SIJ, medial to SIJ, lateral to foramina (sacral ala), no spinopelvic dissociation",
    "e_iii_iv_l_lsi_m_sa_s_ud": "lateral to SIJ, medial to SIJ, lateral to foramina (sacral ala), unilateral spinopelvic dissociation",
    "e_iii_iv_l_lsi_m_sa_s_bd": "lateral to SIJ, medial to SIJ, lateral to foramina (sacral ala), bilateral spinopelvic dissociation",
    "e_iii_iv_l_lsi_m_sa_s_lv": "lateral to SIJ, medial to SIJ, lateral to foramina (sacral ala), includes lumbar vertebra",
    "e_iii_iv_l_lsi_m_f_s_nd": "lateral to SIJ, through foramina (S1 or S2), no spinopelvic dissociation",
    "e_iii_iv_l_lsi_m_f_s_ud": "lateral to SIJ, through foramina (S1 or S2), unilateral spinopelvic dissociation",
    "e_iii_iv_l_lsi_m_f_s_bd": "lateral to SIJ, through foramina (S1 or S2), bilateral spinopelvic dissociation",
    "e_iii_iv_l_lsi_m_f_s_lv": "lateral to SIJ, through foramina (S1 or S2), includes lumbar vertebra",
    "e_iii_iv_l_lsi_m_bm_s_nd": "lateral to SIJ, between foramina and midline, no spinopelvic dissociation",
    "e_iii_iv_l_lsi_m_bm_s_ud": "lateral to SIJ, between foramina and midline, unilateral spinopelvic dissociation",
    "e_iii_iv_l_lsi_m_bm_s_bd": "lateral to SIJ, between foramina and midline, bilateral spinopelvic dissociation",
    "e_iii_iv_l_lsi_m_bm_s_lv": "lateral to SIJ, between foramina and midline, includes lumbar vertebra",
    "e_iii_iv_l_lsi_m_mc_s_nd": "lateral to SIJ, midline to contralateral foramina, no spinopelvic dissociation",
    "e_iii_iv_l_lsi_m_mc_s_ud": "lateral to SIJ, midline to contralateral foramina, unilateral spinopelvic dissociation",
    "e_iii_iv_l_lsi_m_mc_s_bd": "lateral to SIJ, midline to contralateral foramina, bilateral spinopelvic dissociation",
    "e_iii_iv_l_lsi_m_mc_s_lv": "lateral to SIJ, midline to contralateral foramina, includes lumbar vertebra",
    "e_iii_iv_l_lsi_m_cf_s_nd": "lateral to SIJ, contralateral foramina (symmetric or oblique), no spinopelvic dissociation",
    "e_iii_iv_l_lsi_m_cf_s_ud": "lateral to SIJ, contralateral foramina (symmetric or oblique), unilateral spinopelvic dissociation",
    "e_iii_iv_l_lsi_m_cf_s_bd": "lateral to SIJ, contralateral foramina (symmetric or oblique), bilateral spinopelvic dissociation",
    "e_iii_iv_l_lsi_m_cf_s_lv": "lateral to SIJ, contralateral foramina (symmetric or oblique), includes lumbar vertebra",
}


def _canon_label(value: str) -> str:
    s = value.lower().replace("–", "-")
    return re.sub(r"[^a-z0-9]+", "", s)


def _build_label_to_code_map(code_to_label: dict[str, str]) -> dict[str, str]:
    buckets: dict[str, list[str]] = {}
    for code, label in code_to_label.items():
        buckets.setdefault(_canon_label(label), []).append(code)
    # Use only unique label->code mappings to avoid ambiguous mappings.
    return {k: v[0] for k, v in buckets.items() if len(v) == 1}


RESECTION_LABEL_TO_CODE = _build_label_to_code_map(RESECTION_LABELS)
RECONSTRUCTION_LABEL_TO_CODE = _build_label_to_code_map(RECONSTRUCTION_LABELS)
AMPUTATION_LABEL_TO_CODE = _build_label_to_code_map(AMPUTATION_LABELS)
HEMIPELVECTOMY_LABEL_TO_CODE = _build_label_to_code_map(HEMIPELVECTOMY_LABELS)


class SurgeryEvent(BaseModel):
    """
    Repräsentiert eine Zeile aus der croms_surgeries Tabelle.

    Constraint-Werte (DB-Codes):
      indication:              db/constraints/surgery/indication.yml
      surgery_side:            db/constraints/surgery/surgery_side.yml
      resection:               db/constraints/surgery/resection.yml
      reconstruction:          db/constraints/surgery/reconstruction.yml
      amputation:              db/constraints/surgery/amputation.yml
      hemipelvectomy:          db/constraints/surgery/hemipelvectomy.yml
      participated_disciplines: db/constraints/surgery/participated_disciplines.yml
    """

    institution_id: Optional[int] = Field(default=None, ge=0, description="Institution ID")
    patient_id: Optional[int] = Field(default=None, ge=0, description="Patient ID")
    responsible_surgeon_id: Optional[int] = Field(default=None, ge=0, description="Verantwortlicher Chirurg")

    surgery_date: Optional[date] = Field(default=None, description="Datum der Operation")

    indication: Optional[str] = None
    indication_comment: Optional[str] = Field(default=None, max_length=1000)

    surgery_side: Optional[str] = None
    anatomic_region: Optional[str] = None

    greatest_surgical_tumor_dimension_in_mm: Optional[int] = Field(
        default=None, ge=0, description="Größte Tumordimension in mm"
    )
    had_tumor_spillage: Optional[bool] = Field(default=None, description="Tumor-Spillage während der OP")

    resection: List[str] = Field(default_factory=list, description="Art der Resektion (mehrere möglich)")
    resected_tumor_margin: Optional[str] = None

    reconstruction: Optional[str] = None
    amputation: Optional[str] = None
    hemipelvectomy: List[str] = Field(default_factory=list, description="Hemipelvektomie-Details (falls zutreffend)")

    first_revision_details: Optional[str] = Field(default=None, max_length=500)
    second_revision_details: Optional[str] = Field(default=None, max_length=500)

    participated_disciplines: List[str] = Field(default_factory=list, description="Beteiligte Fachdisziplinen")
    participated_disciplines_comment: Optional[str] = Field(default=None, max_length=1000)

    # ─── Normalizer ────────────────────────────────────────────────────────────

    @staticmethod
    def _normalize_indication(value) -> Optional[str]:
        """
        Constraint-Werte laut db/constraints/surgery/indication.yml:
        first_surgery_for_this_reason, first_surgery_after_whoops,
        pathological_fracture, first_revision_surgery,
        second_or_more_revision_surgery, first_surgery_for_local_recurrence,
        second_or_more_surgery_for_local_recurrence,
        first_surgery_for_metastasis, second_or_more_surgery_for_metastasis,
        other_reason
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z0-9_]", "", compact)

        allowed = {
            "first_surgery_for_this_reason", "first_surgery_after_whoops",
            "pathological_fracture", "first_revision_surgery",
            "second_or_more_revision_surgery", "first_surgery_for_local_recurrence",
            "second_or_more_surgery_for_local_recurrence",
            "first_surgery_for_metastasis", "second_or_more_surgery_for_metastasis",
            "other_reason",
        }
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        # Whoops / unplanned excision
        if any(t in lower for t in ["whoops", "unplanned excision", "unbeabsichtigte", "ungeplant"]):
            return "first_surgery_after_whoops"

        # Pathological fracture
        if any(t in lower for t in ["pathological fracture", "pathologisch", "pathologische fraktur"]):
            return "pathological_fracture"

        # Second-or-more variants (check before "first")
        is_second = any(t in lower for t in ["second", "2nd", "3rd", "weitere", "dritte", "erneut"])
        if is_second:
            if any(t in lower for t in ["local recurrence", "lokalrezidiv"]):
                return "second_or_more_surgery_for_local_recurrence"
            if any(t in lower for t in ["metastas"]):
                return "second_or_more_surgery_for_metastasis"
            if any(t in lower for t in ["revision"]):
                return "second_or_more_revision_surgery"

        # First-occurrence variants
        if any(t in lower for t in ["local recurrence", "lokalrezidiv", "lokal rezidiv"]):
            return "first_surgery_for_local_recurrence"
        if any(t in lower for t in ["metastas", "metastectomy", "metastasectomy"]):
            return "first_surgery_for_metastasis"
        if any(t in lower for t in ["revision"]):
            return "first_revision_surgery"

        # Other / palliative / debulking
        if any(t in lower for t in ["palliativ", "palliative", "debulking", "other", "andere", "sonst"]):
            return "other_reason"

        # Primary / definitive / curative → first surgery
        if any(t in lower for t in [
            "definitive", "curative", "kurativ", "primary", "erstmalig",
            "biopsy", "preoperative", "präoperativ", "first surgery", "erste operation",
            "first_surgery", "primary surgery",
        ]):
            return "first_surgery_for_this_reason"

        return raw

    @staticmethod
    def _normalize_surgery_side(value) -> Optional[str]:
        """
        Constraint-Werte laut db/constraints/surgery/surgery_side.yml:
        right, left, midline
        (bilateral / not_applicable nicht im Constraint → raw erhalten)
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        lower = raw.lower()

        allowed = {"right", "left", "midline"}
        if lower in allowed:
            return lower

        if any(t in lower for t in ["right", "rechts"]):
            return "right"
        if any(t in lower for t in ["left", "links"]):
            return "left"
        if any(t in lower for t in ["midline", "mittel", "zentral", "median"]):
            return "midline"

        # bilateral, not_applicable: nicht im Constraint → raw
        return raw

    @staticmethod
    def _normalize_resected_tumor_margin(value) -> Optional[str]:
        """
        Normalisiert Resektionsrand auf: r0, r1, r2, unknown
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        lower = raw.lower()

        allowed = {"r0", "r1", "r2", "unknown"}
        if lower in allowed:
            return lower

        if "r0" in lower or "r 0" in lower or "negative margin" in lower or "complete resection" in lower:
            return "r0"
        if "r1" in lower or "r 1" in lower or "microscopic" in lower or "mikro" in lower:
            return "r1"
        if "r2" in lower or "r 2" in lower or "macroscopic" in lower or "makro" in lower:
            return "r2"
        if any(t in lower for t in ["unknown", "unbekannt", "unklar"]):
            return "unknown"

        return raw

    @staticmethod
    def _normalize_resection_item(value) -> Optional[str]:
        """
        Normalisiert einzelne Resektions-Codes.
        Constraint-Werte laut db/constraints/surgery/resection.yml.
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z0-9_]", "", compact)

        valid_codes = {
            "not_applicable",
            "res_a_1_simple", "res_a_2_muscle_resection", "res_a_3_vessel_dissection",
            "res_a_4_nerve_dissection", "res_a_5_periost_resection", "res_a_6_bone_resection",
            "res_a_7_vessel_resection", "res_a_8_nerve_resection", "res_a_9_mr_hifu",
            "res_a_10_tendon_resection", "res_a_11_ligament_resection",
            "res_a_12_resection_of_funiculus_scrotum_genitals", "res_a_13_other_sts_resection",
            "res_b_1_simple_curettage", "res_b_2_hemi_cortex_resection",
            "res_b_3_complete_whole_bone_res_joint_sparing",
            "res_b_4_complete_whole_bone_res_transarticular_resection",
            "res_b_5_complete_whole_bone_res_extraarticular_joint_resection",
            "res_b_6_with_3d_patient_specific_cutting_guides", "res_b_6_1_3d_planning",
            "res_b_8_radiofrequency_ablation_rfa_cryotherapy_mr_hifu",
            "res_b_9_resection_replantation_upper_extremity",
            "res_b_10_rotationplasty_lower_extremity",
            "res_b_80_tendon_resection", "res_b_81_ligament_resection",
            "res_b_82_forced_epiphyseolysis_ot_canadell_technique",
            "res_b_83_extra_articular_scapulo_humeral_resection_tikhoff_linberg",
            "res_b_84_biopsy_gain_of_diagnostic_tissue", "res_b_85_removal_of_cement",
            "res_b_86_other_bone_resection",
            "res_c_1_chest_wall_resection", "res_c_2_wedge_resection",
            "res_c_3_segmental_resection", "res_c_4_lobectomy",
            "res_c_5_bilobectomy_pneumonectomy", "res_c_6_pleuropneumonectomy",
            "res_c_7_thoracic_wall_resection_ribs", "res_c_8_wedge_resection",
            "res_c_9_lobectomy", "res_c_10_other_chest_lung_resection",
            "res_d_1_abdominal_wall_resection", "res_d_2_none", "res_d_3_kidney",
            "res_d_4_suprarenal_glands", "res_d_5_ureter", "res_d_6_bladder",
            "res_d_7_colon_rectum", "res_d_8_bowel", "res_d_9_uterus_ovaries",
            "res_d_10_spleen", "res_d_11_liver", "res_d_12_pancreas",
            "res_d_13_gall_bladder", "res_d_14_aorta_cava", "res_d_15_other_abdominal_resection",
            "res_e_1_debridement", "res_e_2_inlay_change",
            "res_e_3_partial_removal_of_prosthesis", "res_e_4_complete_removal_of_prosthesis",
            "res_e_5_infection", "res_e_7_wound_healing_failure", "res_e_8_infection",
            "res_e_9_osteosynthesis_failure", "res_e_10_fracture", "res_e_11_other",
            "res_e_12_pseudoarthrosis",
        }

        if lower in valid_codes:
            return lower
        if compact in valid_codes:
            return compact
        label_match = RESECTION_LABEL_TO_CODE.get(_canon_label(raw))
        if label_match is not None:
            return label_match

        # Old SurgeryEvent enum / common synonym mappings
        if any(t in lower for t in ["intralesional", "curettage", "kürettage", "intralesionell"]):
            return "res_b_1_simple_curettage"
        if any(t in lower for t in ["wide excision", "weite resektion", "en_bloc", "en bloc", "en-bloc"]):
            return "res_a_1_simple"
        if any(t in lower for t in ["marginal excision", "marginale resektion"]):
            return "res_a_1_simple"
        if any(t in lower for t in ["compartmental", "kompartiment"]):
            return "res_b_5_complete_whole_bone_res_extraarticular_joint_resection"
        if any(t in lower for t in ["limb sparing", "limb-sparing", "extremitätenerhaltend"]):
            return "res_b_3_complete_whole_bone_res_joint_sparing"
        if any(t in lower for t in ["rotationplasty", "rotationsplastik"]):
            return "res_b_10_rotationplasty_lower_extremity"
        if any(t in lower for t in ["not applicable", "nicht zutreffend", "keine resektion"]):
            return "not_applicable"

        return raw

    @staticmethod
    def _normalize_reconstruction(value) -> Optional[str]:
        """
        Normalisiert Rekonstruktionstyp.
        Constraint-Werte laut db/constraints/surgery/reconstruction.yml.
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z0-9_]", "", compact)

        valid_codes = {
            "not_applicable", "skin_mesh_graft",
            "rectus_abdominis", "rectus_abdominis_with_skin",
            "gastrocnemius", "gastrocnemius_with_skin",
            "latissimus_dorsi", "latissimus_dorsi_with_skin",
            "gracilis", "gracilis_with_skin",
            "sartorius", "sartorius_with_skin",
            "soleus", "soleus_with_skin",
            "serratus", "serratus_with_skin",
            "other_muscle_flap",
            "alt_pedicled", "other_perforator_flap_pedicled",
            "latissimus_dorsi_free", "gracilis_free",
            "other_free_tissue_transfer",
            "alt_free", "other_perforator_flap_free",
            "autologous_tendon_transfer", "allograft_tendon_reconstruction", "local_tendon_reconstruction",
            "cementation", "orif", "pedicle_screws_rods_cages", "artificial_bone_substitute",
            "autograft", "vascularised_fibula_autograft", "vascularised_epiphyseal_transfer",
            "non_vascularised_fibula_autograft", "pasteurised_autograft",
            "allograft_chips", "bulk_allograft",
            "conventional_prosthesis", "modular_tumor_prosthesis", "custom_made_prosthesis",
            "growing_prosthesis", "arthrodesis", "distraction_osteogenesis",
            "cement_spacer_pseudoarthrosis", "canadell_distraction_epiphyseolysis",
            "other_bone_reconstruction", "pseudarthrosis_intentional", "goretex_mesh_trevira",
            "artery_complete", "artery_patch", "vein_complete", "vein_patch",
            "lympho_venous", "other_vessel_reconstruction",
            "nerve_reconstruction", "neurotisation_local_transfer",
            "neurotisation_local_transfer_autologous", "neurotisation_local_transfer_allograft",
            "chest_wall_reconstruction",
            "abdominal_wall_reconstruction",
            "colon_anastomosis", "stoma", "bladder", "ureter", "other_intraabdominal_reconstruction",
            "cement_spacer_implantation", "partial_implantation_replacement",
            "complete_prosthesis_implantation_replacement",
        }

        if lower in valid_codes:
            return lower
        if compact in valid_codes:
            return compact
        label_match = RECONSTRUCTION_LABEL_TO_CODE.get(_canon_label(raw))
        if label_match is not None:
            return label_match

        # Old ReconstructionType enum / synonym mappings
        if any(t in lower for t in ["not applicable", "none", "kein", "keine", "nicht"]):
            return "not_applicable"
        if any(t in lower for t in ["primary closure", "primärverschluss", "direktverschluss"]):
            return "not_applicable"
        if any(t in lower for t in ["skin graft", "split skin", "hauttransplantat", "split thickness", "mesh graft"]):
            return "skin_mesh_graft"
        if any(t in lower for t in ["goretex", "trevira"]):
            return "goretex_mesh_trevira"
        if any(t in lower for t in ["modular tumor", "tumorprothese", "tumor prosthesis", "modular prosthesis"]):
            return "modular_tumor_prosthesis"
        if any(t in lower for t in ["custom made", "maßanfertigung", "individual prosthesis", "custom_made"]):
            return "custom_made_prosthesis"
        if any(t in lower for t in ["conventional prosthesis", "standard prosthesis", "conventional_prosthesis"]):
            return "conventional_prosthesis"
        if any(t in lower for t in ["endoprosthesis", "endoprothese"]):
            return "modular_tumor_prosthesis"
        if any(t in lower for t in ["growing prosthesis", "wachstumsprothese"]):
            return "growing_prosthesis"
        if any(t in lower for t in ["bone graft", "knochentransplantat"]) and "allo" not in lower:
            return "autograft"
        if any(t in lower for t in ["allograft"]):
            return "allograft_chips"
        if any(t in lower for t in ["free flap", "freier lappen", "free tissue"]):
            return "other_free_tissue_transfer"
        if any(t in lower for t in ["local flap", "lokaler lappen", "pedicled", "gestielt"]):
            return "other_perforator_flap_pedicled"
        if any(t in lower for t in ["prosthesis", "prothese"]):
            return "modular_tumor_prosthesis"

        return raw

    @staticmethod
    def _normalize_amputation(value) -> Optional[str]:
        """
        Normalisiert Amputationstyp.
        Constraint-Werte laut db/constraints/surgery/amputation.yml:
        not_determined, resh_010..resh_199, resg_080, ext_ta..ext_visc
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z0-9_]", "", compact)

        valid_codes = {
            "not_determined",
            "resh_010", "resh_020", "resh_030", "resh_040", "resh_050", "resh_060",
            "resh_070", "resh_099", "resh_080", "resh_081",
            "resh_110", "resh_120", "resh_130", "resh_140", "resh_150", "resh_160",
            "resh_170", "resh_180", "resh_199", "resg_080",
            "ext_ta", "ext_ti", "ext_ths", "ext_ths_diss", "ext_hc", "ext_bi", "ext_visc",
        }

        if lower in valid_codes:
            return lower
        if compact in valid_codes:
            return compact
        label_match = AMPUTATION_LABEL_TO_CODE.get(_canon_label(raw))
        if label_match is not None:
            return label_match

        # Old enum / synonym mappings (laut Locale: croms.enums.en.yml surgery.amputation)
        if any(t in lower for t in ["none", "not applicable", "nicht", "kein", "keine", "no amputation", "not_determined"]):
            return "not_determined"

        # Obere Extremität
        if any(t in lower for t in ["above-elbow", "above elbow", "trans-humeral", "transhumeral", "oberarm"]):
            return "resh_060"  # Trans-humeral
        if any(t in lower for t in ["below-elbow", "below elbow", "trans-radial", "transradial", "unterarm", "forearm"]):
            return "resh_040"  # Trans-radial (forearm)
        if any(t in lower for t in ["shoulder disarticulation", "schulterexartikulation", "shoulder_disarticulation"]):
            return "resh_070"  # Shoulder disarticulation
        if any(t in lower for t in ["wrist disarticulation", "handgelenksexartikulation"]):
            return "resh_030"  # Wrist disarticulation
        if any(t in lower for t in ["forequarter", "interscapulothorakal"]):
            return "resh_080"  # Fore-quarter without chest wall

        # Untere Extremität
        if any(t in lower for t in ["above-knee", "above knee", "trans-femoral", "transfemoral", "oberschenkelamputation", "oberschenkel"]):
            return "resh_170"  # Trans-femoral (above-knee)
        if any(t in lower for t in ["below-knee", "below knee", "transtibial", "trans-tibial", "unterschenkelamputation", "unterschenkel"]):
            return "resh_150"  # Transtibial (below-knee, BKA)
        if any(t in lower for t in ["knee disarticulation", "knieexartikulation"]):
            return "resh_160"  # Knee disarticulation
        if any(t in lower for t in ["hip disarticulation", "hüftexartikulation", "hip_disarticulation"]):
            return "resh_180"  # Hip disarticulation
        if any(t in lower for t in ["ankle disarticulation", "sprunggelenksexartikulation", "syme", "boyd"]):
            return "resh_140"  # Ankle disarticulation (Syme / Boyd)

        # Externe Hemipelvektomie (generisch) → resg_080
        if any(t in lower for t in ["hemipelvectomy", "hemipelvektomie", "hind-quarter", "hindquarter"]):
            return "resg_080"  # External hemipelvectomy (hind-quarter)

        # Spezifische resh_* / ext_* Codes: DB-intern – raw erhalten bei unbekannten Werten
        return raw

    @staticmethod
    def _normalize_hemipelvectomy_item(value) -> Optional[str]:
        """
        Normalisiert einzelne Hemipelvektomie-Codes.
        Constraint-Werte laut db/constraints/surgery/hemipelvectomy.yml:
        not_applicable, e_i_*, e_ix_*, e_ii*, e_iii*, e_iv_*, ...
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z0-9_]", "", compact)

        if lower == "not_applicable" or compact == "not_applicable":
            return "not_applicable"
        if any(t in lower for t in ["not applicable", "nicht zutreffend", "none", "kein"]):
            return "not_applicable"
        if lower in HEMIPELVECTOMY_LABELS:
            return lower
        if compact in HEMIPELVECTOMY_LABELS:
            return compact
        label_match = HEMIPELVECTOMY_LABEL_TO_CODE.get(_canon_label(raw))
        if label_match is not None:
            return label_match

        return raw

    @staticmethod
    def _normalize_participated_discipline_item(value) -> Optional[str]:
        """
        Normalisiert einzelne Disziplinen.
        Constraint-Werte laut db/constraints/surgery/participated_disciplines.yml:
        reconstructive_surgery, chest_surgery, vascular_surgery, visceral_surgery,
        orthopedics, sarcoma_surgery, trauma_surgery, hand_surgery, neurosurgery,
        spine_surgery, interventional_radiology, urology, other
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z_]", "", compact)

        allowed = {
            "reconstructive_surgery", "chest_surgery", "vascular_surgery", "visceral_surgery",
            "orthopedics", "sarcoma_surgery", "trauma_surgery", "hand_surgery", "neurosurgery",
            "spine_surgery", "interventional_radiology", "urology", "other",
        }
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        if any(t in lower for t in ["reconstructive", "plastic", "plastisch"]):
            return "reconstructive_surgery"
        if any(t in lower for t in ["chest", "thorac"]):
            return "chest_surgery"
        if any(t in lower for t in ["vascular", "gefäß"]):
            return "vascular_surgery"
        if any(t in lower for t in ["visceral", "general surgery", "allgemeinchirurgie", "allgemein", "abdominal", "gynecol", "gynäkol"]):
            return "visceral_surgery"
        if any(t in lower for t in ["orthopedic", "orthopäd"]):
            return "orthopedics"
        if any(t in lower for t in ["sarcoma surgery", "sarkomc", "sarkom"]):
            return "sarcoma_surgery"
        if any(t in lower for t in ["trauma", "unfallchirurgie"]):
            return "trauma_surgery"
        if any(t in lower for t in ["hand"]):
            return "hand_surgery"
        if any(t in lower for t in ["spine", "wirbel", "spinal"]):
            return "spine_surgery"
        if any(t in lower for t in ["neuro"]):
            return "neurosurgery"
        if any(t in lower for t in ["interventional radiology", "interventionelle radiologie"]):
            return "interventional_radiology"
        if any(t in lower for t in ["urolog"]):
            return "urology"
        if any(t in lower for t in ["other", "andere", "sonst"]):
            return "other"

        return raw

    # ─── Model Validator ───────────────────────────────────────────────────────

    @model_validator(mode="before")
    @classmethod
    def normalize_surgery_fields(cls, data):
        if not isinstance(data, dict):
            return data

        # Einzelwert-Felder mit Constraint
        for field, normalizer in [
            ("indication", cls._normalize_indication),
            ("surgery_side", cls._normalize_surgery_side),
            ("resected_tumor_margin", cls._normalize_resected_tumor_margin),
            ("reconstruction", cls._normalize_reconstruction),
            ("amputation", cls._normalize_amputation),
        ]:
            raw = data.get(field)
            normalized = normalizer(raw)
            if normalized is not None:
                data[field] = normalized
            elif raw is None or (isinstance(raw, str) and not raw.strip()):
                data[field] = None
            else:
                data[field] = raw  # nicht mappbar aber Wert vorhanden → raw_text erhalten

        # Listen-Felder – jedes Element einzeln normalisieren
        for field, item_normalizer in [
            ("resection", cls._normalize_resection_item),
            ("hemipelvectomy", cls._normalize_hemipelvectomy_item),
            ("participated_disciplines", cls._normalize_participated_discipline_item),
        ]:
            raw_list = data.get(field)
            if isinstance(raw_list, list):
                normalized_list = []
                for item in raw_list:
                    normalized = item_normalizer(item)
                    if normalized is not None:
                        normalized_list.append(normalized)
                    elif item is not None and not (isinstance(item, str) and not item.strip()):
                        normalized_list.append(item)  # raw erhalten
                data[field] = normalized_list
            elif raw_list is None:
                data[field] = []

        return data

    # ─── Field Validators ──────────────────────────────────────────────────────

    @field_validator("surgery_date", mode="before")
    @classmethod
    def parse_date(cls, v):
        """
        Parst flexible Datumsformate (DD.MM.YYYY, DD/MM/YYYY, YYYY-MM-DD)
        """
        if v is None or (isinstance(v, str) and not v.strip()):
            return None

        if isinstance(v, date):
            return v

        if isinstance(v, str):
            s = v.strip()
            s = s.split(' ')[0]  # Entfernt Textanhänge
            for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(s, fmt).date()
                except ValueError:
                    pass

        return None  # Unbekanntes Format → leer lassen statt Fehler


class SurgeryEvents(BaseModel):
    """
    Wrapper für mehrere Chirurgie-Events, extrahiert aus einem Bericht.
    """
    events: List[SurgeryEvent]
