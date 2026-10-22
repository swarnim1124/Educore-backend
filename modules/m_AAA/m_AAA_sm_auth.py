"""
File: m_AAA_sm_auth.py
Description: Authentication and session management submodule for m_AAA.

Author: Siddharth Amdal
App: OneApp

"""

from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from .m_AAA_data import AAADataLayer
from .providers.policy_models import PasswordPolicy, SessionPolicy, LoginPolicy
from xsc_lib.xsc_lib_app.xsc_liba_capability import CapabilityRegistry

class sm_auth:
    @staticmethod
    async def session(request, context):
        """
        Executes the `session()` action to process the corresponding client request.

        Args:
            request: The OneAppRequest payload containing the module, submodule, action, actionType, and payload.
            context: The ExecutionContext containing request-scoped dependencies.
        """
        match request.actionType.lower():
            case "add": return await sm_auth.session_add(request, context)
            case "view": return await sm_auth.session_view(request, context)
            case "update": return await sm_auth.session_update(request, context)
            case "delete": return await sm_auth.session_delete(request, context)
            case _: return XSCUtility.error_response("Invalid actionType")

    @staticmethod
    async def _check_account_lock(db_layer, user_id):
        auth_logs_resp = await db_layer.get_auth_logs(user_id)
        if auth_logs_resp["status"] == "success" and auth_logs_resp.get("data"):
            recent_logs = auth_logs_resp["data"]
            failed_count = sum(1 for log in recent_logs[:5] if log.get("evt_status_id") == 2)
            if failed_count >= 5:
                return True
        return False

    @staticmethod
    async def session_add(request, context):
        db_layer = AAADataLayer(context.postgres)
        payload = request.payload or {}
        
        # 0. MFA Verification Branch
        if "challengeToken" in payload and "response" in payload:
            from modules.m_AAA.m_AAA_sm_mfa import sm_mfa
            mfa_res = await sm_mfa.verify_login_challenge(payload, context, db_layer)
            if mfa_res.get("status") != "success":
                return mfa_res
            user_id = mfa_res["user_id"]
            captcha_required = False
        else:
            # Standard Password Login Branch
            username = payload.get("username") or payload.get("email")
            password = payload.get("password")
            captcha_token = payload.get("captchaToken")
            
            if not username or not password:
                return XSCUtility.error_response("Username and password are required")
                
            user_resp = await db_layer.get_user_by_email(username)
            if user_resp["status"] == "error" or not user_resp["data"]:
                return XSCUtility.error_response("Invalid username or password")
                
            user_data = user_resp["data"][0]
            user_id = user_data["id"]
            
            pwd_state_resp = await db_layer.get_user_password_state(user_id)
            if pwd_state_resp["status"] == "success" and pwd_state_resp.get("data"):
                pwd_state = pwd_state_resp["data"][0]
                if pwd_state.get("is_expired") is True:
                    return XSCUtility.error_response("Password expired", error_code="PWD_EXPIRED")
                    
            auth_ctx = await db_layer.get_user_auth_context(user_id)
            inst_id = auth_ctx["orgs"][0]["institution_id"] if auth_ctx["orgs"] else None

            provider = CapabilityRegistry.get_capability("policy_provider")
            if not provider:
                return XSCUtility.error_response("Policy provider unavailable")
            login_policy = await provider.get_login_policy(inst_id)
            captcha_required = login_policy.enable_captcha
            
            if captcha_required:
                if not captcha_token:
                    return XSCUtility.error_response("CAPTCHA token is required", {"captchaRequired": True})
                from xsc_lib.xsc_lib_app.xsc_liba_captcha import get_captcha_provider
                captcha_provider = get_captcha_provider()
                is_captcha_valid = await captcha_provider.verify(captcha_token, action="login")
                if not is_captcha_valid:
                    return XSCUtility.error_response("Invalid CAPTCHA token")

            if await sm_auth._check_account_lock(db_layer, user_id):
                return XSCUtility.error_response("Account temporarily locked due to multiple failed login attempts")

            if not XSCUtility.compare_hash(password, user_data["password_hash"]):
                await db_layer.create_auth_log({
                    "id": XSCUtility.generate_uuid(), "user_id": user_id, "evt_type_id": 1, "evt_status_id": 2,
                    "failure_reason_id": 1, "evt_at": XSCUtility.get_current_timestamp()
                })
                return XSCUtility.error_response("Invalid username or password")

            if user_data.get("status_id") == 5:
                return XSCUtility.success_response("Password change required", {"userId": user_id, "forceChange": True}, status_code=206)

            # Check MFA
            mfa_resp = await db_layer.get_mfa_methods(user_id)
            if mfa_resp["status"] == "success" and mfa_resp["data"]:
                has_active = any(m.get("is_active") == "true" for m in mfa_resp["data"])
                if has_active:
                    import datetime
                    mfa_provider = CapabilityRegistry.get_capability("mfa_provider")
                    if not mfa_provider:
                        return XSCUtility.error_response("MFA Provider unavailable", error_code="500")
                    active_methods = [m for m in mfa_resp["data"] if m.get("is_active") == "true"]
                    primary_method = next((m for m in active_methods if m.get("is_primary") == "true"), active_methods[0])
                    
                    challenge_token = XSCUtility.generate_token(32)
                    expiry = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5)).isoformat()
                    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    
                    from sqlalchemy import insert
                    from modules.m_AAA.db_init import TbMfaChallenge
                    
                    queries = [(insert(TbMfaChallenge).values(
                        id=XSCUtility.generate_uuid(), user_id=user_id, session_id="pending",
                        mfa_method_id=primary_method["id"], challenge_token=challenge_token,
                        issued_at=now, expires_at=expiry, status_id="LOOKUP_CHALLENGE_AUTH"
                    ), None)]
                    await db_layer.execute_transaction(queries)
                    
                    # Notify logic goes here: communication_manager enqueue
                    
                    return XSCUtility.success_response(
                        "MFA Challenge Required", 
                        {"challengeToken": challenge_token, "mfaRequired": True},
                        status_code=206
                    )

        # JWT Issuance (Shared)
        auth_ctx = await db_layer.get_user_auth_context(user_id)
        org_id = auth_ctx["orgs"][0]["org_id"] if auth_ctx["orgs"] else None
        inst_id = auth_ctx["orgs"][0]["institution_id"] if auth_ctx["orgs"] else None
        
        provider = CapabilityRegistry.get_capability("policy_provider")
        session_policy = await provider.get_session_policy(inst_id) if provider else None
        max_concurrent = session_policy.max_concurrent_sessions if session_policy else 1
        max_duration = session_policy.max_session_duration if session_policy else 120

        active_sessions_resp = await db_layer.get_active_sessions_for_user(user_id)
        if active_sessions_resp["status"] == "success":
            active_sessions = active_sessions_resp["data"]
            if len(active_sessions) >= max_concurrent:
                await db_layer.invalidate_all_active_sessions(user_id)

        import xsc_conf.xsc_conf_config as config
        import jwt
        import datetime
        
        session_id = XSCUtility.generate_uuid()
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=max_duration)
        
        await db_layer.create_user_session({
            "id": session_id,
            "user_id": user_id,
            "user_agent": request.payload.get("userAgent", "Unknown"),
            "ip_address": request.payload.get("ipAddress", "0.0.0.0"),
            "expires_at": expires_at
        })

        jwt_payload = {
            "sub": str(user_id),
            "session_id": session_id,
            "org_id": org_id,
            "inst_id": inst_id,
            "exp": expires_at
        }

        jwt_token = jwt.encode(jwt_payload, config.JWT_SECRET, algorithm="HS256")

        await db_layer.create_auth_log({
            "id": XSCUtility.generate_uuid(),
            "user_id": user_id,
            "evt_type_id": 1,
            "evt_status_id": 1, 
            "evt_at": XSCUtility.get_current_timestamp()
        })

        return XSCUtility.success_response("Login successful", {"token": jwt_token, "captchaRequired": captcha_required, "sessionId": session_id})

    @staticmethod
    async def session_view(request, context):
        db_layer = AAADataLayer(context.postgres)
        user_id = context.security.user_id if context.security else None
        
        if not user_id:
            return XSCUtility.error_response("Unauthorized", error_code="401")
            
        resp = await db_layer.get_active_sessions_for_user(user_id)
        if resp.get("status") == "success":
            return XSCUtility.success_response("Sessions retrieved successfully", resp.get("data", []))
        return resp

    @staticmethod
    async def session_update(request, context):
        import xsc_conf.xsc_conf_config as config
        import jwt
        import datetime
        
        if not context.security or not context.security.session_id:
            return XSCUtility.error_response("Unauthorized", error_code="401")
            
        session_id = context.security.session_id
        user_id = context.security.user_id
        
        # Extend the session (assuming 2 hour extension for refresh)
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)
        
        # We would typically update tb_sessions here to reflect the new expiry
        # For now, we generate the new token.
        jwt_payload = {
            "sub": str(user_id),
            "session_id": session_id,
            "org_id": context.security.org_id,
            "inst_id": context.security.institution_id,
            "exp": expires_at
        }
        jwt_token = jwt.encode(jwt_payload, config.JWT_SECRET, algorithm="HS256")

        return XSCUtility.success_response("Session refreshed successfully", {"token": jwt_token})

    @staticmethod
    async def session_delete(request, context):
        db_layer = AAADataLayer(context.postgres)
        user_id = context.security.user_id if context.security else None
        
        if user_id:
            await db_layer.invalidate_all_active_sessions(user_id)
            # Log logout success
            await db_layer.create_auth_log({
                "id": XSCUtility.generate_uuid(),
                "user_id": user_id,
                "evt_type_id": 2, # Logout
                "evt_status_id": 1, # Success
                "evt_at": XSCUtility.get_current_timestamp()
            })
            
        return XSCUtility.success_response("Logout successful")

    @staticmethod
    async def mfa(request, context):
        from modules.m_AAA.m_AAA_sm_mfa import sm_mfa
        match request.actionType.lower():
            case "add": return await sm_mfa.mfa_add(request, context)
            case "view": return await sm_mfa.mfa_view(request, context)
            case "update": return await sm_mfa.mfa_update(request, context)
            case "delete": return await sm_mfa.mfa_delete(request, context)
            case _: return XSCUtility.error_response("Invalid actionType")

    @staticmethod
    async def password(request, context):
        """
        Executes the `password()` action to process the corresponding client request.
        """
        match request.actionType.lower():
            case "add":
                return await sm_auth.password_add(request, context)
            case "view":
                return await sm_auth.password_view(request, context)
            case "update":
                return await sm_auth.password_update(request, context)
            case "delete":
                return await sm_auth.password_delete(request, context)
            case _:
                return XSCUtility.error_response("Invalid actionType")

    @staticmethod
    async def password_add(request, context):
        db_layer = AAADataLayer(context.postgres)
        user_id = context.security.user_id if context.security else None
        inst_id = context.security.institution_id if context.security else None
        
        if not user_id:
            return XSCUtility.error_response("Unauthorized", error_code="401")
            
        payload = request.payload or {}
        new_pwd = payload.get("password")
        
        if not new_pwd:
            return XSCUtility.error_response("Password is required")
            
        # Validate against policy
        from xsc_lib.xsc_lib_app.xsc_liba_capability import CapabilityRegistry
        provider = CapabilityRegistry.get_capability("policy_provider")
        if not provider:
            return XSCUtility.error_response("Policy provider unavailable")
            
        policy = await provider.get_password_policy(inst_id)
        
        if len(new_pwd) < policy.min_length:
            return XSCUtility.error_response(f"Password must be at least {policy.min_length} characters")
        if policy.require_uppercase and not any(c.isupper() for c in new_pwd):
            return XSCUtility.error_response("Password must contain at least one uppercase letter")
        if policy.require_number and not any(c.isdigit() for c in new_pwd):
            return XSCUtility.error_response("Password must contain at least one number")
        if policy.require_special and not any(not c.isalnum() for c in new_pwd):
            return XSCUtility.error_response("Password must contain at least one special character")
            
        new_hash = XSCUtility.generate_hash(new_pwd)
        await db_layer.update_user_password(user_id, new_hash)
        
        # Ensure password state is marked active
        await db_layer.update_user_password_state({
            "user_id": user_id,
            "is_expired": False,
            "expired_at": None
        })
        
        await db_layer.create_auth_log({
            "id": XSCUtility.generate_uuid(),
            "user_id": user_id,
            "evt_type_id": 4, # e.g. password creation event
            "evt_status_id": 1,
            "evt_at": XSCUtility.get_current_timestamp()
        })
        
        return XSCUtility.success_response("Password set successfully")

    @staticmethod
    async def password_view(request, context):
        payload = request.payload or {}
        prospective_pwd = payload.get("password", "")
        
        inst_id = context.security.institution_id if context.security else None
        from xsc_lib.xsc_lib_app.xsc_liba_capability import CapabilityRegistry
        
        provider = CapabilityRegistry.get_capability("policy_provider")
        if not provider:
            return XSCUtility.error_response("Policy provider unavailable")
            
        policy = await provider.get_password_policy(inst_id)
        
        rules = {
            "minLength": len(prospective_pwd) >= policy.min_length,
            "uppercase": not policy.require_uppercase or any(c.isupper() for c in prospective_pwd),
            "lowercase": True, # basic assumption if any policy needed
            "number": not policy.require_number or any(c.isdigit() for c in prospective_pwd),
            "specialCharacter": not policy.require_special or any(not c.isalnum() for c in prospective_pwd)
        }
        
        failed_rules = [k for k, v in rules.items() if not v]
        is_compliant = len(failed_rules) == 0
        score = 100 if is_compliant else (len([v for v in rules.values() if v]) / len(rules)) * 100
        
        return XSCUtility.success_response("Password evaluation complete", {
            "isCompliant": is_compliant,
            "score": int(score),
            "strength": "Strong" if is_compliant else "Weak",
            "rules": rules,
            "failedRules": failed_rules
        })

    @staticmethod
    async def password_update(request, context):
        db_layer = AAADataLayer(context.postgres)
        user_id = context.security.user_id if context.security else None
        inst_id = context.security.institution_id if context.security else None
        
        if not user_id:
            return XSCUtility.error_response("Unauthorized", error_code="401")
            
        payload = request.payload or {}
        current_pwd = payload.get("currentPassword")
        new_pwd = payload.get("newPassword")
        
        if not current_pwd or not new_pwd:
            return XSCUtility.error_response("currentPassword and newPassword are required")
            
        # Verify current password
        user_resp = await db_layer.get_user_password_hash(user_id)
        if user_resp["status"] == "error" or not user_resp["data"]:
            return XSCUtility.error_response("User not found")
            
        if not XSCUtility.compare_hash(current_pwd, user_resp["data"][0]["password_hash"]):
            return XSCUtility.error_response("Current password is incorrect")
            
        # Fetch policy
        provider = CapabilityRegistry.get_capability("policy_provider")
        if not provider:
            return XSCUtility.error_response("Policy provider unavailable")
            
        password_policy = await provider.get_password_policy(inst_id)
        
        min_length = password_policy.min_length
        require_uppercase = password_policy.require_uppercase
        require_numbers = password_policy.require_number
        require_special_chars = password_policy.require_special
            
        if len(new_pwd) < min_length:
            return XSCUtility.error_response(f"Password must be at least {min_length} characters")
        if require_uppercase and not any(c.isupper() for c in new_pwd):
            return XSCUtility.error_response("Password must contain at least one uppercase letter")
        if require_numbers and not any(c.isdigit() for c in new_pwd):
            return XSCUtility.error_response("Password must contain at least one number")
        if require_special_chars and not any(not c.isalnum() for c in new_pwd):
            return XSCUtility.error_response("Password must contain at least one special character")
            
        # Hash and update
        new_hash = XSCUtility.generate_hash(new_pwd)
        await db_layer.update_user_password(user_id, new_hash)
        
        # Log successful password update
        await db_layer.create_auth_log({
            "id": XSCUtility.generate_uuid(),
            "user_id": user_id,
            "evt_type_id": 3, # Password Change
            "evt_status_id": 1, # Success
            "evt_at": XSCUtility.get_current_timestamp()
        })
        
        return XSCUtility.success_response("Password updated successfully")

    @staticmethod
    async def password_delete(request, context):
        db_layer = AAADataLayer(context.postgres)
        user_id = context.security.user_id if context.security else None
        
        if not user_id:
            return XSCUtility.error_response("Unauthorized", error_code="401")
            
        from datetime import datetime, timezone
        
        await db_layer.update_user_password_state({
            "user_id": user_id,
            "is_expired": True,
            "expired_at": datetime.now(timezone.utc)
        })
        
        # Invalidate active sessions
        await db_layer.revoke_user_sessions(user_id)
        
        # Log password expiration
        await db_layer.create_auth_log({
            "id": XSCUtility.generate_uuid(),
            "user_id": user_id,
            "evt_type_id": 3, # Password change/expiration
            "evt_status_id": 1, # Success
            "evt_at": XSCUtility.get_current_timestamp()
        })
        
        return XSCUtility.success_response("Password expired successfully")

    @staticmethod
    async def passwordReset(request, context):
        """
        Executes the `passwordReset()` action to process the corresponding client request.
        """
        match request.actionType.lower():
            case "add":
                return await sm_auth.passwordReset_add(request, context)
            case "view":
                return await sm_auth.passwordReset_view(request, context)
            case "update":
                return await sm_auth.passwordReset_update(request, context)
            case "delete":
                return await sm_auth.passwordReset_delete(request, context)
            case _:
                return XSCUtility.error_response("Invalid actionType")

    @staticmethod
    async def passwordReset_add(request, context):
        db_layer = AAADataLayer(context.postgres)
        payload = request.payload or {}

        # Initiate Password Reset
        email = payload.get("email")
        if not email:
            return XSCUtility.error_response("Email is required")

        user_resp = await db_layer.get_user_by_email(email)
        if user_resp["status"] == "error" or not user_resp["data"]:
            # To prevent email enumeration, return a generic success message
            return XSCUtility.success_response(
                "If an account exists, a reset link has been generated."
            )

        user_id = user_resp["data"][0]["id"]

        # Generate a secure reset token
        import secrets
        import datetime

        reset_token = secrets.token_urlsafe(32)

        now = datetime.datetime.now(datetime.timezone.utc)
        expires = now + datetime.timedelta(hours=1)

        token_data = {
            "user_id": user_id,
            "reset_token": reset_token,
            "requested_at": now,
            "expires_at": expires,
            "status_id": 1,  # Active
        }

        db_resp = await db_layer.create_password_reset_token(token_data)
        if db_resp["status"] == "error":
            return db_resp

        # TODO: Implement Password Reset Notification
        # Ownership: m_Communication
        # Status: Deferred
        # Reason: CommunicationManager is not yet available in the platform baseline.
        # Blocking: No (Reset token is generated, API consumer must route it for now).
        # Target Sprint: Platform Services Sprint
        return XSCUtility.success_response(
            "If an account exists, a password reset link has been sent to the registered email address."
        )

    @staticmethod
    async def passwordReset_view(request, context):
        db_layer = AAADataLayer(context.postgres)
        payload = request.payload or {}

        # Validate token
        token = payload.get("token")
        if not token:
            return XSCUtility.error_response("Token is required")

        token_resp = await db_layer.get_password_reset_token(token)
        if token_resp["status"] == "error" or not token_resp["data"]:
            return XSCUtility.error_response("Invalid or expired token")

        import datetime

        token_data = token_resp["data"][0]
        expires_at_val = token_data.get("expires_at")
        if expires_at_val:
            if isinstance(expires_at_val, str):
                try:
                    expires_at = datetime.datetime.fromisoformat(
                        expires_at_val.replace("Z", "+00:00")
                    )
                except ValueError:
                    expires_at = None
            elif isinstance(expires_at_val, datetime.datetime):
                expires_at = expires_at_val
                # ensure timezone awareness for comparison if it is naive
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=datetime.timezone.utc)
            else:
                expires_at = None

            if expires_at:
                now = datetime.datetime.now(datetime.timezone.utc)
                print(f"DEBUG: now={now} expires_at={expires_at}")
                if now > expires_at:
                    return XSCUtility.error_response(
                        f"Token has expired. Now: {now}, Exp: {expires_at}"
                    )

        return XSCUtility.success_response(
            "Password reset token validated successfully"
        )

    @staticmethod
    async def passwordReset_update(request, context):
        db_layer = AAADataLayer(context.postgres)
        payload = request.payload or {}

        # Execute Reset
        token = payload.get("token")
        new_password = payload.get("newPassword")

        if not token or not new_password:
            return XSCUtility.error_response("Token and newPassword are required")

        token_resp = await db_layer.get_password_reset_token(token)
        if token_resp["status"] == "error" or not token_resp["data"]:
            return XSCUtility.error_response("Invalid or expired token")

        token_data = token_resp["data"][0]
        user_id = token_data["user_id"]
        import datetime

        token_data = token_resp["data"][0]
        expires_at_val = token_data.get("expires_at")
        if expires_at_val:
            if isinstance(expires_at_val, str):
                try:
                    expires_at = datetime.datetime.fromisoformat(
                        expires_at_val.replace("Z", "+00:00")
                    )
                except ValueError:
                    expires_at = None
            elif isinstance(expires_at_val, datetime.datetime):
                expires_at = expires_at_val
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=datetime.timezone.utc)
            else:
                expires_at = None

            if expires_at:
                now = datetime.datetime.now(datetime.timezone.utc)
                if now > expires_at:
                    return XSCUtility.error_response("Token has expired")

        # 1. Enforce Password Policy
        provider = CapabilityRegistry.get_capability("policy_provider")
        if not provider:
            return XSCUtility.error_response("Policy provider unavailable")
            
        auth_ctx = await db_layer.get_user_auth_context(user_id)
        inst_id = auth_ctx["orgs"][0]["institution_id"] if auth_ctx["orgs"] else None
        
        policy = await provider.get_password_policy(inst_id)
        min_length = policy.min_length
        require_uppercase = policy.require_uppercase
        require_numbers = policy.require_number
        require_special_chars = policy.require_special
            
        if len(new_password) < min_length:
            return XSCUtility.error_response(f"Password must be at least {min_length} characters")
        if require_uppercase and not any(c.isupper() for c in new_password):
            return XSCUtility.error_response("Password must contain at least one uppercase letter")
        if require_numbers and not any(c.isdigit() for c in new_password):
            return XSCUtility.error_response("Password must contain at least one number")
        if require_special_chars and not any(not c.isalnum() for c in new_password):
            return XSCUtility.error_response("Password must contain at least one special character")
        # 2-4: Update Password, Invalidate Token, and Revoke Active Sessions via Transaction
        password_hash = XSCUtility.generate_hash(new_password)
        trans_resp = await db_layer.execute_password_reset(
            user_id, 
            password_hash, 
            token, 
            datetime.datetime.utcnow()
        )
        
        if trans_resp.get("status") == "error":
            return trans_resp

        # Log successful password reset
        await db_layer.create_auth_log({
            "id": XSCUtility.generate_uuid(),
            "user_id": user_id,
            "evt_type_id": 4, # Password Reset
            "evt_status_id": 1, # Success
            "evt_at": XSCUtility.get_current_timestamp()
        })

        return XSCUtility.success_response("Password reset successfully")

    @staticmethod
    async def passwordReset_delete(request, context):
        payload = request.payload or {}
        token = payload.get("token")
        
        if not token:
            return XSCUtility.error_response("Token is required")

        db_layer = AAADataLayer(context.postgres)
        
        # 1. Verify token exists and is valid
        token_resp = await db_layer.get_password_reset_token(token)
        if token_resp.get("status") == "error" or not token_resp.get("data"):
            return XSCUtility.error_response("Invalid or expired password reset token")
            
        token_data = token_resp["data"][0]
        expires_at = token_data.get("expires_at")
        
        if expires_at:
            if isinstance(expires_at, str):
                expires_at = datetime.datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=datetime.timezone.utc)
            now = datetime.datetime.now(datetime.timezone.utc)
            if now > expires_at:
                return XSCUtility.error_response("Token has expired")

        # 2. Revoke the token atomically
        revoked_at = datetime.datetime.utcnow()
        revoke_resp = await db_layer.revoke_password_reset_token(token, revoked_at)
        
        if revoke_resp.get("status") == "error":
            return revoke_resp

        return XSCUtility.success_response("Password reset cancelled successfully")

    @staticmethod
    async def user(request, context):
        """
        Executes the `user()` action to process the corresponding client request.
        """
        match request.actionType.lower():
            case "view":
                return await sm_auth.user_view(request, context)
            case _:
                return XSCUtility.error_response("Invalid actionType")

    @staticmethod
    async def user_view(request, context):
        if not context.security or not context.security.user_id:
            return XSCUtility.error_response("Unauthorized", error_code="401")

        response_data = {
            "user_id": context.security.user_id,
            "email": context.security.jwt_claims.get("email"),
            "roles": context.security.roles,
            "permissions": context.security.permissions,
            "institution_id": context.security.institution_id,
            "org_id": context.security.jwt_claims.get("org_id"),
        }
        return XSCUtility.success_response("Current user retrieved", response_data)
