# OneApp m_fees — Functional Specification & Resource Analysis

## 1. Executive Summary
- **Module Purpose**: Manages the end-to-end fee lifecycle for the institution, from structure definition to student assignments, concessions, invoicing, payments, refunds, and late fee penalties.
- **Business Objectives**: Automate and track all fee-related financial transactions; provide clear visibility of dues to students; enforce fee compliance for exams/enrollment.
- **Primary Users**: Finance / Fees Officer, Institution Admin, Student / Parent, Scholarship/Discipline Committee.
- **Business Value**: Centralizes financial tracking, reduces manual reconciliation errors, ensures timely collections via penalties, and integrates tightly with academic progression (exams/enrollment).
- **Module Scope**: `sm_feeStructure`, `sm_feeAssignment`, `sm_concession`, `sm_invoice`, `sm_payment`, `sm_refund`, `sm_penalty`.
- **Out-of-Scope Features**: General accounting ledgers (Chart of Accounts), payroll, purchasing/procurement, and asset management are outside the scope of student fee management.
- **Dependencies**: Relies on `m_aaa` (auth/roles), `m_curriculum` (programmes/batches/enrollment), and `m_exam` (consumers of fee clearance status).
- **Expected Deliverables**: A suite of APIs covering all 7 submodules to support full CRUD operations, state transitions, and integration checks.

## 2. Functional Decomposition
### m_fees
├── **sm_feeStructure**
│   - **Purpose**: Defines master fee templates.
│   - **Responsibilities**: Creates components (tuition, hostel, etc.) with effective dates.
│   - **Boundaries**: Master data only; does not attach to students directly.
│   - **Dependencies**: Depends on institution, programme, academic year.
│   - **Expected Outputs**: Draft/Published fee structures.
├── **sm_feeAssignment**
│   - **Purpose**: Links fee structures to students.
│   - **Responsibilities**: Bulk or individual assignment for a term.
│   - **Boundaries**: Defines gross liability before concessions.
│   - **Dependencies**: Depends on published `sm_feeStructure` and enrolled students.
│   - **Expected Outputs**: Student assignment records linking student to structure.
├── **sm_concession**
│   - **Purpose**: Manages fee reductions (scholarships, waivers, discounts).
│   - **Responsibilities**: Validates eligibility, recalculates net payable, handles renewals.
│   - **Boundaries**: Modifies assignment net liability; triggers invoice regeneration.
│   - **Dependencies**: Depends on existing assignments and committee approvals.
│   - **Expected Outputs**: Concession records and recalculated net payables.
├── **sm_invoice**
│   - **Purpose**: Generates billing documents.
│   - **Responsibilities**: Computes net amount, tracks due dates, manages invoice statuses.
│   - **Boundaries**: Cannot be voided if a payment exists.
│   - **Dependencies**: Depends on assignments and concessions.
│   - **Expected Outputs**: Downloadable invoices, exam dues statuses.
├── **sm_payment**
│   - **Purpose**: Records incoming funds.
│   - **Responsibilities**: Reconciles online/offline payments against invoices, handles bounced payments.
│   - **Boundaries**: Payments reduce invoice balances; full payment clears exam blocks.
│   - **Dependencies**: Depends on invoices and external payment gateways.
│   - **Expected Outputs**: Payment receipts, updated invoice balances, cleared hall-ticket blocks.
├── **sm_refund**
│   - **Purpose**: Manages return of funds.
│   - **Responsibilities**: Processes overpayments, withdrawals, cancellations via approval workflow.
│   - **Boundaries**: Refund cannot exceed actual paid amount.
│   - **Dependencies**: Depends on recorded payments/invoices and Finance approval.
│   - **Expected Outputs**: Pending/Approved/Processed refund records, disbursements.
└── **sm_penalty**
    - **Purpose**: Enforces late fee rules.
    - **Responsibilities**: Configures grace periods and flat/percentage penalties institution-wide.
    - **Boundaries**: Applies prospectively; does not reverse past penalties if removed.
    - **Dependencies**: Depends on overdue unpaid invoices.
    - **Expected Outputs**: Active penalty configuration, automatic penalty accrual on overdue invoices.

## 3. Business Process Analysis

### Feature: Fee Structure Definition
- **Purpose**: Standardize fee charges per programme/year.
- **Actors**: Finance Officer.
- **Preconditions**: Institution, Programme, Academic Year exist.
- **Trigger**: Finance Officer selects 'Create Fee Structure'.
- **Workflow**: Draft created -> Validated -> Published.
- **Business Rules**: `feeStructureCode` must be unique; `effectiveFrom` < `effectiveTo`; amounts must be positive.
- **Post Conditions**: Published structure available for assignment.
- **Failure Scenarios**: Validation failure on overlapping dates or negative amounts.
- **Success Criteria**: Structure selectable by `sm_feeAssignment`.
- **Exceptions**: Deleting a structure with active assignments only deactivates it.
- **Manual/Automated**: Manual creation, automated deactivation check.

