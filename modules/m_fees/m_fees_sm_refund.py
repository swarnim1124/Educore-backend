"""
File: m_fees_sm_refund.py
Description: Handler for Fee Refunds.
"""

import logging
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from .m_fees_data import FeeRefundData, FeeLedgerData
from .sch_fees import FeesValidator

logger = logging.getLogger(__name__)


class sm_refund:
    @staticmethod
    async def feeRefund(request, context):
        action_type = request.actionType.lower()
        if action_type == "add":
            return await sm_refund.add(request, context)
        if action_type == "view":
            return await sm_refund.view(request, context)
        if action_type == "update":
            return await sm_refund.update(request, context)
        if action_type == "delete":
            return await sm_refund.delete(request, context)
        return XSCUtility.error_response("Invalid actionType")

    @staticmethod
    async def add(request, context):
        payload, error = FeesValidator.validate(request.payload, "feeRefund", "add")
        if error:
            return XSCUtility.error_response("Validation failed", error_code=error)

        session = context.postgres.async_session_maker()
        try:
            await FeeRefundData.create_refund(session, payload)
            await session.commit()
            return XSCUtility.success_response("Refund requested successfully")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in feeRefund_add: {str(e)}")
            return XSCUtility.error_response("Refund request failed")
        finally:
            await session.close()

    @staticmethod
    async def view(request, context):
        # structured TODO
        # - Why it cannot be completed: Phase 2 DAL (FeeRefundData) lacks a `get_refunds` method.
        # - Missing artifact: Phase 2 DAL implementation for refund retrieval.
        # - Clarification required: Pagination and filtering requirements for the Finance queue.
        # - Architectural assumption: Implementing this requires raw SQL in the Business Layer.
        return XSCUtility.success_response("feeRefund view not fully implemented")

    @staticmethod
    async def update(request, context):
        payload, error = FeesValidator.validate(request.payload, "feeRefund", "update")
        if error:
            return XSCUtility.error_response("Validation failed", error_code=error)

        session = context.postgres.async_session_maker()
        try:
            status = payload.get("status")
            refund_id = payload.get("refundId")
            await FeeRefundData.update_refund(session, refund_id, payload)
            if status == "APPROVED":
                await FeeLedgerData.create_ledger_entries(
                    session,
                    [
                        {
                            "student_id": payload.get("studentId"),
                            "debit_amount": payload.get("amount", 0.0),
                            "credit_amount": 0.0,
                            "transaction_type": "REFUND",
                            "transaction_re": f"REF_{refund_id}",
                        }
                    ],
                )
            await session.commit()
            return XSCUtility.success_response("Refund status updated")
        except Exception as e:
            await session.rollback()
            return XSCUtility.error_response("Refund update failed")
        finally:
            await session.close()

    @staticmethod
    async def delete(request, context):
        # structured TODO
        # - Why it cannot be completed: Deleting a refund request is not documented. Refunds are state-managed (Pending -> Approved/Rejected).
        # - Missing artifact: Workflow for cancelling a Pending refund request.
        # - Clarification required: Can a student cancel their own refund request?
        # - Architectural assumption: Introducing a hard delete bypasses the state machine.
        return XSCUtility.success_response("feeRefund delete not fully implemented")
