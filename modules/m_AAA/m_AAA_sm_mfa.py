from sqlalchemy import select, insert, update
import datetime
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from xsc_lib.xsc_lib_app.xsc_liba_capability import CapabilityRegistry
from modules.m_AAA.m_AAA_data import AAADataLayer
from modules.m_AAA.db_init import TbMfaMethod, TbMfaChallenge, TbMfaBackupCode, TbAuthLog

class sm_mfa:
    @staticmethod
    async def mfa_add(request, context):
        db_layer = AAADataLayer(context.postgres)
        user_id = context.security.user_id if context.security else None
        
        if not user_id:
            return XSCUtility.error_response("Unauthorized", error_code="401")
            
        provider = CapabilityRegistry.get_capability("mfa_provider")
        if not provider:
            return XSCUtility.error_response("MFA subsystem is not configured", error_code="500")
            
        policy_provider = CapabilityRegistry.get_capability("policy_provider")
        inst_id = context.security.institution_id if context.security else None
        login_policy = await policy_provider.get_login_policy(inst_id) if policy_provider else None
        
        payload = request.payload or {}
        
        # Branch 1: VERIFICATION of an existing pending enrollment challenge
        if "enrollmentChallengeId" in payload and "response" in payload:
            return await sm_mfa.verify_enrollment(request, context, payload, provider, db_layer, user_id)
            
        # Branch 2: INITIATION of a new MFA enrollment
        return await sm_mfa.initiate_enrollment(request, context, provider, db_layer, user_id, login_policy)

    @staticmethod
    async def initiate_enrollment(request, context, provider, db_layer, user_id, login_policy):
        challenge = provider.create_enrollment_challenge(username=user_id, issuer_name="OneApp")
        
        backup_code_count = getattr(login_policy, 'backup_code_count', 10)
        backup_code_length = getattr(login_policy, 'backup_code_length', 8)
        
        plaintext_codes = provider.generate_backup_codes(backup_code_count, backup_code_length)
        
        method_id = XSCUtility.generate_uuid()
        challenge_id = XSCUtility.generate_uuid()
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Policy driven expiry (fallback to 15 mins)
        expiry_minutes = getattr(login_policy, 'enrollment_challenge_expiry_minutes', 15)
        expiry = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=expiry_minutes)).isoformat()
        
        queries = []
        queries.append((
            insert(TbMfaMethod).values(
                id=method_id,
                user_id=user_id,
                mfa_type_id=f"LOOKUP_MFA_{provider.provider_id.upper()}",
                secret_key=challenge["secret"],
                is_primary="false",
                is_verified="false",
                is_active="false",
                created_at=now,
                created_by=user_id
            ),
            None
        ))
        
        queries.append((
            insert(TbMfaChallenge).values(
                id=challenge_id,
                user_id=user_id,
                session_id=context.security.session_id if context.security else "no_session",
                mfa_method_id=method_id,
                challenge_token=challenge["secret"],
                issued_at=now,
                expires_at=expiry,
                status_id="LOOKUP_CHALLENGE_ENROLLMENT"
            ),
            None
        ))
        
        for code in plaintext_codes:
            code_hash = XSCUtility.generate_hash(code)
            queries.append((
                insert(TbMfaBackupCode).values(
                    id=XSCUtility.generate_uuid(),
                    mfa_method_id=method_id,
                    code_hash=code_hash,
                    is_used="false",
                    created_at=now,
                    created_by=user_id
                ),
                None
            ))
            
        queries.append((
            insert(TbAuthLog).values(
                id=XSCUtility.generate_uuid(),
                user_id=user_id,
                event_type_id="LOOKUP_AUTH_EVENT_MFA_ENROLLMENT_INITIATED",
                event_time=now,
                status="success",
                details="MFA Enrollment initiated."
            ),
            None
        ))
        
        tx_result = await db_layer.execute_transaction(queries)
        if tx_result["status"] != "success":
            return XSCUtility.error_response("Failed to initiate MFA enrollment")
            
        return XSCUtility.success_response("MFA enrollment initiated", {
            "mfaType": provider.provider_id,
            "provisioningUri": challenge["provisioning_uri"],
            "backupCodes": plaintext_codes,
            "enrollmentChallengeId": challenge_id
        })

    @staticmethod
    async def verify_enrollment(request, context, payload, provider, db_layer, user_id):
        from modules.m_AAA.m_AAA_sm_auth import sm_auth
        if await sm_auth._check_account_lock(db_layer, user_id):
            return XSCUtility.error_response("Account temporarily locked due to multiple failed login attempts")

        challenge_id = payload.get("enrollmentChallengeId")
        response_code = payload.get("response")
        
        q = select(TbMfaChallenge, TbMfaMethod).join(TbMfaMethod, TbMfaChallenge.mfa_method_id == TbMfaMethod.id).where(
            TbMfaChallenge.id == challenge_id,
            TbMfaChallenge.user_id == user_id,
            TbMfaChallenge.status_id == "LOOKUP_CHALLENGE_ENROLLMENT"
        )
        records = await db_layer.db.async_genericSQL(q)
        if not records or records.get("status") != "success" or not records.get("data"):
            return XSCUtility.error_response("Invalid or expired enrollment challenge")
            
        row = records["data"][0]
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if row.get("expires_at") < now:
            return XSCUtility.error_response("Enrollment challenge expired")
            
        secret = row.get("secret_key")
        is_valid = provider.verify_enrollment_challenge(secret, response_code)
        
        queries = []
        if not is_valid:
            queries.append((
                insert(TbAuthLog).values(
                    id=XSCUtility.generate_uuid(), user_id=user_id, event_type_id="LOOKUP_AUTH_EVENT_MFA_ENROLLMENT_FAILED",
                    event_time=now, status="error", details="Invalid OTP during enrollment."
                ), None
            ))
            await db_layer.execute_transaction(queries)
            return XSCUtility.error_response("Invalid OTP provided")
            
        # Success: transition method to ACTIVE, challenge to VERIFIED
        queries.append((
            update(TbMfaMethod).where(TbMfaMethod.id == row.get("mfa_method_id")).values(
                is_verified="true", is_active="true", modified_at=now, modified_by=user_id
            ), None
        ))
        
        queries.append((
            update(TbMfaChallenge).where(TbMfaChallenge.id == challenge_id).values(
                status_id="LOOKUP_CHALLENGE_VERIFIED", verified_at=now
            ), None
        ))
        
        queries.append((
            insert(TbAuthLog).values(
                id=XSCUtility.generate_uuid(), user_id=user_id, event_type_id="LOOKUP_AUTH_EVENT_MFA_ENROLLMENT_SUCCESS",
                event_time=now, status="success", details="MFA Enrollment completed."
            ), None
        ))
        
        tx_result = await db_layer.execute_transaction(queries)
        if tx_result["status"] != "success":
            return XSCUtility.error_response("Transaction failed during enrollment verification")
            
        # TODO: Implement MFA Verification Notification
        # Ownership: m_Communication
        # Status: Deferred
        # Reason: CommunicationManager is not yet available in the platform baseline.
        # Blocking: No (MFA enrollment succeeds without notification).
        # Target Sprint: Platform Services Sprint
        
        return XSCUtility.success_response("MFA method verified and activated successfully")

    @staticmethod
    async def mfa_view(request, context):
        db_layer = AAADataLayer(context.postgres)
        user_id = context.security.user_id if context.security else None
        if not user_id: return XSCUtility.error_response("Unauthorized", error_code="401")
        
        q = select(TbMfaMethod.id, TbMfaMethod.mfa_type_id, TbMfaMethod.is_primary, TbMfaMethod.is_active).where(
            TbMfaMethod.user_id == user_id,
            TbMfaMethod.is_active == "true"
        )
        res = await db_layer.db.async_genericSQL(q)
        
        return XSCUtility.success_response("MFA methods retrieved successfully", res.get("data", []))

    @staticmethod
    async def mfa_update(request, context):
        db_layer = AAADataLayer(context.postgres)
        user_id = context.security.user_id if context.security else None
        payload = request.payload or {}
        method_id = payload.get("method_id")
        
        if not user_id or not method_id:
            return XSCUtility.error_response("Unauthorized or Missing method_id", error_code="401")
            
        action = payload.get("action", "set_primary")
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        if action == "regenerate_backup_codes":
            q = select(TbMfaMethod).where(TbMfaMethod.id == method_id, TbMfaMethod.user_id == user_id, TbMfaMethod.is_active == "true")
            res = await db_layer.db.async_genericSQL(q)
            if not res or not res.get("data"):
                return XSCUtility.error_response("Method not found or not active")
                
            provider = CapabilityRegistry.get_capability("mfa_provider")
            policy_provider = CapabilityRegistry.get_capability("policy_provider")
            inst_id = context.security.institution_id if context.security else None
            login_policy = await policy_provider.get_login_policy(inst_id) if policy_provider else None
            
            count = getattr(login_policy, 'backup_code_count', 10)
            length = getattr(login_policy, 'backup_code_length', 8)
            plaintext_codes = provider.generate_backup_codes(count, length)
            
            from sqlalchemy import delete
            queries = [
                (delete(TbMfaBackupCode).where(TbMfaBackupCode.mfa_method_id == method_id), None)
            ]
            
            for code in plaintext_codes:
                code_hash = XSCUtility.generate_hash(code)
                queries.append((
                    insert(TbMfaBackupCode).values(
                        id=XSCUtility.generate_uuid(), mfa_method_id=method_id,
                        code_hash=code_hash, is_used="false", created_at=now, created_by=user_id
                    ), None
                ))
            
            queries.append((insert(TbAuthLog).values(
                id=XSCUtility.generate_uuid(), user_id=user_id, event_type_id="LOOKUP_AUTH_EVENT_MFA_BACKUP_CODES_REGENERATED",
                event_time=now, status="success", details="MFA Backup codes regenerated."
            ), None))
            
            tx = await db_layer.execute_transaction(queries)
            if tx["status"] == "success":
                return XSCUtility.success_response("Backup codes regenerated successfully", {"backupCodes": plaintext_codes})
            return XSCUtility.error_response("Failed to regenerate backup codes")

        # Default action: set_primary
        queries = [
            (update(TbMfaMethod).where(TbMfaMethod.user_id == user_id).values(is_primary="false"), None),
            (update(TbMfaMethod).where(TbMfaMethod.id == method_id, TbMfaMethod.user_id == user_id).values(is_primary="true"), None),
            (insert(TbAuthLog).values(
                id=XSCUtility.generate_uuid(), user_id=user_id, event_type_id="LOOKUP_AUTH_EVENT_MFA_PRIMARY_UPDATED",
                event_time=now, status="success", details="MFA Primary method updated."
            ), None)
        ]
        
        tx = await db_layer.execute_transaction(queries)
        if tx["status"] == "success":
            return XSCUtility.success_response("MFA primary method updated successfully")
        return XSCUtility.error_response("Failed to update primary method")

    @staticmethod
    async def mfa_delete(request, context):
        db_layer = AAADataLayer(context.postgres)
        user_id = context.security.user_id if context.security else None
        payload = request.payload or {}
        method_id = payload.get("method_id")
        
        if not user_id or not method_id:
            return XSCUtility.error_response("Unauthorized or missing method_id", error_code="401")
            
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Check if it was primary
        q = select(TbMfaMethod).where(TbMfaMethod.id == method_id, TbMfaMethod.user_id == user_id)
        res = await db_layer.db.async_genericSQL(q)
        is_primary = False
        if res and res.get("data"):
            is_primary = res["data"][0].get("is_primary") == "true"

        queries = [
            (update(TbMfaMethod).where(TbMfaMethod.id == method_id, TbMfaMethod.user_id == user_id).values(
                is_active="false", is_verified="false", is_primary="false"
            ), None)
        ]
        
        if is_primary:
            # Fallback to the oldest active verified method
            fallback_q = select(TbMfaMethod.id).where(
                TbMfaMethod.user_id == user_id, 
                TbMfaMethod.is_active == "true", 
                TbMfaMethod.id != method_id
            ).order_by(TbMfaMethod.created_at.asc()).limit(1)
            fallback_res = await db_layer.db.async_genericSQL(fallback_q)
            if fallback_res and fallback_res.get("data"):
                fallback_id = fallback_res["data"][0].get("id")
                queries.append((update(TbMfaMethod).where(TbMfaMethod.id == fallback_id).values(is_primary="true"), None))
        
        queries.append((insert(TbAuthLog).values(
            id=XSCUtility.generate_uuid(), user_id=user_id, event_type_id="LOOKUP_AUTH_EVENT_MFA_DELETED",
            event_time=now, status="success", details="MFA Method deleted/revoked."
        ), None))
        
        tx = await db_layer.execute_transaction(queries)
        if tx["status"] == "success":
            return XSCUtility.success_response("MFA method deleted successfully")
        return XSCUtility.error_response("Failed to delete MFA method")

    @staticmethod
    async def verify_login_challenge(payload, context, db_layer):
        challenge_token = payload.get("challengeToken")
        response_code = payload.get("response")
        
        q = select(TbMfaChallenge, TbMfaMethod).join(TbMfaMethod, TbMfaChallenge.mfa_method_id == TbMfaMethod.id).where(
            TbMfaChallenge.challenge_token == challenge_token,
            TbMfaChallenge.status_id == "LOOKUP_CHALLENGE_AUTH"
        )
        records = await db_layer.db.async_genericSQL(q)
        if not records or records.get("status") != "success" or not records.get("data"):
            return XSCUtility.error_response("Invalid or expired authentication challenge", error_code="401")
            
        row = records["data"][0]
        user_id = row.get("user_id")
        method_id = row.get("mfa_method_id")
        challenge_id = row.get("id")
        
        from modules.m_AAA.m_AAA_sm_auth import sm_auth
        if await sm_auth._check_account_lock(db_layer, user_id):
            return XSCUtility.error_response("Account temporarily locked due to multiple failed login attempts")

        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if row.get("expires_at") < now:
            return XSCUtility.error_response("Authentication challenge expired", error_code="401")
            
        # Check backup code first
        code_hash = XSCUtility.generate_hash(response_code)
        backup_q = select(TbMfaBackupCode).where(
            TbMfaBackupCode.mfa_method_id == method_id,
            TbMfaBackupCode.code_hash == code_hash,
            TbMfaBackupCode.is_used == "false"
        )
        backup_res = await db_layer.db.async_genericSQL(backup_q)
        
        queries = []
        is_valid = False
        if backup_res and backup_res.get("data"):
            is_valid = True
            backup_id = backup_res["data"][0].get("id")
            queries.append((update(TbMfaBackupCode).where(TbMfaBackupCode.id == backup_id).values(
                is_used="true", used_at=now
            ), None))
        else:
            provider = CapabilityRegistry.get_capability("mfa_provider")
            if not provider:
                return XSCUtility.error_response("MFA Provider unavailable", error_code="500")
            secret = row.get("secret_key")
            is_valid = provider.verify_authentication_challenge(secret, response_code)
            
        if not is_valid:
            queries.append((insert(TbAuthLog).values(
                id=XSCUtility.generate_uuid(), user_id=user_id, event_type_id="LOOKUP_AUTH_EVENT_MFA_AUTH_FAILED",
                event_time=now, status="error", details="Invalid OTP or backup code."
            ), None))
            # Optional: increment failure count & lockout if threshold exceeded
            await db_layer.execute_transaction(queries)
            return XSCUtility.error_response("Invalid code", error_code="401")
            
        queries.append((update(TbMfaChallenge).where(TbMfaChallenge.id == challenge_id).values(
            status_id="LOOKUP_CHALLENGE_VERIFIED", verified_at=now
        ), None))
        
        queries.append((insert(TbAuthLog).values(
            id=XSCUtility.generate_uuid(), user_id=user_id, event_type_id="LOOKUP_AUTH_EVENT_MFA_AUTH_SUCCESS",
            event_time=now, status="success", details="MFA Authentication completed."
        ), None))
        
        tx = await db_layer.execute_transaction(queries)
        if tx["status"] != "success":
            return XSCUtility.error_response("Database transaction failed", error_code="500")
            
        return {"status": "success", "user_id": user_id}