### Feature: Fee Assignment (Bulk/Individual)
- **Purpose**: Bind students to fee liabilities.
- **Actors**: Finance Officer.
- **Preconditions**: Published Fee Structure; active students.
- **Trigger**: Officer selects structure and student(s).
- **Workflow**: Select Structure -> Assign (Bulk/Single) -> Assignment Confirmed.
- **Business Rules**: Bulk assignment is a single transaction (all or none); cannot delete if payments exist.
- **Post Conditions**: Assignments created; acts as basis for concessions/invoices.
- **Failure Scenarios**: Validation failure on one student in bulk batch fails entire batch.
- **Success Criteria**: All selected students have fee assignments.
- **Exceptions**: Program change requires reassignment, does not alter old invoices.

### Feature: Payment Collection
- **Purpose**: Record fee realization.
- **Actors**: Student/Parent (online), Finance Officer (offline).
- **Preconditions**: Unpaid/partially paid invoice exists.
- **Trigger**: Student pays via gateway, or hands cash/DD to Officer.
- **Workflow**: Payment Initiated -> Recorded -> Invoice Updated -> Exam Block Cleared (if full).
- **Business Rules**: Payment amount <= outstanding balance.
- **Post Conditions**: Invoice balance updated, payment record generated.
- **Failure Scenarios**: Bounced cheque or failed gateway transaction.
- **Success Criteria**: Receipt generated, invoice balance reduced.
- **Exceptions**: Bounced payments reopen the invoice balance.

*(Detailed workflows for Concession, Invoice, Refund, Penalty follow similar structured patterns based on the source documents.)*

## 4. Workflow Analysis
### Workflow 1: The Core Fee Lifecycle
`Draft Fee Structure` -> `Publish Structure` -> `Assign to Student (Bulk/Single)` -> `Apply Concessions (Optional)` -> `Auto-Generate Invoice` -> `Student Makes Payment` -> `Invoice Status Updated (Fully Paid)` -> `Exam Block Cleared`.

### Workflow 2: Concession & Invoice Regeneration
`Concession Applied (Post-Invoice)` -> `Invoice Flagged for Regeneration` -> `Invoice Manually Re-run` -> `Updated Net Payable Displayed` -> `Payment Collected`.

### Workflow 3: Payment Discrepancy & Reversal
`Offline Payment Recorded` -> `Invoice Balance Reduced` -> `Cheque Bounces` -> `Payment Marked Bounced` -> `Invoice Balance Reopened` -> `Late Penalty Applies if Overdue`.

### Workflow 4: Refund Processing
`Refund Requested (Overpayment/Withdrawal)` -> `Pending Status` -> `Finance Review` -> `On-Hold (Verification)` -> `Approved & Processed` -> `Disbursed to Student`.

## 5. Business Rule Catalogue
- `BR-FEE-01`: `feeStructureCode` must be unique within an institution.
- `BR-FEE-02`: A fee structure is created in 'draft'; only 'published' structures can be assigned.
- `BR-FEE-03`: Updates to a fee structure apply only to new assignments, not retroactive.
- `BR-FEE-04`: Fee structures cannot be hard-deleted if students are assigned; they are deactivated.
- `BR-FEE-05`: Bulk student assignment must be processed as a single atomic transaction.
- `BR-FEE-06`: Fee assignments cannot be deleted if a payment exists against generated invoices.
- `BR-FEE-07`: Applying/withdrawing a concession immediately recalculates the net payable.
- `BR-FEE-08`: Concessions applied post-invoice generation require invoice regeneration.
- `BR-FEE-09`: An invoice is generated from the net assignment amount.
- `BR-FEE-10`: Paid invoices cannot have their due dates extended.
- `BR-FEE-11`: Invoices cannot be voided if any payment is recorded against them.
- `BR-FEE-12`: Payment amounts cannot exceed the invoice's outstanding balance.
- `BR-FEE-13`: Full payment of an invoice clears tied exam/hall-ticket blocks.
- `BR-FEE-14`: Bounced or reversed payments reopen the invoice balance.
- `BR-FEE-15`: Refund requests start in 'pending' status.
- `BR-FEE-16`: Refund amount cannot exceed the actually paid amount on the referenced invoice.
- `BR-FEE-17`: Rejecting a refund requires mandatory remarks.
- `BR-FEE-18`: Only one active late payment penalty configuration can exist per institution.
- `BR-FEE-19`: Late penalties apply only to invoices going overdue after the rule is configured.
- `BR-FEE-20`: Removing a penalty rule stops future accruals but does not reverse past penalties.

