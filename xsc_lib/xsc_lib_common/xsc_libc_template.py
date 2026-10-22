"""
File: xsc_libc_template.py
Description: Common utility for rendering templates (e.g. Jinja2).
Author: Siddharth Amdal.
"""

from jinja2 import Template
from typing import Dict, Any


class TemplateRenderer:
    @staticmethod
    def render(template_path: str, data: Dict[str, Any]) -> str:
        """
        Reads a template file and renders it with the provided data payload using Jinja2.

        Args:
            template_path (str): Absolute path to the template file.
            data (Dict[str, Any]): Dictionary containing dynamic data for the template.

        Returns:
            str: Rendered template string.
        """
        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        template = Template(template_content)
        return template.render(**data)
