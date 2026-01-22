#!/usr/bin/env python
"""
Analyze the freshly exported page8_export.map16 to find tile 812
Expected: TL=6, TR=7, BL=16, BR=17, Palette=6, Act As=130
"""
import struct

with open('page8_export.map16', 'rb') as f:
    data = f.read()

print("Analyzing page8_export.map16 (fresh from Lunar Magic)")
print("=" * 70)
print(f"File size: {len(data)} bytes")
print(f"Header: {data[:16].hex()}")
print()

header_size = 176

# Search for tile 812
# With +4 offset: file index = (0x812 & 0xFF) - 4 = 0x12 - 4 = 0x0E
target_file_idx = 0x0E
offset = header_size + (target_file_idx * 10)

print(f"Looking for Tile 812 at file index {target_file_idx:02X}:")
print(f"  Offset: {offset} (0x{offset:X})")

tile_bytes = data[offset:offset+10]
words = struct.unpack('<5H', tile_bytes)

print(f"  Raw bytes: {tile_bytes.hex()}")
print(f"  Words: {[f'{w:04X}' for w in words]}")
print()

# Decode each word
print("Decoding subtiles:")
subtile_names = ['Word 0', 'Word 1', 'Word 2', 'Word 3']
for i, name in enumerate(subtile_names):
    w = words[i]
    tile_id = w & 0x3FF
    palette = (w >> 10) & 0x7
    priority = (w >> 13) & 1
    flip_x = (w >> 14) & 1
    flip_y = (w >> 15) & 1
    
    flags = []
    if flip_x: flags.append('X')
    else: flags.append('-')
    if flip_y: flags.append('Y')
    else: flags.append('-')
    if priority: flags.append('P')
    else: flags.append('-')
    flag_str = ''.join(flags)
    
    print(f"  {name}: Tile={tile_id:02X} ({tile_id}), Pal={palette}, Flags={flag_str}")

print(f"\nAct As: {words[4]:04X} ({words[4]})")

print("\n" + "=" * 70)
print("Expected values:")
print("  TL=6, TR=7, BL=16, BR=17")
print("  All Palette 6, Flags=--- (no flips/priority)")
print("  Act As=130 (0x0082)")

# Check column-major order
print("\nIf Column-Major (TL, BL, TR, BR):")
print(f"  Word0(TL)={words[0]&0x3FF:02X}, Word1(BL)={words[1]&0x3FF:02X}, Word2(TR)={words[2]&0x3FF:02X}, Word3(BR)={words[3]&0x3FF:02X}")

# Search entire file for 6,7,16,17 pattern
print("\n" + "=" * 70)
print("Searching entire file for tiles with 6, 7, 16 (0x10), 17 (0x11)...")

for file_idx in range(256):
    offset = header_size + (file_idx * 10)
    if offset + 10 > len(data):
        break
    
    tile_bytes = data[offset:offset+10]
    words = struct.unpack('<5H', tile_bytes)
    tids = [words[i] & 0x3FF for i in range(4)]
    
    if 6 in tids and 7 in tids and 0x10 in tids and 0x11 in tids:
        display_tile = 0x800 + file_idx + 4
        print(f"\n✓ FOUND at File Index {file_idx:02X} → Tile {display_tile:04X}")
        print(f"  Subtiles: {[f'{t:02X}' for t in tids]}")
        print(f"  Raw: {tile_bytes.hex()}")
