# OneApp m_fees — Phase 2 Refined Implementation Plan

This document outlines the final, refined Phase 2 implementation strategy for the `m_fees` Data Access Layer (DAL) inside `m_fees_data.py`. The plan strictly aligns with the OneApp `*Data` naming convention and completely avoids mapping non-persistent entities (like Invoices) at the repository layer.

## Goal
Implement a production-ready, business-agnostic persistence layer mapped to physical ORM entities, exposing standard repository methods (`create`, `get`, `update`) rather than SQL operations (`insert`). 

## User Review Required

> [!IMPORTANT]
> **Removal of Invoice Data Class**
> The previously proposed `FeeInvoiceDAL` has been completely eliminated because there is no persistent `TbInvoice` entity. The aggregate queries supporting logical invoice generation have been safely relocated to `FeeLedgerData` and `FeeAssignmentData`.

> [!CAUTION]
> **Repository Naming Standard**
> All classes have been renamed from `*DAL` to `*Data` (e.g., `FeeStructureData`), and all methods have been renamed from SQL terminology (`insert_`) to repository terminology (`create_`).

## Proposed Changes

### [MODIFY] [m_fees_data.py](/modules/m_fees/m_fees_data.py)

The DAL will be organized into 7 `*Data` classes mapped to the approved submodules and their corresponding ORM entities.

#### 1. `FeeStructureData`
Supports `sm_feeStructure`
- **Responsibility**: Persists master fee configuration (`TbFeeStructure`, `TbFeeStructureComponent`, etc.).
- **Derived Methods**: 
  - `create_fee_structure(session, data)`
  - `get_fee_structures(session, filters, limit, offset)`
  - `update_fee_structure(session, id, data)`
  - `delete_fee_structure(session, id)`

#### 2. `FeeAssignmentData`
Supports `sm_feeAssignment`
- **Responsibility**: Persists student fee liabilities and bulk assignments (`TbStudFeeAsmt`, `TbStudFeeComponent`).
- **Derived Methods**: 
  - `create_bulk_assessments(session, assessment_list)`
  - `get_student_assessments(session, student_id)`
  - `get_active_assessments_with_components(session, student_id)` (Relocated from Invoice)
  - `update_assessment(session, id, data)`

#### 3. `FeeConcessionData`
Supports `sm_concession`
- **Responsibility**: Persists the outcome of scholarship and waiver decisions (`TbScholarship`, `TbConcession`).
- **Derived Methods**: 
  - `create_concession(session, data)`
  - `create_scholarship(session, data)`
  - `get_student_concessions(session, student_id)`
  - `update_concession(session, id, data)`

#### 4. `FeeLedgerData`
Supports multiple submodules (Financial Ledger Persistence)
- **Responsibility**: Persists all double-entry financial debits and credits (`TbFinancialLedger`).
- **Derived Methods**: 
  - `create_ledger_entries(session, entry_list)`
  - `get_ledger_aggregates_by_student(session, student_id)` (Relocated from Invoice; returns raw sum of debits/credits)
  - `lock_and_get_ledger_row(session, ledger_id)` (Provides concurrency safety for allocations)

#### 5. `FeePaymentData`
Supports `sm_payment`
- **Responsibility**: Persists payments, gateway logs, and allocations (`TbPayment`, `TbPaymentAllocation`).
- **Derived Methods**: 
  - `create_payment(session, data)`
  - `create_gateway_transaction(session, data)`
  - `create_payment_allocations(session, allocation_list)`
  - `get_payment_history(session, filters)`

#### 6. `FeeRefundData`
Supports `sm_refund`
- **Responsibility**: Persists refund requests and statuses (`TbRefund`).
- **Derived Methods**: 
  - `create_refund(session, data)`
  - `get_refunds(session, filters)`
  - `update_refund(session, id, data)`

#### 7. `FeePenaltyData`
Supports `sm_penalty`
- **Responsibility**: Persists administrative late penalties and system holds (`TbPenalty`, `TbFinancialHold`).
- **Derived Methods**: 
  - `create_penalty(session, data)`
  - `create_financial_hold(session, data)`
  - `get_penalties(session, filters)`
  - `update_financial_hold(session, id, data)`

## Verification Plan

### Automated Checks
- Validated against OneApp standard: Naming strictly follows `[Entity]Data`.
- Validated against ORM: No repository exists without a corresponding `Tb*` entity.
- The file will strictly type-check against SQLAlchemy 2.0 (using async APIs).
- No business rules (allocation decisions, calculations) will exist in `m_fees_data.py`.
