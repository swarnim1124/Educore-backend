"""
File: weasyprint_provider.py
Description: External integration for PDF generation using WeasyPrint (with ReportLab fallback).
Author: Siddharth Amdal.
"""

from typing import Dict, Any


class WeasyPrintProvider:
    @staticmethod
    def generate(
        rendered_html: str, output_path: str, fallback_data: Dict[str, Any] = None
    ) -> bool:
        """
        Takes rendered HTML string and writes it to a PDF file at output_path.
        If WeasyPrint is unavailable, falls back to ReportLab using fallback_data.

        Args:
            rendered_html (str): The HTML content to convert.
            output_path (str): The destination file path.
            fallback_data (Dict[str, Any]): Data to use if falling back to reportlab.

        Returns:
            bool: True if generated successfully.
        """
        try:
            from weasyprint import HTML

            weasyprint_available = True
        except (ImportError, OSError) as e:
            print(
                f"[WeasyPrintProvider] Could not import WeasyPrint. Falling back to ReportLab: {e}"
            )
            weasyprint_available = False

        try:
            if weasyprint_available:
                # Generate PDF
                HTML(string=rendered_html).write_pdf(output_path)
            else:
                # Fallback to reportlab
                if fallback_data is None:
                    fallback_data = {}
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter

                c = canvas.Canvas(output_path, pagesize=letter)
                c.drawString(
                    100,
                    750,
                    f"Attendance Report - {fallback_data.get('institution_name', 'Institution')}",
                )
                c.drawString(
                    100, 730, f"Student: {fallback_data.get('student_name', 'Unknown')}"
                )
                c.drawString(100, 710, f"USN: {fallback_data.get('usn', 'Unknown')}")
                c.drawString(
                    100,
                    690,
                    f"Overall Percentage: {fallback_data.get('overall_percentage', 0)}%",
                )

                y = 650
                c.drawString(100, y, "Subjects:")
                y -= 20
                for sub in fallback_data.get("subjects", []):
                    c.drawString(
                        120,
                        y,
                        f"- {sub.get('subject')}: {sub.get('percentage')}% ({sub.get('attended')}/{sub.get('total_classes')})",
                    )
                    y -= 20

                c.save()

            return True
        except Exception as _e:
            print(f"[WeasyPrintProvider] Error generating PDF: {str(e)}")
            raise
