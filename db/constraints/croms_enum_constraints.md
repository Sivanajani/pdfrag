# CROMS Enum Constraints (for RAG)

Source: `db/constraints/**/*.yml`

Interpretation used (aligned with `EnumFromFile`):
- Flat enum files: each list item is an allowed value.
- Tree enum files (`label` + `children`): only leaf values in `children` are allowed values.
- Mapping file (`adverse_event/ctcae.yml`): top-level keys are allowed `medical_area`; list entries under each key are allowed `event_type` for that area.

## Repo-Drift Check (pdfrag)

- Path prefix updated from `db/enums/croms/...` to `db/constraints/...`.
- `db/constraints/attachment/category.yml` is present in this repository.

## File Overview

| File | Type | Constraints |
| --- | --- | --- |
| `db/constraints/adverse_event/ctcae.yml` | mapping | 26 keys / 762 mapped values |
| `db/constraints/adverse_event/grade.yml` | flat enum | 5 allowed values |
| `db/constraints/anatomic_region.yml` | tree enum (leaf values) | 260 allowed values |
| `db/constraints/attachment/category.yml` | flat enum | 8 allowed values |
| `db/constraints/diagnosis/anatomic_lesion_side.yml` | flat enum | 3 allowed values |
| `db/constraints/diagnosis/death_reason.yml` | flat enum | 4 allowed values |
| `db/constraints/diagnosis/last_status.yml` | flat enum | 5 allowed values |
| `db/constraints/diagnosis/tumor_syndrome.yml` | flat enum | 21 allowed values |
| `db/constraints/drug/administration_day.yml` | flat enum | 7 allowed values |
| `db/constraints/drug/dose_unit.yml` | flat enum | 6 allowed values |
| `db/constraints/drug/drug_type.yml` | tree enum (leaf values) | 61 allowed values |
| `db/constraints/drug/frequency_unit.yml` | flat enum | 5 allowed values |
| `db/constraints/drug/route.yml` | flat enum | 5 allowed values |
| `db/constraints/ecog.yml` | flat enum | 6 allowed values |
| `db/constraints/hyperthermia_therapy/hyperthermia_type.yml` | flat enum | 2 allowed values |
| `db/constraints/hyperthermia_therapy/indication.yml` | flat enum | 5 allowed values |
| `db/constraints/hyperthermia_therapy/status.yml` | flat enum | 2 allowed values |
| `db/constraints/judgment_of_surgical_margin.yml` | flat enum | 7 allowed values |
| `db/constraints/pathology/biological_barrier_to_closest_margin.yml` | flat enum | 8 allowed values |
| `db/constraints/pathology/biopsied_lesion_type.yml` | flat enum | 6 allowed values |
| `db/constraints/pathology/biopsy_type.yml` | flat enum | 6 allowed values |
| `db/constraints/pathology/diagnostic_grading.yml` | flat enum | 9 allowed values |
| `db/constraints/pathology/eortc_response_grade.yml` | flat enum | 5 allowed values |
| `db/constraints/pathology/extent_of_necrosis.yml` | flat enum | 10 allowed values |
| `db/constraints/pathology/mitoses_per_10hpf.yml` | flat enum | 4 allowed values |
| `db/constraints/pathology/prior_treatment.yml` | flat enum | 5 allowed values |
| `db/constraints/pathology/proliferation_index.yml` | flat enum | 11 allowed values |
| `db/constraints/pathology/report_result.yml` | flat enum | 4 allowed values |
| `db/constraints/pathology/report_status.yml` | flat enum | 3 allowed values |
| `db/constraints/pathology/who_diagnosis.yml` | tree enum (leaf values) | 218 allowed values |
| `db/constraints/patient/gender.yml` | flat enum | 3 allowed values |
| `db/constraints/patient/insurance_class.yml` | flat enum | 5 allowed values |
| `db/constraints/patient/insurance_name.yml` | flat enum | 32 allowed values |
| `db/constraints/radio_therapy/hyperthermia_status.yml` | flat enum | 2 allowed values |
| `db/constraints/radio_therapy/indications.yml` | flat enum | 5 allowed values |
| `db/constraints/radio_therapy/therapy_types.yml` | flat enum | 11 allowed values |
| `db/constraints/radiology_exam/anatomic_location_of_metastasis.yml` | flat enum | 8 allowed values |
| `db/constraints/radiology_exam/choi_response.yml` | flat enum | 5 allowed values |
| `db/constraints/radiology_exam/exam_type.yml` | flat enum | 8 allowed values |
| `db/constraints/radiology_exam/imaging_timing.yml` | flat enum | 6 allowed values |
| `db/constraints/radiology_exam/imaging_type.yml` | flat enum | 2 allowed values |
| `db/constraints/radiology_exam/irecist_response.yml` | flat enum | 6 allowed values |
| `db/constraints/radiology_exam/local_disease_pet_metabolic_response.yml` | flat enum | 4 allowed values |
| `db/constraints/radiology_exam/local_disease_qualitative_mri_response.yml` | flat enum | 3 allowed values |
| `db/constraints/radiology_exam/local_disease_status.yml` | flat enum | 5 allowed values |
| `db/constraints/radiology_exam/location_of_lesion.yml` | flat enum | 3 allowed values |
| `db/constraints/radiology_exam/metastasis.yml` | flat enum | 3 allowed values |
| `db/constraints/radiology_exam/metastasis_indeterminate_category.yml` | flat enum | 4 allowed values |
| `db/constraints/radiology_exam/metastasis_location_count.yml` | flat enum | 3 allowed values |
| `db/constraints/radiology_exam/pet_response.yml` | flat enum | 5 allowed values |
| `db/constraints/radiology_exam/recist_response.yml` | flat enum | 5 allowed values |
| `db/constraints/sarcoma_board/decision_surgery.yml` | flat enum | 4 allowed values |
| `db/constraints/sarcoma_board/follow_up_reason.yml` | flat enum | 7 allowed values |
| `db/constraints/sarcoma_board/last_execution.yml` | flat enum | 8 allowed values |
| `db/constraints/sarcoma_board/reason_for_presentation.yml` | flat enum | 3 allowed values |
| `db/constraints/sarcoma_board/status_after_follow_up.yml` | flat enum | 3 allowed values |
| `db/constraints/sarcoma_board/status_before_follow_up.yml` | flat enum | 3 allowed values |
| `db/constraints/sarcoma_board/treatment_before_follow_up.yml` | flat enum | 8 allowed values |
| `db/constraints/surgery/amputation.yml` | tree enum (leaf values) | 28 allowed values |
| `db/constraints/surgery/hemipelvectomy.yml` | tree enum (leaf values) | 80 allowed values |
| `db/constraints/surgery/indication.yml` | flat enum | 10 allowed values |
| `db/constraints/surgery/participated_disciplines.yml` | flat enum | 13 allowed values |
| `db/constraints/surgery/reconstruction.yml` | tree enum (leaf values) | 69 allowed values |
| `db/constraints/surgery/resection.yml` | tree enum (leaf values) | 67 allowed values |
| `db/constraints/surgery/surgery_side.yml` | flat enum | 3 allowed values |
| `db/constraints/systemic_therapy/bone_protocol.yml` | flat enum | 7 allowed values |
| `db/constraints/systemic_therapy/clinical_trial_inclusion.yml` | flat enum | 3 allowed values |
| `db/constraints/systemic_therapy/cycles_executed.yml` | flat enum | 10 allowed values |
| `db/constraints/systemic_therapy/discontinuation_reason.yml` | flat enum | 14 allowed values |
| `db/constraints/systemic_therapy/hyperthermia_status.yml` | flat enum | 2 allowed values |
| `db/constraints/systemic_therapy/patient_type.yml` | flat enum | 2 allowed values |
| `db/constraints/systemic_therapy/reason.yml` | flat enum | 10 allowed values |
| `db/constraints/systemic_therapy/softtissue_protocol.yml` | flat enum | 4 allowed values |
| `db/constraints/user/function.yml` | flat enum | 8 allowed values |
| `db/constraints/yes_no.yml` | flat enum | 2 allowed values |
| `db/constraints/yes_no_undecided.yml` | flat enum | 3 allowed values |

## Detailed Constraints

### db/constraints/adverse_event/ctcae.yml
Type: mapping (`key -> allowed values`)

Allowed keys:
- blood_and_lymphatic_system_disorders
- cardiac_disorders
- congenital_familial_and_genetic_disorders
- ear_and_labyrinth_disorders
- endocrine_disorders
- eye_disorders
- gastrointestinal_disorders
- general_disorders_and_administration_site_conditions
- hepatobiliary_disorders
- immune_system_disorders
- infections_and_infestations
- injury_poisoning_and_procedural_complications
- investigations
- metabolism_and_nutrition_disorders
- musculoskeletal_and_connective_tissue_disorders
- neoplasms_benign_malignant_and_unspecified_incl_cysts_and_polyps
- nervous_system_disorders
- pregnancy_puerperium_and_perinatal_conditions
- psychiatric_disorders
- renal_and_urinary_disorders
- reproductive_system_and_breast_disorders
- respiratory_thoracic_and_mediastinal_disorders
- skin_and_subcutaneous_tissue_disorders
- social_circumstances
- surgical_and_medical_procedures
- vascular_disorders

