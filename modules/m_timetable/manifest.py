"""
File: manifest.py
Description: Module Manifest for m_timetable (Timetable Management).

Author: EduCore
App: OneApp
"""

MODULE_NAME = "m_timetable"
MODULE_VERSION = "1.0.0"
AUTHOR = "EduCore"
DESCRIPTION = "Timetable Management module — working day configuration, time slots, academic calendar linkage, timetable scheduling, faculty/room allocation, substitution, and approval workflow."

DEPENDENCIES = ["m_AAA", "m_academic_struct", "m_course_ops", "m_infra", "m_emp_fac"]

SUPPORTED_SUBMODULES = [
    "sm_allocation",
    "sm_approval",
    "sm_configuration",
    "sm_schedule",
    "sm_substitution",
]

DATABASE_SCHEMAS = [
    "sch_timetable",
    "sch_academic_struct",
    "sch_course_ops",
    "sch_infra",
    "sch_lookup",
    "sch_org",
]

PERMISSIONS = [
    "timetable.workingDay.add",
    "timetable.workingDay.view",
    "timetable.workingDay.update",
    "timetable.workingDay.delete",
    "timetable.timeSlot.add",
    "timetable.timeSlot.view",
    "timetable.timeSlot.update",
    "timetable.timeSlot.delete",
    "timetable.academicCalendar.add",
    "timetable.academicCalendar.view",
    "timetable.academicCalendar.update",
    "timetable.academicCalendar.delete",
    "timetable.timetable.add",
    "timetable.timetable.view",
    "timetable.timetable.update",
    "timetable.timetable.delete",
    "timetable.facultyAllocation.add",
    "timetable.facultyAllocation.view",
    "timetable.facultyAllocation.update",
    "timetable.facultyAllocation.delete",
    "timetable.roomAllocation.add",
    "timetable.roomAllocation.view",
    "timetable.roomAllocation.update",
    "timetable.roomAllocation.delete",
    "timetable.substitution.add",
    "timetable.substitution.view",
    "timetable.substitution.update",
    "timetable.substitution.delete",
    "timetable.timetableApproval.add",
    "timetable.timetableApproval.view",
    "timetable.timetableApproval.update",
    "timetable.timetableApproval.delete",
]

FEATURE_FLAGS = {}
