# OneApp m_fees — Phase 0.7 Implementation Roadmap

## 1. Executive Summary
- **Module Objective**: Standardize and automate the institutional fee lifecycle, from defining structures to processing payments and managing late penalties.
- **Current Readiness**: Database schema (`sch_fees`) is physically live; Functional Analysis is approved; Phase 0.7 architecture planning is complete.
- **Major Business Capabilities**: Fee Structure Management, Student Assignment, Concessions, Invoicing, Payment Collection, Refunds, Late Payment Penalties.
- **Major Technical Capabilities**: Double-entry ledger integration (`tb_financial_ledger`), gapless receipt number generation, pessimistic concurrency locking (`SELECT FOR UPDATE`), atomic bulk assignment transactions.
- **External Dependencies**: `m_aaa` (Auth/RBAC), `m_curriculum` (Programs/Terms), `m_exam` (Hall-ticket integration), External Payment Gateways.
- **Development Readiness**: Fully ready. Gate 1 criteria met.

## 2. Module Architecture
The module strictly adheres to the OneApp Gold Standard structure:
```text
modules/
└── m_fees/
    ├── manifest.py                 # Module registration and configuration.
    ├── db_init.py                  # ORM classes mapping to sch_fees.
    ├── sch_fees.py                 # Pydantic schemas for request/response serialization.
    ├── m_fees_data.py              # Data access layer (DAL) containing all database queries.
    ├── m_fees_sm_feeStructure.py   # Handler for feeStructure action.
    ├── m_fees_sm_feeAssignment.py  # Handler for studentFeeAssignment action.
    ├── m_fees_sm_concession.py     # Handler for feeConcession action.
    ├── m_fees_sm_invoice.py        # Handler for feeInvoice action.
    ├── m_fees_sm_payment.py        # Handler for feePayment action.
    ├── m_fees_sm_refund.py         # Handler for feeRefund action.
    └── m_fees_sm_penalty.py        # Handler for latePaymentPenalty action.
```
- **Responsibility**: Each `m_fees_sm_*.py` file handles request parsing, validation, calling `m_fees_data.py`, and formatting responses.
- **Ownership**: `m_fees_data.py` exclusively owns PostgreSQL transactions.
- **Dependencies**: Depends on the shared `utils` package for logging and database connection pooling.

## 3. Submodule Architecture

### sm_feeStructure
- **Purpose**: Defines master fee components for a programme/year.
- **Business/Database Ownership**: Finance / `tb_fee_structure`, `tb_fee_structure_component`, `tb_fee_structure_rule`, `tb_installment_plan`.
- **Read Tables**: Self + `tb_financial_ledger` (to check deletion block).
- **Write Tables**: Self tables.
- **Expected APIs**: `feeStructure` (`add`, `view`, `update`, `delete`).
- **Data Layer**: `FeeStructureData` class in `m_fees_data.py`.
- **Risk Level**: Low.

### sm_feeAssignment
- **Purpose**: Links structures to enrolled students.
- **Business/Database Ownership**: Finance / `tb_stud_fee_asmt`, `tb_stud_fee_component`, `tb_stud_installment`, `tb_financial_ledger` (Debit entries).
- **Read Tables**: Self + `tb_fee_structure` + `tb_financial_ledger`.
- **Write Tables**: Self tables + `tb_financial_ledger`.
- **Expected APIs**: `studentFeeAssignment` (`add`, `view`, `update`, `delete`).
- **Data Layer**: `AssessmentData` class in `m_fees_data.py`.
- **Risk Level**: Medium (Bulk assignment atomicity required).

### sm_concession
- **Purpose**: Applies scholarships/discounts.
- **Business/Database Ownership**: Finance / `tb_scholarship`, `tb_concession`, `tb_fee_waiver`.
- **Read Tables**: Self + `tb_stud_fee_asmt` + `tb_financial_ledger`.
- **Write Tables**: Self tables.
- **Expected APIs**: `feeConcession` (`add`, `view`, `update`, `delete`).
- **Data Layer**: `ConcessionData` class in `m_fees_data.py`.
- **Risk Level**: Medium (Triggers net payable recalculations).

### sm_invoice
- **Purpose**: Logical billing generation.
- **Business/Database Ownership**: System/Finance / (Logical aggregation of `tb_stud_fee_asmt` and concessions).
- **Read Tables**: `tb_stud_fee_asmt`, `tb_fee_structure`, `tb_scholarship`, `tb_financial_ledger`.
- **Write Tables**: None physically (handled via assessment and ledger states).
- **Expected APIs**: `feeInvoice` (`add` (regenerate), `view`, `update`, `delete`).
- **Data Layer**: `InvoiceData` class in `m_fees_data.py`.
- **Risk Level**: Low.

