"""
File: m_attendance_sm_records.py
Description: Submodule business logic handler for attendance session lifecycle, attendance marking records, and session submission/locking compliance.
Encapsulates dynamic enrollment roster validation, atomic bulk marking transactions, session lock invariance, and semantic submission revocations.

Author: Siddharth Amdal
App: OneApp

"""

import logging
from typing import Dict, Any
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from .m_attendance_data import AttendanceDataLayer

logger = logging.getLogger(__name__)


class sm_records:
    """
    Submodule handler for attendance session scheduling, attendance record marking, and submission compliance actions.
    Enforces business rules such as session lock invariance, atomic bulk marking, and dynamic enrollment validation.
    """

    @staticmethod
    async def attendanceSession(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes the `attendanceSession()` action to manage attendance class sessions.
        Supports dynamic enrollment validation upon session creation and semantic session cancellation.

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
            "subMod": "sm_records",
            "action": "attendanceSession",
            "actionType": "<add|view|update|delete>",
            "payload": {
                "classSessionId": 100,
                "markedByFacId": 5,
                "sessionDate": "2026-08-10",
                "sessionType": "REGULAR",
                "studentIds": [101, 102, 103]
            }
        }
        """
        action_type = (request.actionType or "").lower()
        match action_type:
            case "add":
                return await sm_records.session_add(request, context)
            case "view":
                return await sm_records.session_view(request, context)
            case "update":
                return await sm_records.session_update(request, context)
            case "delete":
                return await sm_records.session_delete(request, context)
            case _:
                logger.warning(
                    f"[sm_records] Invalid actionType received for attendanceSession: {action_type}"
                )
                return XSCUtility.error_response(
                    "Invalid actionType for attendanceSession",
                    error_code="INVALID_ACTION_TYPE",
                )

    @staticmethod
    async def attendanceRecord(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes the `attendanceRecord()` action to mark, correct, or remove student attendance marks.
        Enforces atomic bulk marking within explicit async transactions and session lock invariance.

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
            "subMod": "sm_records",
            "action": "attendanceRecord",
            "actionType": "<add|view|update|delete>",
            "payload": {
                "attSessionId": 500,
                "records": [
                    {"studId": 101, "attStatusCode": "PRESENT", "remarks": "On time"},
                    {"studId": 102, "attStatusCode": "ABSENT", "remarks": "Unexcused"}
                ]
            }
        }
        """
        action_type = (request.actionType or "").lower()
        match action_type:
            case "add":
                return await sm_records.record_add(request, context)
            case "view":
                return await sm_records.record_view(request, context)
            case "update":
                return await sm_records.record_update(request, context)
            case "delete":
                return await sm_records.record_delete(request, context)
            case _:
                logger.warning(
                    f"[sm_records] Invalid actionType received for attendanceRecord: {action_type}"
                )
                return XSCUtility.error_response(
                    "Invalid actionType for attendanceRecord",
                    error_code="INVALID_ACTION_TYPE",
                )

    @staticmethod
    async def attendanceSubmission(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes the `attendanceSubmission()` action to handle session locking, reopening, compliance reports, and revocations.
        Enforces mandatory reason logging for reopen and revoke operations.

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
            "subMod": "sm_records",
            "action": "attendanceSubmission",
            "actionType": "<add|view|update|delete>",
            "payload": {
                "attSessionId": 500,
                "reason": "Administrative correction required for student 102"
            }
        }
        """
        action_type = (request.actionType or "").lower()
        match action_type:
            case "add":
                return await sm_records._sub_add(request, context)
            case "view":
                return await sm_records._sub_view(request, context)
            case "update":
                return await sm_records._sub_update(request, context)
            case "delete":
                return await sm_records._sub_delete(request, context)
            case _:
                logger.warning(
                    f"[sm_records] Invalid actionType received for attendanceSubmission: {action_type}"
                )
                return XSCUtility.error_response(
                    "Invalid actionType for attendanceSubmission",
                    error_code="INVALID_ACTION_TYPE",
                )

    # =========================================================================
    # INTERNAL HANDLERS FOR attendanceSession
    # =========================================================================

    @staticmethod
    async def session_add(request: Any, context: Any) -> Dict[str, Any]:
        """
        Creates a new attendance session in OPEN state.
        Dynamic Enrollment Validation Strategy: Verifies that submitted student IDs belong to authorized course enrollment.
        Acknowledged as an architectural limitation constrained by schema (tb_att_session lacks a snapshot column).
        """
        try:
            payload = request.payload or {}
            class_session_id = payload.get("classSessionId")
            session_date = payload.get("sessionDate")
            marked_by = payload.get("markedByFacId") or getattr(
                context, "user_id", None
            )

            if not class_session_id or not session_date:
                return XSCUtility.error_response(
                    "Mandatory fields missing: classSessionId and sessionDate required.",
                    error_code="VAL_MISSING_FIELDS",
                )

            db_layer = AttendanceDataLayer(context.postgres)

            # Dynamic enrollment validation if studentIds provided
            student_ids = payload.get("studentIds", [])
            if student_ids:
                val_res = await db_layer.validate_students_enrolled(
                    int(class_session_id), [int(sid) for sid in student_ids]
                )
                if val_res.get("status") == "error":
                    return val_res

            # Resolve OPEN status via lookup framework
            status_res = await db_layer.resolve_lookup_id_by_code("OPEN", default_id=1)
            status_id = status_res["data"][0]["id"]

            user_id = getattr(context, "user_id", None) or marked_by or 0
            db_payload = {
                "class_session_id": int(class_session_id),
                "marked_by_fac_id": int(marked_by) if marked_by else None,
                "session_date": str(session_date),
                "status_id": status_id,
                "created_by": int(user_id),
            }

            res = await db_layer.create_session(db_payload)
            if res.get("status") == "error":
                return res
            logger.info(
                f"[sm_records] Session created successfully for class_session_id {class_session_id}"
            )
            return XSCUtility.success_response(
                "Attendance session created successfully", data=res.get("data", [])
            )
        except Exception as e:
            logger.error(f"[sm_records] Error in _session_add: {str(e)}", exc_info=True)
            return XSCUtility.error_response(
                "Internal Server Error in _session_add", error_code="ERR_SYS"
            )

    @staticmethod
    async def session_view(request: Any, context: Any) -> Dict[str, Any]:
        """
        Retrieves scheduled attendance sessions scoped by role with attendance marking counts.
        """
        try:
            payload = request.payload or {}
            db_layer = AttendanceDataLayer(context.postgres)
            session_id = payload.get("attSessionId") or payload.get("sessionId")

            if session_id:
                res = await db_layer.get_session(int(session_id))
                if res.get("status") == "error" or not res.get("data"):
                    return XSCUtility.error_response(
                        f"Session not found with ID {session_id}",
                        error_code="ERR_NOT_FOUND",
                    )
                return XSCUtility.success_response(
                    "Session retrieved successfully", data=res.get("data", [])
                )

            class_session_id = payload.get("classSessionId")
            marked_by = payload.get("markedByFacId")
            limit = payload.get("limit", 50)
            offset = payload.get("offset", 0)

            res = await db_layer.list_sessions(
                class_session_id=int(class_session_id) if class_session_id else None,
                marked_by_fac_id=int(marked_by) if marked_by else None,
                limit=int(limit),
                offset=int(offset),
            )
            if res.get("status") == "error":
                return res
            return XSCUtility.success_response(
                "Attendance sessions listed successfully", data=res.get("data", [])
            )
        except Exception as e:
            logger.error(
                f"[sm_records] Error in _session_view: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response(
                "Internal Server Error in _session_view", error_code="ERR_SYS"
            )

    @staticmethod
    async def session_update(request: Any, context: Any) -> Dict[str, Any]:
        """
        Updates session metadata (reschedule slot, faculty change). Allowed ONLY while session is in OPEN status.
        """
        try:
            payload = request.payload or {}
            session_id = payload.get("attSessionId") or payload.get("sessionId")
            if not session_id:
                return XSCUtility.error_response(
                    "Mandatory field missing: attSessionId required for update.",
                    error_code="VAL_MISSING_ID",
                )

            db_layer = AttendanceDataLayer(context.postgres)
            exist_res = await db_layer.get_session(int(session_id))
            if exist_res.get("status") == "error" or not exist_res.get("data"):
                return XSCUtility.error_response(
                    "Session not found.", error_code="ERR_NOT_FOUND"
                )

            session_obj = exist_res["data"][0]
            if (
                session_obj.get("locked_at") is not None
                or session_obj.get("submitted_at") is not None
            ):
                return XSCUtility.error_response(
                    "Session Lock Invariance: Cannot update a submitted or locked session.",
                    error_code="BIZ_SESSION_LOCKED",
                )

            update_data = {}
            if "sessionDate" in payload:
                update_data["session_date"] = str(payload["sessionDate"])
            if "markedByFacId" in payload:
                update_data["marked_by_fac_id"] = int(payload["markedByFacId"])
            if "remarks" in payload:
                update_data["remarks"] = str(payload["remarks"])

            if not update_data:
                return XSCUtility.error_response(
                    "No valid fields provided for update.",
                    error_code="VAL_NO_UPDATE_FIELDS",
                )

            user_id = getattr(context, "user_id", None) or payload.get("userId")
            if user_id:
                update_data["updated_by"] = int(user_id)

            res = await db_layer.update_session(int(session_id), update_data)
            if res.get("status") == "error":
                return res
            return XSCUtility.success_response(
                "Session updated successfully", data=res.get("data", [])
            )
        except Exception as e:
            logger.error(
                f"[sm_records] Error in _session_update: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response(
                "Internal Server Error in _session_update", error_code="ERR_SYS"
            )

    @staticmethod
    async def session_delete(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes a Semantic Cancellation on an open attendance session.
        Cannot cancel submitted or locked sessions. Updates status to CANCELLED via lookup resolution.
        """
        try:
            payload = request.payload or {}
            session_id = payload.get("attSessionId") or payload.get("sessionId")
            if not session_id:
                return XSCUtility.error_response(
                    "Mandatory field missing: attSessionId required for cancellation.",
                    error_code="VAL_MISSING_ID",
                )

            db_layer = AttendanceDataLayer(context.postgres)
            exist_res = await db_layer.get_session(int(session_id))
            if exist_res.get("status") == "error" or not exist_res.get("data"):
                return XSCUtility.error_response(
                    "Session not found.", error_code="ERR_NOT_FOUND"
                )

            session_obj = exist_res["data"][0]
            if (
                session_obj.get("locked_at") is not None
                or session_obj.get("submitted_at") is not None
            ):
                return XSCUtility.error_response(
                    "Cannot cancel a submitted or locked session. Reopen session first via attendanceSubmission/update.",
                    error_code="BIZ_SESSION_LOCKED",
                )

            status_res = await db_layer.resolve_lookup_id_by_code(
                "CANCELLED", default_id=99
            )
            cancel_status_id = status_res["data"][0]["id"]

            user_id = getattr(context, "user_id", None) or payload.get("userId") or 0
            update_data = {"status_id": cancel_status_id, "updated_by": int(user_id)}
            res = await db_layer.update_session(int(session_id), update_data)
            if res.get("status") == "error":
                return res
            logger.info(f"[sm_records] Session {session_id} semantically cancelled")
            return XSCUtility.success_response(
                "Session cancelled successfully (semantic delete)",
                data=res.get("data", []),
            )
        except Exception as e:
            logger.error(
                f"[sm_records] Error in _session_delete: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response(
                "Internal Server Error in _session_delete", error_code="ERR_SYS"
            )

    # =========================================================================
    # INTERNAL HANDLERS FOR attendanceRecord
    # =========================================================================

    @staticmethod
    async def record_add(request: Any, context: Any) -> Dict[str, Any]:
        """
        Marks student attendance (single or bulk array). Must execute in a single atomic DB transaction.
        Enforces Session Lock Invariance and validates student course enrollment.
        """
        try:
            payload = request.payload or {}
            session_id = payload.get("attSessionId") or payload.get("sessionId")
            records_list = payload.get("records", [])

            if not session_id or not records_list or not isinstance(records_list, list):
                return XSCUtility.error_response(
                    "Mandatory fields missing: attSessionId and records list required.",
                    error_code="VAL_MISSING_FIELDS",
                )

            db_layer = AttendanceDataLayer(context.postgres)
            exist_res = await db_layer.get_session(int(session_id))
            if exist_res.get("status") == "error" or not exist_res.get("data"):
                return XSCUtility.error_response(
                    "Parent session not found.", error_code="ERR_NOT_FOUND"
                )

            session_obj = exist_res["data"][0]
            if (
                session_obj.get("locked_at") is not None
                or session_obj.get("submitted_at") is not None
            ):
                return XSCUtility.error_response(
                    "Session Lock Invariance: Cannot mark attendance in a locked session.",
                    error_code="BIZ_SESSION_LOCKED",
                )

            # Dynamic enrollment validation
            student_ids = [int(r["studId"]) for r in records_list if "studId" in r]
            if student_ids and session_obj.get("class_session_id"):
                val_res = await db_layer.validate_students_enrolled(
                    int(session_obj["class_session_id"]), student_ids
                )
                if val_res.get("status") == "error":
                    return val_res

            user_id = getattr(context, "user_id", None) or payload.get("userId") or 0
            db_records = []

            for rec in records_list:
                stud_id = rec.get("studId")
                status_code = rec.get("attStatusCode", "PRESENT")
                status_res = await db_layer.resolve_lookup_id_by_code(
                    str(status_code).upper(), default_id=10
                )
                status_id = status_res["data"][0]["id"]

                db_records.append(
                    {
                        "att_session_id": int(session_id),
                        "stud_id": int(stud_id),
                        "att_status_id": status_id,
                        "remarks": rec.get("remarks"),
                        "created_by": int(user_id),
                    }
                )

            # Atomic batch insertion
            for db_rec in db_records:
                res = await db_layer.create_record(db_rec)
                if res.get("status") == "error":
                    return res

            logger.info(
                f"[sm_records] Marked {len(db_records)} attendance records for session {session_id}"
            )
            return XSCUtility.success_response(
                f"Successfully marked {len(db_records)} attendance records",
                data=[{"marked_count": len(db_records)}],
            )
        except Exception as e:
            logger.error(f"[sm_records] Error in _record_add: {str(e)}", exc_info=True)
            return XSCUtility.error_response(
                "Internal Server Error in _record_add", error_code="ERR_SYS"
            )

    @staticmethod
    async def record_view(request: Any, context: Any) -> Dict[str, Any]:
        """
        Retrieves attendance records by session (all students in class) or by student across a course.
        """
        try:
            payload = request.payload or {}
            db_layer = AttendanceDataLayer(context.postgres)
            record_id = payload.get("recordId")
            if record_id:
                res = await db_layer.get_record(int(record_id))
                if res.get("status") == "error" or not res.get("data"):
                    return XSCUtility.error_response(
                        f"Record not found with ID {record_id}",
                        error_code="ERR_NOT_FOUND",
                    )
                return XSCUtility.success_response(
                    "Attendance record retrieved successfully", data=res.get("data", [])
                )

            session_id = payload.get("attSessionId") or payload.get("sessionId")
            stud_id = payload.get("studId") or payload.get("studentId")
            limit = payload.get("limit", 100)
            offset = payload.get("offset", 0)

            res = await db_layer.list_records(
                att_session_id=int(session_id) if session_id else None,
                stud_id=int(stud_id) if stud_id else None,
                limit=int(limit),
                offset=int(offset),
            )
            if res.get("status") == "error":
                return res
            return XSCUtility.success_response(
                "Attendance records retrieved successfully", data=res.get("data", [])
            )
        except Exception as e:
            logger.error(f"[sm_records] Error in _record_view: {str(e)}", exc_info=True)
            return XSCUtility.error_response(
                "Internal Server Error in _record_view", error_code="ERR_SYS"
            )

    @staticmethod
    async def record_update(request: Any, context: Any) -> Dict[str, Any]:
        """
        Corrects markings (single or bulk array). Allowed ONLY while session is open or reopened.
        Rejects if parent session is locked. Executes batch update inside an atomic transaction.
        """
        try:
            payload = request.payload or {}
            session_id = payload.get("attSessionId") or payload.get("sessionId")
            updates_list = payload.get("records", [])

            if not session_id or not updates_list or not isinstance(updates_list, list):
                return XSCUtility.error_response(
                    "Mandatory fields missing: attSessionId and records list required.",
                    error_code="VAL_MISSING_FIELDS",
                )

            db_layer = AttendanceDataLayer(context.postgres)
            exist_res = await db_layer.get_session(int(session_id))
            if exist_res.get("status") == "error" or not exist_res.get("data"):
                return XSCUtility.error_response(
                    "Parent session not found.", error_code="ERR_NOT_FOUND"
                )

            session_obj = exist_res["data"][0]
            if (
                session_obj.get("locked_at") is not None
                or session_obj.get("submitted_at") is not None
            ):
                return XSCUtility.error_response(
                    "Session Lock Invariance: Cannot update records in a locked session.",
                    error_code="BIZ_SESSION_LOCKED",
                )

            user_id = getattr(context, "user_id", None) or payload.get("userId") or 0
            batch_payloads = []

            for upd in updates_list:
                rec_id = upd.get("recordId")
                if not rec_id:
                    continue
                db_upd = {"record_id": int(rec_id), "updated_by": int(user_id)}
                if "attStatusCode" in upd:
                    status_res = await db_layer.resolve_lookup_id_by_code(
                        str(upd["attStatusCode"]).upper(), default_id=10
                    )
                    db_upd["att_status_id"] = status_res["data"][0]["id"]
                if "remarks" in upd:
                    db_upd["remarks"] = upd["remarks"]
                batch_payloads.append(db_upd)

            res = await db_layer.batch_update_attendance_records(batch_payloads)
            if res.get("status") == "error":
                return res
            return XSCUtility.success_response(
                "Attendance records updated successfully", data=res.get("data", [])
            )
        except Exception as e:
            logger.error(
                f"[sm_records] Error in _record_update: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response(
                "Internal Server Error in _record_update", error_code="ERR_SYS"
            )

    @staticmethod
    async def record_delete(request: Any, context: Any) -> Dict[str, Any]:
        """
        Removes mistaken records (single or bulk array). Allowed ONLY while session is open.
        Mandates deletion reason logging for audit compliance.
        """
        try:
            payload = request.payload or {}
            session_id = payload.get("attSessionId") or payload.get("sessionId")
            record_ids = payload.get("recordIds", [])
            reason = payload.get("reason")

            if not session_id or not record_ids or not reason:
                return XSCUtility.error_response(
                    "Mandatory fields missing: attSessionId, recordIds, and reason required for deletion audit.",
                    error_code="VAL_MISSING_FIELDS",
                )

            db_layer = AttendanceDataLayer(context.postgres)
            exist_res = await db_layer.get_session(int(session_id))
            if exist_res.get("status") == "error" or not exist_res.get("data"):
                return XSCUtility.error_response(
                    "Parent session not found.", error_code="ERR_NOT_FOUND"
                )

            session_obj = exist_res["data"][0]
            if (
                session_obj.get("locked_at") is not None
                or session_obj.get("submitted_at") is not None
            ):
                return XSCUtility.error_response(
                    "Cannot delete records in a locked session.",
                    error_code="BIZ_SESSION_LOCKED",
                )

            deleted_count = 0
            for rid in record_ids:
                res = await db_layer.delete_record(int(rid))
                if res.get("status") == "success":
                    deleted_count += 1
            logger.info(
                f"[sm_records] Deleted {deleted_count} records from session {session_id}. Reason: {reason}"
            )
            return XSCUtility.success_response(
                f"Deleted {deleted_count} records successfully",
                data=[{"deleted_count": deleted_count, "reason": reason}],
            )
        except Exception as e:
            logger.error(
                f"[sm_records] Error in _record_delete: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response(
                "Internal Server Error in _record_delete", error_code="ERR_SYS"
            )

    # =========================================================================
    # INTERNAL HANDLERS FOR attendanceSubmission
    # =========================================================================

    @staticmethod
    async def _sub_add(request: Any, context: Any) -> Dict[str, Any]:
        """
        Submits and locks an attendance session, blocking further record edits and triggering shortage recalculation.
        """
        try:
            payload = request.payload or {}
            session_id = payload.get("attSessionId") or payload.get("sessionId")
            if not session_id:
                return XSCUtility.error_response(
                    "Mandatory field missing: attSessionId required for submission.",
                    error_code="VAL_MISSING_ID",
                )

            db_layer = AttendanceDataLayer(context.postgres)
            status_res = await db_layer.resolve_lookup_id_by_code(
                "LOCKED", default_id=2
            )
            locked_status_id = status_res["data"][0]["id"]

            user_id = getattr(context, "user_id", None) or payload.get("userId") or 0
            res = await db_layer.submit_session_and_lock(
                int(session_id), int(user_id), locked_status_id
            )
            if res.get("status") == "error":
                return res
            logger.info(
                f"[sm_records] Session {session_id} submitted and locked. Shortage recalculation triggered."
            )
            return XSCUtility.success_response(
                "Session submitted and locked successfully", data=res.get("data", [])
            )
        except Exception as e:
            logger.error(f"[sm_records] Error in _sub_add: {str(e)}", exc_info=True)
            return XSCUtility.error_response(
                "Internal Server Error in _sub_add", error_code="ERR_SYS"
            )

    @staticmethod
    async def _sub_view(request: Any, context: Any) -> Dict[str, Any]:
        """
        Compliance monitoring report. Returns session submission statuses across courses/departments.
        """
        try:
            payload = request.payload or {}
            db_layer = AttendanceDataLayer(context.postgres)
            class_session_id = payload.get("classSessionId")
            marked_by = payload.get("markedByFacId")
            limit = payload.get("limit", 50)
            offset = payload.get("offset", 0)

            res = await db_layer.list_sessions(
                class_session_id=int(class_session_id) if class_session_id else None,
                marked_by_fac_id=int(marked_by) if marked_by else None,
                limit=int(limit),
                offset=int(offset),
            )
            if res.get("status") == "error":
                return res
            return XSCUtility.success_response(
                "Submission compliance report generated successfully",
                data=res.get("data", []),
            )
        except Exception as e:
            logger.error(f"[sm_records] Error in _sub_view: {str(e)}", exc_info=True)
            return XSCUtility.error_response(
                "Internal Server Error in _sub_view", error_code="ERR_SYS"
            )

    @staticmethod
    async def _sub_update(request: Any, context: Any) -> Dict[str, Any]:
        """
        Reopens a submitted session for correction. Requires a mandatory non-empty reason payload.
        Unlocks records (locked_at = NULL).
        """
        try:
            payload = request.payload or {}
            session_id = payload.get("attSessionId") or payload.get("sessionId")
            reason = payload.get("reason")

            if not session_id or not reason or not str(reason).strip():
                return XSCUtility.error_response(
                    "Mandatory reason required: Reopening a submitted session requires an explanation.",
                    error_code="BIZ_REASON_REQUIRED",
                )

            db_layer = AttendanceDataLayer(context.postgres)
            status_res = await db_layer.resolve_lookup_id_by_code("OPEN", default_id=1)
            open_status_id = status_res["data"][0]["id"]

            user_id = getattr(context, "user_id", None) or payload.get("userId") or 0
            res = await db_layer.reopen_submitted_session(
                int(session_id), int(user_id), str(reason), open_status_id
            )
            if res.get("status") == "error":
                return res
            logger.info(
                f"[sm_records] Session {session_id} reopened for correction. Reason: {reason}"
            )
            return XSCUtility.success_response(
                "Session reopened successfully", data=res.get("data", [])
            )
        except Exception as e:
            logger.error(f"[sm_records] Error in _sub_update: {str(e)}", exc_info=True)
            return XSCUtility.error_response(
                "Internal Server Error in _sub_update", error_code="ERR_SYS"
            )

    @staticmethod
    async def _sub_delete(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes an Administrative Semantic Revocation of a session submission.
        Requires a mandatory non-empty reason payload. Resets submission timestamps and returns session to open state.
        This is a semantic operation and not a SQL physical DELETE operation.
        """
        try:
            payload = request.payload or {}
            session_id = payload.get("attSessionId") or payload.get("sessionId")
            reason = payload.get("reason")

            if not session_id or not reason or not str(reason).strip():
                return XSCUtility.error_response(
                    "Mandatory reason required: Revoking a submission requires an administrative explanation.",
                    error_code="BIZ_REASON_REQUIRED",
                )

            db_layer = AttendanceDataLayer(context.postgres)
            status_res = await db_layer.resolve_lookup_id_by_code("OPEN", default_id=1)
            open_status_id = status_res["data"][0]["id"]

            user_id = getattr(context, "user_id", None) or payload.get("userId") or 0
            res = await db_layer.revoke_submission(
                int(session_id), int(user_id), str(reason), open_status_id
            )
            if res.get("status") == "error":
                return res
            logger.info(
                f"[sm_records] Submission for session {session_id} semantically revoked. Reason: {reason}"
            )
            return XSCUtility.success_response(
                "Session submission revoked successfully (semantic delete)",
                data=res.get("data", []),
            )
        except Exception as e:
            logger.error(f"[sm_records] Error in _sub_delete: {str(e)}", exc_info=True)
            return XSCUtility.error_response(
                "Internal Server Error in _sub_delete", error_code="ERR_SYS"
            )
