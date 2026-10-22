"""
File: xsc_libc_templates.py
Description: Common source-code templates used across the framework.

Author: EduCore
"""

from __future__ import annotations


class Templates:
    """
    Central repository for all source-code templates.

    This class is responsible only for returning template strings.
    It does not perform any file or code editing operations.
    """

    @staticmethod
    def file_header(description: str = "") -> str:
        return '''"""
File:
Description: {description}

Author:
App: OneApp

"""
'''

    @staticmethod
    def module_class(class_name: str) -> str:
        """
        Returns the primary class template for a newly created module/submodule.
        """

        return '''
class {class_name}:
    def __call__(self, req_json_obj):
        action = req_json_obj.get("action")

        if not action:
            return {{
                "status": "error",
                "message": "Action is not mentioned"
            }}

        action_handler = getattr(self, action, None)

        if not callable(action_handler):
            return {{
                "status": "error",
                "message": "Action not found"
            }}

        return action_handler(req_json_obj)


    def health(self, req_json_obj):
        """
        Function to check whether the class is accessible.
        """

        return {{
            "health": "good"
        }}
'''

    @staticmethod
    def action_method(method_name: str) -> str:
        """
        Returns the template for a new action method.
        """

        return '''
def {method_name}(self, req_json_obj):
    """
    TODO: Add description.
    """

    payload = req_json_obj.get("payload") or {{}}

    return {{
        "status": "success",
        "message": "Not implemented"
    }}
'''

    @staticmethod
    def complete_submodule(class_name: str, description: str = "") -> str:
        """
        Returns a complete submodule source file.
        """

        return (
            Templates.file_header(description)
            + "\n\n"
            + Templates.module_class(class_name)
        )

    @staticmethod
    def complete_module(class_name: str, description: str = "") -> str:
        """
        For now modules and submodules share the same template.
        """

        return Templates.complete_submodule(class_name, description)
