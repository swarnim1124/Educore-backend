"""
File: sch_fees.py
Description: Pydantic schemas and standard OneApp payloads for the m_fees module.
Defines strict validation for incoming requests and formats for outgoing responses.

Author: Siddharth Amdal
App: OneApp

"""

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import date
from decimal import Decimal

# ---------------------------------------------------------
# Reusable Validators
# ---------------------------------------------------------


def validate_currency_decimal(v: Decimal) -> Decimal:
    """Ensures monetary values do not exceed 2 decimal places."""
    if v.as_tuple().exponent < -2:
        raise ValueError("Amount cannot have more than 2 decimal places")
    return v


# ---------------------------------------------------------
# Shared Models
# ---------------------------------------------------------


class BaseOneAppRequest(BaseModel):
    mod: str
    subMod: str
    action: str
    actionType: str
    payload: Dict[str, Any]


class BaseOneAppResponse(BaseModel):
    status: str
    message: str
    data: Optional[Any] = None


class FeeComponentSchema(BaseModel):
    headCode: str = Field(..., min_length=1, max_length=50)
    headName: str = Field(..., min_length=1, max_length=100)
    amount: Decimal = Field(..., ge=0)
    isOptional: bool = False

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        return validate_currency_decimal(v)


# ---------------------------------------------------------
# sm_feeStructure (Action: feeStructure)
# ---------------------------------------------------------


class FeeStructureAddPayload(BaseModel):
    inst_id: int = Field(..., gt=0)
    feeStructureCode: str = Field(..., min_length=1, max_length=50)
    feeStructureName: str = Field(..., min_length=1, max_length=100)
    academicYearId: int = Field(..., gt=0)
    programmeId: int = Field(..., gt=0)
    components: List[FeeComponentSchema] = Field(..., min_items=1)
    effectiveFrom: date
    effectiveTo: Optional[date] = None


class FeeStructureViewPayload(BaseModel):
    # Optional filters
    feeStructureId: Optional[int] = Field(None, gt=0)
    inst_id: Optional[int] = Field(None, gt=0)


class FeeStructureUpdatePayload(BaseModel):
    feeStructureId: int = Field(..., gt=0)
    components: Optional[List[FeeComponentSchema]] = None
    effectiveTo: Optional[date] = None
    status: Optional[str] = None


class FeeStructureDeletePayload(BaseModel):
    feeStructureId: int = Field(..., gt=0)


# ---------------------------------------------------------
# sm_feeAssignment (Action: feeAssignment)
# ---------------------------------------------------------


class FeeAssignmentAddPayload(BaseModel):
    feeStructureId: int = Field(..., gt=0)
    termId: int = Field(..., gt=0)
    dueDate: date
    studentId: Optional[int] = None
    studentIds: Optional[List[int]] = None

    @model_validator(mode="after")
    def check_student_presence(self) -> "FeeAssignmentAddPayload":
        if not self.studentIds and not self.studentId:
            raise ValueError("Either studentId or studentIds must be provided")
        return self


class FeeAssignmentViewPayload(BaseModel):
    studentId: Optional[int] = Field(None, gt=0)
    assignmentId: Optional[int] = Field(None, gt=0)


class FeeAssignmentUpdatePayload(BaseModel):
    assignmentId: int = Field(..., gt=0)
    dueDate: Optional[date] = None
    feeStructureId: Optional[int] = None


class FeeAssignmentDeletePayload(BaseModel):
    assignmentId: int = Field(..., gt=0)


# ---------------------------------------------------------
# sm_concession (Action: feeConcession)
# ---------------------------------------------------------


class FeeConcessionAddPayload(BaseModel):
    studentId: int = Field(..., gt=0)
    assignmentId: int = Field(..., gt=0)
    concessionType: str = Field(..., min_length=1)
    amountOrPercent: Decimal = Field(..., gt=0)
    reason: str = Field(..., min_length=1)
    attachments: Optional[List[str]] = None


class FeeConcessionViewPayload(BaseModel):
    studentId: Optional[int] = Field(None, gt=0)


class FeeConcessionUpdatePayload(BaseModel):
    concessionId: int = Field(..., gt=0)
    amountOrPercent: Optional[Decimal] = Field(None, gt=0)
    reason: Optional[str] = None


class FeeConcessionDeletePayload(BaseModel):
    concessionId: int = Field(..., gt=0)


# ---------------------------------------------------------
# sm_invoice (Action: feeInvoice)
# ---------------------------------------------------------


class FeeInvoiceAddPayload(BaseModel):
    assignmentId: int = Field(..., gt=0)


class FeeInvoiceViewPayload(BaseModel):
    invoiceId: Optional[int] = Field(None, gt=0)
    studentId: Optional[int] = Field(None, gt=0)


class FeeInvoiceUpdatePayload(BaseModel):
    invoiceId: int = Field(..., gt=0)
    dueDate: date


class FeeInvoiceDeletePayload(BaseModel):
    # Invoices are typically voided, not hard-deleted, but following the standard CRUD
    invoiceId: int = Field(..., gt=0)


