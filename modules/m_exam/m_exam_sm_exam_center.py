"""
File: m_exam_sm_exam_center.py
Description: Full end-to-end implementation of Exam Centre Management (sm_examCenter).

Author: EduCore
App: OneApp
"""


class ExamCenter:
    """
    Handles Exam Centre Management operations (sm_examCenter -> examCentre).
    """

    async def exam_center(self, action_type, payload, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from .m_exam_data import ExamDataLayer

        dal = ExamDataLayer(context.postgres if hasattr(context, "postgres") else None)
        action_type = (action_type or "").lower()

        match action_type:
            case "add" | "create":
                return await self.add(payload, dal, context)
            case "view" | "read":
                return await self.view(payload, dal, context)
            case "update":
                return await self.update(payload, dal, context)
            case "delete":
                return await self.delete(payload, dal, context)
            case _:
                return XSCUtility.error_response(
                    message=f"Unsupported actionType '{action_type}' for examCentre"
                )

    async def add(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        centre_name = XSCUtility.trim(payload.get("centreName") or "")
        capacity = payload.get("capacity")
        inst_id = (
            payload.get("inst_id")
            or payload.get("instId")
            or (
                context.security.institution_id
                if context and hasattr(context, "security") and context.security
                else 1
            )
        )
        address = payload.get("address", "")
        courses = payload.get("courses") or []

        if not centre_name:
            return XSCUtility.error_response(message="centreName is required")
        if capacity is None or not isinstance(capacity, int) or capacity <= 0:
            return XSCUtility.error_response(
                message="capacity must be a positive integer"
            )

        data = {
            "inst_id": inst_id,
            "centre_name": centre_name,
            "address": address,
            "capacity": capacity,
            "courses": courses,
        }
        res = await dal.create_centre(data)
        if res.get("status") == "error":
            return XSCUtility.error_response(
                message=res.get("message", "Failed to create exam centre")
            )

        return XSCUtility.success_response(
            message="Exam centre registered successfully",
            data=res.get("data")
            or {
                "centreName": centre_name,
                "capacity": capacity,
                "courses": courses,
                "status": "active",
            },
        )

    async def view(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = (
            payload.get("inst_id")
            or payload.get("instId")
            or (
                context.security.institution_id
                if context and hasattr(context, "security") and context.security
                else 1
            )
        )
        centre_id = payload.get("centreId")

        res = await dal.get_centres(inst_id, centre_id)
        centres = res.get("data", [])
        return XSCUtility.success_response(
            message="Exam centres retrieved successfully", data=centres
        )

    async def update(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        centre_id = payload.get("centreId")
        capacity = payload.get("capacity")
        courses = payload.get("courses")
        address = payload.get("address")

        if not centre_id:
            return XSCUtility.error_response(message="centreId is required for update")
        if capacity is not None and (not isinstance(capacity, int) or capacity <= 0):
            return XSCUtility.error_response(
                message="capacity must be a positive integer"
            )

        data = {
            "centre_id": centre_id,
            "capacity": capacity,
            "courses": courses,
            "address": address,
        }
        res = await dal.update_centre(data)
        return XSCUtility.success_response(
            message="Exam centre updated successfully",
            data=res.get("data") or {"centreId": centre_id},
        )

    async def delete(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        centre_id = payload.get("centreId")
        reason = payload.get("reason", "Deactivated by Exam Cell")

        if not centre_id:
            return XSCUtility.error_response(message="centreId is required for delete")

        await dal.deactivate_centre(centre_id, reason)
        return XSCUtility.success_response(
            message="Exam centre deactivated successfully (historical records preserved)",
            data={"centreId": centre_id, "reason": reason},
        )
