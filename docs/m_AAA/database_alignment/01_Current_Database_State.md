# Current Database State

## 1. Schemas
- public
- sch_aaa
- sch_attendance
- sch_core
- sch_iam
- sch_lookup
- sch_org
- sch_rbac

## 2. Tables & Columns (m_AAA relevant schemas)

### sch_aaa
#### tb_account_lock
- **Columns**: 7
- **Indexes**:
  - tb_account_lock_pkey
#### tb_auth_log
- **Columns**: 11
- **Indexes**:
  - tb_auth_log_pkey
#### tb_mfa_challenge
- **Columns**: 10
- **Indexes**:
  - uq_tb_mfa_challenge_token
  - tb_mfa_challenge_pkey
#### tb_mfa_method
- **Columns**: 11
- **Indexes**:
  - uq_tb_mfa_method
  - tb_mfa_method_pkey
#### tb_password_reset
- **Columns**: 8
- **Indexes**:
  - uq_tb_password_reset_token
  - tb_password_reset_pkey

### sch_iam
#### tb_role
- **Columns**: 7
- **Indexes**:
  - uq_tb_role_name
  - uq_tb_role_code
  - tb_role_pkey
#### tb_user
- **Columns**: 8
- **Indexes**:
  - tb_user_pkey
  - tb_user_mobile_key
  - tb_user_email_key
#### tb_user_address
- **Columns**: 7
- **Indexes**:
  - uq_tb_user_address
  - tb_user_address_pkey
#### tb_user_aud
- **Columns**: 8
- **Indexes**:
  - tb_user_aud_pkey
#### tb_user_doc
- **Columns**: 4
- **Indexes**:
  - uq_tb_user_doc
  - tb_user_doc_pkey
#### tb_user_emergency_contact
- **Columns**: 9
- **Indexes**:
  - tb_user_emergency_contact_pkey
#### tb_user_grp_type
- **Columns**: 6
- **Indexes**:
  - tb_user_grp_type_user_group_name_key
  - tb_user_grp_type_pkey
  - tb_user_grp_type_grp_code_key
#### tb_user_identifier
- **Columns**: 9
- **Indexes**:
  - uq_tb_user_identifier
  - tb_user_identifier_pkey
#### tb_user_login
- **Columns**: 8
- **Indexes**:
  - tb_user_login_pkey
#### tb_user_med
- **Columns**: 9
- **Indexes**:
  - tb_user_med_user_id_key
  - tb_user_med_pkey
#### tb_user_preference
- **Columns**: 6
- **Indexes**:
  - uq_tb_user_preference
  - tb_user_preference_pkey
#### tb_user_profile
- **Columns**: 14
- **Indexes**:
  - tb_user_profile_user_id_key
  - tb_user_profile_pkey
#### tb_user_session
- **Columns**: 15
- **Indexes**:
  - tb_user_session_session_token_key
  - tb_user_session_refresh_token_key
  - tb_user_session_pkey

### sch_rbac
#### tb_org_role
- **Columns**: 4
- **Indexes**:
  - uq_tb_org_role
  - tb_org_role_pkey
#### tb_permission
- **Columns**: 6
- **Indexes**:
  - uq_tb_permission_module_name
  - uq_tb_permission_code
  - tb_permission_pkey
#### tb_position
- **Columns**: 6
- **Indexes**:
  - uq_tb_position
  - tb_position_pkey
#### tb_position_assignment
- **Columns**: 6
- **Indexes**:
  - uq_tb_position_assignment
  - tb_position_assignment_pkey
#### tb_role_permission
- **Columns**: 4
- **Indexes**:
  - uq_tb_role_permission
  - tb_role_permission_pkey
#### tb_user_org
- **Columns**: 6
- **Indexes**:
  - uq_tb_user_org
  - tb_user_org_pkey
#### tb_user_role
- **Columns**: 6
- **Indexes**:
  - uq_tb_user_role
  - tb_user_role_pkey

### sch_org
#### tb_corp
- **Columns**: 5
- **Indexes**:
  - tb_corp_pkey
  - tb_corp_org_id_key
#### tb_dept
- **Columns**: 7
- **Indexes**:
  - uq_tb_dept
  - tb_dept_pkey
#### tb_dept_accreditation
- **Columns**: 9
- **Indexes**:
  - uq_tb_dept_accreditation
  - tb_dept_accreditation_pkey
#### tb_dept_profile
- **Columns**: 7
- **Indexes**:
  - tb_dept_profile_pkey
  - tb_dept_profile_dept_id_key
#### tb_govt_agency
- **Columns**: 4
- **Indexes**:
  - tb_govt_agency_pkey
  - tb_govt_agency_org_id_key
#### tb_inst
- **Columns**: 5
- **Indexes**:
  - uq_tb_inst
  - tb_inst_pkey
#### tb_inst_accr_rank
- **Columns**: 9
- **Indexes**:
  - uq_tb_inst_accr_rank
  - tb_inst_accr_rank_pkey
#### tb_inst_config
- **Columns**: 6
- **Indexes**:
  - tb_inst_config_pkey
  - tb_inst_config_inst_id_key
#### tb_inst_grp
- **Columns**: 4
- **Indexes**:
  - uq_tb_inst_grp
  - tb_inst_grp_pkey
#### tb_inst_grp_profile
- **Columns**: 4
- **Indexes**:
  - tb_inst_grp_profile_pkey
  - tb_inst_grp_profile_inst_grp_id_key
#### tb_inst_profile
- **Columns**: 8
- **Indexes**:
  - tb_inst_profile_pkey
  - tb_inst_profile_inst_id_key
#### tb_org
- **Columns**: 8
- **Indexes**:
  - tb_org_reg_no_key
  - tb_org_pkey
  - tb_org_legal_name_key
#### tb_org_branding
- **Columns**: 5
- **Indexes**:
  - tb_org_branding_pkey
  - tb_org_branding_org_id_key
#### tb_org_contact
- **Columns**: 6
- **Indexes**:
  - uq_tb_org_contact
  - tb_org_contact_pkey
#### tb_org_doc
- **Columns**: 5
- **Indexes**:
  - uq_tb_org_doc
  - tb_org_doc_pkey
#### tb_org_profile
- **Columns**: 6
- **Indexes**:
  - tb_org_profile_pkey
  - tb_org_profile_org_id_key
#### tb_org_smm
- **Columns**: 7
- **Indexes**:
  - uq_tb_org_smm
  - tb_org_smm_pkey
#### tb_vend
- **Columns**: 6
- **Indexes**:
  - uq_tb_vend_pan
  - uq_tb_vend_gst
  - tb_vend_pkey
  - tb_vend_org_id_key

### sch_lookup
#### tb_lookup
- **Columns**: 4
- **Indexes**:
  - uq_lookup_cat_name
  - tb_lookup_pkey
#### tb_lookup_cat
- **Columns**: 3
- **Indexes**:
  - tb_lookup_cat_pkey
  - tb_lookup_cat_name_key