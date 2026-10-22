"""
File: m_exam.py
Description: Dynamic BRS Gateway Router for m_exam (Examinations & Results).
             Uses an explicit contract map for submodules and actions.

Author: EduCore
App: OneApp
"""

import importlib
import asyncio

# Explicit BRS Contract Routing Map
ROUTES = {
    # 1. Exam Centre Management
    "sm_examCenter": (
        "m_exam_sm_exam_center",
        "ExamCenter",
        {"examCentre": "exam_center"},
    ),
    "sm_exam_center": (
        "m_exam_sm_exam_center",
        "ExamCenter",
        {"exam_center": "exam_center", "examCentre": "exam_center"},
    ),
    # 2. Exam Schedule Management
    "sm_schedule": (
        "m_exam_sm_schedule",
        "Schedule",
        {
            "examSchedule": "schedule",
            "schedule": "schedule",
            "examSchedulePublication": "exam_schedule_publication",
            "publication": "exam_schedule_publication",
        },
    ),
    # 3. Seating Plan Management
    "sm_seating": (
        "m_exam_sm_seating",
        "Seating",
        {"seatingPlan": "seating", "seating": "seating"},
    ),
    # 4. Invigilation Management
    "sm_invigilation": (
        "m_exam_sm_invigilation",
        "Invigilation",
        {"invigilatorAssignment": "invigilation", "invigilation": "invigilation"},
    ),
    # 5. Hall Ticket Management
    "sm_hallTicket": (
        "m_exam_sm_hall_ticket",
        "HallTicket",
        {
            "hallTicket": "hall_ticket",
            "hall_ticket": "hall_ticket",
            "hallTicketPublication": "hall_ticket_publication",
            "studentBlock": "student_block",
            "student_block": "student_block",
        },
    ),
    "sm_hall_ticket": (
        "m_exam_sm_hall_ticket",
        "HallTicket",
        {
            "hallTicket": "hall_ticket",
            "hall_ticket": "hall_ticket",
            "hallTicketPublication": "hall_ticket_publication",
            "studentBlock": "student_block",
            "student_block": "student_block",
        },
    ),
    # 6. Question Paper Management
    "sm_questionPaper": (
        "m_exam_sm_question_paper",
        "QuestionPaper",
        {
            "questionPaper": "question_paper",
            "question_paper": "question_paper",
            "questionPaperSubmission": "question_paper_submission",
            "questionPaperApproval": "question_paper_approval",
            "questionBank": "question_bank",
            "question_bank": "question_bank",
        },
    ),
    "sm_question_paper": (
        "m_exam_sm_question_paper",
        "QuestionPaper",
        {
            "questionPaper": "question_paper",
            "question_paper": "question_paper",
            "questionPaperSubmission": "question_paper_submission",
            "questionPaperApproval": "question_paper_approval",
            "questionBank": "question_bank",
            "question_bank": "question_bank",
        },
    ),
    # 7. External Examiner Management
    "sm_externalExam": (
        "m_exam_sm_external_exam",
        "ExternalExam",
        {
            "externalExaminer": "external_examiner",
            "external_examiner": "external_examiner",
            "external_exam": "external_exam",
            "externalPaperSetting": "external_paper_setting",
            "externalEvaluation": "external_evaluation",
        },
    ),
    "sm_external_exam": (
        "m_exam_sm_external_exam",
        "ExternalExam",
        {
            "externalExaminer": "external_examiner",
            "external_examiner": "external_examiner",
            "external_exam": "external_exam",
            "externalPaperSetting": "external_paper_setting",
            "externalEvaluation": "external_evaluation",
        },
    ),
    # 8. Internal Exam (CIE) Management
    "sm_internalExam": (
        "m_exam_sm_internal_exam",
        "InternalExam",
        {
            "internalExam": "internal_exam",
            "internal_exam": "internal_exam",
            "internalMarksEntry": "internal_marks_entry",
            "internalMarksConsolidation": "internal_marks_consolidation",
        },
    ),
    "sm_internal_exam": (
        "m_exam_sm_internal_exam",
        "InternalExam",
        {
            "internalExam": "internal_exam",
            "internal_exam": "internal_exam",
            "internalMarksEntry": "internal_marks_entry",
            "internalMarksConsolidation": "internal_marks_consolidation",
        },
    ),
    # 9. Marks & Grading Management
    "sm_marks": (
        "m_exam_sm_marks",
        "Marks",
        {
            "marksEntry": "marks_entry",
            "marks_entry": "marks_entry",
            "marks": "marks",
            "marksVerification": "marks_verification",
            "grade": "grade",
            "gradeLock": "grade_lock",
        },
    ),
    # 10. Evaluation & Moderation Management
    "sm_evaluation": (
        "m_exam_sm_evaluation",
        "Evaluation",
        {
            "evaluationBundle": "evaluation_bundle",
            "evaluation_bundle": "evaluation_bundle",
            "evaluation": "evaluation",
            "secondValuation": "second_valuation",
            "moderation": "moderation",
        },
    ),
    # 11. Result Generation
    "sm_results": (
        "m_exam_sm_results",
        "Results",
        {"result": "result", "results": "results"},
    ),
    # 12. Result Approval & Publication
    "sm_resultApproval": (
        "m_exam_sm_result_approval",
        "ResultApproval",
        {
            "resultApproval": "result_approval",
            "result_approval": "result_approval",
            "resultPublication": "result_publication",
        },
    ),
    "sm_result_approval": (
        "m_exam_sm_result_approval",
        "ResultApproval",
        {
            "resultApproval": "result_approval",
            "result_approval": "result_approval",
            "resultPublication": "result_publication",
        },
    ),
    # 13. Revaluation, Photocopy & Appeal
    "sm_revaluation": (
        "m_exam_sm_revaluation",
        "Revaluation",
        {
            "revaluationRequest": "revaluation_request",
            "revaluation_request": "revaluation_request",
            "revaluation": "revaluation",
            "revaluationProcessing": "revaluation_processing",
            "photocopyRequest": "photocopy_request",
            "appeal": "appeal",
            "challengeRevaluation": "challenge_revaluation",
        },
    ),
    # 14. Supplementary Exam Management
    "sm_supplementary": (
        "m_exam_sm_supplementary",
        "Supplementary",
        {
            "supplementaryExam": "supplementary_exam",
            "supplementary_exam": "supplementary_exam",
            "supplementary": "supplementary",
            "supplementaryRegistration": "supplementary_registration",
        },
    ),
    # 15. Reappear / Improvement Exam Management
    "sm_reappear": (
        "m_exam_sm_reappear",
        "Reappear",
        {
            "reappearExam": "reappear_exam",
            "reappear_exam": "reappear_exam",
            "reappear": "reappear",
            "reappearRegistration": "reappear_registration",
            "reappearEligibility": "reappear_eligibility",
        },
    ),
    # 16. Malpractice Case Management
    "sm_malpractice": (
        "m_exam_sm_malpractice",
        "Malpractice",
        {
            "malpracticeCase": "malpractice_case",
            "malpractice_case": "malpractice_case",
            "malpractice": "malpractice",
        },
    ),
}


