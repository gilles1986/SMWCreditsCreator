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

    # --- Hex Tile ID Validation ---

    MAX_TILE_ID = 0x3FF  # 10-bit tile ID range (0-1023)

    @staticmethod
    def validate_tile_id(value, max_id=None):
        """
        Validates a single hex tile ID string (e.g. "280", "0F8").
        Supports optional flags suffix (e.g. "280:xy").
        Returns (is_valid, error_message).
        """
        if max_id is None:
            max_id = Validator.MAX_TILE_ID

        if not value or not isinstance(value, str):
            return False, "Empty or missing tile ID."

        value = value.strip()
        if not value:
            return False, "Empty tile ID."

        # Strip flags suffix if present (e.g. "280:xy" -> "280")
        base_id = value.split(':')[0].strip()

        if not base_id:
            return False, "Empty tile ID (before flags)."

        # Check for valid hex characters
        if not re.match(r'^[0-9A-Fa-f]+$', base_id):
            return False, f"'{base_id}' contains invalid hex characters."

        # Parse and range-check
        try:
            int_val = int(base_id, 16)
        except ValueError:
            return False, f"'{base_id}' is not a valid hex number."

        if int_val < 0 or int_val > max_id:
            return False, f"Tile ID 0x{int_val:03X} is out of range (0x000-0x{max_id:03X})."

        return True, ""

    @staticmethod
    def validate_mapping_value(value):
        """
        Validates a mapping value which may be:
        - Single tile ID: "280"
        - Single with flags: "280:xy"
        - Comma-separated composite: "280, 290" or "280:x, 290:y"
        Returns (is_valid, error_message).
        """
        if not value or not isinstance(value, str):
            return False, "Empty or missing mapping value."

        value = value.strip()
        if not value:
            return False, "Empty mapping value."

        parts = [p.strip() for p in value.split(',')]
        errors = []

        for i, part in enumerate(parts):
            if not part:
                errors.append(f"Part {i+1}: empty value after comma.")
                continue
            valid, msg = Validator.validate_tile_id(part)
            if not valid:
                errors.append(f"'{part}': {msg}")

        if errors:
            return False, "; ".join(errors)

        return True, ""

    @staticmethod
    def validate_all_mappings(mappings):
        """
        Validates all entries in a mappings dict { char: hex_value }.
        Returns (is_valid, list_of_errors) where each error is (char, value, message).
        """
        errors = []
        for char, value in mappings.items():
            if char == ' ':
                continue  # Space uses blank_tile_id, handled separately
            if not value:
                continue  # Empty mapping = unmapped, not an error
            valid, msg = Validator.validate_mapping_value(value)
            if not valid:
                errors.append((char, value, msg))

        return len(errors) == 0, errors
