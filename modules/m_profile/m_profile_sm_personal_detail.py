"""
File: m_profile_sm_personal_detail.py
Description: Personal Detail and Academic Identifier submodule for m_profile.

Author: EduCore
App: OneApp

"""

import re
from datetime import datetime, timedelta
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from .m_profile_data import ProfileDataLayer

# Grace window (days) within which sensitive fields can be edited directly.
SENSITIVE_FIELD_GRACE_DAYS = 14
SENSITIVE_FIELDS = {"dob", "gender_id", "nationality_id"}

# Strict mapping from lookup category 15 (IDENTIFIER_TYPE)
IDENTIFIER_TYPE_MAP = {
    148: "AADHAAR NUMBER",
    149: "PAN NUMBER",
    150: "PASSPORT NUMBER",
    151: "DRIVING LICENSE NUMBER",
    152: "EMPLOYEE ID",
    153: "STUDENT ID",
    154: "STAFF ID",
    155: "NATIONAL ID",
    156: "TAX ID",
    157: "VISA NUMBER",
    158: "OTHER"
}

def get_identifier_type_name(identifier_value: str, identifier_type_id: int) -> str:
    """
    Validates the identifier value format and type ID, returning the name of the ID
    strictly following the SCH_LOOKUP Excel specification.

    Args:
        identifier_value (str): The alphanumeric identifier value.
        identifier_type_id (int): The numeric lookup ID.

    Returns:
        str: The name of the ID type.

    Raises:
        ValueError: If validation fails or type ID is unknown.
    """
    try:
        type_id = int(identifier_type_id)
    except (ValueError, TypeError):
        raise ValueError("identifier_type_id must be an integer.")

    if type_id not in IDENTIFIER_TYPE_MAP:
        raise ValueError(f"Unknown identifier_type_id: {type_id}. Must be between 148 and 158.")

    if not isinstance(identifier_value, str) or not identifier_value.strip():
        raise ValueError("identifier_value must be a non-empty string.")

    val_clean = identifier_value.strip()

    # Aadhaar Number Validation (12 digits, optional spaces/hyphens allowed but stripped)
    if type_id == 148:
        digits_only = re.sub(r"[\s-]", "", val_clean)
        if not re.match(r"^\d{12}$", digits_only):
            raise ValueError("Invalid Aadhaar Number format. Expected 12 digits.")

    # PAN Number Validation (10 characters: 5 letters, 4 digits, 1 letter)
    elif type_id == 149:
        if not re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", val_clean.upper()):
            raise ValueError("Invalid PAN Number format. Expected format: ABCDE1234F.")

    # Passport Number Validation (8-9 alphanumeric characters)
    elif type_id == 150:
        if not re.match(r"^[A-Z0-9]{8,9}$", val_clean.upper()):
            raise ValueError("Invalid Passport Number format. Expected 8-9 alphanumeric characters.")

    return IDENTIFIER_TYPE_MAP[type_id]



