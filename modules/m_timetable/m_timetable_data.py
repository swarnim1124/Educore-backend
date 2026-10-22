from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
"""
File: m_timetable_data.py
Description: Production-Grade Data Access Layer for m_timetable (Timetable Module).
             Encapsulates all SQL execution against sch_timetable and referenced domain tables.

Author: EduCore
App: OneApp
"""

from sqlalchemy import text


class TimetableDataLayer:
    """
    Data Access Layer for the m_timetable module.
    Encapsulates all SQL execution with strict error reporting, pagination, and dry-run support.
    """

    def __init__(self, db):
        self.db = db

    async def _safe_query(self, stmt, params=None):
        """Executes SQL statements. Returns dry-run success when DB is absent, or error if live DB query fails."""
        if not self.db:
            return {
                "status": "success",
                "message": "Dry-run execution success (no active database connection)",
                "data": [],
            }
        try:
            result = await self.db.async_genericSQL(stmt, params)
            if isinstance(result, dict) and "status" in result:
                return result
            return {"status": "success", "data": result}
        except Exception as e:
            return {
                "status": "error",
                "code": "DATABASE_ERROR",
                "message": f"Database error: {str(e)}",
                "data": [],
            }

    # =========================================================================
    # 1. WORKING DAY (sm_configuration -> workingDay)
    # =========================================================================

    async def create_working_day(self, data):
        """Insert a working day record."""
        stmt = text("""
            INSERT INTO sch_timetable.tb_working_day
                (inst_id, academic_year_id, name, effective_from, effective_to, day_of_week_id, day_name, is_working_day, is_active)
            VALUES (:inst_id, :academic_year_id, :name, :effective_from, :effective_to, :day_of_week_id, :day_name, :is_working_day, true)
            RETURNING id, inst_id, academic_year_id, name, effective_from, effective_to, day_of_week_id, day_name, is_working_day, is_active
        """)
        return await self._safe_query(stmt, data)

    async def check_working_day_overlap(
        self, inst_id, academic_year_id, effective_from, effective_to, exclude_id=None
    ):
        """Check if proposed effective period overlaps an existing working day configuration for the same academicYearId."""
        if not effective_from or not effective_to:
            return {"status": "success", "data": []}
        if exclude_id:
            stmt = text("""
                SELECT id, name, effective_from, effective_to FROM sch_timetable.tb_working_day
                WHERE inst_id = :inst_id AND (academic_year_id = :academic_year_id OR :academic_year_id IS NULL)
                  AND is_active = true AND id != :exclude_id
                  AND effective_from < :effective_to AND effective_to > :effective_from
            """)
            return await self._safe_query(
                stmt,
                {
                    "inst_id": inst_id,
                    "academic_year_id": academic_year_id,
                    "effective_from": effective_from,
                    "effective_to": effective_to,
                    "exclude_id": exclude_id,
                },
            )
        stmt = text("""
            SELECT id, name, effective_from, effective_to FROM sch_timetable.tb_working_day
            WHERE inst_id = :inst_id AND (academic_year_id = :academic_year_id OR :academic_year_id IS NULL)
              AND is_active = true
              AND effective_from < :effective_to AND effective_to > :effective_from
        """)
        return await self._safe_query(
            stmt,
            {
                "inst_id": inst_id,
                "academic_year_id": academic_year_id,
                "effective_from": effective_from,
                "effective_to": effective_to,
            },
        )

    async def get_working_days(
        self, inst_id, academic_year_id=None, working_day_id=None, page=1, limit=20
    ):
        """Retrieve working days for an institution, optionally filtered and paginated."""
        params = {"inst_id": inst_id, "limit": limit, "offset": (page - 1) * limit}
        conditions = ["inst_id = :inst_id", "is_active = true"]

        if academic_year_id:
            conditions.append("academic_year_id = :academic_year_id")
            params["academic_year_id"] = academic_year_id
        if working_day_id:
            conditions.append("id = :working_day_id")
            params["working_day_id"] = working_day_id

        where_clause = " AND ".join(conditions)
        stmt = text("""
            SELECT * FROM sch_timetable.tb_working_day
            WHERE {where_clause}
            ORDER BY day_of_week_id, id
            LIMIT :limit OFFSET :offset
        """)
        return await self._safe_query(stmt, params)

    async def update_working_day(self, data):
        """Update a working day record."""
        stmt = text("""
            UPDATE sch_timetable.tb_working_day
            SET name = COALESCE(:name, name),
                effective_from = COALESCE(:effective_from, effective_from),
                effective_to = COALESCE(:effective_to, effective_to),
                is_working_day = COALESCE(:is_working_day, is_working_day),
                is_active = COALESCE(:is_active, is_active),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :working_day_id AND inst_id = :inst_id
            RETURNING id, inst_id, academic_year_id, name, effective_from, effective_to, day_of_week_id, day_name, is_working_day, is_active
        """)
        return await self._safe_query(stmt, data)

    async def deactivate_working_day(self, inst_id, working_day_id):
        """Soft-delete a working day record."""
        stmt = text("""
            UPDATE sch_timetable.tb_working_day
            SET is_active = false, updated_at = CURRENT_TIMESTAMP
            WHERE id = :working_day_id AND inst_id = :inst_id
            RETURNING id, is_active
        """)
        return await self._safe_query(
            stmt, {"working_day_id": working_day_id, "inst_id": inst_id}
        )

    async def check_working_day_dependencies(self, working_day_id):
        """Check if any active timetable entries reference this working day."""
        stmt = text("""
            SELECT id, tt_id, day_of_week FROM sch_timetable.tb_tt_entry
            WHERE working_day_id = :working_day_id AND is_active = true
        """)
        return await self._safe_query(stmt, {"working_day_id": working_day_id})

    # =========================================================================
    # 2. TIME SLOT (sm_configuration -> timeSlot)
    # =========================================================================

    async def create_time_slot(self, data):
        """Insert a single time slot record."""
        stmt = text("""
            INSERT INTO sch_timetable.tb_time_slot
                (inst_id, slot_name, start_time, end_time, slot_sequence, is_break, is_active)
            VALUES (:inst_id, :slot_name, :start_time, :end_time, :slot_sequence, :is_break, true)
            RETURNING id, inst_id, slot_name, start_time, end_time, slot_sequence, is_break, is_active
        """)
        return await self._safe_query(stmt, data)

    async def get_time_slots(self, inst_id, time_slot_id=None, page=1, limit=20):
        """Retrieve time slots for an institution, ordered by sequence."""
        params = {"inst_id": inst_id, "limit": limit, "offset": (page - 1) * limit}
        if time_slot_id:
            stmt = text("""
                SELECT * FROM sch_timetable.tb_time_slot
                WHERE id = :time_slot_id AND inst_id = :inst_id AND is_active = true
            """)
            return await self._safe_query(
                stmt, {"time_slot_id": time_slot_id, "inst_id": inst_id}
            )
        stmt = text("""
            SELECT * FROM sch_timetable.tb_time_slot
            WHERE inst_id = :inst_id AND is_active = true
            ORDER BY slot_sequence
            LIMIT :limit OFFSET :offset
        """)
        return await self._safe_query(stmt, params)

    async def update_time_slot(self, data):
        """Update a time slot record."""
        stmt = text("""
            UPDATE sch_timetable.tb_time_slot
            SET slot_name = COALESCE(:slot_name, slot_name),
                start_time = COALESCE(:start_time, start_time),
                end_time = COALESCE(:end_time, end_time),
                slot_sequence = COALESCE(:slot_sequence, slot_sequence),
                is_break = COALESCE(:is_break, is_break),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :time_slot_id AND inst_id = :inst_id
            RETURNING id, inst_id, slot_name, start_time, end_time, slot_sequence, is_break, is_active
        """)
        return await self._safe_query(stmt, data)

    async def deactivate_time_slot(self, inst_id, time_slot_id):
        """Soft-delete a time slot record."""
        stmt = text("""
            UPDATE sch_timetable.tb_time_slot
            SET is_active = false, updated_at = CURRENT_TIMESTAMP
            WHERE id = :time_slot_id AND inst_id = :inst_id
            RETURNING id, is_active
        """)
        return await self._safe_query(
            stmt, {"time_slot_id": time_slot_id, "inst_id": inst_id}
        )

    async def check_time_slot_dependencies(self, time_slot_id):
        """Check if any active timetable entries reference this time slot."""
        stmt = text("""
            SELECT id, tt_id FROM sch_timetable.tb_tt_entry
            WHERE time_slot_id = :time_slot_id AND is_active = true
        """)
        return await self._safe_query(stmt, {"time_slot_id": time_slot_id})

    async def check_time_slot_overlap(
        self, inst_id, start_time, end_time, exclude_id=None
    ):
        """Check if a proposed time range overlaps any existing active slot for the institution."""
        if exclude_id:
            stmt = text("""
                SELECT id, slot_name, start_time, end_time FROM sch_timetable.tb_time_slot
                WHERE inst_id = :inst_id AND is_active = true AND id != :exclude_id
                  AND start_time < :end_time AND end_time > :start_time
            """)
            return await self._safe_query(
                stmt,
                {
                    "inst_id": inst_id,
                    "start_time": start_time,
                    "end_time": end_time,
                    "exclude_id": exclude_id,
                },
            )
        stmt = text("""
            SELECT id, slot_name, start_time, end_time FROM sch_timetable.tb_time_slot
            WHERE inst_id = :inst_id AND is_active = true
              AND start_time < :end_time AND end_time > :start_time
        """)
        return await self._safe_query(
            stmt, {"inst_id": inst_id, "start_time": start_time, "end_time": end_time}
        )

    # =========================================================================
    # 3. TIMETABLE HEADER (sm_schedule -> timetable)
    # =========================================================================

    async def create_timetable(self, data):
        """Insert a timetable header record."""
        stmt = text("""
            INSERT INTO sch_timetable.tb_tt
                (inst_id, academic_year_id, term_id, program_id, semester_id, sec_id, tt_code,
                 version_no, effective_from, effective_to, status_id, description, is_active, created_by)
            VALUES (:inst_id, :academic_year_id, :term_id, :program_id, :semester_id, :sec_id, :tt_code,
                    :version_no, :effective_from, :effective_to, :status_id, :description, true, :created_by)
            RETURNING id, inst_id, academic_year_id, term_id, program_id, semester_id, sec_id, tt_code, version_no, effective_from, effective_to, status_id, description, is_active
        """)
        return await self._safe_query(stmt, data)

    async def get_timetables(self, filters, page=1, limit=20):
        """Retrieve timetable headers based on filters and pagination."""
        conditions = ["t.is_active = true"]
        params = {"limit": limit, "offset": (page - 1) * limit}

        if filters.get("inst_id"):
            conditions.append("t.inst_id = :inst_id")
            params["inst_id"] = filters["inst_id"]
        if filters.get("academic_year_id"):
            conditions.append("t.academic_year_id = :academic_year_id")
            params["academic_year_id"] = filters["academic_year_id"]
        if filters.get("term_id"):
            conditions.append("t.term_id = :term_id")
            params["term_id"] = filters["term_id"]
        if filters.get("sec_id"):
            conditions.append("t.sec_id = :sec_id")
            params["sec_id"] = filters["sec_id"]
        if filters.get("tt_id"):
            conditions.append("t.id = :tt_id")
            params["tt_id"] = filters["tt_id"]
        if filters.get("status_id"):
            conditions.append("t.status_id = :status_id")
            params["status_id"] = filters["status_id"]

        where_clause = " AND ".join(conditions)
        stmt = text("""
            SELECT t.* FROM sch_timetable.tb_tt t
            WHERE {where_clause}
            ORDER BY t.created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        return await self._safe_query(stmt, params)

    async def update_timetable(self, data):
        """Update a timetable header record."""
        stmt = text("""
            UPDATE sch_timetable.tb_tt
            SET effective_from = COALESCE(:effective_from, effective_from),
                effective_to = COALESCE(:effective_to, effective_to),
                status_id = COALESCE(:status_id, status_id),
                description = COALESCE(:description, description),
                updated_at = CURRENT_TIMESTAMP,
                updated_by = :updated_by
            WHERE id = :tt_id
            RETURNING id, sec_id, tt_code, version_no, effective_from, effective_to, status_id, description
        """)
        return await self._safe_query(stmt, data)

    async def deactivate_timetable(self, tt_id):
        """Soft-delete a timetable header."""
        stmt = text("""
            UPDATE sch_timetable.tb_tt
            SET is_active = false, updated_at = CURRENT_TIMESTAMP
            WHERE id = :tt_id
            RETURNING id, is_active
        """)
        return await self._safe_query(stmt, {"tt_id": tt_id})

    # =========================================================================
    # 4. TIMETABLE ENTRY (sm_schedule -> timetable entries)
    # =========================================================================

    async def create_tt_entry(self, data):
        """Insert a single timetable entry."""
        stmt = text("""
            INSERT INTO sch_timetable.tb_tt_entry
                (tt_id, inst_id, academic_year_id, term_id, program_id, semester_id, sec_id,
                 course_id, crs_offering_id, fac_id, fac_crs_assignment_id, working_day_id,
                 day_of_week, time_slot_id, room_id, session_type_id, start_date, end_date, is_active)
            VALUES (:tt_id, :inst_id, :academic_year_id, :term_id, :program_id, :semester_id, :sec_id,
                    :course_id, :crs_offering_id, :fac_id, :fac_crs_assignment_id, :working_day_id,
                    :day_of_week, :time_slot_id, :room_id, :session_type_id, :start_date, :end_date, true)
            RETURNING id, tt_id, inst_id, academic_year_id, term_id, program_id, semester_id, sec_id,
                      course_id, crs_offering_id, fac_id, fac_crs_assignment_id, working_day_id,
                      day_of_week, time_slot_id, room_id, session_type_id, start_date, end_date
        """)
        return await self._safe_query(stmt, data)

    async def get_tt_entries(self, filters, page=1, limit=20):
        """Retrieve timetable entries based on filters and pagination."""
        conditions = ["e.is_active = true"]
        params = {"limit": limit, "offset": (page - 1) * limit}

        if filters.get("tt_id"):
            conditions.append("e.tt_id = :tt_id")
            params["tt_id"] = filters["tt_id"]
        if filters.get("tt_entry_id"):
            conditions.append("e.id = :tt_entry_id")
            params["tt_entry_id"] = filters["tt_entry_id"]
        if filters.get("working_day_id"):
            conditions.append("e.working_day_id = :working_day_id")
            params["working_day_id"] = filters["working_day_id"]
        if filters.get("day_of_week"):
            conditions.append("UPPER(e.day_of_week) = UPPER(:day_of_week)")
            params["day_of_week"] = filters["day_of_week"]
        if filters.get("time_slot_id"):
            conditions.append("e.time_slot_id = :time_slot_id")
            params["time_slot_id"] = filters["time_slot_id"]
        if filters.get("room_id"):
            conditions.append("e.room_id = :room_id")
            params["room_id"] = filters["room_id"]
        if filters.get("fac_id"):
            conditions.append("e.fac_id = :fac_id")
            params["fac_id"] = filters["fac_id"]
        if filters.get("fac_crs_assignment_id"):
            conditions.append("e.fac_crs_assignment_id = :fac_crs_assignment_id")
            params["fac_crs_assignment_id"] = filters["fac_crs_assignment_id"]
        if filters.get("sec_id"):
            conditions.append(
                "(e.sec_id = :sec_id OR e.tt_id IN (SELECT id FROM sch_timetable.tb_tt WHERE sec_id = :sec_id AND is_active = true))"
            )
            params["sec_id"] = filters["sec_id"]
        if filters.get("term_id"):
            conditions.append("e.term_id = :term_id")
            params["term_id"] = filters["term_id"]
        if filters.get("academic_year_id"):
            conditions.append("e.academic_year_id = :academic_year_id")
            params["academic_year_id"] = filters["academic_year_id"]

        where_clause = " AND ".join(conditions)
        stmt = text("""
            SELECT e.*, t.tt_code, t.status_id as tt_status
            FROM sch_timetable.tb_tt_entry e
            JOIN sch_timetable.tb_tt t ON e.tt_id = t.id
            WHERE {where_clause}
            ORDER BY e.working_day_id, e.time_slot_id
            LIMIT :limit OFFSET :offset
        """)
        return await self._safe_query(stmt, params)

    async def update_tt_entry(self, data):
        """Update a single timetable entry."""
        stmt = text("""
            UPDATE sch_timetable.tb_tt_entry
            SET course_id = COALESCE(:course_id, course_id),
                crs_offering_id = COALESCE(:crs_offering_id, crs_offering_id),
                fac_id = COALESCE(:fac_id, fac_id),
                fac_crs_assignment_id = COALESCE(:fac_crs_assignment_id, fac_crs_assignment_id),
                working_day_id = COALESCE(:working_day_id, working_day_id),
                day_of_week = COALESCE(:day_of_week, day_of_week),
                time_slot_id = COALESCE(:time_slot_id, time_slot_id),
                room_id = COALESCE(:room_id, room_id),
                session_type_id = COALESCE(:session_type_id, session_type_id),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :tt_entry_id AND is_active = true
            RETURNING id, tt_id, course_id, crs_offering_id, fac_id, fac_crs_assignment_id,
                      working_day_id, day_of_week, time_slot_id, room_id, session_type_id
        """)
        return await self._safe_query(stmt, data)

    async def deactivate_tt_entry(self, tt_entry_id):
        """Soft-delete a timetable entry."""
        stmt = text("""
            UPDATE sch_timetable.tb_tt_entry
            SET is_active = false, updated_at = CURRENT_TIMESTAMP
            WHERE id = :tt_entry_id
            RETURNING id, is_active
        """)
        return await self._safe_query(stmt, {"tt_entry_id": tt_entry_id})

    async def check_faculty_conflict(
        self, fac_id, day_of_week, time_slot_id, term_id=None, exclude_id=None
    ):
        """Check if faculty is double-booked for the given day/slot within a term."""
        params = {
            "fac_id": fac_id,
            "day_of_week": str(day_of_week).upper(),
            "time_slot_id": time_slot_id,
        }
        conditions = [
            "(fac_id = :fac_id OR fac_crs_assignment_id = :fac_id)",
            "(UPPER(day_of_week) = :day_of_week OR working_day_id::text = :day_of_week)",
            "time_slot_id = :time_slot_id",
            "is_active = true",
        ]
        if term_id:
            conditions.append("term_id = :term_id")
            params["term_id"] = term_id
        if exclude_id:
            conditions.append("id != :exclude_id")
            params["exclude_id"] = exclude_id

        where_clause = " AND ".join(conditions)
        stmt = text("""
            SELECT id, tt_id, room_id, fac_id FROM sch_timetable.tb_tt_entry
            WHERE {where_clause}
        """)
        return await self._safe_query(stmt, params)

    async def check_room_conflict(
        self, room_id, day_of_week, time_slot_id, term_id=None, exclude_id=None
    ):
        """Check if room is double-booked for the given day/slot within a term."""
        if not room_id:
            return {"status": "success", "data": []}
        params = {
            "room_id": room_id,
            "day_of_week": str(day_of_week).upper(),
            "time_slot_id": time_slot_id,
        }
        conditions = [
            "room_id = :room_id",
            "(UPPER(day_of_week) = :day_of_week OR working_day_id::text = :day_of_week)",
            "time_slot_id = :time_slot_id",
            "is_active = true",
        ]
        if term_id:
            conditions.append("term_id = :term_id")
            params["term_id"] = term_id
        if exclude_id:
            conditions.append("id != :exclude_id")
            params["exclude_id"] = exclude_id

        where_clause = " AND ".join(conditions)
        stmt = text("""
            SELECT id, tt_id, fac_id FROM sch_timetable.tb_tt_entry
            WHERE {where_clause}
        """)
        return await self._safe_query(stmt, params)

    # =========================================================================
    # 5. TIMETABLE ENTRY SECTION LINKAGE
    # =========================================================================

    async def create_tt_entry_sec(self, tt_entry_id, sec_id):
        """Link a timetable entry to a section."""
        stmt = text("""
            INSERT INTO sch_timetable.tb_tt_entry_sec (tt_entry_id, sec_id)
            VALUES (:tt_entry_id, :sec_id)
            ON CONFLICT (tt_entry_id, sec_id) DO NOTHING
            RETURNING id, tt_entry_id, sec_id
        """)
        return await self._safe_query(
            stmt, {"tt_entry_id": tt_entry_id, "sec_id": sec_id}
        )

    async def get_tt_entry_sections(self, tt_entry_id):
        """Get all sections linked to a timetable entry."""
        stmt = text("""
            SELECT * FROM sch_timetable.tb_tt_entry_sec WHERE tt_entry_id = :tt_entry_id
        """)
        return await self._safe_query(stmt, {"tt_entry_id": tt_entry_id})

    async def delete_tt_entry_sec(self, tt_entry_id, sec_id=None):
        """Remove section linkage for a timetable entry."""
        if sec_id:
            stmt = text("""
                DELETE FROM sch_timetable.tb_tt_entry_sec
                WHERE tt_entry_id = :tt_entry_id AND sec_id = :sec_id
                RETURNING id
            """)
            return await self._safe_query(
                stmt, {"tt_entry_id": tt_entry_id, "sec_id": sec_id}
            )
        stmt = text("""
            DELETE FROM sch_timetable.tb_tt_entry_sec WHERE tt_entry_id = :tt_entry_id RETURNING id
        """)
        return await self._safe_query(stmt, {"tt_entry_id": tt_entry_id})

    # =========================================================================
    # 6. FACULTY ALLOCATION (sm_allocation -> facultyAllocation)
    # References sch_course_ops.tb_fac_crs_assignment
    # =========================================================================

    async def create_faculty_allocation(self, data):
        """Insert a faculty-course assignment record."""
        stmt = text("""
            INSERT INTO sch_course_ops.tb_fac_crs_assignment
                (crs_offering_id, fac_id, assigment_role_id, assignment_status_id,
                 workload_percent, is_primary, start_date, remarks)
            VALUES (:crs_offering_id, :fac_id, :assignment_role_id, 'ACTIVE',
                    :workload_percent, :is_primary, CURRENT_DATE, :remarks)
            RETURNING id, crs_offering_id, fac_id, assigment_role_id, assignment_status_id, is_primary
        """)
        return await self._safe_query(stmt, data)

    async def get_faculty_allocations(self, filters, page=1, limit=20):
        """Retrieve faculty-course assignments based on filters and pagination."""
        conditions = ["assignment_status_id = 'ACTIVE'"]
        params = {"limit": limit, "offset": (page - 1) * limit}

        if filters.get("allocation_id"):
            conditions.append("id = :allocation_id")
            params["allocation_id"] = filters["allocation_id"]
        if filters.get("fac_id"):
            conditions.append("fac_id = :fac_id")
            params["fac_id"] = filters["fac_id"]
        if filters.get("crs_offering_id"):
            conditions.append("crs_offering_id = :crs_offering_id")
            params["crs_offering_id"] = filters["crs_offering_id"]

        where_clause = " AND ".join(conditions)
        stmt = text("""
            SELECT * FROM sch_course_ops.tb_fac_crs_assignment
            WHERE {where_clause}
            ORDER BY id
            LIMIT :limit OFFSET :offset
        """)
        return await self._safe_query(stmt, params)

    async def update_faculty_allocation(self, data):
        """Update a faculty allocation record."""
        stmt = text("""
            UPDATE sch_course_ops.tb_fac_crs_assignment
            SET fac_id = COALESCE(:fac_id, fac_id),
                crs_offering_id = COALESCE(:crs_offering_id, crs_offering_id),
                remarks = COALESCE(:remarks, remarks)
            WHERE id = :allocation_id
            RETURNING id, crs_offering_id, fac_id, assigment_role_id, assignment_status_id
        """)
        return await self._safe_query(stmt, data)

    async def deactivate_faculty_allocation(self, allocation_id):
        """Deactivate a faculty allocation."""
        stmt = text("""
            UPDATE sch_course_ops.tb_fac_crs_assignment
            SET assignment_status_id = 'INACTIVE'
            WHERE id = :allocation_id
            RETURNING id, assignment_status_id
        """)
        return await self._safe_query(stmt, {"allocation_id": allocation_id})

    async def check_faculty_allocation_dependencies(self, allocation_id):
        """Check if any active timetable entries reference this faculty allocation."""
        stmt = text("""
            SELECT id, tt_id FROM sch_timetable.tb_tt_entry
            WHERE (fac_crs_assignment_id = :allocation_id OR fac_id = :allocation_id) AND is_active = true
        """)
        return await self._safe_query(stmt, {"allocation_id": allocation_id})

    # =========================================================================
    # 7. ROOM ALLOCATION (sm_allocation -> roomAllocation)
    # =========================================================================

    async def assign_room_to_entry(self, tt_entry_id, room_id):
        """Assign a room to a timetable entry."""
        stmt = text("""
            UPDATE sch_timetable.tb_tt_entry
            SET room_id = :room_id, updated_at = CURRENT_TIMESTAMP
            WHERE id = :tt_entry_id AND is_active = true
            RETURNING id, tt_id, room_id, working_day_id, day_of_week, time_slot_id, start_date
        """)
        return await self._safe_query(
            stmt, {"tt_entry_id": tt_entry_id, "room_id": room_id}
        )

    async def remove_room_from_entry(self, tt_entry_id):
        """Remove room assignment from a timetable entry (set to NULL)."""
        stmt = text("""
            UPDATE sch_timetable.tb_tt_entry
            SET room_id = NULL, updated_at = CURRENT_TIMESTAMP
            WHERE id = :tt_entry_id AND is_active = true
            RETURNING id, tt_id, room_id
        """)
        return await self._safe_query(stmt, {"tt_entry_id": tt_entry_id})

    async def get_room_allocations(self, filters, page=1, limit=20):
        """Retrieve room allocations with optional conflict-only filter and pagination."""
        conditions = ["e.is_active = true", "e.room_id IS NOT NULL"]
        params = {"limit": limit, "offset": (page - 1) * limit}

        if filters.get("room_id"):
            conditions.append("e.room_id = :room_id")
            params["room_id"] = filters["room_id"]
        if filters.get("tt_entry_id"):
            conditions.append("e.id = :tt_entry_id")
            params["tt_entry_id"] = filters["tt_entry_id"]

        where_clause = " AND ".join(conditions)

        if filters.get("conflict_only"):
            # Return only allocations where room is double-booked
            stmt = text("""
                SELECT e1.id, e1.tt_id, e1.room_id, e1.working_day_id, e1.day_of_week, e1.time_slot_id, e1.start_date,
                       e2.id as conflicting_entry_id, e2.tt_id as conflicting_tt_id
                FROM sch_timetable.tb_tt_entry e1
                JOIN sch_timetable.tb_tt_entry e2
                    ON e1.room_id = e2.room_id
                    AND (UPPER(e1.day_of_week) = UPPER(e2.day_of_week) OR e1.working_day_id = e2.working_day_id)
                    AND e1.time_slot_id = e2.time_slot_id
                    AND (e1.term_id = e2.term_id OR e1.term_id IS NULL)
                    AND e1.id != e2.id
                    AND e2.is_active = true
                WHERE e1.is_active = true AND e1.room_id IS NOT NULL
                ORDER BY e1.room_id, e1.working_day_id, e1.time_slot_id
                LIMIT :limit OFFSET :offset
            """)
            return await self._safe_query(stmt, params)

        stmt = text("""
            SELECT e.id, e.tt_id, e.room_id, e.working_day_id, e.day_of_week, e.time_slot_id,
                   e.start_date, e.end_date, e.crs_offering_id, e.course_id, e.fac_id, e.fac_crs_assignment_id
            FROM sch_timetable.tb_tt_entry e
            WHERE {where_clause}
            ORDER BY e.room_id, e.working_day_id, e.time_slot_id
            LIMIT :limit OFFSET :offset
        """)
        return await self._safe_query(stmt, params)

    # =========================================================================
    # 8. CLASS SESSION (materialised sessions)
    # =========================================================================

    async def create_class_session(self, data):
        """Insert a class session record."""
        stmt = text("""
            INSERT INTO sch_timetable.tb_class_session
                (tt_entry_id, session_date, session_status_id, session_source_id, remarks)
            VALUES (:tt_entry_id, :session_date, :session_status_id, :session_source_id, :remarks)
            ON CONFLICT (tt_entry_id, session_date) DO NOTHING
            RETURNING id, tt_entry_id, session_date, session_status_id, session_source_id
        """)
        return await self._safe_query(stmt, data)

    async def get_class_sessions(self, filters, page=1, limit=20):
        """Retrieve class sessions based on filters and pagination."""
        conditions = []
        params = {"limit": limit, "offset": (page - 1) * limit}

        if filters.get("tt_entry_id"):
            conditions.append("cs.tt_entry_id = :tt_entry_id")
            params["tt_entry_id"] = filters["tt_entry_id"]
        if filters.get("class_session_id"):
            conditions.append("cs.id = :class_session_id")
            params["class_session_id"] = filters["class_session_id"]
        if filters.get("session_date"):
            conditions.append("cs.session_date = :session_date")
            params["session_date"] = filters["session_date"]
        if filters.get("session_status_id"):
            conditions.append("cs.session_status_id = :session_status_id")
            params["session_status_id"] = filters["session_status_id"]
        if filters.get("date_from"):
            conditions.append("cs.session_date >= :date_from")
            params["date_from"] = filters["date_from"]
        if filters.get("date_to"):
            conditions.append("cs.session_date <= :date_to")
            params["date_to"] = filters["date_to"]

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        stmt = text("""
            SELECT cs.* FROM sch_timetable.tb_class_session cs
            WHERE {where_clause}
            ORDER BY cs.session_date
            LIMIT :limit OFFSET :offset
        """)
        return await self._safe_query(stmt, params)

    async def update_class_session_status(self, class_session_id, status_id):
        """Update the status of a class session."""
        stmt = text("""
            UPDATE sch_timetable.tb_class_session
            SET session_status_id = :status_id, updated_at = CURRENT_TIMESTAMP
            WHERE id = :class_session_id
            RETURNING id, session_status_id
        """)
        return await self._safe_query(
            stmt, {"class_session_id": class_session_id, "status_id": status_id}
        )

    # =========================================================================
    # 9. CLASS SESSION FACULTY
    # =========================================================================

    async def create_class_session_fac(self, data):
        """Link a faculty member to a class session."""
        stmt = text("""
            INSERT INTO sch_timetable.tb_class_session_fac (class_session_id, fac_id, is_primary)
            VALUES (:class_session_id, :fac_id, :is_primary)
            ON CONFLICT (class_session_id, fac_id) DO UPDATE SET is_primary = :is_primary
            RETURNING id, class_session_id, fac_id, is_primary
        """)
        return await self._safe_query(stmt, data)

    async def get_class_session_faculty(self, class_session_id):
        """Get all faculty for a class session."""
        stmt = text("""
            SELECT * FROM sch_timetable.tb_class_session_fac
            WHERE class_session_id = :class_session_id
            ORDER BY is_primary DESC
        """)
        return await self._safe_query(stmt, {"class_session_id": class_session_id})

    # =========================================================================
    # 10. CLASS SESSION ROOM
    # =========================================================================

    async def create_class_session_room(self, data):
        """Assign a room to a class session."""
        stmt = text("""
            INSERT INTO sch_timetable.tb_class_session_room (class_session_id, room_id)
            VALUES (:class_session_id, :room_id)
            ON CONFLICT (class_session_id, room_id) DO NOTHING
            RETURNING id, class_session_id, room_id
        """)
        return await self._safe_query(stmt, data)

    # =========================================================================
    # 11. SUBSTITUTION (sm_substitution -> substitution)
    # Maps to tb_class_session_change with change_type_id = 'FAC_CHANGE'
    # =========================================================================

    async def create_substitution(self, data):
        """Create a faculty substitution record."""
        stmt = text("""
            INSERT INTO sch_timetable.tb_class_session_change
                (class_session_id, tt_entry_id, change_type_id, old_fac_id, new_fac_id, reason, status, created_by)
            VALUES (:class_session_id, :tt_entry_id, 'FAC_CHANGE', :old_fac_id, :new_fac_id, :reason, 'ACTIVE', :created_by)
            RETURNING id, class_session_id, tt_entry_id, change_type_id, old_fac_id, new_fac_id, reason, status
        """)
        return await self._safe_query(stmt, data)

    async def get_substitutions(self, filters, page=1, limit=20):
        """Retrieve substitution records based on filters and pagination."""
        conditions = ["csc.change_type_id = 'FAC_CHANGE'"]
        params = {"limit": limit, "offset": (page - 1) * limit}

        if filters.get("substitution_id"):
            conditions.append("csc.id = :substitution_id")
            params["substitution_id"] = filters["substitution_id"]
        if filters.get("class_session_id"):
            conditions.append("csc.class_session_id = :class_session_id")
            params["class_session_id"] = filters["class_session_id"]
        if filters.get("tt_entry_id"):
            conditions.append("csc.tt_entry_id = :tt_entry_id")
            params["tt_entry_id"] = filters["tt_entry_id"]
        if filters.get("old_fac_id"):
            conditions.append("csc.old_fac_id = :old_fac_id")
            params["old_fac_id"] = filters["old_fac_id"]
        if filters.get("fac_id") or filters.get("new_fac_id"):
            target_fac = filters.get("fac_id") or filters.get("new_fac_id")
            conditions.append(
                "(csc.new_fac_id = :target_fac OR csc.old_fac_id = :target_fac)"
            )
            params["target_fac"] = target_fac
        if filters.get("status"):
            conditions.append("csc.status = :status")
            params["status"] = filters["status"]

        where_clause = " AND ".join(conditions)
        stmt = text("""
            SELECT csc.*
            FROM sch_timetable.tb_class_session_change csc
            WHERE {where_clause}
            ORDER BY csc.created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        return await self._safe_query(stmt, params)

    async def update_substitution(self, data):
        """Update a substitution record."""
        stmt = text("""
            UPDATE sch_timetable.tb_class_session_change
            SET new_fac_id = COALESCE(:new_fac_id, new_fac_id),
                reason = COALESCE(:reason, reason),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :substitution_id AND change_type_id = 'FAC_CHANGE' AND status = 'ACTIVE'
            RETURNING id, class_session_id, tt_entry_id, old_fac_id, new_fac_id, reason, status
        """)
        return await self._safe_query(stmt, data)

    async def cancel_substitution(self, substitution_id):
        """Cancel a substitution (revert to original faculty)."""
        stmt = text("""
            UPDATE sch_timetable.tb_class_session_change
            SET status = 'CANCELLED', updated_at = CURRENT_TIMESTAMP
            WHERE id = :substitution_id AND change_type_id = 'FAC_CHANGE'
            RETURNING id, class_session_id, tt_entry_id, old_fac_id, new_fac_id, status
        """)
        return await self._safe_query(stmt, {"substitution_id": substitution_id})

    async def check_active_substitution(self, tt_entry_id=None, class_session_id=None):
        """Check if an active substitution already exists for a timetable entry or class session."""
        if tt_entry_id:
            stmt = text("""
                SELECT id, old_fac_id, new_fac_id FROM sch_timetable.tb_class_session_change
                WHERE tt_entry_id = :tt_entry_id
                  AND change_type_id = 'FAC_CHANGE' AND status = 'ACTIVE'
            """)
            return await self._safe_query(stmt, {"tt_entry_id": tt_entry_id})
        stmt = text("""
            SELECT id, old_fac_id, new_fac_id FROM sch_timetable.tb_class_session_change
            WHERE class_session_id = :class_session_id
              AND change_type_id = 'FAC_CHANGE' AND status = 'ACTIVE'
        """)
        return await self._safe_query(stmt, {"class_session_id": class_session_id})

    # =========================================================================
    # 12. TIMETABLE APPROVAL (sm_approval -> timetableApproval)
    # Maps to tb_tt.status_id transitions
    # =========================================================================

    async def submit_for_approval(self, tt_id, remarks, submitted_by):
        """Transition timetable status from DRAFT to PENDING_APPROVAL."""
        stmt = text("""
            UPDATE sch_timetable.tb_tt
            SET status_id = 'PENDING_APPROVAL',
                description = COALESCE(:remarks, description),
                updated_at = CURRENT_TIMESTAMP,
                updated_by = :submitted_by
            WHERE id = :tt_id AND status_id = 'DRAFT' AND is_active = true
            RETURNING id, sec_id, tt_code, status_id, description
        """)
        return await self._safe_query(
            stmt, {"tt_id": tt_id, "remarks": remarks, "submitted_by": submitted_by}
        )

    async def approve_timetable(self, tt_id, remarks, approved_by):
        """Approve a timetable (PENDING_APPROVAL -> PUBLISHED)."""
        stmt = text("""
            UPDATE sch_timetable.tb_tt
            SET status_id = 'PUBLISHED',
                description = COALESCE(:remarks, description),
                updated_at = CURRENT_TIMESTAMP,
                updated_by = :approved_by
            WHERE id = :tt_id AND status_id = 'PENDING_APPROVAL' AND is_active = true
            RETURNING id, sec_id, tt_code, status_id, description
        """)
        return await self._safe_query(
            stmt, {"tt_id": tt_id, "remarks": remarks, "approved_by": approved_by}
        )

    async def reject_timetable(self, tt_id, remarks, rejected_by):
        """Reject a timetable (PENDING_APPROVAL -> DRAFT with remarks)."""
        stmt = text("""
            UPDATE sch_timetable.tb_tt
            SET status_id = 'DRAFT',
                description = COALESCE(:remarks, description),
                updated_at = CURRENT_TIMESTAMP,
                updated_by = :rejected_by
            WHERE id = :tt_id AND status_id = 'PENDING_APPROVAL' AND is_active = true
            RETURNING id, sec_id, tt_code, status_id, description
        """)
        return await self._safe_query(
            stmt, {"tt_id": tt_id, "remarks": remarks, "rejected_by": rejected_by}
        )

    async def withdraw_approval(self, tt_id, remarks, withdrawn_by):
        """Withdraw a pending approval request (PENDING_APPROVAL -> DRAFT)."""
        stmt = text("""
            UPDATE sch_timetable.tb_tt
            SET status_id = 'DRAFT',
                description = COALESCE(:remarks, description),
                updated_at = CURRENT_TIMESTAMP,
                updated_by = :withdrawn_by
            WHERE id = :tt_id AND status_id = 'PENDING_APPROVAL' AND is_active = true
            RETURNING id, sec_id, tt_code, status_id, description
        """)
        return await self._safe_query(
            stmt, {"tt_id": tt_id, "remarks": remarks, "withdrawn_by": withdrawn_by}
        )

    async def get_approval_requests(self, filters, page=1, limit=20):
        """Retrieve timetables pending approval based on filters and pagination."""
        conditions = ["t.is_active = true"]
        params = {"limit": limit, "offset": (page - 1) * limit}

        if filters.get("status_filter"):
            conditions.append("t.status_id = :status_filter")
            params["status_filter"] = filters["status_filter"]
        else:
            conditions.append(
                "t.status_id IN ('PENDING_APPROVAL', 'PUBLISHED', 'ACTIVE', 'DRAFT')"
            )

        if filters.get("sec_id"):
            conditions.append("t.sec_id = :sec_id")
            params["sec_id"] = filters["sec_id"]

        where_clause = " AND ".join(conditions)
        stmt = text("""
            SELECT t.* FROM sch_timetable.tb_tt t
            WHERE {where_clause}
            ORDER BY t.updated_at DESC
            LIMIT :limit OFFSET :offset
        """)
        return await self._safe_query(stmt, params)

    # =========================================================================
    # 13. EXTRA CLASS
    # =========================================================================

    async def create_extra_class(self, data):
        """Insert an extra class record."""
        stmt = text("""
            INSERT INTO sch_timetable.tb_extra_class
                (crs_offering_id, course_id, sec_id, fac_id, room_id, session_date,
                 time_slot_id, session_type_id, reason, class_session_id, is_active, created_by)
            VALUES (:crs_offering_id, :course_id, :sec_id, :fac_id, :room_id, :session_date,
                    :time_slot_id, :session_type_id, :reason, :class_session_id, true, :created_by)
            RETURNING id, crs_offering_id, course_id, sec_id, fac_id, room_id, session_date, time_slot_id, reason
        """)
        return await self._safe_query(stmt, data)

    async def get_extra_classes(self, filters, page=1, limit=20):
        """Retrieve extra class records based on filters and pagination."""
        conditions = ["ec.is_active = true"]
        params = {"limit": limit, "offset": (page - 1) * limit}

        if filters.get("sec_id"):
            conditions.append("ec.sec_id = :sec_id")
            params["sec_id"] = filters["sec_id"]
        if filters.get("fac_id"):
            conditions.append("ec.fac_id = :fac_id")
            params["fac_id"] = filters["fac_id"]
        if filters.get("session_date"):
            conditions.append("ec.session_date = :session_date")
            params["session_date"] = filters["session_date"]

        where_clause = " AND ".join(conditions)
        stmt = text("""
            SELECT ec.* FROM sch_timetable.tb_extra_class ec
            WHERE {where_clause}
            ORDER BY ec.session_date
            LIMIT :limit OFFSET :offset
        """)
        return await self._safe_query(stmt, params)

    # =========================================================================
    # 14. CLASS CANCELLATION
    # =========================================================================

    async def create_class_cancellation(self, data):
        """Insert a class cancellation record."""
        stmt = text("""
            INSERT INTO sch_timetable.tb_class_cancellation
                (class_session_id, cancellation_reason_id, cancelled_by, cancelled_on, remarks)
            VALUES (:class_session_id, :cancellation_reason_id, :cancelled_by, CURRENT_TIMESTAMP, :remarks)
            RETURNING id, class_session_id, cancellation_reason_id, cancelled_by, cancelled_on, remarks
        """)
        return await self._safe_query(stmt, data)

    async def get_class_cancellations(self, filters, page=1, limit=20):
        """Retrieve class cancellation records based on filters and pagination."""
        conditions = []
        params = {"limit": limit, "offset": (page - 1) * limit}

        if filters.get("class_session_id"):
            conditions.append("cc.class_session_id = :class_session_id")
            params["class_session_id"] = filters["class_session_id"]

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        stmt = text("""
            SELECT cc.*, cs.session_date, cs.tt_entry_id
            FROM sch_timetable.tb_class_cancellation cc
            JOIN sch_timetable.tb_class_session cs ON cc.class_session_id = cs.id
            WHERE {where_clause}
            ORDER BY cc.cancelled_on DESC
            LIMIT :limit OFFSET :offset
        """)
        return await self._safe_query(stmt, params)

    # =========================================================================
    # 15. HOLIDAY ADJUSTMENT
    # =========================================================================

    async def create_holiday_adjustment(self, data):
        """Insert a holiday adjustment record."""
        stmt = text("""
            INSERT INTO sch_timetable.tb_holiday_adjustment
                (acad_term_id, holiday_date, adjustment_type_id,
                 source_working_day_id, target_working_day_id, target_date, remarks, created_by)
            VALUES (:acad_term_id, :holiday_date, :adjustment_type_id,
                    :source_working_day_id, :target_working_day_id, :target_date, :remarks, :created_by)
            RETURNING id, acad_term_id, holiday_date, adjustment_type_id, target_date, remarks
        """)
        return await self._safe_query(stmt, data)

    async def get_holiday_adjustments(self, acad_term_id, page=1, limit=20):
        """Retrieve holiday adjustments for an academic term with pagination."""
        stmt = text("""
            SELECT * FROM sch_timetable.tb_holiday_adjustment
            WHERE acad_term_id = :acad_term_id
            ORDER BY holiday_date
            LIMIT :limit OFFSET :offset
        """)
        return await self._safe_query(
            stmt,
            {
                "acad_term_id": acad_term_id,
                "limit": limit,
                "offset": (page - 1) * limit,
            },
        )
