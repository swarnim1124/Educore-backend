# m_fees - 02 Architecture Review

**Module Name**: m_fees
**Phase**: Phase_3
**Version**: 1.0.0
**Date**: 2026-07-28
**Author**: Siddharth Amdal
**Status**: Approved

## Related Documents
- None

---

## Overview

# OneApp m_fees Module
## Phase 3 Business Layer Analysis Report

---

## 1. Executive Summary
The Phase 3 Business Logic Layer is the orchestrator of the `m_fees` module. Its core responsibility is to translate raw API payloads into validated, transactional financial outcomes utilizing the established Phase 2 Data Access Layer. This analysis synthesizes all approved functional specifications to define the exact boundaries, validations, workflows, and transaction strategies required for Phase 3 implementation. This layer owns all business decision-making and acts as the strict intermediary between the Dispatcher and the Persistence layer, operating entirely within the standard OneApp `ExecutionContext`.

---

## 2. Business Responsibilities
The Phase 3 Business Layer is strictly responsible for:
- **Validation**: Executing complex cross-domain checks (e.g., ensuring payment amounts do not exceed logical outstanding balances).
- **Business Rules Enforcement**: Applying institutional policies (e.g., prohibiting extension of due dates on paid fee statements).
- **Workflow Orchestration**: Coordinating multi-step processes (e.g., calculating net payables after assigning a concession).
- **Transaction Ownership**: Managing `session.commit()` and `session.rollback()` to guarantee atomicity, particularly during bulk assignments or double-entry ledger posting.
- **Cross-Submodule Coordination**: Resolving internal module dependencies (e.g., retrieving active fee structures before generating assignments).
- **Integration**: Bridging the gap between standard OneApp shared libraries (Payment Gateway Manager, Auth) and the fees logic.

---

## 3. Workflow Analysis

### Workflow 1: Fee Structure Publication
- **Trigger**: Finance Officer updates structure status to 'Published'.
- **Inputs**: `feeStructureId`, new status.
- **Validation**: Must have effective dates (`effectiveFrom` < `effectiveTo`), positive amounts.
- **Business Rules**: Draft structures become selectable for assignment only after publication.
- **Repository Interactions**: `FeeStructureData.update_fee_structure()`.
- **Outputs**: Published structure state.

### Workflow 2: Bulk Fee Assignment
- **Trigger**: Finance Officer assigns a fee structure to a batch of students.
- **Inputs**: `studentIds[]`, `feeStructureId`, `termId`, `dueDate`.
- **Validation**: Structure must be published; students must be active.
- **Business Rules**: Processed as a single atomic transaction (all or none).
- **Repository Interactions**: `FeeStructureData.get_fee_structure_components()`, `FeeAssignmentData.create_bulk_assessments()`, `FeeLedgerData.create_ledger_entries()`.
- **Outputs**: Bulk assignment records and logical ledger debits.

### Workflow 3: Concession Application
- **Trigger**: Scholarship Committee applies a discount/waiver.
- **Inputs**: `studentId`, `amountOrPercent`, `reason`.
- **Validation**: Valid amount; mandatory attachments if policy requires.
- **Business Rules**: Immediately triggers recalculation of the student's net payable and regenerates logical outstanding summaries.
- **Repository Interactions**: `FeeConcessionData.create_concession()`, `FeeLedgerData.create_ledger_entries()` (for credit adjustment).
- **Outputs**: Active concession and adjusted net liability.

### Workflow 4: Payment Collection & Ledger Posting
- **Trigger**: Online payment success webhook OR offline payment entry.
- **Inputs**: `studentId`, `amount`, `transactionRef`, `method`.
- **Validation**: `amount` $\le$ total outstanding balance.
- **Business Rules**: Double-entry ledger must balance. Overpayments prevented.
- **Repository Interactions**: `FeePaymentData.create_gateway_transaction()`, `FeeLedgerData.lock_and_get_ledger_row()`, `FeePaymentData.create_payment()`, `FeeLedgerData.create_ledger_entries()`.
- **External Integrations**: `xsc_lib_app` (Payment Gateway Manager).
- **Outputs**: Payment receipt, updated ledger balance, cleared exam blocks.

