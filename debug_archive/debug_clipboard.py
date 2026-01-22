import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def get_format_name(fmt):
    formats = {
        1: "CF_TEXT", 2: "CF_BITMAP", 7: "CF_OEMTEXT", 8: "CF_DIB", 13: "CF_UNICODETEXT", 15: "CF_HDROP"
    }
    if fmt in formats: return formats[fmt]
    buff = ctypes.create_unicode_buffer(256)
    if user32.GetClipboardFormatNameW(fmt, buff, 256): return buff.value
    return f"Unknown ({fmt})"

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
        fmt = 0
        print("Enumerating formats...")
        while True:
            fmt = user32.EnumClipboardFormats(fmt)
            if fmt == 0: 
                print("End of enumeration.")
                break
            
            name = get_format_name(fmt)
            print(f"\nFormat: {fmt} ({name})")
            
            kernel32.SetLastError(0)
            hMem = user32.GetClipboardData(fmt)
            print(f"  hMem: {hMem}")
            
            if not hMem:
                err = kernel32.GetLastError()
                print(f"  GetClipboardData failed. Error: {err}")
                continue

            pData = kernel32.GlobalLock(hMem)
            print(f"  pData: {pData}")
            if not pData:
                print("  GlobalLock failed")
                continue
                
            size = kernel32.GlobalSize(hMem)
            print(f"  Size: {size}")
            
            if size > 0:
                data = ctypes.string_at(pData, size)
                print(f"  Hex Peak: {data.hex()[:64]}...") 
            else:
                print("  Data is empty.")
            
            kernel32.GlobalUnlock(hMem)
            
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        user32.CloseClipboard()

if __name__ == "__main__":
    main()
