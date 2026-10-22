"""
File: m_fees_sm_fee_assignment.py
Description: Handler for Fee Assignment entity.
"""

import logging
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from .m_fees_data import FeeAssignmentData, FeeLedgerData
from .sch_fees import FeesValidator

logger = logging.getLogger(__name__)


class sm_fee_assignment:
    @staticmethod
    async def feeAssignment(request, context):
        action_type = request.actionType.lower()
        if action_type == "add":
            return await sm_fee_assignment.add(request, context)
        if action_type == "view":
            return await sm_fee_assignment.view(request, context)
        if action_type == "update":
            return await sm_fee_assignment.update(request, context)
        if action_type == "delete":
            return await sm_fee_assignment.delete(request, context)
        return XSCUtility.error_response("Invalid actionType")

    @staticmethod
    async def add(request, context):
        payload, error = FeesValidator.validate(request.payload, "feeAssignment", "add")
        if error:
            return XSCUtility.error_response("Validation failed", error_code=error)

        session = context.postgres.async_session_maker()
        try:
            student_ids = payload.get("studentIds", [])
            if payload.get("studentId"):
                student_ids.append(payload.get("studentId"))

            structure_id = payload.get("feeStructureId")
            assessments = []
            ledger_debits = []
            for sid in student_ids:
                assessments.append(
                    {"student_id": sid, "fee_structure_id": structure_id}
                )
                ledger_debits.append(
                    {
                        "student_id": sid,
                        "debit_amount": payload.get(
                            "amount", 0.0
                        ),  # Assuming this needs to be looked up ideally
                        "credit_amount": 0.0,
                        "transaction_type": "FEE_ASSESSMENT",
                        "transaction_re": f"ASMT_{structure_id}_{sid}",
                    }
                )
            await FeeAssignmentData.create_bulk_assessments(session, assessments)
            await FeeLedgerData.create_ledger_entries(session, ledger_debits)
            await session.commit()
            return XSCUtility.success_response(
                f"Successfully assigned fees to {len(student_ids)} students."
            )
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in feeAssignment_add: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Failed to process bulk fee assignment")
        finally:
            await session.close()

    @staticmethod
    async def view(request, context):
        payload, error = FeesValidator.validate(
            request.payload, "feeAssignment", "view"
        )
        if error:
            return XSCUtility.error_response("Validation failed", error_code=error)

        session = context.postgres.async_session_maker()
        try:
            student_id = payload.get("studentId")
            records = await FeeAssignmentData.get_student_assessments(
                session, student_id
            )
            return XSCUtility.success_response(
                "Data fetched", data=[{"stud_asmt_id": r.id} for r in records]
            )
        except Exception as e:
            logger.error(f"Error in feeAssignment_view: {str(e)}")
            return XSCUtility.error_response("Error fetching assignments")
        finally:
            await session.close()

    @staticmethod
    async def update(request, context):
        return XSCUtility.success_response("feeAssignment update not fully implemented")

    @staticmethod
    async def delete(request, context):
        payload, error = FeesValidator.validate(
            request.payload, "feeAssignment", "delete"
        )
        if error:
            return XSCUtility.error_response("Validation failed", error_code=error)

        session = context.postgres.async_session_maker()
        try:
            asmt_id = payload.get("assignmentId")
            await FeeAssignmentData.update_assessment(
                session, asmt_id, {"is_active": False}
            )
            await session.commit()
            return XSCUtility.success_response("Deactivated assessment")
        except Exception:
            await session.rollback()
            return XSCUtility.error_response("Deletion failed")
        finally:
            await session.close()


# Alias for legacy camelCase class reference
sm_feeAssignment = sm_fee_assignment
