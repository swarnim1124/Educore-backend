"""
File: seed_m_exam.py
Description: Database data seeder for the Examinations module (sch_examinations / sch_examination).
             Contains populating operations matching production columns and tables.
"""

import sys
import os
import asyncio
from datetime import datetime, date, time
from sqlalchemy import text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from xsc_lib.xsc_lib_common.xsc_libc_pgrs import PostgreSQLManager


async def seed_exam_data():
    print("Starting Exam Module Database Seeding...")
    db = PostgreSQLManager()
    conn_resp = await db.async_connectDB()
    if conn_resp["status"] == "error":
        print(f"Failed to connect: {conn_resp['message']} | DB Err: {db.errMsg}")
        return

    try:
        # Helper function for executing seeder queries resiliently
        async def exec_query(stmt, params=None, desc="Query"):
            res = await db.async_genericSQL(stmt, params)
            if res["status"] == "error":
                err_msg = str(db.errMsg).lower()
                if (
                    "permission denied" in err_msg
                    or "insufficientprivilege" in err_msg
                    or "does not exist" in err_msg
                ):
                    print(f"[WARNING] Skipping {desc}: DB error: {db.errMsg}")
                    return {
                        "status": "skipped",
                        "message": "Permission denied or table missing",
                    }
                print(
                    f"[ERROR] Failed in {desc}: {res['message']} | DB Err: {db.errMsg}"
                )
                raise Exception(f"{desc} failed: {db.errMsg}")
            return res

        # Fallback maps for lookup categories and lookups
        KNOWN_CATEGORIES = {
            "EXAM_SESSION_TYPE": 71,
            "STATUS": 2,
            "REGISTRATION_MODE": 72,
            "REGISTRATION_STATUS": 73,
            "ATTENDANCE_STATUS": 70,
            "MODERATION_REASON": 74,
            "MALPRACTICE_TYPE": 75,
            "ACTION_TAKEN": 76,
        }

        KNOWN_LOOKUPS = {
            ("EXAM_SESSION_TYPE", "END_SEMESTER"): 713,
            ("EXAM_SESSION_TYPE", "MID_SEMESTER"): 714,
            ("STATUS", "DRAFT"): 7,
            ("STATUS", "ACTIVE"): 4,
            ("STATUS", "COMPLETED"): 715,
            ("STATUS", "PUBLISHED"): 716,
            ("STATUS", "APPROVED"): 8,
            ("STATUS", "FINALIZED"): 717,
            ("STATUS", "RECEIVED"): 718,
            ("STATUS", "REPORTED"): 719,
            ("REGISTRATION_MODE", "ONLINE"): 721,
            ("REGISTRATION_MODE", "AUTO"): 722,
            ("REGISTRATION_STATUS", "REGISTERED"): 723,
            ("ATTENDANCE_STATUS", "PRESENT"): 701,
            ("ATTENDANCE_STATUS", "ABSENT"): 702,
            ("MODERATION_REASON", "MARK_REVIEW"): 724,
            ("MODERATION_REASON", "VERIFICATION"): 725,
            ("MALPRACTICE_TYPE", "USING_MOBILE"): 726,
            ("MALPRACTICE_TYPE", "COPYING"): 727,
            ("ACTION_TAKEN", "WARNING"): 728,
            ("ACTION_TAKEN", "EXPULSION"): 729,
        }

        # Helper functions for lookup tables with fallback fallback values
        async def ensure_lookup_category(cat_name):
            try:
                res = await db.async_genericSQL(
                    text("SELECT id FROM sch_lookup.tb_lookup_cat WHERE name = :name"),
                    {"name": cat_name},
                )
                if res["status"] == "error":
                    err_msg = str(db.errMsg).lower()
                    if (
                        "permission denied" in err_msg
                        or "insufficientprivilege" in err_msg
                    ):
                        val = KNOWN_CATEGORIES.get(cat_name)
                        print(
                            f"[INFO] Privilege restricted on sch_lookup. Cat '{cat_name}' using fallback ID: {val}"
                        )
                        return val
                    print(
                        f"[ERROR] failed to query lookup category: {res['message']} | DB Err: {db.errMsg}"
                    )
                    raise Exception(f"Query lookup category failed: {db.errMsg}")
                if res["data"]:
                    return res["data"][0]["id"]

                max_res = await db.async_genericSQL(
                    text(
                        "SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM sch_lookup.tb_lookup_cat"
                    )
                )
                if max_res["status"] == "error":
                    print(
                        f"[ERROR] failed to query max lookup category: {max_res['message']} | DB Err: {db.errMsg}"
                    )
                    raise Exception(f"Query max lookup category failed: {db.errMsg}")
                next_id = max_res["data"][0]["next_id"]

                insert_res = await db.async_genericSQL(
                    text(
                        "INSERT INTO sch_lookup.tb_lookup_cat (id, name, status) VALUES (:id, :name, true)"
                    ),
                    {"id": next_id, "name": cat_name},
                )
                if insert_res["status"] == "error":
                    print(
                        f"[ERROR] failed to insert lookup category: {insert_res['message']} | DB Err: {db.errMsg}"
                    )
                    raise Exception(f"Insert lookup category failed: {db.errMsg}")
                return next_id
            except Exception as _e:
                val = KNOWN_CATEGORIES.get(cat_name)
                print(
                    f"[INFO] Using fallback ID for category '{cat_name}': {val} due to: {e}"
                )
                return val

        async def ensure_lookup(cat_id, lookup_name):
            # Reverse resolve the category name for dictionary mapping keys
            cat_name = next(
                (k for k, v in KNOWN_CATEGORIES.items() if v == cat_id), "STATUS"
            )
            try:
                res = await db.async_genericSQL(
                    text(
                        "SELECT id FROM sch_lookup.tb_lookup WHERE cat_id = :cat_id AND name = :name"
                    ),
                    {"cat_id": cat_id, "name": lookup_name},
                )
                if res["status"] == "error":
                    err_msg = str(db.errMsg).lower()
                    if (
                        "permission denied" in err_msg
                        or "insufficientprivilege" in err_msg
                    ):
                        val = KNOWN_LOOKUPS.get((cat_name, lookup_name))
                        print(
                            f"[INFO] Privilege restricted on sch_lookup. Lookup '{lookup_name}' using fallback ID: {val}"
                        )
                        return val
                    print(
                        f"[ERROR] failed to query lookup: {res['message']} | DB Err: {db.errMsg}"
                    )
                    raise Exception(f"Query lookup failed: {db.errMsg}")
                if res["data"]:
                    return res["data"][0]["id"]

                max_res = await db.async_genericSQL(
                    text(
                        "SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM sch_lookup.tb_lookup"
                    )
                )
                if max_res["status"] == "error":
                    print(
                        f"[ERROR] failed to query max lookup: {max_res['message']} | DB Err: {db.errMsg}"
                    )
                    raise Exception(f"Query max lookup failed: {db.errMsg}")
                next_id = max_res["data"][0]["next_id"]

                insert_res = await db.async_genericSQL(
                    text(
                        "INSERT INTO sch_lookup.tb_lookup (id, cat_id, name, status) VALUES (:id, :cat_id, :name, true)"
                    ),
                    {"id": next_id, "cat_id": cat_id, "name": lookup_name},
                )
                if insert_res["status"] == "error":
                    print(
                        f"[ERROR] failed to insert lookup: {insert_res['message']} | DB Err: {db.errMsg}"
                    )
                    raise Exception(f"Insert lookup failed: {db.errMsg}")
                return next_id
            except Exception as _e:
                val = KNOWN_LOOKUPS.get((cat_name, lookup_name))
                print(
                    f"[INFO] Using fallback ID for lookup '{lookup_name}': {val} due to: {e}"
                )
                return val

        # Explicitly target the sch_examination schema name
        SCHEMA_NAME = "sch_examination"
        print(f"Target Schema configured: {SCHEMA_NAME}")

        # 1. Populate lookups
        print("Populating lookup metadata...")
        exam_session_type_cat = await ensure_lookup_category("EXAM_SESSION_TYPE")
        end_sem_type_id = await ensure_lookup(exam_session_type_cat, "END_SEMESTER")
        mid_sem_type_id = await ensure_lookup(exam_session_type_cat, "MID_SEMESTER")

        status_cat = await ensure_lookup_category("STATUS")
        draft_status_id = await ensure_lookup(status_cat, "DRAFT")
        active_status_id = await ensure_lookup(status_cat, "ACTIVE")
        completed_status_id = await ensure_lookup(status_cat, "COMPLETED")
        await ensure_lookup(status_cat, "PUBLISHED")
        approved_status_id = await ensure_lookup(status_cat, "APPROVED")
        finalized_status_id = await ensure_lookup(status_cat, "FINALIZED")
        received_status_id = await ensure_lookup(status_cat, "RECEIVED")
        reported_status_id = await ensure_lookup(status_cat, "REPORTED")

        reg_mode_cat = await ensure_lookup_category("REGISTRATION_MODE")
        online_reg_mode_id = await ensure_lookup(reg_mode_cat, "ONLINE")
        auto_reg_mode_id = await ensure_lookup(reg_mode_cat, "AUTO")

        reg_status_cat = await ensure_lookup_category("REGISTRATION_STATUS")
        registered_status_id = await ensure_lookup(reg_status_cat, "REGISTERED")

        att_status_cat = await ensure_lookup_category("ATTENDANCE_STATUS")
        present_att_status_id = await ensure_lookup(att_status_cat, "PRESENT")
        absent_att_status_id = await ensure_lookup(att_status_cat, "ABSENT")

        moderation_reason_cat = await ensure_lookup_category("MODERATION_REASON")
        mark_review_reason_id = await ensure_lookup(
            moderation_reason_cat, "MARK_REVIEW"
        )
        verification_reason_id = await ensure_lookup(
            moderation_reason_cat, "VERIFICATION"
        )

        malpractice_type_cat = await ensure_lookup_category("MALPRACTICE_TYPE")
        using_mobile_type_id = await ensure_lookup(malpractice_type_cat, "USING_MOBILE")
        copying_type_id = await ensure_lookup(malpractice_type_cat, "COPYING")

        action_taken_cat = await ensure_lookup_category("ACTION_TAKEN")
        warning_action_taken_id = await ensure_lookup(action_taken_cat, "WARNING")
        expulsion_action_taken_id = await ensure_lookup(action_taken_cat, "EXPULSION")

        print("Lookups checked/inserted successfully.")

        # 2. Resolve external IDs dynamically
        print("Resolving relational target IDs...")

        # Locate target user accounts
        user_res = await db.async_genericSQL(
            text("SELECT id, email FROM sch_iam.tb_user ORDER BY id")
        )
        users = {u["email"]: u["id"] for u in user_res.get("data", [])}
        admin_uid = users.get("admin@oneapp.local", 1)
        users.get("teacher@oneapp.local", 2)
        users.get("student@oneapp.local", 3)

        # Resolve Academic Terms with fallback self-healing insert
        term_res = await db.async_genericSQL(
            text("SELECT id FROM sch_academic_struct.tb_acad_term ORDER BY id LIMIT 3")
        )
        term_ids = (
            [r["id"] for r in term_res.get("data", [])]
            if (term_res.get("status") == "success" and term_res.get("data"))
            else []
        )
        if not term_ids:
            try:
                # 1. Ensure parent tb_acad_year record exists
                await db.async_genericSQL(text("""
                    INSERT INTO sch_academic_struct.tb_acad_year 
                    (id, institution_id, year_name, start_date, end_date, is_current, status_id)
                    VALUES (1, 1, '2025-2026', '2025-08-01', '2026-07-31', true, 4)
                    ON CONFLICT (id) DO NOTHING
                """))
                # 2. Ensure tb_acad_term record exists matching exact NOT NULL schema columns
                await db.async_genericSQL(text("""
                    INSERT INTO sch_academic_struct.tb_acad_term 
                    (id, acad_year_id, term_number, term_name, term_type_id, start_date, end_date, is_current, status_id)
                    VALUES (1, 1, 1, 'Even Semester 2026', 713, '2026-01-01', '2026-06-30', true, 4)
                    ON CONFLICT (id) DO NOTHING
                """))
                term_ids = [1]
            except Exception as _e:
                print(f"[WARNING] acad_term insert fallback: {e}")
                term_ids = [1]

        # Resolve Course Offerings with fallback insert
        offering_res = await db.async_genericSQL(
            text("SELECT id FROM sch_course_ops.tb_crs_offering ORDER BY id LIMIT 10")
        )
        offering_ids = (
            [r["id"] for r in offering_res.get("data", [])]
            if (offering_res.get("status") == "success" and offering_res.get("data"))
            else []
        )
        if not offering_ids:
            for try_query in [
                "INSERT INTO sch_course_ops.tb_crs_offering (id, offering_code, offering_name, status_id) VALUES (101, 'OFFERING_101', 'Intro Course', 4) ON CONFLICT (id) DO NOTHING",
                "INSERT INTO sch_course_ops.tb_crs_offering (id, crs_offering_code, crs_offering_name, status_id) VALUES (101, 'OFFERING_101', 'Intro Course', 4) ON CONFLICT (id) DO NOTHING",
                "INSERT INTO sch_course_ops.tb_crs_offering (id) VALUES (101) ON CONFLICT (id) DO NOTHING",
            ]:
                res = await db.async_genericSQL(text(try_query))
                if res.get("status") == "success":
                    offering_ids = [101]
                    break
            if not offering_ids:
                offering_ids = [101]

        # Resolve Rooms with fallback insert
        room_res = await db.async_genericSQL(
            text("SELECT id FROM sch_infra.tb_room ORDER BY id LIMIT 10")
        )
        room_ids = (
            [r["id"] for r in room_res.get("data", [])]
            if (room_res.get("status") == "success" and room_res.get("data"))
            else []
        )
        if not room_ids:
            for try_query in [
                "INSERT INTO sch_infra.tb_room (id, room_name, capacity) VALUES (1, 'Main Hall 1', 100) ON CONFLICT (id) DO NOTHING",
                "INSERT INTO sch_infra.tb_room (id, room_no, capacity) VALUES (1, 'R101', 100) ON CONFLICT (id) DO NOTHING",
                "INSERT INTO sch_infra.tb_room (id) VALUES (1) ON CONFLICT (id) DO NOTHING",
            ]:
                res = await db.async_genericSQL(text(try_query))
                if res.get("status") == "success":
                    room_ids = [1]
                    break
            if not room_ids:
                room_ids = [1]

        stud_res = await db.async_genericSQL(
            text("SELECT id FROM sch_student.tb_stud LIMIT 50")
        )
        stud_ids = (
            [r["id"] for r in stud_res.get("data", [])]
            if stud_res.get("data")
            else list(range(1, 51))
        )

        fac_res = await db.async_genericSQL(
            text("SELECT id FROM sch_emp_fac.tb_fac LIMIT 10")
        )
        fac_ids = (
            [r["id"] for r in fac_res.get("data", [])]
            if fac_res.get("data")
            else list(range(1, 11))
        )

        print(
            f"Resolved: term_ids={term_ids}, stud_ids_count={len(stud_ids)}, fac_ids_count={len(fac_ids)}"
        )

        # 3. Clean target tables in reverse foreign key order
        print("Cleaning existing exam module records to ensure idempotency...")
        cleanups = [
            ("tb_exam_malpractice", f"DELETE FROM {SCHEMA_NAME}.tb_exam_malpractice"),
            ("tb_exam_final_mark", f"DELETE FROM {SCHEMA_NAME}.tb_exam_final_mark"),
            ("tb_exam_moderation", f"DELETE FROM {SCHEMA_NAME}.tb_exam_moderation"),
            ("tb_exam_evaluation", f"DELETE FROM {SCHEMA_NAME}.tb_exam_evaluation"),
            ("tb_exam_script", f"DELETE FROM {SCHEMA_NAME}.tb_exam_script"),
            ("tb_exam_att", f"DELETE FROM {SCHEMA_NAME}.tb_exam_att"),
            (
                "tb_exam_room_invigilator",
                f"DELETE FROM {SCHEMA_NAME}.tb_exam_room_invigilator",
            ),
            ("tb_exam_room", f"DELETE FROM {SCHEMA_NAME}.tb_exam_room"),
            ("tb_hall_ticket", f"DELETE FROM {SCHEMA_NAME}.tb_hall_ticket"),
            ("tb_exam_registration", f"DELETE FROM {SCHEMA_NAME}.tb_exam_registration"),
            ("tb_exam", f"DELETE FROM {SCHEMA_NAME}.tb_exam"),
            ("tb_exam_session", f"DELETE FROM {SCHEMA_NAME}.tb_exam_session"),
        ]

        for table_name, delete_query in cleanups:
            await exec_query(text(delete_query), desc=f"cleanup {table_name}")

        # 4. Insert Mock Data
        # =====================================================================
        # (1) Seed 3 Exam Sessions
        # =====================================================================
        print("Seeding 3 Exam Sessions...")
        sessions_data = [
            {
                "id": 1,
                "exam_session_code": "EXM_JUL26",
                "exam_session_name": "Even Semester Exam 2026",
                "exam_session_type_id": end_sem_type_id,
                "acad_term_id": term_ids[0],
                "registration_start_date": date(2026, 1, 7),
                "registration_end_date": date(2026, 7, 15),
                "description": "Final Semester EXAM",
                "wf_instance_id": None,
                "status_id": active_status_id,
                "is_active": True,
                "created_by": admin_uid,
            },
            {
                "id": 2,
                "exam_session_code": "EXM_DEC26",
                "exam_session_name": "Odd Semester Exam 2026",
                "exam_session_type_id": mid_sem_type_id,
                "acad_term_id": term_ids[1] if len(term_ids) > 1 else term_ids[0],
                "registration_start_date": date(2026, 1, 12),
                "registration_end_date": date(2026, 12, 15),
                "description": "Mid Semester EXAM",
                "wf_instance_id": None,
                "status_id": active_status_id,
                "is_active": False,
                "created_by": admin_uid,
            },
            {
                "id": 3,
                "exam_session_code": "EXM_MAY27",
                "exam_session_name": "Summer Session Exam 2027",
                "exam_session_type_id": end_sem_type_id,
                "acad_term_id": term_ids[0],
                "registration_start_date": date(2027, 4, 1),
                "registration_end_date": date(2027, 5, 20),
                "description": "Summer Supplementary EXAM",
                "wf_instance_id": None,
                "status_id": draft_status_id,
                "is_active": False,
                "created_by": admin_uid,
            },
        ]

        for s in sessions_data:
            stmt = text("""
                INSERT INTO {SCHEMA_NAME}.tb_exam_session 
                (id, exam_session_code, exam_session_name, exam_session_type_id, acad_term_id, registration_start_date, registration_end_date, description, wf_instance_id, status_id, is_active, created_by)
                VALUES (:id, :exam_session_code, :exam_session_name, :exam_session_type_id, :acad_term_id, :registration_start_date, :registration_end_date, :description, :wf_instance_id, :status_id, :is_active, :created_by)
            """)
            await exec_query(stmt, s, desc=f"tb_exam_session {s['id']}")

        # =====================================================================
        # (2) Seed 10 Exams
        # =====================================================================
        print("Seeding 10 Exams...")
        exams_data = []
        exam_names = [
            "AI Internal Exam",
            "DBMS End Semester",
            "Data Structures Quiz",
            "Computer Networks Final",
            "Operating Systems Mid",
            "Software Engineering Exam",
            "Theory of Computation End Sem",
            "Compiler Design Final",
            "Cloud Computing Quiz",
            "Cyber Security Exam",
        ]
        for i in range(10):
            exams_data.append(
                {
                    "id": i + 1,
                    "exam_session_id": 1 if i < 6 else 2,
                    "crs_offering_id": offering_ids[i % len(offering_ids)],
                    "exam_code": f"EXM_CODE_{i+1:03d}",
                    "exam_name": exam_names[i],
                    "exam_date": date(2026, 7, 20 + i),
                    "start_time": time(9, 30) if i % 2 == 0 else time(14, 0),
                    "end_time": time(12, 30) if i % 2 == 0 else time(17, 0),
                    "max_marks": 100.0,
                    "pass_marks": 40.0,
                    "allow_manual_registration": True,
                    "is_anonymous_evaluation": True,
                    "description": f"Standard evaluation for {exam_names[i]}",
                    "wf_instance_id": None,
                    "status_id": active_status_id,
                    "created_by": admin_uid,
                }
            )

        for e in exams_data:
            stmt = text("""
                INSERT INTO {SCHEMA_NAME}.tb_exam 
                (id, exam_session_id, crs_offering_id, exam_code, exam_name, exam_date, start_time, end_time, max_marks, pass_marks, allow_manual_registration, is_anonymous_evaluation, description, wf_instance_id, status_id, created_by)
                VALUES (:id, :exam_session_id, :crs_offering_id, :exam_code, :exam_name, :exam_date, :start_time, :end_time, :max_marks, :pass_marks, :allow_manual_registration, :is_anonymous_evaluation, :description, :wf_instance_id, :status_id, :created_by)
            """)
            await exec_query(stmt, e, desc=f"tb_exam {e['id']}")

        # =====================================================================
        # (3) Seed 120 Exam Registrations
        # =====================================================================
        print("Seeding 120 Exam Registrations...")
        registrations_data = []
        reg_counter = 1

        for i, stud_id in enumerate(stud_ids[:30]):
            for j in range(4):
                exam_id = ((i + j) % 10) + 1
                registrations_data.append(
                    {
                        "id": reg_counter,
                        "exam_id": exam_id,
                        "stud_id": stud_id,
                        "registration_mode_id": (
                            online_reg_mode_id
                            if reg_counter % 2 == 0
                            else auto_reg_mode_id
                        ),
                        "registration_date": datetime(2026, 6, 15, 10, 0),
                        "status_id": registered_status_id,
                        "created_by": admin_uid,
                    }
                )
                reg_counter += 1

        for r in registrations_data:
            stmt = text("""
                INSERT INTO {SCHEMA_NAME}.tb_exam_registration 
                (id, exam_id, stud_id, registration_mode_id, registration_date, status_id, created_by)
                VALUES (:id, :exam_id, :stud_id, :registration_mode_id, :registration_date, :status_id, :created_by)
            """)
            await exec_query(stmt, r, desc=f"tb_exam_registration {r['id']}")

        # =====================================================================
        # (4) Seed 120 Hall Tickets
        # =====================================================================
        print("Seeding 120 Hall Tickets...")
        for r in registrations_data:
            h_data = {
                "id": r["id"],
                "exam_registration_id": r["id"],
                "hall_ticket_number": f"HT2026{r['id']:04d}",
                "generated_on": datetime(2026, 7, 1, 9, 0),
                "doc_id": 8000 + r["id"],
                "status_id": active_status_id,
                "created_by": admin_uid,
            }
            stmt = text("""
                INSERT INTO {SCHEMA_NAME}.tb_hall_ticket 
                (id, exam_registration_id, hall_ticket_number, generated_on, doc_id, status_id, created_by)
                VALUES (:id, :exam_registration_id, :hall_ticket_number, :generated_on, :doc_id, :status_id, :created_by)
            """)
            await exec_query(stmt, h_data, desc=f"tb_hall_ticket {h_data['id']}")

        # =====================================================================
        # (5) Seed 15 Exam Rooms
        # =====================================================================
        print("Seeding 15 Exam Rooms...")
        rooms_data = []
        room_counter = 1
        for exam_id in range(1, 11):
            for k in range(1, 3 if exam_id % 2 == 0 else 2):
                rooms_data.append(
                    {
                        "id": room_counter,
                        "exam_id": exam_id,
                        "room_id": room_ids[(room_counter - 1) % len(room_ids)],
                        "room_sequence": k,
                        "capacity": 50 if room_counter % 2 == 0 else 60,
                        "created_by": admin_uid,
                    }
                )
                room_counter += 1

        for rm in rooms_data:
            stmt = text("""
                INSERT INTO {SCHEMA_NAME}.tb_exam_room 
                (id, exam_id, room_id, room_sequence, capacity, created_by)
                VALUES (:id, :exam_id, :room_id, :room_sequence, :capacity, :created_by)
            """)
            await exec_query(stmt, rm, desc=f"tb_exam_room {rm['id']}")

        # =====================================================================
        # (6) Seed 25 Invigilator Assignments
        # =====================================================================
        print("Seeding 25 Invigilator Assignments...")
        invig_counter = 1
        for rm in rooms_data[:12]:
            for m in range(2):
                inv_data = {
                    "id": invig_counter,
                    "exam_room_id": rm["id"],
                    "fac_id": fac_ids[invig_counter % len(fac_ids)],
                    "reporting_time": (
                        datetime(2026, 7, 20, 8, 45)
                        if m == 0
                        else datetime(2026, 7, 20, 9, 0)
                    ),
                    "leaving_time": (
                        datetime(2026, 7, 20, 12, 45)
                        if m == 0
                        else datetime(2026, 7, 20, 13, 0)
                    ),
                    "status_id": active_status_id,
                    "created_by": admin_uid,
                }
                stmt = text("""
                    INSERT INTO {SCHEMA_NAME}.tb_exam_room_invigilator 
                    (id, exam_room_id, fac_id, reporting_time, leaving_time, status_id, created_by)
                    VALUES (:id, :exam_room_id, :fac_id, :reporting_time, :leaving_time, :status_id, :created_by)
                """)
                await exec_query(
                    stmt, inv_data, desc=f"tb_exam_room_invigilator {invig_counter}"
                )
                invig_counter += 1

        # =====================================================================
        # (7) Seed Attendance & (8) Exam Scripts
        # =====================================================================
        print("Seeding Attendance and Scripts...")
        exam_to_rooms = {}
        for rm in rooms_data:
            exam_to_rooms.setdefault(rm["exam_id"], []).append(rm["id"])

        for r in registrations_data:
            assigned_rooms = exam_to_rooms.get(r["exam_id"], [1])
            room_id_picked = assigned_rooms[r["id"] % len(assigned_rooms)]

            is_present = (r["id"] % 10) != 0
            att_data = {
                "id": r["id"],
                "exam_registration_id": r["id"],
                "exam_room_id": room_id_picked,
                "att_status_id": (
                    present_att_status_id if is_present else absent_att_status_id
                ),
                "marked_on": datetime(2026, 7, 20, 10, 0),
                "remarks": "Verified Present" if is_present else "Absent",
                "created_by": admin_uid,
            }
            stmt = text("""
                INSERT INTO {SCHEMA_NAME}.tb_exam_att 
                (id, exam_registration_id, exam_room_id, att_status_id, marked_on, remarks, created_by)
                VALUES (:id, :exam_registration_id, :exam_room_id, :att_status_id, :marked_on, :remarks, :created_by)
            """)
            await exec_query(stmt, att_data, desc=f"tb_exam_att {r['id']}")

            if is_present:
                script_data = {
                    "id": r["id"],
                    "exam_registration_id": r["id"],
                    "script_number": f"SCR{r['id']:04d}",
                    "barcode": f"BC1000{r['id']}",
                    "script_doc_id": 9000 + r["id"],
                    "received_on": datetime(2026, 7, 21, 16, 0),
                    "is_anonymous": True,
                    "status_id": received_status_id,
                    "created_by": admin_uid,
                }
                stmt = text("""
                    INSERT INTO {SCHEMA_NAME}.tb_exam_script 
                    (id, exam_registration_id, script_number, barcode, script_doc_id, received_on, is_anonymous, status_id, created_by)
                    VALUES (:id, :exam_registration_id, :script_number, :barcode, :script_doc_id, :received_on, :is_anonymous, :status_id, :created_by)
                """)
                await exec_query(stmt, script_data, desc=f"tb_exam_script {r['id']}")

        # =====================================================================
        # (9) Seed 108 Evaluations
        # =====================================================================
        print("Seeding 108 Evaluations...")
        eval_counter = 1
        for r in registrations_data:
            is_present = (r["id"] % 10) != 0
            if is_present:
                score = float(45 + (r["id"] % 50))
                eval_data = {
                    "id": eval_counter,
                    "exam_script_id": r["id"],
                    "evaluator_id": fac_ids[eval_counter % len(fac_ids)],
                    "evaluation_no": 1,
                    "total_marks": score,
                    "evaluated_on": datetime(2026, 7, 28, 14, 0),
                    "remarks": "Evaluation complete",
                    "status_id": completed_status_id,
                    "created_by": admin_uid,
                }
                stmt = text("""
                    INSERT INTO {SCHEMA_NAME}.tb_exam_evaluation 
                    (id, exam_script_id, evaluator_id, evaluation_no, total_marks, evaluated_on, remarks, status_id, created_by)
                    VALUES (:id, :exam_script_id, :evaluator_id, :evaluation_no, :total_marks, :evaluated_on, :remarks, :status_id, :created_by)
                """)
                await exec_query(
                    stmt, eval_data, desc=f"tb_exam_evaluation {eval_counter}"
                )
                eval_counter += 1

        # =====================================================================
        # (10) Seed 30 Moderations
        # =====================================================================
        print("Seeding 30 Moderations...")
        mod_counter = 1
        for ev_id in range(1, min(eval_counter, 31)):
            score = float(45 + (ev_id % 50))
            mod_data = {
                "id": mod_counter,
                "exam_evaluation_id": ev_id,
                "moderator_id": fac_ids[(ev_id + 2) % len(fac_ids)],
                "moderated_marks": score + (3.0 if ev_id % 2 == 0 else -1.0),
                "moderation_reason_id": (
                    mark_review_reason_id if ev_id % 2 == 0 else verification_reason_id
                ),
                "moderated_on": datetime(2026, 7, 30, 11, 0),
                "status_id": approved_status_id,
                "created_by": admin_uid,
            }
            stmt = text("""
                INSERT INTO {SCHEMA_NAME}.tb_exam_moderation 
                (id, exam_evaluation_id, moderator_id, moderated_marks, moderation_reason_id, moderated_on, status_id, created_by)
                VALUES (:id, :exam_evaluation_id, :moderator_id, :moderated_marks, :moderation_reason_id, :moderated_on, :status_id, :created_by)
            """)
            await exec_query(stmt, mod_data, desc=f"tb_exam_moderation {mod_counter}")
            mod_counter += 1

        # =====================================================================
        # (11) Seed 108 Final Marks Records
        # =====================================================================
        print("Seeding 108 Final Marks Records...")
        final_counter = 1
        for r in registrations_data:
            is_present = (r["id"] % 10) != 0
            if is_present:
                score = float(45 + (r["id"] % 50))
                if r["id"] <= 30:
                    final_score = score + (3.0 if r["id"] % 2 == 0 else -1.0)
                else:
                    final_score = score

                final_data = {
                    "id": final_counter,
                    "exam_registration_id": r["id"],
                    "final_marks": final_score,
                    "finalized_from_evaluation_id": r["id"],
                    "finalized_by": fac_ids[r["id"] % len(fac_ids)],
                    "finalized_on": datetime(2026, 8, 1, 10, 0),
                    "status_id": finalized_status_id,
                    "created_by": admin_uid,
                }
                stmt = text("""
                    INSERT INTO {SCHEMA_NAME}.tb_exam_final_mark 
                    (id, exam_registration_id, final_marks, finalized_from_evaluation_id, finalized_by, finalized_on, status_id, created_by)
                    VALUES (:id, :exam_registration_id, :final_marks, :finalized_from_evaluation_id, :finalized_by, :finalized_on, :status_id, :created_by)
                """)
                await exec_query(
                    stmt, final_data, desc=f"tb_exam_final_mark {final_counter}"
                )
                final_counter += 1

        # =====================================================================
        # (12) Seed 8 Malpractice Cases
        # =====================================================================
        print("Seeding 8 Malpractice Cases...")
        mal_counter = 1
        for r in registrations_data:
            if r["id"] % 15 == 0 and mal_counter <= 8:
                assigned_rooms = exam_to_rooms.get(r["exam_id"], [1])
                room_id_picked = assigned_rooms[r["id"] % len(assigned_rooms)]

                mal_data = {
                    "id": mal_counter,
                    "exam_registration_id": r["id"],
                    "exam_room_id": room_id_picked,
                    "malpractice_type_id": (
                        using_mobile_type_id
                        if mal_counter % 2 == 0
                        else copying_type_id
                    ),
                    "rpted_by": fac_ids[mal_counter % len(fac_ids)],
                    "rpted_on": datetime(2026, 7, 22, 10, 30),
                    "description": (
                        "Caught copying answers from paper/phone."
                        if mal_counter % 2 == 0
                        else "Mobile device storage detected."
                    ),
                    "action_taken_id": (
                        warning_action_taken_id
                        if mal_counter % 2 == 0
                        else expulsion_action_taken_id
                    ),
                    "status_id": reported_status_id,
                    "created_by": admin_uid,
                }
                stmt = text("""
                    INSERT INTO {SCHEMA_NAME}.tb_exam_malpractice 
                    (id, exam_registration_id, exam_room_id, malpractice_type_id, rpted_by, rpted_on, description, action_taken_id, status_id, created_by)
                    VALUES (:id, :exam_registration_id, :exam_room_id, :malpractice_type_id, :rpted_by, :rpted_on, :description, :action_taken_id, :status_id, :created_by)
                """)
                await exec_query(
                    stmt, mal_data, desc=f"tb_exam_malpractice {mal_counter}"
                )
                mal_counter += 1

        print("\nAll High-Volume Examinations Module data successfully seeded!")

    finally:
        await db.async_disconnectDB()


if __name__ == "__main__":
    asyncio.run(seed_exam_data())
