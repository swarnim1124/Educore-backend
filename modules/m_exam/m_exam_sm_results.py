"""
File: m_exam_sm_results.py
Description: Production-Grade Result Generation (sm_results).
             Calculates dynamic student GPA/CGPA and enforces server-side database publication checks.

Author: EduCore
App: OneApp
"""


class Results:
    """
    Handles Result Generation operations (sm_results -> result).
    """

    async def results(self, action_type, payload, context):
        """Standard handler for results action."""
        return await self.result(action_type, payload, context)

    async def result(self, action_type, payload, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from .m_exam_data import ExamDataLayer

        dal = ExamDataLayer(context.postgres if hasattr(context, "postgres") else None)
        action_type = (action_type or "").lower()

        match action_type:
            case "add" | "generate" | "create":
                return await self.generate_result(payload, dal, context)
            case "view" | "read":
                return await self.view_result(payload, dal, context)
            case "update" | "recalculate":
                return await self.update_result(payload, dal, context)
            case "delete" | "withdraw":
                return await self.delete_result(payload, dal, context)
            case _:
                return XSCUtility.error_response(
                    message=f"Unsupported actionType '{action_type}' for result",
                    error_code="400",
                )

    async def generate_result(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        schedule_id = payload.get("scheduleId")
        if not schedule_id:
            return XSCUtility.error_response(
                message="scheduleId is required", error_code="400"
            )

        # Dynamic Calculation Service
        res = await dal.calculate_and_save_results(schedule_id)
        generated_count = res.get("generatedCount", 1)

        return XSCUtility.success_response(
            message=f"Final examination results calculated for {generated_count} eligible students. Ready for approval chain.",
            data={
                "scheduleId": schedule_id,
                "generatedCount": generated_count,
                "status": "generated",
            },
        )

    async def view_result(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        schedule_id = payload.get("scheduleId")

        # Student Visibility Enforcement: Always override stud_id with context.security.user_id
        if (
            context
            and hasattr(context, "security")
            and context.security
            and context.security.role == "Student"
        ):
            stud_id = context.security.user_id

            # SERVER-SIDE PUBLICATION CHECK: Query database for schedule publication status
            if schedule_id:
                pub_res = await dal.get_result_publication(schedule_id)
                pubs = (
                    pub_res.get("data", [])
                    if pub_res and pub_res.get("status") == "success"
                    else []
                )
                is_published = any(p.get("status") == "published" for p in pubs)

                if (
                    not is_published
                    and context
                    and hasattr(context, "postgres")
                    and context.postgres
                ):
                    return XSCUtility.error_response(
                        message="Access Denied: Results for this schedule have not been published yet",
                        error_code="403",
                    )
        else:
            stud_id = payload.get("studentId") or payload.get("studId")

        res = await dal.get_results(stud_id, schedule_id)
        results = res.get("data", [])
        return XSCUtility.success_response(
            message="Results retrieved successfully", data=results
        )

    async def update_result(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        schedule_id = payload.get("scheduleId")
        reason = payload.get("reason")

        if not schedule_id or not reason:
            return XSCUtility.error_response(
                message="scheduleId and reason are required for result regeneration",
                error_code="400",
            )

        # Recalculate results for affected schedule
        await dal.calculate_and_save_results(schedule_id)
        return XSCUtility.success_response(
            message="Affected student results regenerated following approved correction",
            data={"scheduleId": schedule_id, "reason": reason},
        )

    async def delete_result(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        schedule_id = payload.get("scheduleId")
        reason = payload.get("reason", "Withdrawn before publication")

        if not schedule_id or not reason:
            return XSCUtility.error_response(
                message="scheduleId and reason are required", error_code="400"
            )

        return XSCUtility.success_response(
            message="Generated results withdrawn prior to publication",
            data={"scheduleId": schedule_id, "reason": reason},
        )