## 6. Feature Analysis
### sm_feeStructure
- **Inputs**: `feeStructureCode`, `components[]`, `effectiveFrom`, `effectiveTo`.
- **Outputs**: Published structure.
- **Validations**: `effectiveFrom` < `effectiveTo`, positive component amounts.
- **Permissions**: Finance (Add/View/Update/Delete). System (Read).
- **Audit**: Before/after component values.

### sm_feeAssignment
- **Inputs**: `studentId(s)`, `feeStructureId`, `termId`, `dueDate`.
- **Outputs**: Fee assignment records.
- **Validations**: Structure must be published, single-transaction atomic batch.
- **Permissions**: Finance (Full), Student (View own).

### sm_concession
- **Inputs**: `amountOrPercent`, `reason`, `attachments`.
- **Outputs**: Recalculated net payable.
- **Validations**: Amount valid per type, attachments provided if required.
- **Permissions**: Finance (Full), Student (View own).

### sm_invoice
- **Inputs**: `assignmentId` (auto), `dueDate` (extension).
- **Outputs**: Downloadable PDF invoice.
- **Validations**: Cannot extend paid invoice, cannot void if payment exists.

### sm_payment
- **Inputs**: `invoiceId`, `amount`, `method`, `transactionRef`.
- **Outputs**: Receipt, updated balance.
- **Validations**: Amount <= outstanding balance.

### sm_refund
- **Inputs**: `invoiceId`, `amount`, `reason`.
- **Outputs**: Processed refund.
- **Validations**: Requested amount <= paid amount.

### sm_penalty
- **Inputs**: `gracePeriodDays`, `penaltyType`, `penaltyValue`.
- **Outputs**: Accrued penalties on overdue invoices.
- **Validations**: Only one active rule per institution.

## 7. Cross Module Dependencies
- **m_curriculum**: Reads `m_fees` (published fee structures) to display fee visibility at the time of student enrollment. (Direction: `m_curriculum` -> reads -> `m_fees`).
- **m_exam**: Reads `m_fees` (invoice payment status) to enforce dues checks before hall-ticket generation and result release. (Direction: `m_exam` -> reads -> `m_fees`).
- **m_aaa**: Resolves user roles (Finance Officer, Student, Admin) for authorization, and provides user context for audit logs (`created_by`, `updated_by`).
- **Payment Gateway (External)**: Integrates with `sm_payment` to process online transactions and receive `transactionRef`.

## 8. API Readiness
All modules use the standard OneApp routing payload: `{ "mod", "subMod", "action", "actionType", "payload" }`.

- `sm_feeStructure` (action: `feeStructure`): add, view, update, delete.
- `sm_feeAssignment` (action: `studentFeeAssignment`): add, view, update, delete.
- `sm_concession` (action: `feeConcession`): add, view, update, delete.
- `sm_invoice` (action: `feeInvoice`): add, view, update, delete.
- `sm_payment` (action: `feePayment`): add, view, update, delete.
- `sm_refund` (action: `feeRefund`): add, view, update, delete.
- `sm_penalty` (action: `latePaymentPenalty`): add, view, update, delete.

*Authorization*: Strictly role-scoped. Students have `view` access isolated to their own IDs for assignments, invoices, payments, refunds.

## 9. Data Ownership
- **Finance Officer (sm_feeStructure)** owns the Master Fee Configurations.
- **Finance Officer (sm_feeAssignment)** owns the Liability Generation.
- **Scholarship Committee / Finance (sm_concession)** owns Discounts and Waivers.
- **System / Finance (sm_invoice)** owns Billing Documents.
- **Student / Finance (sm_payment)** owns the Realization of Funds.
- **Finance (sm_refund)** owns the Disbursement of Returns.
- **Institution Admin / Finance (sm_penalty)** owns the Late Fee Policy.

## 10. State Machines
- **Fee Structure**: `Draft` -> `Published` -> `Deactivated` (Soft deleted).
- **Invoice**: `Unpaid` -> `Partially Paid` -> `Fully Paid` (or `Void`).
- **Payment**: `Initiated` -> `Success` / `Failed` -> (if off-line exception) -> `Bounced` / `Disputed` -> `Reconciled` / `Reversed`.
- **Refund**: `Pending` -> `On-Hold` -> `Approved` -> `Processed` (or `Rejected`).

## 11. Roles & Permissions
- **Finance / Fees Officer**: Full CRUD on structure, assignment, concession, invoice, payment, refund queue, and penalty config. Responsible for offline collections and reconciliations.
- **Institution Admin**: Oversight capabilities, primarily viewing reports, managing penalty policies, and overriding deactivations.
- **Student / Parent**: Read-only access to their own assignments, concessions, invoices, and payments. Can request refunds and initiate online payments.
- **System**: Background actor that auto-generates invoices on assignment, applies penalties, and clears exam blocks.

