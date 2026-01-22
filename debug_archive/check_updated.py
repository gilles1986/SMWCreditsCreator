#!/usr/bin/env python
import struct

data = open('page8.map16', 'rb').read()

print("Checking tiles 812, 813, 814 in updated file:")
print("=" * 60)

for display_tile in [0x812, 0x813, 0x814]:
    # With +4 offset: file index = (display_tile & 0xFF) - 4
    file_idx = (display_tile & 0xFF) - 4
    offset = 176 + file_idx * 10
    
    tile_bytes = data[offset:offset+10]
    words = struct.unpack('<5H', tile_bytes)
    
    print(f"\nTile {display_tile:04X} (File Index {file_idx:02X}):")
    print(f"  Raw bytes: {tile_bytes.hex()}")
    
    # Current interpretation (Column-Major storage):
    # Word0=TL, Word1=BL, Word2=TR, Word3=BR
    tids = [words[0] & 0x3FF, words[1] & 0x3FF, words[2] & 0x3FF, words[3] & 0x3FF]
    pals = [(words[i] >> 10) & 0x7 for i in range(4)]
    
    print(f"  Subtiles (current order): TL={tids[0]:02X}, BL={tids[1]:02X}, TR={tids[2]:02X}, BR={tids[3]:02X}")
    print(f"  Palettes: {pals}")
    print(f"  Act As: {words[4]:04X}")
    
    # Show all 4 tile IDs
    print(f"  All subtiles seen: {[f'{t:02X}' for t in tids]}")
