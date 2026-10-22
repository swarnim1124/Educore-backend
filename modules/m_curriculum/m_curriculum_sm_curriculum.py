"""
File: m_curriculum_sm_curriculum.py
Description: Handler for Curriculum entity in m_curriculum. Orchestrates curriculum management
and approval workflows while delegating database access strictly to CurriculumDataLayer.

Author: Siddharth Amdal
App: OneApp

"""

import logging
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from .m_curriculum_data import CurriculumDataLayer
from .sch_curriculum import CurriculumValidator

logger = logging.getLogger(__name__)


class sm_curriculum:
    """
    Submodule handler for Curriculum-related actions (curriculumManagement, curriculumApproval).
    """

    # ------------------------------------------------------------
    # ACTION: curriculumManagement
    # ------------------------------------------------------------
    @staticmethod
    async def curriculumManagement(request, context):
        """
        Executes the `curriculumManagement()` action to process the corresponding client request.

        Args:
            request: The OneAppRequest payload containing the module, submodule, action, actionType, and payload.
            context: The ExecutionContext containing request-scoped dependencies.

        Returns:
            Standard framework response dict.
        """
        match request.actionType.lower():
            case "add":
                return await sm_curriculum.curriculumManagement_add(request, context)
            case "view":
                return await sm_curriculum.curriculumManagement_view(request, context)
            case "update":
                return await sm_curriculum.curriculumManagement_update(request, context)
            case "delete":
                return await sm_curriculum.curriculumManagement_delete(request, context)
            case _:
                return XSCUtility.error_response(
                    "Invalid actionType for curriculumManagement"
                )

    @staticmethod
    async def curriculumManagement_add(request, context):
        """
        Executes the `curriculumManagement_add()` action to create a curriculum and its structural components.

        Args:
            request: The OneAppRequest payload.
            context: The ExecutionContext containing request-scoped dependencies.

        Returns:
            - status: 'success' or 'error'.
            - message: Status details.
            - data: Created curriculum root and version IDs.

        req_json_obj expected format:
        {
            "mod": "m_curriculum",
            "subMod": "sm_curriculum",
            "action": "curriculumManagement",
            "actionType": "add",
            "payload": {
                "progId": 1,
                "currName": "B.Tech Computer Science Curriculum 2026",
                "statusId": 1,
                "terms": [
                    {
                        "termNumber": 1,
                        "totalCredits": 20.0,
                        "courses": [
                            {"crsVersionId": 101, "isMandatory": true}
                        ]
                    }
                ]
            }
        }
        """
        try:
            logger.info("Entering curriculumManagement_add")
            payload = request.payload or {}

            # 1. Payload Validation
            errors = CurriculumValidator.validate_curriculum_add(payload)
            if errors:
                return XSCUtility.error_response("Validation failed", error_code=errors)

            db_layer = CurriculumDataLayer(context.postgres)
            prog_id = payload.get("progId")
            curr_name = payload.get("currName")

            # 2. Business Logic Validation
            # Verify programme existence
            prog_res = await db_layer.get_programme(prog_id)
            if prog_res.get("status") == "error":
                return prog_res
            if not prog_res.get("data") or len(prog_res.get("data", [])) == 0:
                return XSCUtility.error_response(
                    "Specified Programme does not exist", error_code="NOT_FOUND"
                )

            # Check for duplicate curriculum name within the programme
            if await db_layer.check_curriculum_exists(prog_id, curr_name):
                return XSCUtility.error_response(
                    "A curriculum with this name already exists for the programme",
                    error_code="CONFLICT",
                )

            terms = payload.get("terms", [])
            term_numbers = []
            for t in terms:
                t_num = t.get("termNumber")
                if t_num is None:
                    return XSCUtility.error_response("Each term must have a termNumber")
                if t_num in term_numbers:
                    return XSCUtility.error_response(
                        f"Duplicate term number detected: {t_num}"
                    )
                term_numbers.append(t_num)

                courses = t.get("courses", [])
                crs_ids_in_term = []
                for c in courses:
                    c_id = c.get("crsVersionId")
                    if c_id is None:
                        return XSCUtility.error_response(
                            f"Missing crsVersionId in term {t_num}"
                        )
                    if c_id in crs_ids_in_term:
                        return XSCUtility.error_response(
                            f"Duplicate course mapping detected within term {t_num}"
                        )
                    crs_ids_in_term.append(c_id)

            # 3. Construct Payloads for Atomic DAO Execution
            root_payload = {
                "prog_id": prog_id,
                "curr_name": curr_name,
                "status_id": payload.get("statusId"),
            }

            now = XSCUtility.get_utc_timestamp()
            # TODO: Total curriculum credit calculation algorithm (master course credits vs. creditOverride) is not explicitly defined in BRS/API Contract or supported by Database Metadata (Gap Analysis). Currently summing payload term credits.
            total_credits = sum([float(t.get("totalCredits", 0)) for t in terms])
            version_payload = {
                "version_no": 1,
                "version_name": payload.get("versionName", f"{curr_name} v1.0"),
                "total_credits": total_credits,
                "effective_from": now,
                "is_current": True,
                "status_id": payload.get("statusId"),
            }

            # 4. Execute Atomic Multi-Table Transaction via DAO
            txn_resp = await db_layer.create_curriculum_full(
                root_payload, version_payload, terms
            )
            if txn_resp.get("status") == "error":
                return txn_resp

            data = txn_resp.get("data", [{}])[0]
            curr_id = data.get("curr_id")
            version_id = data.get("version_id")

            logger.info(
                f"Curriculum created successfully: root {curr_id}, version {version_id}"
            )
            return XSCUtility.success_response(
                "Curriculum created successfully",
                data={"curriculumId": curr_id, "curriculumVersionId": version_id},
            )

        except Exception as e:
            logger.error(f"Error in curriculumManagement_add: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Internal Server Error")

    @staticmethod
    async def curriculumManagement_view(request, context):
        """
        Executes the `curriculumManagement_view()` action to retrieve curricula.
        """
        try:
            logger.info("Entering curriculumManagement_view")
            payload = request.payload or {}
            db_layer = CurriculumDataLayer(context.postgres)

            curr_id = payload.get("currId")
            if curr_id:
                res = await db_layer.get_curriculum(curr_id)
                if res.get("status") == "error":
                    return res
                if not res.get("data") or len(res.get("data", [])) == 0:
                    return XSCUtility.error_response(
                        "Curriculum not found", error_code="NOT_FOUND"
                    )
                return XSCUtility.success_response(
                    "Curriculum retrieved successfully", data=res.get("data")[0]
                )
            else:
                prog_id = payload.get("progId")
                res = await db_layer.search_curricula(prog_id=prog_id)
                if res.get("status") == "error":
                    return res
                return XSCUtility.success_response(
                    "Curricula retrieved successfully", data=res.get("data", [])
                )

        except Exception as e:
            logger.error(f"Error in curriculumManagement_view: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Internal Server Error")

    @staticmethod
    async def curriculumManagement_update(request, context):
        """
        Executes the `curriculumManagement_update()` action to update a curriculum.
        """
        try:
            logger.info("Entering curriculumManagement_update")
            payload = request.payload or {}

            errors = CurriculumValidator.validate_curriculum_update(payload)
            if errors:
                return XSCUtility.error_response("Validation failed", error_code=errors)

            db_layer = CurriculumDataLayer(context.postgres)
            curr_id = payload.get("currId")

            existing = await db_layer.get_curriculum(curr_id)
            if existing.get("status") == "error":
                return existing
            if not existing.get("data") or len(existing.get("data", [])) == 0:
                return XSCUtility.error_response(
                    "Curriculum not found", error_code="NOT_FOUND"
                )

            # TODO: Implement multi-table update logic across tb_curr, tb_curr_version, tb_curr_term, tb_curr_term_crs (pending full DAO update support and status resolution)
            return XSCUtility.error_response(
                "Not Implemented: Curriculum Management (Update) pending DAO and Status Lookup support",
                error_code="501",
            )

        except Exception as e:
            logger.error(
                f"Error in curriculumManagement_update: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response("Internal Server Error")

    @staticmethod
    async def curriculumManagement_delete(request, context):
        """
        Executes the `curriculumManagement_delete()` action to remove a draft curriculum.
        """
        try:
            logger.info("Entering curriculumManagement_delete")
            payload = request.payload or {}

            errors = CurriculumValidator.validate_curriculum_delete(payload)
            if errors:
                return XSCUtility.error_response("Validation failed", error_code=errors)

            db_layer = CurriculumDataLayer(context.postgres)
            curr_id = payload.get("currId")

            existing = await db_layer.get_curriculum(curr_id)
            if existing.get("status") == "error":
                return existing
            if not existing.get("data") or len(existing.get("data", [])) == 0:
                return XSCUtility.error_response(
                    "Curriculum not found", error_code="404"
                )

            # TODO: Fetch 'Inactive' / 'Deleted' status ID dynamically from m_lookup or perform draft deletion (Gap Analysis)
            return XSCUtility.error_response(
                "Not Implemented: Curriculum Management (Delete) pending Status Lookup integration",
                error_code="501",
            )

        except Exception as e:
            logger.error(
                f"Error in curriculumManagement_delete: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response("Internal Server Error")

    # ------------------------------------------------------------
    # ACTION: curriculumApproval
    # ------------------------------------------------------------
    @staticmethod
    async def curriculumApproval(request, context):
        """
        Executes the `curriculumApproval()` action to process curriculum approval workflows.
        """
        match request.actionType.lower():
            case "add":
                return await sm_curriculum.curriculumApproval_add(request, context)
            case "view":
                return await sm_curriculum.curriculumApproval_view(request, context)
            case "update":
                return await sm_curriculum.curriculumApproval_update(request, context)
            case "delete":
                return await sm_curriculum.curriculumApproval_delete(request, context)
            case _:
                return XSCUtility.error_response(
                    "Invalid actionType for curriculumApproval"
                )

    @staticmethod
    async def curriculumApproval_add(request, context):
        """
        Executes the `curriculumApproval_add()` action to approve a curriculum version.
        """
        try:
            logger.info("Entering curriculumApproval_add")
            payload = request.payload or {}

            errors = CurriculumValidator.validate_curriculum_approval(payload)
            if errors:
                return XSCUtility.error_response("Validation failed", error_code=errors)

            db_layer = CurriculumDataLayer(context.postgres)
            version_id = payload.get("currVersionId")

            existing = await db_layer.get_curriculum_version(version_id)
            if existing.get("status") == "error":
                return existing
            if not existing.get("data") or len(existing.get("data", [])) == 0:
                return XSCUtility.error_response(
                    "Curriculum version not found", error_code="NOT_FOUND"
                )

            # TODO: Resolve 'Approved' status ID dynamically from m_lookup and update curriculum version (Gap Analysis)
            return XSCUtility.error_response(
                "Not Implemented: Curriculum Approval (Add) pending Status Lookup integration",
                error_code="501",
            )

        except Exception as e:
            logger.error(f"Error in curriculumApproval_add: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Internal Server Error")

    @staticmethod
    async def curriculumApproval_view(request, context):
        """
        Executes the `curriculumApproval_view()` action to retrieve the curriculum approval queue.
        """
        try:
            logger.info("Entering curriculumApproval_view")
            payload = request.payload or {}
            db_layer = CurriculumDataLayer(context.postgres)

            status_filter = payload.get("statusFilter")
            res = await db_layer.get_curriculum_approvals(status_filter=status_filter)
            if res.get("status") == "error":
                return res
            return XSCUtility.success_response(
                "Curriculum approvals retrieved successfully", data=res.get("data", [])
            )

        except Exception as e:
            logger.error(f"Error in curriculumApproval_view: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Internal Server Error")

    @staticmethod
    async def curriculumApproval_update(request, context):
        """
        Executes the `curriculumApproval_update()` action to modify an approval decision or request revision.
        """
        try:
            logger.info("Entering curriculumApproval_update")
            payload = request.payload or {}

            errors = CurriculumValidator.validate_curriculum_approval(payload)
            if errors:
                return XSCUtility.error_response("Validation failed", error_code=errors)

            db_layer = CurriculumDataLayer(context.postgres)
            version_id = payload.get("currVersionId")

            existing = await db_layer.get_curriculum_version(version_id)
            if existing.get("status") == "error":
                return existing
            if not existing.get("data") or len(existing.get("data", [])) == 0:
                return XSCUtility.error_response(
                    "Curriculum version not found", error_code="NOT_FOUND"
                )

            # TODO: Resolve 'In Revision' status ID dynamically from m_lookup (Gap Analysis)
            return XSCUtility.error_response(
                "Not Implemented: Curriculum Approval (Update) pending Status Lookup integration",
                error_code="501",
            )

        except Exception as e:
            logger.error(f"Error in curriculumApproval_update: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Internal Server Error")

    @staticmethod
    async def curriculumApproval_delete(request, context):
        """
        Executes the `curriculumApproval_delete()` action to reject a curriculum version.
        """
        try:
            logger.info("Entering curriculumApproval_delete")
            payload = request.payload or {}

            errors = CurriculumValidator.validate_curriculum_approval(payload)
            if errors:
                return XSCUtility.error_response("Validation failed", error_code=errors)

            db_layer = CurriculumDataLayer(context.postgres)
            version_id = payload.get("currVersionId")

            existing = await db_layer.get_curriculum_version(version_id)
            if existing.get("status") == "error":
                return existing
            if not existing.get("data") or len(existing.get("data", [])) == 0:
                return XSCUtility.error_response(
                    "Curriculum version not found", error_code="NOT_FOUND"
                )

            # TODO: Resolve 'Rejected' status ID dynamically from m_lookup (Gap Analysis)
            return XSCUtility.error_response(
                "Not Implemented: Curriculum Approval (Delete) pending Status Lookup integration",
                error_code="501",
            )

        except Exception as e:
            logger.error(f"Error in curriculumApproval_delete: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Internal Server Error")
