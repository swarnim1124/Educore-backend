"""
File: manifest.py
Description: Module Manifest for m_super_admin.

Author: EduCore
App: OneApp
"""

MODULE_NAME = "m_super_admin"
MODULE_VERSION = "2.0.0"
AUTHOR = "Framework Architect"
DESCRIPTION = "Super Admin Core Management Module."

DEPENDENCIES = ["m_AAA"]

SUPPORTED_SUBMODULES = [
    "sm_action",
    "sm_action_type",
    "sm_config",
    "sm_mdm_edu",
    "sm_mods",
    "sm_sub_mods",
]

DATABASE_SCHEMAS = ["sch_super_admin"]

PERMISSIONS = [
    "super_admin.action.manage",
    "super_admin.actionType.manage",
    "super_admin.config.manage",
    "super_admin.mdm.manage",
    "super_admin.mods.manage",
    "super_admin.sub_mods.manage",
]

FEATURE_FLAGS = {}
