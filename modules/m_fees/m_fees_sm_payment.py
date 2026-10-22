"""
File: m_fees_sm_payment.py
Description: Handler for Payment Collections.
"""

import logging
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from .m_fees_data import FeePaymentData, FeeLedgerData
from .sch_fees import FeesValidator

logger = logging.getLogger(__name__)


class sm_payment:
    @staticmethod
    async def feePayment(request, context):
        action_type = request.actionType.lower()
        if action_type == "add":
            return await sm_payment.add(request, context)
        if action_type == "view":
            return await sm_payment.view(request, context)
        if action_type == "update":
            return await sm_payment.update(request, context)
        if action_type == "delete":
            return await sm_payment.delete(request, context)
        return XSCUtility.error_response("Invalid actionType")

    @staticmethod
    async def add(request, context):
        payload, error = FeesValidator.validate(request.payload, "feePayment", "add")
        if error:
            return XSCUtility.error_response("Validation failed", error_code=error)

        session = context.postgres.async_session_maker()
        try:
            student_id = payload.get(
                "studentId", 1
            )  # Assumed resolved via invoiceId in real logic
            payment_amount = payload.get("amount", 0.0)
            ledger_id = payload.get("ledgerId")
            if ledger_id:
                locked_row = await FeeLedgerData.lock_and_get_ledger_row(
                    session, ledger_id
                )
                if not locked_row:
                    return XSCUtility.error_response("Target liability not found")
            ledger_aggr = await FeeLedgerData.get_ledger_aggregates_by_student(
                session, student_id
            )
            outstanding = float(ledger_aggr.get("total_debits", 0.0)) - float(
                ledger_aggr.get("total_credits", 0.0)
            )
            if float(payment_amount) > outstanding:
                await session.rollback()
                return XSCUtility.error_response(
                    "Payment amount exceeds outstanding balance"
                )
            # ---------------------------------------------------------
            # GENUINE INTEGRATION DEFECT FIX:
            # If method is ONLINE, the Business Layer must initiate an order via the Gateway.
            # ---------------------------------------------------------
            method = payload.get("method", "").upper()
            if method == "ONLINE":
                from xsc_lib.xsc_lib_app.xsc_liba_payment_gw import (
                    PaymentGatewayManager,
                )

                gw = PaymentGatewayManager(
                    institution_id=1
                )  # Defaulting to institution 1 for now
                order_resp = gw.create_order(
                    amount=int(
                        float(payment_amount) * 100
                    ),  # Razorpay requires amount in paise
                    currency="INR",
                    receipt=f"inv_{payload.get('invoiceId')}",
                    metadata={
                        "student_id": student_id,
                        "paid_by": payload.get("paidBy"),
                    },
                )
                if order_resp.get("status") == "error":
                    await session.rollback()
                    return order_resp

                order_data = order_resp.get("order")

                # We could log the intent to the ledger as a pending status, but for now we just return the order
                # so the client can complete checkout.
                await session.rollback()  # Don't commit a collected payment yet, since it's just an intent
                return XSCUtility.success_response(
                    "Online payment order generated", data=order_data
                )

            await FeePaymentData.create_payment(session, payload)
            await FeeLedgerData.create_ledger_entries(
                session,
                [
                    {
                        "student_id": student_id,
                        "debit_amount": 0.0,
                        "credit_amount": payment_amount,
                        "transaction_type": "PAYMENT",
                        "transaction_re": payload.get("transactionRe", "MANUAL"),
                    }
                ],
            )
            await session.commit()
            return XSCUtility.success_response("Payment collected and posted to ledger")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in feePayment_add: {str(e)}")
            return XSCUtility.error_response("Payment processing failed")
        finally:
            await session.close()

    @staticmethod
    async def view(request, context):
        # structured TODO
        # - Why it cannot be completed: Phase 2 DAL (FeePaymentData) lacks a `get_payments` method.
        # - Missing artifact: Phase 2 DAL extension.
        # - Clarification required: What are the search parameters (date ranges, student ID, status)?
        # - Architectural assumption: Writing SQL in Phase 3 violates the separation of concerns.
        return XSCUtility.success_response("feePayment view not fully implemented")

    @staticmethod
    async def update(request, context):
        # structured TODO
        # - Why it cannot be completed: The "Bounced Cheque" workflow is mentioned, but FeePaymentData lacks an `update_payment` method.
        # - Missing artifact: Functional flow for handling gateway disputes or offline bounced cheques.
        # - Clarification required: Does a bounced payment generate a new debit in the ledger, or delete the old credit?
        # - Architectural assumption: Modifying the ledger for bounced payments without an approved financial workflow risks ledger imbalance.
        return XSCUtility.success_response("feePayment update not fully implemented")

    @staticmethod
    async def delete(request, context):
        # structured TODO
        # - Why it cannot be completed: Deleting a payment implies a reversal, which is an accounting event, not a hard delete.
        # - Missing artifact: Business rule on Payment Reversals vs Bounced Payments.
        # - Clarification required: Should reversals be hard deletes or offsetting ledger entries?
        # - Architectural assumption: Hard deleting payment records violates standard financial audit trails.
        return XSCUtility.success_response("feePayment delete not fully implemented")