class Exam:
    """
    Gateway Entry Point Router for m_exam.
    Enforces strict BRS contract mapping and returns structured responses.
    """

    def __call__(self, req_json_obj, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        sub_mod = req_json_obj.get("subMod") or req_json_obj.get("submod")
        action = req_json_obj.get("action")
        action_type = req_json_obj.get("actionType")

        if not sub_mod or not action or not action_type:
            return XSCUtility.error_response(
                message="Missing required parameters: 'subMod', 'action', or 'actionType'",
                error_code="400",
            )

        # 1. Resolve in Contract Map
        route = ROUTES.get(sub_mod)
        if not route:
            # Fallback normalization check
            clean_sub = sub_mod if sub_mod.startswith("sm_") else f"sm_{sub_mod}"
            route = ROUTES.get(clean_sub)

        if not route:
            return XSCUtility.error_response(
                message=f"Unsupported BRS submodule '{sub_mod}'", error_code="400"
            )

        module_filename, class_name, action_map = route
        method_name = action_map.get(action) or action

        try:
            # 2. Import Module & Instantiate Class
            module_path = f".{module_filename}"
            module = importlib.import_module(module_path, package=__package__)
            module_class = getattr(module, class_name, None)

            if not module_class:
                return XSCUtility.error_response(
                    message=f"Handler class '{class_name}' not found for '{sub_mod}'",
                    error_code="500",
                )

            instance = module_class()
            action_func = getattr(instance, method_name, None) or getattr(
                instance, action, None
            )

            if not action_func:
                return XSCUtility.error_response(
                    message=f"Action method '{method_name}' not found on handler class '{class_name}'",
                    error_code="400",
                )

            # 3. Dispatch Execution
            payload = (
                req_json_obj.get("payload", {})
                if isinstance(req_json_obj, dict)
                else getattr(req_json_obj, "payload", {})
            )

            if asyncio.iscoroutinefunction(action_func):
                result = asyncio.run(action_func(action_type, payload, context))
            else:
                result = action_func(action_type, payload, context)

            return result

        except ImportError as e:
            return XSCUtility.error_response(
                message=f"Submodule import failure for '{sub_mod}': {str(e)}",
                error_code="500",
            )
        except Exception as e:
            return XSCUtility.error_response(
                message=f"Execution error in m_exam handler: {str(e)}", error_code="500"
            )
