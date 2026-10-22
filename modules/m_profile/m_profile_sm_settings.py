"""
File: m_profile_sm_settings.py
Description: User Preference / Settings submodule for m_profile.

Author: EduCore
App: OneApp

"""

from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from .m_profile_data import ProfileDataLayer

# Default preference values applied on first login or reset.
DEFAULT_PREFERENCES = {
    "language": "en",
    "theme": "light",
    "timezone": "UTC",
    "defaultLandingModule": "m_student",
}

# Mapping from logical preference key to a TB_LOOKUP preference_type_id.
# These IDs should match the institution's configured lookup entries.
PREFERENCE_TYPE_MAP = {
    "language": 1,
    "theme": 2,
    "timezone": 3,
    "defaultLandingModule": 4,
}


class userPreference:
    """
    Action class for user preference / settings CRUD.

    Request format:
    {
        "mod": "m_profile",
        "subMod": "sm_settings",
        "action": "userPreference",
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
                    f"Unsupported actionType '{action_type}' for userPreference"
                )

    # --------------------------------------------------------------------- add
    async def add(self, payload, dal, context):
        user_id = payload.get("userId")
        if not user_id:
            return XSCUtility.error_response("userId is required")

        if not await dal.profile_exists(user_id):
            return XSCUtility.error_response(
                "personalDetail must exist before creating preferences"
            )

        # Check if preferences already exist
        existing = await dal.get_user_preferences(user_id)
        if existing.get("data"):
            return XSCUtility.error_response("Preferences already exist for this user")

        # Use provided values or fall back to defaults
        prefs = {
            "language": payload.get("language", DEFAULT_PREFERENCES["language"]),
            "theme": payload.get("theme", DEFAULT_PREFERENCES["theme"]),
            "timezone": payload.get("timezone", DEFAULT_PREFERENCES["timezone"]),
            "defaultLandingModule": payload.get(
                "defaultLandingModule", DEFAULT_PREFERENCES["defaultLandingModule"]
            ),
        }

        for key, value in prefs.items():
            type_id = PREFERENCE_TYPE_MAP.get(key)
            if type_id:
                await dal.upsert_user_preference(user_id, type_id, str(value))

        return XSCUtility.success_response(
            "User preferences created with defaults", prefs
        )

    # -------------------------------------------------------------------- view
    async def view(self, payload, dal, context):
        user_id = payload.get("userId")
        if not user_id:
            return XSCUtility.error_response("userId is required")

        result = await dal.get_user_preferences(user_id)
        rows = result.get("data", []) if result.get("status") == "success" else []

        # Build a key-value map from the rows
        reverse_map = {v: k for k, v in PREFERENCE_TYPE_MAP.items()}
        prefs = dict(DEFAULT_PREFERENCES)  # Start with defaults

        for row in rows:
            type_id = row.get("preference_type_id")
            key = reverse_map.get(type_id)
            if key:
                prefs[key] = row.get("value", prefs.get(key))

        return XSCUtility.success_response("User preferences retrieved", prefs)

    # ------------------------------------------------------------------ update
    async def update(self, payload, dal, context):
        user_id = payload.get("userId")
        if not user_id:
            return XSCUtility.error_response("userId is required")

        fields = payload.get("fieldsToUpdate", {})
        if not fields:
            return XSCUtility.error_response("No fields provided to update")

        updated_keys = []
        for key, value in fields.items():
            type_id = PREFERENCE_TYPE_MAP.get(key)
            if type_id is None:
                continue  # Skip unknown preference keys

            await dal.upsert_user_preference(user_id, type_id, str(value))
            updated_keys.append(key)

        if not updated_keys:
            return XSCUtility.error_response("No valid preference keys provided")

        return XSCUtility.success_response(
            "User preferences updated", {"updated": updated_keys}
        )

    # ------------------------------------------------------------------ delete
    async def delete(self, payload, dal, context):
        user_id = payload.get("userId")
        if not user_id:
            return XSCUtility.error_response("userId is required")

        # Delete all existing preferences
        await dal.delete_user_preferences(user_id)

        # Re-create with platform defaults
        for key, value in DEFAULT_PREFERENCES.items():
            type_id = PREFERENCE_TYPE_MAP.get(key)
            if type_id:
                await dal.upsert_user_preference(user_id, type_id, str(value))

        return XSCUtility.success_response(
            "User preferences reset to platform defaults", DEFAULT_PREFERENCES
        )


class sm_settings:
    """
    Framework Submodule Wrapper class for sm_settings.
    Routes action call to action class userPreference.
    """

    @staticmethod
    async def userPreference(request, context):
        return await userPreference().execute(request, context)

    @staticmethod
    async def settings(request, context):
        return await userPreference().execute(request, context)
