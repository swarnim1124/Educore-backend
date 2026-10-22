# OneApp m_fees — Enterprise Database Deep-Dive & Backend Readiness Analysis

## 1. Executive Summary
This report provides a comprehensive architectural analysis of the LIVE PostgreSQL database for the `m_fees` module. The database follows a highly normalized, rule-engine-driven design. The architecture robustly supports complex pricing models, installment plans, multidimensional concessions, and a double-entry-like financial ledger system. 

Crucially, **there are no database-level triggers** handling business logic. All financial calculations, running balances, sequence generations (e.g., receipt numbers), and status transitions must be orchestrated entirely by the backend application logic.

## 2. Schema Discovery
The fee domain is encapsulated purely within the **`sch_fees`** schema. There are no supplementary `sch_finance` or `sch_payment` schemas.
`sch_fees` relies heavily on cross-schema relationships:
- `sch_lookup`: Extensive use for all enumerations, statuses, types, and categories.
- `sch_student`: The anchor point for all fee assessments and ledger transactions (`tb_stud_enrollment`).
- `sch_org`: Institutional anchoring for fee structures and installment plans.
- `sch_academic_struct`: Contextual applicability of rules (Prog, Batch, Term).
- `sch_core`: Document integration via `tb_dms` (e.g., scholarship approvals, receipts).
- `sch_iam`: Global audit trail tracking (`tb_user`).

## 3. Table Inventory
| Schema | Table Name | Business Purpose |
| :--- | :--- | :--- |
| `sch_fees` | `tb_fee_structure` | Master template for fees applicable to a group. |
| `sch_fees` | `tb_fee_structure_rule` | The applicability matrix (Prog, Batch, Category) for a structure. |
| `sch_fees` | `tb_fee_structure_component` | Line items comprising a fee structure (Tuition, Transport). |
| `sch_fees` | `tb_installment_plan` | Master configuration for payment schedules. |
| `sch_fees` | `tb_installment_plan_detail` | Specific installment intervals and amounts/percentages. |
| `sch_fees` | `tb_stud_fee_asmt` | The instantiation of a fee structure for a specific student ("Invoice Header"). |
| `sch_fees` | `tb_stud_fee_component` | Snapshot of the line items assessed to the student ("Invoice Lines"). |
| `sch_fees` | `tb_stud_installment` | Snapshot of the specific due dates and amounts for the student. |
| `sch_fees` | `tb_financial_ledger` | Central transactional ledger tracking debits, credits, and running balance. |
| `sch_fees` | `tb_payment` | High-level payment record (Cash, Cheque, Gateway). |
| `sch_fees` | `tb_payment_allocation` | Settles a `tb_payment` against specific `tb_financial_ledger` entries. |
| `sch_fees` | `tb_payment_gateway_transaction` | Technical logs mapping to external payment gateways (e.g. Razorpay). |
| `sch_fees` | `tb_scholarship` | Specific scholarship grants with approval workflows. |
| `sch_fees` | `tb_concession` | Specific fee concessions with approval workflows. |
| `sch_fees` | `tb_fee_waiver` | Specific fee waivers with approval workflows. |
| `sch_fees` | `tb_penalty` | Fines or late fees levied against a student. |
| `sch_fees` | `tb_refund` | Approved refunds mapped to original payments. |
| `sch_fees` | `tb_financial_hold` | System blocks preventing student progression due to unpaid dues. |

## 4. Column Classification
Across all tables, the schema adheres to a strict standard:
- **Audit Columns**: `created_by`, `created_on`, `updated_by`, `updated_on`
- **Soft Delete**: `is_active` (boolean)
- **Status Columns**: `status_id` (used for lifecycle: Draft/Active/Archived), `approval_status_id`, `payment_status_id`
- **Lookup Columns**: `fee_category_id`, `payment_method_id`, `scholarship_type_id`, `penalty_type_id`
- **Business Columns**: `amount`, `percentage`, `running_balance`, `receipt_number`, `due_date`
- **Versioning Columns**: `effective_from`, `effective_to`

