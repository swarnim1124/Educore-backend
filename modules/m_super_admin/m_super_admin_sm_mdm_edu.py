"""
File: m_super_admin_sm_mdm_edu.py
Description: Submodule for Educational MDM (Master Data Management) in Super Admin.

Author: Akshay Basutkar, Siddharth Admal, Swarnim Deshpande
App: OneApp

"""

from pathlib import Path

MODULES_ROOT = Path(__file__).resolve().parents[1]


class MdmEdu:
    """
    Single submodule class handling educational MDM operations (Colleges).
    """

    async def mdm_edu(self, action_type, payload, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        action_type = (action_type or "").lower()

        match action_type:
            case "health":
                return self.health(payload, context)
            case "read":
                return self.read(payload, context)
            case "search":
                return self.search(payload, context)
            case "create":
                return self.create(payload, context)
            case "update":
                return self.update(payload, context)
            case "delete":
                return self.delete(payload, context)
            case _:
                return XSCUtility.error_response(
                    message=f"Unsupported actionType '{action_type}' for mdm_edu"
                )

    # --- Public Action Handlers ---

    def health(self, payload, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        return XSCUtility.success_response(message="", health="good")

    def read(self, payload, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from db import get_connection
        from psycopg.rows import dict_row

        page_no = max(int(payload.get("page_no", 1)), 1)
        items_per_page = max(int(payload.get("items_per_page", 20)), 1)

        offset = (page_no - 1) * items_per_page

        query = """
            SELECT
                id,
                college_name,
                short_form,
                website,
                year_founded,
                university_type,
                type_of_college,
                college_tier
            FROM colleges
            ORDER BY id
            LIMIT %s
            OFFSET %s;
        """

        count_query = """
            SELECT COUNT(*) AS total_records
            FROM colleges;
        """

        try:
            with get_connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(count_query)
                    total_records = cur.fetchone()["total_records"]

                    cur.execute(query, (items_per_page, offset))
                    colleges = cur.fetchall()

            total_pages = (total_records + items_per_page - 1) // items_per_page

            return XSCUtility.success_response(
                message="",
                data=colleges,
                pagination={
                    "page_no": page_no,
                    "items_per_page": items_per_page,
                    "total_records": total_records,
                    "total_pages": total_pages,
                    "has_next": page_no < total_pages,
                    "has_previous": page_no > 1,
                },
            )

        except Exception as e:
            return XSCUtility.error_response(message=str(e))

    def search(self, payload, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from db import get_connection
        from psycopg.rows import dict_row

        search_text = payload.get("search")
        if not search_text:
            return XSCUtility.error_response(message="'search' is required")

        query = """
            SELECT
                id,
                college_name,
                short_form,
                website,
                year_founded,
                university_type,
                type_of_college,
                college_tier
            FROM colleges
            WHERE college_name ILIKE %s
            ORDER BY college_name;
        """

        try:
            with get_connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(query, (f"%{search_text}%",))
                    colleges = cur.fetchall()

            return XSCUtility.success_response(message="", data=colleges)

        except Exception as e:
            return XSCUtility.error_response(message=str(e))

    def create(self, payload, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from db import get_connection
        from psycopg.rows import dict_row

        query = """
            INSERT INTO colleges (
                college_name,
                short_form,
                website,
                year_founded,
                university_type,
                type_of_college,
                college_tier
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """

        values = (
            payload.get("college_name"),
            payload.get("short_form"),
            payload.get("website"),
            payload.get("year_founded"),
            payload.get("university_type"),
            payload.get("type_of_college"),
            payload.get("college_tier"),
        )

        try:
            with get_connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(query, values)
                    college = cur.fetchone()
                conn.commit()

            return XSCUtility.success_response(
                message="College created successfully.", data=college
            )

        except Exception as e:
            return XSCUtility.error_response(message=str(e))

    def update(self, payload, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from db import get_connection

        query = """
            UPDATE colleges
            SET
                college_name = %s,
                short_form = %s,
                website = %s,
                year_founded = %s,
                university_type = %s,
                type_of_college = %s,
                college_tier = %s
            WHERE id = %s;
        """

        values = (
            payload.get("college_name"),
            payload.get("short_form"),
            payload.get("website"),
            payload.get("year_founded"),
            payload.get("university_type"),
            payload.get("type_of_college"),
            payload.get("college_tier"),
            payload.get("id"),
        )

        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, values)
                conn.commit()

            return XSCUtility.success_response(message="College updated successfully.")

        except Exception as e:
            return XSCUtility.error_response(message=str(e))

    def delete(self, payload, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from db import get_connection

        college_id = payload.get("id")

        if college_id is None:
            return XSCUtility.error_response(message="'id' is required")

        query = """
            DELETE FROM colleges
            WHERE id = %s;
        """

        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (college_id,))
                    if cur.rowcount == 0:
                        return XSCUtility.error_response(message="College not found.")
                conn.commit()

            return XSCUtility.success_response(message="College deleted successfully.")

        except Exception as e:
            return XSCUtility.error_response(message=str(e))


# Class name aliases for ActionDispatcher resolution
sm_mdm_edu = MdmEdu
