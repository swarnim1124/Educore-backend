"""
File: m_timetable.py
Description: Dynamic BRS Gateway Router for m_timetable (Timetable Management).
             Uses an explicit contract map for submodules and actions.

Author: EduCore
App: OneApp
"""

import importlib
import asyncio

# Explicit BRS Contract Routing Map
# Format: sub_mod: (module_filename, class_name, action_map)
ROUTES = {
    # 1. Configuration Submodule
    "sm_configuration": (
        "m_timetable_sm_configuration",
        "Configuration",
        {
            "workingDay": "working_day",
            "working_day": "working_day",
            "timeSlot": "time_slot",
            "time_slot": "time_slot",
            "academicCalendar": "academic_calendar",
            "academic_calendar": "academic_calendar",
        },
    ),
    # 2. Schedule Submodule
    "sm_schedule": (
        "m_timetable_sm_schedule",
        "Schedule",
        {"timetable": "timetable", "schedule": "timetable"},
    ),
    # 3. Allocation Submodule
    "sm_allocation": (
        "m_timetable_sm_allocation",
        "Allocation",
        {
            "facultyAllocation": "faculty_allocation",
            "faculty_allocation": "faculty_allocation",
            "roomAllocation": "room_allocation",
            "room_allocation": "room_allocation",
        },
    ),
    # 4. Substitution Submodule
    "sm_substitution": (
        "m_timetable_sm_substitution",
        "Substitution",
        {"substitution": "substitution"},
    ),
    # 5. Approval Submodule
    "sm_approval": (
        "m_timetable_sm_approval",
        "Approval",
        {
            "timetableApproval": "timetable_approval",
            "timetable_approval": "timetable_approval",
        },
    ),
}


class Timetable:
    """
    Gateway Entry Point Router for m_timetable.
    Enforces strict BRS contract mapping and returns structured responses.
    """

    def __call__(self, req_json_obj, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        sub_mod_raw = req_json_obj.get("subMod") or req_json_obj.get("submod")
        sub_mod = XSCUtility.to_snake_case(sub_mod_raw) if sub_mod_raw else None
        action = req_json_obj.get("action")
        action_type = req_json_obj.get("actionType")

        if not sub_mod or not action or not action_type:
            return XSCUtility.error_response(
                message="Missing required parameters: 'subMod', 'action', or 'actionType'",
                error_code="400",
            )

        # 1. Resolve in Contract Map
        sm_sub_mod = sub_mod if sub_mod.startswith("sm_") else f"sm_{sub_mod}"
        route = ROUTES.get(sm_sub_mod) or ROUTES.get(sub_mod)

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
                message=f"Execution error in m_timetable handler: {str(e)}",
                error_code="500",
            )
