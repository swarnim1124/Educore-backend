"""
File: document_constants.py
Description: Constants for the centralized Document Generation Service.
Author: Siddharth Amdal.
"""


class DocumentType:
    PDF = "PDF"
    EXCEL = "EXCEL"
    WORD = "WORD"
    IMAGE = "IMAGE"


class GenerationStatus:
    REQUESTED = "REQUESTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