class personalDetail:
    """
    Action class for personal detail CRUD.

    Request format:
    {
        "mod": "m_profile",
        "subMod": "sm_personal_detail",
        "action": "personalDetail",
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
                    f"Unsupported actionType '{action_type}' for personalDetail"
                )

    # --------------------------------------------------------------------- add
    async def add(self, payload, dal, context):
        user_id = payload.get("userId")
        if not user_id:
            return XSCUtility.error_response("userId is required")

        # Verify user exists in m_aaa
        if not await dal.user_exists(user_id):
            return XSCUtility.error_response("User does not exist in m_aaa")

        # Verify profile not already created
        if await dal.profile_exists(user_id):
            return XSCUtility.error_response(
                "Personal detail record already exists for this user"
            )

        # Mandatory field validation
        first_name = payload.get("firstName")
        last_name = payload.get("lastName")
        dob = payload.get("dob")
        gender_id = payload.get("genderId")
        mobile = payload.get("mobile")

        if not all([first_name, last_name, dob, gender_id, mobile]):
            return XSCUtility.error_response(
                "Missing mandatory fields: firstName, lastName, dob, genderId, mobile"
            )

        # Mobile uniqueness check
        if await dal.check_mobile_unique(mobile):
            return XSCUtility.error_response("Mobile number is already in use")

        # Build profile insert data
        profile_data = {
            "user_id": user_id,
            "f_name": first_name,
            "m_name": payload.get("middleName"),
            "l_name": last_name,
            "dob": dob,
            "gender_id": gender_id,
            "profile_photo_id": payload.get("photoDocId"),
            "nationality_id": payload.get("nationalityId"),
            "primary_lang_id": payload.get("primaryLangId"),
        }

        result = await dal.insert_user_profile(profile_data)
        if result.get("status") == "error":
            return XSCUtility.error_response("Failed to save personal detail")

        # Update mobile on tb_user
        await dal.update_user_mobile(user_id, mobile)

        # Insert blood_group if provided
        blood_group_id = payload.get("bloodGroupId")
        if blood_group_id:
            from sqlalchemy import text

            med_stmt = text("""
                INSERT INTO sch_iam.tb_user_med (user_id, blood_group_id)
                VALUES (:user_id, :blood_group_id)
                ON CONFLICT (user_id) DO UPDATE SET blood_group_id = :blood_group_id
            """)
            await dal._safe_query(
                med_stmt, {"user_id": user_id, "blood_group_id": blood_group_id}
            )

        return XSCUtility.success_response(
            "Personal detail created successfully", {"userId": user_id}
        )

    # -------------------------------------------------------------------- view
    async def view(self, payload, dal, context):
        user_id = payload.get("userId") or (
            context.security.user_id
            if context and hasattr(context, "security") and context.security
            else None
        )

        if user_id:
            # Single user view
            profile = await dal.get_personal_detail(user_id)
            if profile is None:
                return XSCUtility.error_response("Profile not found")
            return XSCUtility.success_response("Personal detail retrieved", profile)

        # Directory view (for admin/HOD)
        # Placeholder: returns empty until directory search is implemented
        return XSCUtility.success_response("Directory view not yet implemented", [])

    # ------------------------------------------------------------------ update
    async def update(self, payload, dal, context):
        user_id = payload.get("userId")
        if not user_id:
            return XSCUtility.error_response("userId is required")

        if not await dal.profile_exists(user_id):
            return XSCUtility.error_response("Profile not found for this user")

        fields_to_update = payload.get("fieldsToUpdate", {})
        if not fields_to_update:
            return XSCUtility.error_response("No fields provided to update")

        # Mobile uniqueness check if mobile is being updated
        new_mobile = fields_to_update.pop("mobile", None)
        if new_mobile:
            if await dal.check_mobile_unique(new_mobile, exclude_user_id=user_id):
                return XSCUtility.error_response("Mobile number is already in use")
            await dal.update_user_mobile(user_id, new_mobile)

        # Grace-window check for sensitive fields
        sensitive_changes = {
            k: v for k, v in fields_to_update.items() if k in SENSITIVE_FIELDS
        }
        non_sensitive_changes = {
            k: v for k, v in fields_to_update.items() if k not in SENSITIVE_FIELDS
        }

        if sensitive_changes:
            created_at = await dal.get_profile_created_at(user_id)
            if created_at:
                if isinstance(created_at, str):
                    try:
                        created_at = datetime.fromisoformat(created_at)
                    except ValueError:
                        created_at = None
                if created_at:
                    grace_deadline = created_at + timedelta(
                        days=SENSITIVE_FIELD_GRACE_DAYS
                    )
                    now = datetime.utcnow()
                    if hasattr(grace_deadline, "replace"):
                        grace_deadline = grace_deadline.replace(tzinfo=None)
                    if now > grace_deadline:
                        return XSCUtility.error_response(
                            "Sensitive field changes require Institution Admin approval after the grace window",
                            error_code="GRACE_WINDOW_EXPIRED",
                        )

        # Merge and apply all allowed updates
        all_profile_fields = {**non_sensitive_changes, **sensitive_changes}

        # Map BRS logical names to DB column names
        column_map = {
            "firstName": "f_name",
            "middleName": "m_name",
            "lastName": "l_name",
            "dob": "dob",
            "genderId": "gender_id",
            "gender_id": "gender_id",
            "photoDocId": "profile_photo_id",
            "nationalityId": "nationality_id",
            "nationality_id": "nationality_id",
            "primaryLangId": "primary_lang_id",
        }
        db_fields = {}
        for k, v in all_profile_fields.items():
            col = column_map.get(k, k)
            db_fields[col] = v

        if db_fields:
            result = await dal.update_user_profile(user_id, db_fields)
            if result.get("status") == "error":
                return XSCUtility.error_response("Failed to update personal detail")

        return XSCUtility.success_response("Personal detail updated successfully")

    # ------------------------------------------------------------------ delete
    async def delete(self, payload, dal, context):
        user_id = payload.get("userId")
        reason = payload.get("reason", "Not specified")

        if not user_id:
            return XSCUtility.error_response("userId is required")

        if not await dal.profile_exists(user_id):
            return XSCUtility.error_response("Profile not found for this user")

        result = await dal.anonymise_personal_detail(user_id)
        if result.get("status") == "error":
            return XSCUtility.error_response("Failed to anonymise personal detail")

        return XSCUtility.success_response(
            "Personal detail anonymised successfully", {"reason": reason}
        )


class sm_personal_detail:
    """
    Framework Submodule Wrapper class for sm_personal_detail.
    Routes action calls to action class personalDetail.
    """

    @staticmethod
    async def personalDetail(request, context):
        return await personalDetail().execute(request, context)


# Alias for legacy camelCase class reference
sm_personalDetail = sm_personal_detail

