"""
File: m_fees_data.py
Description: Data Access Layer (DAL) for the OneApp Fees Module (`m_fees`).
This layer is strictly responsible for database persistence and query operations.
It encapsulates SQLAlchemy 2.0 ORM interactions and natively supports the Phase 3 Business Layer.
No business logic, validations, or transaction orchestrations reside here.

Repository Method Inventory:
--------------------------------------------------
FeeStructureData:
  - create_fee_structure(session, data: dict) -> TbFeeStructure
  - get_fee_structures(session, limit: int, offset: int) -> list[TbFeeStructure]
  - update_fee_structure(session, structure_id: int, data: dict) -> TbFeeStructure
  - get_fee_structure_components(session, structure_id: int) -> list[TbFeeStructureComponent]

FeeAssignmentData:
  - create_bulk_assessments(session, assessments: list[dict]) -> list[TbStudFeeAsmt]
  - get_student_assessments(session, student_id: int) -> list[TbStudFeeAsmt]
  - get_active_assessments_with_components(session, student_id: int) -> list[TbStudFeeAsmt]
  - update_assessment(session, assessment_id: int, data: dict) -> TbStudFeeAsmt

FeeConcessionData:
  - create_scholarship(session, data: dict) -> TbScholarship
  - create_concession(session, data: dict) -> TbConcession
  - get_student_concessions(session, student_id: int) -> list[TbConcession]
  - update_concession(session, concession_id: int, data: dict) -> TbConcession

FeeLedgerData:
  - create_ledger_entries(session, entries: list[dict]) -> list[TbFinancialLedger]
  - get_ledger_aggregates_by_student(session, student_id: int) -> dict
  - lock_and_get_ledger_row(session, ledger_id: int) -> TbFinancialLedger

FeePaymentData:
  - create_payment(session, data: dict) -> TbPayment
  - create_gateway_transaction(session, data: dict) -> TbPaymentGatewayTransaction
  - create_payment_allocations(session, allocations: list[dict]) -> list[TbPaymentAllocation]
  - get_payment_history(session, student_id: int) -> list[TbPayment]

FeeRefundData:
  - create_refund(session, data: dict) -> TbRefund
  - get_refunds(session, filters: dict) -> list[TbRefund]
  - update_refund(session, refund_id: int, data: dict) -> TbRefund

FeePenaltyData:
  - create_penalty(session, data: dict) -> TbPenalty
  - create_financial_hold(session, data: dict) -> TbFinancialHold
  - get_penalties(session, filters: dict) -> list[TbPenalty]
  - update_financial_hold(session, hold_id: int, data: dict) -> TbFinancialHold

Author: Siddharth Amdal
App: OneApp

"""

from typing import List, Dict, Any, Optional
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from .db_init import (
    TbFeeStructure,
    TbFeeStructureComponent,
    TbStudFeeAsmt,
    TbFinancialLedger,
    TbPayment,
    TbPaymentAllocation,
    TbPaymentGatewayTransaction,
    TbScholarship,
    TbConcession,
    TbRefund,
    TbPenalty,
    TbFinancialHold,
)


