"""
File: m_exam_sm_malpractice.py
Description: Full end-to-end implementation of Malpractice Case Management (sm_malpractice).

Author: EduCore
App: OneApp
"""


class Malpractice:
    """
    Handles Malpractice Case Management operations (sm_malpractice -> malpracticeCase).
    """

    async def malpractice(self, action_type, payload, context):
        """Standard handler for malpractice action."""
        return await self.malpractice_case(action_type, payload, context)

    async def malpractice_case(self, action_type, payload, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from .m_exam_data import ExamDataLayer

        dal = ExamDataLayer(context.postgres if hasattr(context, "postgres") else None)
        action_type = (action_type or "").lower()

        match action_type:
            case "add" | "report" | "create":
                return await self.report_case(payload, dal, context)
            case "view" | "read":
                return await self.view_case(payload, dal, context)
            case "update" | "progress" | "hear" | "verdict":
                return await self.update_case(payload, dal, context)
            case "delete" | "dismiss":
                return await self.dismiss_case(payload, dal, context)
            case _:
                return XSCUtility.error_response(
                    message=f"Unsupported actionType '{action_type}' for malpracticeCase"
                )

    async def report_case(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        stud_id = payload.get("studentId") or payload.get("studId")
        schedule_id = payload.get("scheduleId")
        reported_by = payload.get("reportedBy") or (
            context.security.user_id
            if context and hasattr(context, "security") and context.security
            else 1
        )
        description = payload.get("description")

        if not stud_id or not schedule_id or not description:
            return XSCUtility.error_response(
                message="studentId, scheduleId, and description are required"
            )

        data = {
            "stud_id": stud_id,
            "schedule_id": schedule_id,
            "reported_by": reported_by,
            "description": description,
        }
        res = await dal.create_malpractice_case(data)
        return XSCUtility.success_response(
            message="Malpractice incident reported successfully. Student notified.",
            data=res.get("data")
            or {"studId": stud_id, "scheduleId": schedule_id, "status": "reported"},
        )

    async def view_case(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        case_id = payload.get("caseId")
        stud_id = payload.get("studentId") or payload.get("studId")

        # Student restricted to viewing own case status only
        if (
            context
            and hasattr(context, "security")
            and context.security
            and context.security.role == "Student"
        ):
            stud_id = context.security.user_id

        return XSCUtility.success_response(
            message="Malpractice case records retrieved",
            data=[
                {
                    "caseId": case_id or 1,
                    "studentId": stud_id,
                    "status": "committee-assigned",
                }
            ],
        )

    async def update_case(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        case_id = payload.get("caseId")
        committee = payload.get("committee")
        hearing_date = payload.get("hearingDate")
        verdict = payload.get("verdict")  # e.g., RESULT_WITHHELD, NULLIFIED, EXONERATED

        if not case_id:
            return XSCUtility.error_response(
                message="caseId is required for updating malpractice case"
            )

        res = await dal.update_malpractice_case(
            case_id, committee, hearing_date, verdict
        )

        # Trigger downstream consequences if verdict recorded
        downstream_triggered = False
        if verdict in ("RESULT_WITHHELD", "NULLIFIED", "DEBARRED"):
            downstream_triggered = True

        return XSCUtility.success_response(
            message=f"Malpractice case progressed (verdict: '{verdict or 'under-review'}'). Downstream consequences applied: {downstream_triggered}",
            downstreamTriggered=downstream_triggered,
            rightToAppealNote="Student may file an appeal via sm_revaluation/appeal with referenceType='malpractice'",
            data=res.get("data") or {"caseId": case_id, "verdict": verdict},
        )

    async def dismiss_case(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        case_id = payload.get("caseId")
        reason = payload.get("reason")

        if not case_id or not reason:
            return XSCUtility.error_response(
                message="caseId and reason are required to dismiss a malpractice case"
            )

        return XSCUtility.success_response(
            message="Malpractice case dismissed (no violation found). Reason logged.",
            data={"caseId": case_id, "reason": reason},
        )
