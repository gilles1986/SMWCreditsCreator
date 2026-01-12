import os
import logging
import re

logger = logging.getLogger(__name__)

class Validator:
    @staticmethod
    def get_rhr_version(path):
        """
        Parses the RHR version from changelog.txt.
        Returns a float (e.g. 5.13) or None if not found/parseable.
        """
        changelog_path = os.path.join(path, "changelog.txt")
        if not os.path.exists(changelog_path):
            return None

        try:
            with open(changelog_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Find first occurrence of vX.XX
                match = re.search(r"v(\d+)\.(\d+)", content)
                if match:
                    return (int(match.group(1)), int(match.group(2)))
        except Exception as e:
            logger.error(f"Error reading version: {e}")
        
        return None

    @staticmethod
    def validate_folder(path):
        """
        Validates if the folder is a valid RHR project (v5.00+).
        """
        if not path or not os.path.exists(path):
            return False, "Folder does not exist."

        version = Validator.get_rhr_version(path)
        
        if version is None:
             return False, "changelog.txt not found or version unreadable."
             
        if version < (5, 0):
            return False, f"RHR Version too old (Detected: v{version[0]}.{version[1]}). Minimum required: v5.00"

        return True, f"Valid RHR project (v{version[0]}.{version[1]})"
