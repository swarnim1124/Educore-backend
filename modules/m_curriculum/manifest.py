"""
File: manifest.py
Description: Module Manifest for m_curriculum.

Author: Siddharth Amdal
App: OneApp

"""

MODULE_NAME = "m_curriculum"
MODULE_VERSION = "1.0.0"
AUTHOR = "Framework Architect"
DESCRIPTION = "Curriculum Management Module."

DEPENDENCIES = ["m_AAA", "m_organization", "m_lookup", "m_student", "m_course_delivery"]

SUPPORTED_SUBMODULES = ["sm_programme", "sm_course", "sm_curriculum", "sm_enrollment"]

DATABASE_SCHEMAS = ["sch_academic_struct", "sch_student", "sch_course_delivery"]

# TODO: Define permissions based on AAA Permission Matrix (Gap Analysis Reference)
PERMISSIONS = []

FEATURE_FLAGS = {}
