"""
File: db_init.py
Description: SQLAlchemy models for m_curriculum.

Author: Siddharth Amdal
App: OneApp

"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    Date,
    SmallInteger,
    BigInteger,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TbProg(Base):
    __tablename__ = "tb_prog"
    __table_args__ = {"schema": "sch_academic_struct"}

    id = Column(Integer, primary_key=True)
    institution_id = Column(
        BigInteger, ForeignKey("sch_org.tb_inst.id"), nullable=False
    )
    department_id = Column(BigInteger, ForeignKey("sch_org.tb_dept.id"), nullable=False)
    prog_type_id = Column(
        SmallInteger, ForeignKey("sch_lookup.tb_lookup.id"), nullable=False
    )
    prog_code = Column(String, nullable=False)
    prog_name = Column(String, nullable=False)
    duration = Column(SmallInteger, nullable=False)
    duration_unit_id = Column(
        SmallInteger, ForeignKey("sch_lookup.tb_lookup.id"), nullable=False
    )
    total_terms = Column(SmallInteger, nullable=False)
    total_credits = Column(Numeric, nullable=False)
    status_id = Column(
        SmallInteger, ForeignKey("sch_lookup.tb_lookup.id"), nullable=False
    )


class TbCrs(Base):
    __tablename__ = "tb_crs"
    __table_args__ = {"schema": "sch_academic_struct"}

    id = Column(Integer, primary_key=True)
    crs_code = Column(String, nullable=False)
    crs_name = Column(String, nullable=False)
    crs_type_id = Column(
        SmallInteger, ForeignKey("sch_lookup.tb_lookup.id"), nullable=False
    )
    credit_value = Column(Numeric, nullable=False)
    lecture_hours = Column(Numeric, nullable=False)
    tutorial_hours = Column(Numeric, nullable=False)
    practical_hours = Column(Numeric, nullable=False)
    status_id = Column(
        SmallInteger, ForeignKey("sch_lookup.tb_lookup.id"), nullable=False
    )


class TbCrsVersion(Base):
    __tablename__ = "tb_crs_version"
    __table_args__ = {"schema": "sch_academic_struct"}

    id = Column(Integer, primary_key=True)
    crs_id = Column(
        Integer, ForeignKey("sch_academic_struct.tb_crs.id"), nullable=False
    )
    version_no = Column(SmallInteger, nullable=False)
    revision_no = Column(SmallInteger, nullable=False)
    effective_from = Column(Date, nullable=False)
    is_current = Column(Boolean, nullable=False)
    status_id = Column(
        SmallInteger, ForeignKey("sch_lookup.tb_lookup.id"), nullable=False
    )


class TbCrsPrerequisite(Base):
    __tablename__ = "tb_crs_prerequisite"
    __table_args__ = {"schema": "sch_academic_struct"}

    id = Column(Integer, primary_key=True)
    crs_version_id = Column(
        Integer, ForeignKey("sch_academic_struct.tb_crs_version.id"), nullable=False
    )
    prerequisite_crs_version_id = Column(
        Integer, ForeignKey("sch_academic_struct.tb_crs_version.id"), nullable=False
    )
    status_id = Column(
        SmallInteger, ForeignKey("sch_lookup.tb_lookup.id"), nullable=False
    )


class TbCrsCorequisite(Base):
    __tablename__ = "tb_crs_corequisite"
    __table_args__ = {"schema": "sch_academic_struct"}

    id = Column(Integer, primary_key=True)
    crs_version_id = Column(
        Integer, ForeignKey("sch_academic_struct.tb_crs_version.id"), nullable=False
    )
    corequisite_crs_version_id = Column(
        Integer, ForeignKey("sch_academic_struct.tb_crs_version.id"), nullable=False
    )
    status_id = Column(
        SmallInteger, ForeignKey("sch_lookup.tb_lookup.id"), nullable=False
    )


class TbCurr(Base):
    __tablename__ = "tb_curr"
    __table_args__ = {"schema": "sch_academic_struct"}

    id = Column(Integer, primary_key=True)
    prog_id = Column(
        Integer, ForeignKey("sch_academic_struct.tb_prog.id"), nullable=False
    )
    curr_name = Column(String, nullable=False)
    status_id = Column(
        SmallInteger, ForeignKey("sch_lookup.tb_lookup.id"), nullable=False
    )


class TbCurrVersion(Base):
    __tablename__ = "tb_curr_version"
    __table_args__ = {"schema": "sch_academic_struct"}

    id = Column(Integer, primary_key=True)
    curr_id = Column(
        Integer, ForeignKey("sch_academic_struct.tb_curr.id"), nullable=False
    )
    version_no = Column(SmallInteger, nullable=False)
    version_name = Column(String, nullable=False)
    total_credits = Column(Numeric, nullable=False)
    effective_from = Column(Date, nullable=False)
    is_current = Column(Boolean, nullable=False)
    status_id = Column(
        SmallInteger, ForeignKey("sch_lookup.tb_lookup.id"), nullable=False
    )


class TbCurrTerm(Base):
    __tablename__ = "tb_curr_term"
    __table_args__ = {"schema": "sch_academic_struct"}

    id = Column(Integer, primary_key=True)
    curr_version_id = Column(
        Integer, ForeignKey("sch_academic_struct.tb_curr_version.id"), nullable=False
    )
    term_number = Column(SmallInteger, nullable=False)
    total_credits = Column(Numeric, nullable=False)
    status_id = Column(
        SmallInteger, ForeignKey("sch_lookup.tb_lookup.id"), nullable=False
    )


class TbCurrTermCrs(Base):
    __tablename__ = "tb_curr_term_crs"
    __table_args__ = {"schema": "sch_academic_struct"}

    id = Column(Integer, primary_key=True)
    curr_term_id = Column(
        Integer, ForeignKey("sch_academic_struct.tb_curr_term.id"), nullable=False
    )
    crs_version_id = Column(
        Integer, ForeignKey("sch_academic_struct.tb_crs_version.id"), nullable=False
    )
    is_mandatory = Column(Boolean, nullable=False)
    status_id = Column(
        SmallInteger, ForeignKey("sch_lookup.tb_lookup.id"), nullable=False
    )


class TbStudEnrollment(Base):
    __tablename__ = "tb_stud_enrollment"
    __table_args__ = {"schema": "sch_student"}

    id = Column(BigInteger, primary_key=True)
    stud_id = Column(BigInteger, ForeignKey("sch_student.tb_stud.id"), nullable=False)
    prog_intake_id = Column(
        Integer, ForeignKey("sch_admission.tb_prog_intake.id"), nullable=False
    )
    adm_type_id = Column(
        SmallInteger, ForeignKey("sch_lookup.tb_lookup.id"), nullable=False
    )
    enrollment_date = Column(Date, nullable=False)
    status_id = Column(
        SmallInteger, ForeignKey("sch_lookup.tb_lookup.id"), nullable=False
    )
    is_current = Column(Boolean, nullable=False)
    created_on = Column(DateTime(timezone=True), nullable=False)


class TbStudCrsRegistration(Base):
    __tablename__ = "tb_stud_crs_registration"
    __table_args__ = {"schema": "sch_course_delivery"}

    id = Column(BigInteger, primary_key=True)
    stud_id = Column(BigInteger, ForeignKey("sch_student.tb_stud.id"), nullable=False)
    crs_offering_id = Column(
        BigInteger, ForeignKey("sch_course_delivery.tb_crs_offering.id"), nullable=False
    )
    registration_status_id = Column(
        SmallInteger, ForeignKey("sch_lookup.tb_lookup.id"), nullable=False
    )
    registered_at = Column(DateTime(timezone=True), nullable=False)
    created_on = Column(DateTime(timezone=True), nullable=False)
    created_by = Column(String, ForeignKey("sch_iam.tb_user.id"), nullable=True)
    updated_by = Column(String, ForeignKey("sch_iam.tb_user.id"), nullable=True)


# TODO: Reference Gap Analysis for tb_crs_outcome. Not generating ORM model as the table does not exist in the database metadata.