# ---------------------------------------------------------
# sm_payment (Action: feePayment)
# ---------------------------------------------------------


class FeePaymentAddPayload(BaseModel):
    invoiceId: int = Field(..., gt=0)
    amount: Decimal = Field(..., gt=0)
    method: str = Field(..., min_length=1)
    transactionRef: Optional[str] = None
    paidBy: str = Field(..., min_length=1)

    @field_validator("amount")
    @classmethod
    def validate_payment_amount(cls, v: Decimal) -> Decimal:
        return validate_currency_decimal(v)


class FeePaymentViewPayload(BaseModel):
    paymentId: Optional[int] = Field(None, gt=0)
    studentId: Optional[int] = Field(None, gt=0)


class FeePaymentUpdatePayload(BaseModel):
    paymentId: int = Field(..., gt=0)
    status: str = Field(..., min_length=1)


class FeePaymentDeletePayload(BaseModel):
    paymentId: int = Field(..., gt=0)


# ---------------------------------------------------------
# sm_refund (Action: feeRefund)
# ---------------------------------------------------------


class FeeRefundAddPayload(BaseModel):
    studentId: int = Field(..., gt=0)
    invoiceId: int = Field(..., gt=0)
    amount: Decimal = Field(..., gt=0)
    reason: str = Field(..., min_length=1)

    @field_validator("amount")
    @classmethod
    def validate_refund_amount(cls, v: Decimal) -> Decimal:
        return validate_currency_decimal(v)


class FeeRefundViewPayload(BaseModel):
    refundId: Optional[int] = Field(None, gt=0)
    studentId: Optional[int] = Field(None, gt=0)


class FeeRefundUpdatePayload(BaseModel):
    refundId: int = Field(..., gt=0)
    status: str = Field(..., min_length=1)
    remarks: Optional[str] = None


class FeeRefundDeletePayload(BaseModel):
    refundId: int = Field(..., gt=0)
    remarks: str = Field(..., min_length=1)


# ---------------------------------------------------------
# sm_penalty (Action: feePenalty)
# ---------------------------------------------------------


class FeePenaltyAddPayload(BaseModel):
    inst_id: int = Field(..., gt=0)
    gracePeriodDays: int = Field(..., ge=0)
    penaltyType: str = Field(..., min_length=1)
    penaltyValue: Decimal = Field(..., gt=0)


class FeePenaltyViewPayload(BaseModel):
    inst_id: Optional[int] = Field(None, gt=0)


class FeePenaltyUpdatePayload(BaseModel):
    inst_id: int = Field(..., gt=0)
    gracePeriodDays: Optional[int] = Field(None, ge=0)
    penaltyType: Optional[str] = None
    penaltyValue: Optional[Decimal] = Field(None, gt=0)


class FeePenaltyDeletePayload(BaseModel):
    inst_id: int = Field(..., gt=0)


# ---------------------------------------------------------
# Standard Error Response
# ---------------------------------------------------------
class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class FeesValidator:
    @staticmethod
    def validate(payload: dict, action: str, actionType: str):
        schema_map = {
            "feeStructure": {
                "add": FeeStructureAddPayload,
                "view": FeeStructureViewPayload,
                "update": FeeStructureUpdatePayload,
                "delete": FeeStructureDeletePayload,
            },
            "feeAssignment": {
                "add": FeeAssignmentAddPayload,
                "view": FeeAssignmentViewPayload,
                "update": FeeAssignmentUpdatePayload,
                "delete": FeeAssignmentDeletePayload,
            },
            "feeConcession": {
                "add": FeeConcessionAddPayload,
                "view": FeeConcessionViewPayload,
                "update": FeeConcessionUpdatePayload,
                "delete": FeeConcessionDeletePayload,
            },
            "feeInvoice": {
                "add": FeeInvoiceAddPayload,
                "view": FeeInvoiceViewPayload,
                "update": FeeInvoiceUpdatePayload,
                "delete": FeeInvoiceDeletePayload,
            },
            "feePayment": {
                "add": FeePaymentAddPayload,
                "view": FeePaymentViewPayload,
                "update": FeePaymentUpdatePayload,
                "delete": FeePaymentDeletePayload,
            },
            "feeRefund": {
                "add": FeeRefundAddPayload,
                "view": FeeRefundViewPayload,
                "update": FeeRefundUpdatePayload,
                "delete": FeeRefundDeletePayload,
            },
            "feePenalty": {
                "add": FeePenaltyAddPayload,
                "view": FeePenaltyViewPayload,
                "update": FeePenaltyUpdatePayload,
                "delete": FeePenaltyDeletePayload,
            },
        }

        schema = schema_map.get(action, {}).get(actionType)
        if not schema:
            return payload, None

        try:
            validated = schema(**payload)
            # Serialize Decimal correctly and return dict
            dumped = validated.model_dump(exclude_none=True)
            return dumped, None
        except Exception as e:
            return None, str(e)
