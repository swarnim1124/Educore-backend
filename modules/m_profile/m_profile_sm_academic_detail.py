"""
File: m_profile_sm_academic_detail.py
Description: Academic Identifier submodule for m_profile.

Author: EduCore
App: OneApp

"""

from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from .m_profile_data import ProfileDataLayer


class academicDetail:
    """
    Action class for academic identifier CRUD.

    Request format:
    {
        "mod": "m_profile",
        "subMod": "sm_academic_detail",
        "action": "academicDetail",
        "actionType": "<add|view|update|delete>",
        "payload": { ... }
    }
    """

    async def execute(self, request, context):
        action_type = request.actionType.lower()
        dal = ProfileDataLayer(context.postgres)

        match action_type:
            case "add":
                return await self.add(request.payload or {}, dal, context)
            case "view":
                return await self.view(request.payload or {}, dal, context)
            case "update":
                return await self.update(request.payload or {}, dal, context)
            case "delete":
                return await self.delete(request.payload or {}, dal, context)
            case _:
                return XSCUtility.error_response(
                    f"Unsupported actionType '{action_type}' for academicDetail"
                )

    # --------------------------------------------------------------------- add
    async def add(self, payload, dal, context):
        user_id = payload.get("userId")
        if not user_id:
            return XSCUtility.error_response("userId is required")

        if not await dal.profile_exists(user_id):
            return XSCUtility.error_response(
                "personalDetail must exist before creating academicDetail"
            )

        created_ids = []

        # ID Card Number
        id_card = payload.get("idCardNumber")
        if id_card:
            resp = await dal.create_user_identifier(
                {
                    "user_id": user_id,
                    "identifier_type_id": 1,  # Lookup ID for ID Card
                    "identifier_value": id_card,
                    "status_id": 1,
                }
            )
            if resp.get("status") == "success" and resp.get("data"):
                created_ids.append(
                    {"type": "idCardNumber", "id": resp["data"][0]["id"]}
                )

        # Biometric ID
        biometric = payload.get("biometricId")
        if biometric:
            resp = await dal.create_user_identifier(
                {
                    "user_id": user_id,
                    "identifier_type_id": 2,  # Lookup ID for Biometric
                    "identifier_value": biometric,
                    "status_id": 1,
                }
            )
            if resp.get("status") == "success" and resp.get("data"):
                created_ids.append({"type": "biometricId", "id": resp["data"][0]["id"]})

        return XSCUtility.success_response(
            "Academic identifiers created successfully",
            {"userId": user_id, "identifiers": created_ids},
        )

    # -------------------------------------------------------------------- view
    async def view(self, payload, dal, context):
        user_id = payload.get("userId")
        enrollment_number = payload.get("enrollmentNumber")
        employee_code = payload.get("employeeCode")

        result_data = {}

        if user_id:
            # Fetch identifiers from TB_USER_IDENTIFIER
            ident_resp = await dal.get_academic_detail_by_user(user_id)
            identifiers = (
                ident_resp.get("data", [])
                if ident_resp.get("status") == "success"
                else []
            )
            result_data["identifiers"] = identifiers

            # Fetch student record
            stud_resp = await dal.get_student_record(user_id)
            stud_row = (
                stud_resp.get("data", [None])[0] if stud_resp.get("data") else None
            )
            if stud_row:
                result_data["enrollmentNumber"] = stud_row.get("stud_no")
                result_data["branch"] = stud_row.get("branch") or stud_row.get("branch_short")
                result_data["batch"] = stud_row.get("batch")
                result_data["semester"] = stud_row.get("semester")
                result_data["section"] = stud_row.get("section")
                result_data["cgpa"] = (
                    float(stud_row["cgpa"])
                    if stud_row.get("cgpa") is not None
                    else None
                )
            else:
                result_data["enrollmentNumber"] = None
                result_data["branch"] = None
                result_data["batch"] = None
                result_data["semester"] = None
                result_data["section"] = None
                result_data["cgpa"] = None

            # Fetch employee record (may return null if table missing)
            emp_resp = await dal.get_employee_record(user_id)
            emp_row = emp_resp.get("data", [None])[0] if emp_resp.get("data") else None
            result_data["employeeCode"] = emp_row.get("emp_code") if emp_row else None

            return XSCUtility.success_response("Academic detail retrieved", result_data)

        if enrollment_number:
            from sqlalchemy import text

            stmt = text("""
                SELECT s.id, s.user_id, s.stud_no as enrollment_number,
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
                WHERE s.stud_no = :stud_no
            """)
            resp = await dal._safe_query(stmt, {"stud_no": enrollment_number})
            return XSCUtility.success_response(
                "Academic detail retrieved", resp.get("data", [])
            )

        if employee_code:
            from sqlalchemy import text

            stmt = text(
                "SELECT id, user_id, emp_code FROM sch_employee.tb_emp WHERE emp_code = :emp_code"
            )
            resp = await dal._safe_query(stmt, {"emp_code": employee_code})
            if resp.get("status") == "success" and resp.get("data"):
                return XSCUtility.success_response(
                    "Academic detail retrieved", resp.get("data", [])
                )

            stmt_alt = text(
                "SELECT id, user_id, emp_code FROM sch_emp_fac.tb_emp WHERE emp_code = :emp_code"
            )
            resp_alt = await dal._safe_query(stmt_alt, {"emp_code": employee_code})
            return XSCUtility.success_response(
                "Academic detail retrieved", resp_alt.get("data", [])
            )

        return XSCUtility.error_response(
            "Provide userId, enrollmentNumber, or employeeCode"
        )

    # ------------------------------------------------------------------ update
    async def update(self, payload, dal, context):
        user_id = payload.get("userId")
        if not user_id:
            return XSCUtility.error_response("userId is required")

        # enrollmentNumber and employeeCode are immutable
        if payload.get("enrollmentNumber") or payload.get("employeeCode"):
            return XSCUtility.error_response(
                "enrollmentNumber and employeeCode are immutable and cannot be updated"
            )

        updated = []

        # Re-issue ID Card
        new_id_card = payload.get("idCardNumber")
        if new_id_card:
            # Deactivate old, create new
            await dal.deactivate_user_identifier(user_id, 1)
            resp = await dal.create_user_identifier(
                {
                    "user_id": user_id,
                    "identifier_type_id": 1,
                    "identifier_value": new_id_card,
                    "status_id": 1,
                }
            )
            updated.append("idCardNumber")

        # Re-issue Biometric ID
        new_bio = payload.get("biometricId")
        if new_bio:
            await dal.deactivate_user_identifier(user_id, 2)
            resp = await dal.create_user_identifier(
                {
                    "user_id": user_id,
                    "identifier_type_id": 2,
                    "identifier_value": new_bio,
                    "status_id": 1,
                }
            )
            updated.append("biometricId")

        if not updated:
            return XSCUtility.error_response(
                "No updatable fields provided (idCardNumber, biometricId)"
            )

        return XSCUtility.success_response(
            "Academic identifiers updated", {"reIssued": updated}
        )

    # ------------------------------------------------------------------ delete
    async def delete(self, payload, dal, context):
        user_id = payload.get("userId")
        identifier_type = payload.get("identifierType")
        reason = payload.get("reason", "Not specified")

        if not user_id or not identifier_type:
            return XSCUtility.error_response("userId and identifierType are required")

        type_map = {"idCardNumber": 1, "biometricId": 2}
        type_id = type_map.get(identifier_type)

        if not type_id:
            return XSCUtility.error_response(
                "Invalid identifierType. Allowed: idCardNumber, biometricId. "
                "enrollmentNumber/employeeCode cannot be deleted."
            )

        await dal.deactivate_user_identifier(user_id, type_id)
        return XSCUtility.success_response(
            "Identifier deactivated",
            {"identifierType": identifier_type, "reason": reason},
        )


class sm_academic_detail:
    """
    Framework Submodule Wrapper class for sm_academic_detail.
    Routes action calls to action class academicDetail.
    """

    @staticmethod
    async def academicDetail(request, context):
        return await academicDetail().execute(request, context)


# Alias for legacy camelCase class reference
sm_academicDetail = sm_academic_detail