### sm_payment
- **Purpose**: Records incoming funds.
- **Business/Database Ownership**: Finance / `tb_payment`, `tb_payment_allocation`, `tb_payment_gateway_transaction`, `tb_financial_ledger` (Credit entries).
- **Read Tables**: Self + `tb_financial_ledger` + `tb_stud_fee_asmt`.
- **Write Tables**: Self tables + `tb_financial_ledger`.
- **Expected APIs**: `feePayment` (`add`, `view`, `update`, `delete`).
- **Data Layer**: `PaymentData` class in `m_fees_data.py`.
- **Risk Level**: Critical (Pessimistic locking and idempotency required).

### sm_refund
- **Purpose**: Returns funds.
- **Business/Database Ownership**: Finance / `tb_refund`.
- **Read Tables**: Self + `tb_payment`.
- **Write Tables**: Self tables.
- **Expected APIs**: `feeRefund` (`add`, `view`, `update`, `delete`).
- **Data Layer**: `RefundData` class in `m_fees_data.py`.
- **Risk Level**: Medium.

### sm_penalty
- **Purpose**: Late fee enforcement.
- **Business/Database Ownership**: Admin / `tb_penalty`, `tb_financial_hold`.
- **Read Tables**: Self + `tb_financial_ledger` + `tb_stud_fee_asmt`.
- **Write Tables**: Self tables.
- **Expected APIs**: `latePaymentPenalty` (`add`, `view`, `update`, `delete`).
- **Data Layer**: `PenaltyData` class in `m_fees_data.py`.
- **Risk Level**: Medium.

## 4. API Planning Matrix
All APIs use `POST /` gateway.
| Submodule | Action | ActionType | Purpose | Auth | Transaction? | Audit? |
|---|---|---|---|---|---|---|
| `sm_feeStructure` | `feeStructure` | `add/update/delete` | Configures structures | Finance | Yes | Yes |
| `sm_feeStructure` | `feeStructure` | `view` | Lists structures | Finance/Student (own) | No | No |
| `sm_feeAssignment` | `studentFeeAssignment` | `add/update/delete` | Assigns structures | Finance | Yes (Bulk) | Yes |
| `sm_feeAssignment` | `studentFeeAssignment` | `view` | Views dues | Finance/Student (own) | No | No |
| `sm_concession` | `feeConcession` | `add/update/delete` | Manages discounts | Finance | Yes | Yes |
| `sm_concession` | `feeConcession` | `view` | Lists concessions | Finance/Student (own) | No | No |
| `sm_invoice` | `feeInvoice` | `add/update` | Regenerates/Extends | Finance | Yes | Yes |
| `sm_invoice` | `feeInvoice` | `view` | Downloads invoice | Finance/Student (own) | No | No |
| `sm_payment` | `feePayment` | `add/update/delete` | Records/bounces payment | Finance/Student (add) | Yes (Locks) | Yes |
| `sm_payment` | `feePayment` | `view` | Downloads receipt | Finance/Student (own) | No | No |
| `sm_refund` | `feeRefund` | `add/update/delete` | Manages refund workflows | Finance/Student (add) | Yes | Yes |
| `sm_penalty` | `latePaymentPenalty` | `add/update/delete` | Configures late fees | Admin/Finance | Yes | Yes |

## 5. Data Layer Design (`m_fees_data.py`)
Split into distinct classes:
- **`FeeStructureData`**: Owns `tb_fee_structure*`.
- **`AssessmentData`**: Owns `tb_stud_fee_asmt*`. Handles bulk transactional insert.
- **`ConcessionData`**: Owns `tb_scholarship`, `tb_concession`, `tb_fee_waiver`.
- **`PaymentData`**: Owns `tb_payment*`. Public method `allocate_payment(session, payment)` implements pessimistic lock on `tb_financial_ledger`.
- **`LedgerData`**: Owns `tb_financial_ledger`. Provides `get_running_balance(session, studId)`.
- **`RefundData`**: Owns `tb_refund`.
- **`PenaltyData`**: Owns `tb_penalty*`.

## 6. ORM Planning (`db_init.py` & `sch_fees.py`)
- **Entity Grouping**: All mapped under the `SchFees` declarative base.
- **Relationships**: 
  - `TbStudFeeAsmt` has `lazy='selectin'` relationship to `TbStudFeeComponent`.
  - `TbFinancialLedger` has `lazy='noload'` for offline/historic querying to save memory.
- **Cross-Schema**: Uses string references (e.g. `sch_student.tb_stud_enrollment.id`) instead of strict foreign key cascades to enforce decoupled modules.
- **Pydantic**: Base schemas for payload validation; Response schemas for nested outputs.

## 7. Shared Services
- **`NetPayableCalculator`**: Calculates `Gross (Structure) - Concessions`. Consumed by Invoice and Payment.
- **`OutstandingCalculator`**: Calculates `Net Payable - Allocated Credits in Ledger`.
- **`LedgerService`**: Standardizes Debit/Credit insertion and running balance calculation.
- **`ReceiptGenerator`**: Service returning unique gapless receipt strings.

