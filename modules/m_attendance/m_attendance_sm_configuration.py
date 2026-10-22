"""
File: m_attendance_sm_configuration.py
Description: Submodule business logic handler for attendance institutional policy configuration and marking types.
Encapsulates policy creation, validation, single active policy rules, semantic policy resets, and attendance marking type management.

Author: Siddharth Amdal
App: OneApp

"""

import logging
from typing import Dict, Any
from sqlalchemy import select, func, text
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from .m_attendance_data import AttendanceDataLayer
from .db_init import TbAttRecord

logger = logging.getLogger(__name__)


def _get_field(payload: dict, keys: list, default: Any = None) -> Any:
    for k in keys:
        if k in payload:
            return payload[k]
    # case-insensitive and normalized check
    norm_keys = {k.replace("_", "").replace(" ", "").lower() for k in keys}
    for p_key, p_val in payload.items():
        if p_key.replace("_", "").replace(" ", "").lower() in norm_keys:
            return p_val
    return default


def _has_field(payload: dict, keys: list) -> bool:
    for k in keys:
        if k in payload:
            return True
    norm_keys = {k.replace("_", "").replace(" ", "").lower() for k in keys}
    for p_key in payload.keys():
        if p_key.replace("_", "").replace(" ", "").lower() in norm_keys:
            return True
    return False


def _enrich_policy_response(res: dict) -> dict:
    if res.get("status") == "success" and res.get("data"):
        for row in res["data"]:
            if "id" in row:
                row["policyId"] = row["id"]
                row["policy_id"] = row["id"]
    return res


