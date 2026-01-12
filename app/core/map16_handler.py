import os
import logging

logger = logging.getLogger(__name__)

class Map16Handler:
    def __init__(self):
        pass

    def read_text_map16(self, filepath):
        """
        Reads a Lunar Magic Text Map16 file.
        Returns a list of lines or parsed structure.
        """
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
            return lines
        except Exception as e:
            logger.error(f"Error reading Map16: {e}")
            return []

    def write_text_map16(self, filepath, lines):
        """
        Writes lines to a file.
        """
        try:
            with open(filepath, 'w') as f:
                f.writelines(lines)
            return True
        except Exception as e:
            logger.error(f"Error writing Map16: {e}")
            return False

    def find_map16_files(self, project_path):
        # Determine export folder based on common RHR patterns
        # Usually checking 'build/map16' or similar? 
        # For now, just a helper generic walker or specific if known.
        # User said "Analyse der export folders".
        # Let's search for .map16 in the whole folder for now or specific subdirs.
        found = []
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.endswith(".map16"):
                    found.append(os.path.join(root, file))
        return found
