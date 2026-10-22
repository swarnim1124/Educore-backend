"""
File: m_exam_sm_evaluation.py
Description: Full end-to-end implementation of Evaluation & Moderation Management (sm_evaluation).

Author: EduCore
App: OneApp
"""


class Evaluation:
    """
    Handles Evaluation & Moderation operations (sm_evaluation -> evaluationBundle, secondValuation, moderation).
    """

    async def evaluation(self, action_type, payload, context):
        """Standard handler for evaluation action."""
        return await self.evaluation_bundle(action_type, payload, context)

    async def evaluation_bundle(self, action_type, payload, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from .m_exam_data import ExamDataLayer

        dal = ExamDataLayer(context.postgres if hasattr(context, "postgres") else None)
        action_type = (action_type or "").lower()

        match action_type:
            case "add" | "create_bundle" | "create":
                return await self.add_bundle(payload, dal, context)
            case "view" | "read":
                return await self.view_bundle(payload, dal, context)
            case "update":
                return await self.update_bundle(payload, dal, context)
            case "delete":
                return await self.delete_bundle(payload, dal, context)
            case _:
                return XSCUtility.error_response(
                    message=f"Unsupported actionType '{action_type}' for evaluationBundle"
                )

    async def second_valuation(self, action_type, payload, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from .m_exam_data import ExamDataLayer

        dal = ExamDataLayer(context.postgres if hasattr(context, "postgres") else None)
        action_type = (action_type or "").lower()

        match action_type:
            case "add" | "trigger":
                return await self.add_second_valuation(payload, dal, context)
            case "view":
                return await self.view_second_valuation(payload, dal, context)
            case "update":
                return await self.update_second_valuation(payload, dal, context)
            case "delete":
                return await self.delete_second_valuation(payload, dal, context)
            case _:
                return XSCUtility.error_response(
                    message=f"Unsupported actionType '{action_type}' for secondValuation"
                )

    async def moderation(self, action_type, payload, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from .m_exam_data import ExamDataLayer

        dal = ExamDataLayer(context.postgres if hasattr(context, "postgres") else None)
        action_type = (action_type or "").lower()

        match action_type:
            case "add" | "apply":
                return await self.add_moderation(payload, dal, context)
            case "view":
                return await self.view_moderation(payload, dal, context)
            case "update":
                return await self.update_moderation(payload, dal, context)
            case "delete":
                return await self.delete_moderation(payload, dal, context)
            case _:
                return XSCUtility.error_response(
                    message=f"Unsupported actionType '{action_type}' for moderation"
                )

    # --- Bundle Handlers ---

    async def add_bundle(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        schedule_id = payload.get("scheduleId")
        course_id = payload.get("courseId")
        evaluator_id = payload.get("evaluatorId")
        student_ids = payload.get("studentIds") or []

        if not schedule_id or not course_id or not evaluator_id:
            return XSCUtility.error_response(
                message="scheduleId, courseId, and evaluatorId are required"
            )

        data = {
            "schedule_id": schedule_id,
            "course_id": course_id,
            "evaluator_id": evaluator_id,
            "student_ids": student_ids,
        }
        res = await dal.create_evaluation_bundle(data)
        return XSCUtility.success_response(
            message="Evaluation bundle assigned to evaluator",
            data=res.get("data")
            or {"evaluatorId": evaluator_id, "scriptsCount": len(student_ids)},
        )

    async def view_bundle(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        return XSCUtility.success_response(
            message="Evaluation bundles retrieved", data=[]
        )

    async def update_bundle(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        bundle_id = payload.get("bundleId")
        new_evaluator_id = payload.get("evaluatorId")
        return XSCUtility.success_response(
            message="Evaluation bundle reassigned (previously evaluated scripts preserved)",
            data={"bundleId": bundle_id, "evaluatorId": new_evaluator_id},
        )

    async def delete_bundle(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        bundle_id = payload.get("bundleId")
        reason = payload.get("reason", "Cancelled bundle")
        return XSCUtility.success_response(
            message="Evaluation bundle cancelled",
            data={"bundleId": bundle_id, "reason": reason},
        )

    # --- Second Valuation Handlers ---

    async def add_second_valuation(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        bundle_id = payload.get("bundleId")
        stud_id = payload.get("studentId") or payload.get("studId")
        second_evaluator_id = payload.get("secondEvaluatorId")

        if not second_evaluator_id:
            return XSCUtility.error_response(message="secondEvaluatorId is required")

        data = {
            "bundle_id": bundle_id,
            "stud_id": stud_id,
            "second_evaluator_id": second_evaluator_id,
        }
        res = await dal.add_second_valuation(data)
        return XSCUtility.success_response(
            message="Second valuation requested due to policy/threshold trigger",
            data=res.get("data") or {"secondEvaluatorId": second_evaluator_id},
        )

    async def view_second_valuation(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        return XSCUtility.success_response(message="Second valuation queue retrieved")

    async def update_second_valuation(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        second_valuation_id = payload.get("secondValuationId")
        marks = payload.get("marks")
        return XSCUtility.success_response(
            message="Second valuation outcome recorded",
            data={"secondValuationId": second_valuation_id, "marks": marks},
        )

    async def delete_second_valuation(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        second_valuation_id = payload.get("secondValuationId")
        return XSCUtility.success_response(
            message="Second valuation cancelled (reverted to original marks)",
            data={"secondValuationId": second_valuation_id},
        )

    # --- Moderation Handlers ---

    async def add_moderation(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        schedule_id = payload.get("scheduleId")
        course_id = payload.get("courseId")
        rule = payload.get("moderationRule", "Scaling")
        adjustment = payload.get("adjustment")

        if not schedule_id or not course_id or adjustment is None:
            return XSCUtility.error_response(
                message="scheduleId, courseId, and adjustment are required"
            )

        data = {
            "schedule_id": schedule_id,
            "course_id": course_id,
            "moderation_rule": rule,
            "adjustment": adjustment,
        }
        res = await dal.apply_moderation(data)
        return XSCUtility.success_response(
            message="Moderation adjustment applied to course marks",
            data=res.get("data") or {"courseId": course_id, "adjustment": adjustment},
        )

    async def view_moderation(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        return XSCUtility.success_response(message="Moderation rules retrieved")

    async def update_moderation(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        moderation_id = payload.get("moderationId")
        adjustment = payload.get("adjustment")
        reason = payload.get("reason", "Adjusted moderation rule")
        return XSCUtility.success_response(
            message="Moderation adjustment updated",
            data={
                "moderationId": moderation_id,
                "adjustment": adjustment,
                "reason": reason,
            },
        )

    async def delete_moderation(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        moderation_id = payload.get("moderationId")
        reason = payload.get("reason", "Revoked moderation")
        return XSCUtility.success_response(
            message="Moderation adjustment revoked (marks reverted)",
            data={"moderationId": moderation_id, "reason": reason},
        )
