#!/usr/bin/env python
"""
Search entire page8.map16 for tiles containing 6, 7, 16, 17
"""
import struct

with open('page8.map16', 'rb') as f:
    data = f.read()

header_size = 176
tile_count = (len(data) - header_size) // 10

print("Searching ALL tiles for pattern containing 6, 7, 16 (0x10), 17 (0x11)...")
print("=" * 70)

found_tiles = []

for file_idx in range(tile_count):
    offset = header_size + (file_idx * 10)
    tile_bytes = data[offset:offset+10]
    words = struct.unpack('<5H', tile_bytes)
    
    # Extract tile IDs
    tids = [words[i] & 0x3FF for i in range(4)]
    
    # Check if contains 6, 7, 16, 17
    target = {6, 7, 0x10, 0x11}
    tile_set = set(tids)
    
    if target.issubset(tile_set):
        # Found exact match!
        display_tile = 0x800 + file_idx + 4  # +4 offset for page 8
        print(f"\n✓ EXACT MATCH at File Index {file_idx:02X} → Tile {display_tile:04X}")
        print(f"  Raw: {tile_bytes.hex()}")
        print(f"  Subtiles: {[f'{t:02X}' for t in tids]}")
        print(f"  Act As: {words[4]:04X}")
        found_tiles.append(display_tile)
    
    # Also check for partial matches (3 out of 4)
    elif len(target & tile_set) >= 3:
        display_tile = 0x800 + file_idx + 4
        print(f"\n○ Partial match at File Index {file_idx:02X} → Tile {display_tile:04X}")
        print(f"  Subtiles: {[f'{t:02X}' for t in tids]} (has {target & tile_set})")

print("\n" + "=" * 70)
if found_tiles:
    print(f"Found exact match(es) at tile(s): {[f'0x{t:04X}' for t in found_tiles]}")
else:
    print("NO EXACT MATCH FOUND in file!")
    print("\nSearching for individual values...")
    
    # Search for each value individually
    for search_val in [6, 7, 0x10, 0x11]:
        print(f"\n  Tiles containing {search_val:02X}:")
        for file_idx in range(tile_count):
            offset = header_size + (file_idx * 10)
            tile_bytes = data[offset:offset+10]
            words = struct.unpack('<5H', tile_bytes)
            tids = [words[i] & 0x3FF for i in range(4)]
            
            if search_val in tids:
                display_tile = 0x800 + file_idx + 4
                print(f"    File {file_idx:02X} → Tile {display_tile:04X}: {[f'{t:02X}' for t in tids]}")
