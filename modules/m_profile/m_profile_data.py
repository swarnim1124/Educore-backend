"""
File: m_profile_data.py
Description: Data Access Layer for m_profile.

Author: EduCore
App: OneApp

"""

from sqlalchemy import text


class ProfileDataLayer:
    """
    Lightweight module-local Data Access layer that consumes the injected context.postgres.
    All methods gracefully handle missing schemas/tables by returning None.
    """

    def __init__(self, db):
        self.db = db

    async def _safe_query(self, stmt, params=None):
        """
        Executes a query and returns the result dict.
        If the table/schema does not exist or permission is denied, returns a dict with status 'success' and empty data.
        For general DB errors, returns a dict with status 'error'.
        """
        try:
            result = await self.db.async_genericSQL(stmt, params)
            if isinstance(result, dict) and result.get("status") == "error":
                err_msg = str(result.get("message", "")).lower()
                err_code = str(result.get("error_code", ""))
                db_err = str(getattr(self.db, "errMsg", "")).lower()
                if (
                    err_code in ("42P01", "42501")
                    or "does not exist" in err_msg
                    or "relation" in err_msg
                    or "schema" in err_msg
                    or "permission denied" in err_msg
                    or "permission denied" in db_err
                ):
                    return {
                        "status": "success",
                        "message": "Schema/table not available or permission denied",
                        "data": [],
                    }
            return result
        except Exception as e:
            err_msg = str(e).lower()
            if (
                "does not exist" in err_msg
                or "relation" in err_msg
                or "schema" in err_msg
                or "permission denied" in err_msg
            ):
                return {
                    "status": "success",
                    "message": "Schema/table not available or permission denied",
                    "data": [],
                }
            return {"status": "error", "message": str(e), "data": []}

    def _first_or_none(self, result):
        """Extracts the first row from a successful query result, or returns None."""
        if result and result.get("status") == "success" and result.get("data"):
            return result["data"][0]
        return None

    # =========================================================================
    # PERSONAL DETAIL
    # =========================================================================

    async def get_personal_detail(self, user_id):
        """
        Retrieves the composite personal detail for a user by joining
        TB_USER, TB_USER_PROFILE, and TB_USER_MED.
        Returns None for any field whose underlying table does not exist.
        """
        profile_data = {}

        # --- Core user record (sch_iam.tb_user) ---
        user_stmt = text("""
            SELECT id, email, mobile
            FROM sch_iam.tb_user
            WHERE id = :user_id
        """)
        user_resp = await self._safe_query(user_stmt, {"user_id": user_id})
        user_row = self._first_or_none(user_resp)
        if user_row:
            profile_data["userId"] = user_row.get("id")
            profile_data["mobile"] = user_row.get("mobile")
            profile_data["email"] = user_row.get("email")
            profile_data["alternateEmail"] = user_row.get("email")
        else:
            return None

        # --- User profile (sch_iam.tb_user_profile + resolved lookups) ---
        profile_stmt = text("""
            SELECT p.user_id, p.f_name, p.m_name, p.l_name, p.dob, p.gender_id,
                   g.name as gender_name,
                   p.profile_photo_id, p.nationality_id,
                   COALESCE(c.name, n.name) as nationality_name,
                   p.primary_lang_id, l.name as primary_lang_name,
                   p.marital_status_id, ms.name as marital_status_name,
                   p.created_at, p.updated_at
            FROM sch_iam.tb_user_profile p
            LEFT JOIN sch_lookup.tb_lookup g ON g.id = p.gender_id
            LEFT JOIN sch_core.tb_country c ON c.id = p.nationality_id
            LEFT JOIN sch_lookup.tb_lookup n ON n.id = p.nationality_id
            LEFT JOIN sch_lookup.tb_lookup l ON l.id = p.primary_lang_id
            LEFT JOIN sch_lookup.tb_lookup ms ON ms.id = p.marital_status_id
            WHERE p.user_id = :user_id
        """)
        profile_resp = await self._safe_query(profile_stmt, {"user_id": user_id})
        profile_row = self._first_or_none(profile_resp)
        if profile_row:
            profile_data["firstName"] = profile_row.get("f_name")
            profile_data["middleName"] = profile_row.get("m_name")
            profile_data["lastName"] = profile_row.get("l_name")
            profile_data["dob"] = (
                str(profile_row["dob"]) if profile_row.get("dob") else None
            )
            profile_data["genderId"] = profile_row.get("gender_id")
            profile_data["gender"] = profile_row.get("gender_name")
            profile_data["genderName"] = profile_row.get("gender_name")
            profile_data["photoDocId"] = profile_row.get("profile_photo_id")
            profile_data["nationalityId"] = profile_row.get("nationality_id")
            profile_data["nationality"] = profile_row.get("nationality_name")
            profile_data["nationalityName"] = profile_row.get("nationality_name")
            profile_data["primaryLangId"] = profile_row.get("primary_lang_id")
            profile_data["primaryLang"] = profile_row.get("primary_lang_name")
            profile_data["primaryLanguage"] = profile_row.get("primary_lang_name")
            profile_data["maritalStatusId"] = profile_row.get("marital_status_id")
            profile_data["maritalStatus"] = profile_row.get("marital_status_name")
            profile_data["createdAt"] = (
                str(profile_row["created_at"])
                if profile_row.get("created_at")
                else None
            )
            profile_data["updatedAt"] = (
                str(profile_row["updated_at"])
                if profile_row.get("updated_at")
                else None
            )
        else:
            profile_data.update(
                {
                    "firstName": None,
                    "middleName": None,
                    "lastName": None,
                    "dob": None,
                    "genderId": None,
                    "gender": None,
                    "genderName": None,
                    "photoDocId": None,
                    "nationalityId": None,
                    "nationality": None,
                    "nationalityName": None,
                    "primaryLangId": None,
                    "primaryLang": None,
                    "primaryLanguage": None,
                    "maritalStatusId": None,
                    "maritalStatus": None,
                    "createdAt": None,
                    "updatedAt": None,
                }
            )

        # --- Blood group from medical record (sch_iam.tb_user_med + resolved lookup) ---
        med_stmt = text("""
            SELECT m.blood_group_id, bg.name as blood_group_name
            FROM sch_iam.tb_user_med m
            LEFT JOIN sch_lookup.tb_lookup bg ON bg.id = m.blood_group_id
            WHERE m.user_id = :user_id
        """)
        med_resp = await self._safe_query(med_stmt, {"user_id": user_id})
        med_row = self._first_or_none(med_resp)
        bg_id = med_row.get("blood_group_id") if med_row else None
        bg_name = med_row.get("blood_group_name") if med_row else None
        profile_data["bloodGroupId"] = bg_id
        profile_data["bloodGroup"] = bg_name
        profile_data["bloodGroupName"] = bg_name

        # --- Addresses (sch_iam.tb_user_address + sch_core.tb_address + resolved lookups & location names) ---
        addr_stmt = text("""
            SELECT ua.id as user_address_id,
                   ua.is_primary as is_primary,
                   ua.status_id as status_id,
                   lk_stat.name as status_name,
                   a.id as address_id,
                   a.addr_type_id as addr_type_id,
                   lk_type.name as addr_type_name,
                   a.number as number,
                   a.line_1 as line_1,
                   a.line_2 as line_2,
                   a.city_id as city_id,
                   c.name as city_name,
                   d.name as district_name,
                   st.name as state_name,
                   cn.name as country_name,
                   a.postal_code_id as postal_code_id,
                   pc.postal_code as postal_code
            FROM sch_iam.tb_user_address ua
            JOIN sch_core.tb_address a ON a.id = ua.address_id
            LEFT JOIN sch_lookup.tb_lookup lk_type ON lk_type.id = a.addr_type_id
            LEFT JOIN sch_lookup.tb_lookup lk_stat ON lk_stat.id = ua.status_id
            LEFT JOIN sch_core.tb_city c ON c.id = a.city_id
            LEFT JOIN sch_core.tb_district d ON d.id = c.district_id
            LEFT JOIN sch_core.tb_state st ON st.id = d.state_id
            LEFT JOIN sch_core.tb_country cn ON cn.id = st.country_id
            LEFT JOIN sch_core.tb_city_postal_code pc ON pc.id = a.postal_code_id
            WHERE ua.user_id = :user_id
        """)
        addr_resp = await self._safe_query(addr_stmt, {"user_id": user_id})
        raw_addresses = (
            addr_resp.get("data", []) if addr_resp.get("status") == "success" else []
        )

        formatted_addresses = []
        for row in raw_addresses:
            formatted_addresses.append(
                {
                    "user_address_id": row.get("user_address_id"),
                    "is_primary": row.get("is_primary"),
                    "status_id": row.get("status_id"),
                    "status": row.get("status_name"),
                    "address_id": row.get("address_id"),
                    "addr_type_id": row.get("addr_type_id"),
                    "addr_type": row.get("addr_type_name"),
                    "address_type": row.get("addr_type_name"),
                    "number": row.get("number"),
                    "line_1": row.get("line_1"),
                    "line_2": row.get("line_2"),
                    "city_id": row.get("city_id"),
                    "city": row.get("city_name"),
                    "district": row.get("district_name"),
                    "state": row.get("state_name"),
                    "country": row.get("country_name"),
                    "postal_code_id": row.get("postal_code_id"),
                    "postal_code": row.get("postal_code"),
                    "pincode": row.get("postal_code"),
                }
            )
        profile_data["addresses"] = formatted_addresses

        return profile_data

    async def create_user_profile(self, data):
        """Inserts a row into sch_iam.tb_user_profile."""
        stmt = text("""
            INSERT INTO sch_iam.tb_user_profile
                (user_id, f_name, m_name, l_name, dob, gender_id,
                 profile_photo_id, nationality_id, created_at, updated_at)
            VALUES
                (:user_id, :f_name, :m_name, :l_name, :dob, :gender_id,
                 :profile_photo_id, :nationality_id, NOW(), NOW())
            RETURNING id
        """)
        return await self._safe_query(stmt, data)

    async def update_user_profile(self, user_id, fields):
        """
        Dynamically updates sch_iam.tb_user_profile columns.
        `fields` is a dict of column_name -> new_value.
        """
        if not fields:
            return {"status": "error", "message": "No fields to update"}

        set_clauses = ", ".join([f"{k} = :{k}" for k in fields.keys()])
        stmt = text("""
            UPDATE sch_iam.tb_user_profile
            SET {set_clauses}, updated_at = NOW()
            WHERE user_id = :user_id
        """)
        params = {**fields, "user_id": user_id}
        return await self._safe_query(stmt, params)

    async def update_user_mobile(self, user_id, mobile):
        """Updates mobile on sch_iam.tb_user."""
        stmt = text("UPDATE sch_iam.tb_user SET mobile = :mobile WHERE id = :user_id")
        return await self._safe_query(stmt, {"user_id": user_id, "mobile": mobile})

    async def check_mobile_unique(self, mobile, exclude_user_id=None):
        """Checks mobile uniqueness within the system."""
        if exclude_user_id:
            stmt = text(
                "SELECT id FROM sch_iam.tb_user WHERE mobile = :mobile AND id != :exclude_id"
            )
            resp = await self._safe_query(
                stmt, {"mobile": mobile, "exclude_id": exclude_user_id}
            )
        else:
            stmt = text("SELECT id FROM sch_iam.tb_user WHERE mobile = :mobile")
            resp = await self._safe_query(stmt, {"mobile": mobile})
        return bool(resp.get("data"))

    async def anonymise_personal_detail(self, user_id):
        """Clears personal fields for erasure/offboarding."""
        stmt = text("""
            UPDATE sch_iam.tb_user_profile
            SET f_name = 'REDACTED', m_name = NULL, l_name = 'REDACTED',
                dob = NULL, profile_photo_id = NULL, updated_at = NOW()
            WHERE user_id = :user_id
        """)
        return await self._safe_query(stmt, {"user_id": user_id})

    # =========================================================================
    # ACADEMIC DETAIL
    # =========================================================================

    async def get_academic_detail_by_user(self, user_id):
        """Retrieves academic identifiers for a user from TB_USER_IDENTIFIER with resolved lookup names."""
        stmt = text("""
            SELECT i.id, i.user_id, i.identifier_type_id,
                   t.name as identifier_type_name,
                   i.identifier_value, i.status_id,
                   s.name as status_name
            FROM sch_iam.tb_user_identifier i
            LEFT JOIN sch_lookup.tb_lookup t ON t.id = i.identifier_type_id
            LEFT JOIN sch_lookup.tb_lookup s ON s.id = i.status_id
            WHERE i.user_id = :user_id
        """)
        return await self._safe_query(stmt, {"user_id": user_id})

    async def get_student_record(self, user_id):
        """Retrieves comprehensive student academic details including Branch, Batch, Semester, Section, and CGPA."""
        stmt = text("""
            SELECT s.id, s.user_id, s.stud_no, s.current_status_id,
                   COALESCE(sec.sec_name, sec_b.sec_name) as section,
                   COALESCE(b.batch_name, b_intake.batch_name) as batch,
                   COALESCE(p.prog_name, p_intake.prog_name) as branch,
                   COALESCE(p.short_name, p_intake.short_name) as branch_short,
                   COALESCE(ap.cgpa, pr.cgpa) as cgpa,
                   COALESCE(ct.term_number, at.term_number, ap.curr_term_id) as semester
            FROM sch_student.tb_stud s
            LEFT JOIN sch_academic_struct.tb_sec sec ON sec.id = s.current_sec_id
            LEFT JOIN sch_academic_struct.tb_batch b ON b.id = sec.batch_id
            LEFT JOIN sch_academic_struct.tb_curr_version cv ON cv.id = b.curr_version_id
            LEFT JOIN sch_academic_struct.tb_curr c ON c.id = cv.curr_id
            LEFT JOIN sch_academic_struct.tb_prog p ON p.id = c.prog_id
            LEFT JOIN sch_student.tb_stud_enrollment e ON e.id = s.current_enrollment_id OR (e.stud_id = s.id AND e.is_current = true)
            LEFT JOIN sch_admission.tb_prog_intake pi ON pi.id = e.prog_intake_id
            LEFT JOIN sch_academic_struct.tb_batch b_intake ON b_intake.id = pi.batch_id
            LEFT JOIN sch_academic_struct.tb_prog p_intake ON p_intake.id = pi.prog_id
            LEFT JOIN sch_academic_struct.tb_sec sec_b ON sec_b.batch_id = b_intake.id
            LEFT JOIN sch_student.tb_stud_acad_progress ap ON ap.stud_id = s.id
            LEFT JOIN sch_results.tb_prog_res pr ON pr.stud_enrollment_id = e.id
            LEFT JOIN sch_academic_struct.tb_curr_term ct ON ct.id = ap.curr_term_id
            LEFT JOIN sch_academic_struct.tb_acad_term at ON at.id = ap.curr_term_id
            WHERE s.user_id = :user_id
        """)
        return await self._safe_query(stmt, {"user_id": user_id})

    async def get_employee_record(self, user_id):
        """Retrieves employee code from TB_EMP (tries sch_employee, falls back to sch_emp_fac)."""
        stmt = text("""
            SELECT id, user_id, emp_code
            FROM sch_employee.tb_emp
            WHERE user_id = :user_id
        """)
        res = await self._safe_query(stmt, {"user_id": user_id})
        if res.get("status") == "success" and res.get("data"):
            return res

        stmt_alt = text("""
            SELECT id, user_id, emp_code
            FROM sch_emp_fac.tb_emp
            WHERE user_id = :user_id
        """)
        return await self._safe_query(stmt_alt, {"user_id": user_id})

    async def create_user_identifier(self, data):
        """Inserts a user identifier record."""
        stmt = text("""
            INSERT INTO sch_iam.tb_user_identifier
                (user_id, identifier_type_id, identifier_value, status_id)
            VALUES
                (:user_id, :identifier_type_id, :identifier_value, :status_id)
            RETURNING id
        """)
        return await self._safe_query(stmt, data)

    async def update_user_identifier(self, identifier_id, fields):
        """Updates a user identifier record (e.g., re-issue idCardNumber)."""
        set_clauses = ", ".join([f"{k} = :{k}" for k in fields.keys()])
        stmt = text("""
            UPDATE sch_iam.tb_user_identifier
            SET {set_clauses}
            WHERE id = :identifier_id
        """)
        params = {**fields, "identifier_id": identifier_id}
        return await self._safe_query(stmt, params)

    async def deactivate_user_identifier(self, user_id, identifier_type_id):
        """Deactivates a specific identifier type for re-issue."""
        stmt = text("""
            UPDATE sch_iam.tb_user_identifier
            SET status_id = 2
            WHERE user_id = :user_id AND identifier_type_id = :identifier_type_id
        """)
        return await self._safe_query(
            stmt, {"user_id": user_id, "identifier_type_id": identifier_type_id}
        )

    # =========================================================================
    # FAMILY DETAIL
    # =========================================================================

    async def get_family_details(self, stud_id):
        """Retrieves family/guardian records for a student with resolved lookup names."""
        stmt = text("""
            SELECT p.id, p.first_name, p.middle_name, p.last_name,
                   p.gender_id, g.name as gender_name,
                   p.dob, p.mobile_no, p.email,
                   p.occupation, p.annual_income, p.photo_doc_id,
                   p.status_id, s.name as status_name,
                   ps.relationship_type_id, r.name as relationship_type_name,
                   ps.is_primary_guardian, ps.is_emergency_contact
            FROM sch_parents.tb_par p
            JOIN sch_parents.tb_par_stud ps ON ps.par_id = p.id
            LEFT JOIN sch_lookup.tb_lookup g ON g.id = p.gender_id
            LEFT JOIN sch_lookup.tb_lookup s ON s.id = p.status_id
            LEFT JOIN sch_lookup.tb_lookup r ON r.id = ps.relationship_type_id
            WHERE ps.stud_id = :stud_id
        """)
        return await self._safe_query(stmt, {"stud_id": stud_id})

    async def create_family_detail(self, par_data, link_data):
        """
        Creates a parent/guardian record and links to the student.
        par_data  -> columns for sch_parents.tb_par
        link_data -> columns for sch_parents.tb_par_stud
        """
        par_stmt = text("""
            INSERT INTO sch_parents.tb_par
                (user_id, first_name, middle_name, last_name, gender_id,
                 mobile_no, email, occupation, annual_income, status_id)
            VALUES
                (:user_id, :first_name, :middle_name, :last_name, :gender_id,
                 :mobile_no, :email, :occupation, :annual_income, :status_id)
            RETURNING id
        """)
        par_resp = await self._safe_query(par_stmt, par_data)
        par_row = self._first_or_none(par_resp)
        if not par_row:
            return par_resp

        par_id = par_row["id"]
        link_data["par_id"] = par_id

        link_stmt = text("""
            INSERT INTO sch_parents.tb_par_stud
                (stud_id, par_id, relationship_type_id,
                 is_primary_guardian, is_emergency_contact)
            VALUES
                (:stud_id, :par_id, :relationship_type_id,
                 :is_primary_guardian, :is_emergency_contact)
            RETURNING id
        """)
        return await self._safe_query(link_stmt, link_data)

    async def update_family_detail(self, par_id, fields):
        """Updates a parent/guardian record."""
        if not fields:
            return {"status": "error", "message": "No fields to update"}
        set_clauses = ", ".join([f"{k} = :{k}" for k in fields.keys()])
        stmt = text("""
            UPDATE sch_parents.tb_par
            SET {set_clauses}
            WHERE id = :par_id
        """)
        params = {**fields, "par_id": par_id}
        return await self._safe_query(stmt, params)

    async def unset_emergency_contact_flag(self, stud_id):
        """Clears the emergency contact flag on all existing records for a student."""
        stmt = text("""
            UPDATE sch_parents.tb_par_stud
            SET is_emergency_contact = false
            WHERE stud_id = :stud_id AND is_emergency_contact = true
        """)
        return await self._safe_query(stmt, {"stud_id": stud_id})

    async def delete_family_detail(self, par_id):
        """Removes a parent/guardian record and its student link."""
        link_stmt = text("DELETE FROM sch_parents.tb_par_stud WHERE par_id = :par_id")
        await self._safe_query(link_stmt, {"par_id": par_id})

        par_stmt = text("DELETE FROM sch_parents.tb_par WHERE id = :par_id")
        return await self._safe_query(par_stmt, {"par_id": par_id})

    # =========================================================================
    # EMERGENCY CONTACT
    # =========================================================================

    async def get_emergency_contacts(self, user_id):
        """Retrieves emergency contacts for a user, ordered by IS_PRIMARY desc."""
        stmt = text("""
            SELECT id, user_id, f_name, m_name, l_name, mobile, email,
                   is_primary, status_id
            FROM sch_iam.tb_user_emergency_contact
            WHERE user_id = :user_id
            ORDER BY is_primary DESC, id ASC
        """)
        return await self._safe_query(stmt, {"user_id": user_id})

    async def create_emergency_contact(self, data):
        """Creates an emergency contact record."""
        stmt = text("""
            INSERT INTO sch_iam.tb_user_emergency_contact
                (user_id, f_name, l_name, mobile, is_primary, status_id)
            VALUES
                (:user_id, :f_name, :l_name, :mobile, :is_primary, :status_id)
            RETURNING id
        """)
        return await self._safe_query(stmt, data)

    async def update_emergency_contact(self, contact_id, fields):
        """Updates an emergency contact record."""
        if not fields:
            return {"status": "error", "message": "No fields to update"}
        set_clauses = ", ".join([f"{k} = :{k}" for k in fields.keys()])
        stmt = text("""
            UPDATE sch_iam.tb_user_emergency_contact
            SET {set_clauses}
            WHERE id = :contact_id
        """)
        params = {**fields, "contact_id": contact_id}
        return await self._safe_query(stmt, params)

    async def delete_emergency_contact(self, contact_id):
        """Deletes an emergency contact record."""
        stmt = text(
            "DELETE FROM sch_iam.tb_user_emergency_contact WHERE id = :contact_id"
        )
        return await self._safe_query(stmt, {"contact_id": contact_id})

    # =========================================================================
    # MEDICAL DETAIL
    # =========================================================================

    async def get_medical_detail(self, user_id):
        """Retrieves the medical record for a user with resolved lookup names."""
        stmt = text("""
            SELECT m.id, m.user_id, m.height, m.weight, m.blood_group_id,
                   bg.name as blood_group_name,
                   m.allergy_info, m.med_condition, m.disability_type_id,
                   dt.name as disability_type_name,
                   m.emergency_note
            FROM sch_iam.tb_user_med m
            LEFT JOIN sch_lookup.tb_lookup bg ON bg.id = m.blood_group_id
            LEFT JOIN sch_lookup.tb_lookup dt ON dt.id = m.disability_type_id
            WHERE m.user_id = :user_id
        """)
        return await self._safe_query(stmt, {"user_id": user_id})

    async def create_medical_detail(self, data):
        """Creates a medical record for a user."""
        stmt = text("""
            INSERT INTO sch_iam.tb_user_med
                (user_id, blood_group_id, allergy_info, med_condition, emergency_note)
            VALUES
                (:user_id, :blood_group_id, :allergy_info, :med_condition, :emergency_note)
            RETURNING id
        """)
        return await self._safe_query(stmt, data)

    async def update_medical_detail(self, user_id, fields):
        """Updates the medical record for a user."""
        if not fields:
            return {"status": "error", "message": "No fields to update"}
        set_clauses = ", ".join([f"{k} = :{k}" for k in fields.keys()])
        stmt = text("""
            UPDATE sch_iam.tb_user_med
            SET {set_clauses}
            WHERE user_id = :user_id
        """)
        params = {**fields, "user_id": user_id}
        return await self._safe_query(stmt, params)

    async def delete_medical_detail(self, user_id):
        """Deletes the medical record for a user."""
        stmt = text("DELETE FROM sch_iam.tb_user_med WHERE user_id = :user_id")
        return await self._safe_query(stmt, {"user_id": user_id})

    # =========================================================================
    # USER PREFERENCE
    # =========================================================================

    async def get_user_preferences(self, user_id):
        """Retrieves all preference key-value pairs for a user."""
        stmt = text("""
            SELECT id, user_id, preference_type_id, value, created_at, updated_at
            FROM sch_iam.tb_user_preference
            WHERE user_id = :user_id
        """)
        return await self._safe_query(stmt, {"user_id": user_id})

    async def upsert_user_preference(self, user_id, preference_type_id, value):
        """Inserts or updates a single preference entry."""
        # Check if preference already exists
        check_stmt = text("""
            SELECT id FROM sch_iam.tb_user_preference
            WHERE user_id = :user_id AND preference_type_id = :preference_type_id
        """)
        check_resp = await self._safe_query(
            check_stmt, {"user_id": user_id, "preference_type_id": preference_type_id}
        )
        existing = self._first_or_none(check_resp)

        if existing:
            stmt = text("""
                UPDATE sch_iam.tb_user_preference
                SET value = :value, updated_at = NOW()
                WHERE user_id = :user_id AND preference_type_id = :preference_type_id
            """)
        else:
            stmt = text("""
                INSERT INTO sch_iam.tb_user_preference
                    (user_id, preference_type_id, value, created_at, updated_at)
                VALUES
                    (:user_id, :preference_type_id, :value, NOW(), NOW())
                RETURNING id
            """)
        return await self._safe_query(
            stmt,
            {
                "user_id": user_id,
                "preference_type_id": preference_type_id,
                "value": value,
            },
        )

    async def delete_user_preferences(self, user_id):
        """Deletes all preference records for a user (reset to defaults)."""
        stmt = text("DELETE FROM sch_iam.tb_user_preference WHERE user_id = :user_id")
        return await self._safe_query(stmt, {"user_id": user_id})

    # =========================================================================
    # USER EXISTENCE CHECK (shared helper)
    # =========================================================================

    async def user_exists(self, user_id):
        """Checks if a user exists in sch_iam.tb_user."""
        stmt = text("SELECT id FROM sch_iam.tb_user WHERE id = :user_id")
        resp = await self._safe_query(stmt, {"user_id": user_id})
        return bool(resp.get("data"))

    async def profile_exists(self, user_id):
        """Checks if a user_profile record exists."""
        stmt = text("SELECT id FROM sch_iam.tb_user_profile WHERE user_id = :user_id")
        resp = await self._safe_query(stmt, {"user_id": user_id})
        return bool(resp.get("data"))

    async def get_profile_created_at(self, user_id):
        """Returns the creation timestamp of the user profile (for grace window checks)."""
        stmt = text(
            "SELECT created_at FROM sch_iam.tb_user_profile WHERE user_id = :user_id"
        )
        resp = await self._safe_query(stmt, {"user_id": user_id})
        row = self._first_or_none(resp)
        return row.get("created_at") if row else None
