#!/usr/bin/env python
import struct

data = open('page8_export2.map16', 'rb').read()

print("Checking if Act-As values are correct (should be 130 = 0x0082):")
print()

for idx in [0x00, 0x02, 0x04, 0x10, 0x12, 0x14]:
    offset = 176 + (idx * 10)
    tile_bytes = data[offset:offset+10]
    words = struct.unpack('<5H', tile_bytes)
    
    print(f"File Index {idx:02X} (Tile 08{idx:02X}):")
    print(f"  Raw: {tile_bytes.hex()}")
    print(f"  Act-As (Word 4): {words[4]:04X} ({'✓ CORRECT' if words[4] == 0x0082 else '✗ WRONG'})")
    print()
