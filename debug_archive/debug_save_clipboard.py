import ctypes
from ctypes import wintypes
import sys

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Define 64-bit types
kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalLock.restype = ctypes.c_void_p
kernel32.GlobalSize.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalSize.restype = ctypes.c_size_t
kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
user32.GetClipboardData.restype = wintypes.HGLOBAL

def main():
    if not user32.OpenClipboard(None):
        print("Cannot open clipboard")
        return
    try:
        fmt_name = "Lunar Magic 16x16 Tiles"
        fmt = user32.RegisterClipboardFormatW(fmt_name)
        
        if fmt == 0:
            print(f"Format '{fmt_name}' not found/registered.")
            return

        print(f"Format ID: {fmt}")
        
        if not user32.IsClipboardFormatAvailable(fmt):
             print("Format available: NO")
             print("Please copy something in Lunar Magic first.")
             return
        
        hMem = user32.GetClipboardData(fmt)
        if hMem:
            pMem = kernel32.GlobalLock(hMem)
            size = kernel32.GlobalSize(hMem)
            if pMem and size > 0:
                data = ctypes.string_at(pMem, size)
                filename = "clipboard_dump.bin"
                with open(filename, "wb") as f:
                    f.write(data)
                print(f"Saved {size} bytes to {filename}")
                print(f"Hex: {data.hex()[:64]}...")
            kernel32.GlobalUnlock(hMem)
        else:
            print("GetClipboardData returned None")
            
    finally:
        user32.CloseClipboard()

if __name__ == "__main__":
    main()
