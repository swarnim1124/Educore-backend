"""
File: db_init.py
Description: SQLAlchemy models for m_AAA.

Author: Siddharth Amdal
App: OneApp

"""

from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, ForeignKey, Text, JSON, Numeric
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

from xsc_lib.xsc_lib_common.xsc_libc_orm_mixins import UUIDPrimaryKeyMixin, AuditMixin, SoftDeleteMixin as StdSoftDeleteMixin, TenantMixin, VersionMixin

Base = declarative_base()


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class SoftDeleteMixin:
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

class TbUserPasswordState(UUIDPrimaryKeyMixin, AuditMixin, StdSoftDeleteMixin, VersionMixin, Base):
    __tablename__ = 'tb_user_password_state'
    __table_args__ = {'schema': 'sch_iam'}

    user_id = Column(BigInteger, ForeignKey('sch_iam.tb_user.id', ondelete='CASCADE'), nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    requires_reset = Column(Boolean, default=False, nullable=False)
    lockout_until = Column(DateTime(timezone=True), nullable=True)
    failed_attempts = Column(Integer, default=0, nullable=False)


class TbPasswordReset(Base):
    __tablename__ = "tb_password_reset"
    __table_args__ = {"schema": "sch_aaa"}

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('sch_iam.tb_user.id'), nullable=False)
    reset_token = Column(String(256), nullable=False, unique=True)
    requested_at = Column(DateTime(timezone=True), nullable=False)
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("sch_iam.tb_user.id"), nullable=False)
    reset_token = Column(String, nullable=False)
    requested_at = Column(String, nullable=False)
    request_ip = Column(String)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True))
    status_id = Column(Integer, ForeignKey('sch_lookup.tb_lookup.id'), nullable=False)

class TbUserSession(Base):
    __tablename__ = 'tb_user_session'
    __table_args__ = {'schema': 'sch_iam'}

    id = Column(BigInteger, primary_key=True)
    login_id = Column(BigInteger, ForeignKey('sch_iam.tb_user_login.id'), nullable=False)
    user_id = Column(BigInteger, ForeignKey('sch_iam.tb_user.id'), nullable=False)
    user_org_id = Column(BigInteger, ForeignKey('sch_rbac.tb_user_org.id', ondelete='RESTRICT'))
    session_token = Column(String(512), nullable=False, unique=True)
    refresh_token = Column(String(512), nullable=False, unique=True)
    last_activity_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    device_name = Column(String(128))
    device_type_id = Column(Integer, ForeignKey('sch_lookup.tb_lookup.id'))
    device_os = Column(Integer)
    browser = Column(String(128))
    ip_address = Column(String)
    user_agent = Column(String(520))
    status_id = Column(Integer, ForeignKey('sch_lookup.tb_lookup.id'), nullable=False)
    expires_at = Column(String, nullable=False)
    used_at = Column(String)
    status_id = Column(String, ForeignKey("sch_lookup.tb_lookup.id"), nullable=False)


class TbAuthLog(Base):
    __tablename__ = "tb_auth_log"
    __table_args__ = {"schema": "sch_aaa"}

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('sch_iam.tb_user.id'), nullable=False)
    user_org_id = Column(BigInteger, ForeignKey('sch_rbac.tb_user_org.id'))
    session_id = Column(BigInteger, ForeignKey('sch_iam.tb_user_session.id'))
    evt_type_id = Column(Integer, ForeignKey('sch_lookup.tb_lookup.id'), nullable=False)
    evt_status_id = Column(Integer, ForeignKey('sch_lookup.tb_lookup.id'), nullable=False)
    evt_at = Column(DateTime(timezone=True), nullable=False)
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("sch_iam.tb_user.id"), nullable=False)
    user_org_id = Column(String, ForeignKey("sch_rbac.tb_user_org.id"))
    session_id = Column(String, ForeignKey("sch_iam.tb_user_session.id"))
    evt_type_id = Column(String, ForeignKey("sch_lookup.tb_lookup.id"), nullable=False)
    evt_status_id = Column(
        String, ForeignKey("sch_lookup.tb_lookup.id"), nullable=False
    )
    evt_at = Column(String, nullable=False)
    ip_address = Column(String)
    user_agent = Column(String(512))
    device_name = Column(String(128))
    failure_reason_id = Column(Integer, ForeignKey('sch_lookup.tb_lookup.id'))
    user_agent = Column(String)
    device_name = Column(String)
    failure_reason_id = Column(String, ForeignKey("sch_lookup.tb_lookup.id"))


