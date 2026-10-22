"""
File: verify_exam_db.py
Description: Direct database verification suite for the populated Examinations module tables.
"""

import sys
import os
import asyncio
from sqlalchemy import text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from xsc_lib.xsc_lib_common.xsc_libc_pgrs import PostgreSQLManager

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"


def check(label, condition, detail=""):
    status = PASS if condition else FAIL
    msg = f"  [{status}] {label}"
    if detail and not condition:
        msg += f"  — {detail}"
    print(msg)
    if not condition:
        raise AssertionError(f"Verification failed: {label}")


async def run_db_verifications():
    print("=" * 60)
    print("  Examinations DB Seeder Verification")
    print("=" * 60)

    db = PostgreSQLManager()
    conn_resp = await db.async_connectDB()
    if conn_resp["status"] == "error":
        print(f"Failed to connect: {conn_resp['message']}")
        return

    try:
        # Explicitly target the sch_examination schema name
        SCHEMA_NAME = "sch_examination"
        print(f"Target Schema: {SCHEMA_NAME}")

        # 1. Verify schema tables and counts
        tables_to_verify = [
            ("tb_exam_session", 3),
            ("tb_exam", 10),
            ("tb_exam_registration", 120),
            ("tb_hall_ticket", 120),
            ("tb_exam_room", 15),
            ("tb_exam_room_invigilator", 24),
            ("tb_exam_att", 120),
            ("tb_exam_script", 108),  # 90% of 120 are present
            ("tb_exam_evaluation", 108),
            ("tb_exam_moderation", 30),
            ("tb_exam_final_mark", 108),
            ("tb_exam_malpractice", 8),
        ]

        print("\n--- 1. Checking Table Row Counts ---")
        for table_name, expected_count in tables_to_verify:
            res = await db.async_genericSQL(
                text(f"SELECT COUNT(*) as count FROM {SCHEMA_NAME}.{table_name}")
            )
            if res["status"] == "error":
                check(
                    f"Table {table_name} query success", False, f"DB Error: {db.errMsg}"
                )
            else:
                count = res["data"][0]["count"]
                check(
                    f"Table '{table_name}' has populated records",
                    count > 0,
                    f"Found {count} records",
                )
                check(
                    f"Table '{table_name}' matches expected volume",
                    count == expected_count,
                    f"Found {count}, expected {expected_count}",
                )

        # 2. Verify specific data values
        print("\n--- 2. Validating Seeding Integrity & Field Values ---")

        # Verify exam session values
        session_res = await db.async_genericSQL(
            text(f"SELECT * FROM {SCHEMA_NAME}.tb_exam_session WHERE id = 1")
        )
        check("Exam session ID 1 retrieved", len(session_res.get("data", [])) > 0)
        if session_res.get("data"):
            s_row = session_res["data"][0]
            check(
                "Session code matches 'EXM_JUL26'",
                s_row["exam_session_code"] == "EXM_JUL26",
            )
            check(
                "Session name matches 'Even Semester Exam 2026'",
                s_row["exam_session_name"] == "Even Semester Exam 2026",
            )
            check("Session is active", s_row["is_active"] is True)

        # Verify exam values
        exam_res = await db.async_genericSQL(
            text(f"SELECT * FROM {SCHEMA_NAME}.tb_exam WHERE id = 1")
        )
        check("Exam ID 1 retrieved", len(exam_res.get("data", [])) > 0)
        if exam_res.get("data"):
            e_row = exam_res["data"][0]
            check(
                "Exam name matches 'AI Internal Exam'",
                e_row["exam_name"] == "AI Internal Exam",
            )
            check("Exam max marks matches 100.0", float(e_row["max_marks"]) == 100.0)

        # Verify hall ticket values
        ht_res = await db.async_genericSQL(
            text(f"SELECT * FROM {SCHEMA_NAME}.tb_hall_ticket WHERE id = 1")
        )
        check("Hall ticket ID 1 retrieved", len(ht_res.get("data", [])) > 0)
        if ht_res.get("data"):
            ht_row = ht_res["data"][0]
            check(
                "Hall ticket number matches 'HT20260001'",
                ht_row["hall_ticket_number"] == "HT20260001",
            )

        print("\nAll examinations DB Seeder checks passed successfully!")

    finally:
        await db.async_disconnectDB()


if __name__ == "__main__":
    asyncio.run(run_db_verifications())
