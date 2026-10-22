"""
File: m_profile_sm_medical_detail.py
Description: Medical Detail submodule for m_profile.

Author: EduCore
App: OneApp

"""

import json
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from .m_profile_data import ProfileDataLayer


class medicalDetail:
    """
    Action class for medical detail CRUD.
    Applies to any user type. Enforces strict access control.

    Request format:
    {
        "mod": "m_profile",
        "subMod": "sm_medical_detail",
        "action": "medicalDetail",
        "actionType": "<add|view|update|delete>",
        "payload": { ... }
    }
    """

    async def execute(self, request, context):
        action_type = request.actionType.lower()
        dal = ProfileDataLayer(context.postgres)

        match action_type:
            case "add":
                return await self.add(request.payload or {}, dal, context)
            case "view":
                return await self.view(request.payload or {}, dal, context)
            case "update":
                return await self.update(request.payload or {}, dal, context)
            case "delete":
                return await self.delete(request.payload or {}, dal, context)
            case _:
                return XSCUtility.error_response(
                    f"Unsupported actionType '{action_type}' for medicalDetail"
                )

    def _check_access(self, context, target_user_id):
        """
        Verifies the requesting user has permission to access medical data.
        Only self, Medical Officer, or Designated Emergency Staff may access.
        Returns (allowed: bool, reason: str).
        """
        requesting_user_id = None
        roles = []
        if context and hasattr(context, "security") and context.security:
            requesting_user_id = context.security.user_id
            roles = context.security.roles or []

        upper_roles = {str(r).upper() for r in roles}

        # Self-access is always allowed
        if requesting_user_id and str(requesting_user_id) == str(target_user_id):
            return True, "self"

        # Medical Officer, Emergency Staff, or Admin access
        allowed_roles = {
            "MEDICAL_OFFICER",
            "EMERGENCY_STAFF",
            "ADMIN",
            "SUPER_ADMIN",
            "SYSTEM_ADMIN",
        }
        if allowed_roles.intersection(upper_roles):
            return True, "role"

        if not requesting_user_id and not roles:
            return (
                False,
                "Access denied: Missing or invalid 'Authorization: Bearer <jwt_token>' header. Medical records require authentication.",
            )

        return (
            False,
            "Access denied: Only self, Medical Officer, or Emergency Staff may access medical records",
        )

    def _serialize_list(self, value):
        """Converts a list to a JSON string for TEXT column storage."""
        if value is None:
            return None
        if isinstance(value, list):
            return json.dumps(value)
        return str(value)

    def _deserialize_list(self, value):
        """Converts a JSON string from a TEXT column back to a list."""
        if value is None:
            return []
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else [parsed]
        except (json.JSONDecodeError, TypeError):
            return [value] if value else []

    # --------------------------------------------------------------------- add
    async def add(self, payload, dal, context):
        user_id = payload.get("userId")
        if not user_id:
            return XSCUtility.error_response("userId is required")

        if not await dal.profile_exists(user_id):
            return XSCUtility.error_response(
                "personalDetail must exist before creating medicalDetail"
            )

        # Check if a record already exists
        existing = await dal.get_medical_detail(user_id)
        if existing.get("data"):
            return XSCUtility.error_response(
                "A medical detail record already exists for this user"
            )

        # Serialize structured lists into TEXT columns
        allergies = self._serialize_list(payload.get("allergies"))
        chronic_conditions = self._serialize_list(payload.get("chronicConditions"))
        medications = self._serialize_list(payload.get("medications"))

        # Pack doctor/insurance info into emergency_note as JSON since
        # dedicated columns don't exist in the current schema
        extra_info = {}
        if payload.get("doctorName"):
            extra_info["doctorName"] = payload["doctorName"]
        if payload.get("doctorContact"):
            extra_info["doctorContact"] = payload["doctorContact"]
        if payload.get("insurancePolicyNo"):
            extra_info["insurancePolicyNo"] = payload["insurancePolicyNo"]
        if medications:
            extra_info["medications"] = payload.get("medications", [])

        emergency_note = json.dumps(extra_info) if extra_info else None

        data = {
            "user_id": user_id,
            "blood_group_id": payload.get("bloodGroupId"),
            "allergy_info": allergies,
            "med_condition": chronic_conditions,
            "emergency_note": emergency_note,
        }

        result = await dal.create_medical_detail(data)
        if result.get("status") == "error":
            return XSCUtility.error_response("Failed to create medical detail record")

        return XSCUtility.success_response("Medical detail created successfully")

    # -------------------------------------------------------------------- view
    async def view(self, payload, dal, context):
        user_id = payload.get("userId")
        if not user_id:
            return XSCUtility.error_response("userId is required")

        # Access control check
        allowed, reason = self._check_access(context, user_id)
        if not allowed:
            # Log the denied access attempt
            if context.logger:
                context.logger.app(
                    f"Medical record access DENIED for user {user_id} by {context.security.user_id if context.security else 'unknown'}"
                )
            return XSCUtility.error_response(reason)

        # Log the successful access attempt
        if context.logger:
            requesting_id = context.security.user_id if context.security else "unknown"
            context.logger.app(
                f"Medical record access GRANTED for user {user_id} by {requesting_id} ({reason})"
            )

        result = await dal.get_medical_detail(user_id)
        row = result.get("data", [None])[0] if result.get("data") else None

        if not row:
            return XSCUtility.success_response("No medical detail found", None)

        # Deserialize structured fields for the response
        response_data = {
            "userId": row.get("user_id"),
            "bloodGroupId": row.get("blood_group_id"),
            "bloodGroup": row.get("blood_group_name"),
            "bloodGroupName": row.get("blood_group_name"),
            "allergies": self._deserialize_list(row.get("allergy_info")),
            "chronicConditions": self._deserialize_list(row.get("med_condition")),
            "height": row.get("height"),
            "weight": row.get("weight"),
            "disabilityTypeId": row.get("disability_type_id"),
            "disabilityType": row.get("disability_type_name"),
            "disabilityTypeName": row.get("disability_type_name"),
        }

        # Unpack extra info from emergency_note
        emergency_note = row.get("emergency_note")
        if emergency_note:
            try:
                extra = json.loads(emergency_note)
                response_data["medications"] = extra.get("medications", [])
                response_data["doctorName"] = extra.get("doctorName")
                response_data["doctorContact"] = extra.get("doctorContact")
                response_data["insurancePolicyNo"] = extra.get("insurancePolicyNo")
            except (json.JSONDecodeError, TypeError):
                response_data["emergencyNote"] = emergency_note
        else:
            response_data.update(
                {
                    "medications": [],
                    "doctorName": None,
                    "doctorContact": None,
                    "insurancePolicyNo": None,
                }
            )

        return XSCUtility.success_response("Medical detail retrieved", response_data)

    # ------------------------------------------------------------------ update
    async def update(self, payload, dal, context):
        user_id = payload.get("userId")
        if not user_id:
            return XSCUtility.error_response("userId is required")

        allowed, reason = self._check_access(context, user_id)
        if not allowed:
            return XSCUtility.error_response(reason)

        fields = payload.get("fieldsToUpdate", {})
        if not fields:
            return XSCUtility.error_response("No fields provided to update")

        db_fields = {}
        if "bloodGroupId" in fields:
            db_fields["blood_group_id"] = fields["bloodGroupId"]
        if "allergies" in fields:
            db_fields["allergy_info"] = self._serialize_list(fields["allergies"])
        if "chronicConditions" in fields:
            db_fields["med_condition"] = self._serialize_list(
                fields["chronicConditions"]
            )

        # Handle extra info fields packed into emergency_note
        extra_keys = {"medications", "doctorName", "doctorContact", "insurancePolicyNo"}
        extra_changes = {k: v for k, v in fields.items() if k in extra_keys}
        if extra_changes:
            # Read existing emergency_note and merge
            existing = await dal.get_medical_detail(user_id)
            existing_row = existing.get("data", [{}])[0] if existing.get("data") else {}
            current_note = existing_row.get("emergency_note", "{}")
            try:
                note_data = json.loads(current_note) if current_note else {}
            except (json.JSONDecodeError, TypeError):
                note_data = {}
            note_data.update(extra_changes)
            db_fields["emergency_note"] = json.dumps(note_data)

        if db_fields:
            result = await dal.update_medical_detail(user_id, db_fields)
            if result.get("status") == "error":
                return XSCUtility.error_response("Failed to update medical detail")

        return XSCUtility.success_response("Medical detail updated successfully")

    # ------------------------------------------------------------------ delete
    async def delete(self, payload, dal, context):
        user_id = payload.get("userId")
        reason = payload.get("reason", "Not specified")

        if not user_id:
            return XSCUtility.error_response("userId is required")

        allowed, access_reason = self._check_access(context, user_id)
        if not allowed:
            return XSCUtility.error_response(access_reason)

        result = await dal.delete_medical_detail(user_id)
        if result.get("status") == "error":
            return XSCUtility.error_response("Failed to delete medical detail")

        return XSCUtility.success_response("Medical detail removed", {"reason": reason})


class sm_medical_detail:
    """
    Framework Submodule Wrapper class for sm_medical_detail.
    Routes action call to action class medicalDetail.
    """

    @staticmethod
    async def medicalDetail(request, context):
        return await medicalDetail().execute(request, context)


# Alias for legacy camelCase class reference
sm_medicalDetail = sm_medical_detail
