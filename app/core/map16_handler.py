import logging
import re

logger = logging.getLogger(__name__)

class Map16SubTile:
    def __init__(self, tile_id="000", palette=0, flip_x=False, flip_y=False, priority=False):
        self.tile_id = tile_id
        self.palette = palette
        self.flip_x = flip_x
        self.flip_y = flip_y
        self.priority = priority

    def to_string(self):
        # Format: "TILE PAL FLAGS" e.g. "287 0 ---" or "287 0 xyp"
        flags = ""
        flags += "x" if self.flip_x else "-"
        flags += "y" if self.flip_y else "-"
        flags += "p" if self.priority else "-"
        
        # Ensure 3-digit Hex (e.g. 0F8, 280)
        try:
            val = int(self.tile_id, 16)
            t_str = f"{val:03X}"
        except:
             t_str = self.tile_id # Fallback if not hex
             
        return f"{t_str} {self.palette} {flags}"

    @staticmethod
    def from_string(s):
        # Expects parts list or string, but usually caller splits.
        # This helper might need specific args. 
        # Let's assume input is "287 0 xyp" parts.
        pass

class Map16Tile:
    def __init__(self, tile_number, act_as="0025", sub_tiles=None):
        self.tile_number = tile_number # hex str: "6000"
        self.act_as = act_as           # hex str: "0130"
        # List of 4 Map16SubTile objects: TL, BL, TR, BR (User specified order)
        self.sub_tiles = sub_tiles if sub_tiles else [Map16SubTile() for _ in range(4)]
        self.is_empty = False

    def to_line(self):
        # Always output full format (no ~ shorthand)
        # Format: 6000: 0025 { TL BL TR BR }
        # Act As: 4 digits, 8x8 tiles: 3 digits
        
        act_as_str = self.act_as
        try:
            # Parse and re-format to ensure 4 digits (matching error example)
            val = int(self.act_as, 16)
            act_as_str = f"{val:04X}"
        except:
            act_as_str = self.act_as # Fallback if not hex
            
        subs_str = "  ".join([st.to_string() for st in self.sub_tiles])
        return f"{self.tile_number}: {act_as_str} {{ {subs_str} }}\n\n"

class Map16Handler:
    @staticmethod
    def parse_flags(flag_str):
        return 'x' in flag_str, 'y' in flag_str, 'p' in flag_str

    @staticmethod
    def parse_line(line):
        line = line.strip()
        if not line:
            return None
        
        # Check for empty tile: "6006: ~"
        match_empty = re.match(r"([0-9A-F]{4}):\s*~", line)
        if match_empty:
            tile = Map16Tile(match_empty.group(1))
            tile.is_empty = True
            return tile

        # Format: 6000: 0130 { 287 0 ---  0F8 2 ---  2B0 0 ---  0F8 2 --- }
        # Regex to capture parts
        # Group 1: TileNum
        # Group 2: ActAs
        # Group 3: Content inside {}
        match = re.match(r"([0-9A-F]{4}):\s*([0-9A-F]{4})\s*\{\s*(.*)\s*\}", line)
        if match:
            tile_num = match.group(1)
            act_as = match.group(2)
            content = match.group(3)
            
            # Split content by spaces, filtering empty
            parts = content.split()
            # We expect 4 * 3 = 12 parts
            if len(parts) != 12:
                logger.warning(f"Invalid sub-tile count in line: {line}")
                return None
            
            sub_tiles = []
            for i in range(0, 12, 3):
                t_id = parts[i]
                pal = int(parts[i+1])
                flags_str = parts[i+2]
                fx, fy, fp = Map16Handler.parse_flags(flags_str)
                sub_tiles.append(Map16SubTile(t_id, pal, fx, fy, fp))
            
            return Map16Tile(tile_num, act_as, sub_tiles)
        
        return None

    @staticmethod
    def generate_page_content(start_tile_hex, tiles):
        """
        Generates the lines for a Page file.
        start_tile_hex: "6000"
        tiles: list of Map16Tile objects (can be less than 256)
        
        IMPORTANT: Each page MUST have exactly 256 tile entries (00-FF)
        """
        lines = []
        base_addr = int(start_tile_hex, 16)
        
        # Each page must have exactly 256 tiles
        TILES_PER_PAGE = 256
        
        # Pad tiles list to 256 if needed
        while len(tiles) < TILES_PER_PAGE:
            # Create empty tile with 0F8 for all 4 sub-tiles and 0025 Act As
            empty_subtiles = [
                Map16SubTile("0F8", 0, False, False, False),
                Map16SubTile("0F8", 0, False, False, False),
                Map16SubTile("0F8", 0, False, False, False),
                Map16SubTile("0F8", 0, False, False, False)
            ]
            empty_tile = Map16Tile("0000", "0025", empty_subtiles)
            tiles.append(empty_tile)
        
        current_addr = base_addr
        for i, tile in enumerate(tiles[:TILES_PER_PAGE]):  # Only use first 256
            # Update tile number to match position
            hex_addr = f"{current_addr:04X}"
            tile.tile_number = hex_addr
            
            lines.append(tile.to_line())
            current_addr += 1
        
        # Adjust last line ending (remove one \n to end with single \n)
        if lines:
            lines[-1] = lines[-1][:-1]  # Change \n\n to \n
        
        return lines