All `amount`, `debit_amount`, `credit_amount`, and `running_balance` columns use `numeric(12,2)`.

## 5. Relationship Diagram & FK Map

```text
tb_payment
  ├── tb_payment_gateway_transaction (1:N) [Optional, if online]
  └── tb_payment_allocation (1:N) [Mandatory]
        └── tb_financial_ledger (N:1) [Mandatory]
              └── tb_stud_fee_asmt (N:1) [Mandatory]
                    ├── tb_stud_fee_component (1:N) [Mandatory]
                    ├── tb_stud_installment (1:N) [Mandatory]
                    ├── tb_fee_structure (N:1) [Snapshot anchor]
                    └── tb_installment_plan (N:1) [Snapshot anchor]

tb_stud_enrollment (sch_student)
  ├── tb_stud_fee_asmt (1:N)
  ├── tb_scholarship (1:N)
  ├── tb_concession (1:N)
  ├── tb_fee_waiver (1:N)
  ├── tb_penalty (1:N)
  └── tb_financial_hold (1:N)
```
- **Delete/Update Behaviors**: All foreign keys utilize default Postgres behaviors (RESTRICT). Cascading deletes are not implemented, enforcing strict referential integrity. 

## 6. Business Aggregates
- **Configuration Aggregate**: `tb_fee_structure`, `tb_fee_structure_component`, `tb_fee_structure_rule`, `tb_installment_plan`, `tb_installment_plan_detail`.
- **Assessment Aggregate**: `tb_stud_fee_asmt`, `tb_stud_fee_component`, `tb_stud_installment`.
- **Financial Ledger Aggregate**: `tb_financial_ledger` (serves as the central reconciliation point).
- **Payment Aggregate**: `tb_payment`, `tb_payment_allocation`, `tb_payment_gateway_transaction`.
- **Concession Aggregate**: `tb_scholarship`, `tb_concession`, `tb_fee_waiver`.
- **Exception Aggregate**: `tb_refund`, `tb_penalty`, `tb_financial_hold`.

## 7. CRUD Ownership Matrix
| Submodule | Creates | Updates | Deletes (Soft) | Reads |
| :--- | :--- | :--- | :--- | :--- |
| `sm_feeStructure` | Configuration Agg | Configuration Agg | Configuration Agg | Lookup tables |
| `sm_feeAssignment` | Assessment Agg, Ledger | Assessment Agg | - | Config Agg, Student |
| `sm_payment` | Payment Agg, Ledger | Payment Agg, Ledger | - | Assessment Agg, Ledger |
| `sm_concession` | Concession Agg, Ledger | Concession Agg | Concession Agg | Assessment Agg |
| `sm_refund` | Exception Agg, Ledger | Exception Agg | - | Payment Agg, Ledger |
| `sm_penalty` | Exception Agg, Ledger | Exception Agg | Exception Agg | Ledger, Student |

## 8. Read vs Write Matrix
- **Write-Heavy / Append-Only**: `tb_financial_ledger`, `tb_payment`, `tb_payment_allocation`.
- **Read-Heavy / Infrequent Update**: `tb_fee_structure`, `tb_fee_structure_rule`, `tb_installment_plan`.
- **Snapshot (Write Once, Read Many)**: `tb_stud_fee_asmt`, `tb_stud_fee_component`, `tb_stud_installment`.

## 9. Transaction Boundaries
- **Generate Assessment**: Must wrap `INSERT tb_stud_fee_asmt`, `INSERT tb_stud_fee_component`, `INSERT tb_stud_installment`, and `INSERT tb_financial_ledger` (Debit entry) in a single atomic transaction.
- **Receive & Allocate Payment**: Must wrap `INSERT tb_payment`, `INSERT tb_payment_allocation`, `INSERT tb_financial_ledger` (Credit entry), and potentially `UPDATE tb_financial_ledger` (`running_balance`) in one transaction. Rollback required if ledger allocation math does not sum perfectly to `tb_payment.total_amount`.

