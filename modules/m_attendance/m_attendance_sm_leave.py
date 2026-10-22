"""
File: m_attendance_sm_leave.py
Description: Submodule business logic handler for student leave applications.
Author: EduCore
App: OneApp
"""

import logging
from typing import Dict, Any
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from .m_attendance_data import AttendanceDataLayer

logger = logging.getLogger(__name__)


class sm_leave:
    """
    Submodule handler for student leave applications.
    Handles add, view, update, delete actions for student leaves.
    """

    @staticmethod
    async def studentLeave(request: Any, context: Any) -> Dict[str, Any]:
        action_type = (request.actionType or "").lower()
        match action_type:
            case "add":
                return await sm_leave.leave_add(request, context)
            case "view":
                return await sm_leave.leave_view(request, context)
            case "update":
                return await sm_leave.leave_update(request, context)
            case "delete":
                return await sm_leave.leave_delete(request, context)
            case _:
                logger.warning(
                    f"[sm_leave] Invalid actionType received for studentLeave: {action_type}"
                )
                return XSCUtility.error_response(
                    "Invalid actionType for studentLeave",
                    error_code="INVALID_ACTION_TYPE",
                )

    @staticmethod
    async def leave_add(request: Any, context: Any) -> Dict[str, Any]:
        payload = request.payload or {}
        stud_id = payload.get("studentId")
        leave_type_id = payload.get("leaveTypeId")
        from_date = payload.get("fromDate")
        to_date = payload.get("toDate")
        reason = payload.get("reason")
        medical_doc_id = payload.get("medicalDocId")

        if (
            not stud_id
            or not leave_type_id
            or not from_date
            or not to_date
            or not reason
        ):
            return XSCUtility.error_response(
                "studentId, leaveTypeId, fromDate, toDate, and reason are required",
                error_code="VAL_MISSING_DATA",
            )

        actor_id = (
            context.security.user_id
            if context and hasattr(context, "security") and context.security
            else 1
        )
        db_layer = AttendanceDataLayer(context.postgres)

        data = {
            "stud_id": stud_id,
            "leave_type_id": leave_type_id,
            "from_date": from_date,
            "to_date": to_date,
            "reason": reason,
            "medical_doc_id": medical_doc_id,
            "actor_id": actor_id,
        }

        res = await db_layer.create_leave(data)
        if res.get("status") == "success":
            return XSCUtility.success_response(
                "Leave application submitted successfully", data=res.get("data", [])
            )
        return res

    @staticmethod
    async def leave_view(request: Any, context: Any) -> Dict[str, Any]:
        payload = request.payload or {}
        stud_id = payload.get("studentId")
        leave_id = payload.get("leaveId")

        db_layer = AttendanceDataLayer(context.postgres)
        res = await db_layer.get_leaves(stud_id=stud_id, leave_id=leave_id)

        if res.get("status") == "success":
            return XSCUtility.success_response(
                "Leave applications retrieved successfully", data=res.get("data", [])
            )
        return res

    @staticmethod
    async def leave_update(request: Any, context: Any) -> Dict[str, Any]:
        payload = request.payload or {}
        leave_id = payload.get("leaveId")

        if not leave_id:
            return XSCUtility.error_response(
                "leaveId is required for update", error_code="VAL_MISSING_ID"
            )

        actor_id = (
            context.security.user_id
            if context and hasattr(context, "security") and context.security
            else 1
        )
        db_layer = AttendanceDataLayer(context.postgres)

        data = {
            "leave_id": leave_id,
            "leave_type_id": payload.get("leaveTypeId"),
            "from_date": payload.get("fromDate"),
            "to_date": payload.get("toDate"),
            "reason": payload.get("reason"),
            "medical_doc_id": payload.get("medicalDocId"),
            "actor_id": actor_id,
        }

        res = await db_layer.update_leave(data)
        if res.get("status") == "success":
            return XSCUtility.success_response(
                "Leave application updated successfully", data=res.get("data", [])
            )
        return res

    @staticmethod
    async def leave_delete(request: Any, context: Any) -> Dict[str, Any]:
        payload = request.payload or {}
        leave_id = payload.get("leaveId")

        if not leave_id:
            return XSCUtility.error_response(
                "leaveId is required for delete", error_code="VAL_MISSING_ID"
            )

        db_layer = AttendanceDataLayer(context.postgres)
        res = await db_layer.delete_leave(leave_id)

        if res.get("status") == "success":
            return XSCUtility.success_response(
                "Leave application deleted successfully", data=res.get("data", [])
            )
        return res
