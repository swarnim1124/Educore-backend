"""
File: manifest.py
Description: Module Manifest for m_attendance (OneApp Attendance Module).
Defines module metadata, supported submodules, exported schemas, dependencies, and RBAC permissions.

Author: Siddharth Amdal
App: OneApp

"""

MODULE_NAME = "m_attendance"
MODULE_VERSION = "1.0.0"
AUTHOR = "Siddharth Amdal"
DESCRIPTION = "Attendance Management Module for OneApp."

DEPENDENCIES = ["m_AAA", "m_organization", "m_lookup", "m_student", "m_curriculum"]

SUPPORTED_SUBMODULES = [
    "sm_configuration",
    "sm_records",
    "sm_shortage",
    "sm_exception",
    "sm_leave",
]

DATABASE_SCHEMAS = ["sch_attendance", "sch_lookup", "sch_curriculum", "sch_student"]

PERMISSIONS = [
    "ATTENDANCE_CONFIG_MANAGE",
    "ATTENDANCE_SESSION_MANAGE",
    "ATTENDANCE_RECORD_MARK",
    "ATTENDANCE_SUBMISSION_MANAGE",
    "ATTENDANCE_SHORTAGE_VIEW",
    "ATTENDANCE_CONDONATION_MANAGE",
    "ATTENDANCE_EXCEPTION_MANAGE",
]

FEATURE_FLAGS = {"DYNAMIC_ROSTER_VALIDATION": True, "RETROACTIVE_REVOCATION": True}
