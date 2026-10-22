"""
File: m_AAA_data.py
Description: Data Access Layer for m_AAA.

Author: Siddharth Amdal
App: OneApp

"""

from sqlalchemy import select, update, delete, insert, text, table, column, String, Integer, BigInteger
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from .db_init import (
    TbAuthLog, TbPasswordReset, TbMfaMethod, TbMfaChallenge, TbAccountLock,
    TbInstitutionPasswordPolicy, TbInstitutionSessionPolicy, TbInstitutionLoginPolicy,
    TbRole, TbPermission, TbOrgRole, TbRolePermission, TbUserOrg, TbUserRole,
    TbUserPasswordState, TbUserSession
)

tb_user_core = table('tb_user',
    column('id', BigInteger),
    column('email', String),
    column('password_salt', String),
    column('password_hash', String),
    column('status_id', Integer),
    schema='sch_iam'
)

class AAADataLayer:
    """
    Lightweight module-local Data Access layer that consumes the injected context.postgres.
    This keeps business logic readable while maintaining module isolation.
    """

    def __init__(self, db):
        self.db = db

    async def execute_transaction(self, queries: list):
        """
        Executes a list of (stmt, params) tuples within a single transaction.
        Automatically issues BEGIN and COMMIT/ROLLBACK.
        """
        if not self.db.async_engine:
            return {"status": "error", "message": "Database not initialized"}
        
        try:
            async with self.db.async_engine.begin() as conn:
                for query, params in queries:
                    if isinstance(query, str):
                        await conn.exec_driver_sql(query, params)
                    else:
                        await conn.execute(query, params or {})
                return {"status": "success", "message": "Transaction committed"}
        except Exception as e:
            return {"status": "error", "message": f"Transaction failed: {str(e)}"}

    async def get_auth_logs(self, user_id=None):
        """
        Retrieves auth logs, optionally filtered by user_id.
        """
        stmt = select(TbAuthLog)
        if user_id:
            stmt = stmt.where(TbAuthLog.user_id == user_id)

        return await self.db.async_genericSQL(stmt)

    async def create_auth_log(self, log_data: dict):
        """
        Creates a new auth log entry.
        """
        return await self.db.async_insert(TbAuthLog.__tablename__, log_data)

    async def get_mfa_methods(self, user_id: str):
        """
        Retrieves MFA methods for a given user.
        """
        stmt = select(TbMfaMethod).where(
            TbMfaMethod.user_id == user_id, TbMfaMethod.is_active == "true"
        )
        return await self.db.async_genericSQL(stmt)

    async def create_mfa_challenge(self, challenge_data: dict):
        """
        Creates a new MFA challenge.
        """
        return await self.db.async_insert(TbMfaChallenge.__tablename__, challenge_data)

    async def get_mfa_challenge(self, challenge_token: str):
        """
        Retrieves a specific MFA challenge.
        """
        stmt = select(TbMfaChallenge).where(
            TbMfaChallenge.challenge_token == challenge_token
        )
        return await self.db.async_genericSQL(stmt)

    async def get_account_locks(self, user_id: str):
        """
        Retrieves account locks for a given user.
        """
        stmt = select(TbAccountLock).where(TbAccountLock.user_id == user_id)
        return await self.db.async_genericSQL(stmt)

    async def get_password_reset_token(self, token: str):
        """
        Retrieves a password reset token.
        """
        stmt = select(
            TbPasswordReset.id, TbPasswordReset.user_id, TbPasswordReset.reset_token,
            TbPasswordReset.expires_at, TbPasswordReset.used_at
        ).where(TbPasswordReset.reset_token == token, TbPasswordReset.used_at.is_(None))
        return await self.db.async_genericSQL(stmt)

    async def create_password_reset_token(self, token_data: dict):
        """
        Creates a new password reset token.
        """
        stmt = insert(TbPasswordReset).values(**token_data).returning(TbPasswordReset.id)
        return await self.db.async_genericSQL(stmt)
        
    async def consume_password_reset_token(self, token: str, used_at):
        """
        Marks a password reset token as used.
        """
        stmt = update(TbPasswordReset).where(TbPasswordReset.reset_token == token).values(used_at=used_at)
        return await self.db.async_genericSQL(stmt)

    async def revoke_password_reset_token(self, token: str, revoked_at):
        try:
            query = update(TbPasswordReset).where(
                TbPasswordReset.reset_token == token, TbPasswordReset.used_at.is_(None)
            ).values(status_id=0, used_at=revoked_at)
            await self.execute_transaction([(query, None)])
            return {"status": "success", "message": "Token revoked successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def update_user_password(self, user_id: int, password_hash: str):
        """
        Updates a user's password hash in the database.
        """
        stmt = update(tb_user_core).where(tb_user_core.c.id == user_id).values(password_hash=password_hash)
        return await self.db.async_genericSQL(stmt)

    async def get_user_password_hash(self, user_id: str):
        """
        Retrieves the stored password hash for a given user_id.
        Used by password:update to verify the current password before allowing a change.
        
        Args:
            user_id (str): The ID of the user.
            
        Returns:
            dict: Result containing id and password_hash columns.
        """
        stmt = select(tb_user_core.c.id, tb_user_core.c.password_hash).where(tb_user_core.c.id == user_id)
        return await self.db.async_genericSQL(stmt)

    async def get_user_password_state(self, user_id: str):
        """
        Retrieves the password state for a given user_id.
        """
        stmt = select(TbUserPasswordState).where(TbUserPasswordState.user_id == user_id)
        return await self.db.async_genericSQL(stmt)

    async def update_user_password_state(self, state_data: dict):
        """
        Upserts the user password state.
        """
        import uuid
        from datetime import datetime, timezone
        
        # Check if it exists
        existing = await self.get_user_password_state(state_data['user_id'])
        if existing and existing.get('status') == 'success' and existing.get('data'):
            stmt = update(TbUserPasswordState).where(TbUserPasswordState.user_id == state_data['user_id']).values(
                is_expired=state_data.get('is_expired', False),
                expired_at=state_data.get('expired_at'),
                updated_at=datetime.now(timezone.utc)
            )
            return await self.db.async_genericSQL(stmt)
        else:
            state_data['id'] = str(uuid.uuid4())
            state_data['created_at'] = datetime.now(timezone.utc)
            state_data['updated_at'] = datetime.now(timezone.utc)
            return await self.db.async_insert(TbUserPasswordState.__tablename__, state_data)

    async def get_active_sessions_for_user(self, user_id: int):
        """
        Returns all ACTIVE sessions for a given user_id.
        Used during login (session:add) to detect concurrent active sessions.
        """
        stmt = select(TbUserSession.id).where(TbUserSession.user_id == user_id, TbUserSession.status_id == 1)
        return await self.db.async_genericSQL(stmt)

    async def create_user_session(self, session_data: dict):
        """
        Creates a new user session in sch_iam.tb_user_session.
        """
        # Ensure status_id is set
        if 'status_id' not in session_data:
            session_data['status_id'] = 1
            
        stmt = insert(TbUserSession).values(**session_data).returning(TbUserSession.id)
        return await self.db.async_genericSQL(stmt)

    async def get_user_by_email(self, email: str):
        """
        Retrieves a user by email from sch_iam.tb_user for authentication.
        """
        stmt = select(
            tb_user_core.c.id, tb_user_core.c.email, tb_user_core.c.password_salt, 
            tb_user_core.c.password_hash, tb_user_core.c.status_id
        ).where(tb_user_core.c.email == email)
        return await self.db.async_genericSQL(stmt)

    async def get_user_auth_context(self, user_id: int):
        """
        Retrieves org, roles, and permissions for the authenticated user to populate the JWT.
        """
        # Fetch the org and institution
        org_stmt = text("""
            SELECT uo.org_id, o.org_alias, i.id as institution_id
            FROM sch_rbac.tb_user_org uo
            JOIN sch_org.tb_org o ON o.id = uo.org_id
            LEFT JOIN sch_org.tb_inst i ON i.org_id = o.id
            WHERE uo.user_id = :uid AND uo.status_id = 1
        """)
        org_resp = await self.db.async_genericSQL(org_stmt, {"uid": user_id})

        # Fetch roles
        role_stmt = text("""
            SELECT r.role_code
            FROM sch_rbac.tb_user_role ur
            JOIN sch_rbac.tb_org_role or_role ON or_role.id = ur.org_role_id
            JOIN sch_iam.tb_role r ON r.id = or_role.role_id
            JOIN sch_rbac.tb_user_org uo ON uo.id = ur.user_org_id
            WHERE uo.user_id = :uid AND ur.status_id = 1
        """)
        role_resp = await self.db.async_genericSQL(role_stmt, {"uid": user_id})

        # Fetch permissions
        perm_stmt = text("""
            SELECT p.permission_code
            FROM sch_rbac.tb_user_role ur
            JOIN sch_rbac.tb_org_role or_role ON or_role.id = ur.org_role_id
            JOIN sch_rbac.tb_role_permission rp ON rp.role_id = or_role.role_id
            JOIN sch_rbac.tb_permission p ON p.id = rp.permission_id
            JOIN sch_rbac.tb_user_org uo ON uo.id = ur.user_org_id
            WHERE uo.user_id = :uid AND ur.status_id = 1
        """)
        perm_resp = await self.db.async_genericSQL(perm_stmt, {"uid": user_id})

        return {
            "orgs": org_resp.get("data", []) if org_resp["status"] == "success" else [],
            "roles": (
                [r["role_code"] for r in role_resp.get("data", [])]
                if role_resp["status"] == "success"
                else []
            ),
            "permissions": (
                [p["permission_code"] for p in perm_resp.get("data", [])]
                if perm_resp["status"] == "success"
                else []
            ),
        }

    async def resolve_user_permissions(self, user_id: int) -> list:
        """
        Resolves the full list of internal permission codes that the authenticated user is allowed to access.
        This performs the complex resolution of User -> Roles -> Role-Permission Mappings -> Deduplication.
        """
        perm_stmt = text("""
            SELECT DISTINCT p.permission_code
            FROM sch_rbac.tb_user_role ur
            JOIN sch_rbac.tb_org_role or_role ON or_role.id = ur.org_role_id
            JOIN sch_rbac.tb_role_permission rp ON rp.role_id = or_role.role_id
            JOIN sch_rbac.tb_permission p ON p.id = rp.permission_id
            JOIN sch_rbac.tb_user_org uo ON uo.id = ur.user_org_id
            WHERE uo.user_id = :uid AND ur.status_id = 1
        """)
        perm_resp = await self.db.async_genericSQL(perm_stmt, {"uid": user_id})

        if perm_resp["status"] == "success":
            return [p["permission_code"] for p in perm_resp.get("data", [])]
        return []

    async def get_user_identity_context(self, user_id: int) -> dict:
        """
        Retrieves basic identity context for the API response.
        """
        stmt = text(
            "SELECT id, first_name, last_name, email FROM sch_iam.tb_user WHERE id = :uid"
        )
        resp = await self.db.async_genericSQL(stmt, {"uid": user_id})

        user_context = {"id": user_id, "name": "Unknown User", "roles": []}

        if resp["status"] == "success" and resp["data"]:
            user = resp["data"][0]
            name_parts = [
                p for p in [user.get("first_name"), user.get("last_name")] if p
            ]
            if name_parts:
                user_context["name"] = " ".join(name_parts)
            else:
                user_context["name"] = user.get("email", "Unknown User")

        # Get roles for context
        role_stmt = text("""
            SELECT r.role_code
            FROM sch_rbac.tb_user_role ur
            JOIN sch_rbac.tb_org_role or_role ON or_role.id = ur.org_role_id
            JOIN sch_iam.tb_role r ON r.id = or_role.role_id
            JOIN sch_rbac.tb_user_org uo ON uo.id = ur.user_org_id
            WHERE uo.user_id = :uid AND ur.status_id = 1
        """)
        role_resp = await self.db.async_genericSQL(role_stmt, {"uid": user_id})
        if role_resp["status"] == "success":
            user_context["roles"] = [r["role_code"] for r in role_resp.get("data", [])]

        return user_context

    # --- Session Operations ---
    async def execute_password_reset(self, user_id: str, password_hash: str, token: str, used_at):
        """
        Executes password reset, invalidates token, and revokes sessions in a single transaction.
        """
        queries = [
            (
                update(tb_user_core).where(tb_user_core.c.id == user_id).values(password_hash=password_hash),
                None
            ),
            (
                update(TbPasswordReset).where(TbPasswordReset.reset_token == token).values(status_id=0, used_at=used_at),
                None
            ),
            (
                update(TbUserSession).where(TbUserSession.user_id == user_id, TbUserSession.status_id == 1).values(status_id=0),
                None
            )
        ]
        return await self.execute_transaction(queries)

    async def invalidate_all_active_sessions(self, user_id: str):
        """
        Invalidates all active sessions for a user (e.g. after password reset).
        Uses sch_iam.tb_user_session.
        """
        stmt = update(TbUserSession).where(TbUserSession.user_id == user_id, TbUserSession.status_id == 1).values(status_id=0)
        return await self.db.async_genericSQL(stmt)


    # --- Policy Operations ---
    # Policy operations have been migrated to the PolicyProvider subsystem.

    # --- RBAC Operations ---

    async def create_role(self, role_data: dict):
        stmt = text("""
            INSERT INTO sch_iam.tb_role (id, role_code, role_name, description, status_id)
            VALUES (:id, :role_code, :role_name, :description, :status_id)
        """)
        return await self.db.async_genericSQL(stmt, role_data)

    async def get_roles(self):
        stmt = text("SELECT id, role_code, role_name, description, status_id FROM sch_iam.tb_role")
        return await self.db.async_genericSQL(stmt)

    async def update_role(self, role_id: str, role_data: dict):
        stmt = text("""
            UPDATE sch_iam.tb_role
            SET role_name = :role_name, description = :description, status_id = :status_id
            WHERE id = :id
        """)
        role_data["id"] = role_id
        return await self.db.async_genericSQL(stmt, role_data)

    async def delete_role(self, role_id: str):
        # BR-05.1: Block Delete if Active Users (checked via tb_org_role usage)
        check_stmt = text("""
            SELECT count(ur.id) as active_users
            FROM sch_rbac.tb_user_role ur
            JOIN sch_rbac.tb_org_role org ON ur.org_role_id = org.id
            WHERE org.role_id = :role_id
        """)
        check_result = await self.db.async_genericSQL(check_stmt, {"role_id": role_id})
        if check_result["status"] == "success" and check_result["data"]:
            if check_result["data"][0]["active_users"] > 0:
                return {"status": "error", "message": "Cannot delete role: active user assignments exist"}

        stmt = text("DELETE FROM sch_iam.tb_role WHERE id = :id")
        return await self.db.async_genericSQL(stmt, {"id": role_id})

    async def create_permission(self, permission_data: dict):
        stmt = text("""
            INSERT INTO sch_rbac.tb_permission (id, permission_code, description)
            VALUES (:id, :permission_code, :description)
        """)
        return await self.db.async_genericSQL(stmt, permission_data)

    async def get_permissions(self):
        stmt = text("SELECT id, permission_code, description FROM sch_rbac.tb_permission")
        return await self.db.async_genericSQL(stmt)

    async def update_permission(self, permission_id: str, permission_data: dict):
        stmt = text("""
            UPDATE sch_rbac.tb_permission
            SET description = :description, permission_code = :permission_code
            WHERE id = :id
        """)
        permission_data["id"] = permission_id
        return await self.db.async_genericSQL(stmt, permission_data)

    async def delete_permission(self, permission_id: str):
        stmt = text("DELETE FROM sch_rbac.tb_permission WHERE id = :id")
        return await self.db.async_genericSQL(stmt, {"id": permission_id})

    async def assign_role(self, user_org_id: str, org_role_id: str, id: str):
        stmt = text("""
            INSERT INTO sch_rbac.tb_user_role (id, user_org_id, org_role_id, status_id)
            VALUES (:id, :user_org_id, :org_role_id, 1)
        """)
        return await self.db.async_genericSQL(stmt, {"id": id, "user_org_id": user_org_id, "org_role_id": org_role_id})

    async def get_role_assignments(self, user_id: str):
        stmt = text("""
            SELECT ur.id as assignment_id, r.role_code, r.role_name, uo.org_id
            FROM sch_rbac.tb_user_role ur
            JOIN sch_rbac.tb_org_role or_role ON or_role.id = ur.org_role_id
            JOIN sch_iam.tb_role r ON r.id = or_role.role_id
            JOIN sch_rbac.tb_user_org uo ON uo.id = ur.user_org_id
            WHERE uo.user_id = :user_id AND ur.status_id = 1
        """)
        return await self.db.async_genericSQL(stmt, {"user_id": user_id})

    async def revoke_role(self, assignment_id: str):
        stmt = text("UPDATE sch_rbac.tb_user_role SET status_id = 0 WHERE id = :id")
        return await self.db.async_genericSQL(stmt, {"id": assignment_id})

    async def get_accessible_modules(self, permissions: list):
        if not permissions:
            return {"status": "success", "data": []}
            
        # Dynamically build placeholders for the IN clause
        placeholders = {f"p_{i}": p for i, p in enumerate(permissions)}
        in_clause = ", ".join(f":{k}" for k in placeholders.keys())
        
        stmt = text(f"""
            SELECT module_name as "module", display_name as "displayName", icon, route, status, enabled
            FROM sch_rbac.tb_module
            WHERE permission_code IN ({in_clause}) AND enabled = True
        """)
        return await self.db.async_genericSQL(stmt, placeholders)
