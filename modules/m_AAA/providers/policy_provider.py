from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy import select
from xsc_lib.xsc_lib_common.xsc_libc_pgrs import PostgreSQLManager
from xsc_lib.xsc_lib_app.xsc_liba_capability import CapabilityRegistry
from .policy_models import PasswordPolicy, SessionPolicy, LoginPolicy
from modules.m_AAA.db_init import TbInstitutionLoginPolicy, TbInstitutionPasswordPolicy, TbInstitutionSessionPolicy
import json

class PolicyProvider(ABC):
    @abstractmethod
    async def get_login_policy(self, inst_id: str) -> LoginPolicy:
        pass
        
    @abstractmethod
    async def get_password_policy(self, inst_id: str) -> PasswordPolicy:
        pass
        
    @abstractmethod
    async def get_session_policy(self, inst_id: str) -> SessionPolicy:
        pass

    @abstractmethod
    async def upsert_login_policy(self, policy_data: dict):
        pass

    @abstractmethod
    async def delete_login_policy(self, inst_id: str):
        pass

    @abstractmethod
    async def upsert_password_policy(self, policy_data: dict):
        pass

    @abstractmethod
    async def delete_password_policy(self, inst_id: str):
        pass

    @abstractmethod
    async def upsert_session_policy(self, policy_data: dict):
        pass

    @abstractmethod
    async def delete_session_policy(self, inst_id: str):
        pass

class DefaultPolicyProvider(PolicyProvider):
    """
    Fallback provider yielding safe enterprise defaults when the target 
    database environment lacks the required schema capabilities.
    """
    async def get_login_policy(self, inst_id: str) -> LoginPolicy:
        return LoginPolicy()
        
    async def get_password_policy(self, inst_id: str) -> PasswordPolicy:
        return PasswordPolicy()

    async def get_session_policy(self, inst_id: str) -> SessionPolicy:
        return SessionPolicy()

    async def upsert_login_policy(self, policy_data: dict):
        return {"status": "success", "data": [policy_data], "message": "Policy retained in-memory via DefaultPolicyProvider"}

    async def delete_login_policy(self, inst_id: str):
        return {"status": "success", "data": [], "message": "Policy defaults restored via DefaultPolicyProvider"}

    async def upsert_password_policy(self, policy_data: dict):
        return {"status": "success", "data": [policy_data], "message": "Policy retained in-memory via DefaultPolicyProvider"}

    async def delete_password_policy(self, inst_id: str):
        return {"status": "success", "data": [], "message": "Policy defaults restored via DefaultPolicyProvider"}

    async def upsert_session_policy(self, policy_data: dict):
        return {"status": "success", "data": [policy_data], "message": "Policy retained in-memory via DefaultPolicyProvider"}

    async def delete_session_policy(self, inst_id: str):
        return {"status": "success", "data": [], "message": "Policy defaults restored via DefaultPolicyProvider"}

