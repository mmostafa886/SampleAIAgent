"""
CSV Service - Handles all CSV file operations
"""

import csv
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CSVService:
    """Service class for CSV file operations."""

    def __init__(self, output_directory="generated_test_cases"):
        """
        Initialize the CSV service.

        Args:
            output_directory (str): Directory where CSV files will be saved
        """
        self.output_directory = output_directory
        self.fieldnames = [
            'Test Case ID',
            'Test Case Title',
            'Steps',
            'Expected Result',
            'Linked Acceptance Criterion'
        ]
        self._ensure_output_directory_exists()

    def _ensure_output_directory_exists(self):
        """Create the output directory if it doesn't exist."""
        try:
            os.makedirs(self.output_directory, exist_ok=True)
        except Exception as e:
            raise Exception(f"Failed to create output directory: {str(e)}")

    def _generate_filename(self, base_filename):
        """
        Generate a filename with timestamp.

        Args:
            base_filename (str): Base name for the file (without extension)

        Returns:
            str: Complete filename with timestamp and .csv extension
        """
        # Remove .csv extension if user added it
        base_filename = base_filename.replace('.csv', '').strip()

        # Default to 'test_cases' if no filename provided
        if not base_filename:
            base_filename = "test_cases"

        # Add timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_filename}_{timestamp}.csv"

        return filename

    def _get_filepath(self, filename):
        """
        Get the full file path.

        Args:
            filename (str): The filename

        Returns:
            str: Full path to the file
        """
        return os.path.join(self.output_directory, filename)

    def save_test_cases(self, test_cases, base_filename="test_cases"):
        """
        Save test cases to a CSV file.

        Args:
            test_cases (list): List of test case dictionaries
            base_filename (str): Base name for the output file

        Returns:
            dict: Result dictionary with success status and file information
                {
                    "success": bool,
                    "filename": str (if success),
                    "filepath": str (if success),
                    "count": int (if success),
                    "error": str (if failure)
                }
        """
        try:
            # Validate input
            if not test_cases or not isinstance(test_cases, list):
                return {
                    "success": False,
                    "error": "Test cases must be a non-empty list"
                }

            if len(test_cases) == 0:
                return {
                    "success": False,
                    "error": "No test cases to save"
                }

            # Generate filename
            filename = self._generate_filename(base_filename)
            filepath = self._get_filepath(filename)

            # Write to CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(
                    csvfile,
                    fieldnames=self.fieldnames,
                    extrasaction='ignore'  # Ignore extra fields not in fieldnames
                )
                writer.writeheader()
                writer.writerows(test_cases)

            return {
                "success": True,
                "filename": filename,
                "filepath": filepath,
                "count": len(test_cases)
            }

        except PermissionError:
            return {
                "success": False,
                "error": "Permission denied: Cannot write to output directory"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to save CSV file: {str(e)}"
            }

    def file_exists(self, filename):
        """
        Check if a file exists in the output directory.

        Args:
            filename (str): The filename to check

        Returns:
            bool: True if file exists, False otherwise
        """
        filepath = self._get_filepath(filename)
        return os.path.exists(filepath)

    def get_file_path(self, filename):
        """
        Get the full path to a file.

        Args:
            filename (str): The filename

        Returns:
            str: Full path to the file
        """
        return self._get_filepath(filename)

    def list_files(self):
        """
        List all CSV files in the output directory.

        Returns:
            list: List of CSV filenames
        """
        try:
            files = [f for f in os.listdir(self.output_directory) if f.endswith('.csv')]
            return sorted(files, reverse=True)  # Most recent first
        except Exception:
            return []

    def get_output_directory(self):
        """
        Get the output directory path.

        Returns:
            str: Output directory path
        """
        return self.output_directory

    def delete_file(self, filename):
        """
        Delete a CSV file.

        Args:
            filename (str): The filename to delete

        Returns:
            dict: Result dictionary with success status
        """
        try:
            filepath = self._get_filepath(filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return {
                    "success": True,
                    "message": f"File {filename} deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "File not found"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete file: {str(e)}"
            }