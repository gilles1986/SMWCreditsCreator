import os

# Find any map16 file that might be the reference (e.g. page14)
files = [f for f in os.listdir('.') if f.endswith('.map16') and ('page14' in f.lower() or '14' in f)]

if not files:
    print("No 'page14' map16 file found.")
    print("Please export Page 14 (0x0E) from Lunar Magic and save it as 'page14.map16' in this folder.")
else:
    f = files[0]
    print(f"Analyzing {f}...")
    data = open(f, 'rb').read()
    header = data[:176]
    
    print("-" * 60)
    print(f"Header Hex ({len(header)} bytes):")
    print(header.hex())
    print("-" * 60)
    
    # Check suspected offsets for Page 14 (0x0E)
    # Expected Base: 0x0E00 (00 0E 00 00)
    
    print(f"Offset 116 (0x74): {header[116:120].hex()} (Should be 000e0000?)")
    print(f"Offset 120 (0x78): {header[120:124].hex()} (Should be b00e0000?)")
    
    # Search for 0x0E in header
    print("Searching for 0x0E in header:")
    for i, b in enumerate(header):
        if b == 0x0E:
             print(f"at Offset {i} (0x{i:X})")
