"""
File: xsc_libc_file.py
Description: Common utility for file operations.
Author: Siddharth Amdal.
"""

import os


class FileManager:
    @staticmethod
    def ensure_directory_exists(file_path: str) -> None:
        """
        Creates the parent directory for the given file path if it doesn't exist.

        Args:
            file_path (str): The path to the file whose directory should be ensured.

        Returns:
            None
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    @staticmethod
    def validate_file_exists(file_path: str) -> None:
        """
        Validates if a file exists. Raises FileNotFoundError if it doesn't.

        Args:
            file_path (str): The physical path to validate.

        Returns:
            None
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at {file_path}")