### Workflow 5: Refund Processing
- **Trigger**: Finance approves a pending refund request.
- **Inputs**: `refundId`, `amount`, `reason`.
- **Validation**: Requested refund $\le$ actually paid amount. Mandatory remarks if rejected.
- **Business Rules**: Requires Finance workflow approval.
- **Repository Interactions**: `FeeRefundData.update_refund()`, `FeeLedgerData.create_ledger_entries()` (debit adjustment).
- **Outputs**: Processed refund, adjusted ledger.

---

## 4. Submodule Analysis

- **`sm_feeStructure`**: Owns Master Templates. Responsible for enforcing positive amounts and non-overlapping effective dates. Orchestrates draft-to-published state transitions.
- **`sm_feeAssignment`**: Owns Liabilities. Responsible for bulk execution. Generates the initial ledger debits based on the chosen fee structure.
- **`sm_concession`**: Owns Reductions. Responsible for calculating discount impacts and pushing credit adjustments to the ledger.
- **`sm_invoice`**: Owns Logical Billing Views. Responsible for aggregating ledger debits and credits via `FeeLedgerData` to present the Dynamic Fee Summary to the user. Does not create persistent invoice objects.
- **`sm_payment`**: Owns Collections. Responsible for strict validations (no overpayments), interacting with the payment gateway, and securely locking the ledger to post double-entry credits.
- **`sm_refund`**: Owns Returns. Responsible for ensuring refunds never exceed historical payments and enforcing the approval state machine.
- **`sm_penalty`**: Owns Late Fees. Responsible for prospectively calculating late fees on overdue balances.

---

## 5. Action Analysis

The following Actions (derived from Phase 1 `manifest.py`) require Business Layer orchestration:
- `feeStructure` (Add/Update): Validates dates and amounts.
- `feeAssignment` (Add): Orchestrates the massive bulk assignment transaction.
- `feeConcession` (Add): Calculates percentage math and updates ledger.
- `feeInvoice` (View): Dynamically aggregates ledger data to build the Outstanding Summary.
- `feePayment` (Add): Executes gateway validation, locks the ledger, and inserts payment + allocation records.
- `feeRefund` (Update): Executes the state transition (e.g., Pending -> Approved).
- `feePenalty` (Add): Enforces the "one active rule per institution" constraint.

---

## 6. Validation Rules (Organized by Submodule)

### `sm_feeStructure`
- `BR-FEE-01`: `feeStructureCode` must be unique (enforced by DB, handled gracefully by BL).
- `BR-FEE-02`: Only 'published' structures can be assigned.

### `sm_feeAssignment`
- `BR-FEE-05`: Bulk student assignment must be processed as a single atomic transaction.
- `BR-FEE-06`: Fee assignments cannot be deleted if a payment exists.

### `sm_invoice` (Logical Billing View)
- `BR-FEE-10`: Fully paid fee statements cannot have their due dates extended.

### `sm_payment`
- `BR-FEE-12`: Payment amounts cannot exceed the outstanding ledger balance.

### `sm_refund`
- `BR-FEE-16`: Refund amount cannot exceed the actually paid amount.
- `BR-FEE-17`: Rejecting a refund requires mandatory remarks.

### `sm_penalty`
- `BR-FEE-18`: Only one active late payment penalty configuration can exist per institution.

---

## 7. Execution Context & Transaction Strategy

### ExecutionContext
Every Business Layer operation executes within the standard OneApp `ExecutionContext`. The Business Layer functions operate exclusively using:
- **`ExecutionContext`**: Provides authenticated identity, institution context, authorization context, structured logging context, and correlation identifiers.
- **`Request Object`**: The validated Pydantic model (`sch_fees.py`) containing the payload.
- **`AsyncSession`**: The database session used for transaction orchestration.
The Business Layer remains entirely independent of HTTP lifecycle concepts.

