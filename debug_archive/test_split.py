#!/usr/bin/env python
"""
Test Hypothesis:
Full page export separates Tile Data and Act-As Data.
Structure:
  Header: 176 bytes
  Tile Data: 2048 bytes (4 words * 256 tiles)
  Act-As Data: 512 bytes (1 word * 256 tiles)
"""
import struct

data = open('page8_export3.map16', 'rb').read()

header_size = 176
tile_data_size = 2048
act_as_offset = header_size + tile_data_size

print("=" * 70)
print("TESTING SPLIT DATA HYPOTHESIS")
print("=" * 70)
print(f"Header size: {header_size}")
print(f"Tile Data size (estimated): {tile_data_size}")
print(f"Act-As Data offset (estimated): {act_as_offset}")
print(f"File size: {len(data)}")
print()

# Check Act-As block
print("Checking Act-As block at offset 2224:")
act_as_data = data[act_as_offset:]
print(f"Remaining bytes: {len(act_as_data)}")

if len(act_as_data) == 512:
    print("✓ Exactly 512 bytes remaining (matches 256 * 2 bytes!)")
    
    # Parse as words
    act_as_words = struct.unpack('<256H', act_as_data)
    
    # Check specific tiles
    # Tile 812 (Index 0x12) should be 0x002B (User said "2B")
    val_812 = act_as_words[0x12]
    print(f"  Tile 812 Act-As: 0x{val_812:04X}")
    if val_812 == 0x002B:
        print("    ✓ MATCHES EXPECTED 0x002B!")
    else:
        print("    ✗ No match (expected 0x002B)")

    # Check defaults (130 = 0x82)
    # Most tiles should be 130
    val_800 = act_as_words[0x00]
    print(f"  Tile 800 Act-As: 0x{val_800:04X} (Expected 0x0082)")
    
    # Check 16x16 editor logic
    # Maybe 0x0130?
else:
    print("✗ Remaining bytes is not 512")

print("\n" + "=" * 70)
print("Checking Tile Data Structure (First 2048 bytes)")
# If split, then first 2048 bytes = stream of 4-word tuples? 
# Or stream of Word0s, then Word1s?
# Let's check Tile 814 (Index 0x14 - Wait, user said 814 data is at 0x10?)
# Let's assume sequential 4-word blocks

tile_block = data[header_size:act_as_offset]
# Read tile 800 (Index 0)
print("Tile 800 (Index 0):")
t0_bytes = tile_block[0:8]
t0_words = struct.unpack('<4H', t0_bytes)
print(f"  Words: {[f'{w:04X}' for w in t0_words]}")
# Earlier analysis of Index 0 showed: 85, 95, 86, 96
# That was assuming 5-word structure (10 bytes).
# If 4-word structure (8 bytes), then Index 0 is just first 8 bytes.
# The previous analysis [Step 432] read `850c 950c 860c 960c 0410` (10 bytes)
# The first 4 words were `0C85 0C95 0C86 0C96`.
# This matches.

# Does Index 1 start at byte 8 or byte 10?
# If split, it starts at byte 8.
# Let's check Index 1 (Byte 8-16)
t1_bytes = tile_block[8:16]
t1_words = struct.unpack('<4H', t1_bytes)
print(f"Tile 801 (Index 1) assumed at offset 8:")
print(f"  Words: {[f'{w:04X}' for w in t1_words]}")
# Previous analysis (Step 432) at Index 1 (Offset 10) was `04 04 04 1C5`
# The 10-byte read shifted everything.
# If format is 8-byte, then:
# Byte 0-8: Tile 0
# Byte 8-16: Tile 1
# Byte 16-24: Tile 2
# ...
# Let's check if this aligns with "File Index 10 -> Tile 814" mystery
