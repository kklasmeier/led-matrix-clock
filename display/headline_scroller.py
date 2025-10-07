# display/headline_scroller.py - Optimized strip-based scrolling with block tracking

from typing import List, Optional, Dict, Any, Tuple
from PIL import Image
from config import Layout, Colors
from fonts.font_manager import get_font_manager
from fonts.bitmap_font import BitmapFontAdapter

class OptimizedHeadlineScroller:
    """Strip-based headline scroller with block-based memory management"""
    
    def __init__(self, display_width: int = 64):
        """
        Initialize the optimized headline scroller
        
        Args:
            display_width: Width of the display in pixels
        """
        self.display_width = display_width
        self.scroll_speed = 1  # Pixels per frame
        
        # Strip-based scrolling
        self.headline_strip: Optional[Image.Image] = None
        self.strip_width = 0
        self.scroll_x = 0  # Current X offset into the strip
        
        # Headline management
        self.current_headlines: List[str] = []
        self.last_headlines_hash: Optional[str] = None
        
        # NEW: Block tracking for memory management
        self.blocks: List[Dict[str, Any]] = []  # List of {start_pixel, end_pixel, headline_count}
        
        # Font setup
        font_manager = get_font_manager()
        font_obj = font_manager.get_font("tiny64_font", 5)
        
        if not isinstance(font_obj, BitmapFontAdapter):
            raise TypeError(f"Expected BitmapFontAdapter, got {type(font_obj)}")
        
        self.font_adapter: BitmapFontAdapter = font_obj
        
        # Initialize with default content
        self._create_default_strip()
        
    def _create_default_strip(self) -> None:
        """Create default strip when no headlines are available"""
        default_headlines = [
            "Loading news headlines...",
            "Stay tuned for breaking news",
            "News updates coming soon"
        ]
        self._build_headline_strip(default_headlines)
        
    def _calculate_headlines_hash(self, headlines: List[str]) -> str:
        """Calculate a hash of headlines to detect changes"""
        return str(hash(tuple(headlines)))
    
    def _build_headline_strip(self, headlines: List[str]) -> None:
        """
        Build the complete headline strip from a list of headlines
        
        Args:
            headlines: List of headline strings
        """
        if not headlines:
            # Create minimal empty strip
            self.headline_strip = Image.new('RGB', (self.display_width, Layout.HEADLINES_HEIGHT), (0, 0, 0))
            self.strip_width = self.display_width
            self.blocks = []
            return
        
        # Calculate total width needed
        separator = " • "  # Bullet separator between headlines
        total_width = 0
        headline_images = []
        
        for i, headline in enumerate(headlines):
            # Add separator except for first headline
            if i > 0:
                headline_text = separator + headline
            else:
                headline_text = headline
            
            # Create PIL image for this headline
            headline_image = self.font_adapter.font_manager.create_text_image(
                headline_text, self.font_adapter.font_type
            )
            
            if headline_image:
                headline_images.append(headline_image)
                total_width += headline_image.width
            else:
                # Fallback for failed headline creation
                fallback_width, _ = self.font_adapter.getsize(headline_text)
                total_width += fallback_width
        
        # Add some buffer space at the end before looping
        buffer_width = self.display_width * 2
        total_width += buffer_width
        
        # Create the strip image
        self.headline_strip = Image.new('RGB', (total_width, Layout.HEADLINES_HEIGHT), (0, 0, 0))
        
        # Paste all headline images into the strip
        current_x = 0
        for headline_image in headline_images:
            if headline_image:
                # Calculate vertical centering
                y_offset = (Layout.HEADLINES_HEIGHT - headline_image.height) // 2
                y_offset = max(0, y_offset)  # Ensure non-negative
                
                # Paste with color (yellow text)
                for y in range(headline_image.height):
                    for x in range(headline_image.width):
                        if y_offset + y >= Layout.HEADLINES_HEIGHT:
                            break
                        if current_x + x >= total_width:
                            break
                            
                        pixel = headline_image.getpixel((x, y))
                        if pixel != (0, 0, 0):  # Non-black pixel (text)
                            self.headline_strip.putpixel(
                                (current_x + x, y_offset + y), 
                                Colors.YELLOW
                            )
                
                current_x += headline_image.width
        
        self.strip_width = total_width
        self.current_headlines = headlines.copy()
        
        # NEW: Initialize blocks list with first block
        self.blocks = [{
            'start_pixel': 0,
            'end_pixel': total_width,
            'headline_count': len(headlines)
        }]
        
        print(f"Built headline strip: {len(headlines)} headlines, {total_width} pixels wide (Block 0)")
    
    def update_headlines(self, headlines: List[str]) -> None:
        """
        Update headlines with seamless transition
        
        Args:
            headlines: List of new headline strings
        """
        if not headlines:
            return
            
        # Check if headlines have actually changed
        headlines_hash = self._calculate_headlines_hash(headlines)
        if headlines_hash == self.last_headlines_hash:
            return  # No change needed
        
        # Append new headlines to existing strip for seamless transition
        self._append_headlines_to_strip(headlines)
        self.last_headlines_hash = headlines_hash
        
        print(f"Updated headlines: {len(headlines)} new headlines appended as Block {len(self.blocks) - 1}")
    
    def _append_headlines_to_strip(self, new_headlines: List[str]) -> None:
        """
        Append new headlines to the existing strip for seamless scrolling
        
        Args:
            new_headlines: List of new headline strings to append
        """
        if not new_headlines or not self.headline_strip:
            # Fall back to rebuilding the entire strip
            self._build_headline_strip(new_headlines)
            return
        
        # Calculate width needed for new headlines
        separator = " • "
        new_width = 0
        new_headline_images = []
        
        for headline in new_headlines:
            headline_text = separator + headline  # Always add separator for appended headlines
            
            headline_image = self.font_adapter.font_manager.create_text_image(
                headline_text, self.font_adapter.font_type
            )
            
            if headline_image:
                new_headline_images.append(headline_image)
                new_width += headline_image.width
        
        if not new_headline_images:
            return  # Nothing to append
        
        # NEW: Record where this block starts
        block_start = self.strip_width
        
        # Create extended strip
        extended_width = self.strip_width + new_width
        extended_strip = Image.new('RGB', (extended_width, Layout.HEADLINES_HEIGHT), (0, 0, 0))
        
        # Copy existing strip
        if self.headline_strip:
            extended_strip.paste(self.headline_strip, (0, 0))
        
        # Append new headlines
        current_x = self.strip_width
        for headline_image in new_headline_images:
            if headline_image:
                y_offset = (Layout.HEADLINES_HEIGHT - headline_image.height) // 2
                y_offset = max(0, y_offset)
                
                for y in range(headline_image.height):
                    for x in range(headline_image.width):
                        if y_offset + y >= Layout.HEADLINES_HEIGHT:
                            break
                        if current_x + x >= extended_width:
                            break
                            
                        pixel = headline_image.getpixel((x, y))
                        if pixel != (0, 0, 0):
                            extended_strip.putpixel(
                                (current_x + x, y_offset + y), 
                                Colors.YELLOW
                            )
                
                current_x += headline_image.width
        
        # Update strip
        self.headline_strip = extended_strip
        self.strip_width = extended_width
        self.current_headlines.extend(new_headlines)
        
        # NEW: Record this as a new block
        self.blocks.append({
            'start_pixel': block_start,
            'end_pixel': extended_width,
            'headline_count': len(new_headlines)
        })
    
    def trim_scrolled_blocks(self) -> None:
        """
        Trim any headline blocks that have completely scrolled past.
        Only removes entire blocks, never partial blocks.
        Always keeps at least one block (the current one).
        """
        if not self.blocks or len(self.blocks) <= 1:
            return  # Keep at least one block
        
        # Find blocks that are completely behind scroll_x
        blocks_to_trim = []
        for block in self.blocks[:-1]:  # Never consider the last block for trimming
            if self.scroll_x > block['end_pixel']:
                blocks_to_trim.append(block)
            else:
                break  # Stop at first block we haven't fully scrolled past
        
        if not blocks_to_trim:
            return  # Nothing to trim
        
        # Calculate how much to trim (up to the end of the last fully-scrolled block)
        trim_amount = blocks_to_trim[-1]['end_pixel']
        
        # Crop the strip
        if self.headline_strip is not None:
            new_strip = self.headline_strip.crop((
                trim_amount, 0,
                self.strip_width, Layout.HEADLINES_HEIGHT
            ))
            
            # Update tracking
            self.headline_strip = new_strip
            self.strip_width = new_strip.width
            self.scroll_x -= trim_amount
        else:
            return
        
        # Remove trimmed blocks and adjust remaining block positions
        self.blocks = self.blocks[len(blocks_to_trim):]
        for block in self.blocks:
            block['start_pixel'] -= trim_amount
            block['end_pixel'] -= trim_amount
        
        total_headlines_trimmed = sum(b['headline_count'] for b in blocks_to_trim)
        print(f"Trimmed {len(blocks_to_trim)} block(s): {total_headlines_trimmed} headlines, {trim_amount} pixels removed")
    
    def get_display_slice(self) -> Image.Image:
        """
        Get the current 64-pixel wide view from the strip
        
        Returns:
            PIL Image of the current viewport
        """
        if not self.headline_strip:
            return Image.new('RGB', (self.display_width, Layout.HEADLINES_HEIGHT), (0, 0, 0))
        
        # Ensure scroll position is valid
        if self.scroll_x >= self.strip_width:
            self.scroll_x = 0  # Loop back to beginning
        
        # Extract slice from strip
        end_x = self.scroll_x + self.display_width
        
        if end_x <= self.strip_width:
            # Simple case: slice fits entirely within strip
            return self.headline_strip.crop((self.scroll_x, 0, end_x, Layout.HEADLINES_HEIGHT))
        else:
            # Wrap-around case: need to combine end of strip with beginning
            slice_image = Image.new('RGB', (self.display_width, Layout.HEADLINES_HEIGHT), (0, 0, 0))
            
            # Copy remaining portion from current position
            remaining_width = self.strip_width - self.scroll_x
            if remaining_width > 0:
                end_slice = self.headline_strip.crop((
                    self.scroll_x, 0, 
                    self.strip_width, Layout.HEADLINES_HEIGHT
                ))
                slice_image.paste(end_slice, (0, 0))
            
            # Copy beginning portion to fill the rest
            wrap_width = self.display_width - remaining_width
            if wrap_width > 0:
                start_slice = self.headline_strip.crop((
                    0, 0, 
                    min(wrap_width, self.strip_width), Layout.HEADLINES_HEIGHT
                ))
                slice_image.paste(start_slice, (remaining_width, 0))
            
            return slice_image
    
    def advance_scroll(self, pixels: Optional[int] = None) -> None:
        """
        Advance the scroll position
        
        Args:
            pixels: Number of pixels to advance (default: self.scroll_speed)
        """
        if not self.headline_strip:
            return
            
        pixels = pixels or self.scroll_speed
        self.scroll_x += pixels
        
        # Handle wrap-around
        if self.scroll_x >= self.strip_width:
            self.scroll_x = self.scroll_x % self.strip_width
        
        # NEW: Trim old blocks periodically (check every ~1000 pixels scrolled)
        # This runs about once per complete cycle through a block of headlines
        if self.scroll_x % 1000 < self.scroll_speed:
            self.trim_scrolled_blocks()
    
    def set_scroll_speed(self, speed: int) -> None:
        """
        Set the scroll speed
        
        Args:
            speed: Pixels per frame to scroll
        """
        self.scroll_speed = max(1, speed)
    
    def get_current_headline_info(self) -> str:
        """
        Get info about current headlines for debugging
        
        Returns:
            Info string about current state
        """
        headline_count = len(self.current_headlines)
        block_count = len(self.blocks)
        return f"{headline_count} headlines, {self.strip_width}px strip, {block_count} blocks, offset {self.scroll_x}"

# Global scroller instance
_headline_scroller: Optional[OptimizedHeadlineScroller] = None

def get_headline_scroller() -> OptimizedHeadlineScroller:
    """Get or create the global OptimizedHeadlineScroller instance"""
    global _headline_scroller
    if _headline_scroller is None:
        _headline_scroller = OptimizedHeadlineScroller()
    return _headline_scroller