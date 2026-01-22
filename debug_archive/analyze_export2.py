#!/usr/bin/env python
"""
Analyze page8_export2.map16 to understand the true structure
User added tiles at: 800, 802, 804, 810, 812, 814
"""
import struct

with open('page8_export2.map16', 'rb') as f:
    data = f.read()

print("=" * 70)
print("Analyzing page8_export2.map16")
print("=" * 70)
print(f"File size: {len(data)} bytes")
print(f"Header size: 176 bytes")
print(f"Data size: {len(data) - 176} bytes")
print(f"Tile count: {(len(data) - 176) // 10}")
print()

header_size = 176

# User added tiles at: 800, 802, 804, 810, 812, 814
# If there's NO offset: File index 0 = Tile 800
# If there's a +4 offset: File index 0 = Tile 804, so Tile 800 would be at index -4 (impossible)
# OR: Tile 800 is stored in header somehow?

print("Checking first 10 tiles in the file:")
print("=" * 70)

for file_idx in range(10):
    offset = header_size + (file_idx * 10)
    if offset + 10 > len(data):
        print(f"File index {file_idx:02X}: NO DATA (file too short)")
        continue
    
    tile_bytes = data[offset:offset+10]
    words = struct.unpack('<5H', tile_bytes)
    
    tids = [words[i] & 0x3FF for i in range(4)]
    
    # Check if tile is non-default (not all same, not all 0F8, not all 004)
    is_custom = (
        len(set(tids)) > 1 or  # Has different tile IDs
        (tids[0] not in [0x0F8, 0x004] and len(set(tids)) == 1)  # Or all same non-default
    )
    
    # Calculate possible tile numbers
    no_offset_tile = 0x800 + file_idx
    plus4_offset_tile = 0x804 + file_idx
    
    marker = "✓" if is_custom else " "
    
    print(f"{marker} File Index {file_idx:02X}:")
    print(f"    Raw: {tile_bytes.hex()}")
    print(f"    TileIDs: {[f'{t:02X}' for t in tids]}")
    print(f"    If no offset → Tile {no_offset_tile:04X}")
    print(f"    If +4 offset → Tile {plus4_offset_tile:04X}")
    print()

print("=" * 70)
print("Analysis:")
print("User added tiles at: 800, 802, 804, 810, 812, 814")
print()
print("If NO offset:")
print("  File index 00 should be Tile 800 ✓")
print("  File index 02 should be Tile 802 ✓")
print("  File index 04 should be Tile 804 ✓")
print("  File index 10 should be Tile 810 ✓")
print("  File index 12 should be Tile 812 ✓")
print("  File index 14 should be Tile 814 ✓")
print()
print("If +4 offset:")
print("  Tile 800 would be at file index -4 (IMPOSSIBLE)")
print("  File index 00 would be Tile 804")
print("=" * 70)
