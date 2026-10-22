# m_fees API Contract

This document outlines the standard OneApp Request/Response API surface for the `m_fees` module.
It details the exact JSON payloads required for all actions and actionTypes based on the module's Pydantic schemas.

---

## 1. Transport & Common Format

All requests use a single gateway endpoint (`POST /`) with standard JSON payload wrapper:

#### actionType: `add`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "feeStructure",
    "action": "feeStructure",
    "actionType": "add",
    "payload": {
        "inst_id": "<integer> (Required)",
        "feeStructureCode": "<string> (Required)",
        "feeStructureName": "<string> (Required)",
        "academicYearId": "<integer> (Required)",
        "programmeId": "<integer> (Required)",
        "components": "<array> (Required)",
        "effectiveFrom": "<string> (Required)",
        "effectiveTo": "<string | null> (Optional)",
    }
}
```

#### actionType: `view`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "feeStructure",
    "action": "feeStructure",
    "actionType": "view",
    "payload": {
        "feeStructureId": "<integer | null> (Optional)",
        "inst_id": "<integer | null> (Optional)",
    }
}
```

#### actionType: `update`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "feeStructure",
    "action": "feeStructure",
    "actionType": "update",
    "payload": {
        "feeStructureId": "<integer> (Required)",
        "components": "<array | null> (Optional)",
        "effectiveTo": "<string | null> (Optional)",
        "status": "<string | null> (Optional)",
    }
}
```

#### actionType: `delete`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "feeStructure",
    "action": "feeStructure",
    "actionType": "delete",
    "payload": {
        "feeStructureId": "<integer> (Required)",
    }
}
```

---

## Submodule: `feeAssignment`

---

#### actionType: `add`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "feeAssignment",
    "action": "feeAssignment",
    "actionType": "add",
    "payload": {
        "feeStructureId": "<integer> (Required)",
        "termId": "<integer> (Required)",
        "dueDate": "<string> (Required)",
        "studentId": "<integer | null> (Optional)",
        "studentIds": "<array | null> (Optional)",
    }
}
```

#### actionType: `view`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "feeAssignment",
    "action": "feeAssignment",
    "actionType": "view",
    "payload": {
        "studentId": "<integer | null> (Optional)",
        "assignmentId": "<integer | null> (Optional)",
    }
}
```

#### actionType: `update`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "feeAssignment",
    "action": "feeAssignment",
    "actionType": "update",
    "payload": {
        "assignmentId": "<integer> (Required)",
        "dueDate": "<string | null> (Optional)",
        "feeStructureId": "<integer | null> (Optional)",
    }
}
```

#### actionType: `delete`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "feeAssignment",
    "action": "feeAssignment",
    "actionType": "delete",
    "payload": {
        "assignmentId": "<integer> (Required)",
    }
}
```

---

## Submodule: `concession`

### Action: `feeConcession`

#### actionType: `add`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "concession",
    "action": "feeConcession",
    "actionType": "add",
    "payload": {
        "studentId": "<integer> (Required)",
        "assignmentId": "<integer> (Required)",
        "concessionType": "<string> (Required)",
        "amountOrPercent": "<number | string> (Required)",
        "reason": "<string> (Required)",
        "attachments": "<array | null> (Optional)",
    }
}
```

#### actionType: `view`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "concession",
    "action": "feeConcession",
    "actionType": "view",
    "payload": {
        "studentId": "<integer | null> (Optional)",
    }
}
```

#### actionType: `update`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "concession",
    "action": "feeConcession",
    "actionType": "update",
    "payload": {
        "concessionId": "<integer> (Required)",
        "amountOrPercent": "<number | string | null> (Optional)",
        "reason": "<string | null> (Optional)",
    }
}
```

#### actionType: `delete`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "concession",
    "action": "feeConcession",
    "actionType": "delete",
    "payload": {
        "concessionId": "<integer> (Required)",
    }
}
```

---

## Submodule: `invoice`

### 3.2 `view` — Query Master Fee Structure

