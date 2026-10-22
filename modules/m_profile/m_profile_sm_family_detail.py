"""
File: m_profile_sm_family_detail.py
Description: Family Detail and Emergency Contact submodule for m_profile.

Author: EduCore
App: OneApp

"""

from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from .m_profile_data import ProfileDataLayer


class familyDetail:
    """
    Action class for family/guardian detail CRUD.
    Scoped to students only.

    Request format:
    {
        "mod": "m_profile",
        "subMod": "sm_family_detail",
        "action": "familyDetail",
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
                    f"Unsupported actionType '{action_type}'"
                )

    # --------------------------------------------------------------------- add
    async def add(self, payload, dal, context):
        student_id = payload.get("studentId")
        if not student_id:
            return XSCUtility.error_response("studentId is required")

        # Mandatory fields
        relation = payload.get("relation")
        name = payload.get("name", "")
        mobile = payload.get("mobile")

        if not all([relation, name, mobile]):
            return XSCUtility.error_response(
                "Missing mandatory fields: relation, name, mobile"
            )

        # Parse name into first/last
        name_parts = name.strip().split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        is_emergency = payload.get("isEmergencyContact", False)

        # If marking as emergency contact, unset any existing one for this student
        if is_emergency:
            await dal.unset_emergency_contact_flag(student_id)

        # Validate annualIncome
        annual_income = payload.get("annualIncome")
        if annual_income is not None:
            try:
                annual_income = float(annual_income)
                if annual_income < 0:
                    return XSCUtility.error_response(
                        "annualIncome must be non-negative"
                    )
            except (ValueError, TypeError):
                return XSCUtility.error_response("annualIncome must be a valid number")

        par_data = {
            "user_id": None,  # Parent user account may not exist yet
            "first_name": first_name,
            "middle_name": None,
            "last_name": last_name,
            "gender_id": None,
            "mobile_no": mobile,
            "email": payload.get("email"),
            "occupation": payload.get("occupation"),
            "annual_income": annual_income,
            "status_id": 1,
        }

        link_data = {
            "stud_id": student_id,
            "relationship_type_id": relation,
            "is_primary_guardian": False,
            "is_emergency_contact": is_emergency,
        }

        result = await dal.create_family_detail(par_data, link_data)
        if result.get("status") == "error":
            return XSCUtility.error_response("Failed to create family detail record")

        return XSCUtility.success_response("Family detail created successfully")

    # -------------------------------------------------------------------- view
    async def view(self, payload, dal, context):
        student_id = payload.get("studentId")
        if not student_id:
            return XSCUtility.error_response("studentId is required")

        result = await dal.get_family_details(student_id)
        data = result.get("data", []) if result.get("status") == "success" else []

        return XSCUtility.success_response("Family details retrieved", data)

    # ------------------------------------------------------------------ update
    async def update(self, payload, dal, context):
        family_detail_id = payload.get("familyDetailId")
        if not family_detail_id:
            return XSCUtility.error_response("familyDetailId is required")

        fields = payload.get("fieldsToUpdate", {})
        if not fields:
            return XSCUtility.error_response("No fields provided to update")

        # Map BRS names to DB column names
        column_map = {
            "name": None,  # Handled separately
            "mobile": "mobile_no",
            "email": "email",
            "occupation": "occupation",
            "annualIncome": "annual_income",
        }

        db_fields = {}
        for k, v in fields.items():
            if k == "name":
                name_parts = str(v).strip().split(" ", 1)
                db_fields["first_name"] = name_parts[0]
                db_fields["last_name"] = name_parts[1] if len(name_parts) > 1 else ""
            elif k in column_map and column_map[k]:
                db_fields[column_map[k]] = v

        if db_fields:
            result = await dal.update_family_detail(family_detail_id, db_fields)
            if result.get("status") == "error":
                return XSCUtility.error_response("Failed to update family detail")

        return XSCUtility.success_response("Family detail updated successfully")

    # ------------------------------------------------------------------ delete
    async def delete(self, payload, dal, context):
        family_detail_id = payload.get("familyDetailId")
        reason = payload.get("reason", "Not specified")

        if not family_detail_id:
            return XSCUtility.error_response("familyDetailId is required")

        result = await dal.delete_family_detail(family_detail_id)
        if result.get("status") == "error":
            return XSCUtility.error_response("Failed to delete family detail")

        return XSCUtility.success_response("Family detail removed", {"reason": reason})


class emergencyContact:
    """
    Action class for emergency contact CRUD.
    Applies to any user type (student, faculty, staff).

    Request format:
    {
        "mod": "m_profile",
        "subMod": "sm_family_detail",
        "action": "emergencyContact",
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
                    f"Unsupported actionType '{action_type}' for emergencyContact"
                )

    # --------------------------------------------------------------------- add
    async def add(self, payload, dal, context):
        user_id = payload.get("userId")
        if not user_id:
            return XSCUtility.error_response("userId is required")

        # Mandatory fields
        name = payload.get("name", "")
        relation = payload.get("relation")
        mobile = payload.get("mobile")
        priority_order = payload.get("priorityOrder")

        if not all([name, relation, mobile, priority_order is not None]):
            return XSCUtility.error_response(
                "Missing mandatory fields: name, relation, mobile, priorityOrder"
            )

        # Parse name
        name_parts = name.strip().split(" ", 1)
        f_name = name_parts[0]
        l_name = name_parts[1] if len(name_parts) > 1 else ""

        # Use is_primary as a proxy for priority (primary = highest priority)
        is_primary = int(priority_order) == 1

        data = {
            "user_id": user_id,
            "f_name": f_name,
            "l_name": l_name,
            "mobile": mobile,
            "is_primary": is_primary,
            "status_id": 1,
        }

        result = await dal.create_emergency_contact(data)
        if result.get("status") == "error":
            return XSCUtility.error_response("Failed to create emergency contact")

        return XSCUtility.success_response("Emergency contact created successfully")

    # -------------------------------------------------------------------- view
    async def view(self, payload, dal, context):
        user_id = payload.get("userId")
        if not user_id:
            return XSCUtility.error_response("userId is required")

        result = await dal.get_emergency_contacts(user_id)
        data = result.get("data", []) if result.get("status") == "success" else []

        return XSCUtility.success_response("Emergency contacts retrieved", data)

    # ------------------------------------------------------------------ update
    async def update(self, payload, dal, context):
        contact_id = payload.get("contactId")
        if not contact_id:
            return XSCUtility.error_response("contactId is required")

        fields = payload.get("fieldsToUpdate", {})
        if not fields:
            return XSCUtility.error_response("No fields provided to update")

        # Map BRS names to DB columns
        db_fields = {}
        if "name" in fields:
            name_parts = str(fields["name"]).strip().split(" ", 1)
            db_fields["f_name"] = name_parts[0]
            db_fields["l_name"] = name_parts[1] if len(name_parts) > 1 else ""
        if "mobile" in fields:
            db_fields["mobile"] = fields["mobile"]
        if "priorityOrder" in fields:
            db_fields["is_primary"] = int(fields["priorityOrder"]) == 1

        if db_fields:
            result = await dal.update_emergency_contact(contact_id, db_fields)
            if result.get("status") == "error":
                return XSCUtility.error_response("Failed to update emergency contact")

        return XSCUtility.success_response("Emergency contact updated successfully")

    # ------------------------------------------------------------------ delete
    async def delete(self, payload, dal, context):
        contact_id = payload.get("contactId")
        if not contact_id:
            return XSCUtility.error_response("contactId is required")

        result = await dal.delete_emergency_contact(contact_id)
        if result.get("status") == "error":
            return XSCUtility.error_response("Failed to delete emergency contact")

        return XSCUtility.success_response("Emergency contact removed")


class sm_family_detail:
    """
    Framework Submodule Wrapper class for sm_family_detail.
    Routes action calls to action classes familyDetail and emergencyContact.
    """

    @staticmethod
    async def familyDetail(request, context):
        return await familyDetail().execute(request, context)

    @staticmethod
    async def emergencyContact(request, context):
        return await emergencyContact().execute(request, context)


# Alias for legacy camelCase class reference
sm_familyDetail = sm_family_detail
