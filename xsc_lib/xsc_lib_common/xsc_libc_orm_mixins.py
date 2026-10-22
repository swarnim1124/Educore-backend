"""
File: xsc_libc_orm_mixins.py
Description: Shared platform-wide SQLAlchemy ORM Mixins complying with OneApp Engineering Standard v1.0.

Author: Siddharth Amdal
App: OneApp

"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, BigInteger, Boolean, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID

class UUIDPrimaryKeyMixin:
    """
    Standard Primary Key Mixin using native PostgreSQL UUID type.
    The application generates a UUID4 by default before persistence.
    """
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

class AuditMixin:
    """
    Standard Audit Mixin for tracking record creation and modification accountability.
    """
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = Column(BigInteger, nullable=True) # References sch_iam.tb_user(id)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    updated_by = Column(BigInteger, nullable=True) # References sch_iam.tb_user(id)

class SoftDeleteMixin:
    """
    Standard Soft Delete Mixin for safe data recovery without breaking referential integrity.
    Does not replace audit logging.
    """
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(BigInteger, nullable=True) # References sch_iam.tb_user(id)

class TenantMixin:
    """
    Standard Tenant Mixin enforcing the Institution boundary (inst_id).
    """
    inst_id = Column(BigInteger, index=True, nullable=False)

class VersionMixin:
    """
    Standard Version Mixin for optimistic locking on mutable business entities.
    """
    row_version = Column(Integer, default=1, nullable=False)
