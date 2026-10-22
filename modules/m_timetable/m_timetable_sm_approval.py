"""
File: m_timetable_sm_approval.py
Description: Submodule handling Timetable Approval operations for m_timetable.
             Action: timetableApproval (add, view, update, delete).
             Maps to TB_TT.STATUS_ID state transitions per BRS feature specification.

Author: EduCore
App: OneApp
"""


class Approval:
    """
    Submodule handler class for timetable approval workflow.
    Manages the lifecycle of timetable status: DRAFT → PENDING_APPROVAL → PUBLISHED / DRAFT.
    """

    # =========================================================================
    # ACTION: timetableApproval
    # BRS Feature: Timetable Approval Management (Optional)
    # =========================================================================

    async def timetable_approval(self, action_type, payload, context):
        """
        Action method for timetable approval workflow per BRS contract:
        action: timetableApproval
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from .m_timetable_data import TimetableDataLayer

        dal = TimetableDataLayer(
            context.postgres if hasattr(context, "postgres") else None
        )
        action_type = (action_type or "").lower()

        match action_type:
            case "add":
                return await self.approval_submit(payload, dal, context)
            case "view":
                return await self.approval_view(payload, dal, context)
            case "update":
                return await self.approval_action(payload, dal, context)
            case "delete":
                return await self.approval_withdraw(payload, dal, context)
            case _:
                return XSCUtility.error_response(
                    message=f"Unsupported actionType '{action_type}' for timetableApproval",
                    error_code="400",
                )

    async def approval_submit(self, payload, dal, context):
        """
        Submit a timetable for approval per BRS:
        payload: { inst_id, timetableId, remarks }
        Transitions status from DRAFT → PENDING_APPROVAL.
        Validates: only one pending request per timetableId, timetable must be in DRAFT status.
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        tt_id = payload.get("timetableId") or payload.get("ttId")
        remarks = payload.get("remarks")

        if not inst_id or not tt_id:
            return XSCUtility.error_response(
                message="inst_id and timetableId are required per BRS", error_code="400"
            )
        if not remarks or str(remarks).strip() == "":
            return XSCUtility.error_response(
                message="remarks are required for submitting approval per BRS",
                error_code="400",
            )

        # Verify timetable is in DRAFT status
        tt_result = await dal.get_timetables({"tt_id": tt_id})
        tt_data = tt_result.get("data", [])
        if not tt_data or (isinstance(tt_data, list) and len(tt_data) == 0):
            return XSCUtility.error_response(
                message=f"Timetable with id {tt_id} not found", error_code="404"
            )

        current_tt = tt_data[0] if isinstance(tt_data, list) else tt_data
        current_status = current_tt.get("status_id", "")

        if current_status == "PENDING_APPROVAL":
            return XSCUtility.error_response(
                message=f"A timetable approval request is already pending for timetableId {tt_id}.",
                error_code="400",
            )
        if current_status not in ("DRAFT", "REJECTED"):
            return XSCUtility.error_response(
                message=f"Timetable cannot be submitted for approval: current status is '{current_status}', expected 'DRAFT'",
                error_code="400",
            )

        # Validate timetable has at least one entry
        entries_result = await dal.get_tt_entries({"tt_id": tt_id})
        entries_data = entries_result.get("data", [])
        if not entries_data or (
            isinstance(entries_data, list) and len(entries_data) == 0
        ):
            return XSCUtility.error_response(
                message="Timetable cannot be submitted for approval: no entries found in the schedule.",
                error_code="400",
            )

        actor_id = self._get_actor_id(context)
        result = await dal.submit_for_approval(tt_id, remarks, actor_id)

        if result.get("status") == "error":
            return XSCUtility.error_response(
                message=result.get("message", "Failed to submit for approval"),
                error_code="500",
            )

        return XSCUtility.success_response(
            message="Timetable submitted for approval successfully. Status moved to PENDING_APPROVAL.",
            data=result.get("data"),
        )

    async def approval_view(self, payload, dal, context):
        """
        List approval requests per BRS:
        payload: { inst_id, statusFilter, approverId, page, limit }
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        if not inst_id:
            return XSCUtility.error_response(
                message="inst_id is required", error_code="400"
            )

        page = int(payload.get("page", 1))
        limit = int(payload.get("limit", 20))

        filters = {"inst_id": inst_id}
        if payload.get("statusFilter") or payload.get("status"):
            filters["status_filter"] = payload.get("statusFilter") or payload.get(
                "status"
            )
        if payload.get("sectionId") or payload.get("secId"):
            filters["sec_id"] = payload.get("sectionId") or payload.get("secId")

        result = await dal.get_approval_requests(filters, page=page, limit=limit)
        return XSCUtility.success_response(
            message="Approval requests retrieved successfully",
            data=result.get("data", []),
            page=page,
            limit=limit,
        )

    async def approval_action(self, payload, dal, context):
        """
        Approve or reject a timetable or update approval decision per BRS:
        payload: { inst_id, approvalId/timetableId, decision/action, remarks }
        Approve: PENDING_APPROVAL → PUBLISHED (becomes authoritative for downstream consumers)
        Reject: PENDING_APPROVAL → DRAFT (with rejection remarks)
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        tt_id = (
            payload.get("timetableId")
            or payload.get("ttId")
            or payload.get("approvalId")
        )
        decision = (
            payload.get("decision") or payload.get("action") or "APPROVE"
        ).upper()
        remarks = payload.get("remarks")

        if not inst_id or not tt_id:
            return XSCUtility.error_response(
                message="inst_id and timetableId/approvalId are required per BRS",
                error_code="400",
            )

        if not remarks or str(remarks).strip() == "":
            return XSCUtility.error_response(
                message="Decision remarks are required for approval/rejection per BRS",
                error_code="400",
            )

        if decision not in ("APPROVE", "REJECT", "UPDATE"):
            return XSCUtility.error_response(
                message="decision must be 'APPROVE' or 'REJECT'", error_code="400"
            )

        actor_id = self._get_actor_id(context)

        if decision in ("APPROVE", "UPDATE"):
            result = await dal.approve_timetable(tt_id, remarks, actor_id)
            action_msg = "approved and published"
        else:
            result = await dal.reject_timetable(tt_id, remarks, actor_id)
            action_msg = "rejected and reverted to draft"

        if result.get("status") == "error":
            return XSCUtility.error_response(
                message=result.get("message", "Failed to process approval action"),
                error_code="500",
            )

        result_data = result.get("data")
        return XSCUtility.success_response(
            message=f"Timetable {action_msg} successfully", data=result_data
        )

    async def approval_withdraw(self, payload, dal, context):
        """
        Withdraw a pending approval request per BRS:
        payload: { inst_id, approvalId/timetableId, remarks }
        Transitions from PENDING_APPROVAL → DRAFT.
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        tt_id = (
            payload.get("approvalId")
            or payload.get("timetableId")
            or payload.get("ttId")
        )
        remarks = payload.get("remarks") or "Withdrawn by requester"

        if not inst_id or not tt_id:
            return XSCUtility.error_response(
                message="inst_id and approvalId/timetableId are required per BRS",
                error_code="400",
            )

        actor_id = self._get_actor_id(context)
        result = await dal.withdraw_approval(tt_id, remarks, actor_id)

        if result.get("status") == "error":
            return XSCUtility.error_response(
                message=result.get("message", "Failed to withdraw approval request"),
                error_code="500",
            )

        return XSCUtility.success_response(
            message="Approval request withdrawn successfully. Timetable status reverted to DRAFT.",
            data=result.get("data"),
        )

    # --- Utility ---

    def _get_actor_id(self, context):
        """Extract the acting user ID from context."""
        if context and hasattr(context, "security") and context.security:
            return getattr(context.security, "user_id", None)
        return None
