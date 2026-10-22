"""
File: m_AAA_sm_rbac.py
Description: Role-Based Access Control submodule for m_AAA.

Author: Siddharth Amdal
App: OneApp

"""

from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from .m_AAA_data import AAADataLayer


class sm_rbac:
    @staticmethod
    async def role(request, context):
        """
        Executes the `role()` action to process the corresponding client request.

        Args:
            request: The OneAppRequest payload containing the module, submodule, action, actionType, and payload.
            context: The ExecutionContext containing request-scoped dependencies.
        """
        match request.actionType.lower():
            case "add":
                return await sm_rbac.role_add(request, context)
            case "view":
                return await sm_rbac.role_view(request, context)
            case "update":
                return await sm_rbac.role_update(request, context)
            case "delete":
                return await sm_rbac.role_delete(request, context)
            case _:
                return XSCUtility.error_response("Invalid actionType")

    @staticmethod
    async def role_add(request, context):
        db_layer = AAADataLayer(context.postgres)
        payload = request.payload or {}
        
        role_code = payload.get("roleCode")
        role_name = payload.get("roleName")
        description = payload.get("description", "")
        
        if not role_code or not role_name:
            return XSCUtility.error_response("roleCode and roleName are required")
            
        role_data = {
            "id": XSCUtility.generate_uuid(),
            "role_code": role_code,
            "role_name": role_name,
            "description": description,
            "status_id": payload.get("statusId", 1)
        }
        
        # In sch_iam.tb_role, role_code often has a unique constraint.
        # Postgres driver will catch uniqueness violation, but we can also pre-check.
        resp = await db_layer.create_role(role_data)
        if resp["status"] == "error":
            return resp
            
        return XSCUtility.success_response("Role created successfully", {"roleId": role_data["id"]})

    @staticmethod
    async def role_view(request, context):
        db_layer = AAADataLayer(context.postgres)
        resp = await db_layer.get_roles()
        return resp

    @staticmethod
    async def role_update(request, context):
        db_layer = AAADataLayer(context.postgres)
        payload = request.payload or {}
        
        role_id = payload.get("id")
        if not role_id:
            return XSCUtility.error_response("Role ID is required")
            
        role_data = {
            "role_name": payload.get("roleName"),
            "description": payload.get("description", ""),
            "status_id": payload.get("statusId", 1)
        }
        
        resp = await db_layer.update_role(role_id, role_data)
        if resp["status"] == "error":
            return resp
            
        return XSCUtility.success_response("Role updated successfully")

    @staticmethod
    async def role_delete(request, context):
        db_layer = AAADataLayer(context.postgres)
        payload = request.payload or {}
        role_id = payload.get("id")
        
        if not role_id:
            return XSCUtility.error_response("Role ID is required")
            
        # delete_role enforces BR-05.1 (Block Delete if Active Users)
        resp = await db_layer.delete_role(role_id)
        if resp["status"] == "error":
            return resp
            
        return XSCUtility.success_response("Role deleted successfully")

    @staticmethod
    async def roleAssignment(request, context):
        """
        Executes the `roleAssignment()` action to process the corresponding client request.
        """
        match request.actionType.lower():
            case "add":
                return await sm_rbac.roleAssignment_add(request, context)
            case "view":
                return await sm_rbac.roleAssignment_view(request, context)
            case "update":
                return await sm_rbac.roleAssignment_update(request, context)
            case "delete":
                return await sm_rbac.roleAssignment_delete(request, context)
            case _:
                return XSCUtility.error_response("Invalid actionType")

    @staticmethod
    async def roleAssignment_add(request, context):
        db_layer = AAADataLayer(context.postgres)
        payload = request.payload or {}
        
        user_org_id = payload.get("userOrgId")
        org_role_ids = payload.get("orgRoleIds", [])
        
        # Fallback for older single assignment
        if "orgRoleId" in payload and payload["orgRoleId"] not in org_role_ids:
            org_role_ids.append(payload["orgRoleId"])
            
        if not user_org_id or not org_role_ids:
            return XSCUtility.error_response("userOrgId and orgRoleIds (array) are required")
            
        successful = []
        failed = []
        
        for role_id in org_role_ids:
            assignment_id = XSCUtility.generate_uuid()
            resp = await db_layer.assign_role(user_org_id, role_id, assignment_id)
            if resp.get("status") == "success":
                successful.append({"orgRoleId": role_id, "assignmentId": assignment_id})
            else:
                failed.append({"orgRoleId": role_id, "error": resp.get("message", "Unknown error")})
                
        return XSCUtility.success_response(
            "Role assignment completed", 
            {"successful": successful, "failed": failed}
        )

    @staticmethod
    async def roleAssignment_view(request, context):
        db_layer = AAADataLayer(context.postgres)
        payload = request.payload or {}
        user_id = payload.get("userId")
        
        if not user_id:
            return XSCUtility.error_response("userId is required")
            
        resp = await db_layer.get_role_assignments(user_id)
        return resp

    @staticmethod
    async def roleAssignment_update(request, context):
        return XSCUtility.error_response(
            "Role assignment updates are unsupported. Please explicitly revoke the assignment and issue a new one to preserve audit integrity.", 
            error_code="UNSUPPORTED_OPERATION"
        )

    @staticmethod
    async def roleAssignment_delete(request, context):
        db_layer = AAADataLayer(context.postgres)
        payload = request.payload or {}
        assignment_id = payload.get("assignmentId")
        
        if not assignment_id:
            return XSCUtility.error_response("assignmentId is required")
            
        resp = await db_layer.revoke_role(assignment_id)
        if resp["status"] == "error":
            return resp
            
        return XSCUtility.success_response("Role revoked successfully")

    @staticmethod
    async def permission(request, context):
        """
        Executes the `permission()` action to process the corresponding client request.
        """
        match request.actionType.lower():
            case "add":
                return await sm_rbac.permission_add(request, context)
            case "view":
                return await sm_rbac.permission_view(request, context)
            case "update":
                return await sm_rbac.permission_update(request, context)
            case "delete":
                return await sm_rbac.permission_delete(request, context)
            case _:
                return XSCUtility.error_response("Invalid actionType")

    @staticmethod
    async def permission_add(request, context):
        db_layer = AAADataLayer(context.postgres)
        payload = request.payload or {}
        
        permission_code = payload.get("permissionCode")
        description = payload.get("description", "")
        
        if not permission_code:
            return XSCUtility.error_response("permissionCode is required")
            
        permission_data = {
            "id": XSCUtility.generate_uuid(),
            "permission_code": permission_code,
            "description": description
        }
        
        resp = await db_layer.create_permission(permission_data)
        if resp["status"] == "error":
            return resp
            
        return XSCUtility.success_response("Permission registered successfully")

    @staticmethod
    async def permission_view(request, context):
        db_layer = AAADataLayer(context.postgres)
        resp = await db_layer.get_permissions()
        return resp

    @staticmethod
    async def permission_update(request, context):
        db_layer = AAADataLayer(context.postgres)
        payload = request.payload or {}
        
        permission_id = payload.get("id")
        permission_code = payload.get("permissionCode")
        description = payload.get("description", "")
        
        if not permission_id or not permission_code:
            return XSCUtility.error_response("id and permissionCode are required")
            
        permission_data = {
            "permission_code": permission_code,
            "description": description
        }
        
        resp = await db_layer.update_permission(permission_id, permission_data)
        if resp["status"] == "error":
            return resp
            
        return XSCUtility.success_response("Permission description updated successfully")

    @staticmethod
    async def permission_delete(request, context):
        db_layer = AAADataLayer(context.postgres)
        payload = request.payload or {}
        permission_id = payload.get("id")
        
        if not permission_id:
            return XSCUtility.error_response("Permission ID is required")
            
        resp = await db_layer.delete_permission(permission_id)
        if resp["status"] == "error":
            return resp
            
        return XSCUtility.success_response("Permission deleted successfully")

    @staticmethod
    async def accessibleModules(request, context):
        """
        Executes the `accessibleModules()` action to return navigation metadata
        for the authenticated identity.
        """
        match request.actionType.lower():
            case "view":
                return await sm_rbac.accessibleModules_view(request, context)
            case _:
                return XSCUtility.error_response(
                    "Invalid actionType for accessibleModules"
                )

    @staticmethod
    async def accessibleModules_view(request, context):
        if not context.security or not context.security.user_id:
            return XSCUtility.error_response("Unauthorized access", "AUTH_REQUIRED")

        db_layer = AAADataLayer(context.postgres)

        # Resolve identity context
        user_context = await db_layer.get_user_identity_context(
            context.security.user_id
        )

        # Resolve permissions
        permissions = await db_layer.resolve_user_permissions(context.security.user_id)

        # Fetch modules from DB based on permissions
        modules_resp = await db_layer.get_accessible_modules(permissions)
        modules = modules_resp.get("data", []) if modules_resp.get("status") == "success" else []

        # Sort modules by display name for consistency
        modules.sort(key=lambda x: x.get("displayName", ""))

        response_payload = {"user": user_context, "modules": modules}

        return XSCUtility.success_response(
            "Accessible modules resolved successfully", response_payload
        )
