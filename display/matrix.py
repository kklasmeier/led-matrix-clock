# display/matrix.py - LED Matrix initialization and management

import sys
import os
from typing import Optional

# Add the rpi-rgb-led-matrix library path
sys.path.append('/home/pi/rpi-rgb-led-matrix/bindings/python')

try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics # type: ignore
except ImportError as e:
    print(f"Error importing RGB matrix library: {e}")
    print("Make sure rpi-rgb-led-matrix is installed and properly configured")
    sys.exit(1)

from config import Hardware

class MatrixDisplay:
    """Manages the LED matrix hardware and provides drawing interface"""
    
    def __init__(self):
        self.matrix: Optional[RGBMatrix] = None
        self.canvas = None
        self._initialize_matrix()
    
    def _initialize_matrix(self) -> None:
        """Initialize the RGB LED matrix with proper configuration"""
        try:
            # Configure matrix options
            options = RGBMatrixOptions()
            
            # Hardware settings
            options.rows = Hardware.ROWS
            options.cols = Hardware.COLS
            options.chain_length = Hardware.CHAIN_LENGTH
            options.parallel = Hardware.PARALLEL
            
            # Performance settings
            options.gpio_slowdown = Hardware.GPIO_SLOWDOWN
            options.pwm_bits = Hardware.PWM_BITS
            options.brightness = Hardware.BRIGHTNESS
            
            # Quality settings for better display
            options.hardware_mapping = 'adafruit-hat-pwm'  # For Adafruit RGB Matrix Bonnet
            options.pwm_lsb_nanoseconds = 130
            options.led_rgb_sequence = 'RGB'
            options.disable_hardware_pulsing = True
            
            # Create the matrix
            self.matrix = RGBMatrix(options=options)
            
            # Get initial canvas
            self.canvas = self.matrix.CreateFrameCanvas() # type: ignore
            
            print(f"Matrix initialized: {options.cols}x{options.rows}")
            
        except Exception as e:
            print(f"Failed to initialize matrix: {e}")
            raise
    
    def get_canvas(self):
        """
        Get the current drawing canvas
        
        Returns:
            Canvas object for drawing operations
        """
        return self.canvas
    
    def swap_canvas(self):
        """
        Swap the current canvas to display and get a new canvas for drawing
        
        Returns:
            New canvas for the next frame
        """
        if self.matrix and self.canvas:
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
        return self.canvas
    
    def clear_canvas(self) -> None:
        """Clear the current canvas to black"""
        if self.canvas:
            self.canvas.Clear()
    
    def set_pixel(self, x: int, y: int, r: int, g: int, b: int) -> None:
        """
        Set a single pixel on the canvas
        
        Args:
            x: X coordinate (0-63)
            y: Y coordinate (0-63)
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)
        """
        if self.canvas and 0 <= x < 64 and 0 <= y < 64:
            self.canvas.SetPixel(x, y, r, g, b)
    
    def draw_line(self, x1: int, y1: int, x2: int, y2: int, r: int, g: int, b: int) -> None:
        """
        Draw a line on the canvas
        
        Args:
            x1, y1: Start coordinates
            x2, y2: End coordinates
            r, g, b: RGB color values
        """
        if self.canvas:
            graphics.DrawLine(self.canvas, x1, y1, x2, y2, graphics.Color(r, g, b))
    
    def fill_rectangle(self, x: int, y: int, width: int, height: int, r: int, g: int, b: int) -> None:
        """
        Fill a rectangle on the canvas
        
        Args:
            x, y: Top-left coordinates
            width, height: Rectangle dimensions
            r, g, b: RGB color values
        """
        if self.canvas:
            for py in range(y, y + height):
                for px in range(x, x + width):
                    if 0 <= px < 64 and 0 <= py < 64:
                        self.canvas.SetPixel(px, py, r, g, b)
    
    def cleanup(self) -> None:
        """Clean up matrix resources"""
        if self.matrix:
            self.matrix.Clear()
            print("Matrix display cleaned up")

# Global matrix instance
_matrix_display: Optional[MatrixDisplay] = None

def get_matrix_display() -> MatrixDisplay:
    """Get or create the global MatrixDisplay instance"""
    global _matrix_display
    if _matrix_display is None:
        _matrix_display = MatrixDisplay()
    return _matrix_display

def cleanup_matrix() -> None:
    """Clean up the global matrix display"""
    global _matrix_display
    if _matrix_display:
        _matrix_display.cleanup()
        _matrix_display = None