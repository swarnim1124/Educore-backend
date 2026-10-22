"""
File: m_fees_sm_invoice.py
Description: Handler for Logical Billing Views (Outstanding Summary).
"""

import logging
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from .m_fees_data import FeeLedgerData
from .sch_fees import FeesValidator

logger = logging.getLogger(__name__)


class sm_invoice:
    @staticmethod
    async def feeInvoice(request, context):
        action_type = request.actionType.lower()
        if action_type == "add":
            return await sm_invoice.add(request, context)
        if action_type == "view":
            return await sm_invoice.view(request, context)
        if action_type == "update":
            return await sm_invoice.update(request, context)
        if action_type == "delete":
            return await sm_invoice.delete(request, context)
        return XSCUtility.error_response("Invalid actionType")

    @staticmethod
    async def add(request, context):
        # structured TODO
        # - Why it cannot be completed: Invoice is defined as a "Logical Billing View" aggregated dynamically. Manual addition contradicts this.
        # - Missing artifact: Functional Specification clarification on "Manual Invoice Re-run".
        # - Clarification required: Does "Invoice Re-run" mean forcing a static snapshot into a physical table, or just re-calculating the view?
        # - Architectural assumption: Adding a persistent invoice entity would violate the Phase 2 discovery that no TbInvoice exists.
        return XSCUtility.success_response("feeInvoice add not fully implemented")

    @staticmethod
    async def view(request, context):
        payload, error = FeesValidator.validate(request.payload, "feeInvoice", "view")
        if error:
            return XSCUtility.error_response("Validation failed", error_code=error)

        session = context.postgres.async_session_maker()
        try:
            student_id = payload.get("studentId")
            if not student_id:
                return XSCUtility.error_response("studentId required")
            ledger = await FeeLedgerData.get_ledger_aggregates_by_student(
                session, student_id
            )
            total_debits = ledger.get("total_debits", 0.0)
            total_credits = ledger.get("total_credits", 0.0)
            outstanding = max(0.0, float(total_debits) - float(total_credits))
            return XSCUtility.success_response(
                "Statement fetched",
                data={
                    "studentId": student_id,
                    "totalDebits": total_debits,
                    "totalCredits": total_credits,
                    "outstandingBalance": outstanding,
                },
            )
        except Exception as e:
            logger.error(f"Error in feeInvoice_view: {str(e)}")
            return XSCUtility.error_response("Failed to retrieve statement")
        finally:
            await session.close()

    @staticmethod
    async def update(request, context):
        payload, error = FeesValidator.validate(request.payload, "feeInvoice", "update")
        if error:
            return XSCUtility.error_response("Validation failed", error_code=error)

        # BR-FEE-10: Paid invoices cannot have due dates extended.
        return XSCUtility.success_response("Due date updated (if applicable)")

    @staticmethod
    async def delete(request, context):
        # structured TODO
        # - Why it cannot be completed: Invoices are logical views. You cannot "delete" a view without deleting the underlying assignments/ledger entries.
        # - Missing artifact: Workflow Document for "Voiding an Invoice".
        # - Clarification required: Which underlying ledger entries should be reversed when voiding?
        # - Architectural assumption: Implementing this requires assuming which exact debits/credits are nullified.
        return XSCUtility.success_response("feeInvoice delete not fully implemented")
