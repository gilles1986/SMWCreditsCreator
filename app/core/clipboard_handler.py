import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

GMEM_MOVEABLE = 0x0002
GMEM_ZEROINIT = 0x0040

class ClipboardHandler:
    @staticmethod
    def copy_map16(binary_data):
        """
        Copies binary data to clipboard using 'Lunar Magic Map16 Tiles' format.
        Also sets CF_TEXT as fallback if needed (optional, but good for debug).
        """
        # Define types for 64-bit compatibility
        kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
        kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
        kernel32.GlobalLock.restype = ctypes.c_void_p
        kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
        user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HGLOBAL]

        # 1. Register Format
        # Correct format name discovered via debug
        fmt_name = "Lunar Magic 16x16 Tiles" 
        u_format = user32.RegisterClipboardFormatW(fmt_name)
        
        if u_format == 0:
            print("Failed to register clipboard format")
            return False

        if not user32.OpenClipboard(None):
            return False
            
        try:
            user32.EmptyClipboard()
            
            # --- Set Native Format ---
            size = len(binary_data)
            hMem = kernel32.GlobalAlloc(GMEM_MOVEABLE, size)
            if hMem:
                print(f"[DEBUG] hMem: {hMem}")
                pMem = kernel32.GlobalLock(hMem)
                print(f"[DEBUG] pMem: {pMem}")
                
                if not pMem:
                    print("[DEBUG] GlobalLock failed.")
                    
                # Robustly convert to C-buffer
                src_buffer = (ctypes.c_char * size).from_buffer_copy(binary_data)
                ctypes.memmove(pMem, ctypes.addressof(src_buffer), size)
                
                kernel32.GlobalUnlock(hMem)
                
                # SetClipboardData takes ownership of hMem on success
                if not user32.SetClipboardData(u_format, hMem):
                     kernel32.GlobalFree(hMem)
                     user32.CloseClipboard()
                     return False

        finally:
            user32.CloseClipboard()
            
        return True
