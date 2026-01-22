#!/usr/bin/env python
"""
Compare donut_only.map16 (working) vs page8_export3.map16 (broken?)
to understand the format difference
"""
import struct

print("=" * 70)
print("COMPARING EXPORT FORMATS")
print("=" * 70)

# Working file: donut_only.map16
with open('donut_only.map16', 'rb') as f:
    donut_data = f.read()

# Broken file: page8_export3.map16  
with open('page8_export3.map16', 'rb') as f:
    page_data = f.read()

print(f"\ndonut_only.map16: {len(donut_data)} bytes")
print(f"page8_export3.map16: {len(page_data)} bytes")

print("\n" + "=" * 70)
print("HEADERS:")
print("=" * 70)

print(f"donut header (16 bytes): {donut_data[:16].hex()}")
print(f"page header (16 bytes):  {page_data[:16].hex()}")

if donut_data[:16] == page_data[:16]:
    print("✓ Headers match")
else:
    print("✗ Headers differ!")

print("\n" + "=" * 70)
print("FIRST TILE DATA:")
print("=" * 70)

donut_tile = donut_data[176:186]
page_tile = page_data[176:186]

print(f"donut first tile: {donut_tile.hex()}")
print(f"page first tile:  {page_tile.hex()}")

d_words = struct.unpack('<5H', donut_tile)
p_words = struct.unpack('<5H', page_tile)

print(f"\ndonut words: {[f'{w:04X}' for w in d_words]}")
print(f"page words:  {[f'{w:04X}' for w in p_words]}")

print(f"\ndonut Act-As: 0x{d_words[4]:04X}")
print(f"page Act-As:  0x{p_words[4]:04X}")

print("\n" + "=" * 70)
print("HYPOTHESIS:")
print("=" * 70)
print("Maybe full-page exports don't include Act-As in the tile data?")
print("Or Act-As is stored separately for page exports?")
print("\nLet's check the header beyond first 16 bytes:")

print(f"\ndonut header[16:176]: {donut_data[16:176].hex()[:100]}...")
print(f"page header[16:176]:  {page_data[16:176].hex()[:100]}...")

# Check if there's a pattern in the extended header
if donut_data[16:176] != page_data[16:176]:
    print("\n✗ Extended headers differ - Act-As might be stored differently!")
