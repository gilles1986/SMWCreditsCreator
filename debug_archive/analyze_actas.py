#!/usr/bin/env python
import struct

data = open('page8_export3.map16', 'rb').read()

print("Analyzing Tile 812 with Act-As changed to 2B:")
print("=" * 70)

idx = 0x12
offset = 176 + (idx * 10)
tile_bytes = data[offset:offset+10]
words = struct.unpack('<5H', tile_bytes)

print(f"Tile 812 (File Index {idx:02X}):")
print(f"  Raw bytes: {tile_bytes.hex()}")
print(f"  Words: {[f'{w:04X}' for w in words]}")
print(f"  Act-As (Word 4): 0x{words[4]:04X} ({words[4]} decimal)")
print()

print("Interpretation:")
if words[4] == 0x002B:
    print("  ✓ Act-As=0x002B matches input '2B'")
    print("  → Lunar Magic stores hex value directly!")
elif words[4] == 43:  # 2B hex = 43 decimal
    print("  ✓ Act-As=43 (0x2B decimal)")
    print("  → Lunar Magic converts hex input to decimal!")
else:
    print(f"  ? Act-As=0x{words[4]:04X} - unexpected value")

print()
print("Now checking what 130 becomes:")
print("  130 decimal = 0x0082")
print("  130 as hex literal = 0x0130")
print()

# Check other tiles for their Act-As
print("Checking other tiles in this file:")
for test_idx in [0x00, 0x02, 0x04, 0x10, 0x14]:
    offset = 176 + (test_idx * 10)
    tb = data[offset:offset+10]
    w = struct.unpack('<5H', tb)
    print(f"  Tile 08{test_idx:02X}: Act-As = 0x{w[4]:04X}")