Allowed mapped values per key:
- blood_and_lymphatic_system_disorders: anemia, bone_marrow_hypocellular, disseminated_intravascular_coagulation, eosinophilia, febrile_neutropenia, hemolysis, hemolytic_uremic_syndrome, leukocytosis, lymph_node_pain, methemoglobinemia, thrombotic_thrombocytopenic_purpura, blood_and_lymphatic_system_disorders_other_specify
- cardiac_disorders: aortic_valve_disease, asystole, atrial_fibrillation, atrial_flutter, atrioventricular_block_complete, atrioventricular_block_first_degree, cardiac_arrest, chest_pain_cardiac, conduction_disorder, cyanosis, heart_failure, left_ventricular_systolic_dysfunction, mitral_valve_disease, mobitz_type_ii_atrioventricular_block, mobitz_type_i, myocardial_infarction, myocarditis, palpitations, paroxysmal_atrial_tachycardia, pericardial_effusion, pericardial_tamponade, pericarditis, pulmonary_valve_disease, restrictive_cardiomyopathy, right_ventricular_dysfunction, sick_sinus_syndrome, sinus_bradycardia, sinus_tachycardia, supraventricular_tachycardia, tricuspid_valve_disease, ventricular_arrhythmia, ventricular_fibrillation, ventricular_tachycardia, cardiac_disorders_other_specify
- congenital_familial_and_genetic_disorders: congenital_familial_and_genetic_disorders_other_specify
- ear_and_labyrinth_disorders: ear_pain, external_ear_pain, hearing_impaired, middle_ear_inflammation, tinnitus, vertigo, vestibular_disorder, ear_and_labyrinth_disorders_other_specify
- endocrine_disorders: adrenal_insufficiency, cushingoid, delayed_puberty, growth_accelerated, hyperparathyroidism, hyperthyroidism, hypoparathyroidism, hypophysitis, hypopituitarism, hypothyroidism, precocious_puberty, testosterone_deficiency, virilization, endocrine_disorders_other_specify
- eye_disorders: blurred_vision, cataract, corneal_ulcer, dry_eye, extraocular_muscle_paresis, eye_pain, eyelid_function_disorder, flashing_lights, floaters, glaucoma, keratitis, night_blindness, optic_nerve_disorder, papilledema, periorbital_edema, photophobia, retinal_detachment, retinal_tear, retinal_vascular_disorder, retinopathy, scleral_disorder, uveitis, vision_decreased, vitreous_hemorrhage, watering_eyes, eye_disorders_other_specify
- gastrointestinal_disorders: abdominal_distension, abdominal_pain, anal_fissure, anal_fistula, anal_hemorrhage, anal_mucositis, anal_necrosis, anal_pain, anal_stenosis, anal_ulcer, ascites, belching, bloating, cecal_hemorrhage, cheilitis, chylous_ascites, colitis, colonic_fistula, colonic_hemorrhage, colonic_obstruction, colonic_perforation, colonic_stenosis, colonic_ulcer, constipation, dental_caries, diarrhea, dry_mouth, duodenal_fistula, duodenal_hemorrhage, duodenal_obstruction, duodenal_perforation, duodenal_stenosis, duodenal_ulcer, dyspepsia, dysphagia, enterocolitis, enterovesical_fistula, esophageal_fistula, esophageal_hemorrhage, esophageal_necrosis, esophageal_obstruction, esophageal_pain, esophageal_perforation, esophageal_stenosis, esophageal_ulcer, esophageal_varices_hemorrhage, esophagitis
- general_disorders_and_administration_site_conditions: chills, death_neonatal, death_nos, disease_progression, edema_face, edema_limbs, edema_trunk, facial_pain, fatigue, fever, flu_like_symptoms, gait_disturbance, generalized_edema, hypothermia, infusion_site_extravasation, injection_site_reaction, localized_edema, malaise, multi_organ_failure, neck_edema, non_cardiac_chest_pain, pain, sudden_death_nos, vaccination_site_lymphadenopathy, general_disorders_and_administration_site_conditions_other_specify
- hepatobiliary_disorders: bile_duct_stenosis, biliary_fistula, budd_chiari_syndrome, cholecystitis, gallbladder_fistula, gallbladder_necrosis, gallbladder_obstruction, gallbladder_pain, gallbladder_perforation, hepatic_failure, hepatic_hemorrhage, hepatic_necrosis, hepatic_pain, perforation_bile_duct, portal_hypertension, portal_vein_thrombosis, sinusoidal_obstruction_syndrome, hepatobiliary_disorders_other_specify
- immune_system_disorders: allergic_reaction, anaphylaxis, autoimmune_disorder, cytokine_release_syndrome, serum_sickness, immune_system_disorders_other_specify
- infections_and_infestations: abdominal_infection, anorectal_infection, appendicitis, appendicitis_perforated, arteritis_infective, bacteremia, biliary_tract_infection, bladder_infection, bone_infection, breast_infection, bronchial_infection, catheter_related_infection, cecal_infection, cervicitis_infection, conjunctivitis, conjunctivitis_infective, corneal_infection, cranial_nerve_infection, cytomegalovirus_infection_reactivation, device_related_infection, duodenal_infection, encephalitis_infection, encephalomyelitis_infection, endocarditis_infective, endophthalmitis, enterocolitis_infectious, epstein_barr_virus_infection_reactivation, esophageal_infection, eye_infection, folliculitis, fungemia, gallbladder_infection, gum_infection, hepatic_infection, hepatitis_b_reactivation, hepatitis_viral, herpes_simplex_reactivation, infective_myositis, joint_infection, kidney_infection, laryngitis, lip_infection, lung_infection, lymph_gland_infection, mediastinal_infection, meningitis, mucosal_infection, myelitis, nail_infection, otitis_externa, otitis_media, ovarian_infection, pancreas_infection, papulopustular_rash, paronychia, pelvic_infection, penile_infection, periorbital_infection, peripheral_nerve_infection, peritoneal_infection, pharyngitis, phlebitis_infective, pleural_infection, prostate_infection, rash_pustular, rhinitis_infective, salivary_gland_infection, scrotal_infection, sepsis, shingles, sinusitis, skin_infection, small_intestine_infection, soft_tissue_infection, splenic_infection, stoma_site_infection, thrush, tooth_infection, tracheitis, upper_respiratory_infection, urethral_infection, urinary_tract_infection, uterine_infection, vaginal_infection, viremia, vulval_infection, wound_infection, infections_and_infestations_other_specify
- injury_poisoning_and_procedural_complications: ankle_fracture, aortic_injury, arterial_injury, biliary_anastomotic_leak, bladder_anastomotic_leak, bruising, burn, dermatitis_radiation, esophageal_anastomotic_leak, fall, fallopian_tube_anastomotic_leak, fallopian_tube_perforation, fracture, gastric_anastomotic_leak, gastrointestinal_anastomotic_leak, gastrointestinal_stoma_necrosis, hip_fracture, infusion_related_reaction, injury_to_carotid_artery, injury_to_inferior_vena_cava, injury_to_jugular_vein, injury_to_superior_vena_cava, intestinal_stoma_leak, intestinal_stoma_obstruction, intestinal_stoma_site_bleeding, intraoperative_arterial_injury, intraoperative_breast_injury, intraoperative_cardiac_injury, intraoperative_ear_injury, intraoperative_endocrine_injury, intraoperative_gastrointestinal_injury, intraoperative_head_and_neck_injury, intraoperative_hemorrhage, intraoperative_hepatobiliary_injury, intraoperative_musculoskeletal_injury, intraoperative_neurological_injury, intraoperative_ocular_injury, intraoperative_renal_injury, intraoperative_reproductive_tract_injury, intraoperative_respiratory_injury, intraoperative_splenic_injury, intraoperative_urinary_injury, intraoperative_venous_injury, kidney_anastomotic_leak, large_intestinal_anastomotic_leak, pancreatic_anastomotic_leak, pharyngeal_anastomotic_leak, postoperative_hemorrhage, postoperative_thoracic_procedure_complication, prolapse_of_intestinal_stoma, prolapse_of_urostomy, radiation_recall_reaction_dermatologic, rectal_anastomotic_leak, seroma, small_intestinal_anastomotic_leak, spermatic_cord_anastomotic_leak, spinal_fracture, stenosis_of_gastrointestinal_stoma, stomal_ulcer, tracheal_hemorrhage, tracheal_obstruction, tracheostomy_site_bleeding, ureteric_anastomotic_leak, urethral_anastomotic_leak, urostomy_leak, urostomy_obstruction, urostomy_site_bleeding, urostomy_stenosis, uterine_anastomotic_leak, uterine_perforation, vaccination_complication, vaginal_anastomotic_leak, vas_deferens_anastomotic_leak, vascular_access_complication, venous_injury, wound_complication, wound_dehiscence, wrist_fracture, injury_poisoning_and_procedural_complications_other_specify
- investigations: activated_partial_thromboplastin_time_prolonged, alanine_aminotransferase_increased, alkaline_phosphatase_increased, aspartate_aminotransferase_increased, blood_antidiuretic_hormone_abnormal, blood_bicarbonate_decreased, blood_bilirubin_increased, blood_corticotrophin_decreased, blood_gonadotrophin_abnormal, blood_lactate_dehydrogenase_increased, blood_prolactin_abnormal, carbon_monoxide_diffusing_capacity_decreased, cardiac_troponin_i_increased, cardiac_troponin_t_increased, cd4_lymphocytes_decreased, cholesterol_high, cpk_increased, creatinine_increased, ejection_fraction_decreased, electrocardiogram_qt_corrected_interval_prolonged, electrocardiogram_t_wave_abnormal, fibrinogen_decreased, forced_expiratory_volume_decreased, ggt_increased, growth_hormone_abnormal, haptoglobin_decreased, hemoglobin_increased, inr_increased, lipase_increased, lymphocyte_count_decreased, lymphocyte_count_increased, neutrophil_count_decreased, pancreatic_enzymes_decreased, platelet_count_decreased, serum_amylase_increased, thyroid_stimulating_hormone_increased, urine_output_decreased, vital_capacity_abnormal, weight_gain, weight_loss, white_blood_cell_decreased, investigations_other_specify
- metabolism_and_nutrition_disorders: acidosis, alcohol_intolerance, alkalosis, anorexia, dehydration, glucose_intolerance, hypercalcemia, hyperglycemia, hyperkalemia, hyperlipidemia, hypermagnesemia, hypernatremia, hyperphosphatemia, hypertriglyceridemia, hyperuricemia, hypoalbuminemia, hypocalcemia, hypoglycemia, hypokalemia, hypomagnesemia, hyponatremia, hypophosphatemia, iron_overload, obesity, tumor_lysis_syndrome, metabolism_and_nutrition_disorders_other_specify
- musculoskeletal_and_connective_tissue_disorders: abdominal_soft_tissue_necrosis, arthralgia, arthritis, avascular_necrosis, back_pain, bone_pain, buttock_pain, chest_wall_necrosis, chest_wall_pain, exostosis, fibrosis_deep_connective_tissue, flank_pain, generalized_muscle_weakness, growth_suppression, head_soft_tissue_necrosis, joint_effusion, joint_range_of_motion_decreased, joint_range_of_motion_decreased_cervical_spine, joint_range_of_motion_decreased_lumbar_spine, kyphosis, lordosis, muscle_cramp, muscle_weakness_lower_limb, muscle_weakness_trunk, muscle_weakness_upper_limb, musculoskeletal_deformity, myalgia, myositis, neck_pain, neck_soft_tissue_necrosis, osteonecrosis, osteonecrosis_of_jaw, osteoporosis, pain_in_extremity, pelvic_soft_tissue_necrosis, rhabdomyolysis, rotator_cuff_injury, scoliosis, soft_tissue_necrosis_lower_limb, soft_tissue_necrosis_upper_limb, superficial_soft_tissue_fibrosis, trismus, unequal_limb_length, musculoskeletal_and_connective_tissue_disorder_other_specify
- neoplasms_benign_malignant_and_unspecified_incl_cysts_and_polyps: leukemia_secondary_to_oncology_chemotherapy, myelodysplastic_syndrome, skin_papilloma, treatment_related_secondary_malignancy, tumor_hemorrhage, tumor_pain, neoplasms_benign_malignant_and_unspecified_incl_cysts_and_polyps_other_specify
- nervous_system_disorders: abducens_nerve_disorder, accessory_nerve_disorder, acoustic_nerve_disorder_nos, akathisia, amnesia, anosmia, aphonia, arachnoiditis, ataxia, brachial_plexopathy, central_nervous_system_necrosis, cerebrospinal_fluid_leakage, cognitive_disturbance, concentration_impairment, depressed_level_of_consciousness, dizziness, dysarthria, dysesthesia, dysgeusia, dysphasia, edema_cerebral, encephalopathy, extrapyramidal_disorder, facial_muscle_weakness, facial_nerve_disorder, glossopharyngeal_nerve_disorder, guillain_barre_syndrome, headache, hydrocephalus, hypersomnia, hypoglossal_nerve_disorder, intracranial_hemorrhage, ischemia_cerebrovascular, lethargy, leukoencephalopathy, memory_impairment, meningismus, movements_involuntary, muscle_weakness_left_sided, muscle_weakness_right_sided, myasthenia_gravis, neuralgia, nystagmus, oculomotor_nerve_disorder, olfactory_nerve_disorder, paresthesia, peripheral_motor_neuropathy, peripheral_sensory_neuropathy, phantom_pain, presyncope, pyramidal_tract_syndrome, radiculitis, recurrent_laryngeal_nerve_palsy, reversible_posterior_leukoencephalopathy_syndrome, seizure, somnolence, spasticity, spinal_cord_compression, stroke, syncope, tendon_reflex_decreased, transient_ischemic_attacks, tremor, trigeminal_nerve_disorder, trochlear_nerve_disorder, vagus_nerve_disorder, vasovagal_reaction, nervous_system_disorders_other_specify
- pregnancy_puerperium_and_perinatal_conditions: fetal_growth_retardation, pregnancy_loss, premature_delivery, pregnancy_puerperium_and_perinatal_conditions_other_specify
- psychiatric_disorders: agitation, anorgasmia, anxiety, confusion, delayed_orgasm, delirium, delusions, depression, euphoria, hallucinations, insomnia, irritability, libido_decreased, libido_increased, mania, personality_change, psychosis, restlessness, su_icidal_ideation, suicide_attempt, psychiatric_disorders_other_specify
- renal_and_urinary_disorders: acute_kidney_injury, bladder_perforation, bladder_spasm, chronic_kidney_disease, cystitis_noninfective, dysuria, glucosuria, hematuria, hemoglobinuria, nephrotic_syndrome, proteinuria, renal_calculi, renal_colic, renal_hemorrhage, urinary_fistula, urinary_frequency, urinary_incontinence, urinary_retention, urinary_tract_obstruction, urinary_tract_pain, urinary_urgency, urine_discoloration, renal_and_urinary_disorders_other_specify
- reproductive_system_and_breast_disorders: amenorrhea, azoospermia, breast_atrophy, breast_pain, dysmenorrhea, dyspareunia, ejaculation_disorder, erectile_dysfunction, fallopian_tube_obstruction, feminization_acquired, genital_edema, gynecomastia, hematosalpinx, irregular_menstruation, lactation_disorder, menorrhagia, nipple_deformity, oligospermia, ovarian_hemorrhage, ovarian_rupture, ovulation_pain, pelvic_floor_muscle_weakness, pelvic_pain, penile_pain, perineal_pain, premature_menopause, prostatic_hemorrhage, prostatic_obstruction, prostatic_pain, scrotal_pain, spermatic_cord_hemorrhage, spermatic_cord_obstruction, testicular_disorder, testicular_hemorrhage, testicular_pain, uterine_fistula, uterine_hemorrhage, uterine_obstruction, uterine_pain, vaginal_discharge, vaginal_dryness, vaginal_fistula, vaginal_hemorrhage, vaginal_inflammation, vaginal_obstruction, vaginal_pain, vaginal_perforation, vaginal_stricture, reproductive_system_and_breast_disorders_other_specify
- respiratory_thoracic_and_mediastinal_disorders: adult_respiratory_distress_syndrome, allergic_rhinitis, apnea, aspiration, atelectasis, bronchial_fistula, bronchial_obstruction, bronchial_stricture, bronchopleural_fistula, bronchopulmonary_hemorrhage, bronchospasm, chylothorax, cough, dyspnea, epistaxis, hiccups, hoarseness, hypoxia, laryngeal_edema, laryngeal_fistula, laryngeal_hemorrhage, laryngeal_inflammation, laryngeal_mucositis, laryngeal_obstruction, laryngeal_stenosis, laryngopharyngeal_dysesthesia, laryngospasm, mediastinal_hemorrhage, nasal_congestion, oropharyngeal_pain, pharyngeal_fistula, pharyngeal_hemorrhage, pharyngeal_mucositis, pharyngeal_necrosis, pharyngeal_stenosis, pharyngolaryngeal_pain, pleural_effusion, pleural_hemorrhage, pleuritic_pain, pneumonitis, pneumothorax, postnasal_drip, productive_cough, pulmonary_edema, pulmonary_fibrosis, pulmonary_fistula, pulmonary_hypertension, respiratory_failure, retinoic_acid_syndrome, rhinorrhea, sinus_disorder, sinus_pain, sleep_apnea, sneezing, sore_throat, stridor, tracheal_fistula, tracheal_mucositis, tracheal_stenosis, voice_alteration, wheezing, respiratory_thoracic_and_mediastinal_disorders_other_specify
- skin_and_subcutaneous_tissue_disorders: alopecia, body_odor, bullous_dermatitis, dry_skin, eczema, erythema_multiforme, erythroderma, fat_atrophy, hair_color_changes, hair_texture_abnormal, hirsutism, hyperhidrosis, hyperkeratosis, hypertrichosis, hypohidrosis, lipohypertrophy, nail_changes, nail_discoloration, nail_loss, nail_ridging, pain_of_skin, palmar_plantar_erythrodysesthesia_syndrome, photosensitivity, pruritus, purpura, rash_acneiform, rash_maculo_papular, scalp_pain, skin_atrophy, skin_hyperpigmentation, skin_hypopigmentation, skin_induration, skin_ulceration, stevens_johnson_syndrome, subcutaneous_emphysema, telangiectasia, toxic_epidermal_necrolysis, urticaria, skin_and_subcutaneous_tissue_disorders_other_specify
- social_circumstances: social_circumstances_other_specify
- surgical_and_medical_procedures: surgical_and_medical_procedures_other_specify
- vascular_disorders: arterial_thromboembolism, capillary_leak_syndrome, flushing, hematoma, hot_flashes, hypertension, hypotension, lymph_leakage, lymphedema, lymphocele, peripheral_ischemia, phlebitis, superficial_thrombophlebitis, superior_vena_cava_syndrome, thromboembolic_event, vasculitis, vascular_disorders_other_specify

