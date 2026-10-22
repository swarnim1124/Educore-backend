"""
File: db_init.py
Description: SQLAlchemy 2.0 asynchronous ORM models for the OneApp Fees Module (`m_fees`).
This file maps the entire `sch_fees` schema, handling structure definition, student assignments,
financial ledger entries, payments, concessions, refunds, and penalties.

Author: Siddharth Amdal
App: OneApp

"""

from sqlalchemy import (
    Column,
    ForeignKey,
    Sequence,
    UniqueConstraint,
    CheckConstraint,
    Index,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import (
    BIGINT,
    INTEGER,
    NUMERIC,
    BOOLEAN,
    VARCHAR,
    TEXT,
    DATE,
    TIMESTAMP,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class TbFeeStructure(Base):
    """
    Master template for institutional fees.
    Maps to `sch_fees.tb_fee_structure`.
    """

    __tablename__ = "tb_fee_structure"
    __table_args__ = (
        UniqueConstraint(
            "institution_id", "fee_structure_code", name="uk_fee_structure_code"
        ),
        UniqueConstraint(
            "institution_id",
            "fee_structure_name",
            "acad_year_id",
            name="uk_fee_structure_name",
        ),
        CheckConstraint(
            "((effective_to IS NULL) OR (effective_to >= effective_from))",
            name="chk_fee_structure_dates",
        ),
        Index("idx_fee_struct_inst_status", "institution_id", "is_active", "status_id"),
        {"schema": "sch_fees"},
    )

    id = Column(
        BIGINT,
        Sequence("tb_fee_structure_id_seq", schema="sch_fees"),
        primary_key=True,
        nullable=False,
    )
    fee_structure_code = Column(VARCHAR(50), nullable=False)
    fee_structure_name = Column(VARCHAR(100), nullable=False)
    description = Column(TEXT, nullable=True)
    institution_id = Column(BIGINT, nullable=False)
    acad_year_id = Column(BIGINT, nullable=False)
    effective_from = Column(DATE, nullable=False)
    effective_to = Column(DATE, nullable=True)
    status_id = Column(INTEGER, nullable=False)
    is_active = Column(
        BOOLEAN, nullable=False, default=True, server_default=text("true")
    )
    created_by = Column(BIGINT, nullable=True)
    created_on = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
    )
    updated_by = Column(BIGINT, nullable=True)
    updated_on = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    components = relationship(
        "TbFeeStructureComponent",
        back_populates="fee_structure",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    rules = relationship(
        "TbFeeStructureRule",
        back_populates="fee_structure",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    assessments = relationship(
        "TbStudFeeAsmt", back_populates="fee_structure", lazy="noload"
    )


class TbFeeStructureRule(Base):
    """
    Defines the student criteria for which a fee structure applies.
    Maps to `sch_fees.tb_fee_structure_rule`.
    """

    __tablename__ = "tb_fee_structure_rule"
    __table_args__ = (
        UniqueConstraint(
            "fee_structure_id",
            "prog_id",
            "batch_id",
            "stud_category_id",
            "adm_quota_id",
            "reservation_category_id",
            "scholarship_category_id",
            name="uk_fee_structure_rule",
        ),
        CheckConstraint("(priority > 0)", name="chk_fee_structure_priority"),
        {"schema": "sch_fees"},
    )

    id = Column(
        BIGINT,
        Sequence("tb_fee_structure_rule_id_seq", schema="sch_fees"),
        primary_key=True,
        nullable=False,
    )
    fee_structure_id = Column(
        BIGINT,
        ForeignKey(
            "sch_fees.tb_fee_structure.id", onupdate="CASCADE", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    priority = Column(INTEGER, nullable=False)
    prog_id = Column(BIGINT, nullable=False)
    batch_id = Column(BIGINT, nullable=False)
    stud_category_id = Column(INTEGER, nullable=False)
    adm_quota_id = Column(INTEGER, nullable=False)
    reservation_category_id = Column(INTEGER, nullable=True)
    scholarship_category_id = Column(INTEGER, nullable=True)
    status_id = Column(INTEGER, nullable=False)
    is_active = Column(
        BOOLEAN, nullable=False, default=True, server_default=text("true")
    )
    created_by = Column(BIGINT, nullable=True)
    created_on = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
    )
    updated_by = Column(BIGINT, nullable=True)
    updated_on = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    fee_structure = relationship("TbFeeStructure", back_populates="rules")


class TbFeeStructureComponent(Base):
    """
    Specific line items in a fee structure.
    Maps to `sch_fees.tb_fee_structure_component`.
    """

    __tablename__ = "tb_fee_structure_component"
    __table_args__ = (
        UniqueConstraint(
            "fee_structure_id", "component_name", name="uk_fee_component_name"
        ),
        UniqueConstraint(
            "fee_structure_id", "fee_category_id", name="uk_fee_component_category"
        ),
        UniqueConstraint(
            "fee_structure_id", "display_order", name="uk_fee_component_order"
        ),
        CheckConstraint("(amount >= (0)::numeric)", name="chk_fee_component_amount"),
        CheckConstraint("(display_order > 0)", name="chk_fee_component_order"),
        {"schema": "sch_fees"},
    )

    id = Column(
        BIGINT,
        Sequence("tb_fee_structure_component_id_seq", schema="sch_fees"),
        primary_key=True,
        nullable=False,
    )
    fee_structure_id = Column(
        BIGINT,
        ForeignKey(
            "sch_fees.tb_fee_structure.id", onupdate="CASCADE", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    component_name = Column(VARCHAR(100), nullable=False)
    fee_category_id = Column(INTEGER, nullable=False)
    display_order = Column(INTEGER, nullable=False)
    amount = Column(NUMERIC(12, 2), nullable=False)
    is_refundable = Column(
        BOOLEAN, nullable=False, default=False, server_default=text("false")
    )
    is_optional = Column(
        BOOLEAN, nullable=False, default=False, server_default=text("false")
    )
    status_id = Column(INTEGER, nullable=False)
    is_active = Column(
        BOOLEAN, nullable=False, default=True, server_default=text("true")
    )
    created_by = Column(BIGINT, nullable=True)
    created_on = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
    )
    updated_by = Column(BIGINT, nullable=True)
    updated_on = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    fee_structure = relationship("TbFeeStructure", back_populates="components")


class TbInstallmentPlan(Base):
    """
    Master record for payment schedule configurations.
    Maps to `sch_fees.tb_installment_plan`.
    """

    __tablename__ = "tb_installment_plan"
    __table_args__ = (
        UniqueConstraint(
            "institution_id", "plan_code", name="uk_installment_plan_code"
        ),
        UniqueConstraint(
            "institution_id", "plan_name", name="uk_installment_plan_name"
        ),
        {"schema": "sch_fees"},
    )

    id = Column(
        BIGINT,
        Sequence("tb_installment_plan_id_seq", schema="sch_fees"),
        primary_key=True,
        nullable=False,
    )
    institution_id = Column(BIGINT, nullable=False)
    plan_code = Column(VARCHAR(50), nullable=False)
    plan_name = Column(VARCHAR(100), nullable=False)
    description = Column(TEXT, nullable=True)
    status_id = Column(INTEGER, nullable=False)
    is_active = Column(
        BOOLEAN, nullable=False, default=True, server_default=text("true")
    )
    created_by = Column(BIGINT, nullable=True)
    created_on = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
    )
    updated_by = Column(BIGINT, nullable=True)
    updated_on = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    details = relationship(
        "TbInstallmentPlanDetail", back_populates="plan", cascade="all, delete-orphan"
    )


class TbInstallmentPlanDetail(Base):
    """
    Specific due dates or intervals for an installment plan.
    Maps to `sch_fees.tb_installment_plan_detail`.
    """

    __tablename__ = "tb_installment_plan_detail"
    __table_args__ = (
        UniqueConstraint(
            "installment_plan_id", "installment_no", name="uk_installment_detail"
        ),
        CheckConstraint(
            "((fixed_amount IS NULL) OR (fixed_amount >= (0)::numeric))",
            name="chk_installment_amount",
        ),
        CheckConstraint("(installment_no > 0)", name="chk_installment_no"),
        CheckConstraint(
            "((percentage IS NULL) OR ((percentage >= (0)::numeric) AND (percentage <= (100)::numeric)))",
            name="chk_installment_percentage",
        ),
        {"schema": "sch_fees"},
    )

    id = Column(
        BIGINT,
        Sequence("tb_installment_plan_detail_id_seq", schema="sch_fees"),
        primary_key=True,
        nullable=False,
    )
    installment_plan_id = Column(
        BIGINT,
        ForeignKey(
            "sch_fees.tb_installment_plan.id", onupdate="CASCADE", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    installment_no = Column(INTEGER, nullable=False)
    installment_name = Column(VARCHAR(100), nullable=True)
    due_date = Column(DATE, nullable=False)
    percentage = Column(NUMERIC(5, 2), nullable=True)
    fixed_amount = Column(NUMERIC(12, 2), nullable=True)
    status_id = Column(INTEGER, nullable=False)
    is_active = Column(
        BOOLEAN, nullable=False, default=True, server_default=text("true")
    )
    created_by = Column(BIGINT, nullable=True)
    created_on = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
    )
    updated_by = Column(BIGINT, nullable=True)
    updated_on = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    plan = relationship("TbInstallmentPlan", back_populates="details")


class TbStudFeeAsmt(Base):
    """
    Links a student to a fee structure for a specific term (Logical Invoice Header).
    Maps to `sch_fees.tb_stud_fee_asmt`.
    """

    __tablename__ = "tb_stud_fee_asmt"
    __table_args__ = (
        UniqueConstraint("stud_enrollment_id", "acad_term_id", name="uk_stud_fee_asmt"),
        Index("idx_stud_asmt_enrollment", "stud_enrollment_id"),
        Index("idx_stud_asmt_struct_term", "fee_structure_id", "acad_term_id"),
        {"schema": "sch_fees"},
    )

    id = Column(
        BIGINT,
        Sequence("tb_stud_fee_asmt_id_seq", schema="sch_fees"),
        primary_key=True,
        nullable=False,
    )
    stud_enrollment_id = Column(BIGINT, nullable=False)
    acad_term_id = Column(BIGINT, nullable=False)
    fee_structure_id = Column(
        BIGINT,
        ForeignKey(
            "sch_fees.tb_fee_structure.id", onupdate="CASCADE", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    installment_plan_id = Column(
        BIGINT,
        ForeignKey(
            "sch_fees.tb_installment_plan.id", onupdate="CASCADE", ondelete="RESTRICT"
        ),
        nullable=True,
    )
    asmt_type_id = Column(INTEGER, nullable=False)
    asmt_date = Column(DATE, nullable=False)
    status_id = Column(INTEGER, nullable=False)
    is_active = Column(
        BOOLEAN, nullable=False, default=True, server_default=text("true")
    )
    created_by = Column(BIGINT, nullable=True)
    created_on = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
    )
    updated_by = Column(BIGINT, nullable=True)
    updated_on = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    fee_structure = relationship("TbFeeStructure", back_populates="assessments")
    components = relationship(
        "TbStudFeeComponent",
        back_populates="assessment",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    installments = relationship(
        "TbStudInstallment",
        back_populates="assessment",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    ledger_entries = relationship(
        "TbFinancialLedger", back_populates="assessment", lazy="noload"
    )
    penalties = relationship("TbPenalty", back_populates="assessment", lazy="noload")


class TbStudFeeComponent(Base):
    """
    Snapshot of fee components assessed to a student.
    Maps to `sch_fees.tb_stud_fee_component`.
    """

    __tablename__ = "tb_stud_fee_component"
    __table_args__ = (
        UniqueConstraint(
            "stud_fee_asmt_id",
            "fee_structure_component_id",
            name="uk_stud_fee_component",
        ),
        CheckConstraint(
            "(amount >= (0)::numeric)", name="chk_stud_fee_component_amount"
        ),
        {"schema": "sch_fees"},
    )

    id = Column(
        BIGINT,
        Sequence("tb_stud_fee_component_id_seq", schema="sch_fees"),
        primary_key=True,
        nullable=False,
    )
    stud_fee_asmt_id = Column(
        BIGINT,
        ForeignKey(
            "sch_fees.tb_stud_fee_asmt.id", onupdate="CASCADE", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    fee_structure_component_id = Column(
        BIGINT,
        ForeignKey(
            "sch_fees.tb_fee_structure_component.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    amount = Column(NUMERIC(12, 2), nullable=False)
    status_id = Column(INTEGER, nullable=False)
    is_active = Column(
        BOOLEAN, nullable=False, default=True, server_default=text("true")
    )
    created_by = Column(BIGINT, nullable=True)
    created_on = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
    )
    updated_by = Column(BIGINT, nullable=True)
    updated_on = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    assessment = relationship("TbStudFeeAsmt", back_populates="components")


class TbStudInstallment(Base):
    """
    Snapshot of the installment schedule assessed to a student.
    Maps to `sch_fees.tb_stud_installment`.
    """

    __tablename__ = "tb_stud_installment"
    __table_args__ = (
        UniqueConstraint(
            "stud_fee_asmt_id", "installment_no", name="uk_stud_installment"
        ),
        CheckConstraint("(amount >= (0)::numeric)", name="chk_stud_installment_amount"),
        CheckConstraint("(installment_no > 0)", name="chk_stud_installment_no"),
        {"schema": "sch_fees"},
    )

    id = Column(
        BIGINT,
        Sequence("tb_stud_installment_id_seq", schema="sch_fees"),
        primary_key=True,
        nullable=False,
    )
    stud_fee_asmt_id = Column(
        BIGINT,
        ForeignKey(
            "sch_fees.tb_stud_fee_asmt.id", onupdate="CASCADE", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    installment_no = Column(INTEGER, nullable=False)
    due_date = Column(DATE, nullable=False)
    amount = Column(NUMERIC(12, 2), nullable=False)
    status_id = Column(INTEGER, nullable=False)
    is_active = Column(
        BOOLEAN, nullable=False, default=True, server_default=text("true")
    )
    created_by = Column(BIGINT, nullable=True)
    created_on = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
    )
    updated_by = Column(BIGINT, nullable=True)
    updated_on = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    assessment = relationship("TbStudFeeAsmt", back_populates="installments")


class TbFinancialLedger(Base):
    """
    Central double-entry ledger tracking debits, credits, and running balance.
    Maps to `sch_fees.tb_financial_ledger`.
    """

    __tablename__ = "tb_financial_ledger"
    __table_args__ = (
        UniqueConstraint(
            "ledger_transaction_type_id",
            "reference_table_name",
            "reference_record_id",
            name="uk_financial_ledger",
        ),
        CheckConstraint(
            "((debit_amount >= (0)::numeric) AND (credit_amount >= (0)::numeric))",
            name="chk_ledger_amounts",
        ),
        Index("idx_ledger_enrollment", "stud_enrollment_id"),
        Index("idx_ledger_txn_date", "transaction_date"),
        {"schema": "sch_fees"},
    )

    id = Column(
        BIGINT,
        Sequence("tb_financial_ledger_id_seq", schema="sch_fees"),
        primary_key=True,
        nullable=False,
    )
    stud_enrollment_id = Column(BIGINT, nullable=False)
    stud_fee_asmt_id = Column(
        BIGINT,
        ForeignKey(
            "sch_fees.tb_stud_fee_asmt.id", onupdate="CASCADE", ondelete="RESTRICT"
        ),
        nullable=True,
    )
    ledger_transaction_type_id = Column(INTEGER, nullable=False)
    fee_category_id = Column(INTEGER, nullable=True)
    reference_table_name = Column(VARCHAR(50), nullable=False)
    reference_record_id = Column(BIGINT, nullable=False)
    transaction_date = Column(TIMESTAMP(timezone=True), nullable=False)
    debit_amount = Column(NUMERIC(12, 2), nullable=False, default=0)
    credit_amount = Column(NUMERIC(12, 2), nullable=False, default=0)
    running_balance = Column(NUMERIC(12, 2), nullable=True)
    remarks = Column(TEXT, nullable=True)
    status_id = Column(INTEGER, nullable=False)
    is_active = Column(
        BOOLEAN, nullable=False, default=True, server_default=text("true")
    )
    created_by = Column(BIGINT, nullable=True)
    created_on = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
    )
    updated_by = Column(BIGINT, nullable=True)
    updated_on = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    assessment = relationship("TbStudFeeAsmt", back_populates="ledger_entries")
    payment_allocations = relationship(
        "TbPaymentAllocation", back_populates="ledger_entry", lazy="noload"
    )


class TbPayment(Base):
    """
    Master record for a received payment.
    Maps to `sch_fees.tb_payment`.
    """

    __tablename__ = "tb_payment"
    __table_args__ = (
        UniqueConstraint("receipt_number", name="uk_payment_receipt"),
        CheckConstraint("(total_amount >= (0)::numeric)", name="chk_payment_amount"),
        Index("idx_payment_enrollment", "stud_enrollment_id"),
        Index("idx_payment_date", "payment_date"),
        {"schema": "sch_fees"},
    )

    id = Column(
        BIGINT,
        Sequence("tb_payment_id_seq", schema="sch_fees"),
        primary_key=True,
        nullable=False,
    )
    stud_enrollment_id = Column(BIGINT, nullable=False)
    payment_date = Column(TIMESTAMP(timezone=True), nullable=False)
    payment_method_id = Column(INTEGER, nullable=False)
    payment_gateway_id = Column(INTEGER, nullable=True)
    payment_source_id = Column(INTEGER, nullable=True)
    transaction_reference = Column(VARCHAR(100), nullable=True)
    total_amount = Column(NUMERIC(12, 2), nullable=False)
    receipt_number = Column(VARCHAR(50), nullable=False)
    doc_id = Column(BIGINT, nullable=True)
    payment_status_id = Column(INTEGER, nullable=False)
    status_id = Column(INTEGER, nullable=False)
    is_active = Column(
        BOOLEAN, nullable=False, default=True, server_default=text("true")
    )
    created_by = Column(BIGINT, nullable=True)
    created_on = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
    )
    updated_by = Column(BIGINT, nullable=True)
    updated_on = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    allocations = relationship(
        "TbPaymentAllocation",
        back_populates="payment",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    gateway_transactions = relationship(
        "TbPaymentGatewayTransaction",
        back_populates="payment",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    refunds = relationship("TbRefund", back_populates="payment", lazy="noload")


class TbPaymentAllocation(Base):
    """
    Junction settling a payment against specific financial ledger items.
    Maps to `sch_fees.tb_payment_allocation`.
    """

    __tablename__ = "tb_payment_allocation"
    __table_args__ = (
        UniqueConstraint(
            "payment_id", "financial_ledger_id", name="uk_payment_allocation"
        ),
        CheckConstraint(
            "(allocated_amount >= (0)::numeric)", name="chk_payment_allocation_amount"
        ),
        {"schema": "sch_fees"},
    )

    id = Column(
        BIGINT,
        Sequence("tb_payment_allocation_id_seq", schema="sch_fees"),
        primary_key=True,
        nullable=False,
    )
    payment_id = Column(
        BIGINT,
        ForeignKey("sch_fees.tb_payment.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    financial_ledger_id = Column(
        BIGINT,
        ForeignKey(
            "sch_fees.tb_financial_ledger.id", onupdate="CASCADE", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    allocation_date = Column(TIMESTAMP(timezone=True), nullable=False)
    allocated_amount = Column(NUMERIC(12, 2), nullable=False)
    status_id = Column(INTEGER, nullable=False)
    is_active = Column(
        BOOLEAN, nullable=False, default=True, server_default=text("true")
    )
    created_by = Column(BIGINT, nullable=True)
    created_on = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
    )
    updated_by = Column(BIGINT, nullable=True)
    updated_on = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    payment = relationship("TbPayment", back_populates="allocations")
    ledger_entry = relationship(
        "TbFinancialLedger", back_populates="payment_allocations"
    )


class TbPaymentGatewayTransaction(Base):
    """
    Technical log for online payment gateway responses.
    Maps to `sch_fees.tb_payment_gateway_transaction`.
    """

    __tablename__ = "tb_payment_gateway_transaction"
    __table_args__ = (
        UniqueConstraint("gateway_order_id", name="uk_gateway_order"),
        UniqueConstraint("gateway_payment_id", name="uk_gateway_payment"),
        UniqueConstraint("gateway_reference", name="uk_gateway_reference"),
        {"schema": "sch_fees"},
    )

    id = Column(
        BIGINT,
        Sequence("tb_payment_gateway_transaction_id_seq", schema="sch_fees"),
        primary_key=True,
        nullable=False,
    )
    payment_id = Column(
        BIGINT,
        ForeignKey("sch_fees.tb_payment.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    payment_gateway_id = Column(INTEGER, nullable=False)
    gateway_order_id = Column(VARCHAR(100), nullable=False)
    gateway_payment_id = Column(VARCHAR(100), nullable=True)
    gateway_reference = Column(TEXT, nullable=True)
    gateway_response_date = Column(TIMESTAMP(timezone=True), nullable=True)
    gateway_status_id = Column(INTEGER, nullable=False)
    status_id = Column(INTEGER, nullable=False)
    is_active = Column(
        BOOLEAN, nullable=False, default=True, server_default=text("true")
    )
    created_by = Column(BIGINT, nullable=True)
    created_on = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
    )
    updated_by = Column(BIGINT, nullable=True)
    updated_on = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    payment = relationship("TbPayment", back_populates="gateway_transactions")


class TbScholarship(Base):
    """
    Record of a scholarship granted to a student.
    Maps to `sch_fees.tb_scholarship`.
    """

    __tablename__ = "tb_scholarship"
    __table_args__ = (
        UniqueConstraint(
            "stud_enrollment_id", "scholarship_name", name="uk_scholarship"
        ),
        CheckConstraint("(amount >= (0)::numeric)", name="chk_scholarship_amount"),
        Index("idx_scholarship_enroll", "stud_enrollment_id"),
        {"schema": "sch_fees"},
    )

    id = Column(
        BIGINT,
        Sequence("tb_scholarship_id_seq", schema="sch_fees"),
        primary_key=True,
        nullable=False,
    )
    stud_enrollment_id = Column(BIGINT, nullable=False)
    scholarship_type_id = Column(INTEGER, nullable=False)
    scholarship_name = Column(VARCHAR(100), nullable=False)
    amount = Column(NUMERIC(12, 2), nullable=False)
    sanction_date = Column(DATE, nullable=False)
    approved_by = Column(BIGINT, nullable=True)
    approved_on = Column(TIMESTAMP(timezone=True), nullable=True)
    doc_id = Column(BIGINT, nullable=True)
    remarks = Column(TEXT, nullable=True)
    approval_status_id = Column(INTEGER, nullable=False)
    status_id = Column(INTEGER, nullable=False)
    is_active = Column(
        BOOLEAN, nullable=False, default=True, server_default=text("true")
    )
    created_by = Column(BIGINT, nullable=True)
    created_on = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
    )
    updated_by = Column(BIGINT, nullable=True)
    updated_on = Column(TIMESTAMP(timezone=True), nullable=True)


class TbConcession(Base):
    """
    Record of a manual or categorical concession granted.
    Maps to `sch_fees.tb_concession`.
    """

    __tablename__ = "tb_concession"
    __table_args__ = (
        UniqueConstraint("stud_enrollment_id", "concession_name", name="uk_concession"),
        CheckConstraint("(amount >= (0)::numeric)", name="chk_concession_amount"),
        Index("idx_concession_enroll", "stud_enrollment_id"),
        {"schema": "sch_fees"},
    )

    id = Column(
        BIGINT,
        Sequence("tb_concession_id_seq", schema="sch_fees"),
        primary_key=True,
        nullable=False,
    )
    stud_enrollment_id = Column(BIGINT, nullable=False)
    concession_type_id = Column(INTEGER, nullable=False)
    concession_name = Column(VARCHAR(100), nullable=False)
    amount = Column(NUMERIC(12, 2), nullable=False)
    sanction_date = Column(DATE, nullable=False)
    approved_by = Column(BIGINT, nullable=True)
    approved_on = Column(TIMESTAMP(timezone=True), nullable=True)
    doc_id = Column(BIGINT, nullable=True)
    remarks = Column(TEXT, nullable=True)
    approval_status_id = Column(INTEGER, nullable=False)
    status_id = Column(INTEGER, nullable=False)
    is_active = Column(
        BOOLEAN, nullable=False, default=True, server_default=text("true")
    )
    created_by = Column(BIGINT, nullable=True)
    created_on = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
    )
    updated_by = Column(BIGINT, nullable=True)
    updated_on = Column(TIMESTAMP(timezone=True), nullable=True)


class TbRefund(Base):
    """
    Record of a refund issued against a payment.
    Maps to `sch_fees.tb_refund`.
    """

    __tablename__ = "tb_refund"
    __table_args__ = (
        UniqueConstraint("payment_id", name="uk_refund_payment"),
        CheckConstraint("(amount >= (0)::numeric)", name="chk_refund_amount"),
        {"schema": "sch_fees"},
    )

    id = Column(
        BIGINT,
        Sequence("tb_refund_id_seq", schema="sch_fees"),
        primary_key=True,
        nullable=False,
    )
    stud_enrollment_id = Column(BIGINT, nullable=False)
    payment_id = Column(
        BIGINT,
        ForeignKey("sch_fees.tb_payment.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    refund_date = Column(TIMESTAMP(timezone=True), nullable=False)
    amount = Column(NUMERIC(12, 2), nullable=False)
    reason = Column(TEXT, nullable=True)
    approved_by = Column(BIGINT, nullable=True)
    approved_on = Column(TIMESTAMP(timezone=True), nullable=True)
    refund_status_id = Column(INTEGER, nullable=False)
    status_id = Column(INTEGER, nullable=False)
    is_active = Column(
        BOOLEAN, nullable=False, default=True, server_default=text("true")
    )
    created_by = Column(BIGINT, nullable=True)
    created_on = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
    )
    updated_by = Column(BIGINT, nullable=True)
    updated_on = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    payment = relationship("TbPayment", back_populates="refunds")


class TbFeeWaiver(Base):
    """
    Record of a fee waiver granted.
    Maps to `sch_fees.tb_fee_waiver`.
    """

    __tablename__ = "tb_fee_waiver"
    __table_args__ = (
        UniqueConstraint("stud_enrollment_id", "waiver_name", name="uk_fee_waiver"),
        CheckConstraint("(amount >= (0)::numeric)", name="chk_fee_waiver_amount"),
        {"schema": "sch_fees"},
    )

    id = Column(
        BIGINT,
        Sequence("tb_fee_waiver_id_seq", schema="sch_fees"),
        primary_key=True,
        nullable=False,
    )
    stud_enrollment_id = Column(BIGINT, nullable=False)
    waiver_type_id = Column(INTEGER, nullable=False)
    waiver_name = Column(VARCHAR(100), nullable=False)
    amount = Column(NUMERIC(12, 2), nullable=False)
    sanction_date = Column(DATE, nullable=False)
    approved_by = Column(BIGINT, nullable=True)
    approved_on = Column(TIMESTAMP(timezone=True), nullable=True)
    doc_id = Column(BIGINT, nullable=True)
    remarks = Column(TEXT, nullable=True)
    waiver_status_id = Column(INTEGER, nullable=False)
    status_id = Column(INTEGER, nullable=False)
    is_active = Column(
        BOOLEAN, nullable=False, default=True, server_default=text("true")
    )
    created_by = Column(BIGINT, nullable=True)
    created_on = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
    )
    updated_by = Column(BIGINT, nullable=True)
    updated_on = Column(TIMESTAMP(timezone=True), nullable=True)


class TbPenalty(Base):
    """
    Record of a late fee penalty levied.
    Maps to `sch_fees.tb_penalty`.
    """

    __tablename__ = "tb_penalty"
    __table_args__ = (
        CheckConstraint("(amount >= (0)::numeric)", name="chk_penalty_amount"),
        Index("idx_penalty_enroll", "stud_enrollment_id"),
        {"schema": "sch_fees"},
    )

    id = Column(
        BIGINT,
        Sequence("tb_penalty_id_seq", schema="sch_fees"),
        primary_key=True,
        nullable=False,
    )
    stud_enrollment_id = Column(BIGINT, nullable=False)
    stud_fee_asmt_id = Column(
        BIGINT,
        ForeignKey(
            "sch_fees.tb_stud_fee_asmt.id", onupdate="CASCADE", ondelete="RESTRICT"
        ),
        nullable=True,
    )
    penalty_type_id = Column(INTEGER, nullable=False)
    penalty_date = Column(TIMESTAMP(timezone=True), nullable=False)
    amount = Column(NUMERIC(12, 2), nullable=False)
    reason = Column(TEXT, nullable=True)
    penalty_status_id = Column(INTEGER, nullable=False)
    status_id = Column(INTEGER, nullable=False)
    is_active = Column(
        BOOLEAN, nullable=False, default=True, server_default=text("true")
    )
    created_by = Column(BIGINT, nullable=True)
    created_on = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
    )
    updated_by = Column(BIGINT, nullable=True)
    updated_on = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    assessment = relationship("TbStudFeeAsmt", back_populates="penalties")


class TbFinancialHold(Base):
    """
    System block preventing student progression.
    Maps to `sch_fees.tb_financial_hold`.
    """

    __tablename__ = "tb_financial_hold"
    __table_args__ = (
        CheckConstraint(
            "((end_date IS NULL) OR (end_date >= start_date))",
            name="chk_financial_hold_dates",
        ),
        {"schema": "sch_fees"},
    )

    id = Column(
        BIGINT,
        Sequence("tb_financial_hold_id_seq", schema="sch_fees"),
        primary_key=True,
        nullable=False,
    )
    stud_enrollment_id = Column(BIGINT, nullable=False)
    hold_type_id = Column(INTEGER, nullable=False)
    hold_reason = Column(TEXT, nullable=False)
    start_date = Column(DATE, nullable=False)
    end_date = Column(DATE, nullable=True)
    released_by = Column(BIGINT, nullable=True)
    released_on = Column(TIMESTAMP(timezone=True), nullable=True)
    hold_status_id = Column(INTEGER, nullable=False)
    status_id = Column(INTEGER, nullable=False)
    is_active = Column(
        BOOLEAN, nullable=False, default=True, server_default=text("true")
    )
    created_by = Column(BIGINT, nullable=True)
    created_on = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
    )
    updated_by = Column(BIGINT, nullable=True)
    updated_on = Column(TIMESTAMP(timezone=True), nullable=True)
