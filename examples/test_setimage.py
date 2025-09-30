#!/usr/bin/env python
# test_setimage.py - Test if canvas.SetImage() exists and works

import sys
import time
sys.path.append('/home/pi/rpi-rgb-led-matrix/bindings/python')

from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw, ImageFont

def test_setimage():
    """Test if SetImage method exists and works"""
    
    print("Initializing matrix...")
    
    # Configure matrix
    options = RGBMatrixOptions()
    options.rows = 64
    options.cols = 64
    options.chain_length = 1
    options.parallel = 1
    options.gpio_slowdown = 4
    options.pwm_bits = 11
    options.brightness = 100
    options.hardware_mapping = 'adafruit-hat-pwm'
    
    # Create matrix
    matrix = RGBMatrix(options=options)
    
    # Create a test PIL image (64x64 with some colored elements)
    print("Creating test PIL image...")
    test_image = Image.new('RGB', (64, 64), (0, 0, 0))
    draw = ImageDraw.Draw(test_image)
    
    # Draw some test patterns
    draw.rectangle([10, 10, 30, 30], fill=(255, 0, 0))    # Red square
    draw.rectangle([34, 10, 54, 30], fill=(0, 255, 0))    # Green square
    draw.rectangle([10, 34, 30, 54], fill=(0, 0, 255))    # Blue square
    draw.rectangle([34, 34, 54, 54], fill=(255, 255, 0))  # Yellow square
    
    print("\nTesting canvas methods:")
    
    # Get canvas
    canvas = matrix.CreateFrameCanvas()
    
    # Check if SetImage exists
    if hasattr(canvas, 'SetImage'):
        print("✓ SetImage method EXISTS!")
        print("  Attempting to use SetImage()...")
        
        try:
            # Try using SetImage
            start_time = time.time()
            canvas.SetImage(test_image)
            elapsed = time.time() - start_time
            
            print(f"  ✓ SetImage() WORKED! Time: {elapsed*1000:.2f}ms")
            
            # Swap to display
            matrix.SwapOnVSync(canvas)
            print("  Display updated successfully")
            
            # Keep it visible for a few seconds
            time.sleep(3)
            
            return True
            
        except Exception as e:
            print(f"  ✗ SetImage() exists but FAILED: {e}")
            return False
    else:
        print("✗ SetImage method DOES NOT EXIST")
        print("\nAvailable canvas methods:")
        methods = [m for m in dir(canvas) if not m.startswith('_')]
        for method in sorted(methods):
            print(f"  - {method}")
        
        # Fall back to pixel-by-pixel test
        print("\nFalling back to SetPixel test...")
        start_time = time.time()
        
        for y in range(64):
            for x in range(64):
                pixel = test_image.getpixel((x, y))
                canvas.SetPixel(x, y, pixel[0], pixel[1], pixel[2])
        
        elapsed = time.time() - start_time
        print(f"  SetPixel for full frame: {elapsed*1000:.2f}ms")
        
        matrix.SwapOnVSync(canvas)
        time.sleep(3)
        
        return False
    
    # Cleanup
    matrix.Clear()

if __name__ == "__main__":
    try:
        has_setimage = test_setimage()
        
        if has_setimage:
            print("\n" + "="*50)
            print("RESULT: SetImage() is available!")
            print("This could significantly speed up rendering.")
            print("="*50)
        else:
            print("\n" + "="*50)
            print("RESULT: SetImage() is NOT available.")
            print("Pixel-by-pixel copying is the only option.")
            print("="*50)
            
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()