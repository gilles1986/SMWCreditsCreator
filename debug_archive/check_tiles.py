#!/usr/bin/env python
"""
Check exact tile positions in page8.map16
"""
import struct

with open('page8.map16', 'rb') as f:
    data = f.read()

header_size = 176

def show_tile(tile_index):
    """Show tile at given index (0-255)"""
    offset = header_size + (tile_index * 10)
    tile_bytes = data[offset:offset+10]
    words = struct.unpack("<5H", tile_bytes)
    
    print(f"\nTile Index {tile_index:02X} (= Page 8 Tile 08{tile_index:02X}):")
    print(f"  Offset in file: {offset} (0x{offset:X})")
    print(f"  Raw bytes: {tile_bytes.hex()}")
    print(f"  Words: {[f'{w:04X}' for w in words]}")
    
    # Decode subtiles
    for i, name in enumerate(['Word0(TL)', 'Word1(BL)', 'Word2(TR)', 'Word3(BR)']):
        w = words[i]
        tid = w & 0x3FF
        pal = (w >> 10) & 0x7
        print(f"  {name}: Tile={tid:02X} ({tid}), Pal={pal}")
    
    print(f"  Act As: {words[4]:04X}")

print("=" * 60)
print("Checking specific tiles mentioned by user:")
print("=" * 60)

# User says: Tiles 812 and 814 are the only edited ones
# That's index 0x12 and 0x14
show_tile(0x10)  # User says this shows wrong data
show_tile(0x12)  # Should contain 6, 7, 16, 17
show_tile(0x14)  # Another edited tile

print("\n" + "=" * 60)
print("Looking for 6, 7, 16, 17 pattern:")
print("=" * 60)

for i in range(256):
    offset = header_size + (i * 10)
    tile_bytes = data[offset:offset+10]
    words = struct.unpack("<5H", tile_bytes)
    
    tids = [(w & 0x3FF) for w in words[:4]]
    
    # Check for 6, 7, 16, 17 in any order
    if 6 in tids and 7 in tids and 16 in tids and 17 in tids:
        print(f"\nFOUND at index {i:02X} (Tile 08{i:02X}):")
        print(f"  Subtile IDs: {tids}")
        print(f"  Raw: {tile_bytes.hex()}")
