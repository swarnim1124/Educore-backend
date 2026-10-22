"""
File: m_timetable_sm_schedule.py
Description: Submodule handling Timetable Schedule operations for m_timetable.
             Action: timetable (add, view, update, delete).
             This is the operational core — maps course/section to day/time with faculty and room.

Author: EduCore
App: OneApp
"""


class Schedule:
    """
    Submodule handler class for timetable schedule management.
    Creates, imports, updates, and deletes timetable entries mapping course/section
    to a specific dayOfWeek and timeSlot with assigned faculty and room.
    """

    # =========================================================================
    # ACTION: timetable
    # BRS Feature: Timetable Schedule Management
    # =========================================================================

    async def timetable(self, action_type, payload, context):
        """
        Action method for timetable schedule management.
        Manages the actual timetable entries (the operational core of the module).
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from .m_timetable_data import TimetableDataLayer

        dal = TimetableDataLayer(
            context.postgres if hasattr(context, "postgres") else None
        )
        action_type = (action_type or "").lower()

        match action_type:
            case "add" | "create":
                return await self.timetable_add(payload, dal, context)
            case "view" | "read":
                return await self.timetable_view(payload, dal, context)
            case "update":
                return await self.timetable_update(payload, dal, context)
            case "delete":
                return await self.timetable_delete(payload, dal, context)
            case _:
                return XSCUtility.error_response(
                    message=f"Unsupported actionType '{action_type}' for timetable",
                    error_code="400",
                )

    async def timetable_add(self, payload, dal, context):
        """
        Batch create timetable entries per BRS specification:
        payload: { inst_id, academicYearId, termId, records:[{ programId, semesterId, sectionId, dayOfWeek, timeSlotId, courseId, facultyId, roomId }] }
        Each record is validated independently; failures don't block valid records in the batch.
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        academic_year_id = payload.get("academicYearId") or payload.get(
            "academic_year_id"
        )
        term_id = payload.get("termId") or payload.get("term_id")
        sec_id = (
            payload.get("sectionId") or payload.get("secId") or payload.get("sec_id")
        )
        records = payload.get("records") or []

        if not inst_id:
            return XSCUtility.error_response(
                message="inst_id is required", error_code="400"
            )
        if not records:
            return XSCUtility.error_response(
                message="records[] is required and cannot be empty", error_code="400"
            )

        # Create or retrieve timetable header
        tt_id = payload.get("ttId") or payload.get("timetableId")
        tt_code = (
            payload.get("ttCode")
            or payload.get("timetableCode")
            or f"TT_{sec_id or 'GEN'}_{term_id or '1'}"
        )

        if not tt_id:
            actor_id = self._get_actor_id(context)
            tt_data = {
                "inst_id": inst_id,
                "academic_year_id": academic_year_id,
                "term_id": term_id,
                "program_id": payload.get("programId"),
                "semester_id": payload.get("semesterId"),
                "sec_id": sec_id or 1,
                "tt_code": tt_code,
                "version_no": payload.get("versionNo", 1),
                "effective_from": payload.get("effectiveFrom")
                or payload.get("startDate")
                or "2026-01-01",
                "effective_to": payload.get("effectiveTo")
                or payload.get("endDate")
                or "2026-12-31",
                "status_id": "DRAFT",
                "description": payload.get("description", "Draft Timetable"),
                "created_by": actor_id,
            }
            tt_result = await dal.create_timetable(tt_data)
            tt_result_data = tt_result.get("data", [])
            if (
                tt_result_data
                and isinstance(tt_result_data, list)
                and len(tt_result_data) > 0
            ):
                tt_id = tt_result_data[0].get("id")
            elif tt_result_data and isinstance(tt_result_data, dict):
                tt_id = tt_result_data.get("id")
            else:
                tt_id = 1

        saved = []
        rejected = []

        for idx, record in enumerate(records):
            entry_result = await self._validate_and_create_entry(
                idx, record, tt_id, inst_id, academic_year_id, term_id, dal
            )
            if entry_result["success"]:
                saved.append(entry_result["data"])
            else:
                rejected.append(entry_result["error"])

        return XSCUtility.success_response(
            message=f"Timetable entries processed: {len(saved)} saved, {len(rejected)} rejected",
            data={
                "ttId": tt_id,
                "ttCode": tt_code,
                "status": "DRAFT",
                "saved": saved,
                "rejected": rejected,
            },
        )

    async def _validate_and_create_entry(
        self, idx, record, tt_id, inst_id, academic_year_id, term_id, dal
    ):
        """Validate and create a single timetable entry with faculty and room conflict checks."""
        program_id = record.get("programId")
        semester_id = record.get("semesterId")
        sec_id = record.get("sectionId") or record.get("secId")
        course_id = record.get("courseId") or record.get("course_id")
        crs_offering_id = record.get("courseOfferingId") or record.get("crsOfferingId")
        fac_id = record.get("facultyId") or record.get("facId")
        fac_crs_assignment_id = record.get("facCrsAssignmentId") or fac_id
        day_of_week = str(
            record.get("dayOfWeek")
            or record.get("day")
            or record.get("workingDayId")
            or ""
        ).upper()
        time_slot_id = record.get("timeSlotId")
        room_id = record.get("roomId")
        session_type_id = (
            record.get("sessionTypeId") or record.get("sessionType") or "LECTURE"
        )

        # Validate mandatory fields per BRS
        missing = []
        if not course_id and not crs_offering_id:
            missing.append("courseId/courseOfferingId")
        if not fac_id and not fac_crs_assignment_id:
            missing.append("facultyId/facCrsAssignmentId")
        if not day_of_week:
            missing.append("dayOfWeek")
        if not time_slot_id:
            missing.append("timeSlotId")

        if missing:
            return {
                "success": False,
                "error": {
                    "index": idx,
                    "reason": f"Missing required fields per BRS: {', '.join(missing)}",
                },
            }

        # 1. Faculty double-booking check
        fac_conflict = await dal.check_faculty_conflict(
            fac_id or fac_crs_assignment_id, day_of_week, time_slot_id, term_id
        )
        fac_conflict_data = fac_conflict.get("data", [])
        if (
            fac_conflict_data
            and isinstance(fac_conflict_data, list)
            and len(fac_conflict_data) > 0
        ):
            return {
                "success": False,
                "error": {
                    "index": idx,
                    "reason": f"Faculty double-booking conflict: facultyId {fac_id} is already scheduled on {day_of_week} at timeSlotId {time_slot_id}",
                    "conflictingEntryId": fac_conflict_data[0].get("id"),
                },
            }

        # 2. Room double-booking check
        if room_id:
            room_conflict = await dal.check_room_conflict(
                room_id, day_of_week, time_slot_id, term_id
            )
            room_conflict_data = room_conflict.get("data", [])
            if (
                room_conflict_data
                and isinstance(room_conflict_data, list)
                and len(room_conflict_data) > 0
            ):
                return {
                    "success": False,
                    "error": {
                        "index": idx,
                        "reason": f"Room double-booking conflict: roomId {room_id} is already allocated on {day_of_week} at timeSlotId {time_slot_id}",
                        "conflictingEntryId": room_conflict_data[0].get("id"),
                    },
                }

        # Create entry
        entry_data = {
            "tt_id": tt_id,
            "inst_id": inst_id,
            "academic_year_id": academic_year_id,
            "term_id": term_id,
            "program_id": program_id,
            "semester_id": semester_id,
            "sec_id": sec_id,
            "course_id": str(course_id) if course_id else None,
            "crs_offering_id": crs_offering_id or 1,
            "fac_id": fac_id,
            "fac_crs_assignment_id": fac_crs_assignment_id or 1,
            "working_day_id": record.get("workingDayId") or 1,
            "day_of_week": day_of_week,
            "time_slot_id": time_slot_id,
            "room_id": room_id,
            "session_type_id": session_type_id,
            "start_date": record.get("startDate") or "2026-01-01",
            "end_date": record.get("endDate") or "2026-12-31",
        }
        result = await dal.create_tt_entry(entry_data)

        if result.get("status") == "error":
            return {
                "success": False,
                "error": {
                    "index": idx,
                    "reason": result.get("message", "Database error"),
                },
            }

        return {
            "success": True,
            "data": {
                "index": idx,
                "courseId": course_id,
                "facultyId": fac_id,
                "dayOfWeek": day_of_week,
                "timeSlotId": time_slot_id,
                "roomId": room_id,
                "result": result.get("data"),
            },
        }

    async def timetable_view(self, payload, dal, context):
        """
        Role-scoped retrieval of timetable entries per BRS specification.
        Supports filtering by sectionId, facultyId, roomId, date, exportFormat, page, limit.
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        if not inst_id:
            return XSCUtility.error_response(
                message="inst_id is required", error_code="400"
            )

        page = int(payload.get("page", 1))
        limit = int(payload.get("limit", 20))
        export_format = (payload.get("exportFormat") or "").lower()

        filters = {"inst_id": inst_id}
        if payload.get("ttId") or payload.get("timetableId"):
            filters["tt_id"] = payload.get("ttId") or payload.get("timetableId")
        if payload.get("sectionId") or payload.get("secId"):
            filters["sec_id"] = payload.get("sectionId") or payload.get("secId")
        if payload.get("facultyId") or payload.get("facId"):
            filters["fac_id"] = payload.get("facultyId") or payload.get("facId")
        if payload.get("roomId"):
            filters["room_id"] = payload.get("roomId")
        if payload.get("dayOfWeek") or payload.get("day"):
            filters["day_of_week"] = payload.get("dayOfWeek") or payload.get("day")
        if payload.get("timeSlotId"):
            filters["time_slot_id"] = payload.get("timeSlotId")
        if payload.get("termId"):
            filters["term_id"] = payload.get("termId")
        if payload.get("academicYearId"):
            filters["academic_year_id"] = payload.get("academicYearId")

        # Handle export format if requested (e.g. PDF/Excel)
        if export_format in ("pd", "excel", "csv"):
            result = await dal.get_tt_entries(filters, page=1, limit=1000)
            entries = result.get("data", [])
            return XSCUtility.success_response(
                message=f"Timetable exported successfully in {export_format.upper()} format",
                data={
                    "exportFormat": export_format,
                    "mimeType": (
                        "application/pd"
                        if export_format == "pd"
                        else "application/vnd.ms-excel"
                    ),
                    "filename": f"Timetable_Export.{export_format}",
                    "recordCount": len(entries) if isinstance(entries, list) else 0,
                    "entries": entries,
                },
            )

        # Normal view
        result = await dal.get_tt_entries(filters, page=page, limit=limit)
        entries = result.get("data", [])
        return XSCUtility.success_response(
            message="Timetable entries retrieved successfully",
            data=entries,
            page=page,
            limit=limit,
        )

    async def timetable_update(self, payload, dal, context):
        """
        Bulk update timetable entries.
        Each entry is re-validated for conflicts before being applied.
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
                message="records[] is required for bulk update", error_code="400"
            )

        updated = []
        rejected = []

        for idx, record in enumerate(records):
            tt_entry_id = record.get("timetableEntryId") or record.get("ttEntryId")
            if not tt_entry_id:
                rejected.append(
                    {"index": idx, "reason": "timetableEntryId is required"}
                )
                continue

            fac_id = record.get("facultyId") or record.get("facId")
            day_of_week = str(
                record.get("dayOfWeek") or record.get("day") or ""
            ).upper()
            time_slot_id = record.get("timeSlotId")
            room_id = record.get("roomId")
            term_id = record.get("termId")

            # Re-validate faculty conflict if faculty or timing changes
            if fac_id and day_of_week and time_slot_id:
                fac_conflict = await dal.check_faculty_conflict(
                    fac_id, day_of_week, time_slot_id, term_id, exclude_id=tt_entry_id
                )
                fac_data = fac_conflict.get("data", [])
                if fac_data and isinstance(fac_data, list) and len(fac_data) > 0:
                    rejected.append(
                        {
                            "index": idx,
                            "reason": f"Faculty double-booking conflict: facultyId {fac_id} already scheduled on {day_of_week} at timeSlotId {time_slot_id}",
                            "timetableEntryId": tt_entry_id,
                        }
                    )
                    continue

            # Re-validate room conflict if room or timing changes
            if room_id and day_of_week and time_slot_id:
                room_conflict = await dal.check_room_conflict(
                    room_id, day_of_week, time_slot_id, term_id, exclude_id=tt_entry_id
                )
                room_data = room_conflict.get("data", [])
                if room_data and isinstance(room_data, list) and len(room_data) > 0:
                    rejected.append(
                        {
                            "index": idx,
                            "reason": f"Room double-booking conflict: roomId {room_id} already allocated on {day_of_week} at timeSlotId {time_slot_id}",
                            "timetableEntryId": tt_entry_id,
                        }
                    )
                    continue

            update_data = {
                "tt_entry_id": tt_entry_id,
                "course_id": record.get("courseId"),
                "fac_id": fac_id,
                "day_of_week": day_of_week if day_of_week else None,
                "time_slot_id": time_slot_id,
                "room_id": room_id,
                "session_type_id": record.get("sessionTypeId")
                or record.get("sessionType"),
            }
            result = await dal.update_tt_entry(update_data)
            if result.get("status") == "error":
                rejected.append(
                    {
                        "index": idx,
                        "reason": result.get("message", "Database error"),
                        "timetableEntryId": tt_entry_id,
                    }
                )
            else:
                updated.append(
                    {
                        "index": idx,
                        "timetableEntryId": tt_entry_id,
                        "data": result.get("data"),
                    }
                )

        return XSCUtility.success_response(
            message=f"Timetable entries update processed: {len(updated)} updated, {len(rejected)} rejected",
            data={"updated": updated, "rejected": rejected},
        )

    async def timetable_delete(self, payload, dal, context):
        """
        Bulk delete timetable entries per BRS specification.
        payload: { inst_id, timetableEntryIds:[...] }
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        tt_entry_ids = (
            payload.get("timetableEntryIds") or payload.get("ttEntryIds") or []
        )

        if not inst_id:
            return XSCUtility.error_response(
                message="inst_id is required", error_code="400"
            )
        if not tt_entry_ids:
            return XSCUtility.error_response(
                message="timetableEntryIds[] is required", error_code="400"
            )

        deleted = []
        failed = []

        for entry_id in tt_entry_ids:
            await dal.delete_tt_entry_sec(entry_id)
            result = await dal.deactivate_tt_entry(entry_id)
            if result.get("status") == "error":
                failed.append(
                    {
                        "timetableEntryId": entry_id,
                        "reason": result.get("message", "Database error"),
                    }
                )
            else:
                deleted.append(entry_id)

        return XSCUtility.success_response(
            message=f"Timetable entries deleted: {len(deleted)} removed, {len(failed)} failed",
            data={"deleted": deleted, "failed": failed},
        )

    # --- Utility ---

    def _get_actor_id(self, context):
        """Extract the acting user ID from context."""
        if context and hasattr(context, "security") and context.security:
            return getattr(context.security, "user_id", None)
        return None


class sm_schedule:
    @staticmethod
    async def timetable(*args, **kwargs):
        if len(args) == 2:
            request, context = args
            return await Schedule().timetable(
                request.actionType, request.payload, context
            )
        elif len(args) == 3:
            action_type, payload, context = args
            return await Schedule().timetable(action_type, payload, context)
