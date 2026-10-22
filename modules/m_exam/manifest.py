"""
File: manifest.py
Description: Module Manifest for m_exam (Examinations & Results).

Author: EduCore
App: OneApp
"""

MODULE_NAME = "m_exam"
MODULE_VERSION = "1.0.0"
AUTHOR = "EduCore"
DESCRIPTION = "Examinations & Results module — scheduling, venues, hall tickets, question papers, internal/external marks, evaluation, result approval, revaluation, and malpractice cases."

DEPENDENCIES = ["m_AAA", "m_student", "m_profile"]

SUPPORTED_SUBMODULES = [
    "sm_exam_center",
    "sm_schedule",
    "sm_seating",
    "sm_invigilation",
    "sm_hall_ticket",
    "sm_question_paper",
    "sm_external_exam",
    "sm_internal_exam",
    "sm_marks",
    "sm_evaluation",
    "sm_results",
    "sm_result_approval",
    "sm_revaluation",
    "sm_supplementary",
    "sm_reappear",
    "sm_malpractice",
]

DATABASE_SCHEMAS = [
    "sch_exam",
    "sch_student",
    "sch_core",
    "sch_iam",
    "sch_parents",
    "sch_emp_fac",
]

PERMISSIONS = [
    "exam.examCenter.add",
    "exam.examCenter.view",
    "exam.examCenter.update",
    "exam.examCenter.delete",
    "exam.schedule.add",
    "exam.schedule.view",
    "exam.schedule.publish",
    "exam.seating.generate",
    "exam.invigilation.assign",
    "exam.hallTicket.generate",
    "exam.questionPaper.create",
    "exam.questionPaper.approve",
    "exam.marks.entry",
    "exam.marks.verify",
    "exam.results.generate",
    "exam.resultApproval.approve",
    "exam.resultApproval.publish",
    "exam.revaluation.request",
    "exam.malpractice.report",
]

FEATURE_FLAGS = {}
