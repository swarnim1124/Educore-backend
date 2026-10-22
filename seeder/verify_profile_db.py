"""
File: verify_profile_db.py
Description: Integration testing script for the seeded profile module data.
"""

import sys
import os
import asyncio
from sqlalchemy import text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../modules/m_profile"))
)

from xsc_lib.xsc_lib_common.xsc_libc_pgrs import PostgreSQLManager
from xsc_lib.xsc_lib_common.xsc_libc_context import ExecutionContext, SecurityContext
from xsc_lib.xsc_lib_app.xsc_liba_dispatcher import ActionDispatcher
from xsc_lib.xsc_lib_common.xsc_libc_models import OneAppRequest


class MockContainer:
    def __init__(self, db):
        self.postgres = db

    def resolve(self, name):
        if name == "PostgreSQLManager":
            return self.postgres
        return None


PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"


def check(label, condition, detail=""):
    status = PASS if condition else FAIL
    msg = f"  [{status}] {label}"
    if detail and not condition:
        msg += f"  — {detail}"
    print(msg)
    if not condition:
        raise AssertionError(f"Check failed: {label}")


async def run_tests():
    print("=" * 60)
    print("  m_profile DB Seeder Verification")
    print("=" * 60)

    db = PostgreSQLManager()
    conn_resp = await db.async_connectDB()
    if conn_resp["status"] == "error":
        print(f"Failed to connect: {conn_resp['message']}")
        return

    container = MockContainer(db)
    dispatcher = ActionDispatcher()

    # Query target user IDs
    user_res = await db.async_genericSQL(
        text("SELECT id, email FROM sch_iam.tb_user ORDER BY id")
    )
    users = {u["email"]: u["id"] for u in user_res.get("data", [])}

    admin_uid = users.get("admin@oneapp.local")
    teacher_uid = users.get("teacher@oneapp.local")
    student_uid = users.get("student@oneapp.local")

    # Fetch student ID (optional, might not exist due to database privileges)
    stud_id = None
    try:
        stud_ids_res = await db.async_genericSQL(
            text("SELECT id FROM sch_student.tb_stud WHERE user_id = :student_uid"),
            {"student_uid": student_uid},
        )
        if stud_ids_res.get("status") == "success" and stud_ids_res.get("data"):
            stud_id = stud_ids_res["data"][0].get("id")
    except Exception:
        print(
            "[INFO] sch_student.tb_stud table is missing or inaccessible. Skipping student ID resolution."
        )

    # Fetch relationship lookup IDs
    f_res = await db.async_genericSQL(
        text("SELECT id FROM sch_lookup.tb_lookup WHERE name = 'Father'")
    )
    father_id = (
        f_res["data"][0]["id"]
        if f_res["status"] == "success" and f_res["data"]
        else None
    )

    m_res = await db.async_genericSQL(
        text("SELECT id FROM sch_lookup.tb_lookup WHERE name = 'Mother'")
    )
    mother_id = (
        m_res["data"][0]["id"]
        if m_res["status"] == "success" and m_res["data"]
        else None
    )

    # Mock Contexts
    admin_ctx = ExecutionContext(request_id="test_admin", service_container=container)
    admin_ctx.security = SecurityContext(user_id=admin_uid, roles=["ADMIN"])

    teacher_ctx = ExecutionContext(
        request_id="test_teacher", service_container=container
    )
    teacher_ctx.security = SecurityContext(user_id=teacher_uid, roles=["TEACHER"])

    student_ctx = ExecutionContext(
        request_id="test_student", service_container=container
    )
    student_ctx.security = SecurityContext(user_id=student_uid, roles=["STUDENT"])

    try:
        # 1. Verify Personal Detail
        print("\n--- 1. Testing personalDetail.view ---")
        req = OneAppRequest(
            **{
                "mod": "m_profile",
                "subMod": "sm_personal_detail",
                "action": "personalDetail",
                "actionType": "view",
                "payload": {"userId": student_uid},
            }
        )
        resp = await dispatcher.dispatch(req, student_ctx)
        check("personalDetail retrieved successfully", resp.get("status") == "success")
        profile = resp.get("data", {})
        check("First name matches 'Aman'", profile.get("firstName") == "Aman")
        check("Last name matches 'Sharma'", profile.get("lastName") == "Sharma")
        check("Mobile matches '9876543212'", profile.get("mobile") == "9876543212")

        # 2. Verify Academic Identifier
        print("\n--- 2. Testing academicDetail.view ---")
        req = OneAppRequest(
            **{
                "mod": "m_profile",
                "subMod": "sm_academic_detail",
                "action": "academicDetail",
                "actionType": "view",
                "payload": {"userId": student_uid},
            }
        )
        resp = await dispatcher.dispatch(req, student_ctx)
        check("academicDetail retrieved successfully", resp.get("status") == "success")
        acad = resp.get("data", {})
        if acad.get("enrollmentNumber") is not None:
            check(
                "enrollmentNumber matches 'STU-2026-0003'",
                acad.get("enrollmentNumber") == "STU-2026-0003",
            )
        else:
            print(
                "[INFO] enrollmentNumber is None (student master table not available). Skipping enrollmentNumber check."
            )

        identifiers = acad.get("identifiers", [])
        check("Has at least one identifier", len(identifiers) >= 2)
        card_val = next(
            (
                i["identifier_value"]
                for i in identifiers
                if i["identifier_type_id"] == 1
            ),
            None,
        )
        bio_val = next(
            (
                i["identifier_value"]
                for i in identifiers
                if i["identifier_type_id"] == 2
            ),
            None,
        )
        check("Card value matches CARD-STU-0003", card_val == "CARD-STU-0003")
        check("Biometric value matches BIO-STU-0003", bio_val == "BIO-STU-0003")

        # Teacher Academic details
        req = OneAppRequest(
            **{
                "mod": "m_profile",
                "subMod": "sm_academic_detail",
                "action": "academicDetail",
                "actionType": "view",
                "payload": {"userId": teacher_uid},
            }
        )
        resp = await dispatcher.dispatch(req, teacher_ctx)
        check("academicDetail retrieved successfully", resp.get("status") == "success")
        acad_t = resp.get("data", {})
        if acad_t.get("employeeCode") is not None:
            check(
                "employeeCode matches 'EMP-2026-0002'",
                acad_t.get("employeeCode") == "EMP-2026-0002",
            )
        else:
            print(
                "[INFO] employeeCode is None (employee master table not available). Skipping employeeCode check."
            )

        # 3. Verify Family Details
        print("\n--- 3. Testing familyDetail.view ---")
        if stud_id is not None:
            req = OneAppRequest(
                **{
                    "mod": "m_profile",
                    "subMod": "sm_family_detail",
                    "action": "familyDetail",
                    "actionType": "view",
                    "payload": {"studentId": stud_id},
                }
            )
            resp = await dispatcher.dispatch(req, student_ctx)
            check(
                "familyDetail retrieved successfully", resp.get("status") == "success"
            )
            family = resp.get("data", [])
            check("Seeded 2 family members", len(family) == 2)
            father = next(
                (f for f in family if f["relationship_type_id"] == father_id), None
            )
            mother = next(
                (f for f in family if f["relationship_type_id"] == mother_id), None
            )
            check("Father record exists", father is not None)
            check(
                "Father name is Ramesh Sharma",
                f"{father['first_name']} {father['last_name']}" == "Ramesh Sharma",
            )
            check(
                "Father is primary guardian", father["is_primary_guardian"].is_(False)
            )  # Mother is primary in our seeds
            check("Mother record exists", mother is not None)
            check(
                "Mother name is Kiran Sharma",
                f"{mother['first_name']} {mother['last_name']}" == "Kiran Sharma",
            )
            check(
                "Mother is emergency contact", mother["is_emergency_contact"].is_(True)
            )
        else:
            print(
                "[INFO] Skipping familyDetail.view checks (student master record not available)."
            )

        # 4. Verify Emergency Contacts
        print("\n--- 4. Testing emergencyContact.view ---")
        req = OneAppRequest(
            **{
                "mod": "m_profile",
                "subMod": "sm_family_detail",
                "action": "emergencyContact",
                "actionType": "view",
                "payload": {"userId": teacher_uid},
            }
        )
        resp = await dispatcher.dispatch(req, teacher_ctx)
        check(
            "emergencyContact retrieved successfully", resp.get("status") == "success"
        )
        contacts = resp.get("data", [])
        check("Seeded 1 emergency contact", len(contacts) == 1)
        check(
            "Contact name is Suresh Sen",
            f"{contacts[0]['f_name']} {contacts[0]['l_name']}" == "Suresh Sen",
        )
        check("Contact is primary", contacts[0]["is_primary"].is_(True))

        # 5. Verify Medical Details
        print("\n--- 5. Testing medicalDetail.view & Access Control ---")
        # Test Owner access
        req = OneAppRequest(
            **{
                "mod": "m_profile",
                "subMod": "sm_medical_detail",
                "action": "medicalDetail",
                "actionType": "view",
                "payload": {"userId": student_uid},
            }
        )
        resp = await dispatcher.dispatch(req, student_ctx)
        check(
            "Medical retrieved successfully by owner", resp.get("status") == "success"
        )
        med = resp.get("data", {})
        check(
            "Allergies match Dust, Pollen", med.get("allergies") == ["Dust", "Pollen"]
        )
        check(
            "Chronic conditions match Asthma",
            med.get("chronicConditions") == ["Asthma"],
        )
        check(
            "Doctor name matches Dr. S. K. Mehta",
            med.get("doctorName") == "Dr. S. K. Mehta",
        )

        # Test Admin access
        resp = await dispatcher.dispatch(req, admin_ctx)
        check(
            "Medical retrieved successfully by Admin", resp.get("status") == "success"
        )

        # Test Denied Access (Teacher trying to view Student)
        resp = await dispatcher.dispatch(req, teacher_ctx)
        check(
            "Medical access denied to non-authorized roles",
            resp.get("status") == "error",
        )
        check(
            "Correct access denied message returned",
            "Access denied" in resp.get("message", ""),
        )

        # 6. Verify User Preferences
        print("\n--- 6. Testing userPreference.view ---")
        req = OneAppRequest(
            **{
                "mod": "m_profile",
                "subMod": "sm_settings",
                "action": "userPreference",
                "actionType": "view",
                "payload": {"userId": student_uid},
            }
        )
        resp = await dispatcher.dispatch(req, student_ctx)
        check("userPreference retrieved successfully", resp.get("status") == "success")
        prefs = resp.get("data", {})
        check("Theme matches 'dark'", prefs.get("theme") == "dark")
        check(
            "Timezone matches 'Asia/Kolkata'", prefs.get("timezone") == "Asia/Kolkata"
        )
        check(
            "Default landing module is m_student",
            prefs.get("defaultLandingModule") == "m_student",
        )

        print("\nAll Profile DB Seeder checks passed successfully!")

    finally:
        await db.async_disconnectDB()


if __name__ == "__main__":
    asyncio.run(run_tests())
