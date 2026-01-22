#!/usr/bin/env python
"""
Create a visual comparison of what should be vs what is in the file
"""
import struct

print("=" * 70)
print("DIAGNOSTIC: Tile 812 Analysis")
print("=" * 70)

# Expected values
print("\n1. EXPECTED (from user description):")
print("   TL=06, TR=07, BL=16, BR=17")
print("   Palette=6, Flags=--- (no flips/priority)")
print("   Act As=130 (0x0082)")

# Calculate expected binary (Column-Major: TL, BL, TR, BR)
print("\n2. EXPECTED BINARY (Column-Major TL, BL, TR, BR):")

def encode_subtile(tile_id, palette, flip_x=False, flip_y=False, priority=False):
    """Encode a subtile into a 16-bit word"""
    val = (tile_id & 0x3FF)
    val |= ((palette & 0x7) << 10)
    val |= (1 << 13 if priority else 0)
    val |= (1 << 14 if flip_x else 0)
    val |= (1 << 15 if flip_y else 0)
    return val

# Column-Major order: TL, BL, TR, BR
w0_tl = encode_subtile(0x06, 6)
w1_bl = encode_subtile(0x10, 6)  
w2_tr = encode_subtile(0x07, 6)
w3_br = encode_subtile(0x11, 6)
w4_act = 0x0082

expected_bytes = struct.pack('<5H', w0_tl, w1_bl, w2_tr, w3_br, w4_act)
print(f"   Hex: {expected_bytes.hex()}")
print(f"   Words: {[f'{w:04X}' for w in [w0_tl, w1_bl, w2_tr, w3_br, w4_act]]}")

# Actual file content
print("\n3. ACTUAL IN FILE (page8_export.map16):")
with open('page8_export.map16', 'rb') as f:
    data = f.read()

offset = 176 + (0x0E * 10)
actual_bytes = data[offset:offset+10]
actual_words = struct.unpack('<5H', actual_bytes)

print(f"   Hex: {actual_bytes.hex()}")
print(f"   Words: {[f'{w:04X}' for w in actual_words]}")

# Decode actual
print("\n4. DECODED ACTUAL:")
for i, name in enumerate(['TL', 'BL', 'TR', 'BR']):
    w = actual_words[i]
    tile_id = w & 0x3FF
    palette = (w >> 10) & 0x7
    print(f"   {name}={tile_id:02X}, Pal={palette}")
print(f"   Act As={actual_words[4]:04X}")

print("\n5. COMPARISON:")
if actual_bytes == expected_bytes:
    print("   ✓ MATCH - File contains correct data!")
else:
    print("   ✗ MISMATCH - File does NOT contain expected values!")
    print(f"\n   Expected: {expected_bytes.hex()}")
    print(f"   Got:      {actual_bytes.hex()}")

print("\n" + "=" * 70)
print("NEXT STEPS:")
print("If file doesn't match:")
print("1. In Lunar Magic, go to tile 812")
print("2. Verify it shows: 6, 7, 16, 17 in the tile comp editor")
print("3. File → Export → Map16 Data (select ONLY page 8)")
print("4. Save as 'page8_correct.map16'")
print("=" * 70)