## 10. Versioning Strategy
- **Historical Snapshots**: Assessment generation acts as a snapshot. Even if `tb_fee_structure_component.amount` changes, `tb_stud_fee_component.amount` retains the historical value assessed to the student.
- **Effective Dates**: `tb_fee_structure` uses `effective_from` and `effective_to` columns. The backend must query using `CURRENT_DATE BETWEEN effective_from AND effective_to` to enforce this.

## 11. State Machines
The system relies entirely on `sch_lookup` for state workflows.
- **Fee Structures**: Draft -> Published -> Archived (tracked via `status_id`).
- **Concessions/Waivers/Refunds**: Requested -> Approved -> Rejected (tracked via `approval_status_id`).
- **Payments**: Pending -> Success -> Failed (tracked via `payment_status_id`).

## 12. Numbering Strategy
- **Database Sequences**: Native Postgres sequences (`_id_seq`) are used purely for primary keys.
- **Business Numbers**: `receipt_number` (in `tb_payment`) is a `varchar(64)` with a UNIQUE constraint (`uk_payment_receipt`). **There is no native sequence for receipt numbers.** The backend MUST generate gapless receipt numbers programmatically. 
- **Invoice Numbers**: **Do not exist in the database.** The backend must dynamically treat the `tb_stud_fee_asmt.id` or generate a metadata string to serve as an invoice number if physical PDFs are required.

## 13. External Dependencies
- **`sch_student.tb_stud_enrollment`**: Anchor for all assessment and billing.
- **`sch_org.tb_inst`**: Anchor for `tb_fee_structure` (meaning fees are institution-specific, not tenant-wide).
- **`sch_core.tb_dms`**: Used for `doc_id` to link receipts, scholarship approval letters, and physical cheques.
- **`sch_academic_struct.tb_acad_term`**: Defines exactly *when* a fee assessment applies.

## 14. Business Rules Inferred from Database Constraints
1. **Positive Amounts Only**: Extensive CHECK constraints enforce `amount >= 0`, `debit_amount >= 0`, `credit_amount >= 0`. Negative financial entries are physically impossible in this schema.
2. **Valid Percentages**: `chk_installment_percentage` enforces `0 <= percentage <= 100`.
3. **No Overlapping Logic in DB**: While the DB enforces Priority > 0 (`chk_fee_structure_priority`), it does NOT enforce uniqueness on the rule matrix (Prog + Batch + Category). The backend must ensure that multiple fee structures don't clash for the same student.
4. **Unique Allocations**: `tb_payment_allocation` has a composite unique constraint on `(payment_id, financial_ledger_id)`, preventing double-allocations of the same payment to the same ledger item.

## 15. Data Lifecycle
1. **Setup**: Admin creates `tb_fee_structure` and `tb_installment_plan`.
2. **Assignment**: Event triggers Assessment. Backend snapshots config into `tb_stud_fee_asmt` and records a Debit in `tb_financial_ledger`.
3. **Payment**: Student pays. Backend creates `tb_payment`.
4. **Settlement**: Backend splits `tb_payment` into `tb_payment_allocation` and writes Credit records into `tb_financial_ledger`.
5. **Closure**: `tb_financial_ledger.running_balance` reaches 0.00.

## 16. Concurrency Analysis
- **`tb_financial_ledger`**: The `running_balance` column represents a significant concurrency risk. If two payments are processed simultaneously for the same student, calculating the `running_balance` will result in a race condition.
- **Recommendation**: When allocating a payment, the backend MUST use Pessimistic Locking (`SELECT * FROM tb_financial_ledger WHERE stud_enrollment_id = X FOR UPDATE`) before calculating and inserting the new row to ensure the `running_balance` remains strictly sequential and accurate.