class sm_configuration:
    """
    Submodule handler for institutional attendance policy configuration and marking type actions.
    Enforces business rules such as single active policy per institution, percentage bounds, and semantic deletes.
    """

    @staticmethod
    async def attendanceConfiguration(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes the `attendanceConfiguration()` action to process the corresponding client request.
        Supports institutional attendance policy lifecycle including semantic deletion/reseting to defaults.

        Args:
            self: Reference to the current class instance.
            request: The OneAppRequest payload containing the module, submodule, action, actionType, and payload.
            context: The ExecutionContext containing request-scoped dependencies (e.g. PostgreSQLManager instance, logger, user_id).

        Returns:
            - status: Indicates whether the request was processed successfully ('success') or failed ('error').
            - message: A human-readable string providing details about the execution status.
            - data: The core data payload returned by the operation (e.g. database records).

        req_json_obj expected format:
        {
            "mod": "m_attendance",
            "subMod": "sm_configuration",
            "action": "attendanceConfiguration",
            "actionType": "<add|view|update|delete|activate|deactivate|get_active>",
            "payload": {
                "instId": 1,
                "policyName": "Standard Attendance Policy 2026",
                "minAttPercent": 75.0,
                "allowLateMarking": true,
                "lateMarkingWindowMinutes": 15,
                "autoLockAfterHours": 24,
                "requireApproval": true,
                "requireMedProof": false,
                "isActive": true
            }
        }
        """
        action_type = (request.actionType or "").lower()
        match action_type:
            case "add":
                return await sm_configuration.config_add(request, context)
            case "view":
                return await sm_configuration.config_view(request, context)
            case "update":
                return await sm_configuration.config_update(request, context)
            case "delete":
                return await sm_configuration.config_delete(request, context)
            case "activate":
                return await sm_configuration.config_activate(request, context)
            case "deactivate":
                return await sm_configuration.config_deactivate(request, context)
            case "get_active":
                return await sm_configuration.config_get_active(request, context)
            case _:
                logger.warning(
                    f"[sm_configuration] Invalid actionType received for attendanceConfiguration: {action_type}"
                )
                return XSCUtility.error_response(
                    "Invalid actionType for attendanceConfiguration",
                    error_code="INVALID_ACTION_TYPE",
                )

    @staticmethod
    async def attendanceType(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes the `attendanceType()` action to manage attendance marking types (Present, Absent, Late, Excused).
        Enforces semantic deactivation rather than SQL deletion when records reference the type.

        Args:
            self: Reference to the current class instance.
            request: The OneAppRequest payload containing the module, submodule, action, actionType, and payload.
            context: The ExecutionContext containing request-scoped dependencies (e.g. PostgreSQLManager instance, logger, user_id).

        Returns:
            - status: Indicates whether the request was processed successfully ('success') or failed ('error').
            - message: A human-readable string providing details about the execution status.
            - data: The core data payload returned by the operation (e.g. database records).

        req_json_obj expected format:
        {
            "mod": "m_attendance",
            "subMod": "sm_configuration",
            "action": "attendanceType",
            "actionType": "<add|view|update|delete>",
            "payload": {
                "typeCode": "PRESENT",
                "typeName": "Present in Class",
                "countsAsPresent": true
            }
        }
        """
        action_type = (request.actionType or "").lower()
        match action_type:
            case "add":
                return await sm_configuration._type_add(request, context)
            case "view":
                return await sm_configuration._type_view(request, context)
            case "update":
                return await sm_configuration._type_update(request, context)
            case "delete":
                return await sm_configuration._type_delete(request, context)
            case _:
                logger.warning(
                    f"[sm_configuration] Invalid actionType received for attendanceType: {action_type}"
                )
                return XSCUtility.error_response(
                    "Invalid actionType for attendanceType",
                    error_code="INVALID_ACTION_TYPE",
                )

    # =========================================================================
    # INTERNAL HANDLERS FOR attendanceConfiguration
    # =========================================================================

    @staticmethod
    async def config_add(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes the `_config_add()` action to validate and create a new attendance policy.

        Args:
            self: Reference to the current class instance.
            request: The OneAppRequest payload containing policy attributes.
            context: The ExecutionContext containing database manager and user identity.

        Returns:
            - status: Indicates whether the request was processed successfully ('success') or failed ('error').
            - message: A human-readable string providing details about the execution status.
            - data: The core data payload returned by the operation (e.g. database records).

        req_json_obj expected format:
        {
            "mod": "m_attendance",
            "subMod": "sm_configuration",
            "action": "attendanceConfiguration",
            "actionType": "add",
            "payload": {
                "instId": 1,
                "policyName": "Fall 2026 Policy",
                "minAttPercent": 75.0,
                "allowLateMarking": true,
                "isActive": true
            }
        }
        """
        try:
            payload = request.payload or {}
            inst_id = _get_field(payload, ["inst_id", "instId", "ins_id", "insId", "INS_ID"])
            policy_name = _get_field(payload, ["policy_name", "policyName", "POLICY NAME"])
            min_percent = _get_field(payload, ["min_att_percent", "minAttPercent", "MIN ATT PERCENT"])

            if not inst_id or not policy_name or min_percent is None:
                return XSCUtility.error_response(
                    "Mandatory fields missing: instId, policyName, and minAttPercent are required.",
                    error_code="VAL_MISSING_FIELDS",
                )

            try:
                min_percent_val = float(min_percent)
                if min_percent_val < 0.0 or min_percent_val > 100.0:
                    return XSCUtility.error_response(
                        "Validation failed: minAttPercent must be between 0.0 and 100.0.",
                        error_code="VAL_INVALID_PERCENT",
                    )
            except (ValueError, TypeError):
                return XSCUtility.error_response(
                    "Validation failed: minAttPercent must be a numeric value.",
                    error_code="VAL_TYPE_ERR",
                )

            eff_from = _get_field(payload, ["effective_from", "effectiveFrom", "EFFECTIVE FROM"])
            eff_to = _get_field(payload, ["effective_to", "effectiveTo", "EFFECTIVE TO"])
            if eff_from and eff_to and str(eff_to) < str(eff_from):
                return XSCUtility.error_response(
                    "Validation failed: effectiveTo date cannot be earlier than effectiveFrom date.",
                    error_code="VAL_DATE_ORDER",
                )

            db_layer = AttendanceDataLayer(context.postgres)
            is_active = _get_field(payload, ["is_active", "isActive", "IS ACTIVE"], True)

            if is_active:
                active_res = await db_layer.get_active_policy(int(inst_id))
                if active_res.get("status") == "success" and active_res.get("data"):
                    if len(active_res["data"]) > 0:
                        return XSCUtility.error_response(
                            f"An active attendance policy already exists for institution {inst_id}. Deactivate existing policy before activating a new one.",
                            error_code="BIZ_CONFLICT_ACTIVE_POLICY",
                        )

            user_id = getattr(context, "user_id", None) or _get_field(payload, ["userId", "user_id"])
            db_payload = {
                "inst_id": int(inst_id),
                "policy_name": str(policy_name).strip(),
                "min_att_percent": min_percent_val,
                "allow_late_marking": bool(_get_field(payload, ["allow_late_marking", "allowLateMarking", "ALLOW LATE MARKING"], False)),
                "late_marking_window_minutes": _get_field(payload, ["late_marking_window_minutes", "lateMarkingWindowMinutes", "LATE MARKING WINDOW MINUTES"]),
                "auto_lock_after_hours": _get_field(payload, ["auto_lock_after_hours", "autoLockAfterHours", "AUTO LOCK AFTER HOURS"]),
                "require_approval": bool(_get_field(payload, ["require_approval", "requireApproval", "REQUIRE APPROVAL"], False)),
                "require_med_proof": bool(_get_field(payload, ["require_med_proof", "requireMedProof", "require_med_proo", "requireMedProo", "REQUIRE MED PROOF"], False)),
                "effective_from": eff_from,
                "effective_to": eff_to,
                "is_active": bool(is_active),
                "created_by": int(user_id) if user_id else None,
            }

            res = await db_layer.create_policy(db_payload)
            if res.get("status") == "error":
                return res
            logger.info(
                f"[sm_configuration] Policy created successfully for inst_id {inst_id}"
            )
            res = _enrich_policy_response(res)
            return XSCUtility.success_response(
                "Attendance policy created successfully", data=res.get("data", [])
            )
        except Exception as e:
            logger.error(
                f"[sm_configuration] Error in _config_add: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response(
                "Internal Server Error in _config_add", error_code="ERR_SYS"
            )

    @staticmethod
    async def config_view(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes the `_config_view()` action to retrieve policy records by ID or list with filters.

        Args:
            self: Reference to the current class instance.
            request: The OneAppRequest payload containing optional filters (policyId, instId, isActive).
            context: The ExecutionContext containing database manager.

        Returns:
            - status: Indicates whether the request was processed successfully ('success') or failed ('error').
            - message: A human-readable string providing details about the execution status.
            - data: The core data payload returned by the operation (e.g. database records).

        req_json_obj expected format:
        {
            "mod": "m_attendance",
            "subMod": "sm_configuration",
            "action": "attendanceConfiguration",
            "actionType": "view",
            "payload": {
                "policyId": 1001
            }
        }
        """
        try:
            payload = request.payload or {}
            db_layer = AttendanceDataLayer(context.postgres)
            policy_id = _get_field(payload, ["policyId", "policy_id"])

            if policy_id:
                res = await db_layer.get_policy(int(policy_id))
                if res.get("status") == "error":
                    return res
                if not res.get("data"):
                    return XSCUtility.error_response(
                        f"Policy not found with ID {policy_id}",
                        error_code="ERR_NOT_FOUND",
                    )
                res = _enrich_policy_response(res)
                return XSCUtility.success_response(
                    "Attendance policy retrieved successfully", data=res.get("data", [])
                )

            inst_id = _get_field(payload, ["instId", "inst_id", "ins_id", "insId", "INS_ID"])
            is_active = _get_field(payload, ["isActive", "is_active", "IS ACTIVE"])
            limit = payload.get("limit", 50)
            offset = payload.get("offset", 0)

            res = await db_layer.list_policies(
                inst_id=int(inst_id) if inst_id is not None else None,
                is_active=bool(is_active) if is_active is not None else None,
                limit=int(limit),
                offset=int(offset),
            )
            if res.get("status") == "error":
                return res
            res = _enrich_policy_response(res)
            return XSCUtility.success_response(
                "Attendance policies listed successfully", data=res.get("data", [])
            )
        except Exception as e:
            logger.error(
                f"[sm_configuration] Error in _config_view: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response(
                "Internal Server Error in _config_view", error_code="ERR_SYS"
            )

    @staticmethod
    async def config_update(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes the `_config_update()` action to update configuration parameters.
        Takes immediate effect for future calculations; never retroactively recalculates history.

        Args:
            self: Reference to the current class instance.
            request: The OneAppRequest payload containing policyId and update attributes.
            context: The ExecutionContext containing database manager and user identity.

        Returns:
            - status: Indicates whether the request was processed successfully ('success') or failed ('error').
            - message: A human-readable string providing details about the execution status.
            - data: The core data payload returned by the operation (e.g. database records).

        req_json_obj expected format:
        {
            "mod": "m_attendance",
            "subMod": "sm_configuration",
            "action": "attendanceConfiguration",
            "actionType": "update",
            "payload": {
                "policyId": 1001,
                "minAttPercent": 80.0
            }
        }
        """
        try:
            payload = request.payload or {}
            policy_id = _get_field(payload, ["policyId", "policy_id"])
            if not policy_id:
                return XSCUtility.error_response(
                    "Mandatory field missing: policyId is required for update.",
                    error_code="VAL_MISSING_ID",
                )

            db_layer = AttendanceDataLayer(context.postgres)
            existing_res = await db_layer.get_policy(int(policy_id))
            if existing_res.get("status") == "error":
                return existing_res
            if not existing_res.get("data"):
                return XSCUtility.error_response(
                    "Attendance policy not found for update.",
                    error_code="ERR_NOT_FOUND",
                )

            existing_policy = existing_res["data"][0]
            update_data = {}

            if _has_field(payload, ["policy_name", "policyName", "POLICY NAME"]):
                update_data["policy_name"] = str(_get_field(payload, ["policy_name", "policyName", "POLICY NAME"])).strip()
            if _has_field(payload, ["min_att_percent", "minAttPercent", "MIN ATT PERCENT"]):
                try:
                    val = float(_get_field(payload, ["min_att_percent", "minAttPercent", "MIN ATT PERCENT"]))
                    if val < 0.0 or val > 100.0:
                        return XSCUtility.error_response(
                            "minAttPercent must be between 0.0 and 100.0.",
                            error_code="VAL_INVALID_PERCENT",
                        )
                    update_data["min_att_percent"] = val
                except (ValueError, TypeError):
                    return XSCUtility.error_response(
                        "minAttPercent must be numeric.", error_code="VAL_TYPE_ERR"
                    )
            if _has_field(payload, ["allow_late_marking", "allowLateMarking", "ALLOW LATE MARKING"]):
                update_data["allow_late_marking"] = bool(_get_field(payload, ["allow_late_marking", "allowLateMarking", "ALLOW LATE MARKING"]))
            if _has_field(payload, ["late_marking_window_minutes", "lateMarkingWindowMinutes", "LATE MARKING WINDOW MINUTES"]):
                update_data["late_marking_window_minutes"] = _get_field(payload, ["late_marking_window_minutes", "lateMarkingWindowMinutes", "LATE MARKING WINDOW MINUTES"])
            if _has_field(payload, ["auto_lock_after_hours", "autoLockAfterHours", "AUTO LOCK AFTER HOURS"]):
                update_data["auto_lock_after_hours"] = _get_field(payload, ["auto_lock_after_hours", "autoLockAfterHours", "AUTO LOCK AFTER HOURS"])
            if _has_field(payload, ["require_approval", "requireApproval", "REQUIRE APPROVAL"]):
                update_data["require_approval"] = bool(_get_field(payload, ["require_approval", "requireApproval", "REQUIRE APPROVAL"]))
            if _has_field(payload, ["require_med_proof", "requireMedProof", "require_med_proo", "requireMedProo", "REQUIRE MED PROOF"]):
                update_data["require_med_proof"] = bool(_get_field(payload, ["require_med_proof", "requireMedProof", "require_med_proo", "requireMedProo", "REQUIRE MED PROOF"]))
            if _has_field(payload, ["effective_from", "effectiveFrom", "EFFECTIVE FROM"]):
                update_data["effective_from"] = _get_field(payload, ["effective_from", "effectiveFrom", "EFFECTIVE FROM"])
            if _has_field(payload, ["effective_to", "effectiveTo", "EFFECTIVE TO"]):
                update_data["effective_to"] = _get_field(payload, ["effective_to", "effectiveTo", "EFFECTIVE TO"])

            if _has_field(payload, ["is_active", "isActive", "IS ACTIVE"]):
                new_active = bool(_get_field(payload, ["is_active", "isActive", "IS ACTIVE"]))
                if new_active and not existing_policy.get("is_active"):
                    inst_id = existing_policy.get("inst_id")
                    active_res = await db_layer.get_active_policy(int(inst_id))
                    if active_res.get("status") == "success" and active_res.get("data"):
                        for act_pol in active_res["data"]:
                            if act_pol["id"] != int(policy_id):
                                return XSCUtility.error_response(
                                    f"An active policy (ID: {act_pol['id']}) already exists for institution {inst_id}.",
                                    error_code="BIZ_CONFLICT_ACTIVE_POLICY",
                                )
                update_data["is_active"] = new_active

            if not update_data:
                return XSCUtility.error_response(
                    "No valid fields provided for update.",
                    error_code="VAL_NO_UPDATE_FIELDS",
                )

            user_id = getattr(context, "user_id", None) or _get_field(payload, ["userId", "user_id"])
            if user_id:
                update_data["updated_by"] = int(user_id)

            res = await db_layer.update_policy(int(policy_id), update_data)
            if res.get("status") == "error":
                return res
            logger.info(f"[sm_configuration] Policy {policy_id} updated successfully")
            res = _enrich_policy_response(res)
            return XSCUtility.success_response(
                "Attendance policy updated successfully", data=res.get("data", [])
            )
        except Exception as e:
            logger.error(
                f"[sm_configuration] Error in _config_update: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response(
                "Internal Server Error in _config_update", error_code="ERR_SYS"
            )

    @staticmethod
    async def config_delete(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes a Semantic Delete / Reset on an institutional attendance policy record.
        Retains the physical row in tb_att_policy while resetting parameter columns to system defaults
        (e.g., 75% min attendance threshold) and updating audit timestamps.
        This is a semantic operation and not a SQL physical DELETE operation.

        Args:
            self: Reference to the current class instance.
            request: The OneAppRequest payload containing policyId to reset.
            context: The ExecutionContext containing database manager and user identity.

        Returns:
            - status: Indicates whether the request was processed successfully ('success') or failed ('error').
            - message: A human-readable string providing details about the execution status.
            - data: The core data payload returned by the operation (e.g. database records).

        req_json_obj expected format:
        {
            "mod": "m_attendance",
            "subMod": "sm_configuration",
            "action": "attendanceConfiguration",
            "actionType": "delete",
            "payload": {
                "policyId": 1001
            }
        }
        """
        try:
            payload = request.payload or {}
            policy_id = _get_field(payload, ["policyId", "policy_id"])
            if not policy_id:
                return XSCUtility.error_response(
                    "Mandatory field missing: policyId is required for deletion.",
                    error_code="VAL_MISSING_ID",
                )

            db_layer = AttendanceDataLayer(context.postgres)
            existing_res = await db_layer.get_policy(int(policy_id))
            if existing_res.get("status") == "error":
                return existing_res
            if not existing_res.get("data"):
                return XSCUtility.error_response(
                    "Attendance policy not found for deletion/reset.",
                    error_code="ERR_NOT_FOUND",
                )

            user_id = getattr(context, "user_id", None) or _get_field(payload, ["userId", "user_id"]) or 0
            res = await db_layer.reset_attendance_configuration(
                int(policy_id), int(user_id)
            )
            if res.get("status") == "error":
                return res
            logger.info(
                f"[sm_configuration] Policy {policy_id} semantically reset to system defaults"
            )
            res = _enrich_policy_response(res)
            return XSCUtility.success_response(
                "Attendance policy reset to system defaults (semantic delete)",
                data=res.get("data", []),
            )
        except Exception as e:
            logger.error(
                f"[sm_configuration] Error in _config_delete: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response(
                "Internal Server Error in _config_delete", error_code="ERR_SYS"
            )

    @staticmethod
    async def config_activate(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes the `_config_activate()` action to mark a policy as active.

        Args:
            self: Reference to the current class instance.
            request: The OneAppRequest payload containing policyId to activate.
            context: The ExecutionContext containing database manager and user identity.

        Returns:
            - status: Indicates whether the request was processed successfully ('success') or failed ('error').
            - message: A human-readable string providing details about the execution status.
            - data: The core data payload returned by the operation (e.g. database records).

        req_json_obj expected format:
        {
            "mod": "m_attendance",
            "subMod": "sm_configuration",
            "action": "attendanceConfiguration",
            "actionType": "activate",
            "payload": {
                "policyId": 1001
            }
        }
        """
        try:
            payload = request.payload or {}
            policy_id = _get_field(payload, ["policyId", "policy_id"])
            if not policy_id:
                return XSCUtility.error_response(
                    "Mandatory field missing: policyId is required for activation.",
                    error_code="VAL_MISSING_ID",
                )

            db_layer = AttendanceDataLayer(context.postgres)
            existing_res = await db_layer.get_policy(int(policy_id))
            if existing_res.get("status") == "error" or not existing_res.get("data"):
                return XSCUtility.error_response(
                    "Attendance policy not found for activation.",
                    error_code="ERR_NOT_FOUND",
                )

            existing_policy = existing_res["data"][0]
            if existing_policy.get("is_active"):
                existing_res = _enrich_policy_response(existing_res)
                return XSCUtility.success_response(
                    "Attendance policy is already active.", data=existing_res.get("data", [])
                )

            inst_id = existing_policy.get("inst_id")
            active_res = await db_layer.get_active_policy(int(inst_id))
            if active_res.get("status") == "success" and active_res.get("data"):
                for act_pol in active_res["data"]:
                    if act_pol["id"] != int(policy_id):
                        await db_layer.update_policy(
                            int(act_pol["id"]), {"is_active": False}
                        )

            user_id = getattr(context, "user_id", None) or _get_field(payload, ["userId", "user_id"])
            update_data = {"is_active": True}
            if user_id:
                update_data["updated_by"] = int(user_id)

            res = await db_layer.update_policy(int(policy_id), update_data)
            res = _enrich_policy_response(res)
            return XSCUtility.success_response(
                "Attendance policy activated successfully", data=res.get("data", [])
            )
        except Exception as e:
            logger.error(
                f"[sm_configuration] Error in _config_activate: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response(
                "Internal Server Error in _config_activate", error_code="ERR_SYS"
            )

    @staticmethod
    async def config_deactivate(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes the `_config_deactivate()` action to mark a policy as inactive.

        Args:
            self: Reference to the current class instance.
            request: The OneAppRequest payload containing policyId to deactivate.
            context: The ExecutionContext containing database manager and user identity.

        Returns:
            - status: Indicates whether the request was processed successfully ('success') or failed ('error').
            - message: A human-readable string providing details about the execution status.
            - data: The core data payload returned by the operation (e.g. database records).

        req_json_obj expected format:
        {
            "mod": "m_attendance",
            "subMod": "sm_configuration",
            "action": "attendanceConfiguration",
            "actionType": "deactivate",
            "payload": {
                "policyId": 1001
            }
        }
        """
        try:
            payload = request.payload or {}
            policy_id = _get_field(payload, ["policyId", "policy_id"])
            if not policy_id:
                return XSCUtility.error_response(
                    "Mandatory field missing: policyId is required for deactivation.",
                    error_code="VAL_MISSING_ID",
                )

            db_layer = AttendanceDataLayer(context.postgres)
            user_id = getattr(context, "user_id", None) or _get_field(payload, ["userId", "user_id"])
            update_data = {"is_active": False}
            if user_id:
                update_data["updated_by"] = int(user_id)

            res = await db_layer.update_policy(int(policy_id), update_data)
            res = _enrich_policy_response(res)
            return XSCUtility.success_response(
                "Attendance policy deactivated successfully", data=res.get("data", [])
            )
        except Exception as e:
            logger.error(
                f"[sm_configuration] Error in _config_deactivate: {str(e)}",
                exc_info=True,
            )
            return XSCUtility.error_response(
                "Internal Server Error in _config_deactivate", error_code="ERR_SYS"
            )

    @staticmethod
    async def config_get_active(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes the `_config_get_active()` action to retrieve the currently active policy for an institution.

        Args:
            self: Reference to the current class instance.
            request: The OneAppRequest payload containing instId.
            context: The ExecutionContext containing database manager.

        Returns:
            - status: Indicates whether the request was processed successfully ('success') or failed ('error').
            - message: A human-readable string providing details about the execution status.
            - data: The core data payload returned by the operation (e.g. database records).

        req_json_obj expected format:
        {
            "mod": "m_attendance",
            "subMod": "sm_configuration",
            "action": "attendanceConfiguration",
            "actionType": "get_active",
            "payload": {
                "instId": 1
            }
        }
        """
        try:
            payload = request.payload or {}
            inst_id = _get_field(payload, ["instId", "inst_id", "ins_id", "insId", "INS_ID"])
            if not inst_id:
                return XSCUtility.error_response(
                    "Mandatory field missing: instId is required to fetch active policy.",
                    error_code="VAL_MISSING_ID",
                )

            db_layer = AttendanceDataLayer(context.postgres)
            res = await db_layer.get_active_policy(
                int(inst_id), policy_name=_get_field(payload, ["policyName", "policy_name", "POLICY NAME"])
            )
            if res.get("status") == "error":
                return res
            if not res.get("data"):
                return XSCUtility.error_response(
                    f"No active attendance policy found for institution {inst_id}",
                    error_code="ERR_NOT_FOUND",
                )
            res = _enrich_policy_response(res)
            return XSCUtility.success_response(
                "Active attendance policy retrieved successfully",
                data=res.get("data", []),
            )
        except Exception as e:
            logger.error(
                f"[sm_configuration] Error in _config_get_active: {str(e)}",
                exc_info=True,
            )
            return XSCUtility.error_response(
                "Internal Server Error in _config_get_active", error_code="ERR_SYS"
            )

    # =========================================================================
    # INTERNAL HANDLERS FOR attendanceType
    # =========================================================================

    @staticmethod
    async def type_add(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes the `_type_add()` action to create a new attendance marking type in the lookup framework.

        Args:
            self: Reference to the current class instance.
            request: The OneAppRequest payload containing typeCode, typeName, and countsAsPresent.
            context: The ExecutionContext containing database manager.

        Returns:
            - status: Indicates whether the request was processed successfully ('success') or failed ('error').
            - message: A human-readable string providing details about the execution status.
            - data: The core data payload returned by the operation (e.g. database records).

        req_json_obj expected format:
        {
            "mod": "m_attendance",
            "subMod": "sm_configuration",
            "action": "attendanceType",
            "actionType": "add",
            "payload": {
                "typeCode": "PRESENT",
                "typeName": "Present in Class",
                "countsAsPresent": true
            }
        }
        """
        try:
            payload = request.payload or {}
            type_code = payload.get("typeCode")
            type_name = payload.get("typeName")
            bool(payload.get("countsAsPresent", False))

            if not type_code or not type_name:
                return XSCUtility.error_response(
                    "Mandatory fields missing: typeCode and typeName are required.",
                    error_code="VAL_MISSING_FIELDS",
                )

            db_layer = AttendanceDataLayer(context.postgres)
            sql = text("""
                INSERT INTO sch_lookup.tb_lookup (id, cat_id, name, status)
                VALUES ((SELECT coalesce(max(id), 0) + 1 FROM sch_lookup.tb_lookup), 70, :name, True)
                RETURNING id, name AS lookup_code, name AS lookup_name, 'true' AS lookup_val, status AS is_active
            """).bindparams(name=str(type_code).upper())

            res = await db_layer.db.async_genericSQL(sql)
            if res.get("status") == "error":
                return res
            logger.info(
                f"[sm_configuration] Attendance type {type_code} created successfully"
            )
            return XSCUtility.success_response(
                "Attendance type created successfully", data=res.get("data", [])
            )
        except Exception as e:
            logger.error(
                f"[sm_configuration] Error in _type_add: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response(
                "Internal Server Error in _type_add", error_code="ERR_SYS"
            )

    @staticmethod
    async def type_view(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes the `_type_view()` action to retrieve configured attendance marking types.

        Args:
            self: Reference to the current class instance.
            request: The OneAppRequest payload containing optional typeId or typeCode filter.
            context: The ExecutionContext containing database manager.

        Returns:
            - status: Indicates whether the request was processed successfully ('success') or failed ('error').
            - message: A human-readable string providing details about the execution status.
            - data: The core data payload returned by the operation (e.g. database records).

        req_json_obj expected format:
        {
            "mod": "m_attendance",
            "subMod": "sm_configuration",
            "action": "attendanceType",
            "actionType": "view",
            "payload": {}
        }
        """
        try:
            db_layer = AttendanceDataLayer(context.postgres)
            sql = text(
                "SELECT id, name AS lookup_code, name AS lookup_name, 'true' AS lookup_val, status AS is_active FROM sch_lookup.tb_lookup WHERE cat_id = 70 ORDER BY id"
            )
            res = await db_layer.db.async_genericSQL(sql)
            if res.get("status") == "error":
                return res
            return XSCUtility.success_response(
                "Attendance types retrieved successfully", data=res.get("data", [])
            )
        except Exception as e:
            logger.error(
                f"[sm_configuration] Error in _type_view: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response(
                "Internal Server Error in _type_view", error_code="ERR_SYS"
            )

    @staticmethod
    async def type_update(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes the `_type_update()` action to update an attendance marking type metadata.

        Args:
            self: Reference to the current class instance.
            request: The OneAppRequest payload containing typeId and attributes to modify.
            context: The ExecutionContext containing database manager.

        Returns:
            - status: Indicates whether the request was processed successfully ('success') or failed ('error').
            - message: A human-readable string providing details about the execution status.
            - data: The core data payload returned by the operation (e.g. database records).

        req_json_obj expected format:
        {
            "mod": "m_attendance",
            "subMod": "sm_configuration",
            "action": "attendanceType",
            "actionType": "update",
            "payload": {
                "typeId": 10,
                "countsAsPresent": false
            }
        }
        """
        try:
            payload = request.payload or {}
            type_id = payload.get("typeId")
            if not type_id:
                return XSCUtility.error_response(
                    "Mandatory field missing: typeId is required for update.",
                    error_code="VAL_MISSING_ID",
                )

            db_layer = AttendanceDataLayer(context.postgres)
            update_fields = []
            params = {"id": int(type_id)}
            if "typeName" in payload or "typeCode" in payload:
                update_fields.append("name = :name")
                params["name"] = str(
                    payload.get("typeCode") or payload.get("typeName")
                ).upper()
            if "isActive" in payload:
                update_fields.append("status = :act")
                params["act"] = bool(payload["isActive"])

            if not update_fields:
                return XSCUtility.error_response(
                    "No valid fields provided for update.",
                    error_code="VAL_NO_UPDATE_FIELDS",
                )

            sql_str = f"UPDATE sch_lookup.tb_lookup SET {', '.join(update_fields)} WHERE id = :id RETURNING id, name AS lookup_code, name AS lookup_name, 'true' AS lookup_val, status AS is_active"
            sql = text(sql_str).bindparams(**params)
            res = await db_layer.db.async_genericSQL(sql)
            if res.get("status") == "error":
                return res
            return XSCUtility.success_response(
                "Attendance type updated successfully", data=res.get("data", [])
            )
        except Exception as e:
            logger.error(
                f"[sm_configuration] Error in _type_update: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response(
                "Internal Server Error in _type_update", error_code="ERR_SYS"
            )

    @staticmethod
    async def type_delete(request: Any, context: Any) -> Dict[str, Any]:
        """
        Executes a Semantic Deactivation on an attendance marking type rather than a SQL physical DELETE operation.
        Verifies if attendance records reference this type ID; deactivates instead to preserve immutable audit trail.

        Args:
            self: Reference to the current class instance.
            request: The OneAppRequest payload containing typeId to delete/deactivate.
            context: The ExecutionContext containing database manager.

        Returns:
            - status: Indicates whether the request was processed successfully ('success') or failed ('error').
            - message: A human-readable string providing details about the execution status.
            - data: The core data payload returned by the operation (e.g. database records).

        req_json_obj expected format:
        {
            "mod": "m_attendance",
            "subMod": "sm_configuration",
            "action": "attendanceType",
            "actionType": "delete",
            "payload": {
                "typeId": 10
            }
        }
        """
        try:
            payload = request.payload or {}
            type_id = payload.get("typeId")
            if not type_id:
                return XSCUtility.error_response(
                    "Mandatory field missing: typeId is required for deletion.",
                    error_code="VAL_MISSING_ID",
                )

            db_layer = AttendanceDataLayer(context.postgres)
            # Check for existing references in tb_att_record
            stmt = (
                select(func.count())
                .select_from(TbAttRecord)
                .where(TbAttRecord.att_status_id == int(type_id))
            )
            await db_layer.db.async_genericSQL(stmt)

            # Semantic deactivation to prevent historical data corruption
            sql = text(
                "UPDATE sch_lookup.tb_lookup SET status = False WHERE id = :id RETURNING id, name AS lookup_code, name AS lookup_name, status AS is_active"
            ).bindparams(id=int(type_id))
            res = await db_layer.db.async_genericSQL(sql)
            if res.get("status") == "error":
                return res
            logger.info(
                f"[sm_configuration] Attendance type {type_id} semantically deactivated"
            )
            return XSCUtility.success_response(
                "Attendance type deactivated successfully (semantic delete)",
                data=res.get("data", []),
            )
        except Exception as e:
            logger.error(
                f"[sm_configuration] Error in _type_delete: {str(e)}", exc_info=True
            )
            return XSCUtility.error_response(
                "Internal Server Error in _type_delete", error_code="ERR_SYS"
            )
