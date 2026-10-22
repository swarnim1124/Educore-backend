"""
File: compare_excel_db.py
Description: Compares database schemas/fields in the PostgreSQL cloud database
             against the master Excel specification (MASTER DATA MGMT - Jit.xlsx).
"""

import os
import sys
import asyncio
import openpyxl
from sqlalchemy import text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from xsc_lib.xsc_lib_common.xsc_libc_pgrs import PostgreSQLManager

# Map Excel sheets to DB schemas
SHEET_SCHEMA_MAP = {
    "SCH_IAM": "sch_iam",
    "SCH_CORE": "sch_core",
    "SCH_PARENTS": "sch_parents",
    "SCH_STUDENT": "sch_student",
    "SCH_EMP_FAC": "sch_emp_fac",
}


def parse_excel_specification(file_path):
    """
    Parses the Excel file and extracts tables, columns, and types.
    Returns: { schema: { table: { column: { 'key_type': str, 'type': str } } } }
    """
    wb = openpyxl.load_workbook(file_path, data_only=True)
    specs = {}

    for sheet_name, schema_name in SHEET_SCHEMA_MAP.items():
        if sheet_name not in wb.sheetnames:
            continue

        ws = wb[sheet_name]
        specs[schema_name] = {}
        current_table = None

        for r in range(1, ws.max_row + 1):
            t_name = ws.cell(row=r, column=1).value
            col_name = ws.cell(row=r, column=2).value
            key_type = ws.cell(row=r, column=3).value
            d_type = ws.cell(row=r, column=4).value

            if t_name and str(t_name).startswith("TB_"):
                current_table = str(t_name).lower()
                specs[schema_name][current_table] = {}

            if current_table and col_name:
                col_name_str = str(col_name).strip().lower()
                if (
                    col_name_str
                    and not col_name_str.startswith("column")
                    and col_name_str != ""
                ):
                    specs[schema_name][current_table][col_name_str] = {
                        "key_type": str(key_type).strip() if key_type else "",
                        "data_type": str(d_type).strip() if d_type else "",
                    }
    return specs


async def run_comparison():
    excel_path = r"local_docs/MASTER DATA MGMT - Jit.xlsx"
    if not os.path.exists(excel_path):
        print(f"Error: Excel specification not found at {excel_path}")
        return

    print("Parsing Excel database specification...")
    excel_specs = parse_excel_specification(excel_path)

    print("Connecting to cloud database...")
    db = PostgreSQLManager()
    conn_resp = await db.async_connectDB()
    if conn_resp["status"] == "error":
        print(f"Database connection failed: {conn_resp['message']}")
        return

    try:
        # Fetch DB schema metadata
        print("Querying database table & column metadata...\n")
        db_columns_query = text("""
            SELECT table_schema, table_name, column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = ANY(:schemas)
            ORDER BY table_schema, table_name, column_name
        """)
        schemas_list = list(SHEET_SCHEMA_MAP.values())
        res = await db.async_genericSQL(db_columns_query, {"schemas": schemas_list})

        if res["status"] != "success":
            print(
                f"Failed to retrieve column metadata: {res['message']} | DB Err: {db.errMsg}"
            )
            return

        # Parse DB metadata
        # { schema: { table: { column: data_type } } }
        db_specs = {}
        for r in res.get("data", []):
            schema = r["table_schema"].lower()
            table_name = r["table_name"].lower()
            column_name = r["column_name"].lower()
            d_type = r["data_type"].lower()
            max_len = r["character_maximum_length"]

            if max_len:
                d_type = f"{d_type}({max_len})"

            if schema not in db_specs:
                db_specs[schema] = {}
            if table_name not in db_specs[schema]:
                db_specs[schema][table_name] = {}

            db_specs[schema][table_name][column_name] = d_type

        # Perform comparison
        discrepancies_found = False

        for schema, tables in excel_specs.items():
            print(f"=== Comparing Schema: {schema.upper()} ===")
            if schema not in db_specs:
                print(f"  [MISSING SCHEMA] Schema '{schema}' does not exist in DB.")
                discrepancies_found = True
                continue

            for table, cols in tables.items():
                if table not in db_specs[schema]:
                    print(
                        f"  [MISSING TABLE] Table '{schema}.{table}' does not exist in DB."
                    )
                    discrepancies_found = True
                    continue

                # Compare columns
                db_cols = db_specs[schema][table]

                # Check for missing columns
                for col, specs in cols.items():
                    if col not in db_cols:
                        print(
                            f"    [MISSING COLUMN] Column '{col}' ({specs['data_type']}) is missing from table '{schema}.{table}' in DB."
                        )
                        discrepancies_found = True
                    else:
                        # Check type compatibility (basic comparison)
                        excel_type = specs["data_type"].lower()
                        db_type = db_cols[col].lower()

                        # Normalize type strings for comparisons
                        norm_excel = excel_type.replace(" ", "")
                        norm_db = db_type.replace(" ", "")

                        # Common normalization rules
                        type_maps = {
                            "charactervarying": "varchar",
                            "timestampwithtimezone": "timestampz",
                            "timestampwithouttimezone": "timestamp",
                            "doubleprecision": "float",
                            "integer": "int",
                        }
                        for k, v in type_maps.items():
                            norm_excel = norm_excel.replace(k, v)
                            norm_db = norm_db.replace(k, v)

                        # Compare compatibility
                        is_compatible = (
                            (norm_excel in norm_db)
                            or (norm_db in norm_excel)
                            or ("serial" in norm_excel and "int" in norm_db)
                            or ("numeric" in norm_excel and "numeric" in norm_db)
                            or ("text" in norm_excel and "text" in norm_db)
                            or ("bool" in norm_excel and "bool" in norm_db)
                            or ("date" in norm_excel and "date" in norm_db)
                        )

                        if not is_compatible:
                            print(
                                f"    [TYPE MISMATCH] Column '{schema}.{table}.{col}' has type '{db_type}' in DB, but Excel specifies '{excel_type}'."
                            )
                            discrepancies_found = True

                # Check for extra columns in DB not defined in Excel specs
                for db_col in db_cols.keys():
                    if db_col not in cols:
                        # Standard auditing cols might be extra in DB but aren't schema violations
                        if db_col not in [
                            "created_at",
                            "updated_at",
                            "created_on",
                            "updated_on",
                            "id",
                        ]:
                            print(
                                f"    [EXTRA COLUMN] Table '{schema}.{table}' has extra column '{db_col}' ({db_cols[db_col]}) in DB not defined in Excel."
                            )

        if not discrepancies_found:
            print(
                "\nCongratulations! All DB schemas and fields are perfectly aligned with the Excel specification."
            )
        else:
            print("\nComparison finished. Discrepancies were reported above.")

    finally:
        await db.async_disconnectDB()


if __name__ == "__main__":
    asyncio.run(run_comparison())
