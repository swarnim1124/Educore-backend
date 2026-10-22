"""
File: manifest.py
Description: Module Manifest for m_AAA.

Author: Siddharth Amdal
App: OneApp

"""

MODULE_NAME = "m_AAA"
MODULE_VERSION = "2.0.0"
AUTHOR = "Framework Architect"
DESCRIPTION = "Authentication, Authorization & Auditing (Gold Standard)."

DEPENDENCIES = []

SUPPORTED_SUBMODULES = ["sm_auth", "sm_rbac", "sm_policy", "sm_mfa"]

DATABASE_SCHEMAS = ["sch_aaa"]

PERMISSIONS = [
    "aaa.session.view.sel",
    "aaa.session.view.any",
    "aaa.session.delete.sel",
    "aaa.session.delete.any",
    "aaa.mfa.manage.sel",
    "aaa.mfa.manage.any",
    "aaa.password.manage.sel",
    "aaa.password.manage.any",
    "aaa.password.expire",
    "aaa.passwordReset.initiate",
    "aaa.passwordReset.cancel.any",
    "aaa.role.manage",
    "aaa.role.view",
    "aaa.roleAssignment.manage",
    "aaa.roleAssignment.view",
    "aaa.permission.manage",
    "aaa.policy.password.manage",
    "aaa.policy.session.manage",
    "aaa.policy.login.manage",
]

FEATURE_FLAGS = {}
