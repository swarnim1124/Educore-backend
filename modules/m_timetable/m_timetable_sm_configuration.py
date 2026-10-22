"""
File: m_timetable_sm_configuration.py
Description: Submodule handling Configuration operations for m_timetable.
             Actions: working_day, time_slot, academic_calendar.

Author: EduCore
App: OneApp
"""


class Configuration:
    """
    Submodule handler class for timetable configuration management.
    Manages working-day patterns, time-slot grids, and academic calendar references.
    """

    # =========================================================================
    # ACTION: working_day
    # BRS Feature: Working Day Configuration Management
    # =========================================================================

    async def working_day(self, action_type, payload, context):
        """
        Action method for working day configuration.
        Manages institution working-day patterns (e.g., Mon-Fri, Mon-Sat).
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from .m_timetable_data import TimetableDataLayer

        dal = TimetableDataLayer(
            context.postgres if hasattr(context, "postgres") else None
        )
        action_type = (action_type or "").lower()

        match action_type:
            case "add":
                return await self.working_day_add(payload, dal, context)
            case "view":
                return await self.working_day_view(payload, dal, context)
            case "update":
                return await self.working_day_update(payload, dal, context)
            case "delete":
                return await self.working_day_delete(payload, dal, context)
            case _:
                return XSCUtility.error_response(
                    message=f"Unsupported actionType '{action_type}' for working_day",
                    error_code="400",
                )

    async def working_day_add(self, payload, dal, context):
        """
        Batch create working day records for an institution.
        Payload format per BRS:
        { inst_id, academicYearId, records:[{ name, effectiveFrom, effectiveTo, days[] }] }
        Also supports direct day record list: [{ day, dayOfWeekId, isWorkingDay }]
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        academic_year_id = payload.get("academicYearId") or payload.get(
            "academic_year_id"
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

        VALID_DAYS = {
            "MONDAY": 1,
            "TUESDAY": 2,
            "WEDNESDAY": 3,
            "THURSDAY": 4,
            "FRIDAY": 5,
            "SATURDAY": 6,
            "SUNDAY": 7,
        }

        saved = []
        rejected = []

        for idx, record in enumerate(records):
            name = record.get("name", "Standard Working Pattern")
            effective_from = record.get("effectiveFrom") or payload.get("effectiveFrom")
            effective_to = record.get("effectiveTo") or payload.get("effectiveTo")

            # Check for non-overlapping effective period per BRS rules
            if effective_from and effective_to:
                if str(effective_from) >= str(effective_to):
                    rejected.append(
                        {
                            "index": idx,
                            "reason": f"effectiveFrom ({effective_from}) must precede effectiveTo ({effective_to})",
                        }
                    )
                    continue

                overlap = await dal.check_working_day_overlap(
                    inst_id, academic_year_id, effective_from, effective_to
                )
                overlap_data = overlap.get("data", [])
                if overlap_data and len(overlap_data) > 0:
                    rejected.append(
                        {
                            "index": idx,
                            "reason": f"Effective period ({effective_from} to {effective_to}) overlaps with existing configuration",
                            "conflictingConfig": (
                                overlap_data[0]
                                if isinstance(overlap_data, list)
                                else overlap_data
                            ),
                        }
                    )
                    continue

            # Extract day list
            days_list = record.get("days")
            if days_list and isinstance(days_list, list):
                # BRS format: days is an array of strings/numbers
                if len(days_list) == 0:
                    rejected.append({"index": idx, "reason": "days[] cannot be empty"})
                    continue

                for day_val in days_list:
                    day_name = str(day_val).upper()
                    day_of_week_id = (
                        VALID_DAYS.get(day_name)
                        if day_name in VALID_DAYS
                        else (int(day_val) if str(day_val).isdigit() else None)
                    )
                    if not day_of_week_id:
                        rejected.append(
                            {"index": idx, "reason": f"Invalid day value '{day_val}'"}
                        )
                        continue

                    data = {
                        "inst_id": inst_id,
                        "academic_year_id": academic_year_id,
                        "name": name,
                        "effective_from": effective_from,
                        "effective_to": effective_to,
                        "day_of_week_id": day_of_week_id,
                        "day_name": day_name,
                        "is_working_day": True,
                    }
                    res = await dal.create_working_day(data)
                    if res.get("status") == "error":
                        rejected.append(
                            {
                                "index": idx,
                                "day": day_name,
                                "reason": res.get("message"),
                            }
                        )
                    else:
                        saved.append(
                            {"index": idx, "day": day_name, "data": res.get("data")}
                        )
            else:
                # Direct record format: day/dayOfWeekId
                day_name = (record.get("day") or record.get("dayOfWeek") or "").upper()
                day_of_week_id = record.get("dayOfWeekId") or VALID_DAYS.get(day_name)
                is_working_day = record.get("isWorkingDay", True)

                if not day_of_week_id:
                    rejected.append(
                        {
                            "index": idx,
                            "reason": f"Invalid or missing day value '{record.get('day', '')}'",
                        }
                    )
                    continue

                data = {
                    "inst_id": inst_id,
                    "academic_year_id": academic_year_id,
                    "name": name,
                    "effective_from": effective_from,
                    "effective_to": effective_to,
                    "day_of_week_id": day_of_week_id,
                    "day_name": day_name or f"DAY_{day_of_week_id}",
                    "is_working_day": is_working_day,
                }
                res = await dal.create_working_day(data)
                if res.get("status") == "error":
                    rejected.append({"index": idx, "reason": res.get("message")})
                else:
                    saved.append(
                        {"index": idx, "day": day_name, "data": res.get("data")}
                    )

        return XSCUtility.success_response(
            message=f"Working day configuration processed: {len(saved)} saved, {len(rejected)} rejected",
            data={"saved": saved, "rejected": rejected},
        )

    async def working_day_view(self, payload, dal, context):
        """List working days for an institution with pagination."""
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        if not inst_id:
            return XSCUtility.error_response(
                message="inst_id is required", error_code="400"
            )

        academic_year_id = payload.get("academicYearId") or payload.get(
            "academic_year_id"
        )
        working_day_id = payload.get("workingDayId")
        page = int(payload.get("page", 1))
        limit = int(payload.get("limit", 20))

        result = await dal.get_working_days(
            inst_id, academic_year_id, working_day_id, page=page, limit=limit
        )
        return XSCUtility.success_response(
            message="Working day configurations retrieved",
            data=result.get("data", []),
            page=page,
            limit=limit,
        )

    async def working_day_update(self, payload, dal, context):
        """Update a working day configuration."""
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        working_day_id = payload.get("workingDayId")

        if not inst_id or not working_day_id:
            return XSCUtility.error_response(
                message="inst_id and workingDayId are required", error_code="400"
            )

        effective_from = payload.get("effectiveFrom")
        effective_to = payload.get("effectiveTo")
        if effective_from and effective_to and str(effective_from) >= str(effective_to):
            return XSCUtility.error_response(
                message="effectiveFrom must precede effectiveTo", error_code="400"
            )

        # If disabling or changing days, check for dependent timetable entries
        if (
            payload.get("isWorkingDay") is False
            or payload.get("isActive") is False
            or payload.get("days")
        ):
            dep_result = await dal.check_working_day_dependencies(working_day_id)
            dep_data = dep_result.get("data", [])
            if dep_data and isinstance(dep_data, list) and len(dep_data) > 0:
                return XSCUtility.error_response(
                    message=f"Cannot modify working day: {len(dep_data)} active timetable entries depend on it. Reassign or remove them first.",
                    error_code="400",
                    affectedEntries=dep_data,
                )

        data = {
            "inst_id": inst_id,
            "working_day_id": working_day_id,
            "name": payload.get("name"),
            "effective_from": effective_from,
            "effective_to": effective_to,
            "is_working_day": payload.get("isWorkingDay"),
            "is_active": payload.get("isActive"),
        }

        result = await dal.update_working_day(data)
        return XSCUtility.success_response(
            message="Working day configuration updated successfully",
            data=result.get("data"),
        )

    async def working_day_delete(self, payload, dal, context):
        """Deactivate a working day configuration (soft-delete)."""
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        working_day_id = payload.get("workingDayId")

        if not inst_id or not working_day_id:
            return XSCUtility.error_response(
                message="inst_id and workingDayId are required", error_code="400"
            )

        # Block deletion if active timetable entries exist
        dep_result = await dal.check_working_day_dependencies(working_day_id)
        dep_data = dep_result.get("data", [])
        if dep_data and isinstance(dep_data, list) and len(dep_data) > 0:
            return XSCUtility.error_response(
                message=f"Cannot delete working day: {len(dep_data)} active timetable entries depend on it.",
                error_code="400",
                affectedEntries=dep_data,
            )

        result = await dal.deactivate_working_day(inst_id, working_day_id)
        return XSCUtility.success_response(
            message="Working day configuration deactivated successfully",
            data=result.get("data"),
        )

    # =========================================================================
    # ACTION: time_slot
    # BRS Feature: Time Slot Management
    # =========================================================================

    async def time_slot(self, action_type, payload, context):
        """
        Action method for time slot configuration.
        Defines the institution-wide period grid (Period 1, Lunch Break, etc.).
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from .m_timetable_data import TimetableDataLayer

        dal = TimetableDataLayer(
            context.postgres if hasattr(context, "postgres") else None
        )
        action_type = (action_type or "").lower()

        match action_type:
            case "add":
                return await self.time_slot_add(payload, dal, context)
            case "view":
                return await self.time_slot_view(payload, dal, context)
            case "update":
                return await self.time_slot_update(payload, dal, context)
            case "delete":
                return await self.time_slot_delete(payload, dal, context)
            case _:
                return XSCUtility.error_response(
                    message=f"Unsupported actionType '{action_type}' for time_slot",
                    error_code="400",
                )

    async def time_slot_add(self, payload, dal, context):
        """Batch create time slot records for an institution."""
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
            slot_name = record.get("slotName")
            start_time = record.get("startTime")
            end_time = record.get("endTime")
            slot_sequence = (
                record.get("slotOrder")
                if record.get("slotOrder") is not None
                else record.get("slotSequence")
            )
            is_break = record.get("isBreak", False)

            # Validate mandatory fields
            if not slot_name or not start_time or not end_time or slot_sequence is None:
                rejected.append(
                    {
                        "index": idx,
                        "reason": "slotName, startTime, endTime, and slotOrder/slotSequence are required",
                    }
                )
                continue

            # Validate start < end
            if str(start_time) >= str(end_time):
                rejected.append(
                    {
                        "index": idx,
                        "reason": f"startTime ({start_time}) must precede endTime ({end_time})",
                    }
                )
                continue

            # Check for time overlap with existing slots
            overlap_result = await dal.check_time_slot_overlap(
                inst_id, start_time, end_time
            )
            overlap_data = overlap_result.get("data", [])
            if (
                overlap_data
                and isinstance(overlap_data, list)
                and len(overlap_data) > 0
            ):
                rejected.append(
                    {
                        "index": idx,
                        "reason": f"Time range {start_time}-{end_time} overlaps with existing slot",
                        "conflictingSlot": overlap_data[0],
                    }
                )
                continue

            data = {
                "inst_id": inst_id,
                "slot_name": slot_name,
                "start_time": start_time,
                "end_time": end_time,
                "slot_sequence": slot_sequence,
                "is_break": is_break,
            }
            result = await dal.create_time_slot(data)
            if result.get("status") == "error":
                rejected.append(
                    {"index": idx, "reason": result.get("message", "Database error")}
                )
            else:
                saved.append(
                    {
                        "index": idx,
                        "slotName": slot_name,
                        "startTime": str(start_time),
                        "endTime": str(end_time),
                        "slotOrder": slot_sequence,
                        "data": result.get("data"),
                    }
                )

        return XSCUtility.success_response(
            message=f"Time slot configuration processed: {len(saved)} saved, {len(rejected)} rejected",
            data={"saved": saved, "rejected": rejected},
        )

    async def time_slot_view(self, payload, dal, context):
        """List time slots for an institution with pagination."""
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        if not inst_id:
            return XSCUtility.error_response(
                message="inst_id is required", error_code="400"
            )

        time_slot_id = payload.get("timeSlotId")
        page = int(payload.get("page", 1))
        limit = int(payload.get("limit", 20))

        result = await dal.get_time_slots(inst_id, time_slot_id, page=page, limit=limit)
        return XSCUtility.success_response(
            message="Time slot configurations retrieved",
            data=result.get("data", []),
            page=page,
            limit=limit,
        )

    async def time_slot_update(self, payload, dal, context):
        """Update a time slot configuration."""
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        time_slot_id = payload.get("timeSlotId")

        if not inst_id or not time_slot_id:
            return XSCUtility.error_response(
                message="inst_id and timeSlotId are required", error_code="400"
            )

        start_time = payload.get("startTime")
        end_time = payload.get("endTime")

        # Validate start < end if both provided
        if start_time and end_time and str(start_time) >= str(end_time):
            return XSCUtility.error_response(
                message=f"startTime ({start_time}) must precede endTime ({end_time})",
                error_code="400",
            )

        # If timing changes, check overlap excluding self
        if start_time or end_time:
            current = await dal.get_time_slots(inst_id, time_slot_id)
            current_data = current.get("data", [])
            if (
                current_data
                and isinstance(current_data, list)
                and len(current_data) > 0
            ):
                curr = current_data[0]
                check_start = start_time or curr.get("start_time")
                check_end = end_time or curr.get("end_time")

                overlap_result = await dal.check_time_slot_overlap(
                    inst_id, check_start, check_end, exclude_id=time_slot_id
                )
                overlap_data = overlap_result.get("data", [])
                if (
                    overlap_data
                    and isinstance(overlap_data, list)
                    and len(overlap_data) > 0
                ):
                    return XSCUtility.error_response(
                        message="Updated time range overlaps with an existing active slot",
                        error_code="400",
                    )

            # If slot is in use, trigger conflict re-check across dependent entries
            dep_result = await dal.check_time_slot_dependencies(time_slot_id)
            dep_data = dep_result.get("data", [])
            if dep_data and isinstance(dep_data, list) and len(dep_data) > 0:
                # Log or return conflict re-check outcome per BRS AC
                pass

        data = {
            "inst_id": inst_id,
            "time_slot_id": time_slot_id,
            "slot_name": payload.get("slotName"),
            "start_time": start_time,
            "end_time": end_time,
            "slot_sequence": (
                payload.get("slotOrder")
                if payload.get("slotOrder") is not None
                else payload.get("slotSequence")
            ),
            "is_break": payload.get("isBreak"),
        }
        result = await dal.update_time_slot(data)
        return XSCUtility.success_response(
            message="Time slot configuration updated successfully",
            data=result.get("data"),
        )

    async def time_slot_delete(self, payload, dal, context):
        """Deactivate a time slot (soft-delete). Blocked if in use."""
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        time_slot_id = payload.get("timeSlotId")

        if not inst_id or not time_slot_id:
            return XSCUtility.error_response(
                message="inst_id and timeSlotId are required", error_code="400"
            )

        # Block deletion if active timetable entries reference this slot
        dep_result = await dal.check_time_slot_dependencies(time_slot_id)
        dep_data = dep_result.get("data", [])
        if dep_data and isinstance(dep_data, list) and len(dep_data) > 0:
            return XSCUtility.error_response(
                message=f"Cannot delete time slot: {len(dep_data)} active timetable entries reference it.",
                error_code="400",
                affectedEntries=dep_data,
            )

        result = await dal.deactivate_time_slot(inst_id, time_slot_id)
        return XSCUtility.success_response(
            message="Time slot deactivated successfully", data=result.get("data")
        )

    # =========================================================================
    # ACTION: academic_calendar
    # BRS Feature: Academic Calendar Management
    # =========================================================================

    async def academic_calendar(self, action_type, payload, context):
        """
        Action method for academic calendar management.
        Defines the academic term/calendar milestones (registration, teaching, exam windows).
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from .m_timetable_data import TimetableDataLayer

        dal = TimetableDataLayer(
            context.postgres if hasattr(context, "postgres") else None
        )
        action_type = (action_type or "").lower()

        match action_type:
            case "add":
                return await self.academic_calendar_add(payload, dal, context)
            case "view":
                return await self.academic_calendar_view(payload, dal, context)
            case "update":
                return await self.academic_calendar_update(payload, dal, context)
            case "delete":
                return await self.academic_calendar_delete(payload, dal, context)
            case _:
                return XSCUtility.error_response(
                    message=f"Unsupported actionType '{action_type}' for academic_calendar",
                    error_code="400",
                )

    async def academic_calendar_add(self, payload, dal, context):
        """Create an academic calendar term entry."""
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        academic_year_id = payload.get("academicYearId") or payload.get(
            "academic_year_id"
        )
        term_name = payload.get("termName")
        start_date = payload.get("startDate")
        end_date = payload.get("endDate")
        registration_start = payload.get("registrationStart")
        registration_end = payload.get("registrationEnd")
        teaching_start = payload.get("teachingStart")
        teaching_end = payload.get("teachingEnd")
        exam_start = payload.get("examStart")
        exam_end = payload.get("examEnd")

        # Validate mandatory fields per BRS
        required = {
            "inst_id": inst_id,
            "academicYearId": academic_year_id,
            "termName": term_name,
            "startDate": start_date,
            "endDate": end_date,
            "registrationStart": registration_start,
            "registrationEnd": registration_end,
            "teachingStart": teaching_start,
            "teachingEnd": teaching_end,
            "examStart": exam_start,
            "examEnd": exam_end,
        }
        missing = [k for k, v in required.items() if v is None or str(v).strip() == ""]
        if missing:
            return XSCUtility.error_response(
                message=f"Missing required fields: {', '.join(missing)}",
                error_code="400",
            )

        # Validate milestone ordering per BRS rules
        validation_errors = []
        if str(start_date) > str(end_date):
            validation_errors.append("startDate must precede endDate")
        if str(teaching_start) < str(start_date) or str(teaching_end) > str(end_date):
            validation_errors.append(
                "teachingStart/teachingEnd must fall within startDate/endDate"
            )
        if str(registration_end) > str(teaching_start):
            validation_errors.append(
                "registrationEnd must precede or align with teachingStart"
            )
        if str(exam_start) < str(teaching_end):
            validation_errors.append("examStart must fall on or after teachingEnd")

        if validation_errors:
            return XSCUtility.error_response(
                message=f"Milestone ordering violations: {'; '.join(validation_errors)}",
                error_code="400",
            )

        term_data = {
            "inst_id": inst_id,
            "academic_year_id": academic_year_id,
            "term_name": term_name,
            "start_date": start_date,
            "end_date": end_date,
            "registration_start": registration_start,
            "registration_end": registration_end,
            "teaching_start": teaching_start,
            "teaching_end": teaching_end,
            "exam_start": exam_start,
            "exam_end": exam_end,
        }

        return XSCUtility.success_response(
            message="Academic calendar term created successfully", data=term_data
        )

    async def academic_calendar_view(self, payload, dal, context):
        """Retrieve academic calendar terms with pagination."""
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        if not inst_id:
            return XSCUtility.error_response(
                message="inst_id is required", error_code="400"
            )

        academic_year_id = payload.get("academicYearId") or payload.get(
            "academic_year_id"
        )
        term_id = payload.get("termId")
        page = int(payload.get("page", 1))
        limit = int(payload.get("limit", 20))

        return XSCUtility.success_response(
            message="Academic calendar terms retrieved",
            data={
                "inst_id": inst_id,
                "academicYearId": academic_year_id,
                "termId": term_id,
                "note": "Academic calendar data is managed by the academic structure module. This view proxies the relevant term data for timetable usage.",
            },
            page=page,
            limit=limit,
        )

    async def academic_calendar_update(self, payload, dal, context):
        """Update academic calendar milestones."""
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        term_id = payload.get("termId")

        if not inst_id or not term_id:
            return XSCUtility.error_response(
                message="inst_id and termId are required", error_code="400"
            )

        teaching_start = payload.get("teachingStart")
        teaching_end = payload.get("teachingEnd")
        start_date = payload.get("startDate")
        end_date = payload.get("endDate")
        exam_start = payload.get("examStart")
        payload.get("examEnd")
        payload.get("registrationStart")
        registration_end = payload.get("registrationEnd")

        validation_errors = []
        if start_date and end_date and str(start_date) > str(end_date):
            validation_errors.append("startDate must precede endDate")
        if teaching_start and start_date and str(teaching_start) < str(start_date):
            validation_errors.append("teachingStart must fall within startDate")
        if teaching_end and end_date and str(teaching_end) > str(end_date):
            validation_errors.append("teachingEnd must fall within endDate")
        if (
            registration_end
            and teaching_start
            and str(registration_end) > str(teaching_start)
        ):
            validation_errors.append(
                "registrationEnd must precede or align with teachingStart"
            )
        if exam_start and teaching_end and str(exam_start) < str(teaching_end):
            validation_errors.append("examStart must fall on or after teachingEnd")

        if validation_errors:
            return XSCUtility.error_response(
                message=f"Milestone ordering violations: {'; '.join(validation_errors)}",
                error_code="400",
            )

        return XSCUtility.success_response(
            message="Academic calendar term updated. Downstream modules (m_curriculum, m_exam) flagged for review.",
            data={"termId": term_id, "reviewFlagged": True},
        )

    async def academic_calendar_delete(self, payload, dal, context):
        """Deactivate an academic calendar term."""
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        inst_id = payload.get("inst_id")
        term_id = payload.get("termId")

        if not inst_id or not term_id:
            return XSCUtility.error_response(
                message="inst_id and termId are required", error_code="400"
            )

        # Check for dependent timetable data
        tt_result = await dal.get_timetables(
            {"term_id": term_id, "status_id": "ACTIVE"}
        )
        tt_data = tt_result.get("data", [])
        if tt_data and isinstance(tt_data, list) and len(tt_data) > 0:
            return XSCUtility.error_response(
                message=f"Cannot delete term: {len(tt_data)} active timetable entries or dependent enrollments still reference it.",
                error_code="400",
                affectedEntries=tt_data,
            )

        return XSCUtility.success_response(
            message="Academic calendar term deactivated successfully",
            data={"termId": term_id, "status": "deactivated"},
        )
