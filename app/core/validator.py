import os
import logging
import re

logger = logging.getLogger(__name__)

class Validator:
    @staticmethod
    def validate_folder(path):
        """
        Validates if the folder is a valid RHR project.
        Criteria: changelog.txt must contain "v5.10".
        """
        if not path or not os.path.exists(path):
            return False, "Folder does not exist."

        changelog_path = os.path.join(path, "changelog.txt")
        if not os.path.exists(changelog_path):
            return False, "changelog.txt not found. Is this an RHR project?"

        try:
            with open(changelog_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # User specified "v5.10\n" validation
                # Check for "v5.10" or higher logic? Or just presence of "vX.XX" and if it contains "v5.10" or we parse it?
                # User request: "Detect exact version... first version found"
                
                # Regex for vX.XX
                match = re.search(r"v\d+\.\d+", content)
                if match:
                    detected_version = match.group(0)
                    if "v5.10" in content: # Keep the safe check for 5.10 requirement as per original req
                         return True, f"Valid RHR project (Detected: {detected_version})"
                    else:
                         return False, f"Version invalid (Detected: {detected_version}, v5.10 required)"
                
                if "v5.10" in content: # Fallback if regex fails but simple check passes
                    return True, "Valid RHR project (v5.10+)."
                else:
                    return False, "Version too old or invalid (v5.10 required)."
        except Exception as e:
            logger.error(f"Error reading changelog: {e}")
            return False, f"Error reading changelog: {e}"

    @staticmethod
    def get_rhr_version(path):
        """
        Determines the RHR version type.
        Returns ">=5.13" if tools/Callisto exists, else "<5.13" (assuming valid 5.10+ validated before).
        """
        callisto_path = os.path.join(path, "tools", "Callisto")
        if os.path.exists(callisto_path):
            return ">=5.13"
        else:
            return "<5.13"