### db/constraints/adverse_event/grade.yml
Type: flat enum

Allowed values:
- grade_1
- grade_2
- grade_3
- grade_4
- grade_5

### db/constraints/anatomic_region.yml
Type: tree enum (`children` leaves only)

Allowed values:
- not_determined
- b_fhn_fr
- b_fhn_pr
- b_fhn_oc
- b_fhn_tm
- b_fhn_sp
- b_fhn_et
- b_fhn_mx
- b_fhn_md
- b_fhn_zg
- b_fhn_ns
- b_fhn_lc
- b_fhn_pl
- b_fhn_vm
- b_fhn_orb
- b_fhn_c1
- b_fhn_c2
- b_fhn_tmj
- b_ue_cl_prox_intra
- b_ue_cl_prox_extra
- b_ue_cl_dia
- b_ue_cl_dist_intra
- b_ue_cl_dist_extra
- b_ue_ac
- b_ue_sc_sp
- b_ue_sc_gl_intra
- b_ue_sc_gl_extra
- b_ue_sc_b
- b_ue_sc_intra
- b_ue_sc_extra
- b_ue_hu_prox_intra
- b_ue_hu_prox_extra
- b_ue_hu_dia
- b_ue_hu_dist_intra
- b_ue_hu_dist_extra
- b_ue_elb_intra
- b_ue_elb_extra
- b_ue_ra_prox_intra
- b_ue_ra_prox_extra
- b_ue_ra_dia
- b_ue_ra_dist_intra
- b_ue_ra_dist_extra
- b_ue_ul_prox_intra
- b_ue_ul_prox_extra
- b_ue_ul_dia
- b_ue_ul_dist_intra
- b_ue_ul_dist_extra
- b_ue_wrj_intra
- b_ue_wir_extra
- b_ue_cp
- b_ue_mc
- b_ue_ph
- b_sp_cv
- b_sp_tv
- b_sp_lv
- b_tr_rb
- b_tr_st
- b_pv_il
- b_pv_is
- b_pv_pb
- b_pv_sc
- b_pv_cx
- b_pv_sij
- b_pv_hip_extra
- b_pv_hip_intra
- b_le_fm_prox_intra
- b_le_fm_prox_extra
- b_le_fm_dia
- b_le_fm_dist_intra
- b_le_fm_dist_extra
- b_le_pt_intra
- b_le_pt_extra
- b_le_tb_prox_intra
- b_le_tb_prox_extra
- b_le_tb_dia
- b_le_tb_dist_intra
- b_le_tb_dist_extra
- b_le_fb_prox_intra
- b_le_fb_prox_extra
- b_le_fb_dia
- b_le_fb_dist_intra
- b_le_fb_dist_extra
- b_le_anj_intra
- b_le_anj_extra
- b_le_tl
- b_le_cl
- b_le_stj
- b_le_nv
- b_le_cb
- b_le_cnm
- b_le_cni
- b_le_cnl
- b_le_mt
- b_le_ph
- b_le_mfj
- s_fhn_fc
- s_fhn_hd
- s_fhn_na
- s_fhn_np
- s_ue_cl_med
- s_ue_cl_lat
- s_ue_sc_sub
- s_ue_sc_sca
- s_ue_sc_inf
- s_ue_sc_del
- s_ue_sc_ax
- s_ue_ua_ant
- s_ue_ua_post
- s_ue_ua_med
- s_ue_ua_lat
- s_ue_elb_ant
- s_ue_elb_post
- s_ue_elb_med
- s_ue_elb_lat
- s_ue_fa_ant
- s_ue_fa_post
- s_ue_fa_med
- s_ue_fa_lat
- s_ue_hnd_dor
- s_ue_hnd_pal
- s_ue_hnd_dig
- s_tr_tho
- s_tr_tho_lat
- s_tr_tho_post
- s_tr_lum
- s_tr_sac
- s_tr_an
- s_ab_hyp
- s_ab_umb
- s_ab_lat
- s_ch_prs
- s_ch_pec
- s_pv_glu
- s_pv_pub
- s_pv_ugp
- s_pv_ing
- s_le_th_a_prox
- s_le_th_a_diaph
- s_le_th_a_dist
- s_le_th_p_prox
- s_le_th_p_diaph
- s_le_th_p_dist
- s_le_th_m_prox
- s_le_th_m_diaph
- s_le_th_m_dist
- s_le_th_l_prox
- s_le_th_l_diaph
- s_le_th_l_dist
- s_le_kn_ant
- s_le_kn_post
- s_le_kn_med
- s_le_kn_lat
- s_le_ll_ant
- s_le_ll_post
- s_le_ll_med
- s_le_ll_lat
- s_le_ft_cal
- s_le_ft_dor
- s_le_ft_pla
- s_le_ft_dig
- d_fhn_fac
- d_fhn_hed
- d_fhn_na_ant
- d_fhn_na_post
- d_ue_clv
- d_ue_bpx
- d_ue_sc_del
- d_ue_sc_sup
- d_ue_sc_dor
- d_ue_sc_inf
- d_ue_sc_axl
- d_ue_sc_axm
- d_ue_shj_intra
- d_ue_shj_extra
- d_ue_ua_ant_prox
- d_ue_ua_ant_diaph
- d_ue_ua_ant_dist
- d_ue_ua_post_prox
- d_ue_ua_post_diaph
- d_ue_ua_post_dist
- d_ue_elb_intra
- d_ue_elb_extra
- d_ue_fa_ant_prox
- d_ue_fa_ant_diaph
- d_ue_fa_ant_dist
- d_ue_fa_post_prox
- d_ue_fa_post_diaph
- d_ue_fa_post_dist
- d_ue_wrj_intra
- d_ue_wrj_extra
- d_ue_hnd_dor
- d_ue_hnd_pal
- d_ue_hnd_dig
- d_ch_stn
- d_ch_pec
- d_ch_lat
- d_ch_post
- d_ch_lun
- d_ch_ple
- d_ch_med
- d_ch_hrt
- d_tr_csp
- d_tr_tsp
- d_tr_lsp
- d_tr_sac
- d_tr_rbm
- d_ab_aw_ant
- d_ab_aw_lat
- d_ab_ip_omn
- d_ab_ip_mes
- d_ab_ip_mesc
- d_ab_ip_pelv
- d_ab_ip_oth
- d_ab_rp_per
- d_ab_rp_apr
- d_ab_rp_ppr
- d_ab_rp_para
- d_ab_rp_pel
- d_ab_rp_oth
- d_pv_glu
- d_pv_rei
- d_pv_rex
- d_pv_pss
- d_pv_ing
- d_pv_vis_ute
- d_pv_vis_vag
- d_pv_vis_ova
- d_pv_vis_pro
- d_pv_vis_bld
- d_pv_par
- d_pv_hip_intra
- d_pv_hip_extra
- d_pv_for_ant
- d_pv_for_lat
- d_le_th_a_prox
- d_le_th_a_diaph
- d_le_th_a_dist
- d_le_th_m_prox
- d_le_th_m_diaph
- d_le_th_m_dist
- d_le_th_p_prox
- d_le_th_p_diaph
- d_le_th_p_dist
- d_le_knj_intra
- d_le_knj_extra
- d_le_popl
- d_le_ll_a_prox
- d_le_ll_a_diaph
- d_le_ll_a_dist
- d_le_ll_l_prox
- d_le_ll_l_diaph
- d_le_ll_l_dist
- d_le_ll_p_prox
- d_le_ll_p_diaph
- d_le_ll_p_dist
- d_le_anj_intra
- d_le_anj_extra
- d_le_ft_dor
- d_le_ft_pla
- d_le_ft_dig

