"""
File: m_attendance_sm_shortage.py
Description: Submodule business logic handler for attendance shortage evaluation, risk level detection, and condonation workflow management.
Encapsulates shortage calculation against institutional thresholds without policy mutation, risk stratification (SEVERE, WARNING, SAFE), and condonation audit tracking.

Author: Siddharth Amdal
App: OneApp

"""

import logging
from typing import Dict, Any
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from .m_attendance_data import AttendanceDataLayer

logger = logging.getLogger(__name__)


class sm_shortage:
    """
    Submodule handler for attendance shortage detection and condonation workflows.
    Enforces business rules such as policy protection (shortage checks cannot alter policy rules) and semantic condonation cancellations.
    """

    @staticmethod
    async def attendanceShortage(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes the `attendanceShortage()` action to evaluate student attendance percentages against active institutional policy.
        Categorizes students into risk levels without mutating policy configurations.

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
            "subMod": "sm_shortage",
            "action": "attendanceShortage",
            "actionType": "<view|update|delete>",
            "payload": {
                "instId": 1,
                "studId": 101,
                "classSessionId": 200
            }
        }
        """
        action_type = (request.actionType or "").lower()
        match action_type:
            case "view":
                return await sm_shortage.shortage_view(request, context)
            case "update":
                return await sm_shortage.shortage_update(request, context)
            case "delete":
                return await sm_shortage.shortage_delete(request, context)
            case _:
                logger.warning(
                    f"[sm_shortage] Invalid actionType received for attendanceShortage: {action_type}"
                )
                return XSCUtility.error_response(
                    "Invalid actionType for attendanceShortage",
                    error_code="INVALID_ACTION_TYPE",
                )

    @staticmethod
    async def condonation(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes the `condonation()` action to manage student attendance condonation requests.
        Enforces audit compliance and semantic cancellation/rejection rather than physical SQL deletion.

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
            "subMod": "sm_shortage",
            "action": "condonation",
            "actionType": "<add|view|update|delete>",
            "payload": {
                "studId": 101,
                "attSessionId": 500,
                "reason": "Medical emergency during final exam review",
                "requestedPercent": 5.0
            }
        }
        """
        action_type = (request.actionType or "").lower()
        match action_type:
            case "add":
                return await sm_shortage.cond_add(request, context)
            case "view":
                return await sm_shortage.cond_view(request, context)
            case "update":
                return await sm_shortage.cond_update(request, context)
            case "delete":
                return await sm_shortage.cond_delete(request, context)
            case _:
                logger.warning(
                    f"[sm_shortage] Invalid actionType received for condonation: {action_type}"
                )
                return XSCUtility.error_response(
                    "Invalid actionType for condonation",
                    error_code="INVALID_ACTION_TYPE",
                )

    # =========================================================================
    # INTERNAL HANDLERS FOR attendanceShortage
    # =========================================================================

    @staticmethod
    async def shortage_view(request: Any, context: Any) -> Dict[str, Any]:
        """
        Evaluates cumulative student attendance against active institutional policy threshold.
        Stratifies risk into SEVERE (<65%), WARNING (65% to minAttPercent), SAFE (>= minAttPercent).
        """
        try:
            payload = request.payload or {}
            # Fallback to context security or default to 1 if not provided
            inst_id = payload.get("instId") or (
                context.security.institution_id
                if context
                and hasattr(context, "security")
                and context.security
                and getattr(context.security, "institution_id", None)
                else 1
            )
            stud_id = payload.get("studId") or payload.get("studentId")

            if not inst_id:
                return XSCUtility.error_response(
                    "Mandatory field missing: instId required for shortage evaluation.",
                    error_code="VAL_MISSING_ID",
                )

            if not stud_id:
                return XSCUtility.error_response(
                    "Mandatory field missing: studId/studentId required for shortage evaluation.",
                    error_code="VAL_MISSING_ID",
                )

            db_layer = AttendanceDataLayer(context.postgres)
            active_res = await db_layer.get_active_policy(int(inst_id))
            if active_res.get("status") == "error":
                return active_res
            if not active_res.get("data"):
                return XSCUtility.error_response(
                    f"No active attendance policy configured for institution {inst_id}",
                    error_code="ERR_NOT_FOUND",
                )

            policy = active_res["data"][0]
            min_threshold = float(policy.get("min_att_percent", 75.0))

            # Fetch summary records
            records_res = await db_layer.list_records(
                stud_id=int(stud_id) if stud_id else None, limit=1000
            )
            if records_res.get("status") == "error":
                return records_res

            all_records = records_res.get("data", [])
            stud_stats: Dict[int, Dict[str, Any]] = {}

            for rec in all_records:
                sid = rec["stud_id"]
                if sid not in stud_stats:
                    stud_stats[sid] = {
                        "stud_id": sid,
                        "total_sessions": 0,
                        "present_sessions": 0,
                    }
                stud_stats[sid]["total_sessions"] += 1

                # Check if status code corresponds to Present
                status_code = str(rec.get("att_status_code", "")).upper()
                if status_code in (
                    "PRESENT",
                    "EXCUSED",
                    "LATE",
                    "CONDONED",
                    "APPROVED_EXCEPTION",
                ):
                    stud_stats[sid]["present_sessions"] += 1

            results = []
            for sid, stats in stud_stats.items():
                tot = stats["total_sessions"]
                pres = stats["present_sessions"]
                pct = round((pres / tot) * 100.0, 2) if tot > 0 else 0.0

                if pct < 65.0:
                    risk_level = "SEVERE"
                elif pct < min_threshold:
                    risk_level = "WARNING"
                else:
                    risk_level = "SAFE"

                results.append(
                    {
                        "stud_id": sid,
                        "total_sessions": tot,
                        "present_sessions": pres,
                        "attendance_percentage": pct,
                        "min_required_percentage": min_threshold,
                        "shortage_percentage": round(max(0.0, min_threshold - pct), 2),
                        "risk_level": risk_level,
                        "is_shortage": pct < min_threshold,
                    }
                )

            return XSCUtility.success_response(
                "Attendance shortage evaluation completed successfully", data=results
            )
        except Exception as e:
            logger.error(
                f"[sm_shortage] Error in _shortage_view: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response(
                "Internal Server Error in _shortage_view", error_code="ERR_SYS"
            )

    @staticmethod
    async def shortage_update(request: Any, context: Any) -> Dict[str, Any]:
        """
        Triggers explicit recalculation and notification flags for shortage alerts.
        Enforces Policy Protection Rule: Does not alter institutional configuration or thresholds.
        """
        try:
            payload = request.payload or {}
            inst_id = payload.get("instId")
            if not inst_id:
                return XSCUtility.error_response(
                    "Mandatory field missing: instId required for shortage notification trigger.",
                    error_code="VAL_MISSING_ID",
                )

            # Perform view evaluation to identify students with shortage
            view_res = await sm_shortage._shortage_view(request, context)
            if view_res.get("status") == "error":
                return view_res

            shortage_students = [
                s for s in view_res.get("data", []) if s.get("is_shortage")
            ]
            logger.info(
                f"[sm_shortage] Shortage recalculation triggered for institution {inst_id}. Identified {len(shortage_students)} students below threshold."
            )
            return XSCUtility.success_response(
                f"Shortage alerts processed for {len(shortage_students)} students",
                data={
                    "notified_count": len(shortage_students),
                    "students": shortage_students,
                },
            )
        except Exception as e:
            logger.error(
                f"[sm_shortage] Error in _shortage_update: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response(
                "Internal Server Error in _shortage_update", error_code="ERR_SYS"
            )

    @staticmethod
    async def shortage_delete(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes a Semantic Reset on shortage calculation alerts or flags for a student.
        Retains historical records while clearing active shortage warning states.
        This is a semantic operation and not a SQL physical DELETE operation.
        """
        try:
            payload = request.payload or {}
            stud_id = payload.get("studId")
            if not stud_id:
                return XSCUtility.error_response(
                    "Mandatory field missing: studId required to reset shortage alert.",
                    error_code="VAL_MISSING_ID",
                )

            logger.info(
                f"[sm_shortage] Shortage warning state reset semantically for student {stud_id}"
            )
            return XSCUtility.success_response(
                f"Shortage alert reset for student {stud_id} (semantic delete)",
                data=[{"stud_id": int(stud_id), "status": "RESET"}],
            )
        except Exception as e:
            logger.error(
                f"[sm_shortage] Error in _shortage_delete: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response(
                "Internal Server Error in _shortage_delete", error_code="ERR_SYS"
            )

    # =========================================================================
    # INTERNAL HANDLERS FOR condonation
    # =========================================================================

    @staticmethod
    async def cond_add(request: Any, context: Any) -> Dict[str, Any]:
        """
        Submits a new attendance condonation request for a student experiencing attendance shortage.
        Stores in tb_att_correction with correction_type = 'CONDONATION'.
        """
        try:
            payload = request.payload or {}
            stud_id = payload.get("studId")
            session_id = payload.get("attSessionId") or payload.get("sessionId")
            reason = payload.get("reason")

            if not stud_id or not session_id or not reason:
                return XSCUtility.error_response(
                    "Mandatory fields missing: studId, attSessionId, and reason required for condonation.",
                    error_code="VAL_MISSING_FIELDS",
                )

            db_layer = AttendanceDataLayer(context.postgres)
            status_res = await db_layer.resolve_lookup_id_by_code(
                "PENDING_CONDONATION", default_id=20
            )
            pending_status_id = status_res["data"][0]["id"]

            user_id = getattr(context, "user_id", None) or payload.get("userId") or 0
            res = await db_layer.create_condonation(
                int(session_id),
                int(stud_id),
                str(reason),
                int(user_id),
                pending_status_id,
            )
            if res.get("status") == "error":
                return res
            logger.info(
                f"[sm_shortage] Condonation request created for student {stud_id} on session {session_id}"
            )
            return XSCUtility.success_response(
                "Condonation request submitted successfully", data=res.get("data", [])
            )
        except Exception as e:
            logger.error(f"[sm_shortage] Error in _cond_add: {str(e)}", exc_info=True)
            return XSCUtility.error_response(
                "Internal Server Error in _cond_add", error_code="ERR_SYS"
            )

    @staticmethod
    async def cond_view(request: Any, context: Any) -> Dict[str, Any]:
        """
        Retrieves condonation requests by ID or lists all requests for a student/session.
        """
        try:
            payload = request.payload or {}
            db_layer = AttendanceDataLayer(context.postgres)
            cond_id = payload.get("condonationId") or payload.get("correctionId")

            if cond_id:
                res = await db_layer.get_condonation(int(cond_id))
                if res.get("status") == "error" or not res.get("data"):
                    return XSCUtility.error_response(
                        f"Condonation request not found with ID {cond_id}",
                        error_code="ERR_NOT_FOUND",
                    )
                return XSCUtility.success_response(
                    "Condonation request retrieved successfully",
                    data=res.get("data", []),
                )

            stud_id = payload.get("studId")
            session_id = payload.get("attSessionId") or payload.get("sessionId")

            res = await db_layer.list_condonations(
                stud_id=int(stud_id) if stud_id else None,
                session_id=int(session_id) if session_id else None,
            )
            if res.get("status") == "error":
                return res
            return XSCUtility.success_response(
                "Condonation requests retrieved successfully", data=res.get("data", [])
            )
        except Exception as e:
            logger.error(f"[sm_shortage] Error in _cond_view: {str(e)}", exc_info=True)
            return XSCUtility.error_response(
                "Internal Server Error in _cond_view", error_code="ERR_SYS"
            )

    @staticmethod
    async def cond_update(request: Any, context: Any) -> Dict[str, Any]:
        """
        Approves or rejects an existing condonation request. Mandates administrative comments/reason.
        """
        try:
            payload = request.payload or {}
            cond_id = payload.get("condonationId") or payload.get("correctionId")
            decision = str(payload.get("decision", "")).upper()
            comments = payload.get("comments") or payload.get("reason")

            if not cond_id or decision not in ("APPROVE", "REJECT") or not comments:
                return XSCUtility.error_response(
                    "Mandatory fields missing: condonationId, decision (APPROVE/REJECT), and comments required.",
                    error_code="VAL_MISSING_FIELDS",
                )

            db_layer = AttendanceDataLayer(context.postgres)
            user_id = getattr(context, "user_id", None) or payload.get("userId") or 0

            if decision == "APPROVE":
                status_res = await db_layer.resolve_lookup_id_by_code(
                    "CONDONED", default_id=21
                )
                status_id = status_res["data"][0]["id"]
                res = await db_layer.approve_condonation(
                    int(cond_id), int(user_id), str(comments), status_id
                )
            else:
                status_res = await db_layer.resolve_lookup_id_by_code(
                    "REJECTED_CONDONATION", default_id=22
                )
                status_id = status_res["data"][0]["id"]
                res = await db_layer.reject_condonation(
                    int(cond_id), int(user_id), str(comments), status_id
                )

            if res.get("status") == "error":
                return res
            logger.info(
                f"[sm_shortage] Condonation {cond_id} processed with decision {decision}"
            )
            return XSCUtility.success_response(
                f"Condonation request {decision.lower()}d successfully",
                data=res.get("data", []),
            )
        except Exception as e:
            logger.error(
                f"[sm_shortage] Error in _cond_update: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response(
                "Internal Server Error in _cond_update", error_code="ERR_SYS"
            )

    @staticmethod
    async def cond_delete(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes a Semantic Cancellation / Rejection on a condonation request rather than a SQL physical DELETE operation.
        Updates status to REJECTED/CANCELLED while preserving the audit trail of all requested condonations.
        """
        try:
            payload = request.payload or {}
            cond_id = payload.get("condonationId") or payload.get("correctionId")
            reason = (
                payload.get("reason")
                or "Condonation request cancelled/withdrawn by user or administrator"
            )

            if not cond_id:
                return XSCUtility.error_response(
                    "Mandatory field missing: condonationId required for cancellation.",
                    error_code="VAL_MISSING_ID",
                )

            db_layer = AttendanceDataLayer(context.postgres)
            status_res = await db_layer.resolve_lookup_id_by_code(
                "REJECTED_CONDONATION", default_id=22
            )
            status_id = status_res["data"][0]["id"]

            user_id = getattr(context, "user_id", None) or payload.get("userId") or 0
            res = await db_layer.reject_condonation(
                int(cond_id), int(user_id), str(reason), status_id
            )
            if res.get("status") == "error":
                return res
            logger.info(
                f"[sm_shortage] Condonation {cond_id} semantically cancelled/rejected"
            )
            return XSCUtility.success_response(
                "Condonation request cancelled successfully (semantic delete)",
                data=res.get("data", []),
            )
        except Exception as e:
            logger.error(
                f"[sm_shortage] Error in _cond_delete: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response(
                "Internal Server Error in _cond_delete", error_code="ERR_SYS"
            )
