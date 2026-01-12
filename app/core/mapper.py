import json
import logging

logger = logging.getLogger(__name__)

class Mapper:
    def __init__(self):
        # Mappings: { character: tile_id_str }
        # Example: { 'A': '80', 'B': '81' }
        self.mappings = {}
        self.tile_size = "8x8" # or 16x16

    def set_mapping(self, char, tile_id):
        self.mappings[char] = tile_id

    def get_mapping(self, char):
        return self.mappings.get(char, "")

    def load_mappings(self, filepath):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.mappings = data.get("mappings", {})
                self.tile_size = data.get("tile_size", "8x8")
            return True, "Mappings loaded."
        except Exception as e:
            logger.error(f"Error loading mappings: {e}")
            return False, f"Error loading mappings: {e}"

    def save_mappings(self, filepath):
        try:
            data = {
                "tile_size": self.tile_size,
                "mappings": self.mappings
            }
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
            return True, "Mappings saved."
        except Exception as e:
            logger.error(f"Error saving mappings: {e}")
            return False, f"Error saving mappings: {e}"

    def get_default_characters(self):
        # A-Z, 0-9, space, some symbols
        chars = [chr(i) for i in range(ord('A'), ord('Z')+1)]
        chars += [chr(i) for i in range(ord('a'), ord('z')+1)]
        chars += [str(i) for i in range(10)]
        chars += [' ', '.', ',', '!', '?', '-', "'", '"', '/']
        return chars
