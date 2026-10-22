"""
File: m_super_admin_sm_config.py
Description: Submodule for Configuration CRUD operations in Super Admin.
             Config files are stored under <project_root>/xsc_conf/.

Author: Akshay Basutkar, Siddharth Admal, Swarnim Deshpande
App: OneApp

"""

from pathlib import Path

# Anchor: <repo>/modules/m_super_admin -> parents[1] = modules -> parents[0] of that = project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
XSC_CONF_DIR = PROJECT_ROOT / "xsc_con"


def _get_config_path(config_file_name: str) -> Path:
    return XSC_CONF_DIR / f"oa_{config_file_name}.py"


class Config:
    """
    Single submodule class handling configuration variable operations.
    """

    async def config(self, action_type, payload, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        action_type = (action_type or "").lower()

        match action_type:
            case "read":
                return self.read(payload, context)
            case "update":
                return self.update(payload, context)
            case "delete":
                return self.delete(payload, context)
            case _:
                return XSCUtility.error_response(
                    message=f"Unsupported actionType '{action_type}' for config"
                )

    # --- Public Action Handlers ---

    def read(self, payload, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from xsc_lib.xsc_lib_common.xsc_libc_code_editor import CodeEditor

        config_file_name = payload.get("config_file_name")
        file_path = _get_config_path(config_file_name)

        if not file_path.exists():
            return XSCUtility.error_response(
                message=f"Config file '{config_file_name}' does not exist"
            )

        try:
            editor = CodeEditor(file_path)
            vars_dict = editor.get_top_level_variables()
            return XSCUtility.success_response(
                message="Config read successfully", data=vars_dict
            )
        except ValueError as e:
            return XSCUtility.error_response(message=str(e))

    def update(self, payload, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from xsc_lib.xsc_lib_common.xsc_libc_code_editor import CodeEditor

        config_file_name = payload.get("config_file_name")
        var_name = payload.get("variable_name")
        var_value = payload.get("variable_value")

        if not config_file_name or not var_name:
            return XSCUtility.error_response(
                message="config_file_name and variable_name are required"
            )

        file_path = _get_config_path(config_file_name)
        if not file_path.exists():
            return XSCUtility.error_response(
                message=f"Config file '{config_file_name}' does not exist"
            )

        try:
            editor = CodeEditor(file_path)
            existing_vars = editor.get_top_level_variables()
            if var_name not in existing_vars:
                return XSCUtility.error_response(
                    message=f"Variable '{var_name}' does not exist in oa_{config_file_name}.py"
                )

            editor.set_variable_value(var_name, var_value)
            editor.save()
            return XSCUtility.success_response(
                message=f"Variable '{var_name}' updated successfully in oa_{config_file_name}.py"
            )
        except ValueError as e:
            return XSCUtility.error_response(message=str(e))

    def delete(self, payload, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from xsc_lib.xsc_lib_common.xsc_libc_code_editor import CodeEditor

        config_file_name = payload.get("config_file_name")
        var_name = payload.get("variable_name")

        if not config_file_name or not var_name:
            return XSCUtility.error_response(
                message="config_file_name and variable_name are required"
            )

        file_path = _get_config_path(config_file_name)
        if not file_path.exists():
            return XSCUtility.error_response(
                message=f"Config file '{config_file_name}' does not exist"
            )

        try:
            editor = CodeEditor(file_path)
            existing_vars = editor.get_top_level_variables()
            if var_name not in existing_vars:
                return XSCUtility.error_response(
                    message=f"Variable '{var_name}' does not exist in oa_{config_file_name}.py"
                )

            editor.delete_variable(var_name)
            editor.save()
            return XSCUtility.success_response(
                message=f"Variable '{var_name}' deleted successfully from oa_{config_file_name}.py"
            )
        except ValueError as e:
            return XSCUtility.error_response(message=str(e))


# Class name aliases for ActionDispatcher resolution
sm_config = Config
