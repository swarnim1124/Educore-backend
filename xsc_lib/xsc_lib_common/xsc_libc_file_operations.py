"""
Common filesystem operations for the framework.
"""

from __future__ import annotations

import shutil
from pathlib import Path


class FileOperations:
    """Stateless filesystem helpers for file and directory operations."""

    @staticmethod
    def create_file(path: str | Path, content: str = "") -> None:
        """Create a new file, creating parent directories as needed."""
        file_path = FileOperations.to_path(path)
        FileOperations.ensure_parent_directory(file_path)

        if file_path.exists():
            raise FileExistsError(f"File already exists: {file_path}")

        file_path.write_text(content, encoding="utf-8")

    @staticmethod
    def delete_file(path: str | Path) -> None:
        """Delete an existing file."""
        file_path = FileOperations.require_file(path)
        file_path.unlink()

    @staticmethod
    def rename_file(old_path: str | Path, new_path: str | Path) -> None:
        """Rename a file to a new path."""
        source_path = FileOperations.require_file(old_path)
        destination_path = FileOperations.to_path(new_path)
        FileOperations.ensure_parent_directory(destination_path)
        source_path.rename(destination_path)

    @staticmethod
    def copy_file(source_path: str | Path, destination_path: str | Path) -> None:
        """Copy a file to a new path."""
        source = FileOperations.require_file(source_path)
        destination = FileOperations.to_path(destination_path)
        FileOperations.ensure_parent_directory(destination)
        shutil.copy2(source, destination)

    @staticmethod
    def move_file(source_path: str | Path, destination_path: str | Path) -> None:
        """Move a file to a new path."""
        source = FileOperations.require_file(source_path)
        destination = FileOperations.to_path(destination_path)
        FileOperations.ensure_parent_directory(destination)
        shutil.move(str(source), str(destination))

    @staticmethod
    def read_file(path: str | Path) -> str:
        """Read and return the contents of a file."""
        file_path = FileOperations.require_file(path)
        return file_path.read_text(encoding="utf-8")

    @staticmethod
    def write_file(path: str | Path, content: str) -> None:
        """Overwrite a file with the provided content."""
        file_path = FileOperations.to_path(path)
        FileOperations.ensure_parent_directory(file_path)
        file_path.write_text(content, encoding="utf-8")

    @staticmethod
    def append_to_file(path: str | Path, content: str) -> None:
        """Append text to an existing file."""
        file_path = FileOperations.require_file(path)
        with file_path.open("a", encoding="utf-8") as file_obj:
            file_obj.write(content)

    @staticmethod
    def file_exists(path: str | Path) -> bool:
        """Return whether the given path exists and is a file."""
        return FileOperations.to_path(path).is_file()

    @staticmethod
    def create_directory(path: str | Path) -> None:
        """Create a new directory and any missing parent directories."""
        directory_path = FileOperations.to_path(path)
        directory_path.mkdir(parents=True, exist_ok=False)

    @staticmethod
    def delete_directory(path: str | Path, recursive: bool = False) -> None:
        """Delete a directory, optionally including all nested contents."""
        directory_path = FileOperations.require_directory(path)

        if recursive:
            shutil.rmtree(directory_path)
            return

        directory_path.rmdir()

    @staticmethod
    def rename_directory(old_path: str | Path, new_path: str | Path) -> None:
        """Rename a directory to a new path."""
        source_path = FileOperations.require_directory(old_path)
        destination_path = FileOperations.to_path(new_path)
        FileOperations.ensure_parent_directory(destination_path)
        source_path.rename(destination_path)

    @staticmethod
    def directory_exists(path: str | Path) -> bool:
        """Return whether the given path exists and is a directory."""
        return FileOperations.to_path(path).is_dir()

    @staticmethod
    def list_files(path: str | Path) -> list[str]:
        """Return the direct child files within a directory."""
        directory_path = FileOperations.require_directory(path)
        return sorted(
            str(entry) for entry in directory_path.iterdir() if entry.is_file()
        )

    @staticmethod
    def list_directories(path: str | Path) -> list[str]:
        """Return the direct child directories within a directory."""
        directory_path = FileOperations.require_directory(path)
        return sorted(
            str(entry) for entry in directory_path.iterdir() if entry.is_dir()
        )

    @staticmethod
    def to_path(path: str | Path) -> Path:
        """Convert an incoming filesystem value to a Path object."""
        return Path(path)

    @staticmethod
    def ensure_parent_directory(path: str | Path) -> None:
        """Create parent directories for the given path if they do not exist."""
        normalized_path = FileOperations.to_path(path)
        normalized_path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def require_file(path: str | Path) -> Path:
        """Validate that the given path exists and points to a file."""
        file_path = FileOperations.to_path(path)

        if not file_path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")

        if not file_path.is_file():
            raise IsADirectoryError(f"Expected a file path: {file_path}")

        return file_path

    @staticmethod
    def require_directory(path: str | Path) -> Path:
        """Validate that the given path exists and points to a directory."""
        directory_path = FileOperations.to_path(path)

        if not directory_path.exists():
            raise FileNotFoundError(f"Directory does not exist: {directory_path}")

        if not directory_path.is_dir():
            raise NotADirectoryError(f"Expected a directory path: {directory_path}")

        return directory_path
