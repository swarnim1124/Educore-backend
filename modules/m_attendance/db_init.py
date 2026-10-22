"""
File: db_init.py
Description: SQLAlchemy 2.0 asynchronous ORM models for the OneApp Attendance Module (`m_attendance`).

Author: Siddharth Amdal
App: OneApp

"""

from sqlalchemy import (
    Column,
    ForeignKey,
    Sequence,
    UniqueConstraint,
    CheckConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import (
    BIGINT,
    INTEGER,
    SMALLINT,
    NUMERIC,
    BOOLEAN,
    VARCHAR,
    TEXT,
    DATE,
    TIMESTAMP,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class TbAttPolicy(Base):
    """
    SQLAlchemy ORM model for institutional attendance policies and rules.
    Maps to `sch_attendance.tb_att_policy`.
    """

    __tablename__ = "tb_att_policy"
    __table_args__ = (
        UniqueConstraint("inst_id", "policy_name", name="uk_att_policy"),
        CheckConstraint(
            "(effective_to IS NULL) OR (effective_from IS NULL) OR (effective_to >= effective_from)",
            name="chk_att_policy_dates",
        ),
        CheckConstraint(
            "(min_att_percent >= (0)::numeric) AND (min_att_percent <= (100)::numeric)",
            name="chk_att_policy_percent",
        ),
        CheckConstraint(
            "((late_marking_window_minutes IS NULL) OR (late_marking_window_minutes >= 0)) AND ((auto_lock_after_hours IS NULL) OR (auto_lock_after_hours >= 0))",
            name="chk_att_policy_windows",
        ),
        {"schema": "sch_attendance"},
    )

    id = Column(
        INTEGER,
        Sequence("tb_att_policy_id_seq", schema="sch_attendance"),
        primary_key=True,
        nullable=False,
    )
    inst_id = Column(
        BIGINT,
        ForeignKey(
            "sch_org.tb_inst.id",
            name="fk_att_policy_inst",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    policy_name = Column(VARCHAR, nullable=False)
    min_att_percent = Column(NUMERIC, nullable=False)
    allow_late_marking = Column(
        BOOLEAN, nullable=False, default=False, server_default=text("false")
    )
    late_marking_window_minutes = Column(SMALLINT, nullable=True)
    auto_lock_after_hours = Column(SMALLINT, nullable=True)
    require_approval = Column(
        BOOLEAN, nullable=False, default=False, server_default=text("false")
    )
    require_med_proof = Column(
        BOOLEAN, nullable=False, default=False, server_default=text("false")
    )
    effective_from = Column(DATE, nullable=True)
    effective_to = Column(DATE, nullable=True)
    is_active = Column(
        BOOLEAN, nullable=False, default=True, server_default=text("true")
    )
    created_by = Column(
        BIGINT,
        ForeignKey(
            "sch_iam.tb_user.id",
            name="fk_att_policy_created_by",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    created_on = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
    )
    updated_by = Column(
        BIGINT,
        ForeignKey(
            "sch_iam.tb_user.id",
            name="fk_att_policy_updated_by",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    updated_on = Column(TIMESTAMP(timezone=True), nullable=True)


class TbAttSession(Base):
    """
    SQLAlchemy ORM model for attendance marking sessions linked to scheduled timetable sessions.
    Maps to `sch_attendance.tb_att_session`.
    """

    __tablename__ = "tb_att_session"
    __table_args__ = (
        UniqueConstraint("class_session_id", name="uk_att_session"),
        CheckConstraint(
            "((submitted_at IS NULL) OR (started_at IS NULL) OR (submitted_at >= started_at)) AND ((locked_at IS NULL) OR (submitted_at IS NULL) OR (locked_at >= submitted_at))",
            name="chk_att_session_times",
        ),
        {"schema": "sch_attendance"},
    )

    id = Column(
        BIGINT,
        Sequence("tb_att_session_id_seq", schema="sch_attendance"),
        primary_key=True,
        nullable=False,
    )
    class_session_id = Column(
        BIGINT,
        ForeignKey(
            "sch_timetable.tb_class_session.id",
            name="fk_att_session_class",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    session_date = Column(DATE, nullable=False)
    marked_by_fac_id = Column(
        BIGINT,
        ForeignKey(
            "sch_employee.tb_fac.id",
            name="fk_att_session_marked_by",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    status_id = Column(
        SMALLINT,
        ForeignKey(
            "sch_lookup.tb_lookup.id",
            name="fk_att_session_status",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    started_at = Column(TIMESTAMP(timezone=True), nullable=True)
    submitted_at = Column(TIMESTAMP(timezone=True), nullable=True)
    locked_at = Column(TIMESTAMP(timezone=True), nullable=True)
    remarks = Column(TEXT, nullable=True)
    created_by = Column(
        BIGINT,
        ForeignKey(
            "sch_iam.tb_user.id",
            name="fk_att_session_created_by",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    created_on = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
    )
    updated_by = Column(
        BIGINT,
        ForeignKey(
            "sch_iam.tb_user.id",
            name="fk_att_session_updated_by",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    updated_on = Column(TIMESTAMP(timezone=True), nullable=True)

    records = relationship(
        "TbAttRecord",
        back_populates="session",
        foreign_keys="[TbAttRecord.att_session_id]",
    )


class TbAttRecord(Base):
    """
    SQLAlchemy ORM model for individual student attendance entries within a session.
    Maps to `sch_attendance.tb_att_record`.
    """

    __tablename__ = "tb_att_record"
    __table_args__ = (
        UniqueConstraint("att_session_id", "stud_id", name="uk_att_record"),
        {"schema": "sch_attendance"},
    )

    id = Column(
        BIGINT,
        Sequence("tb_att_record_id_seq", schema="sch_attendance"),
        primary_key=True,
        nullable=False,
    )
    att_session_id = Column(
        BIGINT,
        ForeignKey(
            "sch_attendance.tb_att_session.id",
            name="fk_att_record_session",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    stud_id = Column(
        BIGINT,
        ForeignKey(
            "sch_student.tb_stud.id",
            name="fk_att_record_student",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    att_status_id = Column(
        SMALLINT,
        ForeignKey(
            "sch_lookup.tb_lookup.id",
            name="fk_att_record_status",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    marked_at = Column(TIMESTAMP(timezone=True), nullable=True)
    remarks = Column(TEXT, nullable=True)
    created_by = Column(
        BIGINT,
        ForeignKey(
            "sch_iam.tb_user.id",
            name="fk_att_record_created_by",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    created_on = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
    )
    updated_by = Column(
        BIGINT,
        ForeignKey(
            "sch_iam.tb_user.id",
            name="fk_att_record_updated_by",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    updated_on = Column(TIMESTAMP(timezone=True), nullable=True)

    session = relationship(
        "TbAttSession", back_populates="records", foreign_keys=[att_session_id]
    )
    corrections = relationship(
        "TbAttCorrection",
        back_populates="record",
        foreign_keys="[TbAttCorrection.att_record_id]",
    )


class TbAttCorrection(Base):
    """
    SQLAlchemy ORM model for attendance exception, condonation, and correction workflows.
    Maps to `sch_attendance.tb_att_correction`.
    """

    __tablename__ = "tb_att_correction"
    __table_args__ = (
        UniqueConstraint("att_record_id", "requested_at", name="uk_att_correction"),
        CheckConstraint(
            "(approved_at IS NULL) OR (approved_at >= requested_at)",
            name="chk_att_correction_time",
        ),
        {"schema": "sch_attendance"},
    )

    id = Column(
        BIGINT,
        Sequence("tb_att_correction_id_seq", schema="sch_attendance"),
        primary_key=True,
        nullable=False,
    )
    att_record_id = Column(
        BIGINT,
        ForeignKey(
            "sch_attendance.tb_att_record.id",
            name="fk_att_corr_record",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    old_status_id = Column(
        SMALLINT,
        ForeignKey(
            "sch_lookup.tb_lookup.id",
            name="fk_att_corr_old_status",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    new_status_id = Column(
        SMALLINT,
        ForeignKey(
            "sch_lookup.tb_lookup.id",
            name="fk_att_corr_new_status",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    requested_by_user_id = Column(
        BIGINT,
        ForeignKey(
            "sch_iam.tb_user.id",
            name="fk_att_corr_requested_by",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    approved_by_user_id = Column(
        BIGINT,
        ForeignKey(
            "sch_iam.tb_user.id",
            name="fk_att_corr_approved_by",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    status_id = Column(
        SMALLINT,
        ForeignKey(
            "sch_lookup.tb_lookup.id",
            name="fk_att_corr_status",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    correction_reason_id = Column(
        SMALLINT,
        ForeignKey(
            "sch_lookup.tb_lookup.id",
            name="fk_att_corr_reason",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    proof_doc_id = Column(
        BIGINT,
        ForeignKey(
            "sch_core.tb_dms.id",
            name="fk_att_corr_proof_doc",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    requested_at = Column(TIMESTAMP(timezone=True), nullable=False)
    approved_at = Column(TIMESTAMP(timezone=True), nullable=True)
    remarks = Column(TEXT, nullable=True)
    created_by = Column(
        BIGINT,
        ForeignKey(
            "sch_iam.tb_user.id",
            name="fk_att_corr_created_by",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    created_on = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
    )
    updated_by = Column(
        BIGINT,
        ForeignKey(
            "sch_iam.tb_user.id",
            name="fk_att_corr_updated_by",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    updated_on = Column(TIMESTAMP(timezone=True), nullable=True)

    record = relationship(
        "TbAttRecord", back_populates="corrections", foreign_keys=[att_record_id]
    )


class TbStudentLeave(Base):
    """
    SQLAlchemy ORM model for student leave applications.
    Maps to `sch_attendance.tb_student_leave`.
    """

    __tablename__ = "tb_student_leave"
    __table_args__ = {"schema": "sch_attendance"}

    id = Column(
        BIGINT,
        Sequence("tb_student_leave_id_seq", schema="sch_attendance"),
        primary_key=True,
        nullable=False,
    )
    stud_id = Column(
        BIGINT,
        ForeignKey(
            "sch_student.tb_stud.id",
            name="fk_stud_leave_student",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    leave_type_id = Column(
        SMALLINT,
        ForeignKey(
            "sch_lookup.tb_lookup.id",
            name="fk_stud_leave_type",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    from_date = Column(DATE, nullable=False)
    to_date = Column(DATE, nullable=False)
    reason = Column(TEXT, nullable=False)
    medical_doc_id = Column(
        BIGINT,
        ForeignKey(
            "sch_core.tb_dms.id",
            name="fk_stud_leave_medical_doc",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    status = Column(VARCHAR(20), nullable=False, default="pending")
    created_by = Column(
        BIGINT,
        ForeignKey(
            "sch_iam.tb_user.id",
            name="fk_stud_leave_created_by",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    created_on = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
    )
    updated_by = Column(
        BIGINT,
        ForeignKey(
            "sch_iam.tb_user.id",
            name="fk_stud_leave_updated_by",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    updated_on = Column(TIMESTAMP(timezone=True), nullable=True)