## 17. Backend Readiness
The schema is exceptionally well-designed and fully normalized for an enterprise ERP. It is **100% ready** for backend implementation. The separation of the Configuration Aggregate from the Snapshot Aggregate prevents historical data corruption, and the centralized Ledger table ensures robust double-entry-style accounting.

## 18. Recommended `db_init.py` Design

```python
# m_fees_db_init.py

class SchFees(BaseSchema):
    __schema_name__ = "sch_fees"
    
    # 1. Config Aggregate
    TB_FEE_STRUCTURE = "tb_fee_structure"
    TB_FEE_STRUCTURE_COMPONENT = "tb_fee_structure_component"
    TB_FEE_STRUCTURE_RULE = "tb_fee_structure_rule"
    
    # 2. Installment Config Aggregate
    TB_INSTALLMENT_PLAN = "tb_installment_plan"
    TB_INSTALLMENT_PLAN_DETAIL = "tb_installment_plan_detail"
    
    # 3. Assessment Aggregate
    TB_STUD_FEE_ASMT = "tb_stud_fee_asmt"
    TB_STUD_FEE_COMPONENT = "tb_stud_fee_component"
    TB_STUD_INSTALLMENT = "tb_stud_installment"
    
    # 4. Ledger & Payment Aggregate
    TB_FINANCIAL_LEDGER = "tb_financial_ledger"
    TB_PAYMENT = "tb_payment"
    TB_PAYMENT_ALLOCATION = "tb_payment_allocation"
    TB_PAYMENT_GATEWAY_TRANSACTION = "tb_payment_gateway_transaction"
    
    # 5. Concession Aggregate
    TB_SCHOLARSHIP = "tb_scholarship"
    TB_CONCESSION = "tb_concession"
    TB_FEE_WAIVER = "tb_fee_waiver"
    
    # 6. Exceptions
    TB_PENALTY = "tb_penalty"
    TB_REFUND = "tb_refund"
    TB_FINANCIAL_HOLD = "tb_financial_hold"
```
**Relationship Loading**: Assessment -> Components should be Eagerly loaded. Ledger -> Payment Allocations should be Lazily loaded due to volume.

## 19. Recommended `m_fees_data.py` Design
Split the data access layer to map strictly to Aggregates:
- `FeeConfigData`: Orchestrates Create/Update of `tb_fee_structure` alongside its rules and components inside a transaction.
- `InstallmentConfigData`: Orchestrates `tb_installment_plan`.
- `AssessmentData`: Reads from Config, executes Snapshot logic, and writes to `tb_stud_fee_asmt`.
- `LedgerData`: Core engine for writing debits/credits. Handles `FOR UPDATE` locking.
- `PaymentData`: Handles PG integrations, writes `tb_payment`, and calls `LedgerData` to execute allocations.
- `ConcessionData`: Manages Scholarships, Waivers, and Concessions, interfacing with `LedgerData` to write credit entries.

## 20. Risks & Missing Pieces Before Implementation
1. **Invoice Numbering Engine Required**: Because there is no `tb_invoice` and no database sequence for it, the backend MUST implement a thread-safe sequence generator if gapless invoice numbers are a legal compliance requirement.
2. **Receipt Number Generation**: `tb_payment.receipt_number` is a unique `varchar`. The backend must have a robust mechanism to generate this (e.g. `RCPT-2026-0001`) without violating the unique constraint during high-concurrency fee collection days.
3. **Ledger Running Balance**: As noted in Concurrency, relying on a stored `running_balance` in a multi-threaded web application is dangerous without strict row-level locking during the `INSERT` operation.
4. **No Native DB Status Validation**: The database does not constrain status transitions (e.g., Draft -> Active). The Python State Machine logic must rigorously validate `status_id` transitions.
5. **Rule Clashes**: The backend must run complex logic to determine which `tb_fee_structure_rule` wins if a student matches multiple active structures (e.g., they belong to the Batch, and they have the specific Category). The database priority field helps, but the backend must enforce the resolution.