## 8. Shared Utilities
- **`DecimalUtility`**: Enforces strict `Numeric(10,2)` casting and rounding for all float inputs to prevent floating-point drift.
- **`ResponseBuilder`**: Standardizes success/error json blocks.
- **`AuditHelper`**: Standardizes injection of `created_by`/`updated_by` from JWT contexts.

## 9. Validation Catalogue
- **`VAL-FEE-01`**: `feeStructureCode` must be unique. (Severity: High, Owner: `FeeStructureData`)
- **`VAL-FEE-02`**: Payment amount must be `<= outstanding_balance`. (Severity: Critical, Owner: `PaymentData`)
- **`VAL-FEE-03`**: Bulk assignments must rollback entirely on single failure. (Severity: High, Owner: `AssessmentData`)
- **`VAL-FEE-04`**: Refund amount must be `<= paid_amount`. (Severity: High, Owner: `RefundData`)

## 10. Authorization Matrix
- **Student**: `view` (Own ID only). `add` (Payment online, Refund Request).
- **Finance**: `add, view, update, delete` across all submodules globally.
- **Institution Admin**: Reports, Policy Configuration (Penalty), Overrides.
- **System**: Background cron jobs for auto-penalty application.

## 11. Transaction Design
### 11.1 Payment Allocation (Critical)
- **Sequence**: 1. Insert `tb_payment` 2. `SELECT FOR UPDATE` on `tb_financial_ledger` (lock rows) 3. Insert `tb_payment_allocation` 4. Update `running_balance`.
- **Locking Strategy**: Pessimistic Row Lock.
- **Idempotency**: Block duplicate requests sharing identical `transactionRef`.
- **Failure**: Rollback entire block; release lock.

### 11.2 Bulk Assignment
- **Sequence**: Iterate studentIds -> Insert Asmt -> Insert Components -> Insert Debit Ledger.
- **Failure**: Any db constraint failure triggers full `session.rollback()`.

## 12. Integration Architecture
- **`m_exam`**: Reads `sm_payment` status synchronously before generating hall tickets.
- **`m_curriculum`**: Reads `sm_feeStructure` synchronously for enrollment portal.
- **`m_aaa`**: Validates JWTs asynchronously at API gateway level.
- **Payment Gateway**: Asynchronous Webhook triggers `feePayment/add` -> must be idempotent.

## 13. Logging Strategy
- **Request/Response Logs**: Handled by OneApp global interceptor.
- **Audit Logs**: Stored via `created_by` / `updated_by` DB columns.
- **Payment Events**: Critical `info` logs for every payment initialization and resolution. Includes gateway payload traces.
- **Correlation IDs**: Inherit X-Request-ID from gateway for tracing.

## 14. Exception Strategy
- **`FeeValidationException`**: Maps to 400 Bad Request. (e.g. Overpayment attempt).
- **`FeeConcurrencyException`**: Maps to 409 Conflict. (e.g. Lock timeout during payment allocation).
- **`FeeAuthorizationException`**: Maps to 403 Forbidden. (e.g. Student viewing another's invoice).
- **`FeeNotFoundException`**: Maps to 404 Not Found.

## 15. Testing Strategy
- **Unit Tests**: `NetPayableCalculator`, `OutstandingCalculator` (100% coverage).
- **Integration Tests**: Payment Allocation simulating concurrent requests to ensure lock integrity. Bulk assignment rollback testing.
- **API Tests**: Postman scripts verifying payload schemas.
- **Negative Tests**: Attempting overpayment, deleting structures with assignments, floating-point input abuse.

## 16. Development Plan
1. **Foundation**: `manifest.py`, `db_init.py`, `sch_fees.py` (Schemas).
2. **Master Data**: `m_fees_data.py` (FeeStructureData), `sm_feeStructure`.
3. **Core Logic**: Shared Services (`NetPayableCalculator`, `LedgerService`).
4. **Transactions**: `sm_feeAssignment`, `sm_concession`, `sm_invoice`.
5. **Critical Paths**: `sm_payment` (Locking/Allocation), `sm_refund`.
6. **Auxiliary**: `sm_penalty`.

## 17. Risk Assessment
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Concurrent double payment via API & Webhook | Medium | Critical | Pessimistic locking (`FOR UPDATE`) + Idempotency keys (`transactionRef`). |
| Floating point arithmetic drift | Low | Critical | Use strictly `Decimal`/`Numeric(10,2)` in Python and Postgres. |
| Bulk Assignment DB timeout | Medium | Medium | Paginate large batch assignments or process via async queue if > 1000 students. |

## 18. Gate 1 Readiness Checklist (Exit Criteria)
- [x] Framework Reviewed
- [x] Functional Analysis Complete
- [x] Database Analysis Complete
- [x] Architecture Finalized
- [x] API Planning Complete
- [x] Transactions Planned (Locking strategy verified)
- [x] Validation Catalogue Complete
- [x] Authorization Matrix Complete
- [x] Testing Strategy Complete
- [x] Implementation Sequence Approved

**Gate 1 — READY FOR DEVELOPMENT**