### Transaction Boundaries
- **External Session Injection**: Handlers receive an `AsyncSession` from the Dispatcher.
- **Bulk Assignment (Atomic)**: The `feeAssignment` Add action wraps the entire iteration of `studentIds` in a single uncommitted transaction block. If one student fails validation, `session.rollback()` is executed, failing the entire batch.
- **Payment Concurrency (Pessimistic Lock)**: The `feePayment` Add action utilizes `FeeLedgerData.lock_and_get_ledger_row()` to block concurrent requests from reading a student's balance until the current payment is committed, preventing double-payment race conditions.

---

## 8. External Dependencies

### Mandatory
- **`m_aaa`**: Resolves user roles (Finance Officer vs. Student) to enforce authorization and injects context into the `ExecutionContext`.
- **`Logging`**: Structured persistence logging tied to `ExecutionContext`.
- **`ExecutionContext`**: Core runtime wrapper across all submodules.

### Conditional
- **`m_curriculum`**: Required only during `sm_feeAssignment` (to check student enrollment status).
- **`xsc_lib_app` (Payment Gateway Manager)**: Required only during `sm_payment` (to validate webhook callbacks and resolve `transactionRef`).
- **`Notification Service`**: Required only for outbound communication (e.g., successful payment receipt delivery).

---

## 9. Repository Usage

- **`FeeStructureData`**: Consumed by `sm_feeStructure` and read by `sm_feeAssignment` to build liabilities.
- **`FeeAssignmentData`**: Consumed by `sm_feeAssignment`.
- **`FeeConcessionData`**: Consumed by `sm_concession`.
- **`FeeLedgerData`**: Consumed heavily by `sm_feeAssignment` (debits), `sm_payment` (credits), `sm_concession` (credits), and `sm_invoice` (reads).
- **`FeePaymentData`**: Consumed by `sm_payment`.
- **`FeeRefundData`**: Consumed by `sm_refund`.
- **`FeePenaltyData`**: Consumed by `sm_penalty`.

---

## 10. Proposed Business Layer Organization

The Business Layer will strictly follow the established OneApp architecture pattern, maintaining business orchestration directly inside the approved Submodule implementation files. No artificial handler or service layers will be introduced.

The execution flow: `Dispatcher` → `Submodule` → `Action` → `ActionType` → `Business Logic` → `Data Layer`

Files to be implemented:
- `m_fees_sm_feeStructure.py`
- `m_fees_sm_feeAssignment.py`
- `m_fees_sm_concession.py`
- `m_fees_sm_invoice.py`
- `m_fees_sm_payment.py`
- `m_fees_sm_refund.py`
- `m_fees_sm_penalty.py`

Each submodule will natively own its orchestration and selectively consume the required classes from `m_fees_data.py`.

---

## 11. Risks & Open Questions

- **Missing Business Rules**: The penalty calculation frequency is not strictly defined (daily accrual vs. flat fee application).
- **Undefined Workflows**: The exact mechanism for handling "Bounced Cheques" (reversal workflow) is mentioned but lacks step-by-step documentation.
- **Dependencies Requiring Clarification**: Does `xsc_lib_app` expose asynchronous methods for gateway verification, or will the Business Layer need to execute blocking synchronous calls via `run_in_executor`?

---

## 12. Phase 3 Readiness Assessment

The `m_fees` module architecture and Phase 2 implementation provide a fully sufficient foundation for Phase 3. The separation of concerns is clear, the transaction strategy natively leverages `ExecutionContext`, and the validation rules are explicitly mapped to their owning submodules.

**Conclusion**: The project is formally ready to commence Phase 3 (Business Logic Layer) implementation, maintaining strict adherence to the OneApp Architecture Freeze.



---
**Previous**: [../Phase_3/01_Implementation.md](../Phase_3/01_Implementation.md)
**Next**: [../Phase_3/03_Refinement.md](../Phase_3/03_Refinement.md)