## 12. Reports & Documents
- **Invoices (PDF)**: Generated via `sm_invoice`; auto-created on assignment; downloaded by students.
- **Receipts (PDF)**: Generated via `sm_payment` on successful transaction realization.
- **Outstanding Reports (Excel/PDF)**: Consumed by Finance to track unpaid invoices globally.
- **Concession Letters (PDF)**: Supported via attachments in `sm_concession`.
- **Collection Reports**: Derived from `sm_payment` history for daily reconciliation.

## 13. Notification Analysis
- **Invoice Generated**: Sent to Student/Parent; Channel: Email/App Push; Trigger: Invoice created/regenerated.
- **Payment Successful**: Sent to Student/Parent; Channel: Email/SMS; Trigger: Payment reconciled/gateway success.
- **Payment Bounced/Disputed**: Sent to Student/Parent; Channel: Email/SMS/Urgent Push; Priority: High.
- **Refund Approved/Processed**: Sent to Student; Channel: Email.
- **Penalty Applied**: Sent to Student; Trigger: Grace period expires.
- **Exam Block Cleared**: Sent to Student; Trigger: Invoice becomes 'Fully Paid'.

## 14. Audit Requirements
- Every `add`, `update`, `delete` action across all submodules logs the Actor, Timestamp, and Session/IP.
- **sm_feeStructure**: Before/after component values and effective dates.
- **sm_feeAssignment**: Bulk assignment batch results logged atomically (success/fail per student).
- **sm_concession**: Net-payable recalculation trail with reason codes.
- **sm_payment**: Status transition history (Reconciled/Bounced) and reversal reasons.
- **sm_refund**: Approval/Rejection remarks strictly required.

## 15. Edge Cases
- **Bulk Assignment Partial Failure**: Mitigated by atomic transaction requirement (all or nothing).
- **Concession post-Invoice**: Invoice must be flagged for regeneration.
- **Bounced Cheques**: Re-opens the invoice balance and may retroactively trigger late fees if past grace period.
- **Duplicate Online Payments**: Prevented by validating `amount <= outstanding balance` and idempotency via `transactionRef`.
- **Over-Refunds**: Prevented by validating `refund amount <= actually paid amount`.
- **Program Change**: Handled via `feeAssignment/update` (reassignment) without altering historic finalized invoices.

## 16. Implementation Readiness
- **Business Complexity**: High. The interplay between assignments, concessions, and invoice balances requires strict transactional integrity.
- **Technical Complexity**: High. Double-entry ledger logic and pessimistic locking (e.g., `SELECT FOR UPDATE` on balances) will be required.
- **Dependencies**: `m_aaa` (User auth) and `m_curriculum` (Student/Term context) must be mockable or present.
- **Suggested Development Order**: 
  1. `sm_feeStructure` (Master Data)
  2. `sm_penalty` (Global Rules)
  3. `sm_feeAssignment` (Linkage)
  4. `sm_concession` (Modification)
  5. `sm_invoice` (Billing)
  6. `sm_payment` (Collection)
  7. `sm_refund` (Reversal)
- **Risk Level**: Critical. Financial transactions dictate zero-tolerance for race conditions or floating-point errors (must use `Decimal`/`Numeric` types).

## 17. Architecture Compliance Review
- **OneApp COE Compliance**: Fully compliant with the single-entry `POST /` gateway API standard and the `{ mod, subMod, action, actionType, payload }` schema.
- **State Machine Compliance**: Uses strictly defined transitions without skipping mandatory approvals.
- **Ambiguities / Clarifications Needed**: The documents do not specify exactly *how* the payment gateway webhook callbacks will be authenticated (assumed standard JWT/API Key in `m_aaa`).
- **Implementation Risks**: The requirement for bulk assignment to be a "single atomic transaction" across an entire batch (potentially hundreds of students) could cause database lock contention or timeout issues if not optimized properly in the backend.

## 18. Recommendations
1. **Implementation Sequence**: Follow the exact topological dependency graph -> Structure -> Assignment -> Concession -> Invoice -> Payment -> Refund.
2. **Database Types**: *Strictly* enforce `Numeric(10,2)` for all monetary fields in the backend ORM/schemas. Never use floating-point types.
3. **Concurrency Control**: Use Pessimistic Locking (`with_for_update()`) in the backend during `sm_payment` processing to prevent concurrent double-payments against the same invoice balance.
4. **Idempotency Keys**: For `sm_payment`, implement an idempotency layer keyed by `transactionRef` to safely handle webhook retries from the payment gateway.
5. **Shared Utilities**: Develop a `NetPayableCalculator` service shared by `sm_feeAssignment`, `sm_concession`, and `sm_invoice` to ensure identical math logic is used universally.
6. **Future Enhancement**: Add a `sm_wallet` submodule for students to store overpayments as account credits instead of processing physical refunds.
