"""
File: manifest.py
Description: Module Manifest for m_profile.

Author: EduCore
App: OneApp

"""

MODULE_NAME = "m_profile"
MODULE_VERSION = "1.0.0"
AUTHOR = "EduCore"
DESCRIPTION = "Cross-cutting Profile module — personal details, academic identifiers, family/emergency contacts, medical records, and user preferences."

DEPENDENCIES = ["m_AAA"]

SUPPORTED_SUBMODULES = [
    "sm_personal_detail",
    "sm_academic_detail",
    "sm_family_detail",
    "sm_medical_detail",
    "sm_settings",
]

DATABASE_SCHEMAS = [
    "sch_iam",
    "sch_core",
    "sch_student",
    "sch_emp_fac",
    "sch_parents",
    "sch_medical",
]

PERMISSIONS = [
    # Personal Detail
    "profile.personalDetail.add",
    "profile.personalDetail.view.sel",
    "profile.personalDetail.view.dept",
    "profile.personalDetail.view.all",
    "profile.personalDetail.update.sel",
    "profile.personalDetail.update.any",
    "profile.personalDetail.delete",
    "profile.personalDetail.approve",
    # Academic Detail
    "profile.academicDetail.add",
    "profile.academicDetail.view.sel",
    "profile.academicDetail.view.all",
    "profile.academicDetail.update",
    "profile.academicDetail.delete",
    # Family Detail
    "profile.familyDetail.add",
    "profile.familyDetail.view.sel",
    "profile.familyDetail.view.all",
    "profile.familyDetail.update",
    "profile.familyDetail.delete",
    # Emergency Contact
    "profile.emergencyContact.add",
    "profile.emergencyContact.view.sel",
    "profile.emergencyContact.view.all",
    "profile.emergencyContact.update",
    "profile.emergencyContact.delete",
    # Medical Detail
    "profile.medicalDetail.add",
    "profile.medicalDetail.view.sel",
    "profile.medicalDetail.view.medical",
    "profile.medicalDetail.update",
    "profile.medicalDetail.delete",
    # User Preference
    "profile.userPreference.add",
    "profile.userPreference.view.sel",
    "profile.userPreference.update.sel",
    "profile.userPreference.delete.self",
]

FEATURE_FLAGS = {}