class Map16Generator:
    def __init__(self, mapper):
        self.mapper = mapper
        self.blank_tile_id = "00F8" # Default generic transparent 8x8
        self.rows_per_page = 16    # 16x16 grid -> 16 rows of 16 tiles
        self.tiles_per_row = 16

    def generate_credits_tiles(self, credits_data, options):
        """
        Generates a list of Map16Tile objects representing the credits.
        credits_data: dict { "Section": ["Name1", ...] }
        options: dict { "optimize_columns": bool, "blank_tile": "0F8", "add_empty_line": bool, "act_as": str, "palette": int, "priority": bool }
        """
        self.blank_tile_id = options.get("blank_tile", "0F8")
        self.act_as = options.get("act_as", "0025")
        self.palette = options.get("palette", 0)
        self.priority = options.get("priority", False)
        
        optimize = options.get("optimize_columns", False)
        add_empty = options.get("add_empty_line", False)
        
        all_tiles = []
        
        # Processing Order: predefined list or alphabetical keys?
        # User listed: smwsprites, uberasm, smwblocks, smwgraphics, smwmusic
        # Let's try to stick to a logical order if possible, or just alpha.
        # Fixed order map
        order = ["Sprites", "UberASM", "Blocks", "Graphics", "Music", "Patches", "Tools", "General"]
        sections = sorted(credits_data.keys(), key=lambda k: order.index(k) if k in order else 99)
        
        for section in sections:
            names = credits_data[section]
            if not names:
                continue

            # Header
            header_tiles = self._text_to_tiles(section.upper()) # Headers CAPS?
            all_tiles.extend(self._create_single_column_row(section.upper())) # Use single column row logic for header
            
            # Authors
            # If optimize: try to fit 2 names in one row (16 chars * 8px = 128px = 1 row)
            # 16 chars is the limit for full row if using 8x8 font in 16x16 grid?
            # Wait, 1 16x16 Tile = 2x2 8x8 Tiles.
            # 1 Row of 16x16 tiles = 16 * 16 pixels width = 256 pixels.
            # 256 pixels / 8 (char width) = 32 characters per row.
            
            # So a full row of Map16 tiles can hold 32 characters.
            # If we split into 2 columns: 16 chars (approx) per name.
            
            current_row_names = []
            
            for name in names:
                if optimize:
                    if len(name) <= 14: # Allow some spacing used
                        current_row_names.append(name)
                        if len(current_row_names) == 2:
                            # Flush row
                            all_tiles.extend(self._create_two_column_row(current_row_names[0], current_row_names[1]))
                            current_row_names = []
                    else:
                        # Flush pending
                        if current_row_names:
                             all_tiles.extend(self._create_two_column_row(current_row_names[0], ""))
                             current_row_names = []
                        # Long name takes full row
                        all_tiles.extend(self._create_single_column_row(name))
                else:
                    all_tiles.extend(self._create_single_column_row(name))
            
            # Flush remaining
            if current_row_names:
                 all_tiles.extend(self._create_two_column_row(current_row_names[0], ""))
            
            # Empty line after section?
            if add_empty:
                all_tiles.extend(self._create_empty_row())

        return all_tiles

    def _text_to_tiles(self, text):
        """Converts string 'ABC' to list of 8x8 tile IDs ['280', '281', '282']"""
        ids = []
        for char in text:
            mapping = self.mapper.get_mapping(char)
            # Fallback? Spaces might map to something, or default to blank
            if not mapping:
                if char == ' ':
                    ids.append(self.blank_tile_id) # Start with blank
                else:
                    ids.append(self.blank_tile_id) # Unknown char -> Blank or ?
            else:
                ids.append(mapping)
        return ids

    def _create_single_column_row(self, text):
        """Creates Map16Tiles for a centered or left-aligned text taking full row"""
        # We have 32 slots (16 tiles * 2 horizontal sub-tiles)
        # 16 Map16 tiles.
        
        # Let's left align for credits usually?
        # Or Center?
        # User didn't specify alignment. Left is safer.
        char_ids = self._text_to_tiles(text)
        
        # Truncate if too long (max 32 chars)
        if len(char_ids) > 32:
            char_ids = char_ids[:32]
            
        return self._pack_char_ids_into_map16_row(char_ids)

    def _create_two_column_row(self, name1, name2):
        # Col 1: 0-15 (16 chars). Col 2: 16-31 (16 chars).
        ids1 = self._text_to_tiles(name1)[:15] # Leave 1 space margin?
        ids2 = self._text_to_tiles(name2)[:15]
        
        # Padding
        row_ids = ids1 + [self.blank_tile_id] * (16 - len(ids1))
        row_ids += ids2 + [self.blank_tile_id] * (16 - len(ids2))
        
        return self._pack_char_ids_into_map16_row(row_ids)

    def _create_empty_row(self):
         return self._pack_char_ids_into_map16_row([])

    def _pack_char_ids_into_map16_row(self, char_ids):
        """
        Takes up to 32 8x8 tile IDs and packs them into 16 Map16Tiles.
        """
        map16_tiles = []
        # Ensure 32 length
        padded = char_ids + [self.blank_tile_id] * (32 - len(char_ids))
        
        # We need to form 16x16 tiles.
        # Each 16x16 tile has TL, TR, BL, BR
        # Since this is text, we assume 8x8 font.
        # Usually text is 1 tile high? 
        # If user selected "8x8" mode:
        #   A line of text is 8 pixels high.
        #   Within a 16x16 block, we can fit 2 lines of text? Or 1 line centered?
        #   User said: "Wir sollten bei 8x8 großer Schrift auch abfragen ob eine Leerzeile erzeugt werden soll."
        #   And "0F8 ... ist ein transparenter Block".
        
        # Let's assume 1 row of text occupies the TOP half of the 16x16 blocks.
        # The BOTTOM half is left empty (blank).
        # This effectively gives line-height of 16px for 8px text.
        
        # Pairs: (TL, TR) come from the char stream.
        # BL, BR are always blank.
        
        for i in range(0, 32, 2):
            tl_id = padded[i]
            tr_id = padded[i+1]
            bl_id = self.blank_tile_id
            br_id = self.blank_tile_id
            
            # Create sub-tiles
            # Use mapper settings for palette/priority
            pal = self.palette
            prio = self.priority
            
            # Note: We need to respect flipped flags if we ever support them in mapping?
            # Current mapping is just ID.
            
            tl = Map16SubTile(tl_id, pal, False, False, prio)
            tr = Map16SubTile(tr_id, pal, False, False, prio)
            bl = Map16SubTile(bl_id, pal, False, False, prio)
            br = Map16SubTile(br_id, pal, False, False, prio)
            
            # Create Tile
            # Check for Empty logic? If all are blank?
            # If all are blank, is_empty = True?
            # Map16Tile construction
            tile = Map16Tile("0000", self.act_as, [tl, bl, tr, br]) # ORDER: TL, BL, TR, BR
            
            # Mark tile as empty if all 4 sub-tiles are blank (to use ~ shorthand)
            if all(st.tile_id == self.blank_tile_id for st in [tl, tr, bl, br]):
                tile.is_empty = True
            
            map16_tiles.append(tile)
            
        return map16_tiles

