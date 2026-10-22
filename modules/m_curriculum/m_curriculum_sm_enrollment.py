"""
File: m_curriculum_sm_enrollment.py
Description: Handler for Student Enrollment and Course Registration entities in m_curriculum.
Orchestrates enrollment, semester registration, and elective registration workflows while delegating
database access strictly to CurriculumDataLayer.

Author: Siddharth Amdal
App: OneApp

"""

import logging
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from .m_curriculum_data import CurriculumDataLayer
from .sch_curriculum import CurriculumValidator

logger = logging.getLogger(__name__)


class sm_enrollment:
    """
    Submodule handler for student academic enrollment and course registration actions:
    - enrollment
    - semesterRegistration
    - electiveRegistration
    """

    # ------------------------------------------------------------
    # ACTION: enrollment
    # ------------------------------------------------------------
    @staticmethod
    async def enrollment(request, context):
        """
        Executes the `enrollment()` action to process the corresponding client request.

        Args:
            request: The OneAppRequest payload containing actionType and payload.
            context: The ExecutionContext containing request-scoped dependencies.

        Returns:
            Standard framework response dict.
        """
        match request.actionType.lower():
            case "add":
                return await sm_enrollment.enrollment_add(request, context)
            case "view":
                return await sm_enrollment.enrollment_view(request, context)
            case "update":
                return await sm_enrollment.enrollment_update(request, context)
            case "delete":
                return await sm_enrollment.enrollment_delete(request, context)
            case _:
                return XSCUtility.error_response("Invalid actionType for enrollment")

    @staticmethod
    async def enrollment_add(request, context):
        """
        Executes the `enrollment_add()` action to enroll a student into a programme intake.

        Args:
            request: The OneAppRequest payload.
            context: The ExecutionContext containing request-scoped dependencies.

        Returns:
            - status: 'success' or 'error'.
            - message: Status details.
            - data: Created enrollment ID or error details.

        req_json_obj expected format:
        {
            "mod": "m_curriculum",
            "subMod": "sm_enrollment",
            "action": "enrollment",
            "actionType": "add",
            "payload": {
                "studId": 1001,
                "progIntakeId": 202601,
                "admTypeId": 1,
                "enrollmentDate": "2026-08-01",
                "expectedGraduationDate": "2030-05-30",
                "statusId": 1
            }
        }
        """
        try:
            logger.info("Entering enrollment_add")
            payload = request.payload or {}

            # 1. Payload Validation
            errors = CurriculumValidator.validate_enrollment_add(payload)
            if errors:
                return XSCUtility.error_response("Validation failed", error_code=errors)

            db_layer = CurriculumDataLayer(context.postgres)
            stud_id = payload.get("studId")

            # 2. Business Logic Validation: Check for duplicate enrollment
            existing = await db_layer.get_student_enrollment(stud_id=stud_id)
            if (
                existing.get("status") == "success"
                and len(existing.get("data", [])) > 0
            ):
                # In basic business rules, student cannot have duplicate active enrollments in same intake/date
                for enc in existing.get("data", []):
                    if str(enc.get("enrollment_date", "")) == str(
                        payload.get("enrollmentDate", "")
                    ):
                        return XSCUtility.error_response(
                            "Student enrollment already exists for this date",
                            error_code="CONFLICT",
                        )

            # 3. Check for dynamic lookup ID resolution gap
            status_id = payload.get("statusId")
            if status_id is None:
                # TODO: Default enrollment status ID resolution from m_lookup is not yet integrated (Gap Analysis).
                return XSCUtility.error_response(
                    "Not Implemented: Enrollment creation pending dynamic default status ID resolution from m_lookup (Gap Analysis)",
                    error_code="501",
                )

            # 4. Construct Payload and Persist via DAO
            row_data = {
                "stud_id": stud_id,
                "prog_intake_id": payload.get("progIntakeId"),
                "adm_type_id": payload.get("admTypeId"),
                "enrollment_date": payload.get("enrollmentDate"),
                "status_id": status_id,
                "is_current": True,
                "created_on": XSCUtility.get_utc_timestamp(),
            }

            res = await db_layer.create_student_enrollment(row_data)
            if res.get("status") == "error":
                return res

            enc_data = res.get("data", [{}])[0]
            enc_id = enc_data.get("id")
            logger.info(
                f"Student enrollment created successfully for student {stud_id}"
            )
            return XSCUtility.success_response(
                "Student enrolled successfully", data={"enrollmentId": enc_id}
            )

        except Exception as e:
            logger.error(f"Error in enrollment_add: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Internal Server Error")

    @staticmethod
    async def enrollment_view(request, context):
        """
        Executes the `enrollment_view()` action to retrieve student enrollments.
        """
        try:
            logger.info("Entering enrollment_view")
            payload = request.payload or {}
            db_layer = CurriculumDataLayer(context.postgres)

            enrollment_id = payload.get("enrollmentId")
            stud_id = payload.get("studId")
            prog_intake_id = payload.get("progIntakeId")

            res = await db_layer.get_student_enrollment(
                stud_id=stud_id,
                enrollment_id=enrollment_id,
                prog_intake_id=prog_intake_id,
            )
            if res.get("status") == "error":
                return res

            if enrollment_id and len(res.get("data", [])) == 0:
                return XSCUtility.error_response(
                    "Enrollment record not found", error_code="NOT_FOUND"
                )

            return XSCUtility.success_response(
                "Enrollments retrieved successfully", data=res.get("data", [])
            )

        except Exception as e:
            logger.error(f"Error in enrollment_view: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Internal Server Error")

    @staticmethod
    async def enrollment_update(request, context):
        """
        Executes the `enrollment_update()` action to update student enrollment status or current flag.
        """
        try:
            logger.info("Entering enrollment_update")
            payload = request.payload or {}

            errors = CurriculumValidator.validate_enrollment_update(payload)
            if errors:
                return XSCUtility.error_response("Validation failed", error_code=errors)

            db_layer = CurriculumDataLayer(context.postgres)
            enrollment_id = payload.get("enrollmentId")

            existing = await db_layer.get_student_enrollment(
                enrollment_id=enrollment_id
            )
            if existing.get("status") == "error":
                return existing
            if not existing.get("data") or len(existing.get("data", [])) == 0:
                return XSCUtility.error_response(
                    "Enrollment record not found", error_code="NOT_FOUND"
                )

            # TODO: Enrollment update requires status validation against m_lookup and historical enrollment state transitions (Gap Analysis).
            return XSCUtility.error_response(
                "Not Implemented: Enrollment update pending status ID verification and historical state transition rules from m_lookup (Gap Analysis)",
                error_code="501",
            )

        except Exception as e:
            logger.error(f"Error in enrollment_update: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Internal Server Error")

    @staticmethod
    async def enrollment_delete(request, context):
        """
        Executes the `enrollment_delete()` action to withdraw/cancel a student enrollment.
        """
        try:
            logger.info("Entering enrollment_delete")
            payload = request.payload or {}

            errors = CurriculumValidator.validate_enrollment_delete(payload)
            if errors:
                return XSCUtility.error_response("Validation failed", error_code=errors)

            db_layer = CurriculumDataLayer(context.postgres)
            enrollment_id = payload.get("enrollmentId")

            existing = await db_layer.get_student_enrollment(
                enrollment_id=enrollment_id
            )
            if existing.get("status") == "error":
                return existing
            if not existing.get("data") or len(existing.get("data", [])) == 0:
                return XSCUtility.error_response(
                    "Enrollment record not found", error_code="NOT_FOUND"
                )

            # TODO: Enrollment cancellation requires resolving withdrawal status ID dynamically from m_lookup (Gap Analysis).
            return XSCUtility.error_response(
                "Not Implemented: Enrollment withdrawal/cancellation pending dynamic status resolution from m_lookup (Gap Analysis)",
                error_code="501",
            )

        except Exception as e:
            logger.error(f"Error in enrollment_delete: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Internal Server Error")

    # ------------------------------------------------------------
    # ACTION: semesterRegistration
    # ------------------------------------------------------------
    @staticmethod
    async def semesterRegistration(request, context):
        """
        Executes the `semesterRegistration()` action to handle semester course registrations.
        """
        match request.actionType.lower():
            case "add":
                return await sm_enrollment.semesterRegistration_add(request, context)
            case "view":
                return await sm_enrollment.semesterRegistration_view(request, context)
            case "update":
                return await sm_enrollment.semesterRegistration_update(request, context)
            case "delete":
                return await sm_enrollment.semesterRegistration_delete(request, context)
            case _:
                return XSCUtility.error_response(
                    "Invalid actionType for semesterRegistration"
                )

    @staticmethod
    async def semesterRegistration_add(request, context):
        """
        Executes the `semesterRegistration_add()` action to register a student for a set of semester course offerings.
        """
        try:
            logger.info("Entering semesterRegistration_add")
            payload = request.payload or {}

            errors = CurriculumValidator.validate_semester_registration_add(payload)
            if errors:
                return XSCUtility.error_response("Validation failed", error_code=errors)

            db_layer = CurriculumDataLayer(context.postgres)
            stud_id = payload.get("studId")

            # Verify student has an active enrollment before registration
            enc = await db_layer.get_student_enrollment(stud_id=stud_id)
            if enc.get("status") == "error":
                return enc
            if not enc.get("data") or len(enc.get("data", [])) == 0:
                return XSCUtility.error_response(
                    "Student is not enrolled in any programme", error_code="NOT_FOUND"
                )

            # TODO: Semester course registration requires validating course prerequisites (tb_crs_prerequisite), resolving course offerings against external schema sch_course_delivery.tb_crs_offering, and dynamically resolving registration status from m_lookup (Gap Analysis).
            return XSCUtility.error_response(
                "Not Implemented: Semester registration creation pending prerequisite validation (tb_crs_prerequisite), course offering resolution against external schema sch_course_delivery, and dynamic status resolution from m_lookup (Gap Analysis)",
                error_code="501",
            )

        except Exception as e:
            logger.error(f"Error in semesterRegistration_add: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Internal Server Error")

    @staticmethod
    async def semesterRegistration_view(request, context):
        """
        Executes the `semesterRegistration_view()` action to retrieve a student's course registrations.
        """
        try:
            logger.info("Entering semesterRegistration_view")
            payload = request.payload or {}
            db_layer = CurriculumDataLayer(context.postgres)

            stud_id = payload.get("studId")
            crs_offering_id = payload.get("crsOfferingId")

            res = await db_layer.get_student_registrations(
                stud_id=stud_id, crs_offering_id=crs_offering_id
            )
            return XSCUtility.success_response(
                "Semester registrations retrieved successfully",
                data=res.get("data", []),
            )

        except Exception as e:
            logger.error(f"Error in semesterRegistration_view: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Internal Server Error")

    @staticmethod
    async def semesterRegistration_update(request, context):
        """
        Executes the `semesterRegistration_update()` action to modify registration status.
        """
        try:
            logger.info("Entering semesterRegistration_update")
            payload = request.payload or {}

            errors = CurriculumValidator.validate_semester_registration_update(payload)
            if errors:
                return XSCUtility.error_response("Validation failed", error_code=errors)

            db_layer = CurriculumDataLayer(context.postgres)
            registration_id = payload.get("registrationId")

            existing = await db_layer.get_student_registrations(
                registration_id=registration_id
            )
            if existing.get("status") == "error":
                return existing
            if not existing.get("data") or len(existing.get("data", [])) == 0:
                return XSCUtility.error_response(
                    "Registration record not found", error_code="NOT_FOUND"
                )

            # TODO: Modifying registration status requires verifying state transitions against m_lookup and checking academic calendar windows (Gap Analysis).
            return XSCUtility.error_response(
                "Not Implemented: Semester registration update pending status verification against m_lookup and academic window rules (Gap Analysis)",
                error_code="501",
            )

        except Exception as e:
            logger.error(
                f"Error in semesterRegistration_update: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response("Internal Server Error")

    @staticmethod
    async def semesterRegistration_delete(request, context):
        """
        Executes the `semesterRegistration_delete()` action to cancel/drop a course registration.
        """
        try:
            logger.info("Entering semesterRegistration_delete")
            payload = request.payload or {}

            errors = CurriculumValidator.validate_semester_registration_delete(payload)
            if errors:
                return XSCUtility.error_response("Validation failed", error_code=errors)

            db_layer = CurriculumDataLayer(context.postgres)
            registration_id = payload.get("registrationId")

            existing = await db_layer.get_student_registrations(
                registration_id=registration_id
            )
            if existing.get("status") == "error":
                return existing
            if not existing.get("data") or len(existing.get("data", [])) == 0:
                return XSCUtility.error_response(
                    "Registration record not found", error_code="NOT_FOUND"
                )

            # TODO: Canceling registration requires checking course drop-period windows and updating status in sch_course_delivery (Gap Analysis).
            return XSCUtility.error_response(
                "Not Implemented: Semester registration cancellation pending course drop-period window validation (Gap Analysis)",
                error_code="501",
            )

        except Exception as e:
            logger.error(
                f"Error in semesterRegistration_delete: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response("Internal Server Error")

    # ------------------------------------------------------------
    # ACTION: electiveRegistration
    # ------------------------------------------------------------
    @staticmethod
    async def electiveRegistration(request, context):
        """
        Executes the `electiveRegistration()` action to handle elective course selections.
        """
        match request.actionType.lower():
            case "add":
                return await sm_enrollment.electiveRegistration_add(request, context)
            case "view":
                return await sm_enrollment.electiveRegistration_view(request, context)
            case "update":
                return await sm_enrollment.electiveRegistration_update(request, context)
            case "delete":
                return await sm_enrollment.electiveRegistration_delete(request, context)
            case _:
                return XSCUtility.error_response(
                    "Invalid actionType for electiveRegistration"
                )

    @staticmethod
    async def electiveRegistration_add(request, context):
        """
        Executes the `electiveRegistration_add()` action to pick a course for an elective slot.
        """
        try:
            logger.info("Entering electiveRegistration_add")
            payload = request.payload or {}

            errors = CurriculumValidator.validate_elective_registration_add(payload)
            if errors:
                return XSCUtility.error_response("Validation failed", error_code=errors)

            db_layer = CurriculumDataLayer(context.postgres)
            stud_id = payload.get("studId")

            enc = await db_layer.get_student_enrollment(stud_id=stud_id)
            if enc.get("status") == "error":
                return enc
            if not enc.get("data") or len(enc.get("data", [])) == 0:
                return XSCUtility.error_response(
                    "Student is not enrolled in any programme", error_code="NOT_FOUND"
                )

            # TODO: Elective registration creation requires checking elective group capacity in sch_course_delivery.tb_crs_offering and validating elective selection constraints in tb_elective_group (Gap Analysis).
            return XSCUtility.error_response(
                "Not Implemented: Elective registration creation pending elective group capacity check (tb_crs_offering, tb_elective_group) across external module schemas (Gap Analysis)",
                error_code="501",
            )

        except Exception as e:
            logger.error(f"Error in electiveRegistration_add: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Internal Server Error")

    @staticmethod
    async def electiveRegistration_view(request, context):
        """
        Executes the `electiveRegistration_view()` action to retrieve elective picks and capacity details.
        """
        try:
            logger.info("Entering electiveRegistration_view")
            # TODO: Elective registration view requires querying external schema sch_course_delivery.tb_crs_offering and joining with tb_elective_group (Gap Analysis).
            return XSCUtility.error_response(
                "Not Implemented: Elective registration view requires querying external schema sch_course_delivery.tb_crs_offering and joining with elective groups (Gap Analysis)",
                error_code="501",
            )

        except Exception as e:
            logger.error(f"Error in electiveRegistration_view: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Internal Server Error")

    @staticmethod
    async def electiveRegistration_update(request, context):
        """
        Executes the `electiveRegistration_update()` action to change an elective pick.
        """
        try:
            logger.info("Entering electiveRegistration_update")
            payload = request.payload or {}

            errors = CurriculumValidator.validate_elective_registration_update(payload)
            if errors:
                return XSCUtility.error_response("Validation failed", error_code=errors)

            db_layer = CurriculumDataLayer(context.postgres)
            registration_id = payload.get("registrationId")

            existing = await db_layer.get_student_registrations(
                registration_id=registration_id
            )
            if existing.get("status") == "error":
                return existing
            if not existing.get("data") or len(existing.get("data", [])) == 0:
                return XSCUtility.error_response(
                    "Registration record not found", error_code="NOT_FOUND"
                )

            # TODO: Changing elective pick requires checking seat capacity on the new course offering and validating registration windows (Gap Analysis).
            return XSCUtility.error_response(
                "Not Implemented: Elective registration update pending seat capacity verification on new offering (Gap Analysis)",
                error_code="501",
            )

        except Exception as e:
            logger.error(
                f"Error in electiveRegistration_update: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response("Internal Server Error")

    @staticmethod
    async def electiveRegistration_delete(request, context):
        """
        Executes the `electiveRegistration_delete()` action to withdraw an elective pick.
        """
        try:
            logger.info("Entering electiveRegistration_delete")
            payload = request.payload or {}

            errors = CurriculumValidator.validate_elective_registration_delete(payload)
            if errors:
                return XSCUtility.error_response("Validation failed", error_code=errors)

            db_layer = CurriculumDataLayer(context.postgres)
            registration_id = payload.get("registrationId")

            existing = await db_layer.get_student_registrations(
                registration_id=registration_id
            )
            if existing.get("status") == "error":
                return existing
            if not existing.get("data") or len(existing.get("data", [])) == 0:
                return XSCUtility.error_response(
                    "Registration record not found", error_code="NOT_FOUND"
                )

            # TODO: Withdrawing an elective requires checking minimum term credit requirements and drop windows (Gap Analysis).
            return XSCUtility.error_response(
                "Not Implemented: Elective registration withdrawal pending minimum term credit and window rules check (Gap Analysis)",
                error_code="501",
            )

        except Exception as e:
            logger.error(
                f"Error in electiveRegistration_delete: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response("Internal Server Error")
