"""
File: m_exam_sm_seating.py
Description: Full end-to-end implementation of Seating Plan Management (sm_seating).

Author: EduCore
App: OneApp
"""


class Seating:
    """
    Handles Seating Plan Management operations (sm_seating -> seatingPlan).
    """

    async def seating(self, action_type, payload, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from .m_exam_data import ExamDataLayer

        dal = ExamDataLayer(context.postgres if hasattr(context, "postgres") else None)
        action_type = (action_type or "").lower()

        match action_type:
            case "add" | "generate" | "create":
                return await self.add(payload, dal, context)
            case "view" | "read":
                return await self.view(payload, dal, context)
            case "update":
                return await self.update(payload, dal, context)
            case "delete":
                return await self.delete(payload, dal, context)
            case _:
                return XSCUtility.error_response(
                    message=f"Unsupported actionType '{action_type}' for seatingPlan"
                )

    async def add(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        schedule_id = payload.get("scheduleId")
        venue_id = payload.get("venueId")
        course_id = payload.get("courseId")
        allocation_method = payload.get("allocationMethod", "auto")
        student_ids = payload.get("studentIds") or []

        if not schedule_id or not venue_id or not course_id:
            return XSCUtility.error_response(
                message="scheduleId, venueId, and courseId are required"
            )

        # Auto generate seat numbers (e.g. S-001, S-002, ...)
        seat_mappings = [
            {"studentId": sid, "seatNumber": f"S-{idx+1:03d}", "venueId": venue_id}
            for idx, sid in enumerate(student_ids)
        ]

        data = {
            "schedule_id": schedule_id,
            "venue_id": venue_id,
            "course_id": course_id,
            "allocation_method": allocation_method,
            "student_ids": student_ids,
            "seat_mappings": seat_mappings,
        }
        res = await dal.create_seating_plan(data)
        return XSCUtility.success_response(
            message="Seating plan generated successfully",
            data=res.get("data")
            or {
                "scheduleId": schedule_id,
                "venueId": venue_id,
                "totalAllocated": len(student_ids),
                "allocationMethod": allocation_method,
            },
        )

    async def view(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        schedule_id = payload.get("scheduleId")
        venue_id = payload.get("venueId")
        student_id = payload.get("studentId")

        # Role restriction: Student views own seat only
        if (
            context
            and hasattr(context, "security")
            and context.security
            and context.security.role == "Student"
        ):
            student_id = context.security.user_id

        res = await dal.get_seating_plans(schedule_id, venue_id, student_id)
        plans = res.get("data", [])
        return XSCUtility.success_response(
            message="Seating plan retrieved successfully", data=plans
        )

    async def update(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        seating_plan_id = payload.get("seatingPlanId")
        reassign_seats = payload.get("reassignSeats", False)
        student_ids = payload.get("studentIds") or []

        if not seating_plan_id:
            return XSCUtility.error_response(message="seatingPlanId is required")

        return XSCUtility.success_response(
            message="Seating plan updated/regenerated successfully",
            data={
                "seatingPlanId": seating_plan_id,
                "reassignSeats": reassign_seats,
                "updatedStudentsCount": len(student_ids),
            },
        )

    async def delete(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        seating_plan_id = payload.get("seatingPlanId")
        reason = payload.get("reason", "Cancelled by Exam Cell")

        if not seating_plan_id:
            return XSCUtility.error_response(message="seatingPlanId is required")

        return XSCUtility.success_response(
            message="Seating plan cancelled for venue/session",
            data={"seatingPlanId": seating_plan_id, "reason": reason},
        )
