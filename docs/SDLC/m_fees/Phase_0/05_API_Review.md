# m_fees - 05 API Review

**Module Name**: m_fees
**Phase**: Phase_0
**Version**: 1.0.0
**Date**: 2026-07-28
**Author**: Siddharth Amdal
**Status**: Approved

## Related Documents
- None

---

## Overview

# OneApp API Contract: m_fees
## Overview
This document outlines the API contract for the `m_fees` module based on the final Phase 4 schema implementation.

## Endpoints (Actions & Types)

### Action: `feeStructure`
#### `ADD`
**Payload Schema:**
```json
{
    "inst_id": "integer (Required)",
    "feeStructureCode": "string (Required)",
    "feeStructureName": "string (Required)",
    "academicYearId": "integer (Required)",
    "programmeId": "integer (Required)",
    "components": "array (Required)",
    "effectiveFrom": "string (Required)",
    "effectiveTo": "string | null (Optional)"
}
```

#### `VIEW`
**Payload Schema:**
```json
{
    "feeStructureId": "integer | null (Optional)",
    "inst_id": "integer | null (Optional)"
}
```

#### `UPDATE`
**Payload Schema:**
```json
{
    "feeStructureId": "integer (Required)",
    "components": "array | null (Optional)",
    "effectiveTo": "string | null (Optional)",
    "status": "string | null (Optional)"
}
```

#### `DELETE`
**Payload Schema:**
```json
{
    "feeStructureId": "integer (Required)"
}
```

### Action: `feeAssignment`
#### `ADD`
**Payload Schema:**
```json
{
    "feeStructureId": "integer (Required)",
    "termId": "integer (Required)",
    "dueDate": "string (Required)",
    "studentId": "integer | null (Optional)",
    "studentIds": "array | null (Optional)"
}
```

#### `VIEW`
**Payload Schema:**
```json
{
    "studentId": "integer | null (Optional)",
    "assignmentId": "integer | null (Optional)"
}
```

#### `UPDATE`
**Payload Schema:**
```json
{
    "assignmentId": "integer (Required)",
    "dueDate": "string | null (Optional)",
    "feeStructureId": "integer | null (Optional)"
}
```

#### `DELETE`
**Payload Schema:**
```json
{
    "assignmentId": "integer (Required)"
}
```

### Action: `feeConcession`
#### `ADD`
**Payload Schema:**
```json
{
    "studentId": "integer (Required)",
    "assignmentId": "integer (Required)",
    "concessionType": "string (Required)",
    "amountOrPercent": "number | string (Required)",
    "reason": "string (Required)",
    "attachments": "array | null (Optional)"
}
```

#### `VIEW`
**Payload Schema:**
```json
{
    "studentId": "integer | null (Optional)"
}
```

#### `UPDATE`
**Payload Schema:**
```json
{
    "concessionId": "integer (Required)",
    "amountOrPercent": "number | string | null (Optional)",
    "reason": "string | null (Optional)"
}
```

#### `DELETE`
**Payload Schema:**
```json
{
    "concessionId": "integer (Required)"
}
```

### Action: `feeInvoice`
#### `ADD`
**Payload Schema:**
```json
{
    "assignmentId": "integer (Required)"
}
```

#### `VIEW`
**Payload Schema:**
```json
{
    "invoiceId": "integer | null (Optional)",
    "studentId": "integer | null (Optional)"
}
```

#### `UPDATE`
**Payload Schema:**
```json
{
    "invoiceId": "integer (Required)",
    "dueDate": "string (Required)"
}
```

#### `DELETE`
**Payload Schema:**
```json
{
    "invoiceId": "integer (Required)"
}
```

### Action: `feePayment`
#### `ADD`
**Payload Schema:**
```json
{
    "invoiceId": "integer (Required)",
    "amount": "number | string (Required)",
    "method": "string (Required)",
    "transactionRef": "string | null (Optional)",
    "paidBy": "string (Required)"
}
```

#### `VIEW`
**Payload Schema:**
```json
{
    "paymentId": "integer | null (Optional)",
    "studentId": "integer | null (Optional)"
}
```

#### `UPDATE`
**Payload Schema:**
```json
{
    "paymentId": "integer (Required)",
    "status": "string (Required)"
}
```

#### `DELETE`
**Payload Schema:**
```json
{
    "paymentId": "integer (Required)"
}
```

### Action: `feeRefund`
#### `ADD`
**Payload Schema:**
```json
{
    "studentId": "integer (Required)",
    "invoiceId": "integer (Required)",
    "amount": "number | string (Required)",
    "reason": "string (Required)"
}
```

#### `VIEW`
**Payload Schema:**
```json
{
    "refundId": "integer | null (Optional)",
    "studentId": "integer | null (Optional)"
}
```

#### `UPDATE`
**Payload Schema:**
```json
{
    "refundId": "integer (Required)",
    "status": "string (Required)",
    "remarks": "string | null (Optional)"
}
```

#### `DELETE`
**Payload Schema:**
```json
{
    "refundId": "integer (Required)",
    "remarks": "string (Required)"
}
```

### Action: `feePenalty`
#### `ADD`
**Payload Schema:**
```json
{
    "inst_id": "integer (Required)",
    "gracePeriodDays": "integer (Required)",
    "penaltyType": "string (Required)",
    "penaltyValue": "number | string (Required)"
}
```

#### `VIEW`
**Payload Schema:**
```json
{
    "inst_id": "integer | null (Optional)"
}
```

#### `UPDATE`
**Payload Schema:**
```json
{
    "inst_id": "integer (Required)",
    "gracePeriodDays": "integer | null (Optional)",
    "penaltyType": "string | null (Optional)",
    "penaltyValue": "number | string | null (Optional)"
}
```

#### `DELETE`
**Payload Schema:**
```json
{
    "inst_id": "integer (Required)"
}
```



---
**Previous**: [../Phase_0/04_Architecture_Review.md](../Phase_0/04_Architecture_Review.md)
**Next**: [../Phase_0/06_Risk_Assessment.md](../Phase_0/06_Risk_Assessment.md)
