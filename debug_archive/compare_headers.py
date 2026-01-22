import os

def load_file(partial_name):
    files = [f for f in os.listdir('.') if f.endswith('.map16') and partial_name in f.lower()]
    if not files: return None, None
    return files[0], open(files[0], 'rb').read()

f8, d8 = load_file('page8')
f14, d14 = load_file('page14')

if not d8 or not d14:
    print("Need both 'page8.map16' and 'page14.map16' (from Lunar Magic) to compare.")
    print(f"Found Page 8: {f8}")
    print(f"Found Page 14: {f14}")
else:
    print(f"Comparing {f8} vs {f14}...")
    if len(d8) != len(d14):
        print(f"Size Mismatch! {len(d8)} vs {len(d14)}")
    
    diff_count = 0
    # Compare first 200 bytes (Header area)
    limit = 200
    print(f"Differences in first {limit} bytes:")
    
    for i in range(limit):
        b8 = d8[i]
        b14 = d14[i]
        if b8 != b14:
            print(f"Offset {i} (0x{i:X}): Page8=0x{b8:X} vs Page14=0x{b14:X}")
            diff_count += 1
            if diff_count >= 10: 
                print("... (Stopping after 10 diffs)")
                break