#### actionType: `add`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "invoice",
    "action": "feeInvoice",
    "actionType": "add",
    "payload": {
        "assignmentId": "<integer> (Required)",
    }
}
```

#### actionType: `view`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "invoice",
    "action": "feeInvoice",
    "actionType": "view",
    "payload": {
        "invoiceId": "<integer | null> (Optional)",
        "studentId": "<integer | null> (Optional)",
    }
}
```

#### actionType: `update`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "invoice",
    "action": "feeInvoice",
    "actionType": "update",
    "payload": {
        "invoiceId": "<integer> (Required)",
        "dueDate": "<string> (Required)",
    }
}
```

#### actionType: `delete`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "invoice",
    "action": "feeInvoice",
    "actionType": "delete",
    "payload": {
        "invoiceId": "<integer> (Required)",
    }
}
```

---

## Submodule: `payment`

### Action: `feePayment`

#### actionType: `add`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "payment",
    "action": "feePayment",
    "actionType": "add",
    "payload": {
        "invoiceId": "<integer> (Required)",
        "amount": "<number | string> (Required)",
        "method": "<string> (Required)",
        "transactionRef": "<string | null> (Optional)",
        "paidBy": "<string> (Required)",
    }
}
```

#### actionType: `view`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "payment",
    "action": "feePayment",
    "actionType": "view",
    "payload": {
        "paymentId": "<integer | null> (Optional)",
        "studentId": "<integer | null> (Optional)",
    }
}
```

#### actionType: `update`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "payment",
    "action": "feePayment",
    "actionType": "update",
    "payload": {
        "paymentId": "<integer> (Required)",
        "status": "<string> (Required)",
    }
}
```

#### actionType: `delete`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "payment",
    "action": "feePayment",
    "actionType": "delete",
    "payload": {
        "paymentId": "<integer> (Required)",
    }
}
```

---

## Submodule: `refund`

### 3.3 `update` — Modify Fee Structure

#### actionType: `add`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "refund",
    "action": "feeRefund",
    "actionType": "add",
    "payload": {
        "studentId": "<integer> (Required)",
        "invoiceId": "<integer> (Required)",
        "amount": "<number | string> (Required)",
        "reason": "<string> (Required)",
    }
}
```

#### actionType: `view`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "refund",
    "action": "feeRefund",
    "actionType": "view",
    "payload": {
        "refundId": "<integer | null> (Optional)",
        "studentId": "<integer | null> (Optional)",
    }
}
```

#### actionType: `update`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "refund",
    "action": "feeRefund",
    "actionType": "update",
    "payload": {
        "refundId": "<integer> (Required)",
        "status": "<string> (Required)",
        "remarks": "<string | null> (Optional)",
    }
}
```

#### actionType: `delete`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "refund",
    "action": "feeRefund",
    "actionType": "delete",
    "payload": {
        "refundId": "<integer> (Required)",
        "remarks": "<string> (Required)",
    }
}
```

---

## Submodule: `penalty`

---

#### actionType: `add`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "penalty",
    "action": "feePenalty",
    "actionType": "add",
    "payload": {
        "inst_id": "<integer> (Required)",
        "gracePeriodDays": "<integer> (Required)",
        "penaltyType": "<string> (Required)",
        "penaltyValue": "<number | string> (Required)",
    }
}
```

#### actionType: `view`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "penalty",
    "action": "feePenalty",
    "actionType": "view",
    "payload": {
        "inst_id": "<integer | null> (Optional)",
    }
}
```

#### actionType: `update`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "penalty",
    "action": "feePenalty",
    "actionType": "update",
    "payload": {
        "inst_id": "<integer> (Required)",
        "gracePeriodDays": "<integer | null> (Optional)",
        "penaltyType": "<string | null> (Optional)",
        "penaltyValue": "<number | string | null> (Optional)",
    }
}
```

#### actionType: `delete`
**Expected Payload**:
```json
{
    "mod": "m_fees",
    "subMod": "penalty",
    "action": "feePenalty",
    "actionType": "delete",
    "payload": {
        "inst_id": "<integer> (Required)",
    }
}
```

---

