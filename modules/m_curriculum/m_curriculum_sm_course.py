"""
File: m_curriculum_sm_course.py
Description: Handler for Course entity in m_curriculum.

Author: Siddharth Amdal
App: OneApp

"""

import logging
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from .m_curriculum_data import CurriculumDataLayer
from .sch_curriculum import CurriculumValidator

logger = logging.getLogger(__name__)


class sm_course:
    """
    Submodule handler for Course-related actions.
    """

    # ------------------------------------------------------------
    # COURSE DEFINITION
    # ------------------------------------------------------------
    @staticmethod
    async def courseDefinition(request, context):
        """
        Executes the `courseDefinition()` action.
        """
        match request.actionType.lower():
            case "add":
                return await sm_course.courseDefinition_add(request, context)
            case "view":
                return await sm_course.courseDefinition_view(request, context)
            case "update":
                return await sm_course.courseDefinition_update(request, context)
            case "delete":
                return await sm_course.courseDefinition_delete(request, context)
            case _:
                return XSCUtility.error_response("Invalid actionType")

    @staticmethod
    async def courseDefinition_add(request, context):
        try:
            logger.info("Entering courseDefinition_add")
            payload = request.payload or {}

            # 1. Validate Payload
            errors = CurriculumValidator.validate_course_definition_add(payload)
            if errors:
                logger.warning(f"Validation failed for courseDefinition_add: {errors}")
                return XSCUtility.error_response("Validation failed", error_code=errors)

            db_layer = CurriculumDataLayer(context.postgres)

            # 2. Business Validation
            crs_code = payload.get("crsCode")
            exists = await db_layer.search_courses(crs_code=crs_code)
            if exists:
                logger.warning(f"Duplicate course detected: code={crs_code}")
                return XSCUtility.error_response("Course with this code already exists")

            # TODO: Cross-module existence checks for crsTypeId and statusId

            # 3. Execute DB Operation Atomically
            root_payload = {
                "crs_code": crs_code,
                "crs_name": payload.get("crsName"),
                "crs_type_id": payload.get("crsTypeId"),
                "credit_value": payload.get("creditValue"),
                "status_id": payload.get("statusId"),
            }

            # Version Lifecycle Management
            # Creating initial version
            now = XSCUtility.get_utc_timestamp()
            version_payload = {
                "version_no": 1,
                "revision_no": 1,
                "effective_from": now,
                "is_current": True,
                "status_id": payload.get("statusId"),
                "lecture_hours": payload.get("lectureHours", 0),
                "tutorial_hours": payload.get("tutorialHours", 0),
                "practical_hours": payload.get("practicalHours", 0),
                "total_hours": payload.get("lectureHours", 0)
                + payload.get("tutorialHours", 0)
                + payload.get("practicalHours", 0),
            }

            txn_resp = await db_layer.create_course_with_version(
                root_payload, version_payload
            )
            if txn_resp.get("status") == "error":
                return txn_resp

            data = txn_resp.get("data", [{}])[0]
            crs_id = data.get("crs_id")
            version_id = data.get("version_id")

            logger.info(
                f"Course created successfully: root {crs_id}, version {version_id}"
            )
            return XSCUtility.success_response(
                "Course created successfully",
                data={"courseDefinitionId": crs_id, "crsVersionId": version_id},
            )

        except Exception as e:
            logger.error(f"Error in courseDefinition_add: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Internal Server Error")

    @staticmethod
    async def courseDefinition_view(request, context):
        try:
            logger.info("Entering courseDefinition_view")
            payload = request.payload or {}
            db_layer = CurriculumDataLayer(context.postgres)

            crs_id = payload.get("courseDefinitionId")

            if crs_id:
                res = await db_layer.get_course(crs_id)
                if res.get("status") == "error":
                    return res
                records = res.get("data", [])
                if not records:
                    return XSCUtility.error_response(
                        "Course not found", error_code="404"
                    )
                return XSCUtility.success_response(
                    "Course retrieved successfully", data=records[0]
                )
            else:
                crs_code = payload.get("searchQuery")
                res = await db_layer.search_courses(crs_code=crs_code)
                if res.get("status") == "error":
                    return res
                return XSCUtility.success_response(
                    "Courses retrieved successfully", data=res.get("data", [])
                )

        except Exception as e:
            logger.error(f"Error in courseDefinition_view: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Internal Server Error")

    @staticmethod
    async def courseDefinition_update(request, context):
        try:
            logger.info("Entering courseDefinition_update")
            payload = request.payload or {}

            errors = CurriculumValidator.validate_course_definition_update(payload)
            if errors:
                return XSCUtility.error_response("Validation failed", error_code=errors)

            db_layer = CurriculumDataLayer(context.postgres)
            crs_id = payload.get("courseDefinitionId")

            existing = await db_layer.get_course(crs_id)
            if existing.get("status") == "error":
                return existing
            if not existing.get("data") or len(existing.get("data", [])) == 0:
                return XSCUtility.error_response("Course not found", error_code="404")

            # TODO: Add update_course_root to DAO to complete implementation
            return XSCUtility.error_response(
                "Not Implemented: Course Update pending DAO support", error_code="501"
            )

        except Exception as e:
            logger.error(f"Error in courseDefinition_update: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Internal Server Error")

    @staticmethod
    async def courseDefinition_delete(request, context):
        try:
            logger.info("Entering courseDefinition_delete")
            payload = request.payload or {}
            crs_id = payload.get("courseDefinitionId")

            if not crs_id:
                return XSCUtility.error_response("Course ID is required for deletion")

            db_layer = CurriculumDataLayer(context.postgres)
            existing = await db_layer.get_course(crs_id)
            if existing.get("status") == "error":
                return existing
            if not existing.get("data") or len(existing.get("data", [])) == 0:
                return XSCUtility.error_response("Course not found", error_code="404")

            # TODO: Fetch 'Inactive' status ID dynamically from m_lookup and update course root (Gap Analysis)
            return XSCUtility.error_response(
                "Not Implemented: Course Delete pending Status Lookup integration",
                error_code="501",
            )

        except Exception as e:
            logger.error(f"Error in courseDefinition_delete: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Internal Server Error")

    # ------------------------------------------------------------
    # COURSE REQUISITE
    # ------------------------------------------------------------
    @staticmethod
    async def courseRequisite(request, context):
        match request.actionType.lower():
            case "add":
                return await sm_course.courseRequisite_add(request, context)
            case _:
                return XSCUtility.error_response(
                    "Unsupported actionType for courseRequisite. Currently only add is implemented in this phase."
                )

    @staticmethod
    async def courseRequisite_add(request, context):
        try:
            logger.info("Entering courseRequisite_add")
            payload = request.payload or {}

            errors = CurriculumValidator.validate_course_requisite_add(payload)
            if errors:
                return XSCUtility.error_response("Validation failed", error_code=errors)

            db_layer = CurriculumDataLayer(context.postgres)

            crs_version_id = payload.get("crsVersionId")
            req_crs_version_id = payload.get("requisiteCrsVersionId")
            req_type = payload.get("requisiteType")

            if crs_version_id == req_crs_version_id:
                return XSCUtility.error_response(
                    "Self-referencing requisite is not allowed"
                )

            req_payload = {
                "crs_version_id": crs_version_id,
                "status_id": payload.get("statusId"),
            }

            if req_type == "PRE":
                if await db_layer.check_prerequisite_exists(
                    crs_version_id, req_crs_version_id
                ):
                    return XSCUtility.error_response(
                        "This prerequisite relationship already exists"
                    )
                req_payload["prerequisite_crs_version_id"] = req_crs_version_id
                res = await db_layer.create_prerequisite(req_payload)
            elif req_type == "COREQ":
                if await db_layer.check_corequisite_exists(
                    crs_version_id, req_crs_version_id
                ):
                    return XSCUtility.error_response(
                        "This corequisite relationship already exists"
                    )
                req_payload["corequisite_crs_version_id"] = req_crs_version_id
                res = await db_layer.create_corequisite(req_payload)
            else:
                return XSCUtility.error_response(
                    "Invalid requisiteType. Must be PRE or COREQ"
                )

            if res.get("status") == "error":
                return res
            req_data = res.get("data", [{}])[0]
            req_id = req_data.get("id")
            return XSCUtility.success_response(
                "Course requisite added successfully", data={"requisiteId": req_id}
            )

        except Exception as e:
            logger.error(f"Error in courseRequisite_add: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Internal Server Error")

    # ------------------------------------------------------------
    # COURSE OUTCOME
    # ------------------------------------------------------------
    @staticmethod
    async def courseOutcome(request, context):
        # TODO: courseOutcome functionality cannot be implemented.
        # Gap Analysis: `tb_crs_outcome` is entirely missing from the verified database schema.
        # This endpoint is disabled until the DDL is applied.
        return XSCUtility.error_response(
            "courseOutcome is not currently supported due to pending schema upgrades."
        )
