#!/usr/bin/env python
"""
Analyze page8.map16 to understand the structure and find tile 0x912
"""
import struct

def unpack_subtile(word):
    """Unpack a 16-bit word into tile properties"""
    tile_id = word & 0x3FF
    palette = (word >> 10) & 0x7
    priority = (word >> 13) & 1
    flip_x = (word >> 14) & 1
    flip_y = (word >> 15) & 1
    return {
        'tile_id': tile_id,
        'palette': palette,
        'priority': priority,
        'flip_x': flip_x,
        'flip_y': flip_y
    }

with open('page8.map16', 'rb') as f:
    data = f.read()

print(f"File size: {len(data)} bytes")
print(f"Header: {data[:16].hex()}")
print()

# Map16 pages start at 0x800, 0x900, ... 
# Tile 0x912 is on page 9 (0x900), offset 0x12 (18 decimal)
# But this file is "page8.map16", so it contains page 8 (0x800-0x8FF)
# Wait, the user said tile 912 (hex) is in the screenshot
# 0x912 = 2322 decimal
# Page 9 would be 0x900-0x9FF
# But maybe page8.map16 is actually page 0x80?

# Let me check what tiles are actually in this file
# Binary format: 176 byte header + 256 tiles * 10 bytes each

header_size = 176
tile_count = (len(data) - header_size) // 10

print(f"Tile count: {tile_count}")
print()

# Let's look at all non-empty tiles
print("Non-default tiles:")
for i in range(tile_count):
    offset = header_size + (i * 10)
    tile_data = data[offset:offset+10]
    
    # Unpack 5 words (little-endian)
    words = struct.unpack("<5H", tile_data)
    
    # Check if all subtiles are 0x1004 (default empty)
    if all(w == 0x1004 for w in words[:4]):
        continue
    
    # This tile has custom data
    tile_num = i
    print(f"\nTile {tile_num:02X} (page local):")
    print(f"  Raw data: {tile_data.hex()}")
    
    # Parse subtiles (TL, BL, TR, BR based on column-major order)
    subtile_names = ['TL', 'BL', 'TR', 'BR']
    for j, name in enumerate(subtile_names):
        st = unpack_subtile(words[j])
        print(f"  {name}: Tile={st['tile_id']:02X} Pal={st['palette']} Pri={st['priority']} FlipX={st['flip_x']} FlipY={st['flip_y']}")
    
    # Act As
    act_as = words[4]
    print(f"  Act As: {act_as:04X}")

print("\n" + "="*50)
print("Looking for tile with subtiles 6, 7, 16, 17...")

# The user said it should contain tiles made of 6, 7, 16 (0x10), 17 (0x11)
# In column-major order: TL, BL, TR, BR
# So we're looking for TL=6, BL=16, TR=7, BR=17
# Or in reading order: TL=6, TR=7, BL=16, BR=17

for i in range(tile_count):
    offset = header_size + (i * 10)
    tile_data = data[offset:offset+10]
    words = struct.unpack("<5H", tile_data)
    
    # Parse all subtiles
    subtiles = [unpack_subtile(w) for w in words[:4]]
    tile_ids = [st['tile_id'] for st in subtiles]
    
    # Check column-major: [TL, BL, TR, BR] = [6, 16, 7, 17]
    if tile_ids == [6, 16, 7, 17]:
        print(f"\nFOUND (Column-Major)! Tile {i:02X}")
        print(f"  TL=6, BL=16, TR=7, BR=17")
        print(f"  Palette: {subtiles[0]['palette']}")
        print(f"  Priority: {subtiles[0]['priority']}")
        print(f"  Act As: {words[4]:04X}")
        break
    
    # Check reading order: [TL, TR, BL, BR] = [6, 7, 16, 17]
    if tile_ids == [6, 7, 16, 17]:
        print(f"\nFOUND (Reading Order)! Tile {i:02X}")
        print(f"  TL=6, TR=7, BL=16, BR=17")
        print(f"  Palette: {subtiles[0]['palette']}")
        print(f"  Priority: {subtiles[0]['priority']}")
        print(f"  Act As: {words[4]:04X}")
        break
else:
    print("\nTile with 6, 7, 16, 17 NOT FOUND in this file.")
