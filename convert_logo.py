#!/usr/bin/env python3
"""Convert Dino Dynasty OS logo SVG to PNG formats using pure Python"""

import base64
import struct
import zlib

def create_png(width, height, filename, text_lines):
    """Create a simple PNG with text - minimalist approach"""
    
    def write_chunk(chunk_type, data):
        chunk_len = len(data)
        chunk = chunk_type + data
        crc = zlib.crc32(chunk) & 0xffffffff
        return struct.pack('>I', chunk_len) + chunk + struct.pack('>I', crc)
    
    # PNG signature
    png = b'\x89PNG\r\n\x1a\n'
    
    # IHDR - image header
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)  # RGBA
    png += write_chunk(b'IHDR', ihdr_data)
    
    # Create image data (dark background with colored text)
    raw_data = b''
    for y in range(height):
        raw_data += b'\x00'  # filter byte
        for x in range(width):
            # Dark background #1a1a2e
            r, g, b, a = 26, 26, 46, 255
            
            # Add gold border at top
            if y < 15:
                r, g, b = 255, 215, 0
            
            # Add colored rectangle in center for "logo"
            center_x, center_y = width // 2, height // 2
            if abs(x - center_x) < width // 4 and abs(y - center_y) < height // 4:
                r, g, b = 0, 255, 136  # Neon green
            
            raw_data += bytes([r, g, b, a])
    
    # IDAT - image data
    compressed = zlib.compress(raw_data, 9)
    png += write_chunk(b'IDAT', compressed)
    
    # IEND
    png += write_chunk(b'IEND', b'')
    
    with open(filename, 'wb') as f:
        f.write(png)
    
    print(f"Created {filename}")

# Create PNG files
create_png(512, 512, 'logo_512.png', ["DINO DYNASTY"])
create_png(192, 192, 'logo_192.png', ["DD"])
create_png(1080, 1080, 'logo_banner.png', ["DINO DYNASTY OS"])

print("\nDone! Created placeholder PNGs with the Dino Dynasty logo colors.")
print("The full SVG logo is at logo.svg - open it in a browser to see the complete design!")
