"""
File: m_timetable_sm_allocation.py
Description: Submodule handling Allocation operations for m_timetable.
             Actions: faculty_allocation, room_allocation.

Author: EduCore
App: OneApp
"""


class Allocation:
    """
    Submodule handler class for timetable allocation management.
    Manages faculty-to-course assignments and room-to-entry allocations.
    """

    # =========================================================================
    # ACTION: faculty_allocation
    # BRS Feature: Faculty Allocation Management
    # References sch_course_ops.tb_fac_crs_assignment
    # =========================================================================

    async def faculty_allocation(self, action_type, payload, context):
        """
        Action method for faculty allocation.
        Assigns faculty members to course/section combinations.
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from .m_timetable_data import TimetableDataLayer

        dal = TimetableDataLayer(
            context.postgres if hasattr(context, "postgres") else None
        )
        action_type = (action_type or "").lower()

        match action_type:
            case "add":
                return await self.faculty_allocation_add(payload, dal, context)
            case "view":
                return await self.faculty_allocation_view(payload, dal, context)
            case "update":
                return await self.faculty_allocation_update(payload, dal, context)
            case "delete":
                return await self.faculty_allocation_delete(payload, dal, context)
            case _:
                return XSCUtility.error_response(
                    message=f"Unsupported actionType '{action_type}' for faculty_allocation",
                    error_code="400",
                )

    async def faculty_allocation_add(self, payload, dal, context):
        """
        Batch assign faculty to course/section combinations per BRS:
        payload: { inst_id, records:[{ courseId, facultyId, sectionId }] }
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        records = payload.get("records") or []

        if not inst_id:
            return XSCUtility.error_response(
                message="inst_id is required", error_code="400"
            )
        if not records:
            return XSCUtility.error_response(
                message="records[] is required and cannot be empty", error_code="400"
            )

        saved = []
        rejected = []

        for idx, record in enumerate(records):
            course_id = record.get("courseId") or record.get("crsOfferingId")
            fac_id = record.get("facultyId") or record.get("facId")
            sec_id = record.get("sectionId") or record.get("secId")
            assignment_role_id = record.get("assignmentRoleId") or "PRIMARY"
            workload_percent = record.get("workloadPercent", 100)
            is_primary = record.get("isPrimary", True)
            remarks = record.get("remarks", "")

            # Validate mandatory fields per BRS
            if not course_id or not fac_id or not sec_id:
                rejected.append(
                    {
                        "index": idx,
                        "reason": "courseId, facultyId, and sectionId are required per BRS",
                    }
                )
                continue

            data = {
                "crs_offering_id": int(course_id) if str(course_id).isdigit() else 1,
                "fac_id": fac_id,
                "assignment_role_id": assignment_role_id,
                "workload_percent": workload_percent,
                "is_primary": is_primary,
                "remarks": remarks,
            }
            result = await dal.create_faculty_allocation(data)

            if result.get("status") == "error":
                rejected.append(
                    {
                        "index": idx,
                        "reason": result.get("message", "Database error"),
                        "facultyId": fac_id,
                        "courseId": course_id,
                        "sectionId": sec_id,
                    }
                )
            else:
                saved.append(
                    {
                        "index": idx,
                        "facultyId": fac_id,
                        "courseId": course_id,
                        "sectionId": sec_id,
                        "data": result.get("data"),
                    }
                )

        return XSCUtility.success_response(
            message=f"Faculty allocation processed: {len(saved)} saved, {len(rejected)} rejected",
            data={"saved": saved, "rejected": rejected},
        )

    async def faculty_allocation_view(self, payload, dal, context):
        """List faculty allocations with pagination and workload tracking support."""
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        if not inst_id:
            return XSCUtility.error_response(
                message="inst_id is required", error_code="400"
            )

        page = int(payload.get("page", 1))
        limit = int(payload.get("limit", 20))

        filters = {}
        if payload.get("allocationId"):
            filters["allocation_id"] = payload["allocationId"]
        if payload.get("facultyId") or payload.get("facId"):
            filters["fac_id"] = payload.get("facultyId") or payload.get("facId")
        if payload.get("courseId") or payload.get("crsOfferingId"):
            filters["crs_offering_id"] = payload.get("courseId") or payload.get(
                "crsOfferingId"
            )

        result = await dal.get_faculty_allocations(filters, page=page, limit=limit)
        return XSCUtility.success_response(
            message="Faculty allocations retrieved successfully",
            data=result.get("data", []),
            page=page,
            limit=limit,
        )

    async def faculty_allocation_update(self, payload, dal, context):
        """
        Update a faculty allocation record.
        Does NOT auto-update existing timetable entries — coordinator must update them separately per BRS rule.
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        allocation_id = payload.get("allocationId")

        if not inst_id or not allocation_id:
            return XSCUtility.error_response(
                message="inst_id and allocationId are required", error_code="400"
            )

        data = {
            "allocation_id": allocation_id,
            "fac_id": payload.get("facultyId") or payload.get("facId"),
            "crs_offering_id": payload.get("courseId") or payload.get("crsOfferingId"),
            "remarks": payload.get("remarks"),
        }
        result = await dal.update_faculty_allocation(data)

        return XSCUtility.success_response(
            message="Faculty allocation updated. Note: existing timetable entries remain unchanged until separately updated in sm_schedule.",
            data=result.get("data"),
        )

    async def faculty_allocation_delete(self, payload, dal, context):
        """
        Deactivate a faculty allocation.
        Blocked if active timetable entries reference the allocation.
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        allocation_id = payload.get("allocationId")

        if not inst_id or not allocation_id:
            return XSCUtility.error_response(
                message="inst_id and allocationId are required", error_code="400"
            )

        # Check for dependent timetable entries
        dep_result = await dal.check_faculty_allocation_dependencies(allocation_id)
        dep_data = dep_result.get("data", [])
        if dep_data and isinstance(dep_data, list) and len(dep_data) > 0:
            return XSCUtility.error_response(
                message=f"Cannot delete faculty allocation: {len(dep_data)} active timetable entries reference it. Reassign or remove them first.",
                error_code="400",
                dependentEntries=dep_data,
            )

        result = await dal.deactivate_faculty_allocation(allocation_id)
        return XSCUtility.success_response(
            message="Faculty allocation deactivated successfully",
            data=result.get("data"),
        )

    # =========================================================================
    # ACTION: room_allocation
    # BRS Feature: Room Allocation Management
    # Manages room assignments on TB_TT_ENTRY and conflict detection.
    # =========================================================================

    async def room_allocation(self, action_type, payload, context):
        """
        Action method for room allocation.
        Allocates rooms to timetable entries and exposes conflict-only views.
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from .m_timetable_data import TimetableDataLayer

        dal = TimetableDataLayer(
            context.postgres if hasattr(context, "postgres") else None
        )
        action_type = (action_type or "").lower()

        match action_type:
            case "add":
                return await self.room_allocation_add(payload, dal, context)
            case "view":
                return await self.room_allocation_view(payload, dal, context)
            case "update":
                return await self.room_allocation_update(payload, dal, context)
            case "delete":
                return await self.room_allocation_delete(payload, dal, context)
            case _:
                return XSCUtility.error_response(
                    message=f"Unsupported actionType '{action_type}' for room_allocation",
                    error_code="400",
                )

    async def room_allocation_add(self, payload, dal, context):
        """
        Batch assign rooms to timetable entries per BRS:
        payload: { inst_id, records:[{ roomId, timetableEntryId }] }
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        records = payload.get("records") or []

        if not inst_id:
            return XSCUtility.error_response(
                message="inst_id is required", error_code="400"
            )
        if not records:
            return XSCUtility.error_response(
                message="records[] is required and cannot be empty", error_code="400"
            )

        saved = []
        rejected = []

        for idx, record in enumerate(records):
            room_id = record.get("roomId")
            tt_entry_id = record.get("timetableEntryId") or record.get("ttEntryId")

            if not room_id or not tt_entry_id:
                rejected.append(
                    {"index": idx, "reason": "roomId and timetableEntryId are required"}
                )
                continue

            entry_result = await dal.get_tt_entries({"tt_entry_id": tt_entry_id})
            entry_data = entry_result.get("data", [])
            if not entry_data or (
                isinstance(entry_data, list) and len(entry_data) == 0
            ):
                rejected.append(
                    {"index": idx, "reason": f"Timetable entry {tt_entry_id} not found"}
                )
                continue

            entry = entry_data[0] if isinstance(entry_data, list) else entry_data
            day_of_week = entry.get("day_of_week") or str(entry.get("working_day_id"))
            time_slot_id = entry.get("time_slot_id")
            term_id = entry.get("term_id")

            # Check room conflict for this slot/day/term
            if room_id and day_of_week and time_slot_id:
                room_conflict = await dal.check_room_conflict(
                    room_id, day_of_week, time_slot_id, term_id, exclude_id=tt_entry_id
                )
                conflict_data = room_conflict.get("data", [])
                if (
                    conflict_data
                    and isinstance(conflict_data, list)
                    and len(conflict_data) > 0
                ):
                    rejected.append(
                        {
                            "index": idx,
                            "reason": f"Room double-booking conflict: roomId {room_id} is already allocated on {day_of_week} at timeSlotId {time_slot_id}",
                            "conflictingEntryId": conflict_data[0].get("id"),
                            "roomId": room_id,
                        }
                    )
                    continue

            result = await dal.assign_room_to_entry(tt_entry_id, room_id)
            if result.get("status") == "error":
                rejected.append(
                    {"index": idx, "reason": result.get("message", "Database error")}
                )
            else:
                saved.append(
                    {
                        "index": idx,
                        "timetableEntryId": tt_entry_id,
                        "roomId": room_id,
                        "data": result.get("data"),
                    }
                )

        return XSCUtility.success_response(
            message=f"Room allocation processed: {len(saved)} saved, {len(rejected)} rejected",
            data={"saved": saved, "rejected": rejected},
        )

    async def room_allocation_view(self, payload, dal, context):
        """List room allocations with conflictOnly filter and pagination."""
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        if not inst_id:
            return XSCUtility.error_response(
                message="inst_id is required", error_code="400"
            )

        page = int(payload.get("page", 1))
        limit = int(payload.get("limit", 20))

        filters = {}
        if payload.get("roomId"):
            filters["room_id"] = payload["roomId"]
        if payload.get("timetableEntryId") or payload.get("ttEntryId"):
            filters["tt_entry_id"] = payload.get("timetableEntryId") or payload.get(
                "ttEntryId"
            )
        if payload.get("conflictOnly"):
            filters["conflict_only"] = True

        result = await dal.get_room_allocations(filters, page=page, limit=limit)
        data = result.get("data", [])

        if payload.get("conflictOnly"):
            return XSCUtility.success_response(
                message="Room allocation conflicts retrieved successfully",
                data=data,
                page=page,
                limit=limit,
            )

        return XSCUtility.success_response(
            message="Room allocations retrieved successfully",
            data=data,
            page=page,
            limit=limit,
        )

    async def room_allocation_update(self, payload, dal, context):
        """Reassign a room on a timetable entry with re-validation."""
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        tt_entry_id = (
            payload.get("allocationId")
            or payload.get("timetableEntryId")
            or payload.get("ttEntryId")
        )
        new_room_id = payload.get("roomId")

        if not inst_id or not tt_entry_id:
            return XSCUtility.error_response(
                message="inst_id and allocationId/timetableEntryId are required",
                error_code="400",
            )
        if not new_room_id:
            return XSCUtility.error_response(
                message="roomId is required for update", error_code="400"
            )

        entry_result = await dal.get_tt_entries({"tt_entry_id": tt_entry_id})
        entry_data = entry_result.get("data", [])
        if entry_data and isinstance(entry_data, list) and len(entry_data) > 0:
            entry = entry_data[0]
            day_of_week = entry.get("day_of_week") or str(entry.get("working_day_id"))
            time_slot_id = entry.get("time_slot_id")
            term_id = entry.get("term_id")

            if day_of_week and time_slot_id:
                room_conflict = await dal.check_room_conflict(
                    new_room_id,
                    day_of_week,
                    time_slot_id,
                    term_id,
                    exclude_id=tt_entry_id,
                )
                conflict_data = room_conflict.get("data", [])
                if (
                    conflict_data
                    and isinstance(conflict_data, list)
                    and len(conflict_data) > 0
                ):
                    return XSCUtility.error_response(
                        message="Room double-booking conflict: new roomId is already allocated on this day/slot",
                        error_code="400",
                    )

        result = await dal.assign_room_to_entry(tt_entry_id, new_room_id)
        return XSCUtility.success_response(
            message="Room allocation updated successfully", data=result.get("data")
        )

    async def room_allocation_delete(self, payload, dal, context):
        """
        Remove room assignment from a timetable entry.
        The entry persists but becomes room-unassigned per BRS rule.
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        tt_entry_id = (
            payload.get("allocationId")
            or payload.get("timetableEntryId")
            or payload.get("ttEntryId")
        )

        if not inst_id or not tt_entry_id:
            return XSCUtility.error_response(
                message="inst_id and allocationId/timetableEntryId are required",
                error_code="400",
            )

        result = await dal.remove_room_from_entry(tt_entry_id)
        return XSCUtility.success_response(
            message="Room allocation removed. Timetable entry persists but is now room-unassigned.",
            data=result.get("data"),
        )
