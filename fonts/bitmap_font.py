# File: rgb_matrix_lib/bitmap_font.py

import os
from typing import Dict, List, Tuple, Optional
from PIL import Image



class BitmapFontManager:
    """Manages the custom bitmap font for LED matrix display"""
    
    _instance = None  # Singleton instance
    
    @classmethod
    def get_instance(cls) -> 'BitmapFontManager':
        """Get or create the singleton instance of BitmapFontManager"""
        if cls._instance is None:
            cls._instance = BitmapFontManager()
        return cls._instance
    
    def __init__(self):
        """Initialize the bitmap font manager"""
        if BitmapFontManager._instance is not None:
            return
            
        # Change: Now stores multiple fonts
        self.font_data: Dict[str, Dict[str, List[str]]] = {}  # font_type -> char -> bitmap
        self.fonts_loaded: Dict[str, bool] = {}  # track which fonts are loaded
        self.descenders = ['g', 'j', 'p', 'q', 'y']  # Characters with descenders
        
    def load_font(self, font_type: str = "tiny64_font") -> bool:
        """Load the bitmap font data from file"""
        if self.fonts_loaded.get(font_type, False):
            return True
            
        try:
            # Get the directory of the current file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            font_filename = f"{font_type}.txt"
            font_path = os.path.join(current_dir, font_filename)
            
            # Initialize the font data dictionary for this font type
            if font_type not in self.font_data:
                self.font_data[font_type] = {}
            
            with open(font_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                        
                    # Split the line into parts
                    parts = line.split(',')
                    if len(parts) < 2:
                        continue
                    
                    # First part is the character
                    char = parts[0]
                    # Remaining parts are the bitmap rows
                    bitmap = parts[1:]
                    
                    self.font_data[font_type][char] = bitmap
            
            self.fonts_loaded[font_type] = True
            return True
            
        except Exception as e:
            print(f"Error loading bitmap font: {str(e)}")
            return False
    
    def ensure_font_loaded(self, font_type: str = "tiny64_font") -> bool:
        """Ensure the font is loaded before use"""
        if not self.fonts_loaded.get(font_type, False):
            return self.load_font(font_type)
        return True
    
    def get_char_bitmap(self, char: str, font_type: str = "tiny64_font") -> Optional[List[str]]:
        """Get the bitmap data for a character"""
        if not self.ensure_font_loaded(font_type) or not char:
            return None
            
        # Return the bitmap data if the character exists
        return self.font_data.get(font_type, {}).get(char)
    
    def get_char_dimensions(self, char: str, font_type: str = "tiny64_font") -> Tuple[int, int]:
        """Get the width and height of a character"""
        bitmap = self.get_char_bitmap(char, font_type)
        if not bitmap:
            # Default to a space character (typically 2x5)
            return (2, 5)
            
        # Width is determined by the actual width of the bitmap
        width = len(bitmap[0])
        height = len(bitmap)
        
        return (width, height)
    
    def get_text_dimensions(self, text: str, font_type: str = "tiny64_font") -> Tuple[int, int]:
        """Calculate the dimensions of a complete text string"""
        if not text or not self.ensure_font_loaded(font_type):
            return (0, 0)
            
        total_width = 0
        max_height = 5  # Default height
        
        for i, char in enumerate(text):
            width, height = self.get_char_dimensions(char, font_type)
            total_width += width
            max_height = max(max_height, height)
            
            # Add spacing between characters (except after the last one)
            if i < len(text) - 1:
                total_width += 1
        
        return (total_width, max_height)

    def create_text_image(self, text: str, font_type: str = "tiny64_font") -> Optional[Image.Image]:
        """Create a PIL Image from the bitmap font data for the given text"""
        if not text or not self.ensure_font_loaded(font_type):
            return None
            
        # Get the dimensions of the text
        width, height = self.get_text_dimensions(text, font_type)
        if width == 0 or height == 0:
            return None
            
        # Create a new blank image
        img = Image.new('RGB', (width, height), color=(0, 0, 0))
        
        # Position for drawing the next character
        x_pos = 0
        
        for char in text:
            bitmap = self.get_char_bitmap(char, font_type)
            if not bitmap:
                # Skip unknown characters
                x_pos += 2  # Default width + spacing
                continue
                
            char_width = len(bitmap[0])
            char_height = len(bitmap)
            
            # Determine vertical position (handle descenders)
            y_offset = 0
            if char in self.descenders:
                y_offset = 0
            
            # Draw the character
            for y, row in enumerate(bitmap):
                for x, pixel in enumerate(row):
                    if pixel == '1':
                        img.putpixel((x_pos + x, y_offset + y), (255, 255, 255))
            
            # Move to the next character position
            x_pos += char_width + 1  # Add spacing
        
        return img
     
    def get_bitmap_font_image(self, text: str, font_size: int = 5) -> Tuple[Image.Image, Tuple[int, int]]:
        """
        Get a PIL Image with the text rendered using the bitmap font.
        This method serves as a bridge to the existing text rendering system.
        
        Args:
            text: Text to render
            font_size: Ignored, kept for API compatibility
            
        Returns:
            A tuple containing:
            - The PIL Image with the rendered text
            - The dimensions (width, height) of the text
        """
        # Ensure font is loaded
        if not self.ensure_font_loaded():
            # Return a minimal empty image
            img = Image.new('RGB', (1, 5), color=(0, 0, 0))
            return img, (1, 5)
        
        # Get text dimensions
        dimensions = self.get_text_dimensions(text)
        
        # Create the image
        img = self.create_text_image(text)
        if img is None:
            # Return a minimal empty image
            img = Image.new('RGB', (1, 5), color=(0, 0, 0))
            return img, (1, 5)
            
        return img, dimensions
    
    def getsize(self, text: str) -> Tuple[int, int]:
        """
        Get the size of text when rendered with the bitmap font.
        This method mimics the PIL ImageFont.getsize method for compatibility.
        
        Args:
            text: Text to measure
            
        Returns:
            A tuple containing the width and height of the text
        """
        return self.get_text_dimensions(text)


# Helper function to access the bitmap font
def get_bitmap_font_manager() -> BitmapFontManager:
    """Get the singleton instance of the BitmapFontManager"""
    return BitmapFontManager.get_instance()


class BitmapFontAdapter:
    """
    Adapter class to make the bitmap font compatible with
    the existing text rendering system that expects PIL ImageFont objects
    """
    
    def __init__(self, font_size: int = 5, font_type: str = "tiny64_font"):
        """
        Initialize the adapter with the bitmap font manager
        
        Args:
            font_size: Ignored, kept for API compatibility
            font_type: Which bitmap font to use ("tiny64_font" or "clock64_font")
        """
        self.font_manager = BitmapFontManager.get_instance()
        self.font_type = font_type
        
        # Load the specific font
        self.font_manager.load_font(font_type)
        
    def getsize(self, text: str) -> Tuple[int, int]:
        """
        Get the size of text when rendered with the bitmap font
        
        Args:
            text: Text to measure
            
        Returns:
            A tuple containing the width and height of the text
        """
        return self.font_manager.get_text_dimensions(text, self.font_type)
    