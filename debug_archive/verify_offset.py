#!/usr/bin/env python
"""
Verify the offset issue: My parser shows 810, Lunar Magic shows 814
"""
import struct

with open('page8.map16', 'rb') as f:
    data = f.read()

print("Screenshot shows: Page 80, Tile 814")
print("Tile 814 = 0x814 hex")
print("Tile 814 composition: 280, 281 (top row), 282, 283 (bottom row)")
print("Act As: 130")
print()

header_size = 176

# According to my parser: Index 0x10 contains 280,281,282,283
# According to Lunar Magic: This should be tile 0x814

print("=" * 60)
print("My parser reads at index 0x10:")
offset = header_size + (0x10 * 10)
tile_bytes = data[offset:offset+10]
words = struct.unpack("<5H", tile_bytes)
print(f"  Offset: {offset} (header {header_size} + index 0x10 * 10)")
print(f"  Data: {tile_bytes.hex()}")
print(f"  Decoded: TL={words[0]&0x3FF:03X}, BL={words[1]&0x3FF:03X}, TR={words[2]&0x3FF:03X}, BR={words[3]&0x3FF:03X}")
print(f"  Act As: {words[4]:04X}")
print(f"  My display: Tile 0810 (Page 08, Index 10)")
print(f"  Should be: Tile 0814 (according to screenshot)")
print()

print("Difference: 0x814 - 0x810 = 4 tiles")
print()

print("=" * 60)
print("Hypothesis 1: First 4 tiles are missing in file")
print("If file starts at tile 804 instead of 800...")
print()

# Let's check: If the file actually starts at tile 0x804
# then index 0 in file = tile 0x804
# index 0x10 (16) in file = tile 0x804 + 0x10 = 0x814 ✓

print("If file base is 0x804 instead of 0x800:")
print(f"  File index 0x10 = Tile 0x804 + 0x10 = 0x814 ✓ MATCHES!")
print()

print("=" * 60)
print("Hypothesis 2: File actually contains partial page")
print("Checking file size...")
print(f"  Total file size: {len(data)} bytes")
print(f"  Header: 176 bytes") 
print(f"  Data: {len(data) - 176} bytes")
print(f"  Tiles in file: {(len(data) - 176) // 10}")
print(f"  Expected for full page (256 tiles): {header_size + 256*10} bytes")
print()

if (len(data) - 176) // 10 == 256:
    print("File contains full 256 tiles")
    print("So first 4 tiles (800-803) must be empty/default")
    print("And actual custom data starts at tile 804")
else:
    print("File contains partial data!")