### db/constraints/attachment/category.yml
Type: flat enum

Allowed values:
- sarcome_board
- radiology_exam
- pathology
- surgery
- radio_therapy
- systemic_therapy
- laboratory
- other

### db/constraints/diagnosis/anatomic_lesion_side.yml
Type: flat enum

Allowed values:
- right
- left
- midline

### db/constraints/diagnosis/death_reason.yml
Type: flat enum

Allowed values:
- of_other_cancer
- of_treatment_complication
- of_medical_reason_independent_from_cancer
- unknown

### db/constraints/diagnosis/last_status.yml
Type: flat enum

Allowed values:
- no_evidence_of_disease
- alive_with_disease
- dead_of_disease
- dead_of_other_reason
- not_applicable

### db/constraints/diagnosis/tumor_syndrome.yml
Type: flat enum

Allowed values:
- nothing
- previous_cancer
- neurofibromatosis_type_1
- neurofibromatosis_type_2
- gardner_syndrome
- li_fraumeni_syndrome
- retinoblastoma_syndrome
- immunodepressed_due_to_hiv
- immunodepressed_due_to_other_reason
- ollier_syndrome
- maffucci_syndrome
- paget_disease
- multiple_osteochondromas
- mccune_albright_syndrome
- rothmund_thomson_syndrome
- werner_syndrome
- cherubism
- familial_gastrointestinal_stromal_tumor
- stratakis_carney_triad
- other_malignancy_in_family
- other

