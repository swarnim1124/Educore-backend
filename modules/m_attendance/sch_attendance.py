"""
File: sch_attendance.py
Description: Schema registration and ORM export list for the OneApp Attendance Module (`m_attendance`).
Follows lightweight OneApp framework standards without embedding business logic.

Author: Siddharth Amdal
App: OneApp

"""

from .db_init import (
    TbAttPolicy,
    TbAttSession,
    TbAttRecord,
    TbAttCorrection,
    TbStudentLeave,
)

# List of all declarative ORM models in the attendance module
ATTENDANCE_MODELS = [
    TbAttPolicy,
    TbAttSession,
    TbAttRecord,
    TbAttCorrection,
    TbStudentLeave,
]

# ORM Registry mapping physical database table names to SQLAlchemy declarative classes
ORM_REGISTRY = {
    "tb_att_policy": TbAttPolicy,
    "tb_att_session": TbAttSession,
    "tb_att_record": TbAttRecord,
    "tb_att_correction": TbAttCorrection,
    "tb_student_leave": TbStudentLeave,
}

# Explicit module export list
__all__ = [
    "TbAttPolicy",
    "TbAttSession",
    "TbAttRecord",
    "TbAttCorrection",
    "TbStudentLeave",
    "ATTENDANCE_MODELS",
    "ORM_REGISTRY",
]
