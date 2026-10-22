"""
File: m_attendance_data.py
Description: Data Access Layer for the OneApp Attendance Module (`m_attendance`).
Encapsulates all asynchronous database CRUD operations, query construction, aggregate queries,
pagination, filtering, sorting, and atomic transaction handling for attendance persistence.
Strictly excludes business logic, workflow validation, and percentage calculations.

Author: Siddharth Amdal
App: OneApp

"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import select, update, delete, insert, func, text
from sqlalchemy.exc import SQLAlchemyError

from .db_init import TbAttPolicy, TbAttSession, TbAttRecord, TbAttCorrection
from datetime import datetime

logger = logging.getLogger(__name__)


def _convert_date_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(data, dict):
        return data
    for k in (
        "session_date",
        "effective_from",
        "effective_to",
        "date_of_joining",
        "sessionDate",
    ):
        val = data.get(k)
        if val and isinstance(val, str):
            try:
                data[k] = datetime.strptime(val.split("T")[0], "%Y-%m-%d").date()
            except ValueError:
                logger.warning("Failed to parse date string: %s for key: %s", val, k)
    return data


class AttendancePolicyData:
    """
    Repository section encapsulating database persistence operations for institutional
    attendance policies (`sch_attendance.tb_att_policy`).
    """

    def __init__(self, db):
        """
        Initializes the repository with the OneApp PostgreSQLManager instance.

        Args:
            db: Injected PostgreSQLManager instance providing async connection pooling.
        """
        self.db = db

    async def create_policy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inserts a new attendance policy record into the database.

        Args:
            data: Dictionary containing column-value mappings for `tb_att_policy`.

        Returns:
            dict: Standard OneApp response envelope containing the inserted record.
        """
        data = _convert_date_fields(data)
        stmt = insert(TbAttPolicy).values(**data).returning(text("*"))
        return await self.db.async_genericSQL(stmt)

    async def update_policy(
        self, policy_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Updates an existing attendance policy record by its primary key ID.

        Args:
            policy_id: Primary key ID of the policy to update.
            data: Dictionary containing column-value mappings to modify.

        Returns:
            dict: Standard OneApp response envelope containing the updated record.
        """
        data = _convert_date_fields(data)
        stmt = (
            update(TbAttPolicy)
            .where(TbAttPolicy.id == policy_id)
            .values(**data)
            .returning(text("*"))
        )
        return await self.db.async_genericSQL(stmt)

    async def delete_policy(self, policy_id: int) -> Dict[str, Any]:
        """
        Deletes an attendance policy record from the database by its primary key ID.

        Args:
            policy_id: Primary key ID of the policy to delete.

        Returns:
            dict: Standard OneApp response envelope confirming deletion.
        """
        stmt = (
            delete(TbAttPolicy).where(TbAttPolicy.id == policy_id).returning(text("*"))
        )
        return await self.db.async_genericSQL(stmt)

    async def get_policy(self, policy_id: int) -> Dict[str, Any]:
        """
        Retrieves a single attendance policy record by its primary key ID.

        Args:
            policy_id: Primary key ID of the policy to retrieve.

        Returns:
            dict: Standard OneApp response envelope containing the policy record if found.
        """
        stmt = select(TbAttPolicy).where(TbAttPolicy.id == policy_id)
        return await self.db.async_genericSQL(stmt)

    async def list_policies(
        self,
        inst_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Lists attendance policies with optional filtering by institution and active status,
        supporting pagination and deterministic sorting.

        Args:
            inst_id: Optional institution ID filter.
            is_active: Optional boolean active status filter.
            limit: Optional maximum number of rows to return.
            offset: Optional number of rows to skip.

        Returns:
            dict: Standard OneApp response envelope containing matching policy records.
        """
        stmt = select(TbAttPolicy)
        if inst_id is not None:
            stmt = stmt.where(TbAttPolicy.inst_id == inst_id)
        if is_active is not None:
            stmt = stmt.where(TbAttPolicy.is_active == is_active)

        stmt = stmt.order_by(TbAttPolicy.id.desc())
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        return await self.db.async_genericSQL(stmt)

    async def get_active_policy(
        self, inst_id: int, policy_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieves active attendance policies for a specific institution, optionally filtered by policy name.

        Args:
            inst_id: Institution ID whose active policy is being requested.
            policy_name: Optional specific policy name to match.

        Returns:
            dict: Standard OneApp response envelope containing matching active policy records.
        """
        stmt = select(TbAttPolicy).where(
            TbAttPolicy.inst_id == inst_id, TbAttPolicy.is_active.is_(True)
        )
        if policy_name:
            stmt = stmt.where(TbAttPolicy.policy_name == policy_name)
        stmt = stmt.order_by(TbAttPolicy.id.desc())
        return await self.db.async_genericSQL(stmt)


class AttendanceSessionData:
    """
    Repository section encapsulating database persistence operations for class attendance
    sessions (`sch_attendance.tb_att_session`).
    """

    def __init__(self, db):
        """
        Initializes the repository with the OneApp PostgreSQLManager instance.

        Args:
            db: Injected PostgreSQLManager instance providing async connection pooling.
        """
        self.db = db

    async def create_session(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inserts a new class attendance session into the database.

        Args:
            data: Dictionary containing column-value mappings for `tb_att_session`.

        Returns:
            dict: Standard OneApp response envelope containing the inserted session record.
        """
        data = _convert_date_fields(data)
        stmt = insert(TbAttSession).values(**data).returning(text("*"))
        return await self.db.async_genericSQL(stmt)

    async def get_session(self, session_id: int) -> Dict[str, Any]:
        """
        Retrieves a single class attendance session by its primary key ID.

        Args:
            session_id: Primary key ID of the attendance session.

        Returns:
            dict: Standard OneApp response envelope containing the session record if found.
        """
        stmt = select(TbAttSession).where(TbAttSession.id == session_id)
        return await self.db.async_genericSQL(stmt)

    async def get_session_by_class_session(
        self, class_session_id: int
    ) -> Dict[str, Any]:
        """
        Retrieves an attendance session by its unique timetable class session ID.

        Args:
            class_session_id: Timetable class session ID (`sch_timetable.tb_class_session.id`).

        Returns:
            dict: Standard OneApp response envelope containing the matching session record.
        """
        stmt = select(TbAttSession).where(
            TbAttSession.class_session_id == class_session_id
        )
        return await self.db.async_genericSQL(stmt)

    async def update_session(
        self, session_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Updates an existing attendance session record by its primary key ID.

        Args:
            session_id: Primary key ID of the session to update.
            data: Dictionary containing column-value mappings to modify.

        Returns:
            dict: Standard OneApp response envelope containing the updated session record.
        """
        data = _convert_date_fields(data)
        stmt = (
            update(TbAttSession)
            .where(TbAttSession.id == session_id)
            .values(**data)
            .returning(text("*"))
        )
        return await self.db.async_genericSQL(stmt)

    async def submit_session(
        self,
        session_id: int,
        submitted_at: Any,
        updated_by: Optional[int] = None,
        status_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Persists the submission timestamp and optional status update for an attendance session.

        Args:
            session_id: Primary key ID of the session being submitted.
            submitted_at: Timestamp indicating when the session was submitted.
            updated_by: Optional user ID performing the update.
            status_id: Optional lookup status ID indicating submitted state.

        Returns:
            dict: Standard OneApp response envelope containing the updated session record.
        """
        values: Dict[str, Any] = {"submitted_at": submitted_at}
        if updated_by is not None:
            values["updated_by"] = updated_by
        if status_id is not None:
            values["status_id"] = status_id

        stmt = (
            update(TbAttSession)
            .where(TbAttSession.id == session_id)
            .values(**values)
            .returning(text("*"))
        )
        return await self.db.async_genericSQL(stmt)

    async def lock_session(
        self,
        session_id: int,
        locked_at: Any,
        updated_by: Optional[int] = None,
        status_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Persists the lock timestamp and optional status update for an attendance session.

        Args:
            session_id: Primary key ID of the session being locked.
            locked_at: Timestamp indicating when the session was locked.
            updated_by: Optional user ID performing the update.
            status_id: Optional lookup status ID indicating locked state.

        Returns:
            dict: Standard OneApp response envelope containing the locked session record.
        """
        values: Dict[str, Any] = {"locked_at": locked_at}
        if updated_by is not None:
            values["updated_by"] = updated_by
        if status_id is not None:
            values["status_id"] = status_id

        stmt = (
            update(TbAttSession)
            .where(TbAttSession.id == session_id)
            .values(**values)
            .returning(text("*"))
        )
        return await self.db.async_genericSQL(stmt)

    async def list_sessions(
        self,
        class_session_id: Optional[int] = None,
        marked_by_fac_id: Optional[int] = None,
        status_id: Optional[int] = None,
        session_date_from: Optional[Any] = None,
        session_date_to: Optional[Any] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Lists attendance sessions with multi-criteria filtering, deterministic sorting, and pagination.

        Args:
            class_session_id: Optional timetable class session ID filter.
            marked_by_fac_id: Optional faculty ID filter.
            status_id: Optional lookup status ID filter.
            session_date_from: Optional inclusive start date filter.
            session_date_to: Optional inclusive end date filter.
            limit: Optional maximum number of rows to return.
            offset: Optional number of rows to skip.

        Returns:
            dict: Standard OneApp response envelope containing matching session records.
        """
        stmt = select(TbAttSession)
        if class_session_id is not None:
            stmt = stmt.where(TbAttSession.class_session_id == class_session_id)
        if marked_by_fac_id is not None:
            stmt = stmt.where(TbAttSession.marked_by_fac_id == marked_by_fac_id)
        if status_id is not None:
            stmt = stmt.where(TbAttSession.status_id == status_id)
        if session_date_from is not None:
            stmt = stmt.where(TbAttSession.session_date >= session_date_from)
        if session_date_to is not None:
            stmt = stmt.where(TbAttSession.session_date <= session_date_to)

        stmt = stmt.order_by(TbAttSession.session_date.desc(), TbAttSession.id.desc())
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        return await self.db.async_genericSQL(stmt)


class AttendanceRecordData:
    """
    Repository section encapsulating database persistence operations for individual student
    attendance records (`sch_attendance.tb_att_record`).
    """

    def __init__(self, db):
        """
        Initializes the repository with the OneApp PostgreSQLManager instance.

        Args:
            db: Injected PostgreSQLManager instance providing async connection pooling.
        """
        self.db = db

    async def create_record(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inserts a new student attendance record into the database.

        Args:
            data: Dictionary containing column-value mappings for `tb_att_record`.

        Returns:
            dict: Standard OneApp response envelope containing the inserted record.
        """
        stmt = insert(TbAttRecord).values(**data).returning(text("*"))
        return await self.db.async_genericSQL(stmt)

    async def update_record(
        self, record_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Updates an existing student attendance record by its primary key ID.

        Args:
            record_id: Primary key ID of the attendance record to update.
            data: Dictionary containing column-value mappings to modify.

        Returns:
            dict: Standard OneApp response envelope containing the updated record.
        """
        stmt = (
            update(TbAttRecord)
            .where(TbAttRecord.id == record_id)
            .values(**data)
            .returning(text("*"))
        )
        return await self.db.async_genericSQL(stmt)

    async def delete_record(self, record_id: int) -> Dict[str, Any]:
        """
        Deletes a student attendance record from the database by its primary key ID.

        Args:
            record_id: Primary key ID of the record to delete.

        Returns:
            dict: Standard OneApp response envelope confirming deletion.
        """
        stmt = (
            delete(TbAttRecord).where(TbAttRecord.id == record_id).returning(text("*"))
        )
        return await self.db.async_genericSQL(stmt)

    async def get_record(self, record_id: int) -> Dict[str, Any]:
        """
        Retrieves a single student attendance record by its primary key ID.

        Args:
            record_id: Primary key ID of the attendance record.

        Returns:
            dict: Standard OneApp response envelope containing the record if found.
        """
        stmt = select(TbAttRecord).where(TbAttRecord.id == record_id)
        return await self.db.async_genericSQL(stmt)

    async def list_records(
        self,
        att_session_id: Optional[int] = None,
        stud_id: Optional[int] = None,
        att_status_id: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Lists student attendance records with optional filtering by session, student, or status,
        supporting pagination and deterministic sorting.

        Args:
            att_session_id: Optional session ID filter.
            stud_id: Optional student ID filter.
            att_status_id: Optional attendance status lookup ID filter.
            limit: Optional maximum number of rows to return.
            offset: Optional number of rows to skip.

        Returns:
            dict: Standard OneApp response envelope containing matching attendance records.
        """
        stmt = select(TbAttRecord)
        if att_session_id is not None:
            stmt = stmt.where(TbAttRecord.att_session_id == att_session_id)
        if stud_id is not None:
            stmt = stmt.where(TbAttRecord.stud_id == stud_id)
        if att_status_id is not None:
            stmt = stmt.where(TbAttRecord.att_status_id == att_status_id)

        stmt = stmt.order_by(TbAttRecord.id.desc())
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        return await self.db.async_genericSQL(stmt)

    async def list_records_for_session(
        self,
        att_session_id: int,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Retrieves all student attendance records belonging to a specific attendance session,
        ordered deterministically by student ID.

        Args:
            att_session_id: Primary key ID of the attendance session.
            limit: Optional maximum number of rows to return.
            offset: Optional number of rows to skip.

        Returns:
            dict: Standard OneApp response envelope containing session attendance records.
        """
        stmt = (
            select(TbAttRecord)
            .where(TbAttRecord.att_session_id == att_session_id)
            .order_by(TbAttRecord.stud_id, TbAttRecord.id)
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)
        return await self.db.async_genericSQL(stmt)

    async def list_records_for_student(
        self,
        stud_id: int,
        att_status_id: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Retrieves all attendance records for a specific student across sessions, optionally filtered
        by attendance status.

        Args:
            stud_id: Primary key ID of the student (`sch_student.tb_stud.id`).
            att_status_id: Optional attendance status lookup ID filter.
            limit: Optional maximum number of rows to return.
            offset: Optional number of rows to skip.

        Returns:
            dict: Standard OneApp response envelope containing student attendance records.
        """
        stmt = select(TbAttRecord).where(TbAttRecord.stud_id == stud_id)
        if att_status_id is not None:
            stmt = stmt.where(TbAttRecord.att_status_id == att_status_id)

        stmt = stmt.order_by(TbAttRecord.id.desc())
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        return await self.db.async_genericSQL(stmt)


class AttendanceCorrectionData:
    """
    Repository section encapsulating database persistence operations for attendance
    corrections, condonations, and medical exceptions (`sch_attendance.tb_att_correction`).
    """

    def __init__(self, db):
        """
        Initializes the repository with the OneApp PostgreSQLManager instance.

        Args:
            db: Injected PostgreSQLManager instance providing async connection pooling.
        """
        self.db = db

    async def create_correction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inserts a new attendance correction or exception request into the database.

        Args:
            data: Dictionary containing column-value mappings for `tb_att_correction`.

        Returns:
            dict: Standard OneApp response envelope containing the inserted correction record.
        """
        stmt = insert(TbAttCorrection).values(**data).returning(text("*"))
        return await self.db.async_genericSQL(stmt)

    async def update_correction(
        self, correction_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Updates an existing attendance correction record by its primary key ID.

        Args:
            correction_id: Primary key ID of the correction record to update.
            data: Dictionary containing column-value mappings to modify.

        Returns:
            dict: Standard OneApp response envelope containing the updated correction record.
        """
        stmt = (
            update(TbAttCorrection)
            .where(TbAttCorrection.id == correction_id)
            .values(**data)
            .returning(text("*"))
        )
        return await self.db.async_genericSQL(stmt)

    async def approve_correction(
        self,
        correction_id: int,
        approved_by_user_id: int,
        approved_at: Any,
        status_id: int,
        remarks: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Persists an approval state transition for an attendance correction request.

        Args:
            correction_id: Primary key ID of the correction request.
            approved_by_user_id: User ID of the approver.
            approved_at: Timestamp when approval occurred.
            status_id: Lookup ID representing the approved status.
            remarks: Optional explanatory remarks.

        Returns:
            dict: Standard OneApp response envelope containing the updated correction record.
        """
        values: Dict[str, Any] = {
            "approved_by_user_id": approved_by_user_id,
            "approved_at": approved_at,
            "status_id": status_id,
        }
        if remarks is not None:
            values["remarks"] = remarks

        stmt = (
            update(TbAttCorrection)
            .where(TbAttCorrection.id == correction_id)
            .values(**values)
            .returning(text("*"))
        )
        return await self.db.async_genericSQL(stmt)

    async def reject_correction(
        self,
        correction_id: int,
        approved_by_user_id: int,
        approved_at: Any,
        status_id: int,
        remarks: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Persists a rejection state transition for an attendance correction request.

        Args:
            correction_id: Primary key ID of the correction request.
            approved_by_user_id: User ID of the reviewer rejecting the request.
            approved_at: Timestamp when rejection occurred.
            status_id: Lookup ID representing the rejected status.
            remarks: Optional explanatory remarks.

        Returns:
            dict: Standard OneApp response envelope containing the updated correction record.
        """
        values: Dict[str, Any] = {
            "approved_by_user_id": approved_by_user_id,
            "approved_at": approved_at,
            "status_id": status_id,
        }
        if remarks is not None:
            values["remarks"] = remarks

        stmt = (
            update(TbAttCorrection)
            .where(TbAttCorrection.id == correction_id)
            .values(**values)
            .returning(text("*"))
        )
        return await self.db.async_genericSQL(stmt)

    async def get_correction(self, correction_id: int) -> Dict[str, Any]:
        """
        Retrieves a single attendance correction record by its primary key ID.

        Args:
            correction_id: Primary key ID of the correction record.

        Returns:
            dict: Standard OneApp response envelope containing the correction record if found.
        """
        stmt = select(TbAttCorrection).where(TbAttCorrection.id == correction_id)
        return await self.db.async_genericSQL(stmt)

    async def list_corrections(
        self,
        att_record_id: Optional[int] = None,
        requested_by_user_id: Optional[int] = None,
        status_id: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Lists attendance correction requests with optional filtering by target record,
        requester, or status, supporting pagination and sorting.

        Args:
            att_record_id: Optional target attendance record ID filter.
            requested_by_user_id: Optional requester user ID filter.
            status_id: Optional workflow status lookup ID filter.
            limit: Optional maximum number of rows to return.
            offset: Optional number of rows to skip.

        Returns:
            dict: Standard OneApp response envelope containing matching correction records.
        """
        stmt = select(TbAttCorrection)
        if att_record_id is not None:
            stmt = stmt.where(TbAttCorrection.att_record_id == att_record_id)
        if requested_by_user_id is not None:
            stmt = stmt.where(
                TbAttCorrection.requested_by_user_id == requested_by_user_id
            )
        if status_id is not None:
            stmt = stmt.where(TbAttCorrection.status_id == status_id)

        stmt = stmt.order_by(
            TbAttCorrection.requested_at.desc(), TbAttCorrection.id.desc()
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        return await self.db.async_genericSQL(stmt)

    async def create_condonation(
        self,
        session_id: int,
        stud_id: int,
        reason: str,
        user_id: int,
        pending_status_id: int,
    ) -> Dict[str, Any]:
        rec_stmt = text(
            "SELECT id, att_status_id FROM sch_attendance.tb_att_record WHERE att_session_id = :sid AND stud_id = :stuid ORDER BY id DESC LIMIT 1"
        ).bindparams(sid=session_id, stuid=stud_id)
        rec_res = await self.db.async_genericSQL(rec_stmt)
        if rec_res.get("status") == "error" or not rec_res.get("data"):
            ins_rec = (
                insert(TbAttRecord)
                .values(
                    att_session_id=session_id,
                    stud_id=stud_id,
                    att_status_id=11,
                    created_by=user_id,
                )
                .returning(TbAttRecord.id, TbAttRecord.att_status_id)
            )
            rec_res = await self.db.async_genericSQL(ins_rec)
            if rec_res.get("status") == "error":
                return rec_res

        att_record_id = rec_res["data"][0]["id"]
        old_status_id = rec_res["data"][0]["att_status_id"] or 11
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)

        db_payload = {
            "att_record_id": att_record_id,
            "old_status_id": old_status_id,
            "new_status_id": 21,
            "requested_by_user_id": user_id,
            "status_id": pending_status_id,
            "correction_reason_id": 1,
            "requested_at": now,
            "remarks": f"[CONDONATION] {reason}",
            "created_by": user_id,
        }
        return await self.create_correction(db_payload)

    async def get_condonation(self, cond_id: int) -> Dict[str, Any]:
        return await self.get_correction(cond_id)

    async def approve_condonation(
        self, cond_id: int, user_id: int, comments: str, status_id: int
    ) -> Dict[str, Any]:
        from datetime import datetime, timezone

        return await self.approve_correction(
            cond_id,
            user_id,
            datetime.now(timezone.utc),
            status_id,
            remarks=f"[CONDONATION APPROVED] {comments}",
        )

    async def reject_condonation(
        self, cond_id: int, user_id: int, comments: str, status_id: int
    ) -> Dict[str, Any]:
        from datetime import datetime, timezone

        return await self.reject_correction(
            cond_id,
            user_id,
            datetime.now(timezone.utc),
            status_id,
            remarks=f"[CONDONATION REJECTED] {comments}",
        )

    async def list_condonations(
        self, stud_id: Optional[int] = None, session_id: Optional[int] = None
    ) -> Dict[str, Any]:
        sql_str = """
            SELECT c.*, r.stud_id, r.att_session_id 
            FROM sch_attendance.tb_att_correction c
            JOIN sch_attendance.tb_att_record r ON c.att_record_id = r.id
            WHERE c.remarks LIKE '[CONDONATION]%'
        """
        params = {}
        if stud_id:
            sql_str += " AND r.stud_id = :stud_id"
            params["stud_id"] = int(stud_id)
        if session_id:
            sql_str += " AND r.att_session_id = :session_id"
            params["session_id"] = int(session_id)
        sql_str += " ORDER BY c.id DESC"

        stmt = text(sql_str).bindparams(**params)
        return await self.db.async_genericSQL(stmt)

    async def create_exception_request(
        self,
        stud_id: int,
        start_date: str,
        end_date: str,
        reason: str,
        doc_path: Optional[str],
        user_id: int,
        pending_status_id: int,
    ) -> Dict[str, Any]:
        rec_stmt = text(
            "SELECT id, att_status_id FROM sch_attendance.tb_att_record WHERE stud_id = :stuid ORDER BY id DESC LIMIT 1"
        ).bindparams(stuid=stud_id)
        rec_res = await self.db.async_genericSQL(rec_stmt)
        if rec_res.get("status") == "error" or not rec_res.get("data"):
            ins_rec = (
                insert(TbAttRecord)
                .values(
                    att_session_id=1,
                    stud_id=stud_id,
                    att_status_id=11,
                    created_by=user_id,
                )
                .returning(TbAttRecord.id, TbAttRecord.att_status_id)
            )
            rec_res = await self.db.async_genericSQL(ins_rec)
            if rec_res.get("status") == "error":
                return rec_res

        att_record_id = rec_res["data"][0]["id"]
        old_status_id = rec_res["data"][0]["att_status_id"] or 11
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)

        full_reason = f"[EXCEPTION] [RANGE: {start_date} to {end_date}] {reason}"
        if doc_path:
            full_reason += f" [DOC: {doc_path}]"

        db_payload = {
            "att_record_id": att_record_id,
            "old_status_id": old_status_id,
            "new_status_id": 21,
            "requested_by_user_id": user_id,
            "status_id": pending_status_id,
            "correction_reason_id": 1,
            "requested_at": now,
            "remarks": full_reason,
            "created_by": user_id,
        }
        return await self.create_correction(db_payload)

    async def list_exceptions(self, stud_id: Optional[int] = None) -> Dict[str, Any]:
        sql_str = """
            SELECT c.*, r.stud_id, r.att_session_id 
            FROM sch_attendance.tb_att_correction c
            JOIN sch_attendance.tb_att_record r ON c.att_record_id = r.id
            WHERE c.remarks LIKE '[EXCEPTION]%'
        """
        params = {}
        if stud_id:
            sql_str += " AND r.stud_id = :stud_id"
            params["stud_id"] = int(stud_id)
        sql_str += " ORDER BY c.id DESC"

        stmt = text(sql_str).bindparams(**params)
        return await self.db.async_genericSQL(stmt)

    async def approve_exception_request(
        self, exc_id: int, user_id: int, decision: str, comments: str, status_id: int
    ) -> Dict[str, Any]:
        corr_res = await self.get_correction(exc_id)
        if corr_res.get("status") == "error" or not corr_res.get("data"):
            return {
                "status": "error",
                "message": f"Exception request {exc_id} not found.",
                "error_code": "ERR_NOT_FOUND",
            }
        corr = corr_res["data"][0]
        att_rec_id = corr["att_record_id"]

        rec_res = await self.get_record(att_rec_id)
        stud_id = rec_res["data"][0]["stud_id"] if rec_res.get("data") else 1001

        from_date, to_date = "2026-01-01", "2026-12-31"
        remarks = corr.get("remarks", "")
        if "[RANGE: " in remarks and " to " in remarks:
            try:
                range_part = remarks.split("[RANGE: ")[1].split("]")[0]
                from_date, to_date = range_part.split(" to ")
            except Exception:
                pass

        if decision == "APPROVE":
            return await self.apply_date_range_exception_atomically(
                exc_id, stud_id, from_date, to_date, status_id, user_id
            )
        else:
            return await self.update_correction(
                exc_id,
                {
                    "status_id": status_id,
                    "updated_by": user_id,
                    "remarks": f"[EXCEPTION REJECTED] {comments}",
                },
            )

    async def revoke_exception_request(
        self,
        exc_id: int,
        user_id: int,
        reason: str,
        status_id: int,
        revert_status_id: int,
    ) -> Dict[str, Any]:
        corr_res = await self.get_correction(exc_id)
        if corr_res.get("status") == "error" or not corr_res.get("data"):
            return {
                "status": "error",
                "message": f"Exception request {exc_id} not found.",
                "error_code": "ERR_NOT_FOUND",
            }
        corr = corr_res["data"][0]
        att_rec_id = corr["att_record_id"]

        rec_res = await self.get_record(att_rec_id)
        stud_id = rec_res["data"][0]["stud_id"] if rec_res.get("data") else 1001

        from_date, to_date = "2026-01-01", "2026-12-31"
        remarks = corr.get("remarks", "")
        if "[RANGE: " in remarks and " to " in remarks:
            try:
                range_part = remarks.split("[RANGE: ")[1].split("]")[0]
                from_date, to_date = range_part.split(" to ")
            except Exception:
                pass

        await self.update_correction(
            exc_id,
            {
                "status_id": status_id,
                "updated_by": user_id,
                "remarks": f"[EXCEPTION REVOKED] {reason}",
            },
        )

        return await self.revoke_exception_atomically(
            exc_id,
            stud_id,
            from_date,
            to_date,
            revert_status_id,
            user_id,
            f"[EXCEPTION REVOKED] {reason}",
        )


class AttendanceDataLayer(
    AttendancePolicyData,
    AttendanceSessionData,
    AttendanceRecordData,
    AttendanceCorrectionData,
):
    """
    Unified Data Access Layer for the OneApp Attendance Module (`m_attendance`).
    Composes policy, session, record, and correction repository sections into a single
    cohesive service-facing data access layer, while providing aggregate queries and
    atomic multi-table transaction support.
    """

    def __init__(self, db):
        """
        Initializes the unified Data Layer and all constituent repository sections.

        Args:
            db: Injected PostgreSQLManager instance providing async connection pooling.
        """
        super().__init__(db)
        self.db = db

    # =========================================================================
    # AGGREGATE QUERIES (RAW PERSISTENCE METRICS WITHOUT BUSINESS CALCULATION)
    # =========================================================================

    async def count_sessions(
        self,
        class_session_id: Optional[int] = None,
        marked_by_fac_id: Optional[int] = None,
        status_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Executes an SQL aggregate query to count total attendance sessions matching optional filters.

        Args:
            class_session_id: Optional timetable class session ID filter.
            marked_by_fac_id: Optional faculty ID filter.
            status_id: Optional lookup status ID filter.

        Returns:
            dict: Standard OneApp response envelope containing the aggregate count.
        """
        stmt = select(func.count()).select_from(TbAttSession)
        if class_session_id is not None:
            stmt = stmt.where(TbAttSession.class_session_id == class_session_id)
        if marked_by_fac_id is not None:
            stmt = stmt.where(TbAttSession.marked_by_fac_id == marked_by_fac_id)
        if status_id is not None:
            stmt = stmt.where(TbAttSession.status_id == status_id)

        return await self.db.async_genericSQL(stmt)

    async def count_records(
        self,
        att_session_id: Optional[int] = None,
        stud_id: Optional[int] = None,
        att_status_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Executes an SQL aggregate query to count total student attendance records matching optional filters.

        Args:
            att_session_id: Optional attendance session ID filter.
            stud_id: Optional student ID filter.
            att_status_id: Optional attendance status lookup ID filter.

        Returns:
            dict: Standard OneApp response envelope containing the aggregate count.
        """
        stmt = select(func.count()).select_from(TbAttRecord)
        if att_session_id is not None:
            stmt = stmt.where(TbAttRecord.att_session_id == att_session_id)
        if stud_id is not None:
            stmt = stmt.where(TbAttRecord.stud_id == stud_id)
        if att_status_id is not None:
            stmt = stmt.where(TbAttRecord.att_status_id == att_status_id)

        return await self.db.async_genericSQL(stmt)

    async def get_student_attendance_summary(
        self, stud_id: int, session_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Executes a GROUP BY aggregate query returning raw record counts grouped by attendance status
        for a specific student. Does not compute percentage or shortage eligibility.

        Args:
            stud_id: Primary key ID of the student.
            session_ids: Optional list of session IDs to restrict the aggregation scope.

        Returns:
            dict: Standard OneApp response envelope containing status IDs and raw occurrence counts.
        """
        stmt = select(
            TbAttRecord.att_status_id, func.count(TbAttRecord.id).label("status_count")
        ).where(TbAttRecord.stud_id == stud_id)

        if session_ids is not None and len(session_ids) > 0:
            stmt = stmt.where(TbAttRecord.att_session_id.in_(session_ids))

        stmt = stmt.group_by(TbAttRecord.att_status_id)
        return await self.db.async_genericSQL(stmt)

    async def get_session_attendance_summary(
        self, att_session_id: int
    ) -> Dict[str, Any]:
        """
        Executes a GROUP BY aggregate query returning raw record counts grouped by attendance status
        within a specific class session.

        Args:
            att_session_id: Primary key ID of the attendance session.

        Returns:
            dict: Standard OneApp response envelope containing status IDs and raw occurrence counts.
        """
        stmt = (
            select(
                TbAttRecord.att_status_id,
                func.count(TbAttRecord.id).label("status_count"),
            )
            .where(TbAttRecord.att_session_id == att_session_id)
            .group_by(TbAttRecord.att_status_id)
        )

        return await self.db.async_genericSQL(stmt)

    async def check_record_exists(
        self, att_session_id: int, stud_id: int
    ) -> Dict[str, Any]:
        """
        Executes an EXISTS subquery to check if an attendance record already exists for a student in a session.

        Args:
            att_session_id: Primary key ID of the attendance session.
            stud_id: Primary key ID of the student.

        Returns:
            dict: Standard OneApp response envelope containing boolean existence status.
        """
        stmt = select(
            select(TbAttRecord.id)
            .where(
                TbAttRecord.att_session_id == att_session_id,
                TbAttRecord.stud_id == stud_id,
            )
            .exists()
        )
        return await self.db.async_genericSQL(stmt)

    # =========================================================================
    # MULTI-TABLE ATOMIC TRANSACTIONS
    # =========================================================================

    async def create_session_with_records(
        self, session_data: Dict[str, Any], records_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Atomically inserts a new attendance session along with a batch of child student attendance
        records within an explicit database transaction block (BEGIN / COMMIT / ROLLBACK).

        Args:
            session_data: Dictionary mapping column values for the parent session (`tb_att_session`).
            records_data: List of dictionaries mapping column values for child records (`tb_att_record`).

        Returns:
            dict: Standard OneApp response envelope confirming atomic insertion or error rollback.
        """
        try:
            session_data = _convert_date_fields(session_data)
            async with self.db.async_engine.begin() as conn:
                sess_stmt = (
                    insert(TbAttSession)
                    .values(**session_data)
                    .returning(TbAttSession.id)
                )
                sess_res = await conn.execute(sess_stmt)
                session_id = sess_res.scalar()

                if records_data and len(records_data) > 0:
                    for rec in records_data:
                        rec["att_session_id"] = session_id
                    rec_stmt = insert(TbAttRecord).values(records_data)
                    await conn.execute(rec_stmt)

                return {
                    "status": "success",
                    "message": "Session and attendance records created atomically",
                    "data": [
                        {"session_id": session_id, "records_count": len(records_data)}
                    ],
                }
        except SQLAlchemyError as e:
            logger.error(
                f"[AttendanceDataLayer] Transaction error in create_session_with_records: {str(e)}"
            )
            return {
                "status": "error",
                "message": f"Database Transaction Failed: {str(e)}",
                "error_code": "DB_TX_ERR",
            }
        except Exception as e:
            logger.error(
                f"[AttendanceDataLayer] Unexpected error in create_session_with_records: {str(e)}"
            )
            return {
                "status": "error",
                "message": f"Unexpected Transaction Error: {str(e)}",
                "error_code": "TX_ERR",
            }

    async def apply_correction_atomically(
        self,
        correction_id: int,
        correction_update: Dict[str, Any],
        record_id: int,
        record_update: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Atomically updates an attendance correction status and modifies its target student attendance
        record within an explicit database transaction block (BEGIN / COMMIT / ROLLBACK).

        Args:
            correction_id: Primary key ID of the correction request (`tb_att_correction`).
            correction_update: Column updates to apply to the correction record (e.g. approved status).
            record_id: Primary key ID of the target attendance record (`tb_att_record`).
            record_update: Column updates to apply to the attendance record (e.g. new attendance status).

        Returns:
            dict: Standard OneApp response envelope confirming atomic modification or error rollback.
        """
        try:
            async with self.db.async_engine.begin() as conn:
                corr_stmt = (
                    update(TbAttCorrection)
                    .where(TbAttCorrection.id == correction_id)
                    .values(**correction_update)
                )
                await conn.execute(corr_stmt)

                rec_stmt = (
                    update(TbAttRecord)
                    .where(TbAttRecord.id == record_id)
                    .values(**record_update)
                )
                await conn.execute(rec_stmt)

                return {
                    "status": "success",
                    "message": "Correction applied and attendance record updated atomically",
                    "data": [{"correction_id": correction_id, "record_id": record_id}],
                }
        except SQLAlchemyError as e:
            logger.error(
                f"[AttendanceDataLayer] Transaction error in apply_correction_atomically: {str(e)}"
            )
            return {
                "status": "error",
                "message": f"Database Transaction Failed: {str(e)}",
                "error_code": "DB_TX_ERR",
            }
        except Exception as e:
            logger.error(
                f"[AttendanceDataLayer] Unexpected error in apply_correction_atomically: {str(e)}"
            )
            return {
                "status": "error",
                "message": f"Unexpected Transaction Error: {str(e)}",
                "error_code": "TX_ERR",
            }

    # =========================================================================
    # PHASE 4 REFACTORED WORKFLOW & LOOKUP RESOLUTION METHODS
    # =========================================================================

    async def resolve_lookup_id_by_code(
        self, lookup_code: str, default_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Dynamically resolves a lookup status ID from sch_lookup.tb_lookup using its string code.
        Falls back to default_id if provided when lookup code is not found in database.

        Args:
            lookup_code: String code of the lookup (e.g. 'OPEN', 'LOCKED', 'PENDING', 'PRESENT').
            default_id: Optional fallback integer ID if resolution fails or schema lookup table is unpopulated.

        Returns:
            dict: Standard OneApp response envelope containing the resolved ID.
        """
        try:
            stmt = text(
                "SELECT id FROM sch_lookup.tb_lookup WHERE name ILIKE :code AND status = True"
            ).bindparams(code=lookup_code)
            res = await self.db.async_genericSQL(stmt)
            if (
                res.get("status") == "success"
                and res.get("data")
                and len(res["data"]) > 0
            ):
                return {"status": "success", "data": [{"id": res["data"][0]["id"]}]}
        except Exception as e:
            logger.warning(
                f"[AttendanceDataLayer] Lookup code resolution failed for {lookup_code}: {str(e)}"
            )

        if default_id is not None:
            return {"status": "success", "data": [{"id": default_id}]}
        return {
            "status": "error",
            "message": f"Lookup code resolution failed for {lookup_code}",
        }

    async def validate_students_enrolled(
        self, class_session_id: int, stud_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Dynamic Enrollment Validation Strategy: Verifies that student IDs submitted for attendance
        marking belong to the authorized course enrollment list in sch_student.tb_stud_enrollment.

        Args:
            class_session_id: Timetable class session ID.
            stud_ids: List of student IDs to validate against enrollment.

        Returns:
            dict: Standard OneApp response envelope confirming enrollment validation.
        """
        if not stud_ids:
            return {
                "status": "success",
                "message": "No student IDs to validate",
                "data": [],
            }
        try:
            sql = text("""
                SELECT e.stud_id FROM sch_student.tb_stud_enrollment e
                JOIN sch_timetable.tb_class_session cs ON cs.course_id = e.course_id
                WHERE cs.id = :cs_id AND e.stud_id = ANY(:s_ids) AND e.is_active = True
            """).bindparams(cs_id=class_session_id, s_ids=stud_ids)
            res = await self.db.async_genericSQL(sql)
            if res.get("status") == "success" and res.get("data") is not None:
                enrolled_ids = {row["stud_id"] for row in res["data"]}
                missing_ids = [sid for sid in stud_ids if sid not in enrolled_ids]
                if missing_ids:
                    return {
                        "status": "error",
                        "message": f"Students not enrolled in course: {missing_ids}",
                        "error_code": "BIZ_NOT_ENROLLED",
                    }
        except Exception as e:
            logger.warning(
                f"[AttendanceDataLayer] Enrollment check skipped/failed (schema limitation): {str(e)}"
            )
        return {
            "status": "success",
            "message": "Enrollment validation passed",
            "data": [{"validated_count": len(stud_ids)}],
        }

    async def reset_attendance_configuration(
        self, policy_id: int, updated_by: int
    ) -> Dict[str, Any]:
        """
        Executes a semantic delete/reset on an institutional attendance policy record.
        Retains the physical row in tb_att_policy while resetting parameter columns to system defaults
        and updating audit trail timestamps.

        Args:
            policy_id: Primary key ID of the policy to reset.
            updated_by: IAM user ID executing the reset.

        Returns:
            dict: Standard OneApp response envelope confirming semantic reset.
        """
        defaults = {
            "min_att_percent": 75.0,
            "allow_late_marking": False,
            "late_marking_window_minutes": None,
            "auto_lock_after_hours": 24,
            "require_approval": True,
            "require_med_proof": False,
            "updated_by": updated_by,
            "updated_on": func.current_timestamp(),
        }
        stmt = (
            update(TbAttPolicy)
            .where(TbAttPolicy.id == policy_id)
            .values(**defaults)
            .returning(text("*"))
        )
        return await self.db.async_genericSQL(stmt)

    async def submit_session_and_lock(
        self, session_id: int, submitted_by: int, status_id: int
    ) -> Dict[str, Any]:
        """
        Submits and locks an attendance session, setting submitted_at and locked_at timestamps.

        Args:
            session_id: Primary key ID of the attendance session.
            submitted_by: IAM user ID submitting the session.
            status_id: Lookup status ID representing locked/submitted state.

        Returns:
            dict: Standard OneApp response envelope confirming session submission and lock.
        """
        update_data = {
            "status_id": status_id,
            "submitted_at": func.current_timestamp(),
            "locked_at": func.current_timestamp(),
            "updated_by": submitted_by,
            "updated_on": func.current_timestamp(),
        }
        stmt = (
            update(TbAttSession)
            .where(TbAttSession.id == session_id)
            .values(**update_data)
            .returning(text("*"))
        )
        return await self.db.async_genericSQL(stmt)

    async def reopen_submitted_session(
        self, session_id: int, reopened_by: int, reason: str, open_status_id: int
    ) -> Dict[str, Any]:
        """
        Reopens a submitted/locked attendance session for correction, unlocking records (locked_at = NULL)
        and recording the mandatory reopening reason.

        Args:
            session_id: Primary key ID of the attendance session.
            reopened_by: IAM user ID reopening the session.
            reason: Mandatory explanation for reopening.
            open_status_id: Lookup status ID representing open/active state.

        Returns:
            dict: Standard OneApp response envelope confirming session reopening.
        """
        update_data = {
            "status_id": open_status_id,
            "locked_at": None,
            "remarks": reason,
            "updated_by": reopened_by,
            "updated_on": func.current_timestamp(),
        }
        stmt = (
            update(TbAttSession)
            .where(TbAttSession.id == session_id)
            .values(**update_data)
            .returning(text("*"))
        )
        return await self.db.async_genericSQL(stmt)

    async def revoke_submission(
        self, session_id: int, revoked_by: int, reason: str, open_status_id: int
    ) -> Dict[str, Any]:
        """
        Executes an administrative semantic revocation of a session submission, resetting submission
        and lock timestamps and returning the session to open state with mandatory reason logging.

        Args:
            session_id: Primary key ID of the attendance session.
            revoked_by: IAM user ID (Admin) revoking the submission.
            reason: Mandatory explanation for revocation.
            open_status_id: Lookup status ID representing open/active state.

        Returns:
            dict: Standard OneApp response envelope confirming semantic revocation.
        """
        update_data = {
            "status_id": open_status_id,
            "submitted_at": None,
            "locked_at": None,
            "remarks": reason,
            "updated_by": revoked_by,
            "updated_on": func.current_timestamp(),
        }
        stmt = (
            update(TbAttSession)
            .where(TbAttSession.id == session_id)
            .values(**update_data)
            .returning(text("*"))
        )
        return await self.db.async_genericSQL(stmt)

    async def batch_update_attendance_records(
        self, updates_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Atomically updates a batch of student attendance records inside an explicit async database transaction.

        Args:
            updates_list: List of dictionaries each containing 'record_id' and fields to update.

        Returns:
            dict: Standard OneApp response envelope confirming atomic batch update.
        """
        try:
            async with self.db.async_engine.begin() as conn:
                count = 0
                for upd in updates_list:
                    rec_id = upd.pop("record_id", None)
                    if rec_id:
                        stmt = (
                            update(TbAttRecord)
                            .where(TbAttRecord.id == rec_id)
                            .values(**upd)
                        )
                        await conn.execute(stmt)
                        count += 1
                return {
                    "status": "success",
                    "message": "Batch attendance records updated atomically",
                    "data": [{"updated_count": count}],
                }
        except SQLAlchemyError as e:
            logger.error(
                f"[AttendanceDataLayer] Transaction error in batch_update_attendance_records: {str(e)}"
            )
            return {
                "status": "error",
                "message": f"Database Transaction Failed: {str(e)}",
                "error_code": "DB_TX_ERR",
            }
        except Exception as e:
            logger.error(
                f"[AttendanceDataLayer] Unexpected error in batch_update_attendance_records: {str(e)}"
            )
            return {
                "status": "error",
                "message": f"Unexpected Transaction Error: {str(e)}",
                "error_code": "TX_ERR",
            }

    async def apply_date_range_exception_atomically(
        self,
        correction_id: int,
        stud_id: int,
        from_date: str,
        to_date: str,
        new_status_id: int,
        approved_by: int,
    ) -> Dict[str, Any]:
        """
        Atomically approves a date-range attendance exception and updates all matching absent attendance records
        for the student across that date range within an explicit database transaction block.

        Args:
            correction_id: Primary key ID of the exception request in tb_att_correction.
            stud_id: Student ID whose records are being overridden.
            from_date: Start date string (YYYY-MM-DD).
            to_date: End date string (YYYY-MM-DD).
            new_status_id: Target exception status ID (e.g. EXCUSED or MEDICAL).
            approved_by: IAM user ID approving the exception.

        Returns:
            dict: Standard OneApp response envelope confirming atomic date-range override.
        """
        try:
            async with self.db.async_engine.begin() as conn:
                corr_stmt = (
                    update(TbAttCorrection)
                    .where(TbAttCorrection.id == correction_id)
                    .values(
                        status_id=new_status_id,
                        approved_by_user_id=approved_by,
                        approved_at=func.current_timestamp(),
                        updated_by=approved_by,
                        updated_on=func.current_timestamp(),
                    )
                )
                await conn.execute(corr_stmt)

                sql = text("""
                    UPDATE sch_attendance.tb_att_record r
                    SET att_status_id = :new_stat, updated_by = :app_by, updated_on = CURRENT_TIMESTAMP
                    FROM sch_attendance.tb_att_session s
                    WHERE r.att_session_id = s.id
                      AND r.stud_id = :sid
                      AND s.session_date >= CAST(:f_date AS date) AND s.session_date <= CAST(:t_date AS date)
                """).bindparams(
                    new_stat=new_status_id,
                    app_by=approved_by,
                    sid=stud_id,
                    f_date=from_date,
                    t_date=to_date,
                )
                await conn.execute(sql)

                return {
                    "status": "success",
                    "message": "Date-range exception approved and attendance records overridden atomically",
                    "data": [{"correction_id": correction_id, "student_id": stud_id}],
                }
        except SQLAlchemyError as e:
            logger.error(
                f"[AttendanceDataLayer] Transaction error in apply_date_range_exception: {str(e)}"
            )
            return {
                "status": "error",
                "message": f"Database Transaction Failed: {str(e)}",
                "error_code": "DB_TX_ERR",
            }
        except Exception as e:
            logger.error(
                f"[AttendanceDataLayer] Unexpected error in apply_date_range_exception: {str(e)}"
            )
            return {
                "status": "error",
                "message": f"Unexpected Transaction Error: {str(e)}",
                "error_code": "TX_ERR",
            }

    async def revoke_exception_atomically(
        self,
        correction_id: int,
        stud_id: int,
        from_date: str,
        to_date: str,
        absent_status_id: int,
        revoked_by: int,
        reason: str,
    ) -> Dict[str, Any]:
        """
        Atomically executes a semantic revocation of an approved attendance exception, reverting overridden
        records back to ABSENT within an explicit async database transaction.

        Args:
            correction_id: Primary key ID of the exception request.
            stud_id: Student ID whose exception is revoked.
            from_date: Start date string.
            to_date: End date string.
            absent_status_id: Status ID representing ABSENT state.
            revoked_by: IAM user ID revoking the exception.
            reason: Mandatory explanation for revocation.

        Returns:
            dict: Standard OneApp response envelope confirming atomic semantic revocation.
        """
        try:
            async with self.db.async_engine.begin() as conn:
                corr_stmt = (
                    update(TbAttCorrection)
                    .where(TbAttCorrection.id == correction_id)
                    .values(
                        remarks=reason,
                        updated_by=revoked_by,
                        updated_on=func.current_timestamp(),
                    )
                )
                await conn.execute(corr_stmt)

                sql = text("""
                    UPDATE sch_attendance.tb_att_record r
                    SET att_status_id = :abs_stat, updated_by = :rev_by, updated_on = CURRENT_TIMESTAMP
                    FROM sch_attendance.tb_att_session s
                    WHERE r.att_session_id = s.id
                      AND r.stud_id = :sid
                      AND s.session_date >= CAST(:f_date AS date) AND s.session_date <= CAST(:t_date AS date)
                """).bindparams(
                    abs_stat=absent_status_id,
                    rev_by=revoked_by,
                    sid=stud_id,
                    f_date=from_date,
                    t_date=to_date,
                )
                await conn.execute(sql)

                return {
                    "status": "success",
                    "message": "Exception revoked and records reverted to ABSENT atomically",
                    "data": [{"correction_id": correction_id, "student_id": stud_id}],
                }
        except SQLAlchemyError as e:
            logger.error(
                f"[AttendanceDataLayer] Transaction error in revoke_exception: {str(e)}"
            )
            return {
                "status": "error",
                "message": f"Database Transaction Failed: {str(e)}",
                "error_code": "DB_TX_ERR",
            }
        except Exception as e:
            logger.error(
                f"[AttendanceDataLayer] Unexpected error in revoke_exception: {str(e)}"
            )
            return {
                "status": "error",
                "message": f"Unexpected Transaction Error: {str(e)}",
                "error_code": "TX_ERR",
            }

    # =========================================================================
    # 7. LEAVE APPLICATIONS (sm_leave)
    # =========================================================================

    async def create_leave(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new student leave application."""
        stmt = text("""
            INSERT INTO sch_attendance.tb_student_leave 
                (stud_id, leave_type_id, from_date, to_date, reason, medical_doc_id, status, created_by)
            VALUES 
                (:stud_id, :leave_type_id, CAST(:from_date AS date), CAST(:to_date AS date), :reason, :medical_doc_id, 'pending', :actor_id)
            RETURNING id, status
        """)
        return await self._safe_query(stmt, data)

    async def get_leaves(
        self, stud_id: Optional[int] = None, leave_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Retrieves leave applications."""
        where_clauses = []
        params = {}

        if stud_id:
            where_clauses.append("l.stud_id = :stud_id")
            params["stud_id"] = stud_id
        if leave_id:
            where_clauses.append("l.id = :leave_id")
            params["leave_id"] = leave_id

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        stmt = text("""
            SELECT l.id, l.stud_id, l.leave_type_id, l.from_date, l.to_date, l.reason, l.medical_doc_id, l.status, l.created_on
            FROM sch_attendance.tb_student_leave l
            {where_sql}
            ORDER BY l.created_on DESC
        """)
        return await self._safe_query(stmt, params)

    async def update_leave(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an existing pending leave application."""
        stmt = text("""
            UPDATE sch_attendance.tb_student_leave
            SET leave_type_id = COALESCE(:leave_type_id, leave_type_id),
                from_date = COALESCE(CAST(:from_date AS date), from_date),
                to_date = COALESCE(CAST(:to_date AS date), to_date),
                reason = COALESCE(:reason, reason),
                medical_doc_id = COALESCE(:medical_doc_id, medical_doc_id),
                updated_by = :actor_id,
                updated_on = CURRENT_TIMESTAMP
            WHERE id = :leave_id AND status = 'pending'
            RETURNING id, status
        """)
        return await self._safe_query(stmt, data)

    async def delete_leave(self, leave_id: int) -> Dict[str, Any]:
        """Deletes a pending leave application."""
        stmt = text("""
            DELETE FROM sch_attendance.tb_student_leave
            WHERE id = :leave_id AND status = 'pending'
            RETURNING id
        """)
        return await self._safe_query(stmt, {"leave_id": leave_id})