### db/constraints/drug/administration_day.yml
Type: flat enum

Allowed values:
- monday
- tuesday
- wednesday
- thursday
- friday
- saturday
- sunday

### db/constraints/drug/dose_unit.yml
Type: flat enum

Allowed values:
- mg_m2_per_day
- mg_kg_per_day
- auc_per_day
- absolute_dose_mg_per_day
- cumulative_dose_mg_per_day
- units_per_day

### db/constraints/drug/drug_type.yml
Type: tree enum (`children` leaves only)

Allowed values:
- actinomycin_d
- carboplatin
- cisplatin
- cyclophosphamid
- docetaxel
- doxorubicin
- liposomal_doxorubicin
- dtic_dacarbazine
- eribulin
- etoposid
- gemcitabine
- ifosfamie
- irinotecan
- methotrexate
- navelbine
- paclitaxel
- temozolomid
- trabectedin
- trofosfamid
- vincristin
- atezolizumab_pd_l1
- avelumab_pd_l1
- cemiplimab_pd_l1
- durvalumab_pd_l1
- nivolumab_pd_1
- pembrolizumab_pd_1
- alectinib_alk
- avapritinib_ayvakit
- axitinib_vegfr
- binimetinib_mek
- cabozantinib_ros1_met
- cediranib_vegfr
- ceritinib_alk_ros1
- crizotinib_met_ros1
- cobimetinib_mek
- dasatinib_src_bcr_abl
- encorafenib_braf
- erdafitinib_fgfr
- erlotinib_egfr
- imatinib_ckit_pdgfr_a_bcr_abl
- infigratinib_fgfr
- larotrectinib_ntrk
- lenvatinib_fgfr_pdgfr_a_kit_ret
- pazopanib_vegfr_pdgfr_kit
- regorafenib
- sorafenib_raf_c_kit_flt_vegfr_pdgfr
- sunitinib_pdgfr_vegfr_kit_flt3_csf_1r_ret
- tivantinib_mek
- vemurafenib_braf
- everolimus
- nab_sirolimus
- olapatib
- bevacizumab
- ramucirumab
- denosumab
- tazemetostat
- alpelisib
- nutlins
- palbociblib
- ribociclib
- abemaciclib

### db/constraints/drug/frequency_unit.yml
Type: flat enum

Allowed values:
- x_times_per_week
- x_times_per_month
- daily
- every_other_day
- other

### db/constraints/drug/route.yml
Type: flat enum

Allowed values:
- intravenous_iv
- subcutaneous_sc
- per_os_pos
- intramuscular_im
- intraosseous_io

### db/constraints/ecog.yml
Type: flat enum

Allowed values:
- 0
- 1
- 2
- 3
- 4
- 5

### db/constraints/hyperthermia_therapy/hyperthermia_type.yml
Type: flat enum

Allowed values:
- superficial
- deep

### db/constraints/hyperthermia_therapy/indication.yml
Type: flat enum

Allowed values:
- preoperative_intent_previously_irradiated
- inoperable_previously_irradiated
- compression_symptoms
- palliative_situation
- other

### db/constraints/hyperthermia_therapy/status.yml
Type: flat enum

Allowed values:
- no
- yes_chemotherapy_hyperthermia

### db/constraints/judgment_of_surgical_margin.yml
Type: flat enum

Allowed values:
- ro_wide_margin
- r1a_marginal_margin_planned_close_ultimative_positive
- r1b_marginal_margin_positive_after_tumor_bed_re_exicision
- r1c_marginal_margin_inadvertent_positive_margin
- r2_intralesional_margin
- curettage
- not_applicable_because_no_sarcoma

### db/constraints/pathology/biological_barrier_to_closest_margin.yml
Type: flat enum

Allowed values:
- none
- fascia
- adventitia
- perineurium
- periosteum
- growth_plate
- other
- non_applicable

### db/constraints/pathology/biopsied_lesion_type.yml
Type: flat enum

Allowed values:
- biopsy_of_the_primary_tumor
- biopsy_of_local_recurrence
- biopsy_of_metastases
- resection_of_the_primary_tumor
- resection_of_local_recurrence
- resection_of_metastases

### db/constraints/pathology/biopsy_type.yml
Type: flat enum

Allowed values:
- fine_needle
- core_biopsy
- open_incisional_with_suspicion_of_sarcoma
- open_incisional_without_suspicion_of_sarcoma
- excisional_with_suspicion_of_sarcoma
- excisional_without_supsicion_of_sarcoma_whoops

### db/constraints/pathology/diagnostic_grading.yml
Type: flat enum

Allowed values:
- not_a_sarcoma
- g1
- g2
- g3
- benign
- suspicious_of_malignancy
- non_diagnostic
- not_applicable
- intermediate

### db/constraints/pathology/eortc_response_grade.yml
Type: flat enum

Allowed values:
- grade_a
- grade_b
- grade_c
- grade_d
- grade_e

### db/constraints/pathology/extent_of_necrosis.yml
Type: flat enum

Allowed values:
- less_than_10_percent
- 11_to_20_percent
- 21_to_30_percent
- 31_to_40_percent
- 41_to_50_percent
- 51_to_60_percent
- 61_to_70_percent
- 71_to_80_percent
- 81_to_90_percent
- more_than_90_percent

### db/constraints/pathology/mitoses_per_10hpf.yml
Type: flat enum

Allowed values:
- less_than_10_mitoses_per_10hpf
- 10_to_19_mitoses_per_10hpf
- more_than_19_mitoses_per_10hpf
- not_applicable_in_cases_with_neoadjuvant_therapy_necrosis

### db/constraints/pathology/prior_treatment.yml
Type: flat enum

Allowed values:
- no
- radiotherapy
- chemotherapy
- radiotherapy_and_chemotherapy
- unknown

### db/constraints/pathology/proliferation_index.yml
Type: flat enum

Allowed values:
- less_than_10_percent
- 11_to_20_percent
- 21_to_30_percent
- 31_to_40_percent
- 41_to_50_percent
- 51_to_60_percent
- 61_to_70_percent
- 71_to_80_percent
- 81_to_90_percent
- more_than_90_percent
- not_applicable_because_of_therapy_before_biopsy_or_necrosis

### db/constraints/pathology/report_result.yml
Type: flat enum

Allowed values:
- positive
- negative
- not_interpretable
- in_progress

### db/constraints/pathology/report_status.yml
Type: flat enum

Allowed values:
- yes
- no
- not_yet_but_planned

### db/constraints/pathology/who_diagnosis.yml
Type: tree enum (`children` leaves only)

