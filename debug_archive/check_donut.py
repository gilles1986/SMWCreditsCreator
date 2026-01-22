#!/usr/bin/env python
import struct

data = open('donut_only.map16', 'rb').read()

print(f"File: donut_only.map16")
print(f"Size: {len(data)} bytes")
print(f"Header: {data[:16].hex()}")
print()

# Check tile at file index 0x0E (should be tile 812)
idx = 0x0E
offset = 176 + idx * 10
tile_bytes = data[offset:offset+10]
words = struct.unpack('<5H', tile_bytes)

print(f"Tile at file index 0x{idx:02X}:")
print(f"  Raw bytes: {tile_bytes.hex()}")
print(f"  Words: {[f'{w:04X}' for w in words]}")
print()

# Decode (Column-Major: Word0=TL, Word1=BL, Word2=TR, Word3=BR)
tids = [words[i] & 0x3FF for i in range(4)]
pals = [(words[i] >> 10) & 0x7 for i in range(4)]
flips_x = [bool((words[i] >> 14) & 1) for i in range(4)]
flips_y = [bool((words[i] >> 15) & 1) for i in range(4)]
pris = [bool((words[i] >> 13) & 1) for i in range(4)]

print("Decoded (Column-Major TL, BL, TR, BR):")
print(f"  TL = Tile {tids[0]:02X}, Pal {pals[0]}")
print(f"  BL = Tile {tids[1]:02X}, Pal {pals[1]}")
print(f"  TR = Tile {tids[2]:02X}, Pal {pals[2]}")
print(f"  BR = Tile {tids[3]:02X}, Pal {pals[3]}")
print(f"  Act As = {words[4]:04X}")
print()

print("Expected values:")
print("  TL = 06, TR = 07, BL = 16 (0x10), BR = 17 (0x11)")
print("  All Palette 6, Act As = 130 (0x0082)")
print()

# Check if matches
expected_reading_order = [0x06, 0x07, 0x10, 0x11]  # TL, TR, BL, BR
expected_column_major = [0x06, 0x10, 0x07, 0x11]   # TL, BL, TR, BR

if tids == expected_reading_order:
    print("✓ MATCH (Reading Order)!")
elif tids == expected_column_major:
    print("✓ MATCH (Column-Major)!")
else:
    print("✗ NO MATCH")
    print(f"  Got: {[f'{t:02X}' for t in tids]}")
    print(f"  Expected (Column): {[f'{t:02X}' for t in expected_column_major]}")
