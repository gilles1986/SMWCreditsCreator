#!/usr/bin/env python
"""
Detailed byte analysis to find correct subtile order
Compare what we parse vs what should be according to user
"""
import struct

data = open('page8_export2.map16', 'rb').read()
header_size = 176

print("=" * 70)
print("BYTE-LEVEL ANALYSIS")
print("=" * 70)

# Test cases from user
test_cases = [
    {
        'file_idx': 0x00,
        'tile_num': 0x800,
        'expected': {'TL': 0x85, 'TR': 0x86, 'BL': 0x95, 'BR': 0x96, 'ActAs': 0x130}
    },
    {
        'file_idx': 0x02,
        'tile_num': 0x802,
        'expected': {'TL': 0x1C5, 'TR': 0x1C6, 'BL': 0x1D5, 'BR': 0x1D6, 'ActAs': 0x130}
    },
    {
        'file_idx': 0x04,
        'tile_num': 0x804,
        'expected': {'TL': 0x2BC, 'TR': 0x2BD, 'BL': 0x2CC, 'BR': 0x2CD, 'ActAs': 0x130}
    },
]

for test in test_cases:
    idx = test['file_idx']
    offset = header_size + (idx * 10)
    tile_bytes = data[offset:offset+10]
    
    print(f"\nTile {test['tile_num']:04X} (File Index {idx:02X}):")
    print(f"  Raw bytes: {tile_bytes.hex()}")
    
    # Parse as little-endian words
    words = struct.unpack('<5H', tile_bytes)
    print(f"  Words (LE): {[f'{w:04X}' for w in words]}")
    
    # Extract tile IDs from each word
    tile_ids = [(w & 0x3FF) for w in words]
    print(f"  Tile IDs: {[f'{tid:02X}' for tid in tile_ids]}")
    
    # Expected values
    exp = test['expected']
    print(f"\n  Expected:")
    print(f"    TL={exp['TL']:02X}, TR={exp['TR']:02X}, BL={exp['BL']:02X}, BR={exp['BR']:02X}")
    print(f"    ActAs={exp['ActAs']:04X}")
    
    # Try different word orderings
    print(f"\n  Testing different word orders:")
    
    # Option 1: Reading Order (0, 1, 2, 3)
    if (tile_ids[0] == exp['TL'] and tile_ids[1] == exp['TR'] and 
        tile_ids[2] == exp['BL'] and tile_ids[3] == exp['BR']):
        print(f"    ✓ Reading Order (TL=W0, TR=W1, BL=W2, BR=W3)")
    
    # Option 2: Column Major (0, 2, 1, 3)
    if (tile_ids[0] == exp['TL'] and tile_ids[2] == exp['TR'] and 
        tile_ids[1] == exp['BL'] and tile_ids[3] == exp['BR']):
        print(f"    ✓ Column Major (TL=W0, BL=W1, TR=W2, BR=W3)")
    
    # Option 3: Mixed (try all permutations to find match)
    from itertools import permutations
    for perm in permutations([0, 1, 2, 3]):
        if (tile_ids[perm[0]] == exp['TL'] and tile_ids[perm[1]] == exp['TR'] and
            tile_ids[perm[2]] == exp['BL'] and tile_ids[perm[3]] == exp['BR']):
            if perm != (0, 1, 2, 3) and perm != (0, 2, 1, 3):  # Skip already printed
                print(f"    ✓ Custom Order: W{perm[0]}→TL, W{perm[1]}→TR, W{perm[2]}→BL, W{perm[3]}→BR")
    
    # Check Act As
    if words[4] == exp['ActAs']:
        print(f"    ✓ ActAs=W4 matches ({words[4]:04X})")
    else:
        print(f"    ✗ ActAs mismatch: Got {words[4]:04X}, Expected {exp['ActAs']:04X}")

print("\n" + "=" * 70)