Allowed values:
- not_yet_established
- 0_non_neoplastic_tumor_simulator
- 1_1_1_lipoma
- 1_1_2_lipomatosis
- 1_1_3_lipomatosis_of_nerve
- 1_1_4_lipoblastoma_lipoblastomatosis
- 1_1_5_angiolipoma
- 1_1_6_myolipoma_of_soft_tissue
- 1_1_7_chondroid_lipoma
- 1_1_8_spindle_cell_lipoma_and_pleomorphic_lipoma
- 1_1_9_hibernoma
- 1_1_10_atypical_spindle_cell_pleomorphic_lipomatous_tumour
- 1_2_1_atypical_lipomatous_tumour_well_differentiated_liposarcoma
- 1_3_1_dedifferentiated_liposarcoma
- 1_3_2_myxoid_liposarcoma
- 1_3_3_pleomorphic_liposarcoma
- 1_3_4_myxoid_pleomorphic_liposarcoma
- 2_1_1_nodular_fasciitis
- 2_1_2_proliferative_fasciitis
- 2_1_3_proliferative_myositis
- 2_1_4_myositis_ossificans
- 2_1_5_fibro_osseous_pseudotumour_of_digits
- 2_1_6_ischaemic_fasciitis
- 2_1_7_elastofibroma
- 2_1_8_fibrous_hamartoma_of_infancy
- 2_1_9_fibromatosis_colli
- 2_1_10_juvenile_hyaline_fibromatosis
- 2_1_11_inclusion_body_fibromatosis
- 2_1_12_fibroma_of_tendon_sheath
- 2_1_13_desmoplastic_fibroblastoma
- 2_1_14_myofibroblastoma
- 2_1_15_calcifying_aponeurotic_fibroma
- 2_1_16_ewsr1_smad3_positive_fibroblastic_tumour
- 2_1_17_angiomyofibroblastoma
- 2_1_18_cellular_angiofibroma
- 2_1_19_angiofibroma_of_soft_tissue
- 2_1_20_nuchal_type_fibroma
- 2_1_21_acral_fibromyxoma
- 2_1_22_gardner_fibroma
- 2_2_1_palmar_plantar_fibromatosis
- 2_2_2_desmoid_fibromatosis
- 2_2_3_lipofibromatosis
- 2_2_4_giant_cell_fibroblastoma
- 2_2_5_dermatofibrosarcoma_protuberans
- 2_2_6_solitary_fibrous_tumour
- 2_2_7_inflammatory_myofibroblastic_tumour
- 2_2_8_low_grade_myofibroblastic_sarcoma
- 2_2_9_superficial_cd34_positive_fibroblastic_tumour
- 2_2_10_myxoinflammatory_fibroblastic_sarcoma
- 2_2_11_infantile_fibrosarcoma
- 2_2_12_fibrosarcomatous_dermatofibrosarcoma_protuberans
- 2_2_13_pigmented_dermatofibrosarcoma_protuberans
- 2_3_1_adult_fibrosarcoma
- 2_3_2_myxofibrosarcoma
- 2_3_3_low_grade_fibromyxoid_sarcoma
- 2_3_4_sclerosing_epithelioid_fibrosarcoma
- 3_2_1_tenosynovial_giant_cell_tumour
- 3_1_1_deep_fibrous_histiocytoma
- 3_2_2_plexiform_fibrohistiocytic_tumour
- 3_2_3_giant_cell_tumour_of_soft_tissues
- 4_1_1_synovial_haemangioma
- 4_1_2_intramuscular_angioma
- 4_1_3_arteriovenous_malformation_hemangioma
- 4_1_4_venous_hemangioma
- 4_1_5_anastomosing_hemangioma
- 4_1_6_epithelioid_hemangioma
- 4_1_7_lymphangioma_and_lymphangiomatosis
- 4_2_1_tufted_angioma_and_kaposiform_haemangioendothelioma
- 4_2_2_retiform_haemangioendothelioma
- 4_2_3_papillary_intralymphatic_angioendothelioma
- 4_2_4_composite_haemangioendothelioma
- 4_2_5_pseudomyogenic_haemangioendothelioma
- 4_2_6_kaposi_sarcoma
- 4_3_1_epithelioid_haemangioendothelioma
- 4_3_2_angiosarcoma
- 5_2_1_glomus_tumour
- 5_2_2_myopericytoma_including_myofibroma
- 5_1_1_angioleiomyoma
- 6_1_1_leiomyoma
- 6_2_1_ebv_associated_smooth_muscle_tumour
- 6_3_1_inflammatory_leiomyosarcoma
- 6_3_2_leiomyosarcoma
- 7_1_1_rhabdomyoma
- 7_3_1_embryonal_rhabdomyosarcoma
- 7_3_2_alveolar_rhabdomyosarcoma
- 7_3_3_pleomorphic_rhabdomyosarcoma
- 7_3_4_spindle_cell_sclerosing_rhabdomyosarcoma
- 7_3_5_ectomesenchymoma
- 8_3_1_gastrointestinal_stromal_tumour
- 9_1_1_soft_tissue_chondroma
- 9_3_1_extraskeletal_osteosarcoma
- 10_1_1_schwannoma
- 10_1_2_neurofibroma
- 10_1_3_perineurinoma
- 10_1_4_granular_cell_tumour
- 10_1_5_dermal_nerve_sheath_tumour
- 10_1_6_solitary_circumscribed_neuroma
- 10_1_7_ectopic_meningioma_and_meningothelial_hamartoma
- 10_1_8_benign_triton_tumour_neuromuscular_choristoma
- 10_1_9_hybrid_nerve_sheath_tumours
- 10_3_1_malignant_peripheral_nerve_sheath_tumour
- 10_3_2_malignant_melanotic_nerve_sheath_tumour
- 11_1_1_intramuscular_myxoma
- 11_1_2_juxta_articular_myxoma
- 11_1_3_deep_angiomyxoma
- 11_2_1_atypical_fibroxanthoma
- 11_2_2_angiomatoid_fibrous_histiocytoma
- 11_2_3_ossifying_fibromyxoid_tumour
- 11_2_4_myoepithelioma_myoepithelial_carcinoma_and_mixed_tumor
- 11_2_5_pleomorphic_hyalinizing_angiectatic_tumour_of_soft_parts
- 11_2_6_haemosiderotic_fibrolipomatous_tumour
- 11_2_7_phosphaturic_mesenchymal_tumour
- 11_3_1_ntrk_rearranged_spindle_cell_neoplasm
- 11_3_2_synovial_sarcoma
- 11_3_3_epithelioid_sarcoma
- 11_3_4_alveolar_soft_part_sarcoma
- 11_3_5_clear_cell_sarcoma_of_soft_tissue
- 11_3_6_extraskeletal_myxoid_chondrosarcoma
- 11_3_7_desmoplastic_small_round_cell_tumour
- 11_3_8_extra_renal_rhabdoid_tumour
- 11_3_9_pecoma
- 11_3_10_intimal_sarcoma
- 11_3_11_undifferentiated_sarcoma
- 12_3_1_ewing_sarcoma
- 12_3_2_round_cell_sarcoma_with_ewsr1_non_ets_fusions
- 12_3_3_cic_rearranged_sarcoma
- 12_3_4_sarcoma_with_bcor_genetic_alterations
- 13_1_1_subungual_exostosis
- 13_1_2_bizarre_parosteal_osteochondromatous_proliferation
- 13_1_3_periosteal_chondroma
- 13_1_4_enchondroma
- 13_1_5_osteochondroma
- 13_1_6_chondroblastoma
- 13_1_7_chondromyxoid_fibroma
- 13_1_8_osteochondromyxoma
- 13_2_1_synovial_chondromatosis
- 13_2_2_central_atypical_cartilaginous_tumour_chondrosarcoma_grade_i
- 13_2_3_secondary_peripheral_atypical_cartilaginous_tumour_chondrosarcoma_grade_i
- 13_3_1_central_chondrosarcoma_grade_ii_grade_iii
- 13_3_2_secondary_peripheral_chondrosarcoma_grad_ii_grade_iii
- 13_3_3_periosteal_chondrosarcoma
- 13_3_4_clear_cell_chondrosarcoma
- 13_3_5_mesenchymal_chondrosarcoma
- 13_3_6_dedifferentiated_chondrosarcoma
- 14_1_1_osteoma
- 14_1_2_osteoid_osteoma
- 14_2_1_osteoblastoma
- 14_3_1_low_grade_central_osteosarcoma
- 14_3_2_osteosarcoma
- 14_3_3_parosteal_osteosarcoma
- 14_3_4_periosteal_osteosarcoma
- 14_3_5_high_grade_surface_osteosarcoma
- 14_3_6_secondary_osteosarcoma
- 15_2_1_desmoplastic_fibroma_of_bone
- 15_3_1_fibrosarcoma_of_bone
- 16_1_1_haemangioma_of_bone
- 16_2_1_epithelioid_haemangioma_of_bone
- 16_3_1_epithelioid_hemangioendothelioma_of_bone
- 16_3_2_angiosarcoma_of_bone
- 17_1_1_aneurysmal_bone_cyst
- 17_2_1_giant_cell_tumour_of_bone
- 17_1_2_non_ossifying_fibroma
- 18_1_1_benign_notochordal_tumour
- 18_3_1_conventional_chordoma
- 18_3_2_dedifferentiated_chordoma
- 18_3_3_poorly_differentiated_chordoma
- 19_1_1_chondromesenchymal_hamartoma_of_chest_wall
- 19_1_2_osteofibrous_dysplasia
- 19_3_1_adamantinoma_of_long_bones
- 19_3_3_simple_bone_cyst
- 19_2_1_fibrocartilaginous_mesenchymoma
- 19_1_3_fibrous_dysplasia
- 19_1_4_lipoma_and_hibernoma_of_bone
- 19_3_4_leiomyosarcoma_of_bone
- 19_3_5_undifferentiated_pleomorphic_sarcoma_of_bone
- m_1_bone_metastases_lung
- m_2_bone_metastases_breast
- m_3_bone_metastases_prostate
- m_4_bone_metastases_kidney
- m_5_bone_metastases_thyroid
- m_6_bone_metastases_small_cell_carcinoma
- m_7_bone_metastases_squamous_cell_carcinoma
- m_8_bone_metastases_melanoma
- m_9_bone_metastases_colon_lower_gi
- m_10_bone_metastases_upper_gi
- m_11_bone_metastases_pancreas_hepatobiliary
- m_12_bone_metastases_cervix_endometrium
- m_13_bone_metastases_parotis
- m_14_bone_metastases_cup
- m_15_bone_metastases_others
- b_1_solitary_plasmocytoma_of_bone
- b_2_multiple_myeloma
- b_3_primary_non_hodgkin_lymphoma_of_bone
- b_4_leukemia
- b_5_langerhans_cell_histiocytosis
- b_6_erdheim_chester_disease
- b_7_rosai_dorfman_disease
- gs_1_enchondromatosis_ollier
- gs_2_enchondromatosis_maffucci
- gs_3_li_fraumeni_syndrome
- gs_4_mccune_albright_syndrome
- gs_5_multiple_osteochondromas
- gs_6_neurofibromatosis_type_1
- gs_7_rothmund_thomson_syndrome
- gs_8_werner_syndrome
- ot_1_fibroblastic_reticulum_cell_sarcoma
- ot_2_histiocytic_sarcoma
- ot_3_atypical_intradermal_smooth_muscle_neoplasm
- ot_4_pleomorphic_dermal_sarcoma_PDS
- ot_5_phyllodes_tumor
- ot_6_smooth_muscle_tumors_of_uncertain_malignant_potential_STUMP
- ot_7_undifferentiated_uterine_sarcoma
- ot_8_low_grade_endometrial_stromal_sarcoma
- ot_9_high_grade_endometrial_stromal_sarcoma
- ot_10_leiomyosarcoma_of_uterus
- ot_11_adenosarcoma_of_uterus
- ot_12_carcinosarcoma_of_uterus
- ot_13_CNS_neuroblastoma

