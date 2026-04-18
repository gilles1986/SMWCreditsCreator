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
        except (ValueError, TypeError):
            logger.warning(f"Invalid tile_id '{self.tile_id}' in to_string(), using 000")
            t_str = "000"
             
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
        # List of 4 Map16SubTile objects: TL, TR, BL, BR (Reading Order)
        self.sub_tiles = sub_tiles if sub_tiles else [Map16SubTile() for _ in range(4)]
        self.is_empty = False

    def to_line(self):
        if self.is_empty:
            return f"{self.tile_number}: ~\n"
        
        act_as_str = self.act_as
        try:
            val = int(self.act_as, 16)
            act_as_str = f"{val:04X}"
        except (ValueError, TypeError):
            logger.warning(f"Invalid act_as '{self.act_as}' in to_line(), using 0025")
            act_as_str = "0025"
            
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

    @staticmethod
    def generate_map16_text(page_num, tiles):
        """
        Generates clipboard-ready text for Lunar Magic 16x16 Tile Map Editor.
        Format per line: TILE_NUM: ACT_AS { TL BL TR BR }
        """
        lines = []
        base_addr = page_num * 0x100
        
        process_tiles = tiles[:]
        
        while len(process_tiles) < 256:
             empty_subtiles = [Map16SubTile("0F8") for _ in range(4)]
             process_tiles.append(Map16Tile("0000", "0025", empty_subtiles))
             
        for i, tile in enumerate(process_tiles[:256]):
            curr_addr = base_addr + i
            hex_addr = f"{curr_addr:04X}"
            
            act_as = tile.act_as
            try:
                val = int(act_as, 16)
                act_as = f"{val:04X}"
            except (ValueError, TypeError):
                logger.warning(f"Invalid act_as '{act_as}' in text export, using 0025")
                act_as = "0025"
            
            # Export Order: TL, BL, TR, BR (Column Major)
            # Internal List (ExportTab): TL, TR, BL, BR
            export_order = [0, 2, 1, 3]
            
            subs = []
            for idx in export_order:
                if idx < len(tile.sub_tiles):
                    subs.append(tile.sub_tiles[idx].to_string())
                else:
                    subs.append("0F8") # Fallback
            
            line = f"{hex_addr}: {act_as} {{ {'  '.join(subs)} }}"
            lines.append(line)
            
        return "\n".join(lines)

    @staticmethod
    def generate_map16_binary(page_num, tiles):
        """
        Generates the binary content for a .map16 file (Full Page Export Format).
        Format: Split Data (Standard Lunar Magic Page Export)
        Total Size: 2736 bytes
        1. Header: 176 bytes
        2. Tile Data: 2048 bytes (256 tiles * 8 bytes [TL, BL, TR, BR])
        3. Act As Data: 512 bytes (256 tiles * 2 bytes)
        """
        import struct
        
        data = bytearray()
        
        # 1. Header Construction (176 bytes)
        # Use a validated header template from a working Lunar Magic export (Split Format)
        # This includes critical offsets (like 0x8B0 for Act As data) in the extended header.
        full_header_hex = "4c4d31360001010061030100000000007000000040000000100000001000000000000000800000000001070000000000000000000000000000000000000000004c756e6172204d6167696320332e36312020a932303235204675536f59612020446566656e646572206f662052656c6db000000000080000b008000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
        header = bytearray(bytes.fromhex(full_header_hex))
        
        # Patch all page-related fields in the header.
        # The template was built from a page-8 export (LM 3.61).
        #
        # LM reads byte117 directly as the import page number (no offset added).
        # Template encoding for page 8:  offset36=0x0080 (=8*0x10), byte117=0x08, byte121=0x08
        # => For any page: offset36 = page_num * 0x10, byte117 = page_num, byte121 = page_num
        try:
             struct.pack_into("<H", header, 36, (page_num * 0x10) & 0xFFFF)
             header[117] = page_num & 0xFF
             header[121] = page_num & 0xFF
             logger.debug(f"Patched page header for page 0x{page_num:02X}: off36=0x{page_num*0x10:X}, byte117/121=0x{page_num:02X}")
        except Exception as e:
             logger.warning(f"Header patch error: {e}")

             
        data.extend(header)
        
        def pack_subtile(st):
            # Format: yxpccctttttttttt
            try:
                tid = int(st.tile_id, 16)
            except (ValueError, TypeError):
                logger.warning(f"Invalid tile_id '{st.tile_id}' in pack_subtile(), using 0")
                tid = 0
            
            pal = st.palette & 0x7
            pri = 1 if st.priority else 0
            flip_x = 1 if st.flip_x else 0
            flip_y = 1 if st.flip_y else 0
            
            val = (tid & 0x3FF) | ((pal & 0x7) << 10) | ((pri & 1) << 13) | ((flip_x & 1) << 14) | ((flip_y & 1) << 15)
            return val

        # Ensure we have exactly 256 tiles
        process_tiles = tiles[:]
        while len(process_tiles) < 256:
             empty_subtiles = [Map16SubTile("0F8") for _ in range(4)]
             process_tiles.append(Map16Tile("0000", "0025", empty_subtiles))
        process_tiles = process_tiles[:256]

        # 2. Tile Data Block (2048 bytes)
        # Write 256 * 4 words
        # Order: Column Major (TL, BL, TR, BR)
        
        for tile in process_tiles:
            # Internal storage: [TL, TR, BL, BR] (Map16Tile init)
            # Map Internal -> File Output
            # Word 0: TL (Internal 0)
            # Word 1: BL (Internal 2) - Wait! Map16Tile init says: "list order: TL, BL, TR, BR (User specified)"??
            # NO. Let's re-verify parse_map16_binary logic in previous step.
            # Parse logic:
            #   subtiles = [unpack(w0), unpack(w2), unpack(w1), unpack(w3)]
            #   (w0=TL, w2=TR, w1=BL, w3=BR) -> Staged as [TL, TR, BL, BR]
            # So Internal is definitely [TL, TR, BL, BR].
            
            # File expects: TL, BL, TR, BR (Column Major)
            # So needed indices from Internal [TL, TR, BL, BR]:
            # TL -> 0
            # BL -> 2
            # TR -> 1
            # BR -> 3
            
            write_order = [0, 2, 1, 3]
            
            for idx in write_order:
                st = tile.sub_tiles[idx]
                data.extend(struct.pack("<H", pack_subtile(st)))
        
        # 3. Act As Data Block (512 bytes)
        # Write 256 * 1 word
        
        for tile in process_tiles:
            try:
                # User input is usually Hex String like "130"
                act = int(tile.act_as, 16)
            except (ValueError, TypeError):
                logger.warning(f"Invalid act_as '{tile.act_as}' in binary export, using 0x25")
                act = 0x25
            data.extend(struct.pack("<H", act))
            
        return data

    @staticmethod
    def generate_map16_selection(tiles):
        """
        Generates the 'Lunar Magic 16x16 Tiles' binary selection format.
        Header: 160 bytes.
        0x00: Offset TileData (0xA0)
        0x04: Offset ActAs (0xA0 + 8*N)
        0x08: Offset End (0xA0 + 10*N)
        0x50: Width (Tiles)
        0x54: Height (Tiles)
        ...
        Data: 8 bytes * N (Tile Data)
        Data: 2 bytes * N (Act As)
        """
        import struct
        
        count = len(tiles)
        if count == 0: return b""
        
        # Calculate Dimensions (Assume Row of 16 if large, else single row)
        if count <= 16:
            width = count
            height = 1
        else:
            width = 16
            height = (count + 15) // 16
            
        # Pad tiles to rectangular shape
        total_slots = width * height
        process_tiles = tiles[:]
        while len(process_tiles) < total_slots:
             empty_subtiles = [Map16SubTile("0F8") for _ in range(4)]
             process_tiles.append(Map16Tile("0000", "0025", empty_subtiles))
        
        final_count = len(process_tiles)
        
        # Offsets
        off_tile_data = 0xA0 # 160
        off_act_as = off_tile_data + (final_count * 8)
        off_end = off_act_as + (final_count * 2)
        
        # Build Header
        header = bytearray(160)
        struct.pack_into("<I", header, 0, off_tile_data)
        struct.pack_into("<I", header, 4, off_act_as)
        struct.pack_into("<I", header, 8, off_end)
        
        struct.pack_into("<I", header, 0x50, width)
        struct.pack_into("<I", header, 0x54, height)
        # Using 1 for 0x58 as seen in single dump (unknown, maybe selection count or planes)
        struct.pack_into("<I", header, 0x58, 1) 
        
        # Magic Bytes found in analysis (Offset 0x5C)
        # 0x76, 0x05 -> 0x0576
        struct.pack_into("<H", header, 0x5C, 0x0576)
        
        # Build Data
        tile_bytes = bytearray()
        act_bytes = bytearray()
        
        def pack_subtile(st):
            try:
                tid = int(st.tile_id, 16)
            except (ValueError, TypeError):
                logger.warning(f"Invalid tile_id '{st.tile_id}' in clipboard pack, using 0")
                tid = 0
            val = (tid & 0x3FF) | ((st.palette & 0x7) << 10) | ((1 if st.priority else 0) << 13) | ((1 if st.flip_x else 0) << 14) | ((1 if st.flip_y else 0) << 15)
            return val

        for tile in process_tiles:
            # Tile Data (4 words: TL, BL, TR, BR) - Wait, Selection Format might be Row Major?
            # Standard Page Export is Column Major (TL, BL, TR, BR)
            # Let's assume Column Major first as it matches Page Export.
            
            # Subtiles: TL, BL, TR, BR
            # Original export loop: 
            #   struct.pack("<H", pack_subtile(tile.sub_tiles[0])) # TL
            #   struct.pack("<H", pack_subtile(tile.sub_tiles[2])) # BL
            #   struct.pack("<H", pack_subtile(tile.sub_tiles[1])) # TR
            #   struct.pack("<H", pack_subtile(tile.sub_tiles[3])) # BR
            
            # Map16Tile.sub_tiles order is TL, TR, BL, BR (0, 1, 2, 3)
            # Expected Binary Order: TL, BL, TR, BR (0, 2, 1, 3)
            
            t0 = pack_subtile(tile.sub_tiles[0])
            t2 = pack_subtile(tile.sub_tiles[2])
            t1 = pack_subtile(tile.sub_tiles[1])
            t3 = pack_subtile(tile.sub_tiles[3])
            
            tile_bytes.extend(struct.pack("<HHHH", t0, t2, t1, t3))
            
            # Act As
            try: val = int(tile.act_as, 16)
            except (ValueError, TypeError):
                logger.warning(f"Invalid act_as '{tile.act_as}' in clipboard, using 0x25")
                val = 0x25
            act_bytes.extend(struct.pack("<H", val))
            
        full_data = header + tile_bytes + act_bytes
        logger.info(f"Clipboard Header: {header.hex()[:64]}...")
        logger.info(f"Clipboard Data Sample (First Tile): {tile_bytes.hex()[:16]}")
        return full_data
    
    @staticmethod
    def parse_map16_binary(file_path):
        """
        Parse a .map16 binary file and return tiles and page number.
        Returns: (page_num, tiles_list)
        """
        import struct
        import os
        
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # Check minimum size
        if len(data) < 176:
            raise ValueError("Invalid .map16 file: too small")
        
        # Verify header
        if data[0:4] != b'LM16':
            raise ValueError("Invalid .map16 file: missing LM16 signature")
        
        # Try to detect page number from filename
        # Format: page_XX.map16 or pageXX.map16
        basename = os.path.basename(file_path).lower()
        page_num = 0
        
        if 'page' in basename:
            # Extract hex number
            import re
            match = re.search(r'page[_\s]*([0-9a-fA-F]+)', basename)
            if match:
                try:
                    page_num = int(match.group(1), 16)
                except ValueError:
                    pass
        
        def unpack_subtile(word):
            tile_id = word & 0x3FF
            palette = (word >> 10) & 0x7
            priority = bool((word >> 13) & 1)
            flip_x = bool((word >> 14) & 1)
            flip_y = bool((word >> 15) & 1)
            return Map16SubTile(f"{tile_id:03X}", palette, flip_x, flip_y, priority)

        # Detect format based on size
        # Full Page Export (Lunar Magic): 2736 bytes = 176 Header + 2048 Tile Data + 512 Act As Data
        is_full_page_export = (len(data) == 2736)
        
        if is_full_page_export:
            # Full Page Format: Split Data
            # 1. Tile Data Block (2048 bytes): 256 tiles * 4 words (TL, BL, TR, BR)
            # 2. Act As Block (512 bytes): 256 tiles * 1 word
            
            tile_data_offset = 176
            act_as_offset = 176 + 2048
            
            for i in range(256):
                # Read 4 words for sub-tiles (8 bytes)
                t_off = tile_data_offset + (i * 8)
                t_bytes = data[t_off:t_off+8]
                sub_words = struct.unpack('<4H', t_bytes)
                
                # Check if it's a default/empty tile (all 4 are 0x004 or 0x0F8) usually
                # We can filter empty ones if desired, but let's keep all for now to maintain indices
                
                subtiles = []
                # Column Major Order in File: TL, BL, TR, BR
                # We want to store as: TL, TR, BL, BR (Reading Order)
                # Map File Words: 0=TL, 1=BL, 2=TR, 3=BR
                reorder_idx = [0, 2, 1, 3]
                
                for idx in reorder_idx:
                    subtiles.append(unpack_subtile(sub_words[idx]))
                
                # Read Act As word (2 bytes)
                a_off = act_as_offset + (i * 2)
                a_bytes = data[a_off:a_off+2]
                act_as_val = struct.unpack('<H', a_bytes)[0]
                act_as = f"{act_as_val:04X}"
                
                # Tile Number
                tile_num = f"{(page_num * 0x100) + i:04X}"
                
                tile = Map16Tile(tile_num, act_as, subtiles)
                tiles.append(tile)
                
        else:
            # Single/Partial Export Format: Interleaved Data
            # 10 bytes per tile: 4 words (subtiles) + 1 word (Act As)
            
            num_tiles = (len(data) - 176) // 10
            
            for i in range(num_tiles):
                offset = 176 + (i * 10)
                tile_bytes = data[offset:offset+10]
                words = struct.unpack('<5H', tile_bytes)
                
                # Parse subtiles
                # Column Major Order in File: TL, BL, TR, BR
                # File: 0=TL, 1=BL, 2=TR, 3=BR
                subtiles = [
                    unpack_subtile(words[0]), # TL
                    unpack_subtile(words[2]), # TR
                    unpack_subtile(words[1]), # BL
                    unpack_subtile(words[3])  # BR
                ]
                
                # Act As is the 5th word
                act_as = f"{words[4]:04X}"
                
                # Tile number: File index maps directly to tile position
                # Page num * 256 + file index
                tile_num = f"{(page_num * 0x100) + i:04X}"
                
                tile = Map16Tile(tile_num, act_as, subtiles)
                tiles.append(tile)
        
        return page_num, tiles

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
        self.font_size = options.get("font_size", "8x8")
        
        optimize = options.get("optimize_columns", False)
        add_empty = options.get("add_empty_line", False)
        sort_mode = options.get("sort_mode", "predefined")  # "predefined", "alphabetical", or "none"
        
        all_tiles = []
        
        # Processing Order based on sort_mode
        PREDEFINED_ORDER = ["Sprites", "UberASM", "Blocks", "Graphics", "Music", "Patches", "Tools", "General"]
        if sort_mode == "alphabetical":
            sections = sorted(credits_data.keys())
        elif sort_mode == "none":
            sections = list(credits_data.keys())
        else:  # predefined (default)
            sections = sorted(credits_data.keys(), key=lambda k: PREDEFINED_ORDER.index(k) if k in PREDEFINED_ORDER else 99)
        
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
        Packs characters into 16 Map16Tiles based on font_size.
        """
        map16_tiles = []
        
        # Helper to parse ID string -> list of ints/strings
        def parse_ids(id_str):
             if not id_str: return []
             try:
                 parts = id_str.split(',')
                 return [p.strip() for p in parts if p.strip()]
             except (AttributeError, TypeError):
                 return [id_str]

        # Helper to get sub-tile parsed info
        # Returns (hex_str_id, flip_x, flip_y, priority)
        def get_id_and_flags(val):
             try:
                 if isinstance(val, int):
                      return f"{val:03X}", False, False, False
                 
                 flags_str = ""
                 base_id = val
                 
                 if isinstance(val, str) and ':' in val:
                      parts = val.split(':')
                      base_id = parts[0]
                      if len(parts) > 1:
                           flags_str = parts[1]
                 
                 try:
                      int_id = int(base_id, 16)
                      hex_id = f"{int_id:03X}"
                 except (ValueError, TypeError):
                      logger.warning(f"Invalid tile_id '{base_id}' in get_id_and_flags(), using 000")
                      hex_id = "000"
                 
                 fx = 'x' in flags_str
                 fy = 'y' in flags_str
                 fp = 'p' in flags_str
                 
                 return hex_id, fx, fy, fp
             except Exception as e:
                 logger.warning(f"Unexpected error in get_id_and_flags('{val}'): {e}")
                 return "000", False, False, False
        
        # Helper method to apply properties to a specific sub-tile
        def apply_to_subtile(st, val):
             tid, fx, fy, fp = get_id_and_flags(val)
             st.tile_id = tid
             st.flip_x = fx
             st.flip_y = fy
             # Priority: OR with global setting? Or override?
             # Usually "Global Priority" implies all credits on top.
             # If specific tile has priority, it should definitely be set.
             st.priority = self.priority or fp
             st.palette = self.palette

        if self.font_size == "16x16":
             # 1 Char = 1 Map16 Tile
             row_chars = char_ids[:16]
             row_chars += [self.blank_tile_id] * (16 - len(row_chars))
             
             for cid in row_chars:
                  parts = parse_ids(cid)
                  
                  t_tl = parts[0] if parts else self.blank_tile_id
                  
                  # Determine Sub-tile IDs and Flags
                  val_tl = t_tl
                  val_tr, val_bl, val_br = None, None, None
                  
                  # Helper to check if a tile ID is blank
                  def is_blank(v):
                       tid, _, _, _ = get_id_and_flags(v)
                       try: return int(tid, 16) == int(self.blank_tile_id, 16)
                       except ValueError: return False
                  
                  # If the primary tile is blank, all sub-tiles should be blank
                  if is_blank(val_tl):
                       val_tr = self.blank_tile_id
                       val_bl = self.blank_tile_id
                       val_br = self.blank_tile_id
                  elif len(parts) >= 4:
                       val_tr = parts[1]
                       val_bl = parts[2]
                       val_br = parts[3]
                  elif len(parts) == 2:
                       # Smart 2-Row Logic is complex with flags.
                       # If standard int logic applies, we calculate. 
                       # If explicit flags provided, we use as base?
                       # Assuming if using shorthand with flags, logic applies to base ID, flags separate?
                       # OR: if flags are used, shorthand might not be safe.
                       # But let's try to support: "280:x, 285" -> 
                       # TL=280:x, TR=281:x, BL=285, BR=286
                       
                       # Helper to increment hex string with carried flags? 
                       # Currently, let's assume if 2 parts:
                       # TL = P0, BL = P1. TR and BR are calculated (+1).
                       # Inherit flags? Usually mirroring applies to the whole block relative to axis?
                       # If I mirror 16x16 X-wise:
                       # Real 16x16 geometry:
                       # [TL] [TR]  --> [TR_flipped] [TL_flipped]
                       # This is too complex for simple tile mapping shorthand.
                       # Let's assume Flags apply strictly to the 8x8 tile itself as defined.
                       # So: TR = TL base + 1. Flags? Keep same flags as TL? 
                       # Usually if flipping a character, you flip all 8x8s.
                       
                       def offset_val(base_val, offset):
                            tid, fx, fy, fp = get_id_and_flags(base_val)
                            try:
                                 nid = int(tid, 16) + offset
                                 flags = ""
                                 if fx: flags += "x"
                                 if fy: flags += "y"
                                 if fp: flags += "p"
                                 return f"{nid:03X}:{flags}"
                            except ValueError:
                                 return base_val
                                 
                       val_tr = offset_val(val_tl, 1)
                       val_bl = parts[1]
                       val_br = offset_val(val_bl, 1)
                       
                  else:
                       # Fallback 16x16 standard
                       def offset_val(base_val, offset):
                            tid, fx, fy, fp = get_id_and_flags(base_val)
                            try:
                                 nid = int(tid, 16) + offset
                                 flags = ""
                                 if fx: flags += "x"
                                 if fy: flags += "y"
                                 if fp: flags += "p"
                                 return f"{nid:03X}:{flags}"
                            except ValueError:
                                 return base_val

                       val_tr = offset_val(val_tl, 1)
                       val_bl = offset_val(val_tl, 16)
                       val_br = offset_val(val_tl, 17)
                  
                  tile = Map16Tile(f"0000", self.act_as)
                  
                  apply_to_subtile(tile.sub_tiles[0], val_tl)
                  apply_to_subtile(tile.sub_tiles[1], val_tr)
                  apply_to_subtile(tile.sub_tiles[2], val_bl)
                  apply_to_subtile(tile.sub_tiles[3], val_br)
                  
                  map16_tiles.append(tile)

        elif self.font_size == "8x16":
             # 2 Chars per Map16 Tile
             padded = char_ids + [self.blank_tile_id] * (32 - len(char_ids))
             
             for i in range(0, 32, 2):
                  c1 = padded[i]
                  c2 = padded[i+1]
                  
                  p1 = parse_ids(c1)
                  p2 = parse_ids(c2)
                  
                  # Char 1 (Left Half)
                  val_tl = p1[0] if p1 else self.blank_tile_id
                  
                  def is_blank(v):
                       tid, _, _, _ = get_id_and_flags(v)
                       try: return int(tid, 16) == int(self.blank_tile_id, 16)
                       except ValueError: return False # Default
                       
                  if is_blank(val_tl):
                       val_bl = self.blank_tile_id
                  else:
                       if len(p1) >= 2:
                            val_bl = p1[1]
                       else:
                            # Offset +0x10
                             tid, fx, fy, fp = get_id_and_flags(val_tl)
                             try:
                                 nid = int(tid, 16) + 16
                                 flags = ""
                                 if fx: flags += "x"
                                 if fy: flags += "y"
                                 if fp: flags += "p"
                                 val_bl = f"{nid:03X}:{flags}"
                             except ValueError:
                                  val_bl = val_tl 

                  # Char 2 (Right Half)
                  val_tr = p2[0] if p2 else self.blank_tile_id
                  
                  if is_blank(val_tr):
                       val_br = self.blank_tile_id
                  else:
                       if len(p2) >= 2:
                            val_br = p2[1]
                       else:
                             tid, fx, fy, fp = get_id_and_flags(val_tr)
                             try:
                                 nid = int(tid, 16) + 16
                                 flags = ""
                                 if fx: flags += "x"
                                 if fy: flags += "y"
                                 if fp: flags += "p"
                                 val_br = f"{nid:03X}:{flags}"
                             except ValueError:
                                  val_br = val_tr 
                  
                  tile = Map16Tile(f"0000", self.act_as)
                  apply_to_subtile(tile.sub_tiles[0], val_tl)
                  apply_to_subtile(tile.sub_tiles[1], val_tr)
                  apply_to_subtile(tile.sub_tiles[2], val_bl)
                  apply_to_subtile(tile.sub_tiles[3], val_br)
                  
                  map16_tiles.append(tile)

        else: # 8x8 (Default)
             padded = char_ids + [self.blank_tile_id] * (32 - len(char_ids))
             
             for i in range(0, 32, 2):
                  c1 = padded[i]
                  c2 = padded[i+1]
                  
                  p1 = parse_ids(c1)
                  p2 = parse_ids(c2)
                  
                  val_tl = p1[0] if p1 else self.blank_tile_id
                  val_bl = p1[1] if len(p1) > 1 else self.blank_tile_id
                  
                  val_tr = p2[0] if p2 else self.blank_tile_id
                  val_br = p2[1] if len(p2) > 1 else self.blank_tile_id
                  
                  tile = Map16Tile(f"0000", self.act_as)
                  apply_to_subtile(tile.sub_tiles[0], val_tl)
                  apply_to_subtile(tile.sub_tiles[1], val_tr)
                  apply_to_subtile(tile.sub_tiles[2], val_bl)
                  apply_to_subtile(tile.sub_tiles[3], val_br)
                  
                  map16_tiles.append(tile)

        return map16_tiles

