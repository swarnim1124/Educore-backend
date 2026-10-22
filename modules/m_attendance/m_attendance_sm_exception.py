"""
File: m_attendance_sm_exception.py
Description: Submodule business logic handler for attendance date-range exceptions (medical leave, sports representation) and exception approvals.
Encapsulates date-range exception overrides across multiple class sessions inside atomic transactions and retroactive exception revocations.

Author: Siddharth Amdal
App: OneApp

"""

import logging
from typing import Dict, Any
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from .m_attendance_data import AttendanceDataLayer

logger = logging.getLogger(__name__)


class sm_exception:
    """
    Submodule handler for attendance date-range exception requests and exception approval/override workflows.
    Enforces atomic multi-table overrides and semantic revocations that restore original attendance states.
    """

    @staticmethod
    async def attendanceException(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes the `attendanceException()` action to submit, view, modify, or withdraw date-range attendance exceptions.
        Supports retroactive exception revocation inside explicit async transactions when withdrawing an approved exception.

        Args:
            self: Reference to the current class instance.
            request: The OneAppRequest payload containing the module, submodule, action, actionType, and payload.
            context: The ExecutionContext containing request-scoped dependencies (e.g. PostgreSQLManager instance, logger, user_id).

        Returns:
            - status: Indicates whether the request was processed successfully ('success') or failed ('error').
            - message: A human-readable string providing details about the execution status.
            - data: The core data payload returned by the operation (e.g. database records).

        req_json_obj expected format:
        {
            "mod": "m_attendance",
            "subMod": "sm_exception",
            "action": "attendanceException",
            "actionType": "<add|view|update|delete>",
            "payload": {
                "studId": 101,
                "startDate": "2026-08-01",
                "endDate": "2026-08-05",
                "reason": "National University Sports Tournament Representation",
                "docPath": "/uploads/med_proof_101.pdf"
            }
        }
        """
        action_type = (request.actionType or "").lower()
        match action_type:
            case "add":
                return await sm_exception.exc_add(request, context)
            case "view":
                return await sm_exception.exc_view(request, context)
            case "update":
                return await sm_exception.exc_update(request, context)
            case "delete":
                return await sm_exception.exc_delete(request, context)
            case _:
                logger.warning(
                    f"[sm_exception] Invalid actionType received for attendanceException: {action_type}"
                )
                return XSCUtility.error_response(
                    "Invalid actionType for attendanceException",
                    error_code="INVALID_ACTION_TYPE",
                )

    @staticmethod
    async def exceptionApproval(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes the `exceptionApproval()` action to approve or reject date-range attendance exceptions.
        When approved, triggers atomic date-range exception overrides across all matching class sessions.
        When rejected or revoked, executes a semantic rejection to preserve audit compliance.

        Args:
            self: Reference to the current class instance.
            request: The OneAppRequest payload containing the module, submodule, action, actionType, and payload.
            context: The ExecutionContext containing request-scoped dependencies (e.g. PostgreSQLManager instance, logger, user_id).

        Returns:
            - status: Indicates whether the request was processed successfully ('success') or failed ('error').
            - message: A human-readable string providing details about the execution status.
            - data: The core data payload returned by the operation (e.g. database records).

        req_json_obj expected format:
        {
            "mod": "m_attendance",
            "subMod": "sm_exception",
            "action": "exceptionApproval",
            "actionType": "<add|view|update|delete>",
            "payload": {
                "exceptionId": 300,
                "decision": "APPROVE",
                "comments": "Verified official sports participation letter."
            }
        }
        """
        action_type = (request.actionType or "").lower()
        match action_type:
            case "add" | "update":
                return await sm_exception.appr_update(request, context)
            case "view":
                return await sm_exception.exc_view(request, context)
            case "delete":
                return await sm_exception.appr_delete(request, context)
            case _:
                logger.warning(
                    f"[sm_exception] Invalid actionType received for exceptionApproval: {action_type}"
                )
                return XSCUtility.error_response(
                    "Invalid actionType for exceptionApproval",
                    error_code="INVALID_ACTION_TYPE",
                )

    # =========================================================================
    # INTERNAL HANDLERS FOR attendanceException
    # =========================================================================

    @staticmethod
    async def exc_add(request: Any, context: Any) -> Dict[str, Any]:
        """
        Submits a new date-range attendance exception request.
        Stores in tb_att_correction with correction_type = 'DATE_RANGE_EXCEPTION' and encodes start/end dates in reason/metadata.
        """
        try:
            payload = request.payload or {}
            stud_id = payload.get("studId")
            start_date = payload.get("startDate")
            end_date = payload.get("endDate")
            reason = payload.get("reason")
            doc_path = payload.get("docPath")

            if not stud_id or not start_date or not end_date or not reason:
                return XSCUtility.error_response(
                    "Mandatory fields missing: studId, startDate, endDate, and reason required for exception.",
                    error_code="VAL_MISSING_FIELDS",
                )

            if str(end_date) < str(start_date):
                return XSCUtility.error_response(
                    "Validation failed: endDate cannot be earlier than startDate.",
                    error_code="VAL_DATE_ORDER",
                )

            db_layer = AttendanceDataLayer(context.postgres)
            status_res = await db_layer.resolve_lookup_id_by_code(
                "PENDING_EXCEPTION", default_id=30
            )
            pending_status_id = status_res["data"][0]["id"]

            user_id = getattr(context, "user_id", None) or payload.get("userId") or 0
            # Store date range metadata clearly in correction reason / remarks
            full_reason = f"[RANGE: {start_date} to {end_date}] {reason}"
            if doc_path:
                full_reason += f" [DOC: {doc_path}]"

            # We use a dummy session ID or 0 for multi-session date range exceptions if not bound to a single session
            payload.get("attSessionId") or payload.get("sessionId") or 0

            res = await db_layer.create_exception_request(
                stud_id=int(stud_id),
                start_date=str(start_date),
                end_date=str(end_date),
                reason=str(reason),
                doc_path=doc_path,
                user_id=int(user_id),
                pending_status_id=int(pending_status_id),
            )
            if res.get("status") == "error":
                return res
            logger.info(
                f"[sm_exception] Date-range exception request submitted for student {stud_id}"
            )
            return XSCUtility.success_response(
                "Date-range exception request submitted successfully",
                data=res.get("data", []),
            )
        except Exception as e:
            logger.error(f"[sm_exception] Error in _exc_add: {str(e)}", exc_info=True)
            return XSCUtility.error_response(
                "Internal Server Error in _exc_add", error_code="ERR_SYS"
            )

    @staticmethod
    async def exc_view(request: Any, context: Any) -> Dict[str, Any]:
        """
        Retrieves date-range exception requests by ID or lists all requests for a student/course.
        """
        try:
            payload = request.payload or {}
            db_layer = AttendanceDataLayer(context.postgres)
            exc_id = payload.get("exceptionId") or payload.get("correctionId")

            if exc_id:
                res = await db_layer.get_correction(int(exc_id))
                if res.get("status") == "error" or not res.get("data"):
                    return XSCUtility.error_response(
                        f"Exception request not found with ID {exc_id}",
                        error_code="ERR_NOT_FOUND",
                    )
                return XSCUtility.success_response(
                    "Exception request retrieved successfully", data=res.get("data", [])
                )

            stud_id = payload.get("studId")
            payload.get("limit", 100)
            payload.get("offset", 0)

            res = await db_layer.list_exceptions(
                stud_id=int(stud_id) if stud_id else None
            )
            if res.get("status") == "error":
                return res
            return XSCUtility.success_response(
                "Exception requests retrieved successfully", data=res.get("data", [])
            )
        except Exception as e:
            logger.error(f"[sm_exception] Error in _exc_view: {str(e)}", exc_info=True)
            return XSCUtility.error_response(
                "Internal Server Error in _exc_view", error_code="ERR_SYS"
            )

    @staticmethod
    async def exc_update(request: Any, context: Any) -> Dict[str, Any]:
        """
        Modifies an unapproved exception request (e.g., updating reason or date range).
        """
        try:
            payload = request.payload or {}
            exc_id = payload.get("exceptionId") or payload.get("correctionId")
            if not exc_id:
                return XSCUtility.error_response(
                    "Mandatory field missing: exceptionId required for update.",
                    error_code="VAL_MISSING_ID",
                )

            db_layer = AttendanceDataLayer(context.postgres)
            exist_res = await db_layer.get_correction(int(exc_id))
            if exist_res.get("status") == "error" or not exist_res.get("data"):
                return XSCUtility.error_response(
                    "Exception request not found.", error_code="ERR_NOT_FOUND"
                )

            update_data = {}
            if "reason" in payload:
                update_data["remarks"] = f"[EXCEPTION] {payload['reason']}"

            if not update_data:
                return XSCUtility.error_response(
                    "No valid fields provided for update.",
                    error_code="VAL_NO_UPDATE_FIELDS",
                )

            res = await db_layer.update_correction(int(exc_id), update_data)
            if res.get("status") == "error":
                return res
            return XSCUtility.success_response(
                "Exception request updated successfully", data=res.get("data", [])
            )
        except Exception as e:
            logger.error(
                f"[sm_exception] Error in _exc_update: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response(
                "Internal Server Error in _exc_update", error_code="ERR_SYS"
            )

    @staticmethod
    async def exc_delete(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes a Semantic Withdrawal / Revocation of a date-range exception.
        If the exception was previously approved, invokes revoke_exception_atomically inside an explicit
        async transaction to revert any associated attendance records back to ABSENT/unexcused.
        This is a semantic operation and not a SQL physical DELETE operation.
        """
        try:
            payload = request.payload or {}
            exc_id = payload.get("exceptionId") or payload.get("correctionId")
            reason = (
                payload.get("reason")
                or "Exception request withdrawn/revoked by user or administrator"
            )

            if not exc_id:
                return XSCUtility.error_response(
                    "Mandatory field missing: exceptionId required for withdrawal.",
                    error_code="VAL_MISSING_ID",
                )

            db_layer = AttendanceDataLayer(context.postgres)
            status_res = await db_layer.resolve_lookup_id_by_code(
                "REVOKED_EXCEPTION", default_id=33
            )
            revoked_status_id = status_res["data"][0]["id"]

            revert_res = await db_layer.resolve_lookup_id_by_code(
                "ABSENT", default_id=11
            )
            revert_status_id = revert_res["data"][0]["id"]

            user_id = getattr(context, "user_id", None) or payload.get("userId") or 0
            res = await db_layer.revoke_exception_request(
                int(exc_id),
                int(user_id),
                str(reason),
                revoked_status_id,
                revert_status_id,
            )
            if res.get("status") == "error":
                return res
            logger.info(
                f"[sm_exception] Exception {exc_id} semantically revoked/withdrawn"
            )
            return XSCUtility.success_response(
                "Exception request withdrawn/revoked successfully (semantic delete)",
                data=res.get("data", []),
            )
        except Exception as e:
            logger.error(
                f"[sm_exception] Error in _exc_delete: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response(
                "Internal Server Error in _exc_delete", error_code="ERR_SYS"
            )

    # =========================================================================
    # INTERNAL HANDLERS FOR exceptionApproval
    # =========================================================================

    @staticmethod
    async def appr_update(request: Any, context: Any) -> Dict[str, Any]:
        """
        Approves or rejects a date-range attendance exception.
        When approved (APPROVE), invokes apply_date_range_exception_atomically inside an explicit async transaction
        to override existing attendance records within the date range to APPROVED_EXCEPTION.
        """
        try:
            payload = request.payload or {}
            exc_id = payload.get("exceptionId") or payload.get("correctionId")
            decision = str(payload.get("decision", "")).upper()
            comments = payload.get("comments") or payload.get("reason")

            if not exc_id or decision not in ("APPROVE", "REJECT") or not comments:
                return XSCUtility.error_response(
                    "Mandatory fields missing: exceptionId, decision (APPROVE/REJECT), and comments required.",
                    error_code="VAL_MISSING_FIELDS",
                )

            db_layer = AttendanceDataLayer(context.postgres)
            user_id = getattr(context, "user_id", None) or payload.get("userId") or 0

            if decision == "APPROVE":
                status_res = await db_layer.resolve_lookup_id_by_code(
                    "APPROVED_EXCEPTION", default_id=31
                )
                status_id = status_res["data"][0]["id"]
            else:
                status_res = await db_layer.resolve_lookup_id_by_code(
                    "REJECTED_EXCEPTION", default_id=32
                )
                status_id = status_res["data"][0]["id"]

            res = await db_layer.approve_exception_request(
                int(exc_id), int(user_id), decision, str(comments), status_id
            )

            if res.get("status") == "error":
                return res
            logger.info(
                f"[sm_exception] Exception approval {exc_id} processed with decision {decision}"
            )
            return XSCUtility.success_response(
                f"Date-range exception {decision.lower()}d successfully",
                data=res.get("data", []),
            )
        except Exception as e:
            logger.error(
                f"[sm_exception] Error in _appr_update: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response(
                "Internal Server Error in _appr_update", error_code="ERR_SYS"
            )

    @staticmethod
    async def appr_delete(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes a Semantic Rejection / Cancellation on an exception approval.
        Preserves the audit log while revoking approved status.
        """
        return await sm_exception._exc_delete(request, context)