### db/constraints/patient/gender.yml
Type: flat enum

Allowed values:
- male
- female
- other

### db/constraints/patient/insurance_class.yml
Type: flat enum

Allowed values:
- unknown
- general
- half_private
- private
- self_paying

### db/constraints/patient/insurance_name.yml
Type: flat enum

Allowed values:
- unknown
- helsana
- css
- assura
- concordia
- swica
- sanitas
- kpt
- oekk
- visana
- mutuel
- krankenkasse_luzerner_hinterland
- agrisano
- aquilana
- atupri
- avenir
- egk
- einsiedler
- galenos
- glarner_krankenversicherung
- krankenkasse_slkk
- krankenkasse_steffisburg
- klug
- krankenkasse_birchmeier
- philos
- sana24
- sanavals
- krankenkasse_waedenswil
- sumiswalder
- vita_surselva
- vivacare
- vivao_sympany

### db/constraints/radio_therapy/hyperthermia_status.yml
Type: flat enum

Allowed values:
- no
- yes_radiation_hyperthermia

### db/constraints/radio_therapy/indications.yml
Type: flat enum

Allowed values:
- preoperative
- postoperative
- definitive
- palliative
- curative

### db/constraints/radio_therapy/therapy_types.yml
Type: flat enum

Allowed values:
- intensity_modulated_radiotherapy_imrt
- lattice_lrt
- volumetric_arc_vmat
- conventional_3d
- stereotactic_radiotherapy
- proton_therapy
- intraoperative_linac
- intraoperative_brachytherapy
- brachytherapy
- sequential_boost
- simultaneous_integrated_boost

### db/constraints/radiology_exam/anatomic_location_of_metastasis.yml
Type: flat enum

Allowed values:
- lung
- pleura
- bone
- liver
- soft_tissue
- lymph_node
- brain
- other

### db/constraints/radiology_exam/choi_response.yml
Type: flat enum

Allowed values:
- not_applicable
- complete_response_cr
- partial_response_pr
- stable_disease_sd
- progressive_disease_pd

### db/constraints/radiology_exam/exam_type.yml
Type: flat enum

Allowed values:
- conventional_x_ray
- mri
- ct_scan
- ultrasound
- pet_ct
- pet_mri
- scintigraphy
- other

### db/constraints/radiology_exam/imaging_timing.yml
Type: flat enum

Allowed values:
- initial_imaging
- post_neoadjuvant_pre_op
- immediate_post_op_baseline_6_12_weeks
- surveillance
- at_suspicion_of_local_recurrence
- at_suspicion_of_systemic_recurrence

### db/constraints/radiology_exam/imaging_type.yml
Type: flat enum

Allowed values:
- local_imaging
- systemic_imaging

### db/constraints/radiology_exam/irecist_response.yml
Type: flat enum

Allowed values:
- not_applicable
- complete_response_icr
- partial_response_ipr
- stable_disease_isd
- unconfirmed_progressive_iupd
- confirmed_progression_icpd

### db/constraints/radiology_exam/local_disease_pet_metabolic_response.yml
Type: flat enum

Allowed values:
- cmr
- pmr
- smd
- pmd

### db/constraints/radiology_exam/local_disease_qualitative_mri_response.yml
Type: flat enum

Allowed values:
- likely_viable
- indeterminate
- likely_treatment_effect

### db/constraints/radiology_exam/local_disease_status.yml
Type: flat enum

Allowed values:
- no_evidence_of_local_disease
- residual_viable_local_tumor_suspected
- indeterminate_post_treatment_change
- local_recurrence_suspected
- local_recurrence_confirmed

### db/constraints/radiology_exam/location_of_lesion.yml
Type: flat enum

Allowed values:
- epifascial
- subfascial
- bone

### db/constraints/radiology_exam/metastasis.yml
Type: flat enum

Allowed values:
- no
- yes
- indeterminate

### db/constraints/radiology_exam/metastasis_indeterminate_category.yml
Type: flat enum

Allowed values:
- ipn_low
- ipn_indeterminate
- ipn_high
- unclear

### db/constraints/radiology_exam/metastasis_location_count.yml
Type: flat enum

Allowed values:
- one
- two_to_five
- more_than_five

### db/constraints/radiology_exam/pet_response.yml
Type: flat enum

Allowed values:
- not_applicable
- complete_metabolic_response_mcr
- partial_metabolic_response_pmr
- stable_metabolic_disease_smd
- progressive_metabolic_disease_pmd

### db/constraints/radiology_exam/recist_response.yml
Type: flat enum

Allowed values:
- not_applicable
- complete_remission_cr
- partial_remission_pr
- stable_disease_sd
- progressive_disease_pd

### db/constraints/sarcoma_board/decision_surgery.yml
Type: flat enum

Allowed values:
- yes
- yes_interventional_radiology
- no
- undecided

### db/constraints/sarcoma_board/follow_up_reason.yml
Type: flat enum

Allowed values:
- in_context_of_primary_treatment
- first_local_recurrence
- in_context_of_treatment_for_first_local_recurrence
- first_systemic_recurrence
- in_context_of_first_systemic_recurrence
- second_or_more_local_systemic_recurrences
- important_follow_up_information_of_general_interest

### db/constraints/sarcoma_board/last_execution.yml
Type: flat enum

Allowed values:
- patient_related_factors
- physician_healthcare_provider_related_factors
- logistical_administrative_factors
- no_re_presentation_at_sarcomaboard
- systemic_institutional_factors
- disease_course
- research_trial_related_factors
- no_categorization_possible

### db/constraints/sarcoma_board/reason_for_presentation.yml
Type: flat enum

Allowed values:
- first_time
- unplanned_excision
- follow_up

### db/constraints/sarcoma_board/status_after_follow_up.yml
Type: flat enum

Allowed values:
- partial_therapy_for_primary_tumor
- completed_therapy_for_primary_tumor
- other

### db/constraints/sarcoma_board/status_before_follow_up.yml
Type: flat enum

Allowed values:
- no_previous_therapy
- locally_advanced_tumor
- exophytic_growth

### db/constraints/sarcoma_board/treatment_before_follow_up.yml
Type: flat enum

Allowed values:
- none
- surgery
- radiotherapy
- systemic_therapy
- surgery_radiotherapy
- surgery_chemotherapy
- radiotherapy_chemotherapy
- surgery_chemotherapy_radiotherapy

### db/constraints/surgery/amputation.yml
Type: tree enum (`children` leaves only)

Allowed values:
- not_determined
- resh_010
- resh_020
- resh_030
- resh_040
- resh_050
- resh_060
- resh_070
- resh_099
- resh_080
- resh_081
- resh_110
- resh_120
- resh_130
- resh_140
- resh_150
- resh_160
- resh_170
- resh_180
- resh_199
- resg_080
- ext_ta
- ext_ti
- ext_ths
- ext_ths_diss
- ext_hc
- ext_bi
- ext_visc

### db/constraints/surgery/hemipelvectomy.yml
Type: tree enum (`children` leaves only)

Allowed values:
- not_applicable
- e_i_il_ls_rp
- e_i_il_ls_rd
- e_i_is_ms
- e_i_is_f
- e_i_is_mf
- e_ix_il_ls
- e_ix_is_ms
- e_ix_is_f
- e_ix_is_mf
- e_iip_a_sy
- e_iip_p_my
- e_iip_i_py
- e_iix_pi_c
- e_ii_a_rd
- e_ii_a_rp
- e_iii_p_sr
- e_iii_p_ir_rp
- e_iii_p_ir_rd
- e_iii_p_irt
- e_iii_p_sir
- e_iii_p_sirt
- e_iii_p_bsr
- e_iii_p_bsir
- e_iii_p_bsirt
- e_iii_p_birt
- e_iv_s_ls_h
- e_iv_s_ls_b
- e_iv_s_hs_u
- e_iv_s_hs_b
- e_iv_s_hs_l
- e_iv_s_hs_ld
- e_iv_s_hslp_p
- e_iv_s_hslp_c
- e_ix_ii_ls
- e_i_ii_ls
- e_iix_iii_sr
- e_iix_iii_ist
- e_iix_iii_irt
- e_iix_iii_sirt
- e_iix_iii_sirtx
- e_iix_iii_bsr
- e_iix_iii_bsir
- e_iix_iii_bsirt
- e_ii_iii_sr
- e_ii_iii_ist
- e_ii_iii_irt
- e_ii_iii_sirt
- e_ii_iii_sirtx
- e_ii_iii_bsr
- e_ii_iii_bsir
- e_ii_iii_bsirt
- e_ix_iix_iii_sr
- e_ix_iix_iii_ist
- e_ix_iix_iii_irt
- e_ix_iix_iii_sirt
- e_ix_iix_iii_sirtx
- e_ix_iix_iii_bsr
- e_ix_iix_iii_bsir
- e_ix_iix_iii_bsirt
- e_iii_iv_l_lsi_m_sa_s_nd
- e_iii_iv_l_lsi_m_sa_s_ud
- e_iii_iv_l_lsi_m_sa_s_bd
- e_iii_iv_l_lsi_m_sa_s_lv
- e_iii_iv_l_lsi_m_f_s_nd
- e_iii_iv_l_lsi_m_f_s_ud
- e_iii_iv_l_lsi_m_f_s_bd
- e_iii_iv_l_lsi_m_f_s_lv
- e_iii_iv_l_lsi_m_bm_s_nd
- e_iii_iv_l_lsi_m_bm_s_ud
- e_iii_iv_l_lsi_m_bm_s_bd
- e_iii_iv_l_lsi_m_bm_s_lv
- e_iii_iv_l_lsi_m_mc_s_nd
- e_iii_iv_l_lsi_m_mc_s_ud
- e_iii_iv_l_lsi_m_mc_s_bd
- e_iii_iv_l_lsi_m_mc_s_lv
- e_iii_iv_l_lsi_m_cf_s_nd
- e_iii_iv_l_lsi_m_cf_s_ud
- e_iii_iv_l_lsi_m_cf_s_bd
- e_iii_iv_l_lsi_m_cf_s_lv

