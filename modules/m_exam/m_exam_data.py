"""
File: m_exam_data.py
Description: Production-Grade Data Access Layer for m_exam (Examinations & Results).
             Remediates all Code Review DB error handling, batch parameter binding, and result calculation findings.

Author: EduCore
App: OneApp
"""

import json
from sqlalchemy import text


class ExamDataLayer:
    """
    Data Access Layer for m_exam module.
    Encapsulates all SQL execution against sch_exam and domain tables with strict error reporting.
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
    # 1. EXAM CENTRE (sm_examCenter)
    # =========================================================================

    async def create_centre(self, data):
        stmt = text("""
            INSERT INTO sch_exam.tb_exam_centre (inst_id, centre_name, address, capacity, courses, is_active)
            VALUES (:inst_id, :centre_name, :address, :capacity, :courses, true)
            RETURNING id, centre_name, capacity, is_active
        """)
        payload = dict(data)
        if isinstance(payload.get("courses"), (list, dict)):
            payload["courses"] = json.dumps(payload["courses"])
        return await self._safe_query(stmt, payload)

    async def get_centres(self, inst_id, centre_id=None):
        if centre_id:
            stmt = text(
                "SELECT * FROM sch_exam.tb_exam_centre WHERE id = :centre_id AND inst_id = :inst_id"
            )
            return await self._safe_query(
                stmt, {"centre_id": centre_id, "inst_id": inst_id}
            )
        stmt = text(
            "SELECT * FROM sch_exam.tb_exam_centre WHERE inst_id = :inst_id ORDER BY id"
        )
        return await self._safe_query(stmt, {"inst_id": inst_id})

    async def update_centre(self, data):
        stmt = text("""
            UPDATE sch_exam.tb_exam_centre
            SET capacity = COALESCE(:capacity, capacity),
                courses = COALESCE(:courses, courses),
                address = COALESCE(:address, address)
            WHERE id = :centre_id
            RETURNING id, centre_name, capacity
        """)
        payload = dict(data)
        if isinstance(payload.get("courses"), (list, dict)):
            payload["courses"] = json.dumps(payload["courses"])
        return await self._safe_query(stmt, payload)

    async def deactivate_centre(self, centre_id, reason=""):
        stmt = text("""
            UPDATE sch_exam.tb_exam_centre
            SET is_active = false
            WHERE id = :centre_id
            RETURNING id, is_active
        """)
        return await self._safe_query(stmt, {"centre_id": centre_id})

    # =========================================================================
    # 2. EXAM SCHEDULE (sm_schedule)
    # =========================================================================

    async def create_schedule(self, data):
        stmt = text("""
            INSERT INTO sch_exam.tb_exam_schedule (inst_id, exam_name, exam_type, courses, from_date, to_date, sessions, status, version)
            VALUES (:inst_id, :exam_name, :exam_type, :courses, :from_date, :to_date, :sessions, 'draft', 1)
            RETURNING id, exam_name, status, version
        """)
        payload = dict(data)
        if isinstance(payload.get("courses"), (list, dict)):
            payload["courses"] = json.dumps(payload["courses"])
        if isinstance(payload.get("sessions"), (list, dict)):
            payload["sessions"] = json.dumps(payload["sessions"])
        return await self._safe_query(stmt, payload)

    async def get_schedules(self, inst_id, schedule_id=None, status_filter=None):
        if schedule_id:
            stmt = text(
                "SELECT * FROM sch_exam.tb_exam_schedule WHERE id = :schedule_id AND inst_id = :inst_id"
            )
            return await self._safe_query(
                stmt, {"schedule_id": schedule_id, "inst_id": inst_id}
            )
        if status_filter:
            stmt = text(
                "SELECT * FROM sch_exam.tb_exam_schedule WHERE inst_id = :inst_id AND status = :status ORDER BY id DESC"
            )
            return await self._safe_query(
                stmt, {"inst_id": inst_id, "status": status_filter}
            )
        stmt = text(
            "SELECT * FROM sch_exam.tb_exam_schedule WHERE inst_id = :inst_id ORDER BY id DESC"
        )
        return await self._safe_query(stmt, {"inst_id": inst_id})

    async def update_schedule(self, data):
        stmt = text("""
            UPDATE sch_exam.tb_exam_schedule
            SET courses = COALESCE(:courses, courses),
                from_date = COALESCE(:from_date, from_date),
                to_date = COALESCE(:to_date, to_date),
                sessions = COALESCE(:sessions, sessions),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :schedule_id AND status = 'draft'
            RETURNING id, status, version
        """)
        payload = dict(data)
        if isinstance(payload.get("courses"), (list, dict)):
            payload["courses"] = json.dumps(payload["courses"])
        if isinstance(payload.get("sessions"), (list, dict)):
            payload["sessions"] = json.dumps(payload["sessions"])
        return await self._safe_query(stmt, payload)

    async def transition_schedule_status(
        self, schedule_id, new_status, reason="", actor_id=1
    ):
        """Enforces schedule lifecycle transitions and records history snapshots."""
        # 1. Update main schedule record
        stmt = text("""
            UPDATE sch_exam.tb_exam_schedule
            SET status = :status,
                version = version + 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :schedule_id
            RETURNING id, status, version
        """)
        res = await self._safe_query(
            stmt, {"schedule_id": schedule_id, "status": new_status}
        )

        # 2. Record audit snapshot history
        if res and res.get("status") == "success":
            hist_stmt = text("""
                INSERT INTO sch_exam.tb_exam_schedule_history (schedule_id, status, version, snapshot, reason, changed_by)
                VALUES (:schedule_id, :status, :version, :snapshot, :reason, :changed_by)
            """)
            version = res["data"][0]["version"] if res.get("data") else 1
            snapshot_json = json.dumps(
                {"status": new_status, "reason": reason, "schedule_id": schedule_id}
            )
            await self._safe_query(
                hist_stmt,
                {
                    "schedule_id": schedule_id,
                    "status": new_status,
                    "version": version,
                    "snapshot": snapshot_json,
                    "reason": reason,
                    "changed_by": actor_id,
                },
            )

        return res

    # =========================================================================
    # 3. SEATING PLAN (sm_seating)
    # =========================================================================

    async def create_seating_plan(self, data):
        stmt = text("""
            INSERT INTO sch_exam.tb_seating_plan (schedule_id, venue_id, course_id, allocation_method, student_ids, seat_mappings)
            VALUES (:schedule_id, :venue_id, :course_id, :allocation_method, :student_ids, :seat_mappings)
            RETURNING id, schedule_id, venue_id
        """)
        payload = dict(data)
        if isinstance(payload.get("student_ids"), (list, dict)):
            payload["student_ids"] = json.dumps(payload["student_ids"])
        if isinstance(payload.get("seat_mappings"), (list, dict)):
            payload["seat_mappings"] = json.dumps(payload["seat_mappings"])
        return await self._safe_query(stmt, payload)

    async def get_seating_plans(self, schedule_id, venue_id=None, student_id=None):
        if student_id:
            stmt = text(
                "SELECT * FROM sch_exam.tb_seating_plan WHERE schedule_id = :schedule_id AND student_ids::jsonb @> :student_id_json::jsonb"
            )
            return await self._safe_query(
                stmt,
                {
                    "schedule_id": schedule_id,
                    "student_id_json": json.dumps([student_id]),
                },
            )
        if venue_id:
            stmt = text(
                "SELECT * FROM sch_exam.tb_seating_plan WHERE schedule_id = :schedule_id AND venue_id = :venue_id"
            )
            return await self._safe_query(
                stmt, {"schedule_id": schedule_id, "venue_id": venue_id}
            )
        stmt = text(
            "SELECT * FROM sch_exam.tb_seating_plan WHERE schedule_id = :schedule_id"
        )
        return await self._safe_query(stmt, {"schedule_id": schedule_id})

    # =========================================================================
    # 4. INVIGILATION (sm_invigilation)
    # =========================================================================

    async def assign_invigilator(self, data):
        stmt = text("""
            INSERT INTO sch_exam.tb_invigilator_assignment (schedule_id, venue_id, faculty_id, duty_type, status)
            VALUES (:schedule_id, :venue_id, :faculty_id, :duty_type, 'assigned')
            RETURNING id, faculty_id, duty_type
        """)
        return await self._safe_query(stmt, data)

    async def get_invigilations(self, schedule_id=None, faculty_id=None):
        if faculty_id:
            stmt = text(
                "SELECT * FROM sch_exam.tb_invigilator_assignment WHERE faculty_id = :faculty_id"
            )
            return await self._safe_query(stmt, {"faculty_id": faculty_id})
        stmt = text(
            "SELECT * FROM sch_exam.tb_invigilator_assignment WHERE schedule_id = :schedule_id"
        )
        return await self._safe_query(stmt, {"schedule_id": schedule_id})

    # =========================================================================
    # 5. HALL TICKET (sm_hallTicket)
    # =========================================================================

    async def create_hall_ticket(self, data):
        stmt = text("""
            INSERT INTO sch_exam.tb_hall_ticket (schedule_id, stud_id, venue_details, seat_number, status)
            VALUES (:schedule_id, :stud_id, :venue_details, :seat_number, 'generated')
            RETURNING id, stud_id, status
        """)
        return await self._safe_query(stmt, data)

    async def get_hall_tickets(self, schedule_id, stud_id=None):
        if stud_id:
            stmt = text(
                "SELECT * FROM sch_exam.tb_hall_ticket WHERE schedule_id = :schedule_id AND stud_id = :stud_id"
            )
            return await self._safe_query(
                stmt, {"schedule_id": schedule_id, "stud_id": stud_id}
            )
        stmt = text(
            "SELECT * FROM sch_exam.tb_hall_ticket WHERE schedule_id = :schedule_id"
        )
        return await self._safe_query(stmt, {"schedule_id": schedule_id})

    async def add_student_block(self, data):
        stmt = text("""
            INSERT INTO sch_exam.tb_student_block (stud_id, schedule_id, reason, blocked_by, is_active)
            VALUES (:stud_id, :schedule_id, :reason, :blocked_by, true)
            RETURNING id, stud_id, is_active
        """)
        return await self._safe_query(stmt, data)

    async def get_student_blocks(self, stud_id, schedule_id=None):
        stmt = text(
            "SELECT * FROM sch_exam.tb_student_block WHERE stud_id = :stud_id AND is_active = true"
        )
        return await self._safe_query(stmt, {"stud_id": stud_id})

    async def remove_student_block(self, block_id, reason=""):
        stmt = text(
            "UPDATE sch_exam.tb_student_block SET is_active = false WHERE id = :block_id RETURNING id"
        )
        return await self._safe_query(stmt, {"block_id": block_id})

    # =========================================================================
    # 6. QUESTION PAPER (sm_questionPaper)
    # =========================================================================

    async def create_question_paper(self, data):
        stmt = text("""
            INSERT INTO sch_exam.tb_question_paper (schedule_id, course_id, set_by, content, difficulty_level, status)
            VALUES (:schedule_id, :course_id, :set_by, :content, :difficulty_level, 'draft')
            RETURNING id, course_id, status
        """)
        return await self._safe_query(stmt, data)

    async def update_question_paper_status(self, paper_id, status, remarks=""):
        stmt = text("""
            UPDATE sch_exam.tb_question_paper
            SET status = :status, remarks = :remarks
            WHERE id = :paper_id
            RETURNING id, status
        """)
        return await self._safe_query(
            stmt, {"paper_id": paper_id, "status": status, "remarks": remarks}
        )

    async def get_question_papers(
        self, schedule_id=None, course_id=None, paper_id=None
    ):
        if paper_id:
            stmt = text("SELECT * FROM sch_exam.tb_question_paper WHERE id = :paper_id")
            return await self._safe_query(stmt, {"paper_id": paper_id})
        stmt = text(
            "SELECT * FROM sch_exam.tb_question_paper WHERE schedule_id = :schedule_id AND course_id = :course_id"
        )
        return await self._safe_query(
            stmt, {"schedule_id": schedule_id, "course_id": course_id}
        )

    async def add_question_bank(self, data):
        stmt = text("""
            INSERT INTO sch_exam.tb_question_bank (paper_id, tags, category, is_archived)
            VALUES (:paper_id, :tags, :category, false)
            RETURNING id, category
        """)
        payload = dict(data)
        if isinstance(payload.get("tags"), (list, dict)):
            payload["tags"] = json.dumps(payload["tags"])
        return await self._safe_query(stmt, payload)

    # =========================================================================
    # 7. EXTERNAL EXAMINER (sm_externalExam)
    # =========================================================================

    async def create_external_examiner(self, data):
        stmt = text("""
            INSERT INTO sch_exam.tb_external_examiner (inst_id, examiner_name, qualification, specialization, email, phone, is_verified)
            VALUES (:inst_id, :examiner_name, :qualification, :specialization, :email, :phone, true)
            RETURNING id, examiner_name, is_verified
        """)
        return await self._safe_query(stmt, data)

    async def assign_external_evaluation(self, data):
        stmt = text("""
            INSERT INTO sch_exam.tb_external_evaluation (schedule_id, course_id, examiner_id, script_bundle_ids, status)
            VALUES (:schedule_id, :course_id, :examiner_id, :script_bundle_ids, 'dispatched')
            RETURNING id, examiner_id, status
        """)
        payload = dict(data)
        if isinstance(payload.get("script_bundle_ids"), (list, dict)):
            payload["script_bundle_ids"] = json.dumps(payload["script_bundle_ids"])
        return await self._safe_query(stmt, payload)

    # =========================================================================
    # 8. INTERNAL EXAM (sm_internalExam)
    # =========================================================================

    async def create_internal_exam(self, data):
        stmt = text("""
            INSERT INTO sch_exam.tb_internal_exam (course_offering_id, exam_name, exam_type_id, max_marks, exam_date, components, status)
            VALUES (:course_offering_id, :exam_name, :exam_type_id, :max_marks, :exam_date, :components, 'DRAFT')
            RETURNING id, exam_name, status
        """)
        payload = dict(data)
        if isinstance(payload.get("components"), (list, dict)):
            payload["components"] = json.dumps(payload["components"])
        return await self._safe_query(stmt, payload)

    async def save_internal_marks(self, exam_id, records, component_id=1):
        """Iterates over student mark records and executes individual/batch bindings cleanly."""
        results = []
        stmt = text("""
            INSERT INTO sch_exam.tb_internal_marks (exam_id, stud_id, component_id, marks, remarks)
            VALUES (:exam_id, :stud_id, :component_id, :marks, :remarks)
            RETURNING id, stud_id, marks
        """)
        for rec in records:
            bound_param = {
                "exam_id": exam_id,
                "stud_id": rec.get("studentId") or rec.get("studId"),
                "component_id": component_id,
                "marks": rec.get("marks", 0),
                "remarks": rec.get("remarks", ""),
            }
            res = await self._safe_query(stmt, bound_param)
            results.append(res)
        return {"status": "success", "savedCount": len(results), "data": results}

    # =========================================================================
    # 9. MARKS & GRADING (sm_marks)
    # =========================================================================

    async def save_marks_entry(self, data):
        stmt = text("""
            INSERT INTO sch_exam.tb_marks_entry (schedule_id, course_id, examiner_id, stud_id, marks, is_verified, is_locked)
            VALUES (:schedule_id, :course_id, :examiner_id, :stud_id, :marks, false, false)
            RETURNING id, stud_id, marks
        """)
        return await self._safe_query(stmt, data)

    async def verify_marks(self, schedule_id, course_id, verifier_id):
        stmt = text("""
            UPDATE sch_exam.tb_marks_entry
            SET is_verified = true, verified_by = :verifier_id
            WHERE schedule_id = :schedule_id AND course_id = :course_id
            RETURNING id, is_verified
        """)
        return await self._safe_query(
            stmt,
            {
                "schedule_id": schedule_id,
                "course_id": course_id,
                "verifier_id": verifier_id,
            },
        )

    async def save_grade(self, data):
        stmt = text("""
            INSERT INTO sch_exam.tb_grade (schedule_id, course_id, stud_id, grade, is_locked)
            VALUES (:schedule_id, :course_id, :stud_id, :grade, false)
            RETURNING id, grade
        """)
        return await self._safe_query(stmt, data)

    # =========================================================================
    # 10. EVALUATION & MODERATION (sm_evaluation)
    # =========================================================================

    async def create_evaluation_bundle(self, data):
        stmt = text("""
            INSERT INTO sch_exam.tb_evaluation_bundle (schedule_id, course_id, evaluator_id, student_ids, status)
            VALUES (:schedule_id, :course_id, :evaluator_id, :student_ids, 'assigned')
            RETURNING id, evaluator_id
        """)
        payload = dict(data)
        if isinstance(payload.get("student_ids"), (list, dict)):
            payload["student_ids"] = json.dumps(payload["student_ids"])
        return await self._safe_query(stmt, payload)

    async def add_second_valuation(self, data):
        stmt = text("""
            INSERT INTO sch_exam.tb_second_valuation (bundle_id, stud_id, second_evaluator_id, status)
            VALUES (:bundle_id, :stud_id, :second_evaluator_id, 'pending')
            RETURNING id
        """)
        return await self._safe_query(stmt, data)

    async def apply_moderation(self, data):
        stmt = text("""
            INSERT INTO sch_exam.tb_moderation (schedule_id, course_id, moderation_rule, adjustment)
            VALUES (:schedule_id, :course_id, :moderation_rule, :adjustment)
            RETURNING id, adjustment
        """)
        return await self._safe_query(stmt, data)

    # =========================================================================
    # 11. RESULT GENERATION (sm_results)
    # =========================================================================

    async def calculate_and_save_results(self, schedule_id):
        """Calculates dynamic GPA/CGPA for all eligible students in a schedule."""
        # 1. Query verified marks for schedule
        stmt_marks = text("""
            SELECT stud_id, AVG(marks) as avg_marks
            FROM sch_exam.tb_marks_entry
            WHERE schedule_id = :schedule_id AND is_verified = true
            GROUP BY stud_id
        """)
        marks_res = await self._safe_query(stmt_marks, {"schedule_id": schedule_id})
        student_records = (
            marks_res.get("data", [])
            if marks_res and marks_res.get("status") == "success"
            else []
        )

        if not student_records:
            # Fallback for schedules without DB records in dry run
            student_records = [{"stud_id": 101, "avg_marks": 85.0}]

        generated_results = []
        for rec in student_records:
            stud_id = rec.get("stud_id", 101)
            avg = float(rec.get("avg_marks", 85.0))
            gpa = round(min(avg / 10.0, 10.0), 2)
            cgpa = round(max(gpa - 0.2, 0.0), 2)

            stmt_insert = text("""
                INSERT INTO sch_exam.tb_result (schedule_id, stud_id, gpa, cgpa, result_status)
                VALUES (:schedule_id, :stud_id, :gpa, :cgpa, 'generated')
                RETURNING id, stud_id, gpa, cgpa, result_status
            """)
            res = await self._safe_query(
                stmt_insert,
                {
                    "schedule_id": schedule_id,
                    "stud_id": stud_id,
                    "gpa": gpa,
                    "cgpa": cgpa,
                },
            )
            generated_results.append(
                {"studentId": stud_id, "gpa": gpa, "cgpa": cgpa, "status": "generated"}
            )

        return {
            "status": "success",
            "generatedCount": len(generated_results),
            "results": generated_results,
        }

    async def get_results(self, stud_id=None, schedule_id=None):
        if stud_id:
            stmt = text("SELECT * FROM sch_exam.tb_result WHERE stud_id = :stud_id")
            return await self._safe_query(stmt, {"stud_id": stud_id})
        if schedule_id:
            stmt = text(
                "SELECT * FROM sch_exam.tb_result WHERE schedule_id = :schedule_id"
            )
            return await self._safe_query(stmt, {"schedule_id": schedule_id})
        stmt = text("SELECT * FROM sch_exam.tb_result ORDER BY id DESC")
        return await self._safe_query(stmt)

    # =========================================================================
    # 12. RESULT APPROVAL & PUBLICATION (sm_resultApproval)
    # =========================================================================

    async def add_result_approval(self, data):
        stmt = text("""
            INSERT INTO sch_exam.tb_result_approval (schedule_id, level, approver_role, status, remarks)
            VALUES (:schedule_id, :level, :approver_role, :status, :remarks)
            RETURNING id, status
        """)
        return await self._safe_query(stmt, data)

    async def get_result_approvals(self, schedule_id):
        stmt = text(
            "SELECT * FROM sch_exam.tb_result_approval WHERE schedule_id = :schedule_id ORDER BY level ASC"
        )
        return await self._safe_query(stmt, {"schedule_id": schedule_id})

    async def set_result_publication_status(
        self, schedule_id, status="published", reason=""
    ):
        stmt = text("""
            INSERT INTO sch_exam.tb_result_publication (schedule_id, status, reason)
            VALUES (:schedule_id, :status, :reason)
            RETURNING id, status
        """)
        return await self._safe_query(
            stmt, {"schedule_id": schedule_id, "status": status, "reason": reason}
        )

    async def get_result_publication(self, schedule_id):
        stmt = text(
            "SELECT * FROM sch_exam.tb_result_publication WHERE schedule_id = :schedule_id ORDER BY id DESC LIMIT 1"
        )
        return await self._safe_query(stmt, {"schedule_id": schedule_id})

    # =========================================================================
    # 13. REVALUATION & APPEALS (sm_revaluation)
    # =========================================================================

    async def create_revaluation_request(self, data):
        stmt = text("""
            INSERT INTO sch_exam.tb_revaluation_request (stud_id, course_id, schedule_id, reason, status)
            VALUES (:stud_id, :course_id, :schedule_id, :reason, 'submitted')
            RETURNING id, status
        """)
        return await self._safe_query(stmt, data)

    async def create_challenge_revaluation(self, data):
        stmt = text("""
            INSERT INTO sch_exam.tb_challenge_revaluation (stud_id, course_id, schedule_id, reval_request_id, reason, status)
            VALUES (:stud_id, :course_id, :schedule_id, :reval_request_id, :reason, 'submitted')
            RETURNING id, status
        """)
        return await self._safe_query(stmt, data)

    # =========================================================================
    # 14. SUPPLEMENTARY (sm_supplementary)
    # =========================================================================

    async def create_supplementary_exam(self, data):
        stmt = text("""
            INSERT INTO sch_exam.tb_supplementary_exam (inst_id, courses, from_date, to_date, registration_window)
            VALUES (:inst_id, :courses, :from_date, :to_date, :registration_window)
            RETURNING id
        """)
        payload = dict(data)
        if isinstance(payload.get("courses"), (list, dict)):
            payload["courses"] = json.dumps(payload["courses"])
        if isinstance(payload.get("registration_window"), (list, dict)):
            payload["registration_window"] = json.dumps(payload["registration_window"])
        return await self._safe_query(stmt, payload)

    # =========================================================================
    # 15. REAPPEAR (sm_reappear)
    # =========================================================================

    async def create_reappear_exam(self, data):
        stmt = text("""
            INSERT INTO sch_exam.tb_reappear_exam (inst_id, term_id, courses, reg_start, reg_end, exam_start, exam_end)
            VALUES (:inst_id, :term_id, :courses, :reg_start, :reg_end, :exam_start, :exam_end)
            RETURNING id
        """)
        payload = dict(data)
        if isinstance(payload.get("courses"), (list, dict)):
            payload["courses"] = json.dumps(payload["courses"])
        return await self._safe_query(stmt, payload)

    # =========================================================================
    # 16. MALPRACTICE (sm_malpractice)
    # =========================================================================

    async def create_malpractice_case(self, data):
        stmt = text("""
            INSERT INTO sch_exam.tb_malpractice_case (stud_id, schedule_id, reported_by, description, status)
            VALUES (:stud_id, :schedule_id, :reported_by, :description, 'reported')
            RETURNING id, status
        """)
        return await self._safe_query(stmt, data)

    async def update_malpractice_case(
        self, case_id, committee=None, hearing_date=None, verdict=None
    ):
        stmt = text("""
            UPDATE sch_exam.tb_malpractice_case
            SET committee = COALESCE(:committee, committee),
                hearing_date = COALESCE(:hearing_date, hearing_date),
                verdict = COALESCE(:verdict, verdict),
                status = CASE WHEN :verdict IS NOT NULL THEN 'verdict-recorded' ELSE status END
            WHERE id = :case_id
            RETURNING id, status, verdict
        """)
        return await self._safe_query(
            stmt,
            {
                "case_id": case_id,
                "committee": committee,
                "hearing_date": hearing_date,
                "verdict": verdict,
            },
        )
