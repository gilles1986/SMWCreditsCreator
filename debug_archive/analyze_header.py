import struct

with open("clipboard_dump.bin", "rb") as f:
    data = f.read()

print(f"Total Size: {len(data)}")

header = data[:160]
print("--- Header Non-Zero ---")
for i, b in enumerate(header):
    if b != 0:
        print(f"Offset {i} (0x{i:X}): {b} (0x{b:X})")

print("--- Data ---")
print(data[160:].hex())