### db/constraints/surgery/indication.yml
Type: flat enum

Allowed values:
- first_surgery_for_this_reason
- first_surgery_after_whoops
- pathological_fracture
- first_revision_surgery
- second_or_more_revision_surgery
- first_surgery_for_local_recurrence
- second_or_more_surgery_for_local_recurrence
- first_surgery_for_metastasis
- second_or_more_surgery_for_metastasis
- other_reason

### db/constraints/surgery/participated_disciplines.yml
Type: flat enum

Allowed values:
- reconstructive_surgery
- chest_surgery
- vascular_surgery
- visceral_surgery
- orthopedics
- sarcoma_surgery
- trauma_surgery
- hand_surgery
- neurosurgery
- spine_surgery
- interventional_radiology
- urology
- other

### db/constraints/surgery/reconstruction.yml
Type: tree enum (`children` leaves only)

Allowed values:
- not_applicable
- skin_mesh_graft
- rectus_abdominis
- rectus_abdominis_with_skin
- gastrocnemius
- gastrocnemius_with_skin
- latissimus_dorsi
- latissimus_dorsi_with_skin
- gracilis
- gracilis_with_skin
- sartorius
- sartorius_with_skin
- soleus
- soleus_with_skin
- serratus
- serratus_with_skin
- other_muscle_flap
- alt_pedicled
- other_perforator_flap_pedicled
- latissimus_dorsi_free
- gracilis_free
- other_free_tissue_transfer
- alt_free
- other_perforator_flap_free
- autologous_tendon_transfer
- allograft_tendon_reconstruction
- local_tendon_reconstruction
- cementation
- orif
- pedicle_screws_rods_cages
- artificial_bone_substitute
- autograft
- vascularised_fibula_autograft
- vascularised_epiphyseal_transfer
- non_vascularised_fibula_autograft
- pasteurised_autograft
- allograft_chips
- bulk_allograft
- conventional_prosthesis
- modular_tumor_prosthesis
- custom_made_prosthesis
- growing_prosthesis
- arthrodesis
- distraction_osteogenesis
- cement_spacer_pseudoarthrosis
- canadell_distraction_epiphyseolysis
- other_bone_reconstruction
- pseudarthrosis_intentional
- goretex_mesh_trevira
- artery_complete
- artery_patch
- vein_complete
- vein_patch
- lympho_venous
- other_vessel_reconstruction
- nerve_reconstruction
- neurotisation_local_transfer
- neurotisation_local_transfer_autologous
- neurotisation_local_transfer_allograft
- chest_wall_reconstruction
- abdominal_wall_reconstruction
- colon_anastomosis
- stoma
- bladder
- ureter
- other_intraabdominal_reconstruction
- cement_spacer_implantation
- partial_implantation_replacement
- complete_prosthesis_implantation_replacement

### db/constraints/surgery/resection.yml
Type: tree enum (`children` leaves only)

Allowed values:
- not_applicable
- res_a_1_simple
- res_a_2_muscle_resection
- res_a_3_vessel_dissection
- res_a_4_nerve_dissection
- res_a_5_periost_resection
- res_a_6_bone_resection
- res_a_7_vessel_resection
- res_a_8_nerve_resection
- res_a_9_mr_hifu
- res_a_10_tendon_resection
- res_a_11_ligament_resection
- res_a_12_resection_of_funiculus_scrotum_genitals
- res_a_13_other_sts_resection
- res_b_1_simple_curettage
- res_b_2_hemi_cortex_resection
- res_b_3_complete_whole_bone_res_joint_sparing
- res_b_4_complete_whole_bone_res_transarticular_resection
- res_b_5_complete_whole_bone_res_extraarticular_joint_resection
- res_b_6_with_3d_patient_specific_cutting_guides
- res_b_6_1_3d_planning
- res_b_8_radiofrequency_ablation_rfa_cryotherapy_mr_hifu
- res_b_9_resection_replantation_upper_extremity
- res_b_10_rotationplasty_lower_extremity
- res_b_80_tendon_resection
- res_b_81_ligament_resection
- res_b_82_forced_epiphyseolysis_ot_canadell_technique
- res_b_83_extra_articular_scapulo_humeral_resection_tikhoff_linberg
- res_b_84_biopsy_gain_of_diagnostic_tissue
- res_b_85_removal_of_cement
- res_b_86_other_bone_resection
- res_c_1_chest_wall_resection
- res_c_2_wedge_resection
- res_c_3_segmental_resection
- res_c_4_lobectomy
- res_c_5_bilobectomy_pneumonectomy
- res_c_6_pleuropneumonectomy
- res_c_7_thoracic_wall_resection_ribs
- res_c_10_other_chest_lung_resection
- res_c_8_wedge_resection
- res_c_9_lobectomy
- res_d_1_abdominal_wall_resection
- res_d_2_none
- res_d_3_kidney
- res_d_4_suprarenal_glands
- res_d_5_ureter
- res_d_6_bladder
- res_d_7_colon_rectum
- res_d_8_bowel
- res_d_9_uterus_ovaries
- res_d_10_spleen
- res_d_11_liver
- res_d_12_pancreas
- res_d_13_gall_bladder
- res_d_14_aorta_cava
- res_d_15_other_abdominal_resection
- res_e_5_infection
- res_e_7_wound_healing_failure
- res_e_8_infection
- res_e_9_osteosynthesis_failure
- res_e_10_fracture
- res_e_12_pseudoarthrosis
- res_e_1_debridement
- res_e_2_inlay_change
- res_e_3_partial_removal_of_prosthesis
- res_e_4_complete_removal_of_prosthesis
- res_e_11_other

### db/constraints/surgery/surgery_side.yml
Type: flat enum

Allowed values:
- right
- left
- midline

### db/constraints/systemic_therapy/bone_protocol.yml
Type: flat enum

Allowed values:
- euramos
- euroboss
- ewing2008
- euroewing_2012_vide
- euroewing_2012_vdc_ie
- cws
- other

### db/constraints/systemic_therapy/clinical_trial_inclusion.yml
Type: flat enum

Allowed values:
- no
- yes_ssn_outcome_prediction
- yes_other

### db/constraints/systemic_therapy/cycles_executed.yml
Type: flat enum

Allowed values:
- one
- two
- three
- four
- five
- six
- seven
- eight
- nine
- until_progression

### db/constraints/systemic_therapy/discontinuation_reason.yml
Type: flat enum

Allowed values:
- completed
- progressive_disease_radiologic
- progressive_disease_clinical
- toxicity
- maximum_safe_cumulative_dose
- clinical_deterioration_non_pd
- intercurrent_illness
- patient_decision
- definitive_local_therapy
- switch_to_next_line_or_maintenance
- treatment_related_mortality
- lost_to_follow_up_or_administrative
- death_tumor_related
- death_non_tumor_related

### db/constraints/systemic_therapy/hyperthermia_status.yml
Type: flat enum

Allowed values:
- no
- yes_chemotherapy_hyperthermia

### db/constraints/systemic_therapy/patient_type.yml
Type: flat enum

Allowed values:
- outpatient
- inpatient

### db/constraints/systemic_therapy/reason.yml
Type: flat enum

Allowed values:
- curative_intent_neoadjuvant
- curative_intent_adjuvant
- trial_mandated_systemic_therapy
- oligometastatic_program_partner
- conversion_downstaging
- consolidation
- additive_maintenance
- symptom_control
- palliative
- other

### db/constraints/systemic_therapy/softtissue_protocol.yml
Type: flat enum

Allowed values:
- cws
- pazoqol
- napage
- other

### db/constraints/user/function.yml
Type: flat enum

Allowed values:
- medical_doctor
- data_manager
- research_associate
- medical_oncology
- radiation_oncology
- surgery
- pathology
- radiology

### db/constraints/yes_no.yml
Type: flat enum

Allowed values:
- yes
- no

### db/constraints/yes_no_undecided.yml
Type: flat enum

Allowed values:
- yes
- no
- undecided
