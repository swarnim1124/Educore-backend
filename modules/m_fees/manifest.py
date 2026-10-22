"""
File: manifest.py
Description: Module Manifest for m_fees (OneApp Fees Module).
Defines module metadata, supported submodules, exported schemas, dependencies, and RBAC permissions.

Author: Siddharth Amdal
App: OneApp

"""

# ==============================================================================
# 1. Module Metadata
# ==============================================================================
MODULE_NAME = "m_fees"
MODULE_VERSION = "1.0.0"
AUTHOR = "Siddharth Amdal"
DESCRIPTION = "Comprehensive Fees Lifecycle Management Module for OneApp."

# ==============================================================================
# 2. Dependencies
# ==============================================================================
# Modules required to be initialized prior to m_fees
DEPENDENCIES = [
    "m_aaa",  # Authentication and RBAC
    "m_student",  # Student Enrollment Core
    "m_curriculum",  # Academic Terms and Programmes
    "m_organization",  # Institution configuration
    "m_lookup",  # Core enumerations
    "m_core",  # Shared utilities
]

DATABASE_SCHEMAS = ["sch_fees"]

# ==============================================================================
# 3. Submodules & API Contract
# ==============================================================================
SUPPORTED_SUBMODULES = [
    "sm_fee_structure",  # Master fee components and rules
    "sm_fee_assignment",  # Student fee assessment and enrollment mapping
    "sm_concession",  # Scholarships, waivers, and discounts
    "sm_invoice",  # Logical bill generation
    "sm_payment",  # Payment processing and allocation
    "sm_refund",  # Overpayment and cancellation returns
    "sm_penalty",  # Late fee configuration and enforcement
]

SUPPORTED_ACTIONS = [
    "feeStructure",
    "feeAssignment",  # Standardized from studentFeeAssignment
    "feeConcession",
    "feeInvoice",
    "feePayment",
    "feeRefund",
    "feePenalty",  # Standardized from latePaymentPenalty
]

SUPPORTED_ACTION_TYPES = ["add", "view", "update", "delete"]

# ==============================================================================
# 4. Permissions (RBAC)
# ==============================================================================
# Format: <MODULE>_<FEATURE>_<ACCESS>
PERMISSIONS = [
    "FEES_STRUCTURE_MANAGE",
    "FEES_ASSIGNMENT_MANAGE",
    "FEES_CONCESSION_MANAGE",
    "FEES_INVOICE_MANAGE",
    "FEES_PAYMENT_MANAGE",
    "FEES_REFUND_MANAGE",
    "FEES_PENALTY_MANAGE",
    "FEES_REPORTS_VIEW",
    "FEES_STUDENT_VIEW",
]

# ==============================================================================
# 5. Configuration Flags
# ==============================================================================
FEATURE_FLAGS = {"REQUIRE_FINANCE_APPROVAL_REFUNDS": True, "AUTO_PENALTY_ACCRUAL": True}