class TbMfaMethod(TimestampMixin, Base):
    __tablename__ = "tb_mfa_method"
    __table_args__ = {"schema": "sch_aaa"}

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('sch_iam.tb_user.id'), nullable=False)
    mfa_type_id = Column(Integer, ForeignKey('sch_lookup.tb_lookup.id'), nullable=False)
    secret_key = Column(String(256))
    phone = Column(String(32))
    email = Column(String(256))
    is_primary = Column(Boolean, nullable=False)
    is_verified = Column(Boolean, nullable=False)
    is_active = Column(Boolean, nullable=False)

class TbMfaBackupCode(UUIDPrimaryKeyMixin, AuditMixin, StdSoftDeleteMixin, VersionMixin, Base):
    __tablename__ = 'tb_mfa_backup_code'
    __table_args__ = {'schema': 'sch_aaa'}

    mfa_method_id = Column(BigInteger, ForeignKey('sch_aaa.tb_mfa_method.id', ondelete='CASCADE'), nullable=False, index=True)
    code_hash = Column(String, nullable=False)
    is_used = Column(Boolean, nullable=False, default=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("sch_iam.tb_user.id"), nullable=False)
    mfa_type_id = Column(String, ForeignKey("sch_lookup.tb_lookup.id"), nullable=False)
    secret_key = Column(String)
    phone = Column(String)
    email = Column(String)
    is_primary = Column(String, nullable=False)
    is_verified = Column(String, nullable=False)
    is_active = Column(String, nullable=False)


class TbMfaChallenge(Base):
    __tablename__ = "tb_mfa_challenge"
    __table_args__ = {"schema": "sch_aaa"}

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('sch_iam.tb_user.id'), nullable=False)
    session_id = Column(BigInteger, ForeignKey('sch_iam.tb_user_session.id'), nullable=False)
    mfa_method_id = Column(BigInteger, ForeignKey('sch_aaa.tb_mfa_method.id'), nullable=False)
    challenge_token = Column(String(256), nullable=False, unique=True)
    otp_code = Column(String(16))
    issued_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified_at = Column(DateTime(timezone=True))
    status_id = Column(Integer, ForeignKey('sch_lookup.tb_lookup.id'), nullable=False)
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("sch_iam.tb_user.id"), nullable=False)
    session_id = Column(
        String, ForeignKey("sch_iam.tb_user_session.id"), nullable=False
    )
    mfa_method_id = Column(
        String, ForeignKey("sch_aaa.tb_mfa_method.id"), nullable=False
    )
    challenge_token = Column(String, nullable=False)
    otp_code = Column(String)
    issued_at = Column(String, nullable=False)
    expires_at = Column(String, nullable=False)
    verified_at = Column(String)
    status_id = Column(String, ForeignKey("sch_lookup.tb_lookup.id"), nullable=False)


class TbAccountLock(Base):
    __tablename__ = 'tb_account_lock'
    __table_args__ = {'schema': 'sch_aaa'}

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('sch_iam.tb_user.id'), nullable=False)
    lock_reason_id = Column(Integer, ForeignKey('sch_lookup.tb_lookup.id'), nullable=False)
    locked_at = Column(DateTime(timezone=True), nullable=False)
    locked_until = Column(DateTime(timezone=True))
    unlocked_at = Column(DateTime(timezone=True))
    unlock_reason_id = Column(Integer, ForeignKey('sch_lookup.tb_lookup.id'))


class TbInstitutionPasswordPolicy(UUIDPrimaryKeyMixin, TenantMixin, AuditMixin, StdSoftDeleteMixin, Base):
    __tablename__ = 'tb_institution_password_policy'
    __table_args__ = {'schema': 'sch_aaa'}

    inst_id = Column(BigInteger, ForeignKey('sch_org.tb_inst.id', ondelete='CASCADE'), nullable=False, index=True)
    min_length = Column(Integer, default=8)
    require_uppercase = Column(Boolean, default=True)
    require_number = Column(Boolean, default=True)
    require_special = Column(Boolean, default=True)
    expiry_days = Column(Integer, default=90)
    history_count = Column(Integer, default=5)
    max_attempts = Column(Integer, default=5)
    is_deleted = Column(Boolean, default=False, nullable=True)

