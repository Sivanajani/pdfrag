# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[8.0].define(version: 2025_12_18_180444) do
  # These are extensions that must be enabled in order to support this database
  enable_extension "pg_catalog.plpgsql"
  enable_extension "unaccent"

  create_table "active_hashcash_stamps", force: :cascade do |t|
    t.string "version", null: false
    t.integer "bits", null: false
    t.date "date", null: false
    t.string "resource", null: false
    t.string "ext", null: false
    t.string "rand", null: false
    t.string "counter", null: false
    t.string "request_path"
    t.string "ip_address"
    t.jsonb "context"
    t.datetime "created_at", precision: nil, null: false
    t.datetime "updated_at", precision: nil, null: false
    t.index ["counter", "rand", "date", "resource", "bits", "version", "ext"], name: "index_active_hashcash_stamps_unique", unique: true
    t.index ["ip_address", "created_at"], name: "index_active_hashcash_stamps_on_ip_address_and_created_at", where: "(ip_address IS NOT NULL)"
  end

  create_table "active_storage_attachments", force: :cascade do |t|
    t.string "name", null: false
    t.string "record_type", null: false
    t.bigint "record_id", null: false
    t.bigint "blob_id", null: false
    t.datetime "created_at", null: false
    t.index ["blob_id"], name: "index_active_storage_attachments_on_blob_id"
    t.index ["record_type", "record_id", "name", "blob_id"], name: "index_active_storage_attachments_uniqueness", unique: true
  end

  create_table "active_storage_blobs", force: :cascade do |t|
    t.string "key", null: false
    t.string "filename", null: false
    t.string "content_type"
    t.text "metadata"
    t.string "service_name", null: false
    t.bigint "byte_size", null: false
    t.string "checksum"
    t.datetime "created_at", null: false
    t.index ["key"], name: "index_active_storage_blobs_on_key", unique: true
  end

  create_table "active_storage_variant_records", force: :cascade do |t|
    t.bigint "blob_id", null: false
    t.string "variation_digest", null: false
    t.index ["blob_id", "variation_digest"], name: "index_active_storage_variant_records_uniqueness", unique: true
  end

  create_table "croms_adverse_events", force: :cascade do |t|
    t.bigint "systemic_therapy_id", null: false
    t.string "medical_area", null: false
    t.string "event_type", null: false
    t.string "grade", null: false
    t.date "start_date"
    t.date "end_date"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.text "comment"
    t.index ["systemic_therapy_id"], name: "index_croms_adverse_events_on_systemic_therapy_id"
  end

  create_table "croms_attachments", force: :cascade do |t|
    t.string "category", null: false
    t.bigint "patient_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.text "category_comment"
    t.index ["patient_id"], name: "index_croms_attachments_on_patient_id"
  end

  create_table "croms_contracts", force: :cascade do |t|
    t.bigint "user_id", null: false
    t.bigint "institution_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["institution_id"], name: "index_croms_contracts_on_institution_id"
    t.index ["user_id", "institution_id"], name: "index_croms_contracts_on_user_id_and_institution_id", unique: true
    t.index ["user_id"], name: "index_croms_contracts_on_user_id"
  end

  create_table "croms_diagnoses", force: :cascade do |t|
    t.string "tumor_anatomic_region"
    t.string "tumor_anatomic_lesion_side"
    t.string "tumor_syndromes", default: [], array: true
    t.text "tumor_diagnosis"
    t.string "additional_tumor_anatomic_region"
    t.string "additional_tumor_anatomic_lesion_side"
    t.text "additional_tumor_diagnosis"
    t.text "other_diagnosis"
    t.text "patient_history"
    t.integer "diagnosis_ecog"
    t.date "last_contact_date"
    t.string "last_status"
    t.string "death_reason"
    t.bigint "patient_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.text "tumor_syndromes_comment"
    t.boolean "imported", default: false, null: false
    t.date "first_contact_date"
    t.index ["patient_id"], name: "index_croms_diagnoses_on_patient_id"
  end

  create_table "croms_drugs", force: :cascade do |t|
    t.bigint "systemic_therapy_id", null: false
    t.string "drug_type", null: false
    t.decimal "dose"
    t.string "dose_unit"
    t.decimal "frequency"
    t.string "frequency_unit"
    t.string "route"
    t.string "administration_day"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.text "frequency_unit_comment"
    t.index ["systemic_therapy_id"], name: "index_croms_drugs_on_systemic_therapy_id"
  end

  create_table "croms_hyperthermia_therapies", force: :cascade do |t|
    t.string "indication"
    t.date "start_date"
    t.date "end_date"
    t.string "hyperthermia_type"
    t.integer "therapy_sessions_count"
    t.string "schedule"
    t.boolean "board_accepted_indication"
    t.text "comment"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "therapy_type"
    t.bigint "therapy_id"
    t.text "indication_comment"
    t.index ["therapy_type", "therapy_id"], name: "index_croms_hyperthermia_therapies_on_therapy"
  end

  create_table "croms_institutions", force: :cascade do |t|
    t.string "name", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["name"], name: "index_croms_institutions_on_name", unique: true
  end

  create_table "croms_pathologies", force: :cascade do |t|
    t.string "biopsied_lesion_type"
    t.date "biopsy_resection_date"
    t.date "registrate_date"
    t.date "first_report_date"
    t.date "final_report_date"
    t.string "prior_treatment"
    t.string "who_diagnosis"
    t.string "diagnostic_grading"
    t.string "judgment_of_surgical_margin"
    t.string "proliferation_index"
    t.string "mitoses_per_10hpf"
    t.string "extent_of_necrosis"
    t.integer "closest_distance_to_margin_mm"
    t.string "biological_barrier_to_closest_margin"
    t.string "ihc_performed_status"
    t.string "fish_performed_status"
    t.string "rna_performed_status"
    t.string "dna_performed_status"
    t.string "ihc_result"
    t.string "fish_result"
    t.string "rna_result"
    t.string "dna_result"
    t.bigint "patient_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.bigint "responsible_pathologist_id"
    t.string "biopsy_type"
    t.text "biological_barrier_to_closest_margin_comment"
    t.bigint "institution_id"
    t.boolean "imported", default: false, null: false
    t.string "eortc_response_grade"
    t.text "report"
    t.date "report_date"
    t.index ["institution_id"], name: "index_croms_pathologies_on_institution_id"
    t.index ["patient_id"], name: "index_croms_pathologies_on_patient_id"
    t.index ["responsible_pathologist_id"], name: "index_croms_pathologies_on_responsible_pathologist_id"
  end

  create_table "croms_patient_registrations", force: :cascade do |t|
    t.string "patient_reference_code", null: false
    t.string "patient_birth_date"
    t.string "patient_first_name"
    t.string "patient_last_name"
    t.string "patient_gender"
    t.string "patient_street_name"
    t.string "patient_street_number"
    t.string "patient_city"
    t.string "patient_zip_code"
    t.string "patient_country"
    t.string "patient_phone_number"
    t.string "patient_ahv"
    t.string "patient_insurance_name"
    t.string "patient_insurance_number"
    t.string "patient_general_practitioner_name"
    t.integer "patient_institution_ids", default: [], array: true
    t.string "sarcoma_board_reason_for_presentation"
    t.text "sarcoma_board_question"
    t.text "sarcoma_board_proposed_procedure"
    t.date "sarcoma_board_presentation_date"
    t.text "diagnosis_tumor_diagnosis"
    t.text "diagnosis_other_diagnosis"
    t.string "diagnosis_tumor_anatomic_region"
    t.string "diagnosis_tumor_anatomic_lesion_side"
    t.text "diagnosis_patient_history"
    t.string "pathology_who_diagnosis"
    t.string "pathology_biopsied_lesion_type"
    t.date "pathology_biopsy_resection_date"
    t.string "pathology_biopsy_type"
    t.date "radiology_exam_exam_date"
    t.string "radiology_exam_exam_type"
    t.text "radiology_exam_exam_type_comment"
    t.string "radiology_exam_imaging_timing"
    t.string "radiology_exam_imaging_type"
    t.integer "radiology_exam_largest_lesion_size_in_mm"
    t.integer "radiology_exam_medium_lesion_size_in_mm"
    t.integer "radiology_exam_smallest_lesion_size_in_mm"
    t.boolean "radiology_exam_metastasis_presence"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.date "diagnosis_first_contact_date"
    t.string "patient_general_practitioner_email"
    t.string "patient_general_practitioner_location"
    t.boolean "patient_consent", default: false, null: false
    t.bigint "pathology_responsible_pathologist_id"
    t.bigint "pathology_institution_id"
    t.bigint "sarcoma_board_presenting_physician_id"
    t.string "radiology_exam_local_disease_status"
    t.date "radiology_exam_report_date"
    t.date "pathology_report_date"
    t.index ["sarcoma_board_presenting_physician_id"], name: "idx_on_sarcoma_board_presenting_physician_id_e52ce90c9e"
  end

  create_table "croms_patients", force: :cascade do |t|
    t.string "reference_code", null: false
    t.boolean "consent", null: false
    t.string "ahv"
    t.string "last_name", null: false
    t.string "first_name", null: false
    t.string "gender"
    t.string "street_name"
    t.string "street_number"
    t.string "zip_code"
    t.string "city"
    t.string "country"
    t.string "phone_number"
    t.string "email"
    t.string "insurance_name"
    t.string "insurance_class"
    t.string "insurance_number"
    t.string "general_practitioner_name"
    t.string "general_practitioner_email"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "birth_date"
    t.text "general_practitioner_location"
    t.boolean "imported", default: false
    t.index ["ahv"], name: "index_croms_patients_on_ahv", unique: true
    t.index ["reference_code"], name: "index_croms_patients_on_ref", unique: true
  end

  create_table "croms_radio_therapies", force: :cascade do |t|
    t.bigint "patient_id", null: false
    t.string "therapy_types", default: [], null: false, array: true
    t.date "referral_date"
    t.date "first_contact_date"
    t.date "therapy_start_date"
    t.date "therapy_end_date"
    t.float "total_dose_in_gy"
    t.integer "given_fractions"
    t.float "ptv_volume_in_cm3"
    t.float "gtv_volume_in_cm3"
    t.boolean "was_tumor_located_in_radiated_area"
    t.boolean "was_tumor_located_with_pre_existing_lymph_edema"
    t.text "comments"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "hyperthermia_status"
    t.bigint "responsible_oncologist_id"
    t.bigint "institution_id"
    t.boolean "imported", default: false, null: false
    t.string "indications", default: [], array: true
    t.index ["institution_id"], name: "index_croms_radio_therapies_on_institution_id"
    t.index ["patient_id"], name: "index_croms_radio_therapies_on_patient_id"
    t.index ["responsible_oncologist_id"], name: "index_croms_radio_therapies_on_responsible_oncologist_id"
  end

  create_table "croms_radiology_exams", force: :cascade do |t|
    t.bigint "patient_id", null: false
    t.date "exam_date", null: false
    t.string "exam_type"
    t.string "imaging_timing"
    t.string "imaging_type"
    t.integer "largest_lesion_size_in_mm"
    t.integer "medium_lesion_size_in_mm"
    t.integer "smallest_lesion_size_in_mm"
    t.string "location_of_lesion"
    t.string "recist_response"
    t.string "choi_response"
    t.string "irecist_response"
    t.string "pet_response"
    t.boolean "metastasis_presence"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.text "exam_type_comment"
    t.text "radiology_report"
    t.boolean "imported", default: false, null: false
    t.string "local_disease_status"
    t.string "local_disease_measurable"
    t.integer "local_disease_report_largest_diameter"
    t.string "local_disease_qualitative_mri_response"
    t.integer "local_disease_radiologist_confidence"
    t.string "local_disease_pet_metabolic_response"
    t.string "metastasis"
    t.string "anatomic_location_of_metastasis", default: [], array: true
    t.string "metastasis_location_lung_count"
    t.string "metastasis_location_pleura_count"
    t.string "metastasis_location_bone_count"
    t.string "metastasis_location_liver_count"
    t.string "metastasis_location_soft_tissue_count"
    t.string "metastasis_location_lymph_node_count"
    t.string "metastasis_location_brain_count"
    t.string "metastasis_location_other_count"
    t.integer "metastasis_target_lesion_count"
    t.integer "metastasis_longest_diameter_mm"
    t.string "metastasis_indeterminate_category"
    t.date "report_date"
    t.index ["patient_id"], name: "index_croms_radiology_exams_on_patient_id"
  end

  create_table "croms_sarcoma_board_participants", force: :cascade do |t|
    t.bigint "sarcoma_board_id", null: false
    t.bigint "participant_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["participant_id"], name: "index_croms_sarcoma_board_participants_on_participant_id"
    t.index ["sarcoma_board_id"], name: "index_croms_sarcoma_board_participants_on_sarcoma_board_id"
  end

  create_table "croms_sarcoma_boards", force: :cascade do |t|
    t.bigint "patient_id", null: false
    t.date "presentation_date", null: false
    t.string "reason_for_presentation"
    t.string "status_before_follow_up"
    t.date "unplanned_excision_date"
    t.string "status_after_follow_up"
    t.string "treatment_before_follow_up"
    t.string "follow_up_reason"
    t.text "question"
    t.string "last_execution"
    t.text "proposed_procedure"
    t.integer "current_ecog"
    t.string "decision_surgery"
    t.text "decision_surgery_comment"
    t.string "decision_radio_therapy"
    t.text "decision_radio_therapy_comment"
    t.string "decision_systemic_surgery"
    t.text "decision_systemic_surgery_comment"
    t.string "decision_follow_up"
    t.text "decision_follow_up_comment"
    t.string "decision_diagnostics"
    t.text "decision_diagnostics_comment"
    t.string "decision_palliative_care"
    t.text "decision_palliative_care_comment"
    t.text "summary"
    t.text "further_details"
    t.boolean "fast_track", default: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.bigint "whoops_surgery_institution_id"
    t.text "status_after_follow_up_comment"
    t.text "patient_history"
    t.text "summary_patient_information"
    t.text "summary_radiology"
    t.text "summary_pathology"
    t.boolean "imported", default: false, null: false
    t.bigint "presenting_physician_id"
    t.index ["patient_id"], name: "index_croms_sarcoma_boards_on_patient_id"
    t.index ["presenting_physician_id"], name: "index_croms_sarcoma_boards_on_presenting_physician_id"
    t.index ["whoops_surgery_institution_id"], name: "index_croms_sarcoma_boards_on_whoops_surgery_institution_id"
  end

  create_table "croms_sessions", force: :cascade do |t|
    t.bigint "user_id", null: false
    t.string "ip_address"
    t.string "user_agent"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["user_id"], name: "index_croms_sessions_on_user_id"
  end

  create_table "croms_surgeries", force: :cascade do |t|
    t.bigint "patient_id", null: false
    t.date "surgery_date", null: false
    t.string "indication"
    t.string "surgery_side"
    t.integer "greatest_surgical_tumor_dimension_in_mm"
    t.boolean "had_tumor_spillage"
    t.string "first_revision_details"
    t.string "second_revision_details"
    t.string "anatomic_region"
    t.string "resection", default: [], array: true
    t.string "reconstruction"
    t.string "amputation"
    t.string "resected_tumor_margin"
    t.string "participated_disciplines", default: [], array: true
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "hemipelvectomy", default: [], array: true
    t.bigint "responsible_surgeon_id", null: false
    t.text "participated_disciplines_comment"
    t.text "indication_comment"
    t.bigint "institution_id"
    t.boolean "imported", default: false, null: false
    t.index ["institution_id"], name: "index_croms_surgeries_on_institution_id"
    t.index ["patient_id"], name: "index_croms_surgeries_on_patient_id"
    t.index ["responsible_surgeon_id"], name: "index_croms_surgeries_on_responsible_surgeon_id"
  end

  create_table "croms_systemic_therapies", force: :cascade do |t|
    t.bigint "patient_id", null: false
    t.string "reason"
    t.integer "treatment_line"
    t.string "cycles_executed"
    t.string "bone_protocol"
    t.string "softtissue_protocol"
    t.date "cycle_start_date"
    t.date "cycle_end_date"
    t.string "discontinuation_reason"
    t.boolean "was_rct_concomittant", default: false, null: false
    t.text "comments"
    t.string "clinical_trial_inclusion"
    t.string "hyperthermia_status"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.bigint "responsible_oncologist_id"
    t.string "patient_type"
    t.text "bone_protocol_comment"
    t.text "reason_comment"
    t.text "softtissue_protocol_comment"
    t.bigint "institution_id"
    t.date "assessment_date"
    t.boolean "imported", default: false, null: false
    t.index ["institution_id"], name: "index_croms_systemic_therapies_on_institution_id"
    t.index ["patient_id"], name: "index_croms_systemic_therapies_on_patient_id"
    t.index ["responsible_oncologist_id"], name: "index_croms_systemic_therapies_on_responsible_oncologist_id"
  end

  create_table "croms_treatments", force: :cascade do |t|
    t.bigint "patient_id", null: false
    t.bigint "institution_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["institution_id"], name: "index_croms_treatments_on_institution_id"
    t.index ["patient_id", "institution_id"], name: "index_croms_treatments_on_patient_id_and_institution_id", unique: true
    t.index ["patient_id"], name: "index_croms_treatments_on_patient_id"
  end

  create_table "croms_users", force: :cascade do |t|
    t.string "first_name", null: false
    t.string "last_name", null: false
    t.string "email"
    t.boolean "admin", default: false, null: false
    t.string "function", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "password_digest", null: false
    t.index ["email"], name: "index_croms_users_on_email", unique: true
  end

  create_table "solid_cable_messages", force: :cascade do |t|
    t.binary "channel", null: false
    t.binary "payload", null: false
    t.datetime "created_at", null: false
    t.bigint "channel_hash", null: false
    t.index ["channel"], name: "index_solid_cable_messages_on_channel"
    t.index ["channel_hash"], name: "index_solid_cable_messages_on_channel_hash"
    t.index ["created_at"], name: "index_solid_cable_messages_on_created_at"
  end

  create_table "solid_cache_entries", force: :cascade do |t|
    t.binary "key", null: false
    t.binary "value", null: false
    t.datetime "created_at", null: false
    t.bigint "key_hash", null: false
    t.integer "byte_size", null: false
    t.index ["byte_size"], name: "index_solid_cache_entries_on_byte_size"
    t.index ["key_hash", "byte_size"], name: "index_solid_cache_entries_on_key_hash_and_byte_size"
    t.index ["key_hash"], name: "index_solid_cache_entries_on_key_hash", unique: true
  end

  create_table "solid_queue_blocked_executions", force: :cascade do |t|
    t.bigint "job_id", null: false
    t.string "queue_name", null: false
    t.integer "priority", default: 0, null: false
    t.string "concurrency_key", null: false
    t.datetime "expires_at", null: false
    t.datetime "created_at", null: false
    t.index ["concurrency_key", "priority", "job_id"], name: "index_solid_queue_blocked_executions_for_release"
    t.index ["expires_at", "concurrency_key"], name: "index_solid_queue_blocked_executions_for_maintenance"
    t.index ["job_id"], name: "index_solid_queue_blocked_executions_on_job_id", unique: true
  end

  create_table "solid_queue_claimed_executions", force: :cascade do |t|
    t.bigint "job_id", null: false
    t.bigint "process_id"
    t.datetime "created_at", null: false
    t.index ["job_id"], name: "index_solid_queue_claimed_executions_on_job_id", unique: true
    t.index ["process_id", "job_id"], name: "index_solid_queue_claimed_executions_on_process_id_and_job_id"
  end

  create_table "solid_queue_failed_executions", force: :cascade do |t|
    t.bigint "job_id", null: false
    t.text "error"
    t.datetime "created_at", null: false
    t.index ["job_id"], name: "index_solid_queue_failed_executions_on_job_id", unique: true
  end

  create_table "solid_queue_jobs", force: :cascade do |t|
    t.string "queue_name", null: false
    t.string "class_name", null: false
    t.text "arguments"
    t.integer "priority", default: 0, null: false
    t.string "active_job_id"
    t.datetime "scheduled_at"
    t.datetime "finished_at"
    t.string "concurrency_key"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["active_job_id"], name: "index_solid_queue_jobs_on_active_job_id"
    t.index ["class_name"], name: "index_solid_queue_jobs_on_class_name"
    t.index ["finished_at"], name: "index_solid_queue_jobs_on_finished_at"
    t.index ["queue_name", "finished_at"], name: "index_solid_queue_jobs_for_filtering"
    t.index ["scheduled_at", "finished_at"], name: "index_solid_queue_jobs_for_alerting"
  end

  create_table "solid_queue_pauses", force: :cascade do |t|
    t.string "queue_name", null: false
    t.datetime "created_at", null: false
    t.index ["queue_name"], name: "index_solid_queue_pauses_on_queue_name", unique: true
  end

  create_table "solid_queue_processes", force: :cascade do |t|
    t.string "kind", null: false
    t.datetime "last_heartbeat_at", null: false
    t.bigint "supervisor_id"
    t.integer "pid", null: false
    t.string "hostname"
    t.text "metadata"
    t.datetime "created_at", null: false
    t.string "name", null: false
    t.index ["last_heartbeat_at"], name: "index_solid_queue_processes_on_last_heartbeat_at"
    t.index ["name", "supervisor_id"], name: "index_solid_queue_processes_on_name_and_supervisor_id", unique: true
    t.index ["supervisor_id"], name: "index_solid_queue_processes_on_supervisor_id"
  end

  create_table "solid_queue_ready_executions", force: :cascade do |t|
    t.bigint "job_id", null: false
    t.string "queue_name", null: false
    t.integer "priority", default: 0, null: false
    t.datetime "created_at", null: false
    t.index ["job_id"], name: "index_solid_queue_ready_executions_on_job_id", unique: true
    t.index ["priority", "job_id"], name: "index_solid_queue_poll_all"
    t.index ["queue_name", "priority", "job_id"], name: "index_solid_queue_poll_by_queue"
  end

  create_table "solid_queue_recurring_executions", force: :cascade do |t|
    t.bigint "job_id", null: false
    t.string "task_key", null: false
    t.datetime "run_at", null: false
    t.datetime "created_at", null: false
    t.index ["job_id"], name: "index_solid_queue_recurring_executions_on_job_id", unique: true
    t.index ["task_key", "run_at"], name: "index_solid_queue_recurring_executions_on_task_key_and_run_at", unique: true
  end

  create_table "solid_queue_recurring_tasks", force: :cascade do |t|
    t.string "key", null: false
    t.string "schedule", null: false
    t.string "command", limit: 2048
    t.string "class_name"
    t.text "arguments"
    t.string "queue_name"
    t.integer "priority", default: 0
    t.boolean "static", default: true, null: false
    t.text "description"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["key"], name: "index_solid_queue_recurring_tasks_on_key", unique: true
    t.index ["static"], name: "index_solid_queue_recurring_tasks_on_static"
  end

  create_table "solid_queue_scheduled_executions", force: :cascade do |t|
    t.bigint "job_id", null: false
    t.string "queue_name", null: false
    t.integer "priority", default: 0, null: false
    t.datetime "scheduled_at", null: false
    t.datetime "created_at", null: false
    t.index ["job_id"], name: "index_solid_queue_scheduled_executions_on_job_id", unique: true
    t.index ["scheduled_at", "priority", "job_id"], name: "index_solid_queue_dispatch_all"
  end

  create_table "solid_queue_semaphores", force: :cascade do |t|
    t.string "key", null: false
    t.integer "value", default: 1, null: false
    t.datetime "expires_at", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["expires_at"], name: "index_solid_queue_semaphores_on_expires_at"
    t.index ["key", "value"], name: "index_solid_queue_semaphores_on_key_and_value"
    t.index ["key"], name: "index_solid_queue_semaphores_on_key", unique: true
  end

  create_table "versions", force: :cascade do |t|
    t.string "whodunnit"
    t.datetime "created_at"
    t.bigint "item_id", null: false
    t.string "item_type", null: false
    t.string "event", null: false
    t.text "object"
    t.text "object_changes"
    t.index ["item_type", "item_id"], name: "index_versions_on_item_type_and_item_id"
  end

  add_foreign_key "active_storage_attachments", "active_storage_blobs", column: "blob_id"
  add_foreign_key "active_storage_variant_records", "active_storage_blobs", column: "blob_id"
  add_foreign_key "croms_adverse_events", "croms_systemic_therapies", column: "systemic_therapy_id"
  add_foreign_key "croms_attachments", "croms_patients", column: "patient_id"
  add_foreign_key "croms_contracts", "croms_institutions", column: "institution_id"
  add_foreign_key "croms_contracts", "croms_users", column: "user_id"
  add_foreign_key "croms_diagnoses", "croms_patients", column: "patient_id"
  add_foreign_key "croms_drugs", "croms_systemic_therapies", column: "systemic_therapy_id"
  add_foreign_key "croms_pathologies", "croms_institutions", column: "institution_id"
  add_foreign_key "croms_pathologies", "croms_patients", column: "patient_id"
  add_foreign_key "croms_pathologies", "croms_users", column: "responsible_pathologist_id"
  add_foreign_key "croms_patient_registrations", "croms_users", column: "sarcoma_board_presenting_physician_id"
  add_foreign_key "croms_radio_therapies", "croms_institutions", column: "institution_id"
  add_foreign_key "croms_radio_therapies", "croms_patients", column: "patient_id"
  add_foreign_key "croms_radio_therapies", "croms_users", column: "responsible_oncologist_id"
  add_foreign_key "croms_radiology_exams", "croms_patients", column: "patient_id"
  add_foreign_key "croms_sarcoma_board_participants", "croms_sarcoma_boards", column: "sarcoma_board_id"
  add_foreign_key "croms_sarcoma_board_participants", "croms_users", column: "participant_id"
  add_foreign_key "croms_sarcoma_boards", "croms_institutions", column: "whoops_surgery_institution_id"
  add_foreign_key "croms_sarcoma_boards", "croms_patients", column: "patient_id"
  add_foreign_key "croms_sarcoma_boards", "croms_users", column: "presenting_physician_id"
  add_foreign_key "croms_sessions", "croms_users", column: "user_id"
  add_foreign_key "croms_surgeries", "croms_institutions", column: "institution_id"
  add_foreign_key "croms_surgeries", "croms_patients", column: "patient_id"
  add_foreign_key "croms_surgeries", "croms_users", column: "responsible_surgeon_id"
  add_foreign_key "croms_systemic_therapies", "croms_institutions", column: "institution_id"
  add_foreign_key "croms_systemic_therapies", "croms_patients", column: "patient_id"
  add_foreign_key "croms_systemic_therapies", "croms_users", column: "responsible_oncologist_id"
  add_foreign_key "croms_treatments", "croms_institutions", column: "institution_id"
  add_foreign_key "croms_treatments", "croms_patients", column: "patient_id"
  add_foreign_key "solid_queue_blocked_executions", "solid_queue_jobs", column: "job_id", on_delete: :cascade
  add_foreign_key "solid_queue_claimed_executions", "solid_queue_jobs", column: "job_id", on_delete: :cascade
  add_foreign_key "solid_queue_failed_executions", "solid_queue_jobs", column: "job_id", on_delete: :cascade
  add_foreign_key "solid_queue_ready_executions", "solid_queue_jobs", column: "job_id", on_delete: :cascade
  add_foreign_key "solid_queue_recurring_executions", "solid_queue_jobs", column: "job_id", on_delete: :cascade
  add_foreign_key "solid_queue_scheduled_executions", "solid_queue_jobs", column: "job_id", on_delete: :cascade
end
