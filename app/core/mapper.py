import json
import logging
from app.core.map16_handler import Map16SubTile, Map16Tile, Map16Handler

logger = logging.getLogger(__name__)

class Mapper:
    def __init__(self):
        # Mappings: { character: tile_id_str } (source 8x8 tile id)
        self.mappings = {}
        
    def set_mapping(self, char, tile_id):
        self.mappings[char] = tile_id

    def get_mapping(self, char):
        return self.mappings.get(char, "")

    def load_mappings(self, filepath):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                # Support both old format (full dict) and new (just mappings)
                # If "mappings" key exists, use it. Else assume root is mappings? 
                # Or stick to structure. Structure is {"mappings": {...}}
                self.mappings = data.get("mappings", {})
                
            return True, "Mappings loaded."
        except Exception as e:
            logger.error(f"Error loading mappings: {e}")
            return False, f"Error loading mappings: {e}"

    def save_mappings(self, filepath):
        try:
            data = {
                "mappings": self.mappings
            }
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
            return True, "Mappings saved."
        except Exception as e:
            logger.error(f"Error saving mappings: {e}")
            return False, f"Error saving mappings: {e}"

    def load_default_mappings(self, filepath="mapping.json"):
        import os
        if not os.path.exists(filepath):
            # Create default if not exists
            # Optional: Populate with standard defaults?
            # User might expect A-Z to be mapped?
            # Let's populate defaults: A starts at 280 (Standard SMW)
            start_tile = 0x280
            for i in range(26): # A-Z
                char = chr(ord('A') + i)
                self.mappings[char] = f"{start_tile + i:X}"
            
            self.save_mappings(filepath)
            return True, f"Created default mapping file at {filepath} with standard A-Z."
        else:
            return self.load_mappings(filepath)

    def get_default_characters(self):
        # A-Z, 0-9, space, some symbols
        chars = [chr(i) for i in range(ord('A'), ord('Z')+1)]
        chars += [chr(i) for i in range(ord('a'), ord('z')+1)]
        chars += [str(i) for i in range(10)]
        chars += [' ', '.', ',', '!', '?', '-', "'", '"', '/']
        # Sort uniqueness
        return sorted(list(set(chars + list(self.mappings.keys()))))

    def apply_bulk_rules(self, rules_text):
        """
        Parses rules line by line.
        Syntax:
        - Range: A-Z = 280
        - Single: ! = 100
        """
        report = []
        lines = rules_text.split('\n')
        count = 0
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"): # Comment support
                continue
                
            if "=" not in line:
                report.append(f"Skipped invalid line: {line}")
                continue
                
            parts = line.split("=")
            key_part = parts[0].strip()
            val_part = parts[1].strip()
            
            try:
                start_tile = int(val_part, 16)
            except ValueError:
                report.append(f"Invalid hex value '{val_part}' in line: {line}")
                continue

            # Check if Range
            if "-" in key_part and len(key_part) == 3: # Simple A-Z check
                start_char = key_part[0]
                end_char = key_part[2]
                
                # Iterate range
                curr_tile = start_tile
                # ord ranges works for ASCII.
                s_code = ord(start_char)
                e_code = ord(end_char)
                
                if s_code > e_code:
                     report.append(f"Invalid range {key_part} (Start > End)")
                     continue
                     
                for code in range(s_code, e_code + 1):
                    char = chr(code)
                    hex_str = f"{curr_tile:X}"
                    self.mappings[char] = hex_str
                    curr_tile += 1
                    count += 1
                report.append(f"Applied range {key_part} starting at {val_part}")
                
            # Check if Bracket Set: [ABC]
            elif key_part.startswith("[") and key_part.endswith("]"):
                content = key_part[1:-1]
                # Parse content with escapes
                chars_to_map = []
                i = 0
                while i < len(content):
                    char = content[i]
                    if char == '\\' and i + 1 < len(content):
                        # Escape next
                         chars_to_map.append(content[i+1])
                         i += 2
                    else:
                         chars_to_map.append(char)
                         i += 1
                
                curr_tile = start_tile
                for char in chars_to_map:
                    hex_str = f"{curr_tile:X}"
                    self.mappings[char] = hex_str
                    curr_tile += 1
                    count += 1
                report.append(f"Mapped set {key_part} starting at {val_part}")

            else:
                # Single char (or maybe complex string key?)
                # User asked for "eigene Sonderzeichen".
                if len(key_part) == 1:
                    char = key_part
                    hex_str = f"{start_tile:X}"
                    self.mappings[char] = hex_str
                    count += 1
                    report.append(f"Mapped {char} = {hex_str}")
                else:
                    report.append(f"Skipped complex key '{key_part}' (only single chars or A-Z ranges supported for now)")

        return True, f"Processed {count} mappings.\n" + "\n".join(report)
