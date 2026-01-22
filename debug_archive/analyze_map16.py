import os
import struct

path = 'd:/dev/work/SMWCreditsCreator/smwprojects/Blindrace_Kuesti/Page2.map16'

with open(path, 'rb') as f:
    data = f.read()

print(f"File size: {len(data)}")

# Header seems to end around 0xB0 or similar?
# "Lunar Magic 3.40" string is in there.

# Try to find where repetitive data starts.
# We expect 256 items.
# If item size is 10 bytes: 2560 bytes.
# Header = len - 2560 = 176 bytes?

header_size = 176
if len(data) >= 2560 + header_size:
    print(f"Assuming header size {header_size}")
    header = data[:header_size]
    content = data[header_size:]
    
    # Analyze first tile (Tile 0 on Page 2 -> "200")
    # Content format guess: 
    # 2 bytes ActAs
    # 2 bytes TL
    # 2 bytes BL
    # 2 bytes TR
    # 2 bytes BR
    # OR some other order.

    print("First 5 tiles hex:")
    for i in range(5):
        chunk = content[i*10 : (i+1)*10]
        print(f"Tile {i}: {chunk.hex()}")
        
else:
    print("Size didn't match 2560 + 176 hypothesis.")