class TbInstitutionSessionPolicy(UUIDPrimaryKeyMixin, TenantMixin, AuditMixin, StdSoftDeleteMixin, Base):
    __tablename__ = 'tb_institution_session_policy'
    __table_args__ = {'schema': 'sch_aaa'}

    inst_id = Column(BigInteger, ForeignKey('sch_org.tb_inst.id', ondelete='CASCADE'), nullable=False, index=True)
    idle_timeout_minutes = Column(Integer, default=15)
    max_session_duration = Column(Integer, default=720) # 12 hours
    max_concurrent_sessions = Column(Integer, default=1)
    enforce_device_binding = Column(Boolean, default=False)
    ip_whitelist = Column(JSONB, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=True)

class TbInstitutionLoginPolicy(UUIDPrimaryKeyMixin, TenantMixin, AuditMixin, StdSoftDeleteMixin, Base):
    __tablename__ = 'tb_institution_login_policy'
    __table_args__ = {'schema': 'sch_aaa'}

    inst_id = Column(BigInteger, ForeignKey('sch_org.tb_inst.id', ondelete='CASCADE'), nullable=False, index=True)
    enable_captcha = Column(Boolean, default=False)
    captcha_threshold = Column(Numeric, default=0.5)
    allowed_auth_methods = Column(JSONB, default=["password"])
    enable_ip_restriction = Column(Boolean, default=False)
    blocked_ips = Column(JSONB, nullable=True)
    enable_geo_restriction = Column(Boolean, default=False)
    allowed_countries = Column(JSONB, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=True)

class TbRole(TimestampMixin, Base):
    __tablename__ = 'tb_role'
    __table_args__ = {'schema': 'sch_iam'}

    id = Column(String, primary_key=True)
    role_code = Column(String, nullable=False, unique=True)
    role_name = Column(String, nullable=False)
    description = Column(String)
    status_id = Column(Integer, default=1)

class TbPermission(TimestampMixin, Base):
    __tablename__ = 'tb_permission'
    __table_args__ = {'schema': 'sch_rbac'}

    id = Column(String, primary_key=True)
    permission_code = Column(String, nullable=False, unique=True)
    description = Column(String)

class TbModule(TimestampMixin, Base):
    __tablename__ = 'tb_module'
    __table_args__ = {'schema': 'sch_rbac'}

    id = Column(String, primary_key=True)
    permission_code = Column(String, ForeignKey('sch_rbac.tb_permission.permission_code', ondelete='CASCADE'), nullable=False)
    module_name = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    icon = Column(String)
    route = Column(String)
    status = Column(String, default='Active')
    enabled = Column(Boolean, default=True)

class TbOrgRole(TimestampMixin, Base):
    __tablename__ = 'tb_org_role'
    __table_args__ = {'schema': 'sch_rbac'}

    id = Column(String, primary_key=True)
    org_id = Column(String, nullable=False)
    role_id = Column(String, ForeignKey('sch_iam.tb_role.id'), nullable=False)
    status_id = Column(Integer, default=1)

class TbRolePermission(TimestampMixin, Base):
    __tablename__ = 'tb_role_permission'
    __table_args__ = {'schema': 'sch_rbac'}

    id = Column(String, primary_key=True)
    role_id = Column(String, ForeignKey('sch_iam.tb_role.id', ondelete='CASCADE'), nullable=False)
    permission_id = Column(String, ForeignKey('sch_rbac.tb_permission.id', ondelete='CASCADE'), nullable=False)

class TbUserOrg(TimestampMixin, Base):
    __tablename__ = 'tb_user_org'
    __table_args__ = {'schema': 'sch_rbac'}
    __tablename__ = "tb_account_lock"
    __table_args__ = {"schema": "sch_aaa"}

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('sch_iam.tb_user.id'), nullable=False)
    org_id = Column(String, nullable=False)
    status_id = Column(Integer, default=1)

class TbUserRole(TimestampMixin, Base):
    __tablename__ = 'tb_user_role'
    __table_args__ = {'schema': 'sch_rbac'}

    id = Column(String, primary_key=True)
    user_org_id = Column(String, ForeignKey('sch_rbac.tb_user_org.id', ondelete='CASCADE'), nullable=False)
    org_role_id = Column(String, ForeignKey('sch_rbac.tb_org_role.id', ondelete='CASCADE'), nullable=False)
    status_id = Column(Integer, default=1)

    user_id = Column(String, ForeignKey("sch_iam.tb_user.id"), nullable=False)
    lock_reason_id = Column(
        String, ForeignKey("sch_lookup.tb_lookup.id"), nullable=False
    )
    locked_at = Column(String, nullable=False)
    locked_until = Column(String)
    unlocked_at = Column(String)
    unlock_reason_id = Column(String, ForeignKey("sch_lookup.tb_lookup.id"))
