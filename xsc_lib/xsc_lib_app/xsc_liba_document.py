"""
File: lib_document.py
Description: The central Document Generation Application Abstraction for xsc_lib.
Author: Siddharth Amdal.
"""

from typing import Dict, Any
from ..xsc_lib_common.xsc_libc_document_constants import DocumentType
from ..xsc_lib_common.xsc_libc_template import TemplateRenderer
from ..xsc_lib_common.xsc_libc_file import FileManager
from ..xsc_lib_extn.xsc_libe_weasyprint_provider import WeasyPrintProvider
from ..xsc_lib_extn.xsc_libe_excel_provider import ExcelProvider
from ..xsc_lib_extn.xsc_libe_word_provider import WordProvider
from ..xsc_lib_extn.xsc_libe_image_provider import ImageProvider


class DocumentManager:
    """
    Application abstraction layer that hides implementation details of various
    document generation external libraries.
    """

    @staticmethod
    def generate_document(
        document_type: str, template_path: str, data: Dict[str, Any], output_path: str
    ) -> bool:
        """
        Routes the generation request to the appropriate external integration.

        Args:
            document_type (str): The format (PDF, EXCEL, WORD, IMAGE).
            template_path (str): The path to the physical template (can be empty string for EXCEL).
            data (Dict[str, Any]): The dynamic data payload to inject.
            output_path (str): The destination path for the generated document.

        Returns:
            bool: True if successful, raises an Exception otherwise.
        """
        # Create output directory structure via common utility
        FileManager.ensure_directory_exists(output_path)

        if document_type == DocumentType.PDF:
            FileManager.validate_file_exists(template_path)
            rendered_html = TemplateRenderer.render(template_path, data)
            return WeasyPrintProvider.generate(
                rendered_html, output_path, fallback_data=data
            )

        elif document_type == DocumentType.EXCEL:
            # Excel doesn't strictly need a template_path in our implementation
            return ExcelProvider.generate(data, output_path)

        elif document_type == DocumentType.WORD:
            FileManager.validate_file_exists(template_path)
            return WordProvider.generate(template_path, data, output_path)

        elif document_type == DocumentType.IMAGE:
            FileManager.validate_file_exists(template_path)
            return ImageProvider.generate(template_path, data, output_path)

        else:
            raise ValueError(f"Unsupported document type: {document_type}")
