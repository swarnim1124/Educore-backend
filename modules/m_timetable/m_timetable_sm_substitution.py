"""
File: m_timetable_sm_substitution.py
Description: Submodule handling Substitution operations for m_timetable.
             Action: substitution (add, view, update, delete).
             Maps to TB_CLASS_SESSION_CHANGE with change_type_id = 'FAC_CHANGE'.

Author: EduCore
App: OneApp
"""


class Substitution:
    """
    Submodule handler class for faculty substitution management.
    Tracks original-to-substitute faculty swaps for specific class sessions.
    """

    # =========================================================================
    # ACTION: substitution
    # BRS Feature: Faculty Substitution Management
    # =========================================================================

    async def substitution(self, action_type, payload, context):
        """
        Action method for faculty substitution.
        Creates, views, updates, and cancels faculty substitution records.
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from .m_timetable_data import TimetableDataLayer

        dal = TimetableDataLayer(
            context.postgres if hasattr(context, "postgres") else None
        )
        action_type = (action_type or "").lower()

        match action_type:
            case "add":
                return await self.substitution_add(payload, dal, context)
            case "view":
                return await self.substitution_view(payload, dal, context)
            case "update":
                return await self.substitution_update(payload, dal, context)
            case "delete":
                return await self.substitution_delete(payload, dal, context)
            case _:
                return XSCUtility.error_response(
                    message=f"Unsupported actionType '{action_type}' for substitution",
                    error_code="400",
                )

    async def substitution_add(self, payload, dal, context):
        """
        Create a faculty substitution record per BRS specification:
        payload: { inst_id, timetableEntryId, substituteFacultyId, remarks }
        Validates: only one active substitution per timetableEntryId at a time.
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        tt_entry_id = payload.get("timetableEntryId") or payload.get("ttEntryId")
        substitute_fac_id = (
            payload.get("substituteFacultyId")
            or payload.get("substituteFacId")
            or payload.get("newFacId")
        )
        remarks = payload.get("remarks") or payload.get("reason", "")
        class_session_id = payload.get("classSessionId")

        # Validate mandatory fields per BRS
        if not inst_id or not tt_entry_id:
            return XSCUtility.error_response(
                message="inst_id and timetableEntryId are required per BRS",
                error_code="400",
            )
        if not substitute_fac_id:
            return XSCUtility.error_response(
                message="substituteFacultyId is required", error_code="400"
            )
        if not remarks or str(remarks).strip() == "":
            return XSCUtility.error_response(
                message="remarks are required for substitution per BRS",
                error_code="400",
            )

        # Get timetable entry details to find original faculty
        entry_result = await dal.get_tt_entries({"tt_entry_id": tt_entry_id})
        entry_data = entry_result.get("data", [])

        original_fac_id = None
        if entry_data and isinstance(entry_data, list) and len(entry_data) > 0:
            entry = entry_data[0]
            original_fac_id = entry.get("fac_id") or entry.get("fac_crs_assignment_id")

        if original_fac_id and str(original_fac_id) == str(substitute_fac_id):
            return XSCUtility.error_response(
                message="substituteFacultyId must be different from the original faculty",
                error_code="400",
            )

        # Check for existing active substitution on this timetable entry
        existing = await dal.check_active_substitution(
            tt_entry_id=tt_entry_id, class_session_id=class_session_id
        )
        existing_data = existing.get("data", [])
        if existing_data and isinstance(existing_data, list) and len(existing_data) > 0:
            return XSCUtility.error_response(
                message="An active substitution already exists for this timetable entry. Update or cancel the existing one first.",
                error_code="400",
                existingSubstitution=existing_data[0],
            )

        actor_id = self._get_actor_id(context)
        data = {
            "tt_entry_id": tt_entry_id,
            "class_session_id": class_session_id,
            "old_fac_id": original_fac_id,
            "new_fac_id": substitute_fac_id,
            "reason": remarks,
            "created_by": actor_id,
        }
        result = await dal.create_substitution(data)

        if result.get("status") == "error":
            return XSCUtility.error_response(
                message=result.get("message", "Failed to create substitution"),
                error_code="500",
            )

        return XSCUtility.success_response(
            message="Faculty substitution created successfully", data=result.get("data")
        )

    async def substitution_view(self, payload, dal, context):
        """
        Role-scoped retrieval of substitution records per BRS specification:
        payload: { inst_id, facultyId, statusFilter, dateRange, page, limit }
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        if not inst_id:
            return XSCUtility.error_response(
                message="inst_id is required", error_code="400"
            )

        page = int(payload.get("page", 1))
        limit = int(payload.get("limit", 20))

        filters = {}
        if payload.get("substitutionId"):
            filters["substitution_id"] = payload["substitutionId"]
        if payload.get("timetableEntryId") or payload.get("ttEntryId"):
            filters["tt_entry_id"] = payload.get("timetableEntryId") or payload.get(
                "ttEntryId"
            )
        if payload.get("facultyId") or payload.get("facId"):
            filters["fac_id"] = payload.get("facultyId") or payload.get("facId")
        if payload.get("statusFilter") or payload.get("status"):
            filters["status"] = payload.get("statusFilter") or payload.get("status")

        result = await dal.get_substitutions(filters, page=page, limit=limit)
        return XSCUtility.success_response(
            message="Substitution records retrieved successfully",
            data=result.get("data", []),
            page=page,
            limit=limit,
        )

    async def substitution_update(self, payload, dal, context):
        """
        Update a substitution record per BRS specification:
        payload: { inst_id, substitutionId, substituteFacultyId, remarks }
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        substitution_id = payload.get("substitutionId")

        if not inst_id or not substitution_id:
            return XSCUtility.error_response(
                message="inst_id and substitutionId are required", error_code="400"
            )

        data = {
            "substitution_id": substitution_id,
            "new_fac_id": payload.get("substituteFacultyId")
            or payload.get("substituteFacId")
            or payload.get("newFacId"),
            "reason": payload.get("remarks") or payload.get("reason"),
        }
        result = await dal.update_substitution(data)

        if result.get("status") == "error":
            return XSCUtility.error_response(
                message=result.get("message", "Failed to update substitution"),
                error_code="500",
            )

        return XSCUtility.success_response(
            message="Substitution updated successfully", data=result.get("data")
        )

    async def substitution_delete(self, payload, dal, context):
        """
        Cancel a substitution, reverting the class to original faculty per BRS:
        payload: { inst_id, substitutionId }
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        substitution_id = payload.get("substitutionId")

        if not inst_id or not substitution_id:
            return XSCUtility.error_response(
                message="inst_id and substitutionId are required", error_code="400"
            )

        result = await dal.cancel_substitution(substitution_id)

        if result.get("status") == "error":
            return XSCUtility.error_response(
                message=result.get("message", "Failed to cancel substitution"),
                error_code="500",
            )

        result_data = result.get("data", {})
        if isinstance(result_data, list) and len(result_data) > 0:
            result_data = result_data[0]

        return XSCUtility.success_response(
            message="Substitution cancelled successfully. Class reverted to original faculty.",
            data=result_data,
        )

    # --- Utility ---

    def _get_actor_id(self, context):
        """Extract the acting user ID from context."""
        if context and hasattr(context, "security") and context.security:
            return getattr(context.security, "user_id", None)
        return None
