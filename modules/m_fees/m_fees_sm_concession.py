"""
File: m_fees_sm_concession.py
Description: Handler for Fee Concession.
"""

import logging
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from .m_fees_data import FeeConcessionData, FeeLedgerData
from .sch_fees import FeesValidator

logger = logging.getLogger(__name__)


class sm_concession:
    @staticmethod
    async def feeConcession(request, context):
        action_type = request.actionType.lower()
        if action_type == "add":
            return await sm_concession.add(request, context)
        if action_type == "view":
            return await sm_concession.view(request, context)
        if action_type == "update":
            return await sm_concession.update(request, context)
        if action_type == "delete":
            return await sm_concession.delete(request, context)
        return XSCUtility.error_response("Invalid actionType")

    @staticmethod
    async def add(request, context):
        payload, error = FeesValidator.validate(request.payload, "feeConcession", "add")
        if error:
            return XSCUtility.error_response("Validation failed", error_code=error)

        session = context.postgres.async_session_maker()
        try:
            student_id = payload.get("studentId")
            concession_amt = payload.get("amountOrPercent", 0.0)
            await FeeConcessionData.create_concession(session, payload)
            await FeeLedgerData.create_ledger_entries(
                session,
                [
                    {
                        "student_id": student_id,
                        "debit_amount": 0.0,
                        "credit_amount": concession_amt,
                        "transaction_type": "CONCESSION",
                        "transaction_re": f"CONC_{student_id}",
                    }
                ],
            )
            await session.commit()
            return XSCUtility.success_response("Concession applied successfully")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in feeConcession_add: {str(e)}")
            return XSCUtility.error_response("Concession failed")
        finally:
            await session.close()

    @staticmethod
    async def view(request, context):
        # structured TODO
        # - Why it cannot be completed: Phase 2 DAL (FeeConcessionData) lacks a generalized `get_concession` or paginated fetch method.
        # - Missing artifact: Phase 2 DAL implementation for concession retrieval.
        # - Clarification required: Should students see all history, or just active concessions?
        # - Architectural assumption: Implementing would require writing SQL directly in the Business Layer, violating architecture rules.
        return XSCUtility.success_response("feeConcession view not fully implemented")

    @staticmethod
    async def update(request, context):
        # structured TODO
        # - Why it cannot be completed: Updating a concession's amount requires reversing the previous ledger credit and applying a new one. This exact workflow is not documented.
        # - Missing artifact: Functional Flow Document detailing concession modifications.
        # - Clarification required: Is a concession update an in-place edit, or a cancel-and-reissue workflow?
        # - Architectural assumption: Assuming in-place edits on double-entry ledgers risks financial audit trail corruption.
        return XSCUtility.success_response("feeConcession update not fully implemented")

    @staticmethod
    async def delete(request, context):
        # structured TODO
        # - Why it cannot be completed: "Withdrawing a concession" is mentioned but the reversal workflow is undefined.
        # - Missing artifact: Business Rules regarding concession withdrawal limits and ledger reversal.
        # - Clarification required: Should deleting a concession post a debit to the ledger to reinstate the liability?
        # - Architectural assumption: Inventing the ledger reversal logic without explicit approval.
        return XSCUtility.success_response("feeConcession delete not fully implemented")
