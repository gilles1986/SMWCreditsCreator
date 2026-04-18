from PIL import Image
import struct
import logging

logger = logging.getLogger(__name__)

class SNESGraphics:
    @staticmethod
    def decode_4bpp(data):
        """
        Decodes SNES 4BPP graphics data into a list of pixel indices (0-15).
        Input: bytes
        Output: list of integers (0-15), 8x8 tiles linear
        """
        pixels = []
        tile_size = 32 # 8x8 pixels * 4 bits = 32 bytes
        
        num_tiles = len(data) // tile_size
        
        for t in range(num_tiles):
            tile_data = data[t*tile_size : (t+1)*tile_size]
            
            # 4BPP format: 
            # Planes 0,1 are interleaved in first 16 bytes
            # Planes 2,3 are interleaved in next 16 bytes
            
            for row in range(8):
                # Plane 0 and 1
                b0 = tile_data[row * 2]
                b1 = tile_data[row * 2 + 1]
                
                # Plane 2 and 3 (offset by 16 bytes)
                b2 = tile_data[16 + row * 2]
                b3 = tile_data[16 + row * 2 + 1]
                
                for col in range(8):
                    mask = 1 << (7 - col)
                    
                    p0 = (b0 & mask) >> (7 - col)
                    p1 = (b1 & mask) >> (7 - col)
                    p2 = (b2 & mask) >> (7 - col)
                    p3 = (b3 & mask) >> (7 - col)
                    
                    color_index = p0 + (p1 << 1) + (p2 << 2) + (p3 << 3)
                    pixels.append(color_index)
                    
        return pixels, num_tiles

    @staticmethod
    def create_image(pixels, width_in_tiles, palette=None):
        """
        Creates a PIL Image from decoded pixels.
        width_in_tiles: Number of tiles per row in the output image.
        palette: Usage: list of (R,G,B) tuples. Length 16.
        """
        num_tiles = len(pixels) // 64
        height_in_tiles = (num_tiles + width_in_tiles - 1) // width_in_tiles
        
        img_width = width_in_tiles * 8
        img_height = height_in_tiles * 8
        
        img = Image.new('RGB', (img_width, img_height))
        pixel_data = img.load()
        
        if palette is None:
            # Default grayscale palette
            palette = []
            for i in range(16):
                val = i * 17 # 0-15 -> 0-255
                palette.append((val, val, val))
                
        for t in range(num_tiles):
            base_x = (t % width_in_tiles) * 8
            base_y = (t // width_in_tiles) * 8
            
            tile_pixels = pixels[t*64 : (t+1)*64]
            
            for i, p in enumerate(tile_pixels):
                row = i // 8
                col = i % 8
                color = palette[p]
                pixel_data[base_x + col, base_y + row] = color
                
        return img

    @staticmethod
    def decode_palette(data):
        """
        Decodes Palette data. Supports:
        1. JASC-PAL (Text)
        2. Binary RGB (3 bytes/color)
        3. SNES BGR (2 bytes/color)
        """
        # 1. Check for JASC-PAL (Paint Shop Pro) Text Format
        if data.startswith(b'JASC-PAL'):
            try:
                text = data.decode('ascii', errors='ignore')
                lines = text.splitlines()
                # Skip header lines (JASC-PAL, version, count)
                colors = []
                start_idx = 0
                for idx, line in enumerate(lines):
                    if len(line.strip().split()) == 3:
                         # Heuristic: finding first line with 3 numbers
                         # after header
                         if idx >= 3: 
                             start_idx = idx
                             break
                
                if start_idx == 0 and len(lines) > 3: start_idx = 3 # Default assumption

                for line in lines[start_idx:]:
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        try:
                            r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
                            colors.append((r, g, b))
                        except (ValueError, TypeError): pass
            except Exception as e:
                logger.warning("JASC-PAL decode error: %s", e)
        
        # 2. Check for Binary RGB (3 bytes per color)
        # Common sizes: 768 (256 colors), 48 (16 colors)
        # Use modulo 3 check. SNES sizes (512, 32) are NOT divisible by 3.
        if len(data) % 3 == 0 and len(data) > 0:
             colors = []
             for i in range(0, len(data), 3):
                 r = data[i]
                 g = data[i+1]
                 b = data[i+2]
                 colors.append((r, g, b))
             return colors

        # 3. Default: Binary SNES BGR (2 bytes per color)
        colors = []
        num_colors = len(data) // 2
        for i in range(num_colors):
            val = int.from_bytes(data[i*2:i*2+2], byteorder='little')
            # Format: 0BBBBBGGGGGRRRRR (Standard SNES)
            r5 = (val & 0x1F)
            g5 = (val >> 5) & 0x1F
            b5 = (val >> 10) & 0x1F
            
            # Scale 5-bit to 8-bit
            r = (r5 * 255) // 31
            g = (g5 * 255) // 31
            b = (b5 * 255) // 31
            colors.append((r, g, b))
        return colors
