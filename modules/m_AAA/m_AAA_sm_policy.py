"""
File: m_AAA_sm_policy.py
Description: Policy Configuration submodule for m_AAA.

Author: Siddharth Amdal
App: OneApp

"""

from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from .m_AAA_data import AAADataLayer
from xsc_lib.xsc_lib_app.xsc_liba_capability import CapabilityRegistry
import uuid

class sm_policy:
    @staticmethod
    async def passwordPolicy(request, context):
        """
        Executes the `passwordPolicy()` action.
        """
        match request.actionType.lower():
            case "add":
                return await sm_policy.passwordPolicy_add(request, context)
            case "view":
                return await sm_policy.passwordPolicy_view(request, context)
            case "update":
                return await sm_policy.passwordPolicy_update(request, context)
            case "delete":
                return await sm_policy.passwordPolicy_delete(request, context)
            case _:
                return XSCUtility.error_response("Invalid actionType")

    @staticmethod
    async def passwordPolicy_add(request, context):
        payload = request.payload or {}
        payload["inst_id"] = context.security.institution_id if context.security else None
        payload["id"] = str(uuid.uuid4())
        
        provider = CapabilityRegistry.get_capability("policy_provider")
        if not provider:
            return XSCUtility.error_response("Policy provider unavailable")
            
        resp = await provider.upsert_password_policy(payload)
        
        if resp and resp.get("status") == "success":
            return XSCUtility.success_response("Password policy created successfully", resp.get("data", []))
        return XSCUtility.error_response("Failed to create password policy")

    @staticmethod
    async def passwordPolicy_view(request, context):
        provider = CapabilityRegistry.get_capability("policy_provider")
        if not provider:
            return XSCUtility.error_response("Policy provider unavailable")
        inst_id = context.security.institution_id if context.security else None
        
        policy = await provider.get_password_policy(inst_id)
        if policy:
            policy_dict = policy.__dict__.copy()
            policy_dict.pop('_sa_instance_state', None)
            return XSCUtility.success_response("Password policy retrieved", policy_dict)
            
        return XSCUtility.error_response("Password policy not found")

    @staticmethod
    async def passwordPolicy_update(request, context):
        payload = request.payload or {}
        if not payload.get("id"):
            return XSCUtility.error_response("Missing 'id' in payload")
            
        payload["inst_id"] = context.security.institution_id if context.security else None
        
        provider = CapabilityRegistry.get_capability("policy_provider")
        if not provider:
            return XSCUtility.error_response("Policy provider unavailable")
            
        resp = await provider.upsert_password_policy(payload)
        
        if resp and resp.get("status") == "success":
            return XSCUtility.success_response("Password policy updated successfully", resp.get("data", []))
        return XSCUtility.error_response("Failed to update password policy")

    @staticmethod
    async def passwordPolicy_delete(request, context):
        provider = CapabilityRegistry.get_capability("policy_provider")
        if not provider:
            return XSCUtility.error_response("Policy provider unavailable")
            
        resp = await provider.delete_password_policy(context.security.institution_id if context.security else None)
        
        if resp and resp.get("status") == "success":
            return XSCUtility.success_response("Password policy deleted successfully. Platform defaults will apply prospectively.", None)
        return XSCUtility.error_response("Failed to delete password policy")


    @staticmethod
    async def sessionPolicy(request, context):
        """
        Executes the `sessionPolicy()` action.
        """
        match request.actionType.lower():
            case "add":
                return await sm_policy.sessionPolicy_add(request, context)
            case "view":
                return await sm_policy.sessionPolicy_view(request, context)
            case "update":
                return await sm_policy.sessionPolicy_update(request, context)
            case "delete":
                return await sm_policy.sessionPolicy_delete(request, context)
            case _:
                return XSCUtility.error_response("Invalid actionType")

    @staticmethod
    async def sessionPolicy_add(request, context):
        payload = request.payload or {}
        payload["inst_id"] = context.security.institution_id if context.security else None
        payload["id"] = str(uuid.uuid4())
        
        provider = CapabilityRegistry.get_capability("policy_provider")
        if not provider:
            return XSCUtility.error_response("Policy provider unavailable")
            
        resp = await provider.upsert_session_policy(payload)
        
        if resp and resp.get("status") == "success":
            return XSCUtility.success_response("Session policy created successfully", resp.get("data", []))
        return XSCUtility.error_response("Failed to create session policy")

    @staticmethod
    async def sessionPolicy_view(request, context):
        provider = CapabilityRegistry.get_capability("policy_provider")
        if not provider:
            return XSCUtility.error_response("Policy provider unavailable")
        inst_id = context.security.institution_id if context.security else None
        
        policy = await provider.get_session_policy(inst_id)
        if policy:
            policy_dict = policy.__dict__.copy()
            policy_dict.pop('_sa_instance_state', None)
            return XSCUtility.success_response("Session policy retrieved", policy_dict)
            
        return XSCUtility.error_response("Session policy not found")

    @staticmethod
    async def sessionPolicy_update(request, context):
        payload = request.payload or {}
        if not payload.get("id"):
            return XSCUtility.error_response("Missing 'id' in payload")
            
        payload["inst_id"] = context.security.institution_id if context.security else None
        provider = CapabilityRegistry.get_capability("policy_provider")
        if not provider:
            return XSCUtility.error_response("Policy provider unavailable")
            
        resp = await provider.upsert_session_policy(payload)
        
        if resp and resp.get("status") == "success":
            return XSCUtility.success_response("Session policy updated successfully", resp.get("data", []))
        return XSCUtility.error_response("Failed to update session policy")

    @staticmethod
    async def sessionPolicy_delete(request, context):
        provider = CapabilityRegistry.get_capability("policy_provider")
        if not provider:
            return XSCUtility.error_response("Policy provider unavailable")
            
        resp = await provider.delete_session_policy(context.security.institution_id if context.security else None)
        
        if resp and resp.get("status") == "success":
            return XSCUtility.success_response("Session policy deleted successfully", None)
        return XSCUtility.error_response("Failed to delete session policy")


    @staticmethod
    async def loginPolicy(request, context):
        """
        Executes the `loginPolicy()` action.
        """
        match request.actionType.lower():
            case "add":
                return await sm_policy.loginPolicy_add(request, context)
            case "view":
                return await sm_policy.loginPolicy_view(request, context)
            case "update":
                return await sm_policy.loginPolicy_update(request, context)
            case "delete":
                return await sm_policy.loginPolicy_delete(request, context)
            case _:
                return XSCUtility.error_response("Invalid actionType")

    @staticmethod
    async def loginPolicy_add(request, context):
        payload = request.payload or {}
        payload["inst_id"] = context.security.institution_id if context.security else None
        payload["id"] = str(uuid.uuid4())
        
        provider = CapabilityRegistry.get_capability("policy_provider")
        if not provider:
            return XSCUtility.error_response("Policy provider unavailable")
            
        resp = await provider.upsert_login_policy(payload)
        
        if resp and resp.get("status") == "success":
            return XSCUtility.success_response("Login policy created successfully", resp.get("data", []))
        return XSCUtility.error_response("Failed to create login policy")

    @staticmethod
    async def loginPolicy_view(request, context):
        provider = CapabilityRegistry.get_capability("policy_provider")
        if not provider:
            return XSCUtility.error_response("Policy provider unavailable")
        inst_id = context.security.institution_id if context.security else None
        
        policy = await provider.get_login_policy(inst_id)
        if policy:
            policy_dict = policy.__dict__.copy()
            policy_dict.pop('_sa_instance_state', None)
            return XSCUtility.success_response("Login policy retrieved", policy_dict)
            
        return XSCUtility.error_response("Login policy not found")

    @staticmethod
    async def loginPolicy_update(request, context):
        payload = request.payload or {}
        if not payload.get("id"):
            return XSCUtility.error_response("Missing 'id' in payload")
            
        payload["inst_id"] = context.security.institution_id if context.security else None
        provider = CapabilityRegistry.get_capability("policy_provider")
        if not provider:
            return XSCUtility.error_response("Policy provider unavailable")
            
        resp = await provider.upsert_login_policy(payload)
        
        if resp and resp.get("status") == "success":
            return XSCUtility.success_response("Login policy updated successfully", resp.get("data", []))
        return XSCUtility.error_response("Failed to update login policy")

    @staticmethod
    async def loginPolicy_delete(request, context):
        provider = CapabilityRegistry.get_capability("policy_provider")
        if not provider:
            return XSCUtility.error_response("Policy provider unavailable")
            
        resp = await provider.delete_login_policy(context.security.institution_id if context.security else None)
        
        if resp and resp.get("status") == "success":
            return XSCUtility.success_response("Login policy deleted successfully", None)
        return XSCUtility.error_response("Failed to delete login policy")
