"""
File: seed_m_profile.py
Description: Database data seeder for the profile module (m_profile).
             Contains only data populating operations matching columns and tables
             specified in the master data management Excel sheet.
"""

import sys
import os
import asyncio
import json
from datetime import datetime
from sqlalchemy import text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from xsc_lib.xsc_lib_common.xsc_libc_pgrs import PostgreSQLManager


async def seed_profile_data():
    print("Starting Profile Module Database Seeding...")
    db = PostgreSQLManager()
    conn_resp = await db.async_connectDB()
    if conn_resp["status"] == "error":
        print(f"Failed to connect: {conn_resp['message']} | DB Err: {db.errMsg}")
        return

    try:
        # Helper function for executing seeder queries
        async def exec_query(stmt, params=None, desc="Query"):
            res = await db.async_genericSQL(stmt, params)
            if res["status"] == "error":
                err_msg = str(db.errMsg).lower()
                if (
                    "permission denied" in err_msg
                    or "insufficientprivilege" in err_msg
                    or "does not exist" in err_msg
                ):
                    print(
                        f"[WARNING] Skipping {desc}: DB permission denied or table missing."
                    )
                    return {
                        "status": "skipped",
                        "message": "Permission denied or table missing",
                    }
                print(
                    f"[ERROR] Failed in {desc}: {res['message']} | DB Err: {db.errMsg}"
                )
                raise Exception(f"{desc} failed: {db.errMsg}")
            return res

        # Helper functions for lookup tables
        async def ensure_lookup_category(cat_name):
            res = await db.async_genericSQL(
                text("SELECT id FROM sch_lookup.tb_lookup_cat WHERE name = :name"),
                {"name": cat_name},
            )
            if res["status"] == "success" and res["data"]:
                return res["data"][0]["id"]

            max_res = await db.async_genericSQL(
                text(
                    "SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM sch_lookup.tb_lookup_cat"
                )
            )
            next_id = max_res["data"][0]["next_id"]

            await db.async_genericSQL(
                text(
                    "INSERT INTO sch_lookup.tb_lookup_cat (id, name, status) VALUES (:id, :name, true)"
                ),
                {"id": next_id, "name": cat_name},
            )
            return next_id

        async def ensure_lookup(cat_id, lookup_name):
            res = await db.async_genericSQL(
                text(
                    "SELECT id FROM sch_lookup.tb_lookup WHERE cat_id = :cat_id AND name = :name"
                ),
                {"cat_id": cat_id, "name": lookup_name},
            )
            if res["status"] == "success" and res["data"]:
                return res["data"][0]["id"]

            max_res = await db.async_genericSQL(
                text(
                    "SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM sch_lookup.tb_lookup"
                )
            )
            next_id = max_res["data"][0]["next_id"]

            await db.async_genericSQL(
                text(
                    "INSERT INTO sch_lookup.tb_lookup (id, cat_id, name, status) VALUES (:id, :cat_id, :name, true)"
                ),
                {"id": next_id, "cat_id": cat_id, "name": lookup_name},
            )
            return next_id

        # 1. Populate lookups
        print("Populating lookup metadata...")
        gender_cat = await ensure_lookup_category("GENDER")
        male_id = await ensure_lookup(gender_cat, "Male")
        female_id = await ensure_lookup(gender_cat, "Female")

        blood_cat = await ensure_lookup_category("BLOOD_GROUP")
        o_pos_id = await ensure_lookup(blood_cat, "O+")
        await ensure_lookup(blood_cat, "A+")
        await ensure_lookup(blood_cat, "B+")

        relation_cat = await ensure_lookup_category("RELATIONSHIP_TYPE")
        father_id = await ensure_lookup(relation_cat, "Father")
        mother_id = await ensure_lookup(relation_cat, "Mother")

        lang_cat = await ensure_lookup_category("LANGUAGE")
        await ensure_lookup(lang_cat, "English")

        status_cat = await ensure_lookup_category("STATUS")
        active_status_id = await ensure_lookup(status_cat, "ACTIVE")

        print("Lookups checked/inserted successfully.")

        # 2. Locate target user accounts
        user_res = await db.async_genericSQL(
            text("SELECT id, email FROM sch_iam.tb_user ORDER BY id")
        )
        users = {u["email"]: u["id"] for u in user_res.get("data", [])}

        admin_uid = users.get("admin@oneapp.local")
        teacher_uid = users.get("teacher@oneapp.local")
        student_uid = users.get("student@oneapp.local")

        if not admin_uid or not teacher_uid or not student_uid:
            print(
                "Error: Default AAA users not found in the database. Run seed_m_aaa.py first!"
            )
            return

        target_uids = [admin_uid, teacher_uid, student_uid]
        print(f"Cleaning existing profile records for target users {target_uids}...")

        # 3. Clean existing seeded data to ensure idempotency
        await exec_query(
            text("DELETE FROM sch_iam.tb_user_preference WHERE user_id = ANY(:uids)"),
            {"uids": target_uids},
            "clean preferences",
        )
        await exec_query(
            text("DELETE FROM sch_iam.tb_user_med WHERE user_id = ANY(:uids)"),
            {"uids": target_uids},
            "clean medical",
        )
        await exec_query(
            text("DELETE FROM sch_iam.tb_user_identifier WHERE user_id = ANY(:uids)"),
            {"uids": target_uids},
            "clean identifiers",
        )
        await exec_query(
            text(
                "DELETE FROM sch_iam.tb_user_emergency_contact WHERE user_id = ANY(:uids)"
            ),
            {"uids": target_uids},
            "clean emergency contacts",
        )

        # User addresses and physical addresses clean
        addr_ids_res = await exec_query(
            text(
                "SELECT address_id FROM sch_iam.tb_user_address WHERE user_id = ANY(:uids)"
            ),
            {"uids": target_uids},
            "select addresses to clean",
        )
        await exec_query(
            text("DELETE FROM sch_iam.tb_user_address WHERE user_id = ANY(:uids)"),
            {"uids": target_uids},
            "clean user address mapping",
        )
        if addr_ids_res.get("status") == "success" and addr_ids_res.get("data"):
            addr_ids = [
                r["address_id"] for r in addr_ids_res["data"] if r.get("address_id")
            ]
            if addr_ids:
                await exec_query(
                    text("DELETE FROM sch_core.tb_address WHERE id = ANY(:a_ids)"),
                    {"a_ids": addr_ids},
                    "clean addresses",
                )

        # Parent profiles and student-parent mappings clean
        stud_ids_res = await db.async_genericSQL(
            text("SELECT id FROM sch_student.tb_stud WHERE user_id = :student_uid"),
            {"student_uid": student_uid},
        )
        if stud_ids_res.get("status") == "success" and stud_ids_res.get("data"):
            stud_id = stud_ids_res["data"][0].get("id")
            if stud_id:
                par_ids_res = await db.async_genericSQL(
                    text(
                        "SELECT par_id FROM sch_parents.tb_par_stud WHERE stud_id = :stud_id"
                    ),
                    {"stud_id": stud_id},
                )
                await exec_query(
                    text(
                        "DELETE FROM sch_parents.tb_par_stud WHERE stud_id = :stud_id"
                    ),
                    {"stud_id": stud_id},
                    "clean student parent links",
                )
                if par_ids_res.get("status") == "success" and par_ids_res.get("data"):
                    par_ids = [
                        r["par_id"] for r in par_ids_res["data"] if r.get("par_id")
                    ]
                    if par_ids:
                        await exec_query(
                            text(
                                "DELETE FROM sch_parents.tb_par WHERE id = ANY(:p_ids)"
                            ),
                            {"p_ids": par_ids},
                            "clean parents",
                        )

        await exec_query(
            text("DELETE FROM sch_student.tb_stud WHERE user_id = :student_uid"),
            {"student_uid": student_uid},
            "clean student master record",
        )
        await exec_query(
            text("DELETE FROM sch_emp_fac.tb_emp WHERE user_id = :teacher_uid"),
            {"teacher_uid": teacher_uid},
            "clean employee master record",
        )
        await exec_query(
            text("DELETE FROM sch_iam.tb_user_profile WHERE user_id = ANY(:uids)"),
            {"uids": target_uids},
            "clean profiles",
        )

        print("Cleanup completed successfully.")

        # 4. Insert student and employee master records
        print("Inserting student and employee master records...")

        # Student Record
        stud_id = None
        stud_insert = await exec_query(
            text("""
                INSERT INTO sch_student.tb_stud (user_id, stud_no, current_status_id, is_active)
                VALUES (:user_id, 'STU-2026-0003', :status_id, true) RETURNING id
            """),
            {"user_id": student_uid, "status_id": active_status_id},
            "seed student master",
        )
        if stud_insert.get("status") == "success" and stud_insert.get("data"):
            stud_id = stud_insert["data"][0]["id"]

        # Employee Record
        emp_insert = await exec_query(
            text("""
                INSERT INTO sch_emp_fac.tb_emp (user_id, emp_code, status_id, is_active)
                VALUES (:user_id, 'EMP-2026-0002', :status_id, true) RETURNING id
            """),
            {"user_id": teacher_uid, "status_id": active_status_id},
            "seed employee master",
        )

        # 5. Insert personal details (sch_iam.tb_user_profile)
        print("Inserting personal details...")
        profiles = [
            {
                "user_id": admin_uid,
                "f_name": "Aditya",
                "m_name": "Raj",
                "l_name": "Malhotra",
                "dob": "1988-03-24",
                "gender_id": male_id,
                "mobile": "9876543210",
            },
            {
                "user_id": teacher_uid,
                "f_name": "Meera",
                "m_name": None,
                "l_name": "Sen",
                "dob": "1980-08-14",
                "gender_id": female_id,
                "mobile": "9876543211",
            },
            {
                "user_id": student_uid,
                "f_name": "Aman",
                "m_name": "Kumar",
                "l_name": "Sharma",
                "dob": "2003-05-15",
                "gender_id": male_id,
                "mobile": "9876543212",
            },
        ]

        for p in profiles:
            await exec_query(
                text("UPDATE sch_iam.tb_user SET mobile = :mobile WHERE id = :user_id"),
                {"mobile": p["mobile"], "user_id": p["user_id"]},
                f"update mobile {p['user_id']}",
            )
            await exec_query(
                text("""
                    INSERT INTO sch_iam.tb_user_profile 
                        (user_id, f_name, m_name, l_name, dob, gender_id, created_at, updated_at)
                    VALUES 
                        (:user_id, :f_name, :m_name, :l_name, :dob, :gender_id, NOW(), NOW())
                """),
                {
                    "user_id": p["user_id"],
                    "f_name": p["f_name"],
                    "m_name": p["m_name"],
                    "l_name": p["l_name"],
                    "dob": datetime.strptime(p["dob"], "%Y-%m-%d").date(),
                    "gender_id": p["gender_id"],
                },
                f"seed profile {p['user_id']}",
            )

        # 6. Insert academic identifiers (sch_iam.tb_user_identifier)
        print("Inserting academic identifiers...")
        identifiers = [
            {"user_id": student_uid, "type_id": 1, "value": "CARD-STU-0003"},
            {"user_id": student_uid, "type_id": 2, "value": "BIO-STU-0003"},
            {"user_id": teacher_uid, "type_id": 1, "value": "CARD-EMP-0002"},
            {"user_id": teacher_uid, "type_id": 2, "value": "BIO-EMP-0002"},
        ]
        for ident in identifiers:
            await exec_query(
                text("""
                    INSERT INTO sch_iam.tb_user_identifier (user_id, identifier_type_id, identifier_value, status_id)
                    VALUES (:user_id, :type_id, :value, :status_id)
                """),
                {
                    "user_id": ident["user_id"],
                    "type_id": ident["type_id"],
                    "value": ident["value"],
                    "status_id": active_status_id,
                },
                f"seed identifier {ident['user_id']}",
            )

        # 7. Insert family details (sch_parents.tb_par, sch_parents.tb_par_stud)
        if stud_id:
            print("Inserting family details...")
            parents = [
                {
                    "par_no": "PAR-2026-0001",
                    "first_name": "Ramesh",
                    "last_name": "Sharma",
                    "relation_id": father_id,
                    "mobile": "9900998877",
                    "email": "ramesh@parents.local",
                    "occupation": "Business",
                    "income": 1200000.0,
                    "is_primary": True,
                    "is_emergency": False,
                },
                {
                    "par_no": "PAR-2026-0002",
                    "first_name": "Kiran",
                    "last_name": "Sharma",
                    "relation_id": mother_id,
                    "mobile": "9900998878",
                    "email": "kiran@parents.local",
                    "occupation": "Teacher",
                    "income": 500000.0,
                    "is_primary": False,
                    "is_emergency": True,
                },
            ]

            for p in parents:
                par_res = await exec_query(
                    text("""
                        INSERT INTO sch_parents.tb_par 
                            (par_no, first_name, last_name, gender_id, mobile_no, email, occupation, annual_income, status_id)
                        VALUES 
                            (:par_no, :f_name, :l_name, :gender_id, :mobile, :email, :occupation, :income, :status_id)
                        RETURNING id
                    """),
                    {
                        "par_no": p["par_no"],
                        "f_name": p["first_name"],
                        "l_name": p["last_name"],
                        "gender_id": (
                            male_id if p["relation_id"] == father_id else female_id
                        ),
                        "mobile": p["mobile"],
                        "email": p["email"],
                        "occupation": p["occupation"],
                        "income": p["income"],
                        "status_id": active_status_id,
                    },
                    "seed parent profile",
                )

                if par_res.get("status") == "success" and par_res.get("data"):
                    par_id = par_res["data"][0]["id"]
                    await exec_query(
                        text("""
                            INSERT INTO sch_parents.tb_par_stud 
                                (stud_id, par_id, relationship_type_id, is_primary_guardian, is_emergency_contact)
                            VALUES 
                                (:stud_id, :par_id, :relation_id, :is_primary, :is_emergency)
                        """),
                        {
                            "stud_id": stud_id,
                            "par_id": par_id,
                            "relation_id": p["relation_id"],
                            "is_primary": p["is_primary"],
                            "is_emergency": p["is_emergency"],
                        },
                        "link parent to student",
                    )

        # 8. Insert emergency contacts (sch_iam.tb_user_emergency_contact)
        print("Inserting general emergency contacts...")
        emergency_contacts = [
            {
                "user_id": admin_uid,
                "f_name": "Rohan",
                "l_name": "Malhotra",
                "mobile": "9812345678",
                "is_primary": True,
            },
            {
                "user_id": teacher_uid,
                "f_name": "Suresh",
                "l_name": "Sen",
                "mobile": "9812345679",
                "is_primary": True,
            },
        ]
        for ec in emergency_contacts:
            await exec_query(
                text("""
                    INSERT INTO sch_iam.tb_user_emergency_contact (user_id, f_name, l_name, mobile, is_primary, status_id)
                    VALUES (:user_id, :f_name, :l_name, :mobile, :is_primary, :status_id)
                """),
                {
                    "user_id": ec["user_id"],
                    "f_name": ec["f_name"],
                    "l_name": ec["l_name"],
                    "mobile": ec["mobile"],
                    "is_primary": ec["is_primary"],
                    "status_id": active_status_id,
                },
                f"seed emergency contact {ec['user_id']}",
            )

        # 9. Insert medical details (sch_iam.tb_user_med)
        print("Inserting medical details...")
        extra_note_dict = {
            "medications": ["Asthalin Inhaler"],
            "doctorName": "Dr. S. K. Mehta",
            "doctorContact": "9822334455",
            "insurancePolicyNo": "POL-ONEAPP-99881",
        }
        await exec_query(
            text("""
                INSERT INTO sch_iam.tb_user_med 
                    (user_id, blood_group_id, allergy_info, med_condition, emergency_note)
                VALUES 
                    (:user_id, :blood_group_id, :allergies, :chronic_conditions, :emergency_note)
            """),
            {
                "user_id": student_uid,
                "blood_group_id": o_pos_id,
                "allergies": json.dumps(["Dust", "Pollen"]),
                "chronic_conditions": json.dumps(["Asthma"]),
                "emergency_note": json.dumps(extra_note_dict),
            },
            "seed medical details",
        )

        # 10. Insert user preferences (sch_iam.tb_user_preference)
        print("Inserting user preferences...")
        preferences = [
            {"user_id": student_uid, "pref_type_id": 1, "value": "en"},
            {"user_id": student_uid, "pref_type_id": 2, "value": "dark"},
            {"user_id": student_uid, "pref_type_id": 3, "value": "Asia/Kolkata"},
            {"user_id": student_uid, "pref_type_id": 4, "value": "m_student"},
            {"user_id": teacher_uid, "pref_type_id": 1, "value": "en"},
            {"user_id": teacher_uid, "pref_type_id": 2, "value": "light"},
            {"user_id": teacher_uid, "pref_type_id": 3, "value": "Asia/Kolkata"},
            {"user_id": teacher_uid, "pref_type_id": 4, "value": "m_teacher"},
        ]
        for pref in preferences:
            await exec_query(
                text("""
                    INSERT INTO sch_iam.tb_user_preference (user_id, preference_type_id, value, created_at, updated_at)
                    VALUES (:user_id, :pref_type_id, :value, NOW(), NOW())
                """),
                {
                    "user_id": pref["user_id"],
                    "pref_type_id": pref["pref_type_id"],
                    "value": pref["value"],
                },
                f"seed preference {pref['user_id']}:{pref['pref_type_id']}",
            )

        print("\nAll Profile Module data successfully seeded!")

    finally:
        await db.async_disconnectDB()


if __name__ == "__main__":
    asyncio.run(seed_profile_data())
