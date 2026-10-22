"""
File: m_curriculum_sm_programme.py
Description: Handler for Programme entity in m_curriculum.

Author: Siddharth Amdal
App: OneApp

"""

import logging
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from .m_curriculum_data import CurriculumDataLayer
from .sch_curriculum import CurriculumValidator

logger = logging.getLogger(__name__)


class sm_programme:
    """
    Submodule handler for Programme-related actions.
    """

    @staticmethod
    async def programme(request, context):
        """
        Executes the `programme()` action to process the corresponding client request.

        Args:
            request: The OneAppRequest payload containing the module, submodule, action, actionType, and payload.
            context: The ExecutionContext containing request-scoped dependencies.

        Returns:
            Standard framework response dict.
        """
        match request.actionType.lower():
            case "add":
                return await sm_programme.programme_add(request, context)
            case "view":
                return await sm_programme.programme_view(request, context)
            case "update":
                return await sm_programme.programme_update(request, context)
            case "delete":
                return await sm_programme.programme_delete(request, context)
            case _:
                return XSCUtility.error_response("Invalid actionType")

    @staticmethod
    async def programme_add(request, context):
        try:
            logger.info("Entering programme_add")
            payload = request.payload or {}

            # 1. Validate Payload
            errors = CurriculumValidator.validate_programme_add(payload)
            if errors:
                logger.warning(f"Validation failed for programme_add: {errors}")
                return XSCUtility.error_response("Validation failed", error_code=errors)

            db_layer = CurriculumDataLayer(context.postgres)

            # 2. Business Validation
            inst_id = payload.get("institutionId")
            dept_id = payload.get("departmentId")
            prog_code = payload.get("progCode")
            prog_name = payload.get("progName")

            exists = await db_layer.check_programme_exists(
                inst_id, prog_code, prog_name
            )
            if exists:
                logger.warning(
                    f"Duplicate programme detected: inst={inst_id}, code={prog_code}"
                )
                return XSCUtility.error_response(
                    "Programme with this code or name already exists in the institution"
                )

            # TODO: Cross-module existence checks for inst_id, dept_id, progTypeId could be added here

            # 3. Execute DB Operation
            db_payload = {
                "institution_id": inst_id,
                "department_id": dept_id,
                "prog_type_id": payload.get("progTypeId"),
                "prog_code": prog_code,
                "prog_name": prog_name,
                "duration": payload.get("duration"),
                "duration_unit_id": payload.get("durationUnitId"),
                "total_terms": payload.get("totalTerms"),
                "total_credits": payload.get("totalCredits"),
                "status_id": payload.get(
                    "statusId"
                ),  # TODO: Resolve default 'Active' status from m_lookup if not provided
            }

            res = await db_layer.create_programme(db_payload)
            if res.get("status") == "error":
                return res
            prog_data = res.get("data", [{}])[0]
            prog_id = prog_data.get("id")
            logger.info(f"Programme created successfully with id {prog_id}")

            return XSCUtility.success_response(
                "Programme created successfully", data={"id": prog_id}
            )

        except Exception as e:
            logger.error(f"Error in programme_add: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Internal Server Error")

    @staticmethod
    async def programme_view(request, context):
        try:
            logger.info("Entering programme_view")
            payload = request.payload or {}
            db_layer = CurriculumDataLayer(context.postgres)

            prog_id = payload.get("programmeId")

            if prog_id:
                # View single programme
                res = await db_layer.get_programme(prog_id)
                if res.get("status") == "error":
                    return res
                records = res.get("data", [])
                if not records:
                    return XSCUtility.error_response(
                        "Programme not found", error_code="404"
                    )
                return XSCUtility.success_response(
                    "Programme retrieved successfully", data=records[0]
                )
            else:
                # Search programmes
                inst_id = payload.get("institutionId")
                dept_id = payload.get("departmentId")
                res = await db_layer.search_programmes(inst_id, dept_id)
                if res.get("status") == "error":
                    return res
                return XSCUtility.success_response(
                    "Programmes retrieved successfully", data=res.get("data", [])
                )

        except Exception as e:
            logger.error(f"Error in programme_view: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Internal Server Error")

    @staticmethod
    async def programme_update(request, context):
        try:
            logger.info("Entering programme_update")
            payload = request.payload or {}
            prog_id = payload.get("programmeId")

            if not prog_id:
                return XSCUtility.error_response("Programme ID is required for update")

            db_layer = CurriculumDataLayer(context.postgres)

            # Check if exists
            existing = await db_layer.get_programme(prog_id)
            if existing.get("status") == "error":
                return existing
            if not existing.get("data") or len(existing.get("data", [])) == 0:
                return XSCUtility.error_response(
                    "Programme not found", error_code="404"
                )

            # Build update payload (only include provided fields)
            # Note: progCode, progTypeId, duration, durationUnitId, departmentId,
            # and institutionId are immutable according to the API Contract.
            update_payload = {}
            if "progName" in payload:
                update_payload["prog_name"] = payload.get("progName")
            if "totalTerms" in payload:
                update_payload["total_terms"] = payload.get("totalTerms")
            if "totalCredits" in payload:
                update_payload["total_credits"] = payload.get("totalCredits")
            if "statusId" in payload:
                update_payload["status_id"] = payload.get("statusId")

            if not update_payload:
                return XSCUtility.error_response("No valid fields provided for update")

            res = await db_layer.update_programme(prog_id, update_payload)
            if res.get("status") == "error":
                return res
            logger.info(f"Programme {prog_id} updated successfully")

            return XSCUtility.success_response("Programme updated successfully")

        except Exception as e:
            logger.error(f"Error in programme_update: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Internal Server Error")

    @staticmethod
    async def programme_delete(request, context):
        try:
            logger.info("Entering programme_delete")
            payload = request.payload or {}
            prog_id = payload.get("programmeId")

            if not prog_id:
                return XSCUtility.error_response(
                    "Programme ID is required for deletion"
                )

            db_layer = CurriculumDataLayer(context.postgres)

            # Verify existence
            existing = await db_layer.get_programme(prog_id)
            if existing.get("status") == "error":
                return existing
            if not existing.get("data") or len(existing.get("data", [])) == 0:
                return XSCUtility.error_response(
                    "Programme not found", error_code="404"
                )

            # Soft delete by updating status_id to inactive
            # TODO: Fetch 'Inactive' status ID dynamically from m_lookup instead of hardcoding (Gap Analysis)
            # await db_layer.update_programme(prog_id, {"status_id": INACTIVE_STATUS_ID})
            logger.info(f"Programme {prog_id} soft-deleted successfully")

            return XSCUtility.success_response("Programme deleted successfully")

        except Exception as e:
            logger.error(f"Error in programme_delete: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Internal Server Error")
