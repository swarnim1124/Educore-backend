# OneApp Relationship Inventory

| Parent Table | Child Table | Parent Column | Child Column | Constraint Name | Delete Behaviour | Update Behaviour | Nullable | Owner Module | Classification |
|---|---|---|---|---|---|---|---|---|---|
| sch_aaa.tb_mfa_method | sch_aaa.tb_mfa_backup_code | id | mfa_method_id | fk_tb_mfa_backup_code_method | CASCADE | NO ACTION | NO | m_AAA | Composition |
| sch_aaa.tb_mfa_method | sch_aaa.tb_mfa_challenge | id | mfa_method_id | fk_tb_mfa_challenge_method | NO ACTION | NO ACTION | NO | m_AAA | Aggregation |
| sch_academic_struct.tb_acad_calendar | sch_course_delivery.tb_acad_evt | id | acad_calendar_id | fk_acad_evt_calendar | RESTRICT | CASCADE | NO | m_course_delivery | Aggregation |
| sch_academic_struct.tb_acad_term | sch_academic_struct.tb_acad_calendar | id | acad_term_id | fk_acad_calendar_term | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_academic_struct.tb_acad_term | sch_course_delivery.tb_crs_offering | id | acad_term_id | fk_crs_offering_term | RESTRICT | CASCADE | NO | m_course_delivery | Aggregation |
| sch_academic_struct.tb_acad_term | sch_examination.tb_exam_session | id | acad_term_id | fk_exam_session_term | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_academic_struct.tb_acad_term | sch_fees.tb_stud_fee_asmt | id | acad_term_id | fk_stud_fee_asmt_term | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_academic_struct.tb_acad_term | sch_results.tb_prog_res | id | last_res_term_id | fk_prog_res_last_term | RESTRICT | CASCADE | YES | m_results | Aggregation |
| sch_academic_struct.tb_acad_term | sch_results.tb_term_res | id | acad_term_id | fk_term_res_term | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_academic_struct.tb_acad_term | sch_student_leave.tb_student_leave_blackout | id | term_id | fk_tb_student_leave_blackout_term | RESTRICT | CASCADE | NO | m_student_leave | Aggregation |
| sch_academic_struct.tb_acad_term | sch_student_leave.tb_student_leave_eligibility | id | term_id | fk_tb_student_leave_eligibility_term | RESTRICT | CASCADE | NO | m_student_leave | Aggregation |
| sch_academic_struct.tb_acad_term | sch_timetable.tb_holiday_adjustment | id | acad_term_id | fk_holiday_term | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_academic_struct.tb_acad_year | sch_academic_struct.tb_acad_term | id | acad_year_id | fk_acad_term_year | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_academic_struct.tb_acad_year | sch_admission.tb_adm_cycle | id | acad_year_id | fk_adm_cycle_acad_year | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_academic_struct.tb_acad_year | sch_employee.tb_fac_advisor_assignment | id | acad_year_id | fk_fac_advisor_assignment_year | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_academic_struct.tb_acad_year | sch_fees.tb_fee_structure | id | acad_year_id | fk_fee_structure_year | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_academic_struct.tb_batch | sch_academic_struct.tb_sec | id | batch_id | fk_sec_batch | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_academic_struct.tb_batch | sch_admission.tb_prog_intake | id | batch_id | fk_prog_intake_batch | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_academic_struct.tb_batch | sch_fees.tb_fee_structure_rule | id | batch_id | fk_fee_rule_batch | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_academic_struct.tb_crs | sch_academic_struct.tb_crs_version | id | crs_id | fk_crs_version_crs | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_academic_struct.tb_crs_version | sch_academic_struct.tb_crs_corequisite | id | corequisite_crs_version_id | fk_crs_coreq_required | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_academic_struct.tb_crs_version | sch_academic_struct.tb_crs_corequisite | id | crs_version_id | fk_crs_coreq_crs | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_academic_struct.tb_crs_version | sch_academic_struct.tb_crs_prerequisite | id | crs_version_id | fk_crs_prereq_crs | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_academic_struct.tb_crs_version | sch_academic_struct.tb_crs_prerequisite | id | prerequisite_crs_version_id | fk_crs_prereq_required | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_academic_struct.tb_crs_version | sch_academic_struct.tb_curr_term_crs | id | crs_version_id | fk_curr_term_crs_version | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_academic_struct.tb_crs_version | sch_academic_struct.tb_elective_group_crs | id | crs_version_id | fk_elective_group_crs_version | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_academic_struct.tb_crs_version | sch_course_delivery.tb_crs_offering | id | crs_version_id | fk_crs_offering_version | RESTRICT | CASCADE | NO | m_course_delivery | Aggregation |
| sch_academic_struct.tb_curr | sch_academic_struct.tb_curr_version | id | curr_id | fk_curr_version_curr | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_academic_struct.tb_curr_term | sch_academic_struct.tb_curr_term_crs | id | curr_term_id | fk_curr_term_crs_curr_term | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_academic_struct.tb_curr_term | sch_academic_struct.tb_elective_group | id | curr_term_id | fk_elective_group_curr_term | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_academic_struct.tb_curr_term | sch_student.tb_stud_acad_progress | id | curr_term_id | fk_stud_progress_term | RESTRICT | CASCADE | NO | m_student | Aggregation |
| sch_academic_struct.tb_curr_version | sch_academic_struct.tb_batch | id | curr_version_id | fk_batch_curr_version | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_academic_struct.tb_curr_version | sch_academic_struct.tb_curr_term | id | curr_version_id | fk_curr_term_curr_version | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_academic_struct.tb_curr_version | sch_admission.tb_prog_intake | id | curr_version_id | fk_prog_intake_curr_version | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_academic_struct.tb_elective_group | sch_academic_struct.tb_elective_group_crs | id | elective_group_id | fk_elective_group_crs_group | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_academic_struct.tb_prog | sch_academic_struct.tb_curr | id | prog_id | fk_curr_prog | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_academic_struct.tb_prog | sch_admission.tb_merit_list | id | prog_id | fk_merit_list_program | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_academic_struct.tb_prog | sch_admission.tb_prog_intake | id | prog_id | fk_prog_intake_prog | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_academic_struct.tb_prog | sch_employee.tb_fac_acad_assignment | id | prog_id | fk_fac_acad_assignment_prog | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_academic_struct.tb_prog | sch_employee.tb_fac_advisor_assignment | id | prog_id | fk_fac_advisor_assignment_prog | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_academic_struct.tb_prog | sch_fees.tb_fee_structure_rule | id | prog_id | fk_fee_rule_prog | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_academic_struct.tb_sec | sch_admission.tb_seat_allocation | id | sec_id | fk_seat_allocation_section | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_academic_struct.tb_sec | sch_course_delivery.tb_crs_offering | id | sec_id | fk_crs_offering_sec | RESTRICT | CASCADE | NO | m_course_delivery | Aggregation |
| sch_academic_struct.tb_sec | sch_results.tb_res_publication | id | sec_id | fk_res_publication_sec | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_academic_struct.tb_sec | sch_student.tb_stud | id | current_sec_id | fk_stud_section | RESTRICT | CASCADE | YES | m_student | Aggregation |
| sch_academic_struct.tb_sec | sch_student.tb_stud_sec_history | id | to_sec_id | fk_sec_history_to_sec | RESTRICT | CASCADE | NO | m_student | Historical |
| sch_academic_struct.tb_sec | sch_student.tb_stud_sec_history | id | from_sec_id | fk_sec_history_from_sec | RESTRICT | CASCADE | NO | m_student | Historical |
| sch_academic_struct.tb_sec | sch_timetable.tb_extra_class | id | sec_id | fk_extra_sec | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_academic_struct.tb_sec | sch_timetable.tb_tt | id | sec_id | fk_tt_sec | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_academic_struct.tb_sec | sch_timetable.tb_tt_entry_sec | id | sec_id | fk_tt_entry_sec_section | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_admission.tb_adm | sch_student.tb_stud | id | adm_id | fk_stud_admission | RESTRICT | CASCADE | YES | m_student | Aggregation |
| sch_admission.tb_adm_cycle | sch_admission.tb_adm_deferral | id | from_cycle_id | fk_deferral_from_cycle | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_adm_cycle | sch_admission.tb_adm_deferral | id | to_cycle_id | fk_deferral_to_cycle | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_adm_cycle | sch_admission.tb_adm_round | id | adm_cycle_id | fk_adm_round_cycle | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_adm_cycle | sch_admission.tb_prog_intake | id | adm_cycle_id | fk_prog_intake_cycle | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_adm_offer | sch_admission.tb_offer_response | id | adm_offer_id | fk_offer_response_offer | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_adm_offer | sch_admission.tb_seat_allocation | id | adm_offer_id | fk_seat_allocation_offer | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_adm_round | sch_admission.tb_adm_window | id | adm_round_id | fk_adm_window_round | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_adm_round | sch_admission.tb_application | id | adm_round_id | fk_application_round | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_adm_round | sch_admission.tb_merit_list | id | adm_round_id | fk_merit_list_round | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_applicant | sch_admission.tb_applicant_source | id | applicant_id | fk_applicant_source_applicant | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_applicant | sch_admission.tb_application | id | applicant_id | fk_application_applicant | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_application | sch_admission.tb_adm | id | application_id | fk_adm_application | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_application | sch_admission.tb_adm_deferral | id | application_id | fk_deferral_application | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_application | sch_admission.tb_adm_offer | id | application_id | fk_adm_offer_application | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_application | sch_admission.tb_application_asmt | id | application_id | fk_app_asmt_application | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_application | sch_admission.tb_application_doc | id | application_id | fk_app_doc_application | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_application | sch_admission.tb_application_eligibility | id | application_id | fk_app_eligibility_application | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_application | sch_admission.tb_application_evt | id | application_id | fk_app_evt_application | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_application | sch_admission.tb_application_note | id | application_id | fk_app_note_application | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_application | sch_admission.tb_application_status_history | id | application_id | fk_app_status_history_app | RESTRICT | CASCADE | NO | m_admission | Historical |
| sch_admission.tb_application | sch_admission.tb_application_verification | id | application_id | fk_app_verify_application | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_application | sch_admission.tb_application_withdrawal | id | application_id | fk_application_withdrawal_app | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_application | sch_admission.tb_merit_list_entry | id | application_id | fk_merit_entry_application | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_application | sch_admission.tb_selection_decision | id | application_id | fk_selection_decision_app | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_application | sch_admission.tb_waitlist | id | application_id | fk_waitlist_application | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_application_asmt | sch_admission.tb_asmt_res | id | application_asmt_id | fk_asmt_res_asmt | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_application_doc | sch_admission.tb_doc_verification | id | application_doc_id | fk_doc_verify_doc | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_application_eligibility | sch_admission.tb_eligibility_criteria_res | id | application_eligibility_id | fk_eligibility_result | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_merit_list | sch_admission.tb_merit_list_entry | id | merit_list_id | fk_merit_entry_list | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_prog_intake | sch_admission.tb_application | id | prog_intake_id | fk_application_prog_intake | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_prog_intake | sch_admission.tb_prog_intake_category | id | prog_intake_id | fk_intake_category | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_prog_intake | sch_admission.tb_seat_allocation | id | prog_intake_id | fk_seat_allocation_intake | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_admission.tb_prog_intake | sch_student.tb_stud_enrollment | id | prog_intake_id | fk_stud_enrollment_prog_intake | RESTRICT | CASCADE | NO | m_student | Aggregation |
| sch_assessment.tb_asmt | sch_assessment.tb_asmt_component | id | asmt_id | fk_asmt_component_asmt | RESTRICT | CASCADE | NO | m_assessment | Aggregation |
| sch_assessment.tb_asmt | sch_assessment.tb_asmt_submission | id | asmt_id | fk_asmt_submission_asmt | RESTRICT | CASCADE | NO | m_assessment | Aggregation |
| sch_assessment.tb_asmt | sch_lms.tb_lms_assignment | id | asmt_id | fk_tb_lms_assignment_asmt | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_assessment.tb_asmt | sch_lms.tb_lms_assignment_grade_view | id | asmt_id | fk_tb_lms_assignment_grade_view_asmt | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_assessment.tb_asmt_component | sch_assessment.tb_asmt_att_policy | id | asmt_component_id | fk_asmt_att_policy_component | RESTRICT | CASCADE | NO | m_assessment | Aggregation |
| sch_assessment.tb_asmt_component | sch_assessment.tb_asmt_mark | id | asmt_component_id | fk_asmt_mark_component | RESTRICT | CASCADE | NO | m_assessment | Aggregation |
| sch_assessment.tb_asmt_mark | sch_assessment.tb_rubric_score | id | asmt_mark_id | fk_rubric_score_mark | RESTRICT | CASCADE | NO | m_assessment | Aggregation |
| sch_assessment.tb_asmt_submission | sch_assessment.tb_asmt_mark | id | submission_id | fk_asmt_mark_submission | RESTRICT | CASCADE | YES | m_assessment | Aggregation |
| sch_assessment.tb_rubric | sch_assessment.tb_asmt_component | id | rubric_id | fk_asmt_component_rubric | RESTRICT | CASCADE | YES | m_assessment | Aggregation |
| sch_assessment.tb_rubric | sch_assessment.tb_rubric_criteria | id | rubric_id | fk_rubric_criteria_rubric | RESTRICT | CASCADE | NO | m_assessment | Aggregation |
| sch_assessment.tb_rubric_criteria | sch_assessment.tb_rubric_score | id | rubric_criteria_id | fk_rubric_score_criteria | RESTRICT | CASCADE | NO | m_assessment | Aggregation |
| sch_attendance.tb_att_policy | sch_assessment.tb_asmt_att_policy | id | att_policy_id | fk_asmt_att_policy_att_policy | RESTRICT | CASCADE | NO | m_assessment | Aggregation |
| sch_attendance.tb_att_record | sch_attendance.tb_att_correction | id | att_record_id | fk_att_corr_record | RESTRICT | CASCADE | NO | m_attendance | Aggregation |
| sch_attendance.tb_att_session | sch_attendance.tb_att_record | id | att_session_id | fk_att_record_session | RESTRICT | CASCADE | NO | m_attendance | Aggregation |
| sch_core.tb_address | sch_iam.tb_user_address | id | address_id | fk_tb_user_address_address | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_core.tb_address | sch_org.tb_org_profile | id | address_id | fk_tb_org_profile_address | NO ACTION | NO ACTION | YES | m_org | Aggregation |
| sch_core.tb_city | sch_core.tb_address | id | city_id | fk_tb_address_city | NO ACTION | NO ACTION | NO | m_core | Aggregation |
| sch_core.tb_city | sch_core.tb_city_postal_code | id | city_id | fk_tb_city_postal_code_city | NO ACTION | NO ACTION | NO | m_core | Aggregation |
| sch_core.tb_city_postal_code | sch_core.tb_address | id | postal_code_id | fk_tb_address_postal | NO ACTION | NO ACTION | NO | m_core | Aggregation |
| sch_core.tb_country | sch_core.tb_country_profile | id | country_id | fk_tb_country_profile_country | NO ACTION | NO ACTION | NO | m_core | Aggregation |
| sch_core.tb_country | sch_core.tb_state | id | country_id | fk_tb_state_country | NO ACTION | NO ACTION | NO | m_core | Aggregation |
| sch_core.tb_country | sch_iam.tb_user_profile | id | nationality_id | fk_tb_user_profile_country | NO ACTION | NO ACTION | YES | m_iam | Aggregation |
| sch_core.tb_country | sch_org.tb_org | id | country_id | fk_tb_org_country | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_core.tb_country | sch_sys_admin.tb_login_policy_allowed_country | id | country_id | fk_tb_login_policy_allowed_country_country | NO ACTION | NO ACTION | NO | m_sys_admin | Historical |
| sch_core.tb_country | sch_sys_admin.tb_login_policy_blocked_country | id | country_id | fk_tb_login_policy_blocked_country_country | NO ACTION | NO ACTION | NO | m_sys_admin | Historical |
| sch_core.tb_currency | sch_core.tb_country_profile | currency_code | currency_code | fk_tb_country_profile_currency | NO ACTION | NO ACTION | YES | m_core | Aggregation |
| sch_core.tb_district | sch_core.tb_city | id | district_id | fk_tb_city_district | NO ACTION | NO ACTION | NO | m_core | Aggregation |
| sch_core.tb_dms | sch_admission.tb_application_doc | id | doc_id | fk_app_doc_dms | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_core.tb_dms | sch_assessment.tb_asmt_submission | id | submission_doc_id | fk_asmt_submission_doc | RESTRICT | CASCADE | YES | m_assessment | Aggregation |
| sch_core.tb_dms | sch_attendance.tb_att_correction | id | proof_doc_id | fk_att_corr_proof_doc | RESTRICT | CASCADE | YES | m_attendance | Aggregation |
| sch_core.tb_dms | sch_employee.tb_emp_exp | id | proof_doc_id | fk_emp_exp_doc | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_core.tb_dms | sch_employee.tb_emp_profile | id | photo_doc_id | fk_emp_profile_photo | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_core.tb_dms | sch_employee.tb_emp_qual | id | deg_credential_id | fk_emp_qual_doc | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_core.tb_dms | sch_employee.tb_fac_certification | id | certificate_doc_id | fk_fac_cert_doc | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_core.tb_dms | sch_examination.tb_exam_script | id | script_doc_id | fk_exam_script_doc | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_core.tb_dms | sch_examination.tb_hall_ticket | id | doc_id | fk_hall_ticket_doc | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_core.tb_dms | sch_fees.tb_concession | id | doc_id | fk_concession_doc | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_core.tb_dms | sch_fees.tb_fee_waiver | id | doc_id | fk_waiver_doc | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_core.tb_dms | sch_fees.tb_payment | id | doc_id | fk_payment_doc | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_core.tb_dms | sch_fees.tb_scholarship | id | doc_id | fk_scholarship_doc | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_core.tb_dms | sch_iam.tb_user_doc | id | doc_id | fk_tb_user_doc_dms | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_core.tb_dms | sch_iam.tb_user_identifier | id | scanned_copy | fk_tb_user_identifier_dms | NO ACTION | NO ACTION | YES | m_iam | Aggregation |
| sch_core.tb_dms | sch_iam.tb_user_profile | id | profile_photo_id | fk_tb_user_profile_photo | NO ACTION | NO ACTION | YES | m_iam | Aggregation |
| sch_core.tb_dms | sch_lms.tb_lms_announcement_attachment | id | dms_id | fk_tb_lms_announcement_attachment_dms | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_core.tb_dms | sch_lms.tb_lms_assignment_attachment | id | dms_id | fk_tb_lms_assignment_attachment_dms | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_core.tb_dms | sch_lms.tb_lms_badge | id | badge_image_dms_id | fk_tb_lms_badge_image | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_core.tb_dms | sch_lms.tb_lms_certificate_award | id | certificate_dms_id | fk_tb_lms_certificate_award_dms | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_core.tb_dms | sch_lms.tb_lms_certificate_template | id | template_dms_id | fk_tb_lms_certificate_template_dms | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_core.tb_dms | sch_lms.tb_lms_content_attachment | id | dms_id | fk_tb_lms_content_attachment_dms | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_core.tb_dms | sch_lms.tb_lms_content_translation | id | dms_id | fk_tb_lms_content_translation_dms | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_core.tb_dms | sch_lms.tb_lms_content_version | id | dms_id | fk_tb_lms_content_version_dms | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_core.tb_dms | sch_lms.tb_lms_document | id | dms_id | fk_tb_lms_document_dms | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_core.tb_dms | sch_lms.tb_lms_feedback_attachment | id | dms_id | fk_tb_lms_feedback_attachment_dms | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_core.tb_dms | sch_lms.tb_lms_library_resource | id | dms_id | fk_tb_lms_library_resource_dms | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_core.tb_dms | sch_lms.tb_lms_question_attachment | id | dms_id | fk_tb_lms_question_attachment_dms | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_core.tb_dms | sch_lms.tb_lms_question_explanation | id | dms_id | fk_tb_lms_question_explanation_dms | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_core.tb_dms | sch_lms.tb_lms_reply_attachment | id | dms_id | fk_tb_lms_reply_attachment_dms | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_core.tb_dms | sch_lms.tb_lms_scorm_package | id | dms_id | fk_tb_lms_scorm_package_dms | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_core.tb_dms | sch_lms.tb_lms_submission_file | id | dms_id | fk_tb_lms_submission_file_dms | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_core.tb_dms | sch_lms.tb_lms_thread_attachment | id | dms_id | fk_tb_lms_thread_attachment_dms | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_core.tb_dms | sch_lms.tb_lms_video | id | thumbnail_dms_id | fk_tb_lms_video_thumbnail_dms | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_core.tb_dms | sch_lms.tb_lms_video_caption | id | dms_id | fk_tb_lms_video_caption_dms | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_core.tb_dms | sch_lms.tb_lms_workspace_profile | id | banner_dms_id | fk_tb_lms_workspace_profile_banner_dms | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_core.tb_dms | sch_lms.tb_lms_xapi_package | id | dms_id | fk_tb_lms_xapi_package_dms | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_core.tb_dms | sch_org.tb_inst_grp_profile | id | mission_stmt_id | fk_tb_inst_grp_profile_mission | NO ACTION | NO ACTION | YES | m_org | Aggregation |
| sch_core.tb_dms | sch_org.tb_inst_grp_profile | id | vision_stmt_id | fk_tb_inst_grp_profile_vision | NO ACTION | NO ACTION | YES | m_org | Aggregation |
| sch_core.tb_dms | sch_org.tb_inst_profile | id | vision_stmt_id | fk_tb_inst_profile_vision | NO ACTION | NO ACTION | YES | m_org | Aggregation |
| sch_core.tb_dms | sch_org.tb_inst_profile | id | motto_id | fk_tb_inst_profile_motto | NO ACTION | NO ACTION | YES | m_org | Aggregation |
| sch_core.tb_dms | sch_org.tb_inst_profile | id | mission_stmt_id | fk_tb_inst_profile_mission | NO ACTION | NO ACTION | YES | m_org | Aggregation |
| sch_core.tb_dms | sch_org.tb_org_branding | id | logo_id | fk_tb_org_branding_logo | NO ACTION | NO ACTION | YES | m_org | Aggregation |
| sch_core.tb_dms | sch_org.tb_org_doc | id | doc_id | fk_tb_org_doc_dms | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_core.tb_dms | sch_results.tb_grade_card | id | doc_id | fk_grade_card_doc | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_core.tb_dms | sch_results.tb_res_publication | id | publication_doc_id | fk_res_publication_doc | RESTRICT | CASCADE | YES | m_results | Aggregation |
| sch_core.tb_dms | sch_student.tb_stud | id | photo_doc_id | fk_stud_photo | RESTRICT | CASCADE | YES | m_student | Aggregation |
| sch_core.tb_dms | sch_student.tb_stud_graduation | id | certificate_doc_id | fk_stud_grad_certificate | RESTRICT | CASCADE | YES | m_student | Aggregation |
| sch_core.tb_dms | sch_student_leave.tb_student_leave_support_doc | id | dms_id | fk_tb_student_leave_support_doc_dms | RESTRICT | CASCADE | NO | m_student_leave | Aggregation |
| sch_core.tb_language | sch_core.tb_country_profile | id | primary_lang | fk_tb_country_profile_language | NO ACTION | NO ACTION | YES | m_core | Aggregation |
| sch_core.tb_language | sch_iam.tb_user_profile | id | primary_lang_id | fk_tb_user_profile_language | NO ACTION | NO ACTION | YES | m_iam | Aggregation |
| sch_core.tb_language | sch_lms.tb_lms_workspace_profile | id | default_language_id | fk_tb_lms_workspace_profile_language | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_core.tb_state | sch_core.tb_district | id | state_id | fk_tb_district_state | NO ACTION | NO ACTION | NO | m_core | Aggregation |
| sch_course_delivery.tb_crs_offering | sch_assessment.tb_asmt | id | crs_offering_id | fk_asmt_crs_offering | RESTRICT | CASCADE | NO | m_assessment | Aggregation |
| sch_course_delivery.tb_crs_offering | sch_assessment.tb_asmt_att_policy | id | crs_offering_id | fk_asmt_att_policy_crs | RESTRICT | CASCADE | NO | m_assessment | Aggregation |
| sch_course_delivery.tb_crs_offering | sch_course_delivery.tb_crs_offering_group | id | crs_offering_id | fk_crs_offering_group_offering | RESTRICT | CASCADE | NO | m_course_delivery | Aggregation |
| sch_course_delivery.tb_crs_offering | sch_course_delivery.tb_crs_offering_status_history | id | crs_offering_id | fk_crs_offering_status_history_offering | RESTRICT | CASCADE | NO | m_course_delivery | Historical |
| sch_course_delivery.tb_crs_offering | sch_course_delivery.tb_fac_crs_assignment | id | crs_offering_id | fk_fac_crs_assignment_offering | RESTRICT | CASCADE | NO | m_course_delivery | Aggregation |
| sch_course_delivery.tb_crs_offering | sch_course_delivery.tb_stud_crs_registration | id | crs_offering_id | fk_stud_crs_registration_offering | RESTRICT | CASCADE | NO | m_course_delivery | Aggregation |
| sch_course_delivery.tb_crs_offering | sch_examination.tb_exam | id | crs_offering_id | fk_exam_crs | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_course_delivery.tb_crs_offering | sch_lms.tb_lms_workspace | id | crs_offering_id | fk_tb_lms_workspace_crs_offering | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_course_delivery.tb_crs_offering | sch_timetable.tb_extra_class | id | crs_offering_id | fk_extra_crs | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_course_delivery.tb_crs_offering | sch_timetable.tb_tt_entry | id | crs_offering_id | fk_tt_entry_crs | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_course_delivery.tb_crs_offering_group | sch_course_delivery.tb_fac_group_assignment | id | crs_offering_group_id | fk_fac_group_assignment_group | RESTRICT | CASCADE | NO | m_course_delivery | Aggregation |
| sch_course_delivery.tb_fac_crs_assignment | sch_timetable.tb_tt_entry | id | fac_crs_assignment_id | fk_tt_entry_fac_assignment | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_course_delivery.tb_stud_crs_registration | sch_results.tb_crs_res | id | stud_crs_enrollment_id | fk_crs_res_enrollment | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_employee.tb_emp | sch_employee.tb_emp_exp | id | emp_id | fk_emp_exp_emp | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_employee.tb_emp | sch_employee.tb_emp_profile | id | emp_id | fk_emp_profile_emp | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_employee.tb_emp | sch_employee.tb_emp_qual | id | emp_id | fk_emp_qual_emp | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_employee.tb_emp | sch_employee.tb_employment | id | emp_id | fk_employment_emp | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_employee.tb_emp | sch_employee.tb_fac | id | emp_id | fk_fac_emp | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_employee.tb_employment | sch_employee.tb_department_assignment | id | employment_id | fk_department_assignment_employment | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_employee.tb_employment | sch_employee.tb_employment_history | id | employment_id | fk_employment_history_employment | RESTRICT | CASCADE | NO | m_employee | Historical |
| sch_employee.tb_employment | sch_employee.tb_rpting_manager | id | manager_employment_id | fk_rpting_manager_manager | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_employee.tb_employment | sch_employee.tb_rpting_manager | id | employment_id | fk_rpting_manager_employment | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_employee.tb_fac | sch_assessment.tb_asmt_mark | id | evaluated_by_fac_id | fk_asmt_mark_evaluated_by | RESTRICT | CASCADE | YES | m_assessment | Aggregation |
| sch_employee.tb_fac | sch_attendance.tb_att_session | id | marked_by_fac_id | fk_att_session_marked_by | RESTRICT | CASCADE | NO | m_attendance | Aggregation |
| sch_employee.tb_fac | sch_course_delivery.tb_fac_crs_assignment | id | fac_id | fk_fac_crs_assignment_fac | RESTRICT | CASCADE | NO | m_course_delivery | Aggregation |
| sch_employee.tb_fac | sch_course_delivery.tb_fac_group_assignment | id | fac_id | fk_fac_group_assignment_fac | RESTRICT | CASCADE | NO | m_course_delivery | Aggregation |
| sch_employee.tb_fac | sch_employee.tb_fac_acad_assignment | id | fac_id | fk_fac_acad_assignment_fac | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_employee.tb_fac | sch_employee.tb_fac_advisor_assignment | id | fac_id | fk_fac_advisor_assignment_fac | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_employee.tb_fac | sch_employee.tb_fac_certification | id | fac_id | fk_fac_cert_fac | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_employee.tb_fac | sch_employee.tb_fac_profile | id | fac_id | fk_fac_profile_fac | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_employee.tb_fac | sch_examination.tb_exam_evaluation | id | evaluator_id | fk_exam_evaluation_fac | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_employee.tb_fac | sch_examination.tb_exam_final_mark | id | finalized_by | fk_exam_final_by | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_employee.tb_fac | sch_examination.tb_exam_malpractice | id | rpted_by | fk_exam_malpractice_reported_by | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_employee.tb_fac | sch_examination.tb_exam_moderation | id | moderator_id | fk_exam_mod_moderator | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_employee.tb_fac | sch_examination.tb_exam_room_invigilator | id | fac_id | fk_invigilator_fac | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_employee.tb_fac | sch_lms.tb_lms_live_class | id | host_id | fk_tb_lms_live_class_host | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_employee.tb_fac | sch_lms.tb_lms_submission_feedback | id | faculty_id | fk_tb_lms_submission_feedback_faculty | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_employee.tb_fac | sch_timetable.tb_class_session_change | id | old_fac_id | fk_change_old_fac | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_employee.tb_fac | sch_timetable.tb_class_session_change | id | new_fac_id | fk_change_new_fac | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_employee.tb_fac | sch_timetable.tb_class_session_fac | id | fac_id | fk_class_session_fac_fac | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_employee.tb_fac | sch_timetable.tb_extra_class | id | fac_id | fk_extra_fac | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_examination.tb_exam | sch_examination.tb_exam_registration | id | exam_id | fk_exam_registration_exam | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_examination.tb_exam | sch_examination.tb_exam_room | id | exam_id | fk_exam_room_exam | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_examination.tb_exam_evaluation | sch_examination.tb_exam_final_mark | id | finalized_from_evaluation_id | fk_exam_final_evaluation | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_examination.tb_exam_evaluation | sch_examination.tb_exam_moderation | id | exam_evaluation_id | fk_exam_mod_evaluation | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_examination.tb_exam_registration | sch_examination.tb_exam_att | id | exam_registration_id | fk_exam_att_reg | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_examination.tb_exam_registration | sch_examination.tb_exam_final_mark | id | exam_registration_id | fk_exam_final_reg | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_examination.tb_exam_registration | sch_examination.tb_exam_malpractice | id | exam_registration_id | fk_exam_malpractice_reg | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_examination.tb_exam_registration | sch_examination.tb_exam_script | id | exam_registration_id | fk_exam_script_reg | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_examination.tb_exam_registration | sch_examination.tb_hall_ticket | id | exam_registration_id | fk_hall_ticket_reg | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_examination.tb_exam_room | sch_examination.tb_exam_att | id | exam_room_id | fk_exam_att_room | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_examination.tb_exam_room | sch_examination.tb_exam_malpractice | id | exam_room_id | fk_exam_malpractice_room | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_examination.tb_exam_room | sch_examination.tb_exam_room_invigilator | id | exam_room_id | fk_invigilator_room | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_examination.tb_exam_script | sch_examination.tb_exam_evaluation | id | exam_script_id | fk_exam_evaluation_script | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_examination.tb_exam_session | sch_examination.tb_exam | id | exam_session_id | fk_exam_session | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_fees.tb_fee_structure | sch_fees.tb_fee_structure_component | id | fee_structure_id | fk_fee_component_structure | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_fees.tb_fee_structure | sch_fees.tb_fee_structure_rule | id | fee_structure_id | fk_fee_rule_structure | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_fees.tb_fee_structure | sch_fees.tb_stud_fee_asmt | id | fee_structure_id | fk_stud_fee_asmt_structure | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_fees.tb_fee_structure_component | sch_fees.tb_stud_fee_component | id | fee_structure_component_id | fk_stud_fee_component_structure | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_fees.tb_financial_ledger | sch_fees.tb_payment_allocation | id | financial_ledger_id | fk_payment_alloc_ledger | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_fees.tb_installment_plan | sch_fees.tb_installment_plan_detail | id | installment_plan_id | fk_installment_detail_plan | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_fees.tb_installment_plan | sch_fees.tb_stud_fee_asmt | id | installment_plan_id | fk_stud_fee_asmt_installment_plan | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_fees.tb_payment | sch_fees.tb_payment_allocation | id | payment_id | fk_payment_alloc_payment | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_fees.tb_payment | sch_fees.tb_payment_gateway_transaction | id | payment_id | fk_gateway_payment | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_fees.tb_payment | sch_fees.tb_refund | id | payment_id | fk_refund_payment | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_fees.tb_stud_fee_asmt | sch_fees.tb_financial_ledger | id | stud_fee_asmt_id | fk_ledger_asmt | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_fees.tb_stud_fee_asmt | sch_fees.tb_penalty | id | stud_fee_asmt_id | fk_penalty_asmt | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_fees.tb_stud_fee_asmt | sch_fees.tb_stud_fee_component | id | stud_fee_asmt_id | fk_stud_fee_component_asmt | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_fees.tb_stud_fee_asmt | sch_fees.tb_stud_installment | id | stud_fee_asmt_id | fk_stud_installment_asmt | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_iam.tb_role | sch_iam.tb_role | id | par_role_id | fk_tb_role_parent | NO ACTION | NO ACTION | YES | m_iam | Aggregation |
| sch_iam.tb_role | sch_rbac.tb_org_role | id | role_id | fk_tb_org_role_role | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_iam.tb_role | sch_rbac.tb_role_permission | id | role_id | fk_tb_role_permission_role | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_iam.tb_user | sch_aaa.tb_account_lock | id | user_id | fk_tb_account_lock_user | NO ACTION | NO ACTION | NO | m_AAA | Aggregation |
| sch_iam.tb_user | sch_aaa.tb_auth_log | id | user_id | fk_tb_auth_log_user | NO ACTION | NO ACTION | NO | m_AAA | Historical |
| sch_iam.tb_user | sch_aaa.tb_mfa_challenge | id | user_id | fk_tb_mfa_challenge_user | NO ACTION | NO ACTION | NO | m_AAA | Aggregation |
| sch_iam.tb_user | sch_aaa.tb_mfa_method | id | user_id | fk_tb_mfa_method_user | NO ACTION | NO ACTION | NO | m_AAA | Aggregation |
| sch_iam.tb_user | sch_aaa.tb_password_reset | id | user_id | fk_tb_password_reset_user | NO ACTION | NO ACTION | NO | m_AAA | Aggregation |
| sch_iam.tb_user | sch_admission.tb_adm | id | confirmed_by | fk_adm_confirmed_by | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_iam.tb_user | sch_admission.tb_adm_deferral | id | approved_by | fk_deferral_approved_by | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_iam.tb_user | sch_admission.tb_applicant | id | user_id | fk_applicant_user | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_iam.tb_user | sch_admission.tb_application_eligibility | id | evaluated_by | fk_app_eligibility_user | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_iam.tb_user | sch_admission.tb_application_evt | id | performed_by | fk_app_evt_user | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_iam.tb_user | sch_admission.tb_application_note | id | created_by | fk_app_note_user | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_iam.tb_user | sch_admission.tb_application_status_history | id | changed_by | fk_app_status_history_user | RESTRICT | CASCADE | NO | m_admission | Historical |
| sch_iam.tb_user | sch_admission.tb_application_verification | id | verified_by | fk_app_verify_user | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_iam.tb_user | sch_admission.tb_doc_verification | id | verified_by | fk_doc_verify_user | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_iam.tb_user | sch_admission.tb_selection_decision | id | decided_by | fk_selection_decision_user | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_iam.tb_user | sch_assessment.tb_asmt | id | created_by | fk_asmt_created_by | RESTRICT | CASCADE | YES | m_assessment | Aggregation |
| sch_iam.tb_user | sch_assessment.tb_asmt | id | updated_by | fk_asmt_updated_by | RESTRICT | CASCADE | YES | m_assessment | Aggregation |
| sch_iam.tb_user | sch_assessment.tb_asmt_att_policy | id | updated_by | fk_asmt_att_policy_updated_by | RESTRICT | CASCADE | YES | m_assessment | Aggregation |
| sch_iam.tb_user | sch_assessment.tb_asmt_att_policy | id | created_by | fk_asmt_att_policy_created_by | RESTRICT | CASCADE | YES | m_assessment | Aggregation |
| sch_iam.tb_user | sch_assessment.tb_asmt_component | id | updated_by | fk_asmt_component_updated_by | RESTRICT | CASCADE | YES | m_assessment | Aggregation |
| sch_iam.tb_user | sch_assessment.tb_asmt_component | id | created_by | fk_asmt_component_created_by | RESTRICT | CASCADE | YES | m_assessment | Aggregation |
| sch_iam.tb_user | sch_assessment.tb_asmt_mark | id | created_by | fk_asmt_mark_created_by | RESTRICT | CASCADE | YES | m_assessment | Aggregation |
| sch_iam.tb_user | sch_assessment.tb_asmt_mark | id | updated_by | fk_asmt_mark_updated_by | RESTRICT | CASCADE | YES | m_assessment | Aggregation |
| sch_iam.tb_user | sch_assessment.tb_asmt_submission | id | updated_by | fk_asmt_submission_updated_by | RESTRICT | CASCADE | YES | m_assessment | Aggregation |
| sch_iam.tb_user | sch_assessment.tb_asmt_submission | id | created_by | fk_asmt_submission_created_by | RESTRICT | CASCADE | YES | m_assessment | Aggregation |
| sch_iam.tb_user | sch_assessment.tb_rubric | id | updated_by | fk_rubric_updated_by | RESTRICT | CASCADE | YES | m_assessment | Aggregation |
| sch_iam.tb_user | sch_assessment.tb_rubric | id | created_by | fk_rubric_created_by | RESTRICT | CASCADE | YES | m_assessment | Aggregation |
| sch_iam.tb_user | sch_assessment.tb_rubric_criteria | id | created_by | fk_rubric_criteria_created_by | RESTRICT | CASCADE | YES | m_assessment | Aggregation |
| sch_iam.tb_user | sch_assessment.tb_rubric_criteria | id | updated_by | fk_rubric_criteria_updated_by | RESTRICT | CASCADE | YES | m_assessment | Aggregation |
| sch_iam.tb_user | sch_assessment.tb_rubric_score | id | updated_by | fk_rubric_score_updated_by | RESTRICT | CASCADE | YES | m_assessment | Aggregation |
| sch_iam.tb_user | sch_assessment.tb_rubric_score | id | created_by | fk_rubric_score_created_by | RESTRICT | CASCADE | YES | m_assessment | Aggregation |
| sch_iam.tb_user | sch_attendance.tb_att_correction | id | approved_by_user_id | fk_att_corr_approved_by | RESTRICT | CASCADE | YES | m_attendance | Aggregation |
| sch_iam.tb_user | sch_attendance.tb_att_correction | id | requested_by_user_id | fk_att_corr_requested_by | RESTRICT | CASCADE | NO | m_attendance | Aggregation |
| sch_iam.tb_user | sch_attendance.tb_att_correction | id | updated_by | fk_att_corr_updated_by | RESTRICT | CASCADE | YES | m_attendance | Aggregation |
| sch_iam.tb_user | sch_attendance.tb_att_correction | id | created_by | fk_att_corr_created_by | RESTRICT | CASCADE | YES | m_attendance | Aggregation |
| sch_iam.tb_user | sch_attendance.tb_att_policy | id | updated_by | fk_att_policy_updated_by | RESTRICT | CASCADE | YES | m_attendance | Aggregation |
| sch_iam.tb_user | sch_attendance.tb_att_policy | id | created_by | fk_att_policy_created_by | RESTRICT | CASCADE | YES | m_attendance | Aggregation |
| sch_iam.tb_user | sch_attendance.tb_att_record | id | created_by | fk_att_record_created_by | RESTRICT | CASCADE | YES | m_attendance | Aggregation |
| sch_iam.tb_user | sch_attendance.tb_att_record | id | updated_by | fk_att_record_updated_by | RESTRICT | CASCADE | YES | m_attendance | Aggregation |
| sch_iam.tb_user | sch_attendance.tb_att_session | id | updated_by | fk_att_session_updated_by | RESTRICT | CASCADE | YES | m_attendance | Aggregation |
| sch_iam.tb_user | sch_attendance.tb_att_session | id | created_by | fk_att_session_created_by | RESTRICT | CASCADE | YES | m_attendance | Aggregation |
| sch_iam.tb_user | sch_course_delivery.tb_acad_evt | id | created_by | fk_acad_evt_created_by | RESTRICT | CASCADE | YES | m_course_delivery | Aggregation |
| sch_iam.tb_user | sch_course_delivery.tb_acad_evt | id | updated_by | fk_acad_evt_updated_by | RESTRICT | CASCADE | YES | m_course_delivery | Aggregation |
| sch_iam.tb_user | sch_course_delivery.tb_crs_offering | id | updated_by | fk_crs_offering_updated_by | RESTRICT | CASCADE | YES | m_course_delivery | Aggregation |
| sch_iam.tb_user | sch_course_delivery.tb_crs_offering | id | created_by | fk_crs_offering_created_by | RESTRICT | CASCADE | YES | m_course_delivery | Aggregation |
| sch_iam.tb_user | sch_course_delivery.tb_crs_offering_group | id | created_by | fk_crs_offering_group_created_by | RESTRICT | CASCADE | YES | m_course_delivery | Aggregation |
| sch_iam.tb_user | sch_course_delivery.tb_crs_offering_group | id | updated_by | fk_crs_offering_group_updated_by | RESTRICT | CASCADE | YES | m_course_delivery | Aggregation |
| sch_iam.tb_user | sch_course_delivery.tb_crs_offering_status_history | id | updated_by | fk_crs_offering_status_history_updated_by | RESTRICT | CASCADE | YES | m_course_delivery | Historical |
| sch_iam.tb_user | sch_course_delivery.tb_crs_offering_status_history | id | created_by | fk_crs_offering_status_history_created_by | RESTRICT | CASCADE | YES | m_course_delivery | Historical |
| sch_iam.tb_user | sch_course_delivery.tb_fac_crs_assignment | id | updated_by | fk_fac_crs_assignment_updated_by | RESTRICT | CASCADE | YES | m_course_delivery | Aggregation |
| sch_iam.tb_user | sch_course_delivery.tb_fac_crs_assignment | id | created_by | fk_fac_crs_assignment_created_by | RESTRICT | CASCADE | YES | m_course_delivery | Aggregation |
| sch_iam.tb_user | sch_course_delivery.tb_fac_group_assignment | id | created_by | fk_fac_group_assignment_created_by | RESTRICT | CASCADE | YES | m_course_delivery | Aggregation |
| sch_iam.tb_user | sch_course_delivery.tb_fac_group_assignment | id | updated_by | fk_fac_group_assignment_updated_by | RESTRICT | CASCADE | YES | m_course_delivery | Aggregation |
| sch_iam.tb_user | sch_course_delivery.tb_stud_crs_registration | id | created_by | fk_stud_crs_registration_created_by | RESTRICT | CASCADE | YES | m_course_delivery | Aggregation |
| sch_iam.tb_user | sch_course_delivery.tb_stud_crs_registration | id | updated_by | fk_stud_crs_registration_updated_by | RESTRICT | CASCADE | YES | m_course_delivery | Aggregation |
| sch_iam.tb_user | sch_employee.tb_department_assignment | id | updated_by | fk_department_assignment_updated_by | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_iam.tb_user | sch_employee.tb_department_assignment | id | created_by | fk_department_assignment_created_by | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_iam.tb_user | sch_employee.tb_emp | id | user_id | fk_emp_user | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_iam.tb_user | sch_employee.tb_emp | id | updated_by | fk_emp_updated_by | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_iam.tb_user | sch_employee.tb_emp | id | created_by | fk_emp_created_by | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_iam.tb_user | sch_employee.tb_emp_exp | id | updated_by | fk_emp_exp_updated_by | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_iam.tb_user | sch_employee.tb_emp_exp | id | created_by | fk_emp_exp_created_by | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_iam.tb_user | sch_employee.tb_emp_profile | id | updated_by | fk_emp_profile_updated_by | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_iam.tb_user | sch_employee.tb_emp_profile | id | created_by | fk_emp_profile_created_by | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_iam.tb_user | sch_employee.tb_emp_qual | id | updated_by | fk_emp_qual_updated_by | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_iam.tb_user | sch_employee.tb_emp_qual | id | created_by | fk_emp_qual_created_by | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_iam.tb_user | sch_employee.tb_employment | id | created_by | fk_employment_created_by | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_iam.tb_user | sch_employee.tb_employment | id | updated_by | fk_employment_updated_by | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_iam.tb_user | sch_employee.tb_employment_history | id | created_by | fk_employment_history_created_by | RESTRICT | CASCADE | YES | m_employee | Historical |
| sch_iam.tb_user | sch_employee.tb_employment_history | id | updated_by | fk_employment_history_updated_by | RESTRICT | CASCADE | YES | m_employee | Historical |
| sch_iam.tb_user | sch_employee.tb_fac | id | updated_by | fk_fac_updated_by | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_iam.tb_user | sch_employee.tb_fac | id | created_by | fk_fac_created_by | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_iam.tb_user | sch_employee.tb_fac_acad_assignment | id | created_by | fk_fac_acad_assignment_created_by | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_iam.tb_user | sch_employee.tb_fac_acad_assignment | id | updated_by | fk_fac_acad_assignment_updated_by | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_iam.tb_user | sch_employee.tb_fac_advisor_assignment | id | created_by | fk_fac_advisor_assignment_created_by | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_iam.tb_user | sch_employee.tb_fac_advisor_assignment | id | updated_by | fk_fac_advisor_assignment_updated_by | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_iam.tb_user | sch_employee.tb_fac_certification | id | created_by | fk_fac_cert_created_by | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_iam.tb_user | sch_employee.tb_fac_certification | id | updated_by | fk_fac_cert_updated_by | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_iam.tb_user | sch_employee.tb_fac_profile | id | updated_by | fk_fac_profile_updated_by | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_iam.tb_user | sch_employee.tb_fac_profile | id | created_by | fk_fac_profile_created_by | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_iam.tb_user | sch_employee.tb_rpting_manager | id | updated_by | fk_rpting_manager_updated_by | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_iam.tb_user | sch_employee.tb_rpting_manager | id | created_by | fk_rpting_manager_created_by | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_iam.tb_user | sch_examination.tb_exam | id | updated_by | fk_exam_updated_by | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_iam.tb_user | sch_examination.tb_exam | id | created_by | fk_exam_created_by | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_iam.tb_user | sch_examination.tb_exam_att | id | created_by | fk_exam_att_created_by | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_iam.tb_user | sch_examination.tb_exam_att | id | updated_by | fk_exam_att_updated_by | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_iam.tb_user | sch_examination.tb_exam_evaluation | id | created_by | fk_exam_evaluation_created_by | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_iam.tb_user | sch_examination.tb_exam_evaluation | id | updated_by | fk_exam_evaluation_updated_by | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_iam.tb_user | sch_examination.tb_exam_final_mark | id | created_by | fk_exam_final_created_by | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_iam.tb_user | sch_examination.tb_exam_final_mark | id | updated_by | fk_exam_final_updated_by | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_iam.tb_user | sch_examination.tb_exam_malpractice | id | created_by | fk_exam_malpractice_created_by | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_iam.tb_user | sch_examination.tb_exam_malpractice | id | updated_by | fk_exam_malpractice_updated_by | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_iam.tb_user | sch_examination.tb_exam_moderation | id | updated_by | fk_exam_mod_updated_by | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_iam.tb_user | sch_examination.tb_exam_moderation | id | created_by | fk_exam_mod_created_by | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_iam.tb_user | sch_examination.tb_exam_registration | id | updated_by | fk_exam_registration_updated_by | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_iam.tb_user | sch_examination.tb_exam_registration | id | created_by | fk_exam_registration_created_by | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_iam.tb_user | sch_examination.tb_exam_room | id | updated_by | fk_exam_room_updated_by | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_iam.tb_user | sch_examination.tb_exam_room | id | created_by | fk_exam_room_created_by | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_iam.tb_user | sch_examination.tb_exam_room_invigilator | id | created_by | fk_invigilator_created_by | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_iam.tb_user | sch_examination.tb_exam_room_invigilator | id | updated_by | fk_invigilator_updated_by | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_iam.tb_user | sch_examination.tb_exam_script | id | created_by | fk_exam_script_created_by | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_iam.tb_user | sch_examination.tb_exam_script | id | updated_by | fk_exam_script_updated_by | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_iam.tb_user | sch_examination.tb_exam_session | id | updated_by | fk_exam_session_updated_by | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_iam.tb_user | sch_examination.tb_exam_session | id | created_by | fk_exam_session_created_by | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_iam.tb_user | sch_examination.tb_hall_ticket | id | created_by | fk_hall_ticket_created_by | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_iam.tb_user | sch_examination.tb_hall_ticket | id | updated_by | fk_hall_ticket_updated_by | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_iam.tb_user | sch_fees.tb_concession | id | updated_by | fk_concession_updated_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_concession | id | approved_by | fk_concession_approved_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_concession | id | created_by | fk_concession_created_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_fee_structure | id | updated_by | fk_fee_structure_updated_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_fee_structure | id | created_by | fk_fee_structure_created_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_fee_structure_component | id | updated_by | fk_fee_component_updated_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_fee_structure_component | id | created_by | fk_fee_component_created_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_fee_structure_rule | id | updated_by | fk_fee_rule_updated_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_fee_structure_rule | id | created_by | fk_fee_rule_created_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_fee_waiver | id | created_by | fk_waiver_created_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_fee_waiver | id | updated_by | fk_waiver_updated_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_fee_waiver | id | approved_by | fk_waiver_approved_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_financial_hold | id | created_by | fk_financial_hold_created_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_financial_hold | id | updated_by | fk_financial_hold_updated_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_financial_hold | id | released_by | fk_financial_hold_released_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_financial_ledger | id | created_by | fk_ledger_created_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_financial_ledger | id | updated_by | fk_ledger_updated_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_installment_plan | id | updated_by | fk_installment_plan_updated_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_installment_plan | id | created_by | fk_installment_plan_created_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_installment_plan_detail | id | created_by | fk_installment_detail_created_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_installment_plan_detail | id | updated_by | fk_installment_detail_updated_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_payment | id | updated_by | fk_payment_updated_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_payment | id | created_by | fk_payment_created_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_payment_allocation | id | updated_by | fk_payment_alloc_updated_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_payment_allocation | id | created_by | fk_payment_alloc_created_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_payment_gateway_transaction | id | created_by | fk_gateway_created_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_payment_gateway_transaction | id | updated_by | fk_gateway_updated_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_penalty | id | updated_by | fk_penalty_updated_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_penalty | id | created_by | fk_penalty_created_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_refund | id | updated_by | fk_refund_updated_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_refund | id | approved_by | fk_refund_approved_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_refund | id | created_by | fk_refund_created_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_scholarship | id | updated_by | fk_scholarship_updated_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_scholarship | id | created_by | fk_scholarship_created_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_scholarship | id | approved_by | fk_scholarship_approved_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_stud_fee_asmt | id | updated_by | fk_stud_fee_asmt_updated_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_stud_fee_asmt | id | created_by | fk_stud_fee_asmt_created_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_stud_fee_component | id | updated_by | fk_stud_fee_component_updated_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_stud_fee_component | id | created_by | fk_stud_fee_component_created_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_stud_installment | id | updated_by | fk_stud_installment_updated_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_fees.tb_stud_installment | id | created_by | fk_stud_installment_created_by | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_iam.tb_user | sch_iam.tb_user_address | id | user_id | fk_tb_user_address_user | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_iam.tb_user | sch_iam.tb_user_aud | id | action_by | fk_tb_user_aud_action_by | NO ACTION | NO ACTION | YES | m_iam | Historical |
| sch_iam.tb_user | sch_iam.tb_user_aud | id | user_id | fk_tb_user_aud_user | NO ACTION | NO ACTION | NO | m_iam | Historical |
| sch_iam.tb_user | sch_iam.tb_user_doc | id | user_id | fk_tb_user_doc_user | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_iam.tb_user | sch_iam.tb_user_emergency_contact | id | user_id | fk_tb_user_emergency_contact_user | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_iam.tb_user | sch_iam.tb_user_identifier | id | user_id | fk_tb_user_identifier_user | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_iam.tb_user | sch_iam.tb_user_login | id | user_id | fk_tb_user_login_user | NO ACTION | NO ACTION | NO | m_iam | Historical |
| sch_iam.tb_user | sch_iam.tb_user_med | id | user_id | fk_tb_user_med_user | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_iam.tb_user | sch_iam.tb_user_password_state | id | user_id | fk_tb_user_password_state_user | CASCADE | NO ACTION | NO | m_iam | Composition |
| sch_iam.tb_user | sch_iam.tb_user_preference | id | user_id | fk_tb_user_preference_user | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_iam.tb_user | sch_iam.tb_user_profile | id | user_id | fk_tb_user_profile_user | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_iam.tb_user | sch_iam.tb_user_session | id | user_id | fk_tb_user_session_user | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_iam.tb_user | sch_infra.tb_building | id | updated_by | fk_building_updated_by | RESTRICT | CASCADE | YES | m_infra | Aggregation |
| sch_iam.tb_user | sch_infra.tb_building | id | created_by | fk_building_created_by | RESTRICT | CASCADE | YES | m_infra | Aggregation |
| sch_iam.tb_user | sch_infra.tb_room | id | created_by | fk_room_created_by | RESTRICT | CASCADE | YES | m_infra | Aggregation |
| sch_iam.tb_user | sch_infra.tb_room | id | updated_by | fk_room_updated_by | RESTRICT | CASCADE | YES | m_infra | Aggregation |
| sch_iam.tb_user | sch_infra.tb_room_feature | id | updated_by | fk_room_feature_updated_by | RESTRICT | CASCADE | YES | m_infra | Aggregation |
| sch_iam.tb_user | sch_infra.tb_room_feature | id | created_by | fk_room_feature_created_by | RESTRICT | CASCADE | YES | m_infra | Aggregation |
| sch_iam.tb_user | sch_infra.tb_room_specifications | id | updated_by | fk_room_specifications_updated_by | RESTRICT | CASCADE | YES | m_infra | Aggregation |
| sch_iam.tb_user | sch_infra.tb_room_specifications | id | created_by | fk_room_specifications_created_by | RESTRICT | CASCADE | YES | m_infra | Aggregation |
| sch_iam.tb_user | sch_lms.tb_lms_achievement_award | id | awarded_by | fk_tb_lms_achievement_award_awarded_by | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_iam.tb_user | sch_lms.tb_lms_ai_conversation | id | user_id | fk_tb_lms_ai_conversation_user | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_iam.tb_user | sch_lms.tb_lms_ai_request | id | user_id | fk_tb_lms_ai_request_user | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_iam.tb_user | sch_lms.tb_lms_announcement | id | created_by | fk_tb_lms_announcement_created_by | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_iam.tb_user | sch_lms.tb_lms_badge_award | id | awarded_by | fk_tb_lms_badge_award_awarded_by | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_iam.tb_user | sch_lms.tb_lms_certificate_award | id | awarded_by | fk_tb_lms_certificate_award_awarded_by | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_iam.tb_user | sch_lms.tb_lms_content_approval | id | approved_by | fk_tb_lms_content_approval_user | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_iam.tb_user | sch_lms.tb_lms_content_report | id | reported_by | fk_tb_lms_content_report_user | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_iam.tb_user | sch_lms.tb_lms_content_version | id | published_by | fk_tb_lms_content_version_published_by | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_iam.tb_user | sch_lms.tb_lms_content_version | id | created_by | fk_tb_lms_content_version_created_by | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_iam.tb_user | sch_lms.tb_lms_discussion_reply | id | created_by | fk_tb_lms_discussion_reply_created_by | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_iam.tb_user | sch_lms.tb_lms_discussion_thread | id | created_by | fk_tb_lms_discussion_thread_created_by | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_iam.tb_user | sch_lms.tb_lms_live_chat | id | user_id | fk_tb_lms_live_chat_user | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_iam.tb_user | sch_lms.tb_lms_live_class_attendee | id | user_id | fk_tb_lms_live_class_attendee_user | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_iam.tb_user | sch_lms.tb_lms_live_class_event | id | user_id | fk_tb_lms_live_class_event_user | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_iam.tb_user | sch_lms.tb_lms_operation_log | id | user_id | fk_tb_lms_operation_log_user | RESTRICT | CASCADE | NO | m_lms | Historical |
| sch_iam.tb_user | sch_lms.tb_lms_poll_response | id | user_id | fk_tb_lms_poll_response_user | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_iam.tb_user | sch_lms.tb_lms_qna | id | user_id | fk_tb_lms_qna_user | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_iam.tb_user | sch_lms.tb_lms_qna | id | answered_by | fk_tb_lms_qna_answered_by | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_iam.tb_user | sch_lms.tb_lms_reply_reaction | id | user_id | fk_tb_lms_reply_reaction_user | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_iam.tb_user | sch_lms.tb_lms_submission_comment | id | user_id | fk_tb_lms_submission_comment_user | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_iam.tb_user | sch_lms.tb_lms_submission_history | id | action_by | fk_tb_lms_submission_history_action_by | RESTRICT | CASCADE | NO | m_lms | Historical |
| sch_iam.tb_user | sch_lms.tb_lms_thread_moderation | id | moderated_by | fk_tb_lms_thread_moderation_user | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_iam.tb_user | sch_lms.tb_lms_thread_reaction | id | user_id | fk_tb_lms_thread_reaction_user | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_iam.tb_user | sch_lms.tb_lms_thread_subscription | id | user_id | fk_tb_lms_thread_subscription_user | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_iam.tb_user | sch_lms.tb_lms_workspace_member | id | user_id | fk_tb_lms_workspace_member_user | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_iam.tb_user | sch_org.tb_dept_profile | id | hod_user_id | fk_tb_dept_profile_hod | NO ACTION | NO ACTION | YES | m_org | Aggregation |
| sch_iam.tb_user | sch_org.tb_org_contact | id | user_id | fk_tb_org_contact_user | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_iam.tb_user | sch_rbac.tb_user_org | id | user_id | fk_tb_user_org_user | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_iam.tb_user | sch_rbac.tb_user_role | id | assigned_by | fk_tb_user_role_assigned_by | NO ACTION | NO ACTION | YES | m_iam | Aggregation |
| sch_iam.tb_user | sch_results.tb_crs_res | id | updated_by | fk_crs_res_updated_by | RESTRICT | CASCADE | YES | m_results | Aggregation |
| sch_iam.tb_user | sch_results.tb_crs_res | id | created_by | fk_crs_res_created_by | RESTRICT | CASCADE | YES | m_results | Aggregation |
| sch_iam.tb_user | sch_results.tb_grade_card | id | updated_by | fk_grade_card_updated_by | RESTRICT | CASCADE | YES | m_results | Aggregation |
| sch_iam.tb_user | sch_results.tb_grade_card | id | generated_by | fk_grade_card_generated_by | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_iam.tb_user | sch_results.tb_grade_card | id | created_by | fk_grade_card_created_by | RESTRICT | CASCADE | YES | m_results | Aggregation |
| sch_iam.tb_user | sch_results.tb_prog_res | id | updated_by | fk_prog_res_updated_by | RESTRICT | CASCADE | YES | m_results | Aggregation |
| sch_iam.tb_user | sch_results.tb_prog_res | id | created_by | fk_prog_res_created_by | RESTRICT | CASCADE | YES | m_results | Aggregation |
| sch_iam.tb_user | sch_results.tb_res_policy | id | created_by | fk_res_policy_created_by | RESTRICT | CASCADE | YES | m_results | Aggregation |
| sch_iam.tb_user | sch_results.tb_res_policy | id | updated_by | fk_res_policy_updated_by | RESTRICT | CASCADE | YES | m_results | Aggregation |
| sch_iam.tb_user | sch_results.tb_res_publication | id | updated_by | fk_res_publication_updated_by | RESTRICT | CASCADE | YES | m_results | Aggregation |
| sch_iam.tb_user | sch_results.tb_res_publication | id | created_by | fk_res_publication_created_by | RESTRICT | CASCADE | YES | m_results | Aggregation |
| sch_iam.tb_user | sch_results.tb_term_res | id | updated_by | fk_term_res_updated_by | RESTRICT | CASCADE | YES | m_results | Aggregation |
| sch_iam.tb_user | sch_results.tb_term_res | id | created_by | fk_term_res_created_by | RESTRICT | CASCADE | YES | m_results | Aggregation |
| sch_iam.tb_user | sch_student.tb_stud | id | updated_by | fk_stud_updated_by | RESTRICT | CASCADE | YES | m_student | Aggregation |
| sch_iam.tb_user | sch_student.tb_stud | id | user_id | fk_stud_user | RESTRICT | CASCADE | NO | m_student | Aggregation |
| sch_iam.tb_user | sch_student.tb_stud | id | created_by | fk_stud_created_by | RESTRICT | CASCADE | NO | m_student | Aggregation |
| sch_iam.tb_user | sch_student.tb_stud_exit | id | exit_approved_by | fk_stud_exit_approved_by | RESTRICT | CASCADE | NO | m_student | Aggregation |
| sch_iam.tb_user | sch_student.tb_stud_sec_history | id | approved_by | fk_sec_history_approved_by | RESTRICT | CASCADE | NO | m_student | Historical |
| sch_iam.tb_user | sch_student_leave.tb_student_leave_status_history | id | changed_by | fk_tb_student_leave_status_history_changed_by | RESTRICT | CASCADE | NO | m_student_leave | Historical |
| sch_iam.tb_user | sch_timetable.tb_class_cancellation | id | updated_by | fk_cancel_updated_by | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_iam.tb_user | sch_timetable.tb_class_cancellation | id | cancelled_by | fk_cancel_by | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_iam.tb_user | sch_timetable.tb_class_cancellation | id | created_by | fk_cancel_created_by | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_iam.tb_user | sch_timetable.tb_class_session | id | created_by | fk_class_session_created_by | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_iam.tb_user | sch_timetable.tb_class_session | id | updated_by | fk_class_session_updated_by | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_iam.tb_user | sch_timetable.tb_class_session_change | id | created_by | fk_change_created_by | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_iam.tb_user | sch_timetable.tb_class_session_change | id | updated_by | fk_change_updated_by | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_iam.tb_user | sch_timetable.tb_class_session_change | id | approved_by | fk_change_approved_by | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_iam.tb_user | sch_timetable.tb_class_session_fac | id | updated_by | fk_class_session_fac_updated_by | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_iam.tb_user | sch_timetable.tb_class_session_fac | id | created_by | fk_class_session_fac_created_by | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_iam.tb_user | sch_timetable.tb_class_session_room | id | updated_by | fk_class_session_room_updated_by | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_iam.tb_user | sch_timetable.tb_class_session_room | id | created_by | fk_class_session_room_created_by | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_iam.tb_user | sch_timetable.tb_extra_class | id | created_by | fk_extra_created_by | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_iam.tb_user | sch_timetable.tb_extra_class | id | updated_by | fk_extra_updated_by | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_iam.tb_user | sch_timetable.tb_holiday_adjustment | id | updated_by | fk_holiday_updated_by | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_iam.tb_user | sch_timetable.tb_holiday_adjustment | id | created_by | fk_holiday_created_by | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_iam.tb_user | sch_timetable.tb_time_slot | id | updated_by | fk_time_slot_updated_by | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_iam.tb_user | sch_timetable.tb_time_slot | id | created_by | fk_time_slot_created_by | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_iam.tb_user | sch_timetable.tb_tt | id | created_by | fk_tt_created_by | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_iam.tb_user | sch_timetable.tb_tt | id | updated_by | fk_tt_updated_by | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_iam.tb_user | sch_timetable.tb_tt_entry | id | updated_by | fk_tt_entry_updated_by | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_iam.tb_user | sch_timetable.tb_tt_entry | id | created_by | fk_tt_entry_created_by | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_iam.tb_user | sch_timetable.tb_tt_entry_sec | id | created_by | fk_tt_entry_sec_created_by | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_iam.tb_user | sch_timetable.tb_tt_entry_sec | id | updated_by | fk_tt_entry_sec_updated_by | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_iam.tb_user | sch_timetable.tb_working_day | id | updated_by | fk_working_day_updated_by | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_iam.tb_user | sch_timetable.tb_working_day | id | created_by | fk_working_day_created_by | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_iam.tb_user_grp_type | sch_iam.tb_role | id | user_grp_type_id | fk_tb_role_user_grp_type | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_iam.tb_user_login | sch_iam.tb_user_session | id | login_id | fk_tb_user_session_login | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_iam.tb_user_session | sch_aaa.tb_auth_log | id | session_id | fk_tb_auth_log_session | NO ACTION | NO ACTION | YES | m_AAA | Historical |
| sch_iam.tb_user_session | sch_aaa.tb_mfa_challenge | id | session_id | fk_tb_mfa_challenge_session | NO ACTION | NO ACTION | NO | m_AAA | Aggregation |
| sch_infra.tb_building | sch_infra.tb_room | id | building_id | fk_room_building | RESTRICT | CASCADE | NO | m_infra | Aggregation |
| sch_infra.tb_room | sch_examination.tb_exam_room | id | room_id | fk_exam_room_room | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_infra.tb_room | sch_infra.tb_room_feature | id | room_id | fk_room_feature_room | RESTRICT | CASCADE | NO | m_infra | Aggregation |
| sch_infra.tb_room | sch_infra.tb_room_specifications | id | room_id | fk_room_specifications_room | RESTRICT | CASCADE | NO | m_infra | Aggregation |
| sch_infra.tb_room | sch_timetable.tb_class_session_change | id | new_room_id | fk_change_new_room | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_infra.tb_room | sch_timetable.tb_class_session_change | id | old_room_id | fk_change_old_room | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_infra.tb_room | sch_timetable.tb_class_session_room | id | room_id | fk_class_session_room_room | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_infra.tb_room | sch_timetable.tb_extra_class | id | room_id | fk_extra_room | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_infra.tb_room | sch_timetable.tb_tt_entry | id | room_id | fk_tt_entry_room | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_lms.tb_lms_achievement | sch_lms.tb_lms_achievement_award | id | achievement_id | fk_tb_lms_achievement_award_achievement | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_achievement | sch_lms.tb_lms_achievement_rule | id | achievement_id | fk_tb_lms_achievement_rule_achievement | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_activity_type | sch_lms.tb_lms_content | id | content_type_id | fk_tb_lms_content_type | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_activity_type | sch_lms.tb_lms_learning_activity | id | activity_type_id | fk_tb_lms_learning_activity_type | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_ai_conversation | sch_lms.tb_lms_ai_message | id | conversation_id | fk_tb_lms_ai_message_conversation | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_ai_provider | sch_lms.tb_lms_ai_service | id | provider_id | fk_tb_lms_ai_service_provider | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_ai_provider | sch_lms.tb_lms_content_embedding | id | embedding_provider_id | fk_tb_lms_content_embedding_provider | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_ai_service | sch_lms.tb_lms_ai_conversation | id | service_id | fk_tb_lms_ai_conversation_service | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_ai_service | sch_lms.tb_lms_ai_recommendation | id | generated_by | fk_tb_lms_ai_recommendation_service | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_ai_service | sch_lms.tb_lms_ai_request | id | service_id | fk_tb_lms_ai_request_service | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_announcement | sch_lms.tb_lms_announcement_attachment | id | announcement_id | fk_tb_lms_announcement_attachment_announcement | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_assignment | sch_lms.tb_lms_assignment_attachment | id | assignment_id | fk_tb_lms_assignment_attachment_assignment | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_assignment | sch_lms.tb_lms_assignment_group | id | assignment_id | fk_tb_lms_assignment_group_assignment | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_assignment | sch_lms.tb_lms_assignment_instruction | id | assignment_id | fk_tb_lms_assignment_instruction_assignment | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_assignment | sch_lms.tb_lms_assignment_rubric | id | assignment_id | fk_tb_lms_assignment_rubric_assignment | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_assignment | sch_lms.tb_lms_assignment_submission | id | assignment_id | fk_tb_lms_assignment_submission_assignment | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_assignment_group | sch_lms.tb_lms_assignment_group_member | id | group_id | fk_tb_lms_assignment_group_member_group | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_assignment_rubric | sch_lms.tb_lms_rubric_criteria | id | rubric_id | fk_tb_lms_rubric_criteria_rubric | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_assignment_submission | sch_lms.tb_lms_assignment_grade_view | id | submission_id | fk_tb_lms_assignment_grade_view_submission | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_assignment_submission | sch_lms.tb_lms_assignment_plagiarism | id | submission_id | fk_tb_lms_assignment_plagiarism_submission | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_assignment_submission | sch_lms.tb_lms_submission_comment | id | submission_id | fk_tb_lms_submission_comment_submission | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_assignment_submission | sch_lms.tb_lms_submission_feedback | id | submission_id | fk_tb_lms_submission_feedback_submission | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_assignment_submission | sch_lms.tb_lms_submission_file | id | submission_id | fk_tb_lms_submission_file_submission | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_assignment_submission | sch_lms.tb_lms_submission_history | id | submission_id | fk_tb_lms_submission_history_submission | RESTRICT | CASCADE | NO | m_lms | Historical |
| sch_lms.tb_lms_attempt_response | sch_lms.tb_lms_response_option | id | response_id | fk_tb_lms_response_option_response | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_badge | sch_lms.tb_lms_badge_award | id | badge_id | fk_tb_lms_badge_award_badge | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_badge | sch_lms.tb_lms_badge_rule | id | badge_id | fk_tb_lms_badge_rule_badge | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_certificate | sch_lms.tb_lms_certificate_award | id | certificate_id | fk_tb_lms_certificate_award_certificate | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_certificate | sch_lms.tb_lms_certificate_rule | id | certificate_id | fk_tb_lms_certificate_rule_certificate | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_certificate_template | sch_lms.tb_lms_certificate | id | template_id | fk_tb_lms_certificate_template | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_completion_rule | sch_lms.tb_lms_achievement_rule | id | completion_rule_id | fk_tb_lms_achievement_rule_completion_rule | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_completion_rule | sch_lms.tb_lms_badge_rule | id | completion_rule_id | fk_tb_lms_badge_rule_completion_rule | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_completion_rule | sch_lms.tb_lms_certificate_rule | id | completion_rule_id | fk_tb_lms_certificate_rule_completion_rule | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_content | sch_lms.tb_lms_ai_recommendation | id | content_id | fk_tb_lms_ai_recommendation_content | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_content | sch_lms.tb_lms_bookmark | id | content_id | fk_tb_lms_bookmark_content | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_content | sch_lms.tb_lms_content_approval | id | content_id | fk_tb_lms_content_approval_content | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_content | sch_lms.tb_lms_content_attachment | id | content_id | fk_tb_lms_content_attachment_content | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_content | sch_lms.tb_lms_content_embedding | id | content_id | fk_tb_lms_content_embedding_content | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_content | sch_lms.tb_lms_content_license | id | content_id | fk_tb_lms_content_license_content | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_content | sch_lms.tb_lms_content_metadata | id | content_id | fk_tb_lms_content_metadata_content | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_content | sch_lms.tb_lms_content_release | id | content_id | fk_tb_lms_content_release_content | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_content | sch_lms.tb_lms_content_translation | id | content_id | fk_tb_lms_content_translation_content | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_content | sch_lms.tb_lms_document | id | content_id | fk_tb_lms_document_content | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_content | sch_lms.tb_lms_external_resource | id | content_id | fk_tb_lms_external_resource_content | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_content | sch_lms.tb_lms_favorite | id | content_id | fk_tb_lms_favorite_content | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_content | sch_lms.tb_lms_highlight | id | content_id | fk_tb_lms_highlight_content | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_content | sch_lms.tb_lms_html_content | id | content_id | fk_tb_lms_html_content_content | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_content | sch_lms.tb_lms_learning_event | id | content_id | fk_tb_lms_learning_event_content | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_content | sch_lms.tb_lms_note | id | content_id | fk_tb_lms_note_content | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_content | sch_lms.tb_lms_notebook | id | content_id | fk_tb_lms_notebook_content | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_content | sch_lms.tb_lms_offline_download | id | content_id | fk_tb_lms_offline_download_content | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_content | sch_lms.tb_lms_resume_state | id | content_id | fk_tb_lms_resume_state_content | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_content | sch_lms.tb_lms_scorm_package | id | content_id | fk_tb_lms_scorm_package_content | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_content | sch_lms.tb_lms_simulation | id | content_id | fk_tb_lms_simulation_content | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_content | sch_lms.tb_lms_video | id | content_id | fk_tb_lms_video_content | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_content | sch_lms.tb_lms_xapi_package | id | content_id | fk_tb_lms_xapi_package_content | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_discussion_forum | sch_lms.tb_lms_discussion_thread | id | forum_id | fk_tb_lms_discussion_thread_forum | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_discussion_reply | sch_lms.tb_lms_content_report | id | reply_id | fk_tb_lms_content_report_reply | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lms.tb_lms_discussion_reply | sch_lms.tb_lms_discussion_reply | id | parent_reply_id | fk_tb_lms_discussion_reply_parent | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lms.tb_lms_discussion_reply | sch_lms.tb_lms_reply_attachment | id | reply_id | fk_tb_lms_reply_attachment_reply | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_discussion_reply | sch_lms.tb_lms_reply_reaction | id | reply_id | fk_tb_lms_reply_reaction_reply | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_discussion_thread | sch_lms.tb_lms_content_report | id | thread_id | fk_tb_lms_content_report_thread | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lms.tb_lms_discussion_thread | sch_lms.tb_lms_discussion_reply | id | thread_id | fk_tb_lms_discussion_reply_thread | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_discussion_thread | sch_lms.tb_lms_thread_attachment | id | thread_id | fk_tb_lms_thread_attachment_thread | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_discussion_thread | sch_lms.tb_lms_thread_moderation | id | thread_id | fk_tb_lms_thread_moderation_thread | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_discussion_thread | sch_lms.tb_lms_thread_reaction | id | thread_id | fk_tb_lms_thread_reaction_thread | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_discussion_thread | sch_lms.tb_lms_thread_subscription | id | thread_id | fk_tb_lms_thread_subscription_thread | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_document | sch_lms.tb_lms_document_progress | id | document_id | fk_tb_lms_document_progress_document | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_learning_activity | sch_lms.tb_lms_activity_progress | id | activity_id | fk_tb_lms_activity_progress_activity | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_learning_activity | sch_lms.tb_lms_activity_sequence | id | activity_id | fk_tb_lms_activity_sequence_activity | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_learning_activity | sch_lms.tb_lms_activity_sequence | id | next_activity_id | fk_tb_lms_activity_sequence_next_activity | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lms.tb_lms_learning_activity | sch_lms.tb_lms_activity_sequence | id | previous_activity_id | fk_tb_lms_activity_sequence_previous_activity | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lms.tb_lms_learning_activity | sch_lms.tb_lms_content | id | activity_id | fk_tb_lms_content_activity | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_learning_activity | sch_lms.tb_lms_library_resource | id | activity_id | fk_tb_lms_library_resource_activity | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lms.tb_lms_learning_event | sch_lms.tb_lms_activity_log | id | event_id | fk_tb_lms_activity_log_event | RESTRICT | CASCADE | NO | m_lms | Historical |
| sch_lms.tb_lms_learning_module | sch_lms.tb_lms_topic | id | module_id | fk_tb_lms_topic_module | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_learning_session | sch_lms.tb_lms_learning_event | id | session_id | fk_tb_lms_learning_event_session | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lms.tb_lms_lesson | sch_lms.tb_lms_assignment | id | lesson_id | fk_tb_lms_assignment_lesson | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_lesson | sch_lms.tb_lms_learning_activity | id | lesson_id | fk_tb_lms_learning_activity_lesson | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_lesson | sch_lms.tb_lms_lesson_progress | id | lesson_id | fk_tb_lms_lesson_progress_lesson | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_lesson | sch_lms.tb_lms_live_class | id | lesson_id | fk_tb_lms_live_class_lesson | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_lesson | sch_lms.tb_lms_quiz | id | lesson_id | fk_tb_lms_quiz_lesson | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_library_resource | sch_lms.tb_lms_content_version | id | resource_id | fk_tb_lms_content_version_resource | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_library_resource | sch_lms.tb_lms_resource_tag_map | id | resource_id | fk_tb_lms_resource_tag_map_resource | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_live_class | sch_lms.tb_lms_live_chat | id | live_class_id | fk_tb_lms_live_chat_live_class | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_live_class | sch_lms.tb_lms_live_class_attendee | id | live_class_id | fk_tb_lms_live_class_attendee_live_class | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_live_class | sch_lms.tb_lms_live_class_event | id | live_class_id | fk_tb_lms_live_class_event_live_class | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_live_class | sch_lms.tb_lms_meeting | id | live_class_id | fk_tb_lms_meeting_live_class | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_live_class | sch_lms.tb_lms_poll | id | live_class_id | fk_tb_lms_poll_live_class | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_live_class | sch_lms.tb_lms_qna | id | live_class_id | fk_tb_lms_qna_live_class | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_live_class | sch_lms.tb_lms_recording | id | live_class_id | fk_tb_lms_recording_live_class | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_meeting_provider | sch_lms.tb_lms_live_class | id | provider_id | fk_tb_lms_live_class_provider | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_poll | sch_lms.tb_lms_poll_option | id | poll_id | fk_tb_lms_poll_option_poll | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_poll | sch_lms.tb_lms_poll_response | id | poll_id | fk_tb_lms_poll_response_poll | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_poll_option | sch_lms.tb_lms_poll_response | id | option_id | fk_tb_lms_poll_response_option | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_question | sch_lms.tb_lms_attempt_response | id | question_id | fk_tb_lms_attempt_response_question | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_question | sch_lms.tb_lms_matching_pair | id | question_id | fk_tb_lms_matching_pair_question | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_question | sch_lms.tb_lms_ordering_item | id | question_id | fk_tb_lms_ordering_item_question | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_question | sch_lms.tb_lms_pool_question | id | question_id | fk_tb_lms_pool_question_question | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_question | sch_lms.tb_lms_question_attachment | id | question_id | fk_tb_lms_question_attachment_question | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_question | sch_lms.tb_lms_question_explanation | id | question_id | fk_tb_lms_question_explanation_question | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_question | sch_lms.tb_lms_question_hint | id | question_id | fk_tb_lms_question_hint_question | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_question | sch_lms.tb_lms_question_option | id | question_id | fk_tb_lms_question_option_question | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_question | sch_lms.tb_lms_quiz_question | id | question_id | fk_tb_lms_quiz_question_question | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_question_bank | sch_lms.tb_lms_question | id | question_bank_id | fk_tb_lms_question_bank | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_question_bank | sch_lms.tb_lms_question_category | id | question_bank_id | fk_tb_lms_question_category_bank | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_question_bank | sch_lms.tb_lms_question_pool | id | question_bank_id | fk_tb_lms_question_pool_bank | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_question_category | sch_lms.tb_lms_question | id | category_id | fk_tb_lms_question_category | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_question_option | sch_lms.tb_lms_response_option | id | option_id | fk_tb_lms_response_option_option | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_question_pool | sch_lms.tb_lms_pool_question | id | pool_id | fk_tb_lms_pool_question_pool | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_question_type | sch_lms.tb_lms_question | id | question_type_id | fk_tb_lms_question_type | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_quiz | sch_lms.tb_lms_quiz_analytics | id | quiz_id | fk_tb_lms_quiz_analytics_quiz | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_quiz | sch_lms.tb_lms_quiz_attempt | id | quiz_id | fk_tb_lms_quiz_attempt_quiz | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_quiz | sch_lms.tb_lms_quiz_feedback | id | quiz_id | fk_tb_lms_quiz_feedback_quiz | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_quiz | sch_lms.tb_lms_quiz_question | id | quiz_id | fk_tb_lms_quiz_question_quiz | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_quiz_attempt | sch_lms.tb_lms_attempt_response | id | attempt_id | fk_tb_lms_attempt_response_attempt | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_resource_library | sch_lms.tb_lms_library_resource | id | library_id | fk_tb_lms_library_resource_library | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_resource_tag | sch_lms.tb_lms_resource_tag_map | id | tag_id | fk_tb_lms_resource_tag_map_tag | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_submission_feedback | sch_lms.tb_lms_feedback_attachment | id | feedback_id | fk_tb_lms_feedback_attachment_feedback | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_topic | sch_lms.tb_lms_lesson | id | topic_id | fk_tb_lms_lesson_topic | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_video | sch_lms.tb_lms_recording | id | video_id | fk_tb_lms_recording_video | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_video | sch_lms.tb_lms_video_caption | id | video_id | fk_tb_lms_video_caption_video | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_video | sch_lms.tb_lms_video_progress | id | video_id | fk_tb_lms_video_progress_video | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_workspace | sch_lms.tb_lms_achievement | id | workspace_id | fk_tb_lms_achievement_workspace | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_workspace | sch_lms.tb_lms_ai_conversation | id | workspace_id | fk_tb_lms_ai_conversation_workspace | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_workspace | sch_lms.tb_lms_ai_request | id | workspace_id | fk_tb_lms_ai_request_workspace | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_workspace | sch_lms.tb_lms_announcement | id | workspace_id | fk_tb_lms_announcement_workspace | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_workspace | sch_lms.tb_lms_assignment | id | workspace_id | fk_tb_lms_assignment_workspace | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_workspace | sch_lms.tb_lms_badge | id | workspace_id | fk_tb_lms_badge_workspace | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_workspace | sch_lms.tb_lms_certificate | id | workspace_id | fk_tb_lms_certificate_workspace | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_workspace | sch_lms.tb_lms_course_progress | id | workspace_id | fk_tb_lms_course_progress_workspace | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_workspace | sch_lms.tb_lms_discussion_forum | id | workspace_id | fk_tb_lms_discussion_forum_workspace | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_workspace | sch_lms.tb_lms_enrollment | id | workspace_id | fk_tb_lms_enrollment_workspace | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_workspace | sch_lms.tb_lms_learning_module | id | workspace_id | fk_tb_lms_learning_module_workspace | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_workspace | sch_lms.tb_lms_learning_session | id | workspace_id | fk_tb_lms_learning_session_workspace | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_workspace | sch_lms.tb_lms_live_class | id | workspace_id | fk_tb_lms_live_class_workspace | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_workspace | sch_lms.tb_lms_operation_log | id | workspace_id | fk_tb_lms_operation_log_workspace | RESTRICT | CASCADE | NO | m_lms | Historical |
| sch_lms.tb_lms_workspace | sch_lms.tb_lms_question_bank | id | workspace_id | fk_tb_lms_question_bank_workspace | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_workspace | sch_lms.tb_lms_quiz | id | workspace_id | fk_tb_lms_quiz_workspace | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_workspace | sch_lms.tb_lms_visibility_rule | id | workspace_id | fk_tb_lms_visibility_rule_workspace | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_workspace | sch_lms.tb_lms_workspace_member | id | workspace_id | fk_tb_lms_workspace_member_workspace | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_workspace | sch_lms.tb_lms_workspace_profile | id | workspace_id | fk_tb_lms_workspace_profile_workspace | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_workspace_role | sch_lms.tb_lms_role_permission | id | role_id | fk_tb_lms_role_permission_role | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lms.tb_lms_workspace_role | sch_lms.tb_lms_workspace_member | id | role_id | fk_tb_lms_workspace_member_role | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_aaa.tb_account_lock | id | lock_reason_id | fk_tb_account_lock_reason | NO ACTION | NO ACTION | NO | m_AAA | Aggregation |
| sch_lookup.tb_lookup | sch_aaa.tb_account_lock | id | unlock_reason_id | fk_tb_account_unlock_reason | NO ACTION | NO ACTION | YES | m_AAA | Aggregation |
| sch_lookup.tb_lookup | sch_aaa.tb_auth_log | id | failure_reason_id | fk_tb_auth_log_failure_reason | NO ACTION | NO ACTION | YES | m_AAA | Historical |
| sch_lookup.tb_lookup | sch_aaa.tb_auth_log | id | evt_status_id | fk_tb_auth_log_evt_status | NO ACTION | NO ACTION | NO | m_AAA | Historical |
| sch_lookup.tb_lookup | sch_aaa.tb_auth_log | id | evt_type_id | fk_tb_auth_log_evt_type | NO ACTION | NO ACTION | NO | m_AAA | Historical |
| sch_lookup.tb_lookup | sch_aaa.tb_mfa_challenge | id | status_id | fk_tb_mfa_challenge_status | NO ACTION | NO ACTION | NO | m_AAA | Aggregation |
| sch_lookup.tb_lookup | sch_aaa.tb_mfa_method | id | mfa_type_id | fk_tb_mfa_method_type | NO ACTION | NO ACTION | NO | m_AAA | Aggregation |
| sch_lookup.tb_lookup | sch_aaa.tb_password_reset | id | status_id | fk_tb_password_reset_status | NO ACTION | NO ACTION | NO | m_AAA | Aggregation |
| sch_lookup.tb_lookup | sch_academic_struct.tb_acad_calendar | id | event_type_id | fk_acad_calendar_event_type | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_lookup.tb_lookup | sch_academic_struct.tb_acad_calendar | id | status_id | fk_acad_calendar_status | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_lookup.tb_lookup | sch_academic_struct.tb_acad_term | id | term_type_id | fk_acad_term_type | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_lookup.tb_lookup | sch_academic_struct.tb_acad_term | id | status_id | fk_acad_term_status | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_lookup.tb_lookup | sch_academic_struct.tb_acad_year | id | status_id | fk_acad_year_status | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_lookup.tb_lookup | sch_academic_struct.tb_batch | id | status_id | fk_batch_status | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_lookup.tb_lookup | sch_academic_struct.tb_crs | id | crs_type_id | fk_crs_type | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_lookup.tb_lookup | sch_academic_struct.tb_crs | id | status_id | fk_crs_status | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_lookup.tb_lookup | sch_academic_struct.tb_crs_corequisite | id | status_id | fk_crs_coreq_status | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_lookup.tb_lookup | sch_academic_struct.tb_crs_prerequisite | id | status_id | fk_crs_prereq_status | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_lookup.tb_lookup | sch_academic_struct.tb_crs_version | id | status_id | fk_crs_version_status | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_lookup.tb_lookup | sch_academic_struct.tb_curr | id | status_id | fk_curr_status | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_lookup.tb_lookup | sch_academic_struct.tb_curr_term | id | status_id | fk_curr_term_status | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_lookup.tb_lookup | sch_academic_struct.tb_curr_term_crs | id | status_id | fk_curr_term_crs_status | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_lookup.tb_lookup | sch_academic_struct.tb_curr_version | id | status_id | fk_curr_version_status | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_lookup.tb_lookup | sch_academic_struct.tb_elective_group | id | status_id | fk_elective_group_status | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_lookup.tb_lookup | sch_academic_struct.tb_elective_group_crs | id | status_id | fk_elective_group_crs_status | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_lookup.tb_lookup | sch_academic_struct.tb_prog | id | status_id | fk_prog_status | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_lookup.tb_lookup | sch_academic_struct.tb_prog | id | prog_type_id | fk_prog_type | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_lookup.tb_lookup | sch_academic_struct.tb_prog | id | duration_unit_id | fk_prog_duration_unit | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_lookup.tb_lookup | sch_academic_struct.tb_sec | id | status_id | fk_sec_status | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_adm | id | status_id | fk_adm_status | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_adm_cycle | id | status_id | fk_adm_cycle_status | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_adm_deferral | id | reason_id | fk_deferral_reason | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_adm_offer | id | status_id | fk_adm_offer_status | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_adm_round | id | status_id | fk_adm_round_status | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_adm_window | id | status_id | fk_adm_window_status | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_applicant | id | status_id | fk_applicant_status | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_applicant_source | id | source_type_id | fk_applicant_source_type | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_application | id | current_status_id | fk_application_status | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_application_asmt | id | status_id | fk_app_asmt_status | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_application_asmt | id | asmt_type_id | fk_app_asmt_type | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_application_doc | id | doc_type_id | fk_app_doc_type | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_application_doc | id | status_id | fk_app_doc_status | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_application_eligibility | id | eligibility_status_id | fk_app_eligibility_status | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_application_evt | id | evt_type_id | fk_app_evt_type | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_application_note | id | note_type_id | fk_app_note_type | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_application_status_history | id | status_id | fk_app_status_history_status | RESTRICT | CASCADE | NO | m_admission | Historical |
| sch_lookup.tb_lookup | sch_admission.tb_application_verification | id | status_id | fk_app_verify_status | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_application_withdrawal | id | reason_id | fk_application_withdrawal_reason | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_asmt_res | id | res_status_id | fk_asmt_res_status | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_doc_verification | id | verification_status_id | fk_doc_verify_status | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_eligibility_criteria_res | id | criteria_id | fk_eligibility_criteria | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_eligibility_criteria_res | id | result_id | fk_eligibility_status | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_merit_list | id | status_id | fk_merit_list_status | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_merit_list | id | category_id | fk_merit_list_category | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_merit_list_entry | id | status_id | fk_merit_entry_status | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_offer_response | id | response_status_id | fk_offer_response_status | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_prog_intake | id | status_id | fk_prog_intake_status | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_prog_intake_category | id | category_id | fk_category | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_seat_allocation | id | status_id | fk_seat_allocation_status | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_selection_decision | id | decision_status_id | fk_selection_decision_status | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_admission.tb_waitlist | id | status_id | fk_waitlist_status | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_lookup.tb_lookup | sch_assessment.tb_asmt | id | status_id | fk_asmt_status | RESTRICT | CASCADE | NO | m_assessment | Aggregation |
| sch_lookup.tb_lookup | sch_assessment.tb_asmt | id | asmt_type_id | fk_asmt_type | RESTRICT | CASCADE | NO | m_assessment | Aggregation |
| sch_lookup.tb_lookup | sch_assessment.tb_asmt | id | evaluation_method_id | fk_asmt_eval_method | RESTRICT | CASCADE | NO | m_assessment | Aggregation |
| sch_lookup.tb_lookup | sch_assessment.tb_asmt_component | id | component_type_id | fk_asmt_component_type | RESTRICT | CASCADE | NO | m_assessment | Aggregation |
| sch_lookup.tb_lookup | sch_assessment.tb_asmt_submission | id | submission_status_id | fk_asmt_submission_status | RESTRICT | CASCADE | NO | m_assessment | Aggregation |
| sch_lookup.tb_lookup | sch_assessment.tb_rubric | id | status_id | fk_rubric_status | RESTRICT | CASCADE | NO | m_assessment | Aggregation |
| sch_lookup.tb_lookup | sch_attendance.tb_att_correction | id | new_status_id | fk_att_corr_new_status | RESTRICT | CASCADE | NO | m_attendance | Aggregation |
| sch_lookup.tb_lookup | sch_attendance.tb_att_correction | id | status_id | fk_att_corr_status | RESTRICT | CASCADE | NO | m_attendance | Aggregation |
| sch_lookup.tb_lookup | sch_attendance.tb_att_correction | id | correction_reason_id | fk_att_corr_reason | RESTRICT | CASCADE | NO | m_attendance | Aggregation |
| sch_lookup.tb_lookup | sch_attendance.tb_att_correction | id | old_status_id | fk_att_corr_old_status | RESTRICT | CASCADE | NO | m_attendance | Aggregation |
| sch_lookup.tb_lookup | sch_attendance.tb_att_record | id | att_status_id | fk_att_record_status | RESTRICT | CASCADE | NO | m_attendance | Aggregation |
| sch_lookup.tb_lookup | sch_attendance.tb_att_session | id | status_id | fk_att_session_status | RESTRICT | CASCADE | NO | m_attendance | Aggregation |
| sch_lookup.tb_lookup | sch_core.tb_address | id | addr_type_id | fk_tb_address_type | NO ACTION | NO ACTION | NO | m_core | Aggregation |
| sch_lookup.tb_lookup | sch_core.tb_city | id | city_type_id | fk_tb_city_type | NO ACTION | NO ACTION | YES | m_core | Aggregation |
| sch_lookup.tb_lookup | sch_core.tb_currency | id | status_id | fk_tb_currency_status | NO ACTION | NO ACTION | NO | m_core | Aggregation |
| sch_lookup.tb_lookup | sch_core.tb_dms | id | status_id | fk_tb_dms_status | NO ACTION | NO ACTION | NO | m_core | Aggregation |
| sch_lookup.tb_lookup | sch_core.tb_dms | id | doc_type_id | fk_tb_dms_doc_type | NO ACTION | NO ACTION | NO | m_core | Aggregation |
| sch_lookup.tb_lookup | sch_course_delivery.tb_acad_evt | id | status_id | fk_acad_evt_status | RESTRICT | CASCADE | NO | m_course_delivery | Aggregation |
| sch_lookup.tb_lookup | sch_course_delivery.tb_acad_evt | id | evt_type_id | fk_acad_evt_type | RESTRICT | CASCADE | NO | m_course_delivery | Aggregation |
| sch_lookup.tb_lookup | sch_course_delivery.tb_crs_offering | id | delivery_status_id | fk_crs_offering_status | RESTRICT | CASCADE | NO | m_course_delivery | Aggregation |
| sch_lookup.tb_lookup | sch_course_delivery.tb_crs_offering | id | delivery_mode_id | fk_crs_offering_mode | RESTRICT | CASCADE | NO | m_course_delivery | Aggregation |
| sch_lookup.tb_lookup | sch_course_delivery.tb_crs_offering_group | id | status_id | fk_crs_offering_group_status | RESTRICT | CASCADE | NO | m_course_delivery | Aggregation |
| sch_lookup.tb_lookup | sch_course_delivery.tb_crs_offering_group | id | group_type_id | fk_crs_offering_group_type | RESTRICT | CASCADE | NO | m_course_delivery | Aggregation |
| sch_lookup.tb_lookup | sch_course_delivery.tb_crs_offering_status_history | id | status_id | fk_crs_offering_status_history_status | RESTRICT | CASCADE | NO | m_course_delivery | Historical |
| sch_lookup.tb_lookup | sch_course_delivery.tb_fac_crs_assignment | id | assignment_role_id | fk_fac_crs_assignment_role | RESTRICT | CASCADE | NO | m_course_delivery | Aggregation |
| sch_lookup.tb_lookup | sch_course_delivery.tb_fac_crs_assignment | id | assignment_status_id | fk_fac_crs_assignment_status | RESTRICT | CASCADE | NO | m_course_delivery | Aggregation |
| sch_lookup.tb_lookup | sch_course_delivery.tb_fac_group_assignment | id | role_assignment_id | fk_fac_group_assignment_role | RESTRICT | CASCADE | NO | m_course_delivery | Aggregation |
| sch_lookup.tb_lookup | sch_course_delivery.tb_stud_crs_registration | id | registration_status_id | fk_stud_crs_registration_status | RESTRICT | CASCADE | NO | m_course_delivery | Aggregation |
| sch_lookup.tb_lookup | sch_employee.tb_department_assignment | id | status_id | fk_department_assignment_status | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_lookup.tb_lookup | sch_employee.tb_emp | id | emp_type_id | fk_emp_type | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_lookup.tb_lookup | sch_employee.tb_emp | id | status_id | fk_emp_status | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_lookup.tb_lookup | sch_employee.tb_emp_exp | id | industry_type_id | fk_emp_exp_industry | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_lookup.tb_lookup | sch_employee.tb_emp_exp | id | reason_for_leaving_id | fk_emp_exp_reason | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_lookup.tb_lookup | sch_employee.tb_emp_qual | id | qual_type_id | fk_emp_qual_type | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_lookup.tb_lookup | sch_employee.tb_emp_qual | id | grade_type_id | fk_emp_grade_type | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_lookup.tb_lookup | sch_employee.tb_employment | id | employment_category_id | fk_employment_category | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_lookup.tb_lookup | sch_employee.tb_employment | id | employment_type_id | fk_employment_type | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_lookup.tb_lookup | sch_employee.tb_employment | id | status_id | fk_employment_status | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_lookup.tb_lookup | sch_employee.tb_employment_history | id | evt_type_id | fk_employment_history_event | RESTRICT | CASCADE | NO | m_employee | Historical |
| sch_lookup.tb_lookup | sch_employee.tb_fac | id | acad_rank_id | fk_fac_rank | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_lookup.tb_lookup | sch_employee.tb_fac | id | fac_type_id | fk_fac_type | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_lookup.tb_lookup | sch_employee.tb_fac | id | status_id | fk_fac_status | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_lookup.tb_lookup | sch_employee.tb_fac_acad_assignment | id | status_id | fk_fac_acad_assignment_status | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_lookup.tb_lookup | sch_employee.tb_fac_advisor_assignment | id | status_id | fk_fac_advisor_assignment_status | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_lookup.tb_lookup | sch_employee.tb_fac_certification | id | status_id | fk_fac_cert_status | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_lookup.tb_lookup | sch_employee.tb_fac_certification | id | issuing_org_id | fk_fac_cert_issuer | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_lookup.tb_lookup | sch_employee.tb_fac_certification | id | certification_type_id | fk_fac_cert_type | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_lookup.tb_lookup | sch_employee.tb_fac_profile | id | area_of_interest_id | fk_fac_profile_area | RESTRICT | CASCADE | YES | m_employee | Aggregation |
| sch_lookup.tb_lookup | sch_employee.tb_rpting_manager | id | rpting_type_id | fk_rpting_manager_type | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_lookup.tb_lookup | sch_examination.tb_exam | id | status_id | fk_exam_status | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_lookup.tb_lookup | sch_examination.tb_exam_att | id | att_status_id | fk_exam_att_status | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_lookup.tb_lookup | sch_examination.tb_exam_evaluation | id | status_id | fk_exam_evaluation_status | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_lookup.tb_lookup | sch_examination.tb_exam_final_mark | id | status_id | fk_exam_final_status | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_lookup.tb_lookup | sch_examination.tb_exam_malpractice | id | status_id | fk_exam_malpractice_status | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_lookup.tb_lookup | sch_examination.tb_exam_malpractice | id | malpractice_type_id | fk_exam_malpractice_type | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_lookup.tb_lookup | sch_examination.tb_exam_malpractice | id | action_taken_id | fk_exam_malpractice_action | RESTRICT | CASCADE | YES | m_examination | Aggregation |
| sch_lookup.tb_lookup | sch_examination.tb_exam_moderation | id | status_id | fk_exam_mod_status | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_lookup.tb_lookup | sch_examination.tb_exam_moderation | id | moderation_reason_id | fk_exam_mod_reason | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_lookup.tb_lookup | sch_examination.tb_exam_registration | id | status_id | fk_exam_registration_status | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_lookup.tb_lookup | sch_examination.tb_exam_registration | id | registration_mode_id | fk_exam_registration_mode | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_lookup.tb_lookup | sch_examination.tb_exam_room_invigilator | id | status_id | fk_invigilator_status | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_lookup.tb_lookup | sch_examination.tb_exam_script | id | status_id | fk_exam_script_status | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_lookup.tb_lookup | sch_examination.tb_exam_session | id | status_id | fk_exam_session_status | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_lookup.tb_lookup | sch_examination.tb_exam_session | id | exam_session_type_id | fk_exam_session_type | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_lookup.tb_lookup | sch_examination.tb_hall_ticket | id | status_id | fk_hall_ticket_status | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_concession | id | status_id | fk_concession_status | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_concession | id | approval_status_id | fk_concession_approval_status | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_concession | id | concession_type_id | fk_concession_type | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_fee_structure | id | status_id | fk_fee_structure_status | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_fee_structure_component | id | fee_category_id | fk_fee_component_category | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_fee_structure_component | id | status_id | fk_fee_component_status | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_fee_structure_rule | id | stud_category_id | fk_fee_rule_stud_category | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_fee_structure_rule | id | status_id | fk_fee_rule_status | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_fee_structure_rule | id | scholarship_category_id | fk_fee_rule_sch_category | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_fee_structure_rule | id | reservation_category_id | fk_fee_rule_res_category | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_fee_structure_rule | id | adm_quota_id | fk_fee_rule_adm_quota | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_fee_waiver | id | waiver_status_id | fk_waiver_status_lookup | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_fee_waiver | id | status_id | fk_waiver_status | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_fee_waiver | id | waiver_type_id | fk_waiver_type | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_financial_hold | id | hold_type_id | fk_financial_hold_type | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_financial_hold | id | hold_status_id | fk_financial_hold_status_lookup | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_financial_hold | id | status_id | fk_financial_hold_status | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_financial_ledger | id | fee_category_id | fk_ledger_fee_category | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_financial_ledger | id | status_id | fk_ledger_status | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_financial_ledger | id | ledger_transaction_type_id | fk_ledger_txn_type | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_installment_plan | id | status_id | fk_installment_plan_status | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_installment_plan_detail | id | status_id | fk_installment_detail_status | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_payment | id | payment_gateway_id | fk_payment_gateway | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_payment | id | payment_status_id | fk_payment_status_lookup | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_payment | id | status_id | fk_payment_status | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_payment | id | payment_source_id | fk_payment_source | RESTRICT | CASCADE | YES | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_payment | id | payment_method_id | fk_payment_method | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_payment_allocation | id | status_id | fk_payment_alloc_status | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_payment_gateway_transaction | id | payment_gateway_id | fk_gateway_provider | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_payment_gateway_transaction | id | status_id | fk_gateway_record_status | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_payment_gateway_transaction | id | gateway_status_id | fk_gateway_status | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_penalty | id | penalty_type_id | fk_penalty_type | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_penalty | id | status_id | fk_penalty_status | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_penalty | id | penalty_status_id | fk_penalty_status_lookup | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_refund | id | refund_status_id | fk_refund_status_lookup | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_refund | id | status_id | fk_refund_status | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_scholarship | id | approval_status_id | fk_scholarship_approval_status | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_scholarship | id | status_id | fk_scholarship_status | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_scholarship | id | scholarship_type_id | fk_scholarship_type | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_stud_fee_asmt | id | status_id | fk_stud_fee_asmt_status | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_stud_fee_asmt | id | asmt_type_id | fk_stud_fee_asmt_type | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_stud_fee_component | id | status_id | fk_stud_fee_component_status | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_fees.tb_stud_installment | id | status_id | fk_stud_installment_status | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_lookup.tb_lookup | sch_iam.tb_role | id | status_id | fk_tb_role_status | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_lookup.tb_lookup | sch_iam.tb_user | id | status_id | fk_tb_user_status | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_lookup.tb_lookup | sch_iam.tb_user_address | id | status_id | fk_tb_user_address_status | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_lookup.tb_lookup | sch_iam.tb_user_aud | id | new_status_id | fk_tb_user_aud_new_status | NO ACTION | NO ACTION | YES | m_iam | Historical |
| sch_lookup.tb_lookup | sch_iam.tb_user_aud | id | old_status_id | fk_tb_user_aud_old_status | NO ACTION | NO ACTION | YES | m_iam | Historical |
| sch_lookup.tb_lookup | sch_iam.tb_user_doc | id | status_id | fk_tb_user_doc_status | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_lookup.tb_lookup | sch_iam.tb_user_emergency_contact | id | status_id | fk_tb_user_emergency_contact_status | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_lookup.tb_lookup | sch_iam.tb_user_grp_type | id | status_id | fk_tb_user_grp_type_status | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_lookup.tb_lookup | sch_iam.tb_user_identifier | id | status_id | fk_tb_user_identifier_status | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_lookup.tb_lookup | sch_iam.tb_user_identifier | id | identifier_type_id | fk_tb_user_identifier_type | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_lookup.tb_lookup | sch_iam.tb_user_login | id | failure_reason_id | fk_tb_user_login_failure | NO ACTION | NO ACTION | YES | m_iam | Historical |
| sch_lookup.tb_lookup | sch_iam.tb_user_login | id | login_method_id | fk_tb_user_login_method | NO ACTION | NO ACTION | NO | m_iam | Historical |
| sch_lookup.tb_lookup | sch_iam.tb_user_login | id | login_status_id | fk_tb_user_login_status | NO ACTION | NO ACTION | NO | m_iam | Historical |
| sch_lookup.tb_lookup | sch_iam.tb_user_med | id | blood_group_id | fk_tb_user_med_blood_group | NO ACTION | NO ACTION | YES | m_iam | Aggregation |
| sch_lookup.tb_lookup | sch_iam.tb_user_med | id | disability_type_id | fk_tb_user_med_disability | NO ACTION | NO ACTION | YES | m_iam | Aggregation |
| sch_lookup.tb_lookup | sch_iam.tb_user_preference | id | preference_type_id | fk_tb_user_preference_type | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_lookup.tb_lookup | sch_iam.tb_user_profile | id | gender_id | fk_tb_user_profile_gender | NO ACTION | NO ACTION | YES | m_iam | Aggregation |
| sch_lookup.tb_lookup | sch_iam.tb_user_profile | id | salutation_id | fk_tb_user_profile_salutation | NO ACTION | NO ACTION | YES | m_iam | Aggregation |
| sch_lookup.tb_lookup | sch_iam.tb_user_profile | id | marital_status_id | fk_tb_user_profile_marital_status | NO ACTION | NO ACTION | YES | m_iam | Aggregation |
| sch_lookup.tb_lookup | sch_iam.tb_user_session | id | device_type_id | fk_tb_user_session_device_type | NO ACTION | NO ACTION | YES | m_iam | Aggregation |
| sch_lookup.tb_lookup | sch_iam.tb_user_session | id | status_id | fk_tb_user_session_status | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_lookup.tb_lookup | sch_infra.tb_building | id | building_type_id | fk_building_type | RESTRICT | CASCADE | NO | m_infra | Aggregation |
| sch_lookup.tb_lookup | sch_infra.tb_room | id | room_type_id | fk_room_type | RESTRICT | CASCADE | NO | m_infra | Aggregation |
| sch_lookup.tb_lookup | sch_infra.tb_room_feature | id | feature_id | fk_room_feature_type | RESTRICT | CASCADE | NO | m_infra | Aggregation |
| sch_lookup.tb_lookup | sch_infra.tb_room_specifications | id | area_unit_id | fk_room_specifications_area_unit | RESTRICT | CASCADE | YES | m_infra | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_achievement | id | achievement_type_id | fk_tb_lms_achievement_type | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_achievement | id | status_id | fk_tb_lms_achievement_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_activity_progress | id | status_id | fk_tb_lms_activity_progress_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_activity_type | id | status_id | fk_tb_lms_activity_type_status | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_ai_conversation | id | status_id | fk_tb_lms_ai_conversation_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_ai_message | id | message_type_id | fk_tb_lms_ai_message_type | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_ai_provider | id | status_id | fk_tb_lms_ai_provider_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_ai_recommendation | id | recommendation_type_id | fk_tb_lms_ai_recommendation_type | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_ai_request | id | request_type_id | fk_tb_lms_ai_request_type | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_ai_request | id | status_id | fk_tb_lms_ai_request_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_ai_service | id | service_type_id | fk_tb_lms_ai_service_type | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_ai_service | id | status_id | fk_tb_lms_ai_service_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_announcement | id | status_id | fk_tb_lms_announcement_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_assignment | id | status_id | fk_tb_lms_assignment_status | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_assignment_plagiarism | id | status_id | fk_tb_lms_assignment_plagiarism_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_assignment_submission | id | status_id | fk_tb_lms_assignment_submission_status | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_badge | id | status_id | fk_tb_lms_badge_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_certificate | id | status_id | fk_tb_lms_certificate_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_certificate_template | id | status_id | fk_tb_lms_certificate_template_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_completion_rule | id | entity_type_id | fk_tb_lms_completion_rule_entity_type | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_completion_rule | id | completion_type_id | fk_tb_lms_completion_rule_completion_type | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_content | id | status_id | fk_tb_lms_content_status | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_content_approval | id | approval_status_id | fk_tb_lms_content_approval_status | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_content_license | id | license_type_id | fk_tb_lms_content_license_type | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_content_release | id | release_type_id | fk_tb_lms_content_release_type | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_content_report | id | report_reason_id | fk_tb_lms_content_report_reason | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_content_report | id | status_id | fk_tb_lms_content_report_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_content_translation | id | language_id | fk_tb_lms_content_translation_language | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_discussion_forum | id | status_id | fk_tb_lms_discussion_forum_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_discussion_forum | id | forum_type_id | fk_tb_lms_discussion_forum_forum_type | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_discussion_reply | id | status_id | fk_tb_lms_discussion_reply_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_discussion_thread | id | status_id | fk_tb_lms_discussion_thread_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_discussion_thread | id | thread_type_id | fk_tb_lms_discussion_thread_thread_type | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_document | id | document_category_id | fk_tb_lms_document_category | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_enrollment | id | status_id | fk_tb_lms_enrollment_status | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_external_resource | id | url_type_id | fk_tb_lms_external_resource_url_type | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_learning_activity | id | status_id | fk_tb_lms_learning_activity_status | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_learning_event | id | event_type_id | fk_tb_lms_learning_event_type | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_learning_module | id | status_id | fk_tb_lms_learning_module_status | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_learning_session | id | device_type_id | fk_tb_lms_learning_session_device | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_learning_session | id | platform_id | fk_tb_lms_learning_session_platform | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_lesson | id | status_id | fk_tb_lms_lesson_status | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_lesson | id | difficulty_level_id | fk_tb_lms_lesson_difficulty_level | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_lesson_progress | id | status_id | fk_tb_lms_lesson_progress_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_library_resource | id | status_id | fk_tb_lms_library_resource_status | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_live_chat | id | status_id | fk_tb_lms_live_chat_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_live_class | id | status_id | fk_tb_lms_live_class_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_live_class_attendee | id | attendance_sync_status_id | fk_tb_lms_live_class_attendee_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_live_class_event | id | event_type_id | fk_tb_lms_live_class_event_type | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_meeting_provider | id | status_id | fk_tb_lms_meeting_provider_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_offline_download | id | sync_status_id | fk_tb_lms_offline_download_sync_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_operation_log | id | event_type_id | fk_tb_lms_operation_log_event_type | RESTRICT | CASCADE | NO | m_lms | Historical |
| sch_lookup.tb_lookup | sch_lms.tb_lms_prerequisite | id | target_entity_type_id | fk_tb_lms_prerequisite_target_entity_type | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_prerequisite | id | prerequisite_type_id | fk_tb_lms_prerequisite_type | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_prerequisite | id | source_entity_type_id | fk_tb_lms_prerequisite_source_entity_type | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_qna | id | status_id | fk_tb_lms_qna_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_question | id | status_id | fk_tb_lms_question_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_question | id | difficulty_level_id | fk_tb_lms_question_difficulty | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_question_bank | id | status_id | fk_tb_lms_question_bank_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_question_type | id | status_id | fk_tb_lms_question_type_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_quiz | id | status_id | fk_tb_lms_quiz_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_quiz_attempt | id | status_id | fk_tb_lms_quiz_attempt_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_release_rule | id | release_type_id | fk_tb_lms_release_rule_release_type | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_release_rule | id | entity_type_id | fk_tb_lms_release_rule_entity_type | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_reply_reaction | id | reaction_type_id | fk_tb_lms_reply_reaction_type | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_resource_library | id | library_type_id | fk_tb_lms_resource_library_library_type | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_resource_library | id | status_id | fk_tb_lms_resource_library_status | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_resource_tag | id | status_id | fk_tb_lms_resource_tag_status | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_role_permission | id | permission_id | fk_tb_lms_role_permission_permission | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_submission_history | id | action_type_id | fk_tb_lms_submission_history_action_type | RESTRICT | CASCADE | NO | m_lms | Historical |
| sch_lookup.tb_lookup | sch_lms.tb_lms_thread_moderation | id | action_type_id | fk_tb_lms_thread_moderation_action_type | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_thread_reaction | id | reaction_type_id | fk_tb_lms_thread_reaction_type | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_topic | id | status_id | fk_tb_lms_topic_status | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_video | id | transcoding_status_id | fk_tb_lms_video_transcoding_status | RESTRICT | CASCADE | YES | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_video | id | status_id | fk_tb_lms_video_status | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_video_caption | id | language_id | fk_tb_lms_video_caption_language | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_visibility_rule | id | visibility_level_id | fk_tb_lms_visibility_rule_level | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_workspace | id | status_id | fk_tb_lms_workspace_status | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_lms.tb_lms_workspace_role | id | status_id | fk_tb_lms_workspace_role_status | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_corp | id | industry_type_id | fk_tb_corp_industry | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_corp | id | status_id | fk_tb_corp_status | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_corp | id | company_size_id | fk_tb_corp_company_size | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_dept | id | dept_type_id | fk_tb_dept_type | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_dept | id | status_id | fk_tb_dept_status | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_dept_accreditation | id | status_id | fk_tb_dept_accreditation_status | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_dept_accreditation | id | accr_type_id | fk_tb_dept_accreditation_type | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_govt_agency | id | govt_level_id | fk_tb_govt_agency_level | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_govt_agency | id | status_id | fk_tb_govt_agency_status | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_inst | id | status_id | fk_tb_inst_status | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_inst | id | inst_type_id | fk_tb_inst_type | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_inst_accr_rank | id | accr_type_id | fk_tb_inst_accr_rank_type | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_inst_accr_rank | id | status_id | fk_tb_inst_accr_rank_status | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_inst_config | id | att_policy_type_id | fk_tb_inst_config_att_policy | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_inst_config | id | acad_cal_type_id | fk_tb_inst_config_acad_cal | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_inst_config | id | status_id | fk_tb_inst_config_status | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_inst_config | id | grading_system_type_id | fk_tb_inst_config_grading | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_inst_grp | id | status_id | fk_tb_inst_grp_status | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_inst_grp | id | grp_type_id | fk_tb_inst_grp_type | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_org | id | org_grp_id | fk_tb_org_group | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_org | id | status_id | fk_tb_org_status | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_org | id | org_type_id | fk_tb_org_type | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_org_contact | id | status_id | fk_tb_org_contact_status | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_org_doc | id | status_id | fk_tb_org_doc_status | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_org_doc | id | doc_type_id | fk_tb_org_doc_type | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_org_smm | id | sm_app_id | fk_tb_org_smm_app | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_org_smm | id | status_id | fk_tb_org_smm_status | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_vend | id | status_id | fk_tb_vend_status | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_org.tb_vend | id | vendor_type_id | fk_tb_vend_type | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_lookup.tb_lookup | sch_rbac.tb_org_role | id | status_id | fk_tb_org_role_status | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_lookup.tb_lookup | sch_rbac.tb_permission | id | status_id | fk_tb_permission_status | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_lookup.tb_lookup | sch_rbac.tb_position | id | status_id | fk_tb_position_status | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_lookup.tb_lookup | sch_rbac.tb_position | id | position_type_id | fk_tb_position_type | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_lookup.tb_lookup | sch_rbac.tb_position_assignment | id | status_id | fk_tb_position_assignment_status | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_lookup.tb_lookup | sch_rbac.tb_user_org | id | status_id | fk_tb_user_org_status | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_lookup.tb_lookup | sch_rbac.tb_user_role | id | status_id | fk_tb_user_role_status | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_lookup.tb_lookup | sch_results.tb_crs_res | id | status_id | fk_crs_res_status | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_lookup.tb_lookup | sch_results.tb_crs_res | id | res_status_id | fk_crs_res_result_status | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_lookup.tb_lookup | sch_results.tb_crs_res | id | result_source_id | fk_crs_res_source | RESTRICT | CASCADE | YES | m_results | Aggregation |
| sch_lookup.tb_lookup | sch_results.tb_crs_res | id | grade_id | fk_crs_res_grade | RESTRICT | CASCADE | YES | m_results | Aggregation |
| sch_lookup.tb_lookup | sch_results.tb_grade_card | id | status_id | fk_grade_card_status | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_lookup.tb_lookup | sch_results.tb_prog_res | id | acad_standing_id | fk_prog_res_acad_standing | RESTRICT | CASCADE | YES | m_results | Aggregation |
| sch_lookup.tb_lookup | sch_results.tb_prog_res | id | completion_status_id | fk_prog_res_completion | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_lookup.tb_lookup | sch_results.tb_prog_res | id | status_id | fk_prog_res_status | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_lookup.tb_lookup | sch_results.tb_res_policy | id | grading_policy_id | fk_res_policy_grading | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_lookup.tb_lookup | sch_results.tb_res_policy | id | status_id | fk_res_policy_status | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_lookup.tb_lookup | sch_results.tb_res_policy | id | acad_standing_policy_id | fk_res_policy_acad_standing | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_lookup.tb_lookup | sch_results.tb_res_policy | id | attempt_policy_id | fk_res_policy_attempt | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_lookup.tb_lookup | sch_results.tb_res_policy | id | credit_policy_id | fk_res_policy_credit | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_lookup.tb_lookup | sch_results.tb_res_publication | id | status_id | fk_res_publication_status | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_lookup.tb_lookup | sch_results.tb_term_res | id | acad_standing_id | fk_term_res_acad_standing | RESTRICT | CASCADE | YES | m_results | Aggregation |
| sch_lookup.tb_lookup | sch_results.tb_term_res | id | res_status_id | fk_term_res_result_status | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_lookup.tb_lookup | sch_results.tb_term_res | id | status_id | fk_term_res_status | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_lookup.tb_lookup | sch_student.tb_alumni | id | status_id | fk_alumni_status | RESTRICT | CASCADE | NO | m_student | Aggregation |
| sch_lookup.tb_lookup | sch_student.tb_stud | id | current_status_id | fk_stud_status | RESTRICT | CASCADE | NO | m_student | Aggregation |
| sch_lookup.tb_lookup | sch_student.tb_stud_acad_progress | id | acad_standing_id | fk_stud_progress_standing | RESTRICT | CASCADE | NO | m_student | Aggregation |
| sch_lookup.tb_lookup | sch_student.tb_stud_acad_progress | id | status_id | fk_stud_progress_status | RESTRICT | CASCADE | NO | m_student | Aggregation |
| sch_lookup.tb_lookup | sch_student.tb_stud_enrollment | id | adm_type_id | fk_stud_enrollment_adm_type | RESTRICT | CASCADE | NO | m_student | Aggregation |
| sch_lookup.tb_lookup | sch_student.tb_stud_enrollment | id | status_id | fk_stud_enrollment_status | RESTRICT | CASCADE | NO | m_student | Aggregation |
| sch_lookup.tb_lookup | sch_student.tb_stud_exit | id | reason_id | fk_stud_exit_reason | RESTRICT | CASCADE | NO | m_student | Aggregation |
| sch_lookup.tb_lookup | sch_student.tb_stud_exit | id | status_id | fk_stud_exit_status | RESTRICT | CASCADE | NO | m_student | Aggregation |
| sch_lookup.tb_lookup | sch_student.tb_stud_exit | id | exit_type_id | fk_stud_exit_type | RESTRICT | CASCADE | NO | m_student | Aggregation |
| sch_lookup.tb_lookup | sch_student.tb_stud_graduation | id | status_id | fk_stud_grad_status | RESTRICT | CASCADE | NO | m_student | Aggregation |
| sch_lookup.tb_lookup | sch_student.tb_stud_graduation | id | classification_id | fk_stud_grad_classification | RESTRICT | CASCADE | NO | m_student | Aggregation |
| sch_lookup.tb_lookup | sch_student.tb_stud_profile | id | status_id | fk_stud_profile_status | RESTRICT | CASCADE | NO | m_student | Aggregation |
| sch_lookup.tb_lookup | sch_student.tb_stud_profile | id | cat_id | fk_stud_profile_category | RESTRICT | CASCADE | YES | m_student | Aggregation |
| sch_lookup.tb_lookup | sch_student.tb_stud_sec_history | id | status_id | fk_sec_history_status | RESTRICT | CASCADE | NO | m_student | Historical |
| sch_lookup.tb_lookup | sch_student.tb_stud_sec_history | id | transfer_reason_id | fk_sec_history_reason | RESTRICT | CASCADE | NO | m_student | Historical |
| sch_lookup.tb_lookup | sch_student_leave.tb_student_leave_application | id | status_id | fk_tb_student_leave_application_status | RESTRICT | CASCADE | YES | m_student_leave | Aggregation |
| sch_lookup.tb_lookup | sch_student_leave.tb_student_leave_application | id | current_status_id | fk_tb_student_leave_application_current_status | RESTRICT | CASCADE | YES | m_student_leave | Aggregation |
| sch_lookup.tb_lookup | sch_student_leave.tb_student_leave_application | id | leave_type_id | fk_tb_student_leave_application_leave_type | RESTRICT | CASCADE | NO | m_student_leave | Aggregation |
| sch_lookup.tb_lookup | sch_student_leave.tb_student_leave_blackout | id | status_id | fk_tb_student_leave_blackout_status | RESTRICT | CASCADE | YES | m_student_leave | Aggregation |
| sch_lookup.tb_lookup | sch_student_leave.tb_student_leave_day | id | status_id | fk_tb_student_leave_day_status | RESTRICT | CASCADE | YES | m_student_leave | Aggregation |
| sch_lookup.tb_lookup | sch_student_leave.tb_student_leave_day | id | session_id | fk_tb_student_leave_day_session | RESTRICT | CASCADE | NO | m_student_leave | Aggregation |
| sch_lookup.tb_lookup | sch_student_leave.tb_student_leave_eligibility | id | status_id | fk_tb_student_leave_eligibility_status | RESTRICT | CASCADE | YES | m_student_leave | Aggregation |
| sch_lookup.tb_lookup | sch_student_leave.tb_student_leave_eligibility | id | leave_type_id | fk_tb_student_leave_eligibility_leave_type | RESTRICT | CASCADE | NO | m_student_leave | Aggregation |
| sch_lookup.tb_lookup | sch_student_leave.tb_student_leave_policy | id | status_id | fk_tb_student_leave_policy_status | RESTRICT | CASCADE | YES | m_student_leave | Aggregation |
| sch_lookup.tb_lookup | sch_student_leave.tb_student_leave_policy | id | leave_type_id | fk_tb_student_leave_policy_leave_type | RESTRICT | CASCADE | NO | m_student_leave | Aggregation |
| sch_lookup.tb_lookup | sch_student_leave.tb_student_leave_process_log | id | status_id | fk_tb_student_leave_process_log_status | RESTRICT | CASCADE | YES | m_student_leave | Historical |
| sch_lookup.tb_lookup | sch_student_leave.tb_student_leave_process_log | id | event_type_id | fk_tb_student_leave_process_log_event_type | RESTRICT | CASCADE | NO | m_student_leave | Historical |
| sch_lookup.tb_lookup | sch_student_leave.tb_student_leave_rule_exception | id | status_id | fk_tb_student_leave_rule_exception_status | RESTRICT | CASCADE | YES | m_student_leave | Aggregation |
| sch_lookup.tb_lookup | sch_student_leave.tb_student_leave_status_history | id | status_id | fk_tb_student_leave_status_history_status | RESTRICT | CASCADE | NO | m_student_leave | Historical |
| sch_lookup.tb_lookup | sch_student_leave.tb_student_leave_support_doc | id | status_id | fk_tb_student_leave_support_doc_status | RESTRICT | CASCADE | YES | m_student_leave | Aggregation |
| sch_lookup.tb_lookup | sch_student_leave.tb_student_leave_support_doc | id | document_type_id | fk_tb_student_leave_support_doc_document_type | RESTRICT | CASCADE | YES | m_student_leave | Aggregation |
| sch_lookup.tb_lookup | sch_sys_admin.tb_login_policy | id | status_id | fk_tb_login_policy_status | NO ACTION | NO ACTION | NO | m_sys_admin | Historical |
| sch_lookup.tb_lookup | sch_sys_admin.tb_login_policy_allowed_country | id | status_id | fk_tb_login_policy_allowed_country_status | NO ACTION | NO ACTION | NO | m_sys_admin | Historical |
| sch_lookup.tb_lookup | sch_sys_admin.tb_login_policy_allowed_ip | id | status_id | fk_tb_login_policy_allowed_ip_status | NO ACTION | NO ACTION | NO | m_sys_admin | Historical |
| sch_lookup.tb_lookup | sch_sys_admin.tb_login_policy_auth_method | id | auth_method_id | fk_tb_login_policy_auth_method_lookup | NO ACTION | NO ACTION | NO | m_sys_admin | Historical |
| sch_lookup.tb_lookup | sch_sys_admin.tb_login_policy_auth_method | id | status_id | fk_tb_login_policy_auth_method_status | NO ACTION | NO ACTION | NO | m_sys_admin | Historical |
| sch_lookup.tb_lookup | sch_sys_admin.tb_login_policy_blocked_country | id | status_id | fk_tb_login_policy_blocked_country_status | NO ACTION | NO ACTION | NO | m_sys_admin | Historical |
| sch_lookup.tb_lookup | sch_sys_admin.tb_login_policy_blocked_ip | id | status_id | fk_tb_login_policy_blocked_ip_status | NO ACTION | NO ACTION | NO | m_sys_admin | Historical |
| sch_lookup.tb_lookup | sch_sys_admin.tb_password_policy | id | status_id | fk_tb_password_policy_status | NO ACTION | NO ACTION | NO | m_sys_admin | Aggregation |
| sch_lookup.tb_lookup | sch_sys_admin.tb_session_policy | id | status_id | fk_tb_session_policy_status | NO ACTION | NO ACTION | NO | m_sys_admin | Aggregation |
| sch_lookup.tb_lookup | sch_timetable.tb_class_cancellation | id | cancellation_reason_id | fk_cancel_reason | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_lookup.tb_lookup | sch_timetable.tb_class_session | id | session_source_id | fk_class_session_source | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_lookup.tb_lookup | sch_timetable.tb_class_session | id | session_status_id | fk_class_session_status | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_lookup.tb_lookup | sch_timetable.tb_class_session_change | id | change_type_id | fk_change_type | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_lookup.tb_lookup | sch_timetable.tb_extra_class | id | session_type_id | fk_extra_session_type | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_lookup.tb_lookup | sch_timetable.tb_holiday_adjustment | id | adjustment_type_id | fk_holiday_type | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_lookup.tb_lookup | sch_timetable.tb_tt | id | status_id | fk_tt_status | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_lookup.tb_lookup | sch_timetable.tb_tt_entry | id | session_type_id | fk_tt_entry_session_type | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_lookup.tb_lookup | sch_timetable.tb_working_day | id | day_of_week_id | fk_working_day_day | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_lookup.tb_lookup_cat | sch_lookup.tb_lookup | id | cat_id | fk_lookup_cat | RESTRICT | CASCADE | NO | m_lookup | Aggregation |
| sch_org.tb_dept | sch_academic_struct.tb_prog | id | department_id | fk_prog_dept | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_org.tb_dept | sch_employee.tb_department_assignment | id | department_id | fk_department_assignment_department | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_org.tb_dept | sch_employee.tb_fac_acad_assignment | id | department_id | fk_fac_acad_assignment_dept | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_org.tb_dept | sch_org.tb_dept | id | parent_dept_id | fk_tb_dept_parent | NO ACTION | NO ACTION | YES | m_org | Aggregation |
| sch_org.tb_dept | sch_org.tb_dept_accreditation | id | dept_id | fk_tb_dept_accreditation_dept | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_org.tb_dept | sch_org.tb_dept_profile | id | dept_id | fk_tb_dept_profile_dept | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_org.tb_dept | sch_rbac.tb_position | id | dept_id | fk_tb_position_dept | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_org.tb_inst | sch_aaa.tb_institution_login_policy | id | inst_id | fk_tb_institution_login_policy_inst | CASCADE | NO ACTION | NO | m_AAA | Composition |
| sch_org.tb_inst | sch_aaa.tb_institution_password_policy | id | inst_id | fk_tb_institution_password_policy_inst | CASCADE | NO ACTION | NO | m_AAA | Composition |
| sch_org.tb_inst | sch_aaa.tb_institution_session_policy | id | inst_id | fk_tb_institution_session_policy_inst | CASCADE | NO ACTION | NO | m_AAA | Composition |
| sch_org.tb_inst | sch_academic_struct.tb_acad_year | id | institution_id | fk_acad_year_inst | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_org.tb_inst | sch_academic_struct.tb_prog | id | institution_id | fk_prog_inst | RESTRICT | CASCADE | NO | m_academic_struct | Aggregation |
| sch_org.tb_inst | sch_admission.tb_adm_cycle | id | institution_id | fk_adm_cycle_inst | RESTRICT | CASCADE | NO | m_admission | Aggregation |
| sch_org.tb_inst | sch_assessment.tb_rubric | id | inst_id | fk_rubric_inst | RESTRICT | CASCADE | NO | m_assessment | Aggregation |
| sch_org.tb_inst | sch_attendance.tb_att_policy | id | inst_id | fk_att_policy_inst | RESTRICT | CASCADE | NO | m_attendance | Aggregation |
| sch_org.tb_inst | sch_fees.tb_fee_structure | id | institution_id | fk_fee_structure_inst | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_org.tb_inst | sch_fees.tb_installment_plan | id | institution_id | fk_installment_plan_inst | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_org.tb_inst | sch_infra.tb_building | id | ins_id | fk_building_inst | RESTRICT | CASCADE | NO | m_infra | Aggregation |
| sch_org.tb_inst | sch_org.tb_dept | id | inst_id | fk_tb_dept_inst | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_org.tb_inst | sch_org.tb_inst_accr_rank | id | inst_id | fk_tb_inst_accr_rank_inst | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_org.tb_inst | sch_org.tb_inst_config | id | inst_id | fk_tb_inst_config_inst | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_org.tb_inst | sch_org.tb_inst_profile | id | inst_id | fk_tb_inst_profile_inst | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_org.tb_inst | sch_results.tb_res_policy | id | inst_id | fk_res_policy_inst | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_org.tb_inst | sch_student_leave.tb_student_leave_policy | id | institution_id | fk_tb_student_leave_policy_inst | RESTRICT | CASCADE | NO | m_student_leave | Aggregation |
| sch_org.tb_inst | sch_timetable.tb_time_slot | id | inst_id | fk_time_slot_inst | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_org.tb_inst | sch_timetable.tb_working_day | id | inst_id | fk_working_day_inst | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_org.tb_inst_grp | sch_org.tb_inst | id | inst_grp_id | fk_tb_inst_group | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_org.tb_inst_grp | sch_org.tb_inst_grp_profile | id | inst_grp_id | fk_tb_inst_grp_profile_group | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_org.tb_org | sch_employee.tb_emp | id | org_id | fk_emp_org | RESTRICT | CASCADE | NO | m_employee | Aggregation |
| sch_org.tb_org | sch_lms.tb_lms_certificate_template | id | org_id | fk_tb_lms_certificate_template_org | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_org.tb_org | sch_lms.tb_lms_resource_library | id | org_id | fk_tb_lms_resource_library_org | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_org.tb_org | sch_org.tb_corp | id | org_id | fk_tb_corp_org | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_org.tb_org | sch_org.tb_govt_agency | id | org_id | fk_tb_govt_agency_org | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_org.tb_org | sch_org.tb_inst | id | org_id | fk_tb_inst_org | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_org.tb_org | sch_org.tb_inst_grp | id | org_id | fk_tb_inst_grp_org | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_org.tb_org | sch_org.tb_org_branding | id | org_id | fk_tb_org_branding_org | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_org.tb_org | sch_org.tb_org_contact | id | org_id | fk_tb_org_contact_org | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_org.tb_org | sch_org.tb_org_doc | id | org_id | fk_tb_org_doc_org | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_org.tb_org | sch_org.tb_org_profile | id | org_id | fk_tb_org_profile_org | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_org.tb_org | sch_org.tb_org_smm | id | org_id | fk_tb_org_smm_org | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_org.tb_org | sch_org.tb_vend | id | org_id | fk_tb_vend_org | NO ACTION | NO ACTION | NO | m_org | Aggregation |
| sch_org.tb_org | sch_rbac.tb_org_role | id | org_id | fk_tb_org_role_org | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_org.tb_org | sch_rbac.tb_position | id | org_id | fk_tb_position_org | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_org.tb_org | sch_rbac.tb_user_org | id | org_id | fk_tb_user_org_org | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_org.tb_org | sch_sys_admin.tb_login_policy | id | org_id | fk_tb_login_policy_org | NO ACTION | NO ACTION | NO | m_sys_admin | Historical |
| sch_org.tb_org | sch_sys_admin.tb_password_policy | id | org_id | fk_tb_password_policy_org | NO ACTION | NO ACTION | NO | m_sys_admin | Aggregation |
| sch_org.tb_org | sch_sys_admin.tb_session_policy | id | org_id | fk_tb_session_policy_org | NO ACTION | NO ACTION | NO | m_sys_admin | Aggregation |
| sch_rbac.tb_org_role | sch_org.tb_org_contact | id | contact_role_id | fk_tb_org_contact_role | NO ACTION | NO ACTION | YES | m_org | Aggregation |
| sch_rbac.tb_org_role | sch_rbac.tb_user_role | id | org_role_id | fk_tb_user_role_org_role | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_rbac.tb_permission | sch_rbac.tb_role_permission | id | permission_id | fk_tb_role_permission_permission | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_rbac.tb_position | sch_rbac.tb_position_assignment | id | position_id | fk_tb_position_assignment_position | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_rbac.tb_user_org | sch_aaa.tb_auth_log | id | user_org_id | fk_tb_auth_log_user_org | NO ACTION | NO ACTION | YES | m_AAA | Historical |
| sch_rbac.tb_user_org | sch_rbac.tb_position_assignment | id | user_org_id | fk_tb_position_assignment_user_org | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_rbac.tb_user_org | sch_rbac.tb_user_role | id | user_org_id | fk_tb_user_role_user_org | NO ACTION | NO ACTION | NO | m_iam | Aggregation |
| sch_results.tb_res_policy | sch_results.tb_crs_res | id | res_policy_id | fk_crs_res_policy | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_results.tb_res_policy | sch_results.tb_prog_res | id | res_policy_id | fk_prog_res_policy | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_results.tb_res_policy | sch_results.tb_term_res | id | res_policy_id | fk_term_res_policy | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_results.tb_term_res | sch_results.tb_grade_card | id | term_res_id | fk_grade_card_term | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_results.tb_term_res | sch_results.tb_res_publication | id | term_res_id | fk_res_publication_term | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_student.tb_stud | sch_assessment.tb_asmt_mark | id | stud_id | fk_asmt_mark_student | RESTRICT | CASCADE | NO | m_assessment | Aggregation |
| sch_student.tb_stud | sch_assessment.tb_asmt_submission | id | stud_id | fk_asmt_submission_student | RESTRICT | CASCADE | NO | m_assessment | Aggregation |
| sch_student.tb_stud | sch_attendance.tb_att_record | id | stud_id | fk_att_record_student | RESTRICT | CASCADE | NO | m_attendance | Aggregation |
| sch_student.tb_stud | sch_course_delivery.tb_stud_crs_registration | id | stud_id | fk_stud_crs_registration_student | RESTRICT | CASCADE | NO | m_course_delivery | Aggregation |
| sch_student.tb_stud | sch_examination.tb_exam_registration | id | stud_id | fk_exam_registration_stud | RESTRICT | CASCADE | NO | m_examination | Aggregation |
| sch_student.tb_stud | sch_lms.tb_lms_achievement_award | id | student_id | fk_tb_lms_achievement_award_student | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_student.tb_stud | sch_lms.tb_lms_activity_log | id | student_id | fk_tb_lms_activity_log_student | RESTRICT | CASCADE | NO | m_lms | Historical |
| sch_student.tb_stud | sch_lms.tb_lms_activity_progress | id | student_id | fk_tb_lms_activity_progress_student | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_student.tb_stud | sch_lms.tb_lms_ai_recommendation | id | student_id | fk_tb_lms_ai_recommendation_student | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_student.tb_stud | sch_lms.tb_lms_assignment_group_member | id | student_id | fk_tb_lms_assignment_group_member_student | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_student.tb_stud | sch_lms.tb_lms_assignment_submission | id | student_id | fk_tb_lms_assignment_submission_student | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_student.tb_stud | sch_lms.tb_lms_badge_award | id | student_id | fk_tb_lms_badge_award_student | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_student.tb_stud | sch_lms.tb_lms_bookmark | id | student_id | fk_tb_lms_bookmark_student | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_student.tb_stud | sch_lms.tb_lms_certificate_award | id | student_id | fk_tb_lms_certificate_award_student | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_student.tb_stud | sch_lms.tb_lms_course_progress | id | student_id | fk_tb_lms_course_progress_student | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_student.tb_stud | sch_lms.tb_lms_document_progress | id | student_id | fk_tb_lms_document_progress_student | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_student.tb_stud | sch_lms.tb_lms_enrollment | id | student_id | fk_tb_lms_enrollment_student | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_student.tb_stud | sch_lms.tb_lms_favorite | id | student_id | fk_tb_lms_favorite_student | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_student.tb_stud | sch_lms.tb_lms_highlight | id | student_id | fk_tb_lms_highlight_student | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_student.tb_stud | sch_lms.tb_lms_learning_event | id | student_id | fk_tb_lms_learning_event_student | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_student.tb_stud | sch_lms.tb_lms_learning_session | id | student_id | fk_tb_lms_learning_session_student | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_student.tb_stud | sch_lms.tb_lms_learning_streak | id | student_id | fk_tb_lms_learning_streak_student | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_student.tb_stud | sch_lms.tb_lms_lesson_progress | id | student_id | fk_tb_lms_lesson_progress_student | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_student.tb_stud | sch_lms.tb_lms_note | id | student_id | fk_tb_lms_note_student | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_student.tb_stud | sch_lms.tb_lms_offline_download | id | student_id | fk_tb_lms_offline_download_student | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_student.tb_stud | sch_lms.tb_lms_quiz_analytics | id | student_id | fk_tb_lms_quiz_analytics_student | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_student.tb_stud | sch_lms.tb_lms_quiz_attempt | id | student_id | fk_tb_lms_quiz_attempt_student | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_student.tb_stud | sch_lms.tb_lms_resume_state | id | student_id | fk_tb_lms_resume_state_student | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_student.tb_stud | sch_lms.tb_lms_video_progress | id | student_id | fk_tb_lms_video_progress_student | RESTRICT | CASCADE | NO | m_lms | Aggregation |
| sch_student.tb_stud | sch_student.tb_alumni | id | stud_id | fk_alumni_stud | RESTRICT | CASCADE | NO | m_student | Aggregation |
| sch_student.tb_stud | sch_student.tb_stud_acad_progress | id | stud_id | fk_stud_progress_stud | RESTRICT | CASCADE | NO | m_student | Aggregation |
| sch_student.tb_stud | sch_student.tb_stud_enrollment | id | stud_id | fk_stud_enrollment_stud | RESTRICT | CASCADE | NO | m_student | Aggregation |
| sch_student.tb_stud | sch_student.tb_stud_exit | id | stud_id | fk_stud_exit_stud | RESTRICT | CASCADE | NO | m_student | Aggregation |
| sch_student.tb_stud | sch_student.tb_stud_graduation | id | stud_id | fk_stud_grad_stud | RESTRICT | CASCADE | NO | m_student | Aggregation |
| sch_student.tb_stud | sch_student.tb_stud_profile | id | stud_id | fk_stud_profile_stud | RESTRICT | CASCADE | NO | m_student | Aggregation |
| sch_student.tb_stud | sch_student.tb_stud_sec_history | id | stud_id | fk_sec_history_stud | RESTRICT | CASCADE | NO | m_student | Historical |
| sch_student.tb_stud | sch_student_leave.tb_student_leave_application | id | student_id | fk_tb_student_leave_application_student | RESTRICT | CASCADE | NO | m_student_leave | Aggregation |
| sch_student.tb_stud | sch_student_leave.tb_student_leave_eligibility | id | student_id | fk_tb_student_leave_eligibility_student | RESTRICT | CASCADE | NO | m_student_leave | Aggregation |
| sch_student.tb_stud | sch_student_leave.tb_student_leave_rule_exception | id | student_id | fk_tb_student_leave_rule_exception_student | RESTRICT | CASCADE | NO | m_student_leave | Aggregation |
| sch_student.tb_stud_enrollment | sch_fees.tb_concession | id | stud_enrollment_id | fk_concession_stud | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_student.tb_stud_enrollment | sch_fees.tb_fee_waiver | id | stud_enrollment_id | fk_waiver_stud | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_student.tb_stud_enrollment | sch_fees.tb_financial_hold | id | stud_enrollment_id | fk_financial_hold_stud | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_student.tb_stud_enrollment | sch_fees.tb_financial_ledger | id | stud_enrollment_id | fk_ledger_stud | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_student.tb_stud_enrollment | sch_fees.tb_payment | id | stud_enrollment_id | fk_payment_stud | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_student.tb_stud_enrollment | sch_fees.tb_penalty | id | stud_enrollment_id | fk_penalty_stud | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_student.tb_stud_enrollment | sch_fees.tb_refund | id | stud_enrollment_id | fk_refund_stud | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_student.tb_stud_enrollment | sch_fees.tb_scholarship | id | stud_enrollment_id | fk_scholarship_stud | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_student.tb_stud_enrollment | sch_fees.tb_stud_fee_asmt | id | stud_enrollment_id | fk_stud_fee_asmt_enrollment | RESTRICT | CASCADE | NO | m_fees | Aggregation |
| sch_student.tb_stud_enrollment | sch_results.tb_prog_res | id | stud_enrollment_id | fk_prog_res_enrollment | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_student.tb_stud_enrollment | sch_results.tb_term_res | id | stud_enrollment_id | fk_term_res_enrollment | RESTRICT | CASCADE | NO | m_results | Aggregation |
| sch_student.tb_stud_enrollment | sch_student.tb_stud | id | current_enrollment_id | fk_stud_current_enrollment | RESTRICT | CASCADE | YES | m_student | Aggregation |
| sch_student_leave.tb_student_leave_application | sch_student_leave.tb_student_leave_day | id | leave_application_id | fk_tb_student_leave_day_application | RESTRICT | CASCADE | NO | m_student_leave | Aggregation |
| sch_student_leave.tb_student_leave_application | sch_student_leave.tb_student_leave_process_log | id | leave_application_id | fk_tb_student_leave_process_log_application | RESTRICT | CASCADE | NO | m_student_leave | Historical |
| sch_student_leave.tb_student_leave_application | sch_student_leave.tb_student_leave_status_history | id | leave_application_id | fk_tb_student_leave_status_history_application | RESTRICT | CASCADE | NO | m_student_leave | Historical |
| sch_student_leave.tb_student_leave_application | sch_student_leave.tb_student_leave_support_doc | id | leave_application_id | fk_tb_student_leave_support_doc_application | RESTRICT | CASCADE | NO | m_student_leave | Aggregation |
| sch_student_leave.tb_student_leave_policy | sch_student_leave.tb_student_leave_application | id | leave_policy_id | fk_tb_student_leave_application_policy | RESTRICT | CASCADE | NO | m_student_leave | Aggregation |
| sch_student_leave.tb_student_leave_policy | sch_student_leave.tb_student_leave_blackout | id | leave_policy_id | fk_tb_student_leave_blackout_policy | RESTRICT | CASCADE | NO | m_student_leave | Aggregation |
| sch_student_leave.tb_student_leave_policy | sch_student_leave.tb_student_leave_eligibility | id | leave_policy_id | fk_tb_student_leave_eligibility_policy | RESTRICT | CASCADE | NO | m_student_leave | Aggregation |
| sch_student_leave.tb_student_leave_policy | sch_student_leave.tb_student_leave_rule_exception | id | leave_policy_id | fk_tb_student_leave_rule_exception_policy | RESTRICT | CASCADE | NO | m_student_leave | Aggregation |
| sch_sys_admin.tb_login_policy | sch_sys_admin.tb_login_policy_allowed_country | id | login_policy_id | fk_tb_login_policy_allowed_country_policy | NO ACTION | NO ACTION | NO | m_sys_admin | Historical |
| sch_sys_admin.tb_login_policy | sch_sys_admin.tb_login_policy_allowed_ip | id | login_policy_id | fk_tb_login_policy_allowed_ip_policy | NO ACTION | NO ACTION | NO | m_sys_admin | Historical |
| sch_sys_admin.tb_login_policy | sch_sys_admin.tb_login_policy_auth_method | id | login_policy_id | fk_tb_login_policy_auth_method_policy | NO ACTION | NO ACTION | NO | m_sys_admin | Historical |
| sch_sys_admin.tb_login_policy | sch_sys_admin.tb_login_policy_blocked_country | id | login_policy_id | fk_tb_login_policy_blocked_country_policy | NO ACTION | NO ACTION | NO | m_sys_admin | Historical |
| sch_sys_admin.tb_login_policy | sch_sys_admin.tb_login_policy_blocked_ip | id | login_policy_id | fk_tb_login_policy_blocked_ip_policy | NO ACTION | NO ACTION | NO | m_sys_admin | Historical |
| sch_timetable.tb_class_session | sch_attendance.tb_att_session | id | class_session_id | fk_att_session_class | RESTRICT | CASCADE | NO | m_attendance | Aggregation |
| sch_timetable.tb_class_session | sch_timetable.tb_class_cancellation | id | class_session_id | fk_cancel_session | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_timetable.tb_class_session | sch_timetable.tb_class_session_change | id | class_session_id | fk_change_session | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_timetable.tb_class_session | sch_timetable.tb_class_session_fac | id | class_session_id | fk_class_session_fac_session | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_timetable.tb_class_session | sch_timetable.tb_class_session_room | id | class_session_id | fk_class_session_room_session | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_timetable.tb_class_session | sch_timetable.tb_extra_class | id | class_session_id | fk_extra_class_session | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_timetable.tb_time_slot | sch_timetable.tb_class_session_change | id | new_time_slot_id | fk_change_new_slot | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_timetable.tb_time_slot | sch_timetable.tb_class_session_change | id | old_time_slot_id | fk_change_old_slot | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_timetable.tb_time_slot | sch_timetable.tb_extra_class | id | time_slot_id | fk_extra_slot | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_timetable.tb_time_slot | sch_timetable.tb_tt_entry | id | time_slot_id | fk_tt_entry_time_slot | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_timetable.tb_tt | sch_timetable.tb_tt_entry | id | tt_id | fk_tt_entry_tt | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_timetable.tb_tt_entry | sch_timetable.tb_class_session | id | tt_entry_id | fk_class_session_tt_entry | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_timetable.tb_tt_entry | sch_timetable.tb_tt_entry_sec | id | tt_entry_id | fk_tt_entry_sec_entry | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
| sch_timetable.tb_working_day | sch_timetable.tb_holiday_adjustment | id | source_working_day_id | fk_holiday_source_day | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_timetable.tb_working_day | sch_timetable.tb_holiday_adjustment | id | target_working_day_id | fk_holiday_target_day | RESTRICT | CASCADE | YES | m_timetable | Aggregation |
| sch_timetable.tb_working_day | sch_timetable.tb_tt_entry | id | working_day_id | fk_tt_entry_working_day | RESTRICT | CASCADE | NO | m_timetable | Aggregation |