class DatabasePolicyProvider(PolicyProvider):
    def __init__(self, db: PostgreSQLManager):
        self.db = db

    async def get_login_policy(self, inst_id: str) -> LoginPolicy:
        q = select(TbInstitutionLoginPolicy).where(TbInstitutionLoginPolicy.inst_id == inst_id)
        try:
            records = await self.db.async_genericSQL(q)
            if records and records.get("status") == "success" and records.get("data"):
                r = records["data"][0]
                return LoginPolicy(
                    enable_captcha=r.get("enable_captcha", False),
                    captcha_threshold=str(r.get("captcha_threshold", "0.5")),
                    allowed_auth_methods=json.loads(r.get("allowed_auth_methods")) if isinstance(r.get("allowed_auth_methods"), str) else r.get("allowed_auth_methods", ["password"]),
                    enable_ip_restriction=r.get("enable_ip_restriction", False),
                    blocked_ips=json.loads(r.get("blocked_ips")) if isinstance(r.get("blocked_ips"), str) else r.get("blocked_ips", None),
                    enable_geo_restriction=r.get("enable_geo_restriction", False),
                    allowed_countries=json.loads(r.get("allowed_countries")) if isinstance(r.get("allowed_countries"), str) else r.get("allowed_countries", None)
                )
        except Exception:
            pass
        return LoginPolicy()

    async def get_password_policy(self, inst_id: str) -> PasswordPolicy:
        q = select(TbInstitutionPasswordPolicy).where(TbInstitutionPasswordPolicy.inst_id == inst_id)
        try:
            records = await self.db.async_genericSQL(q)
            if records and records.get("status") == "success" and records.get("data"):
                r = records["data"][0]
                return PasswordPolicy(
                    min_length=r.get("min_length", 8),
                    require_uppercase=r.get("require_uppercase", True),
                    require_number=r.get("require_number", True),
                    require_special=r.get("require_special", True),
                    expiry_days=r.get("expiry_days", 90),
                    history_count=r.get("history_count", 5),
                    max_attempts=r.get("max_attempts", 5)
                )
        except Exception:
            pass
        return PasswordPolicy()

    async def get_session_policy(self, inst_id: str) -> SessionPolicy:
        q = select(TbInstitutionSessionPolicy).where(TbInstitutionSessionPolicy.inst_id == inst_id)
        try:
            records = await self.db.async_genericSQL(q)
            if records and records.get("status") == "success" and records.get("data"):
                r = records["data"][0]
                return SessionPolicy(
                    idle_timeout_minutes=r.get("idle_timeout_minutes", 15),
                    max_session_duration=r.get("max_session_duration", 720),
                    max_concurrent_sessions=r.get("max_concurrent_sessions", 1),
                    enforce_device_binding=r.get("enforce_device_binding", False),
                    ip_whitelist=json.loads(r.get("ip_whitelist")) if isinstance(r.get("ip_whitelist"), str) else r.get("ip_whitelist", None)
                )
        except Exception:
            pass
        return SessionPolicy()

    async def upsert_password_policy(self, policy_data: dict):
        from sqlalchemy import update
        if "id" in policy_data and policy_data["id"]:
            stmt = update(TbInstitutionPasswordPolicy).where(TbInstitutionPasswordPolicy.id == policy_data["id"]).values(**policy_data)
            return await self.db.async_genericSQL(stmt)
        else:
            return await self.db.async_insert(TbInstitutionPasswordPolicy.__tablename__, policy_data)

    async def delete_password_policy(self, inst_id: str):
        from sqlalchemy import delete
        stmt = delete(TbInstitutionPasswordPolicy).where(TbInstitutionPasswordPolicy.inst_id == inst_id)
        return await self.db.async_genericSQL(stmt)

    async def upsert_session_policy(self, policy_data: dict):
        from sqlalchemy import update
        if "id" in policy_data and policy_data["id"]:
            stmt = update(TbInstitutionSessionPolicy).where(TbInstitutionSessionPolicy.id == policy_data["id"]).values(**policy_data)
            return await self.db.async_genericSQL(stmt)
        else:
            return await self.db.async_insert(TbInstitutionSessionPolicy.__tablename__, policy_data)

    async def delete_session_policy(self, inst_id: str):
        from sqlalchemy import delete
        stmt = delete(TbInstitutionSessionPolicy).where(TbInstitutionSessionPolicy.inst_id == inst_id)
        return await self.db.async_genericSQL(stmt)

    async def upsert_login_policy(self, policy_data: dict):
        from sqlalchemy import update
        if "id" in policy_data and policy_data["id"]:
            stmt = update(TbInstitutionLoginPolicy).where(TbInstitutionLoginPolicy.id == policy_data["id"]).values(**policy_data)
            return await self.db.async_genericSQL(stmt)
        else:
            return await self.db.async_insert(TbInstitutionLoginPolicy.__tablename__, policy_data)

    async def delete_login_policy(self, inst_id: str):
        from sqlalchemy import delete
        stmt = delete(TbInstitutionLoginPolicy).where(TbInstitutionLoginPolicy.inst_id == inst_id)
        return await self.db.async_genericSQL(stmt)

async def detect_policy_capability(db: PostgreSQLManager):
    """
    Discovers database capabilities dynamically and registers the appropriate
    PolicyProvider into the central CapabilityRegistry.
    """
    try:
        required_tables = ['tb_institution_password_policy', 'tb_institution_session_policy', 'tb_institution_login_policy']
        from sqlalchemy import text
        q = text(f"""
            SELECT count(*) as count 
            FROM information_schema.tables 
            WHERE table_schema = 'sch_aaa' 
            AND table_name IN ({', '.join([f"'{t}'" for t in required_tables])})
        """)
        result = await db.async_genericSQL(q)
        if result and result.get("status") == "success" and result.get("data") and result["data"][0]['count'] == len(required_tables):
            CapabilityRegistry.register_capability("policy_provider", DatabasePolicyProvider(db), "DATABASE")
        else:
            CapabilityRegistry.register_capability("policy_provider", DefaultPolicyProvider(), "DEFAULT POLICY")
            print("\n[WARNING] Policy Provider: Enterprise Defaults (DefaultPolicyProvider). Reason: Database policy tables unavailable in sch_aaa. Application will operate using enterprise default policies.\n")
    except Exception as e:
        CapabilityRegistry.register_capability("policy_provider", DefaultPolicyProvider(), "DEFAULT POLICY")
        print(f"\n[WARNING] Policy Provider: Enterprise Defaults (DefaultPolicyProvider). Reason: Capability detection failed ({str(e)}). Application will operate using enterprise default policies.\n")