class FeeStructureData:
    """
    Repository for the sm_feeStructure submodule.
    Manages institutional master templates for fees.
    """

    @staticmethod
    async def create_fee_structure(
        session: AsyncSession, data: Dict[str, Any]
    ) -> TbFeeStructure:
        entity = TbFeeStructure(**data)
        session.add(entity)
        await session.flush()
        return entity

    @staticmethod
    async def get_fee_structures(
        session: AsyncSession, limit: int = 100, offset: int = 0
    ) -> List[TbFeeStructure]:
        stmt = (
            select(TbFeeStructure)
            .where(TbFeeStructure.is_active.is_(True))
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update_fee_structure(
        session: AsyncSession, structure_id: int, data: Dict[str, Any]
    ) -> Optional[TbFeeStructure]:
        stmt = (
            update(TbFeeStructure)
            .where(TbFeeStructure.fee_structure_id == structure_id)
            .values(**data)
            .returning(TbFeeStructure)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_fee_structure_components(
        session: AsyncSession, structure_id: int
    ) -> List[TbFeeStructureComponent]:
        stmt = select(TbFeeStructureComponent).where(
            TbFeeStructureComponent.fee_structure_id == structure_id,
            TbFeeStructureComponent.is_active.is_(True),
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())


class FeeAssignmentData:
    """
    Repository for the sm_feeAssignment submodule.
    Manages logical student fee liabilities and bulk assignments.
    """

    @staticmethod
    async def create_bulk_assessments(
        session: AsyncSession, assessments: List[Dict[str, Any]]
    ) -> List[TbStudFeeAsmt]:
        entities = [TbStudFeeAsmt(**a) for a in assessments]
        session.add_all(entities)
        await session.flush()
        return entities

    @staticmethod
    async def get_student_assessments_by_student(
        session: AsyncSession, student_id: int
    ) -> List[TbStudFeeAsmt]:
        stmt = select(TbStudFeeAsmt).where(TbStudFeeAsmt.student_id == student_id)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_student_assessments(
        session: AsyncSession, stud_enrollment_id: int
    ) -> List[TbStudFeeAsmt]:
        stmt = select(TbStudFeeAsmt).where(
            TbStudFeeAsmt.stud_enrollment_id == stud_enrollment_id
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_active_assessments_with_components(
        session: AsyncSession, stud_enrollment_id: int
    ) -> List[TbStudFeeAsmt]:
        stmt = (
            select(TbStudFeeAsmt)
            .options(joinedload(TbStudFeeAsmt.components))
            .where(
                TbStudFeeAsmt.stud_enrollment_id == stud_enrollment_id,
                TbStudFeeAsmt.is_active.is_(True),
            )
        )
        result = await session.execute(stmt)
        return list(result.unique().scalars().all())

    @staticmethod
    async def update_assessment(
        session: AsyncSession, assessment_id: int, data: Dict[str, Any]
    ) -> Optional[TbStudFeeAsmt]:
        stmt = (
            update(TbStudFeeAsmt)
            .where(TbStudFeeAsmt.stud_asmt_id == assessment_id)
            .values(**data)
            .returning(TbStudFeeAsmt)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


class FeeConcessionData:
    """
    Repository for the sm_concession submodule.
    Persists scholarships, discounts, and fee waivers.
    """

    @staticmethod
    async def create_scholarship(
        session: AsyncSession, data: Dict[str, Any]
    ) -> TbScholarship:
        entity = TbScholarship(**data)
        session.add(entity)
        await session.flush()
        return entity

    @staticmethod
    async def create_concession(
        session: AsyncSession, data: Dict[str, Any]
    ) -> TbConcession:
        entity = TbConcession(**data)
        session.add(entity)
        await session.flush()
        return entity

    @staticmethod
    async def get_student_concessions(
        session: AsyncSession, student_id: int
    ) -> List[TbConcession]:
        stmt = select(TbConcession).where(
            TbConcession.student_id == student_id, TbConcession.is_active.is_(True)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update_concession(
        session: AsyncSession, concession_id: int, data: Dict[str, Any]
    ) -> Optional[TbConcession]:
        stmt = (
            update(TbConcession)
            .where(TbConcession.concession_id == concession_id)
            .values(**data)
            .returning(TbConcession)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


class FeeLedgerData:
    """
    Core Financial Ledger persistence. Supports multiple submodules.
    Persists double-entry accounting records (debits/credits).
    """

    @staticmethod
    async def create_ledger_entries(
        session: AsyncSession, entries: List[Dict[str, Any]]
    ) -> List[TbFinancialLedger]:
        entities = [TbFinancialLedger(**e) for e in entries]
        session.add_all(entities)
        await session.flush()
        return entities

    @staticmethod
    async def get_ledger_aggregates_by_student(
        session: AsyncSession, stud_enrollment_id: int
    ) -> Dict[str, Any]:
        """
        Returns raw aggregates for credits and debits to feed logical invoice construction.
        """
        stmt = select(
            func.sum(TbFinancialLedger.debit_amount).label("total_debits"),
            func.sum(TbFinancialLedger.credit_amount).label("total_credits"),
        ).where(
            TbFinancialLedger.stud_enrollment_id == stud_enrollment_id,
            TbFinancialLedger.status_id == 1,
        )
        result = await session.execute(stmt)
        row = result.first()
        return {
            "total_debits": float(row.total_debits or 0),
            "total_credits": float(row.total_credits or 0),
        }

    @staticmethod
    async def lock_and_get_ledger_row(
        session: AsyncSession, ledger_id: int
    ) -> Optional[TbFinancialLedger]:
        """
        Retrieves a ledger row with pessimistic locking (SELECT FOR UPDATE)
        to ensure concurrency safety during payment allocation updates.
        """
        stmt = (
            select(TbFinancialLedger)
            .where(TbFinancialLedger.ledger_id == ledger_id)
            .with_for_update()
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


class FeePaymentData:
    """
    Repository for the sm_payment submodule.
    Persists payments, allocations, and gateway interactions.
    """

    @staticmethod
    async def create_payment(session: AsyncSession, data: Dict[str, Any]) -> TbPayment:
        entity = TbPayment(**data)
        session.add(entity)
        await session.flush()
        return entity

    @staticmethod
    async def create_gateway_transaction(
        session: AsyncSession, data: Dict[str, Any]
    ) -> TbPaymentGatewayTransaction:
        entity = TbPaymentGatewayTransaction(**data)
        session.add(entity)
        await session.flush()
        return entity

    @staticmethod
    async def create_payment_allocations(
        session: AsyncSession, allocations: List[Dict[str, Any]]
    ) -> List[TbPaymentAllocation]:
        entities = [TbPaymentAllocation(**a) for a in allocations]
        session.add_all(entities)
        await session.flush()
        return entities

    @staticmethod
    async def get_payment_history(
        session: AsyncSession, student_id: int
    ) -> List[TbPayment]:
        stmt = select(TbPayment).where(
            TbPayment.student_id == student_id, TbPayment.is_active.is_(True)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())


class FeeRefundData:
    """
    Repository for the sm_refund submodule.
    Persists refund workflows and outcomes.
    """

    @staticmethod
    async def create_refund(session: AsyncSession, data: Dict[str, Any]) -> TbRefund:
        entity = TbRefund(**data)
        session.add(entity)
        await session.flush()
        return entity

    @staticmethod
    async def get_refunds(
        session: AsyncSession, filters: Dict[str, Any]
    ) -> List[TbRefund]:
        stmt = select(TbRefund)
        for key, value in filters.items():
            if hasattr(TbRefund, key):
                stmt = stmt.where(getattr(TbRefund, key) == value)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update_refund(
        session: AsyncSession, refund_id: int, data: Dict[str, Any]
    ) -> Optional[TbRefund]:
        stmt = (
            update(TbRefund)
            .where(TbRefund.refund_id == refund_id)
            .values(**data)
            .returning(TbRefund)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


class FeePenaltyData:
    """
    Repository for the sm_penalty submodule.
    Persists disciplinary and late fees along with system holds.
    """

    @staticmethod
    async def create_penalty(session: AsyncSession, data: Dict[str, Any]) -> TbPenalty:
        entity = TbPenalty(**data)
        session.add(entity)
        await session.flush()
        return entity

    @staticmethod
    async def create_financial_hold(
        session: AsyncSession, data: Dict[str, Any]
    ) -> TbFinancialHold:
        entity = TbFinancialHold(**data)
        session.add(entity)
        await session.flush()
        return entity

    @staticmethod
    async def get_penalties(
        session: AsyncSession, filters: Dict[str, Any]
    ) -> List[TbPenalty]:
        stmt = select(TbPenalty)
        for key, value in filters.items():
            if hasattr(TbPenalty, key):
                stmt = stmt.where(getattr(TbPenalty, key) == value)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update_financial_hold(
        session: AsyncSession, hold_id: int, data: Dict[str, Any]
    ) -> Optional[TbFinancialHold]:
        stmt = (
            update(TbFinancialHold)
            .where(TbFinancialHold.hold_id == hold_id)
            .values(**data)
            .returning(TbFinancialHold)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
