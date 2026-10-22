"""
File: m_curriculum_data.py
Description: Data Access Layer for m_curriculum.

Author: Siddharth Amdal
App: OneApp

"""

import logging
from sqlalchemy import select, update, insert
from .db_init import (
    TbProg,
    TbCrs,
    TbCrsVersion,
    TbCrsPrerequisite,
    TbCrsCorequisite,
    TbCurr,
    TbCurrVersion,
    TbCurrTerm,
    TbCurrTermCrs,
    TbStudEnrollment,
    TbStudCrsRegistration,
)

logger = logging.getLogger(__name__)


class CurriculumDataLayer:
    """
    Lightweight module-local Data Access layer that consumes the injected context.postgres.
    This keeps business logic readable while maintaining module isolation.
    """

    def __init__(self, db):
        self.db = db

    # ------------------------------------------------------------
    # PROGRAMME ENTITY
    # ------------------------------------------------------------
    async def create_programme(self, data: dict):
        return await self.db.async_insert(TbProg.__tablename__, data)

    async def get_programme(self, prog_id: int):
        stmt = select(TbProg).where(TbProg.id == prog_id)
        return await self.db.async_genericSQL(stmt)

    async def update_programme(self, prog_id: int, data: dict):
        stmt = update(TbProg).where(TbProg.id == prog_id).values(**data)
        return await self.db.async_genericSQL(stmt)

    async def search_programmes(
        self, institution_id: int = None, department_id: int = None
    ):
        stmt = select(TbProg)
        if institution_id:
            stmt = stmt.where(TbProg.institution_id == institution_id)
        if department_id:
            stmt = stmt.where(TbProg.department_id == department_id)
        return await self.db.async_genericSQL(stmt)

    async def check_programme_exists(
        self, institution_id: int, prog_code: str, prog_name: str
    ):
        stmt = select(TbProg).where(
            (TbProg.institution_id == institution_id)
            & ((TbProg.prog_code == prog_code) | (TbProg.prog_name == prog_name))
        )
        res = await self.db.async_genericSQL(stmt)
        return len(res.get("data", [])) > 0 if res.get("status") == "success" else False

    # ------------------------------------------------------------
    # COURSE ENTITY
    # ------------------------------------------------------------
    async def create_course_root(self, data: dict):
        return await self.db.async_insert(TbCrs.__tablename__, data)

    async def create_course_version(self, data: dict):
        return await self.db.async_insert(TbCrsVersion.__tablename__, data)

    async def create_course_with_version(self, root_data: dict, version_data: dict):
        """
        Creates a course root and its initial version atomically.
        Wrapped in BEGIN, COMMIT, ROLLBACK blocks as per the framework standard for multi-table transactions.
        """
        try:
            async with self.db.async_engine.begin() as conn:
                root_stmt = insert(TbCrs).values(**root_data).returning(TbCrs.id)
                root_res = await conn.execute(root_stmt)
                crs_id = root_res.scalar()

                version_data["crs_id"] = crs_id
                ver_stmt = (
                    insert(TbCrsVersion)
                    .values(**version_data)
                    .returning(TbCrsVersion.id)
                )
                ver_res = await conn.execute(ver_stmt)
                version_id = ver_res.scalar()

                return {
                    "status": "success",
                    "message": "Transaction committed successfully",
                    "data": [{"crs_id": crs_id, "version_id": version_id}],
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Database Operation Failed: {str(e)}",
                "error_code": "DB_ERR",
            }

    async def get_course(self, crs_id: int):
        stmt = select(TbCrs).where(TbCrs.id == crs_id)
        return await self.db.async_genericSQL(stmt)

    async def search_courses(self, crs_code: str = None):
        stmt = select(TbCrs)
        if crs_code:
            stmt = stmt.where(TbCrs.crs_code == crs_code)
        return await self.db.async_genericSQL(stmt)

    async def get_active_course_version(self, crs_id: int):
        stmt = select(TbCrsVersion).where(
            (TbCrsVersion.crs_id == crs_id) & (TbCrsVersion.is_current.is_(True))
        )
        return await self.db.async_genericSQL(stmt)

    async def set_course_version_status(self, version_id: int, is_current: bool):
        stmt = (
            update(TbCrsVersion)
            .where(TbCrsVersion.id == version_id)
            .values(is_current=is_current)
        )
        return await self.db.async_genericSQL(stmt)

    async def check_prerequisite_exists(
        self, crs_version_id: int, req_crs_version_id: int
    ):
        stmt = select(TbCrsPrerequisite).where(
            (TbCrsPrerequisite.crs_version_id == crs_version_id)
            & (TbCrsPrerequisite.prerequisite_crs_version_id == req_crs_version_id)
        )
        res = await self.db.async_genericSQL(stmt)
        return len(res.get("data", [])) > 0 if res.get("status") == "success" else False

    async def check_corequisite_exists(
        self, crs_version_id: int, req_crs_version_id: int
    ):
        stmt = select(TbCrsCorequisite).where(
            (TbCrsCorequisite.crs_version_id == crs_version_id)
            & (TbCrsCorequisite.corequisite_crs_version_id == req_crs_version_id)
        )
        res = await self.db.async_genericSQL(stmt)
        return len(res.get("data", [])) > 0 if res.get("status") == "success" else False

    async def create_prerequisite(self, data: dict):
        return await self.db.async_insert(TbCrsPrerequisite.__tablename__, data)

    async def create_corequisite(self, data: dict):
        return await self.db.async_insert(TbCrsCorequisite.__tablename__, data)

    # ------------------------------------------------------------
    # CURRICULUM ENTITY
    # ------------------------------------------------------------
    async def create_curriculum_root(self, data: dict):
        return await self.db.async_insert(TbCurr.__tablename__, data)

    async def create_curriculum_version(self, data: dict):
        return await self.db.async_insert(TbCurrVersion.__tablename__, data)

    async def get_curriculum(self, curr_id: int):
        stmt = select(TbCurr).where(TbCurr.id == curr_id)
        return await self.db.async_genericSQL(stmt)

    async def search_curricula(self, prog_id: int = None):
        stmt = select(TbCurr)
        if prog_id is not None:
            stmt = stmt.where(TbCurr.prog_id == prog_id)
        return await self.db.async_genericSQL(stmt)

    async def check_curriculum_exists(self, prog_id: int, curr_name: str):
        stmt = select(TbCurr).where(
            (TbCurr.prog_id == prog_id) & (TbCurr.curr_name == curr_name)
        )
        res = await self.db.async_genericSQL(stmt)
        return len(res.get("data", [])) > 0 if res.get("status") == "success" else False

    async def get_active_curriculum_version(self, curr_id: int):
        stmt = select(TbCurrVersion).where(
            (TbCurrVersion.curr_id == curr_id) & (TbCurrVersion.is_current.is_(True))
        )
        return await self.db.async_genericSQL(stmt)

    async def get_curriculum_version(self, version_id: int):
        stmt = select(TbCurrVersion).where(TbCurrVersion.id == version_id)
        return await self.db.async_genericSQL(stmt)

    async def get_curriculum_approvals(self, status_filter: int = None):
        stmt = select(TbCurrVersion)
        if status_filter is not None:
            stmt = stmt.where(TbCurrVersion.status_id == status_filter)
        return await self.db.async_genericSQL(stmt)

    async def create_curriculum_term(self, data: dict):
        return await self.db.async_insert(TbCurrTerm.__tablename__, data)

    async def link_course_to_term(self, data: dict):
        return await self.db.async_insert(TbCurrTermCrs.__tablename__, data)

    async def create_curriculum_full(
        self, root_data: dict, version_data: dict, terms_data: list
    ):
        """
        Creates a curriculum root, version, terms, and term courses atomically.
        Wrapped in BEGIN, COMMIT, ROLLBACK blocks as per the framework standard for multi-table transactions.
        """
        try:
            async with self.db.async_engine.begin() as conn:
                root_stmt = insert(TbCurr).values(**root_data).returning(TbCurr.id)
                root_res = await conn.execute(root_stmt)
                curr_id = root_res.scalar()

                version_data["curr_id"] = curr_id
                ver_stmt = (
                    insert(TbCurrVersion)
                    .values(**version_data)
                    .returning(TbCurrVersion.id)
                )
                ver_res = await conn.execute(ver_stmt)
                version_id = ver_res.scalar()

                for term in terms_data:
                    term_row = {
                        "curr_version_id": version_id,
                        "term_number": term.get("termNumber"),
                        "total_credits": term.get("totalCredits", 0),
                        "status_id": term.get(
                            "statusId", version_data.get("status_id")
                        ),
                    }
                    term_stmt = (
                        insert(TbCurrTerm).values(**term_row).returning(TbCurrTerm.id)
                    )
                    term_res = await conn.execute(term_stmt)
                    term_id = term_res.scalar()

                    courses = term.get("courses", [])
                    for crs in courses:
                        crs_row = {
                            "curr_term_id": term_id,
                            "crs_version_id": crs.get("crsVersionId"),
                            "is_mandatory": crs.get("isMandatory", True),
                            "status_id": crs.get("statusId", term_row["status_id"]),
                        }
                        crs_stmt = insert(TbCurrTermCrs).values(**crs_row)
                        await conn.execute(crs_stmt)

                return {
                    "status": "success",
                    "message": "Transaction committed successfully",
                    "data": [{"curr_id": curr_id, "version_id": version_id}],
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Database Operation Failed: {str(e)}",
                "error_code": "DB_ERR",
            }

    # ------------------------------------------------------------
    # ENROLLMENT ENTITY
    # ------------------------------------------------------------
    async def create_student_enrollment(self, data: dict):
        return await self.db.async_insert(TbStudEnrollment.__tablename__, data)

    async def get_student_enrollment(
        self, stud_id: int = None, enrollment_id: int = None, prog_intake_id: int = None
    ):
        stmt = select(TbStudEnrollment)
        if enrollment_id is not None:
            stmt = stmt.where(TbStudEnrollment.id == enrollment_id)
        if stud_id is not None:
            stmt = stmt.where(TbStudEnrollment.stud_id == stud_id)
        if prog_intake_id is not None:
            stmt = stmt.where(TbStudEnrollment.prog_intake_id == prog_intake_id)
        return await self.db.async_genericSQL(stmt)

    async def update_student_enrollment(self, enrollment_id: int, data: dict):
        stmt = (
            update(TbStudEnrollment)
            .where(TbStudEnrollment.id == enrollment_id)
            .values(**data)
        )
        return await self.db.async_genericSQL(stmt)

    async def create_semester_registration(self, data: dict):
        return await self.db.async_insert(TbStudCrsRegistration.__tablename__, data)

    async def create_semester_registrations_batch(self, registrations_data: list):
        try:
            async with self.db.async_engine.begin() as conn:
                for reg_data in registrations_data:
                    await conn.execute(insert(TbStudCrsRegistration).values(**reg_data))
            return {
                "status": "success",
                "message": "Batch registrations created successfully",
            }
        except Exception as e:
            logger.error(
                f"Transaction failed in create_semester_registrations_batch: {str(e)}",
                exc_info=True,
            )
            return {
                "status": "error",
                "message": "Database transaction failed during batch registration",
                "error_code": "DB_TRANSACTION_ERROR",
            }

    async def get_student_registrations(
        self,
        stud_id: int = None,
        crs_offering_id: int = None,
        registration_id: int = None,
    ):
        stmt = select(TbStudCrsRegistration)
        if registration_id is not None:
            stmt = stmt.where(TbStudCrsRegistration.id == registration_id)
        if stud_id is not None:
            stmt = stmt.where(TbStudCrsRegistration.stud_id == stud_id)
        if crs_offering_id is not None:
            stmt = stmt.where(TbStudCrsRegistration.crs_offering_id == crs_offering_id)
        return await self.db.async_genericSQL(stmt)

    async def update_student_registration(self, registration_id: int, data: dict):
        stmt = (
            update(TbStudCrsRegistration)
            .where(TbStudCrsRegistration.id == registration_id)
            .values(**data)
        )
        return await self.db.async_genericSQL(stmt)


# TODO: Reference Gap Analysis for tb_crs_outcome. Implementation pending schema upgrades.
