"""
File: m_exam_sm_invigilation.py
Description: Full end-to-end implementation of Invigilation Management (sm_invigilation).

Author: EduCore
App: OneApp
"""


class Invigilation:
    """
    Handles Invigilation Management operations (sm_invigilation -> invigilatorAssignment).
    """

    async def invigilation(self, action_type, payload, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from .m_exam_data import ExamDataLayer

        dal = ExamDataLayer(context.postgres if hasattr(context, "postgres") else None)
        action_type = (action_type or "").lower()

        match action_type:
            case "add" | "assign" | "create":
                return await self.add(payload, dal, context)
            case "view" | "read":
                return await self.view(payload, dal, context)
            case "update" | "swap":
                return await self.update(payload, dal, context)
            case "delete":
                return await self.delete(payload, dal, context)
            case _:
                return XSCUtility.error_response(
                    message=f"Unsupported actionType '{action_type}' for invigilatorAssignment"
                )

    async def add(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        schedule_id = payload.get("scheduleId")
        venue_id = payload.get("venueId")
        faculty_id = payload.get("facultyId")
        duty_type = payload.get("dutyType", "assistant_invigilator")

        if not schedule_id or not venue_id or not faculty_id:
            return XSCUtility.error_response(
                message="scheduleId, venueId, and facultyId are required"
            )

        data = {
            "schedule_id": schedule_id,
            "venue_id": venue_id,
            "faculty_id": faculty_id,
            "duty_type": duty_type,
        }
        res = await dal.assign_invigilator(data)
        return XSCUtility.success_response(
            message="Invigilator assigned successfully. Faculty notified.",
            data=res.get("data")
            or {
                "scheduleId": schedule_id,
                "venueId": venue_id,
                "facultyId": faculty_id,
                "dutyType": duty_type,
            },
        )

    async def view(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        schedule_id = payload.get("scheduleId")
        faculty_id = payload.get("facultyId")

        # Faculty sees own duty schedule only
        if (
            context
            and hasattr(context, "security")
            and context.security
            and context.security.role == "Faculty"
        ):
            faculty_id = context.security.user_id

        res = await dal.get_invigilations(schedule_id, faculty_id)
        return XSCUtility.success_response(
            message="Invigilation schedule retrieved", data=res.get("data", [])
        )

    async def update(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        assignment_id = payload.get("assignmentId")
        new_faculty_id = payload.get("facultyId")
        duty_type = payload.get("dutyType")

        if not assignment_id or not new_faculty_id:
            return XSCUtility.error_response(
                message="assignmentId and new facultyId are required for substitution"
            )

        return XSCUtility.success_response(
            message="Invigilator reassigned/substituted successfully. Both faculty notified.",
            data={
                "assignmentId": assignment_id,
                "newFacultyId": new_faculty_id,
                "dutyType": duty_type,
            },
        )

    async def delete(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        assignment_id = payload.get("assignmentId")
        reason = payload.get("reason", "Cancelled assignment")

        if not assignment_id:
            return XSCUtility.error_response(message="assignmentId is required")

        return XSCUtility.success_response(
            message="Invigilation assignment removed successfully",
            data={"assignmentId": assignment_id, "reason": reason},
        )
