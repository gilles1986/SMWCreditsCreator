import struct

path = 'd:/dev/work/SMWCreditsCreator/smwprojects/Blindrace_Kuesti/Page2.map16'

with open(path, 'rb') as f:
    data = f.read()

header = data[:176]
content = data[176:]

print(f"Header: {header[:16].hex()} ...")

# Analyze first 3 tiles (30 bytes)
# We expect 5 words per tile.
print("-" * 30)
for i in range(3):
    offset = i * 10
    tile_data = content[offset : offset + 10]
    words = struct.unpack('<HHHHH', tile_data)
    print(f"Tile {i} (Hex): {tile_data.hex()}")
    print(f"Tile {i} (Words): {words}")
    
    # helper to print word details
    def print_word(name, w):
        tile_id = w & 0x3FF
        pal = (w >> 10) & 7
        prio = (w >> 13) & 1
        flip_x = (w >> 14) & 1
        flip_y = (w >> 15) & 1
        print(f"  {name}: {w:04X} -> Tile:{tile_id:03X} Pal:{pal} P:{prio} X:{flip_x} Y:{flip_y}")

    # Hypothesis: TL, BL, TR, BR, ActAs
    # OR TL, TR, BL, BR, ActAs
    
    # We know Tile 0 of Page 2 (200) likely uses some 8x8 tiles.
    # Let's see what they are.
    print_word("Word 0", words[0])
    print_word("Word 1", words[1])
    print_word("Word 2", words[2])
    print_word("Word 3", words[3])
    print_word("Word 4", words[4])
