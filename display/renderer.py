# display/renderer.py - Optimized renderer using SetImage with static frame buffer

from typing import Optional, Tuple, Dict, Any
from PIL import Image, ImageDraw
from config import Layout, Colors, Fonts
from fonts.font_manager import get_font_manager, FontError
from fonts.bitmap_font import BitmapFontAdapter, get_bitmap_font_manager
from .headline_scroller import get_headline_scroller

class OptimizedDisplayRenderer:
    """Optimized renderer using PIL compositing and SetImage for maximum performance"""
    
    def __init__(self):
        self.font_manager = get_font_manager()
        self._image_cache: Dict[str, Image.Image] = {}
        
        # Static frame buffer for non-scrolling content
        self.static_frame_buffer: Optional[Image.Image] = None
        self.static_buffer_dirty = True
        
        # Track last rendered static content to detect changes
        self.last_date = ""
        self.last_time = ""
        self.last_ampm = ""
        self.last_weather_data = None
        self.last_stock_data = None
        
        # Get the headline scroller
        self.headline_scroller = get_headline_scroller()
        
        # Load fonts
        try:
            self.tiny_font = self.font_manager.get_font(Fonts.TINY_FONT, Fonts.TINY_SIZE)
            self.clock_font = self.font_manager.get_font(Fonts.CLOCK_FONT, Fonts.CLOCK_SIZE)
        except FontError as e:
            print(f"Error loading fonts: {e}")
            raise
    
    def get_text_image(self, text: str, font_type: str, cache_key: Optional[str] = None) -> Optional[Image.Image]:
        """
        Get PIL image for text, with optional caching
        
        Args:
            text: Text to render
            font_type: "tiny64_font" or "clock64_font"
            cache_key: Optional key for caching the image
            
        Returns:
            PIL Image or None if error
        """
        # Use cache if key provided and image exists
        if cache_key and cache_key in self._image_cache:
            return self._image_cache[cache_key]
        
        try:
            # Get the appropriate bitmap font adapter
            if font_type == Fonts.TINY_FONT:
                font_adapter = self.tiny_font
            elif font_type == Fonts.CLOCK_FONT:
                font_adapter = self.clock_font
            else:
                print(f"Unknown font type: {font_type}")
                return None
            
            # Check if this is a BitmapFontAdapter (our bitmap fonts)
            if isinstance(font_adapter, BitmapFontAdapter):
                image = font_adapter.font_manager.create_text_image(text, font_adapter.font_type)
            else:
                # Fallback: Use bitmap font manager directly
                print(f"Font adapter is not BitmapFontAdapter, using fallback")
                bitmap_manager = get_bitmap_font_manager()
                image = bitmap_manager.create_text_image(text, font_type)
            
            # Cache if key provided
            if cache_key and image:
                self._image_cache[cache_key] = image
            
            return image
            
        except Exception as e:
            print(f"Error creating text image for '{text}': {e}")
            return None
    
    def calculate_centered_x(self, text_width: int, section_width: int, section_start_x: int = 0) -> int:
        """
        Calculate X position to center text within a section
        
        Args:
            text_width: Width of the text in pixels
            section_width: Width of the section in pixels
            section_start_x: Starting X position of the section
            
        Returns:
            X position to center the text
        """
        if text_width >= section_width:
            return section_start_x
        
        return section_start_x + (section_width - text_width) // 2 + 1
    
    def draw_dividers(self, image: Image.Image) -> None:
        """Draw all divider lines on the image"""
        draw = ImageDraw.Draw(image)
        
        # Horizontal dividers
        # Date divider
        draw.rectangle(
            [0, Layout.DATE_DIVIDER_Y, 63, Layout.DATE_DIVIDER_Y + Layout.DATE_DIVIDER_HEIGHT - 1],
            fill=Colors.DIM_WHITE
        )
        
        # Time divider
        draw.rectangle(
            [0, Layout.TIME_DIVIDER_Y, 63, Layout.TIME_DIVIDER_Y + Layout.TIME_DIVIDER_HEIGHT - 1],
            fill=Colors.DIM_WHITE
        )
        
        # Bottom divider
        draw.line(
            [(0, Layout.BOTTOM_DIVIDER_Y), (63, Layout.BOTTOM_DIVIDER_Y)],
            fill=Colors.DIM_WHITE
        )
        
        # Vertical divider between weather and stocks
        draw.rectangle(
            [Layout.VERTICAL_DIVIDER_X, Layout.VERTICAL_DIVIDER_START_Y,
             Layout.VERTICAL_DIVIDER_X + Layout.VERTICAL_DIVIDER_WIDTH - 1, Layout.VERTICAL_DIVIDER_END_Y],
            fill=Colors.DIM_WHITE
        )
    
    def paste_colored_text(self, target: Image.Image, text_image: Image.Image, 
                          x: int, y: int, color: Tuple[int, int, int]) -> None:
        """
        Paste a white text image onto target with specified color
        
        Args:
            target: Target PIL image
            text_image: Source text image (white text on black)
            x, y: Position to paste
            color: RGB color tuple for the text
        """
        if not text_image:
            return
            
        # Create colored version of text
        colored_text = Image.new('RGB', text_image.size, (0, 0, 0))
        
        for py in range(text_image.height):
            for px in range(text_image.width):
                pixel = text_image.getpixel((px, py))
                if pixel != (0, 0, 0):  # Non-black pixel (text)
                    colored_text.putpixel((px, py), color)
        
        # Paste onto target
        target.paste(colored_text, (x, y))
    
    def render_weather(self, frame: Image.Image, weather_data: Dict[str, Any]) -> None:
            """Render weather information with color-coded temperatures"""
            high_low_text = weather_data.get("high_low_text", "H-- L--")
            current_text = weather_data.get("current_text", "Now --")
            
            # Split high_low_text into parts: "H86 L57"
            parts = high_low_text.split()
            if len(parts) == 2:
                high_part = parts[0]  # e.g., "H86"
                low_part = parts[1]   # e.g., "L57"
                
                # Split "H86" into "H" and "86"
                if len(high_part) > 1:
                    high_label = high_part[0]  # "H"
                    high_value = high_part[1:]  # "86"
                    
                    # Render "H" in white
                    h_image = self.get_text_image(high_label, Fonts.TINY_FONT, f"weather_h_{high_label}")
                    if h_image:
                        self.paste_colored_text(frame, h_image, Layout.WEATHER_START_X, Layout.WEATHER_START_Y, Colors.WHITE)
                    
                    # Render "86" in orange, positioned after "H"
                    high_value_image = self.get_text_image(high_value, Fonts.TINY_FONT, f"weather_high_{high_value}")
                    if high_value_image and h_image:
                        high_x = Layout.WEATHER_START_X + h_image.width + 1
                        self.paste_colored_text(frame, high_value_image, high_x, Layout.WEATHER_START_Y, Colors.ORANGE)
                
                # Split "L57" into "L" and "57"
                if len(low_part) > 1:
                    low_label = low_part[0]  # "L"
                    low_value = low_part[1:]  # "57"
                    
                    # Render low value in blue
                    low_value_image = self.get_text_image(low_value, Fonts.TINY_FONT, f"weather_low_{low_value}")
                    if low_value_image:
                        # Right align: divider is at x=31, we want 1 pixel gap, so end at x=30
                        low_x = 30 - low_value_image.width
                        self.paste_colored_text(frame, low_value_image, low_x, Layout.WEATHER_START_Y, Colors.BLUE)
                        
                        # Render "L" in white, positioned before the value
                        l_image = self.get_text_image(low_label, Fonts.TINY_FONT, f"weather_l_{low_label}")
                        if l_image:
                            l_x = low_x - l_image.width - 1
                            self.paste_colored_text(frame, l_image, l_x, Layout.WEATHER_START_Y, Colors.WHITE)
            else:
                # Fallback: render the whole string at start position
                high_low_image = self.get_text_image(high_low_text, Fonts.TINY_FONT, f"weather_hl_{high_low_text}")
                if high_low_image:
                    self.paste_colored_text(frame, high_low_image, Layout.WEATHER_START_X, Layout.WEATHER_START_Y, Colors.BLUE)
            
            # Split current_text into "Now" and "##" parts
            current_parts = current_text.split()
            if len(current_parts) == 2:
                now_label = current_parts[0]  # "Now"
                now_value = current_parts[1]  # e.g., "85"
                
                # Render "Now" label at start position in cyan
                now_label_image = self.get_text_image(now_label, Fonts.TINY_FONT, f"weather_now_{now_label}")
                if now_label_image:
                    self.paste_colored_text(frame, now_label_image, Layout.WEATHER_START_X, Layout.WEATHER_START_Y + 7, Colors.CYAN)
                
                # Render temperature value flush right in cyan
                now_value_image = self.get_text_image(now_value, Fonts.TINY_FONT, f"weather_value_{now_value}")
                if now_value_image:
                    # Right align: divider is at x=31, we want 1 pixel gap, so end at x=30
                    value_x = 30 - now_value_image.width
                    self.paste_colored_text(frame, now_value_image, value_x, Layout.WEATHER_START_Y + 7, Colors.CYAN)
            else:
                # Fallback: render the whole string at start position
                current_image = self.get_text_image(current_text, Fonts.TINY_FONT, f"weather_cur_{current_text}")
                if current_image:
                    self.paste_colored_text(frame, current_image, Layout.WEATHER_START_X, Layout.WEATHER_START_Y + 7, Colors.CYAN)

    def rebuild_static_frame_buffer(self, time_data: Dict[str, Any], 
                                   weather_data: Dict[str, Any], 
                                   stock_data: Dict[str, Any]) -> None:
        """
        Rebuild the static frame buffer with date/time/weather/stocks
        
        Args:
            time_data: Time data dictionary
            weather_data: Weather data dictionary
            stock_data: Stock data dictionary
        """
        # Create new blank frame
        frame = Image.new('RGB', (64, 64), (0, 0, 0))
        
        # Draw dividers first
        self.draw_dividers(frame)
        
        # Render date
        date_text = time_data.get('date', '')
        if date_text:
            date_image = self.get_text_image(date_text, Fonts.TINY_FONT, f"date_{date_text}")
            if date_image:
                x_pos = self.calculate_centered_x(date_image.width, 64, 0)
                self.paste_colored_text(frame, date_image, x_pos, Layout.DATE_START_Y, Colors.CYAN)
        
        # Render time
        time_text = time_data.get('time', '')
        if time_text:
            time_image = self.get_text_image(time_text, Fonts.CLOCK_FONT, f"time_{time_text}")
            if time_image:
                self.paste_colored_text(frame, time_image, Layout.TIME_START_X, Layout.TIME_START_Y, Colors.RED)
        
        # Render AM/PM
        ampm_text = time_data.get('ampm', '')
        if ampm_text:
            ampm_image = self.get_text_image(ampm_text, Fonts.TINY_FONT, f"ampm_{ampm_text}")
            if ampm_image:
                self.paste_colored_text(frame, ampm_image, Layout.AMPM_START_X, Layout.AMPM_START_Y, Colors.RED)
        
        # Render weather with new right-aligned method
        self.render_weather(frame, weather_data)
        
        # Render stocks with separate labels and values
        self.render_stocks(frame, stock_data)
        
        # Store the static buffer
        self.static_frame_buffer = frame
        self.static_buffer_dirty = False
        
        # Update tracking variables
        self.last_date = date_text
        self.last_time = time_text
        self.last_ampm = ampm_text
        self.last_weather_data = weather_data
        self.last_stock_data = stock_data
    
    def render_stocks(self, frame: Image.Image, stock_data: Dict[str, Any]) -> None:
        """Render stock information with right-aligned values"""
        # Get labels and values separately
        dow_label = stock_data.get("dow_label", "DOW")
        dow_value = stock_data.get("dow_value", "0")
        sp_label = stock_data.get("sp_label", "S&P")
        sp_value = stock_data.get("sp_value", "0")
        
        # Use green for positive, red for negative changes
        dow_change = stock_data.get("dow_change", 0)
        sp_change = stock_data.get("sp_change", 0)
        
        dow_color = Colors.GREEN if dow_change >= 0 else Colors.RED
        sp_color = Colors.GREEN if sp_change >= 0 else Colors.RED
        
        # Render DOW
        dow_label_image = self.get_text_image(dow_label, Fonts.TINY_FONT, f"dow_label_{dow_label}")
        if dow_label_image:
            # Label starts at STOCKS_START_X
            self.paste_colored_text(frame, dow_label_image, Layout.STOCKS_START_X, Layout.STOCKS_START_Y, Colors.WHITE)
        
        dow_value_image = self.get_text_image(dow_value, Fonts.TINY_FONT, f"dow_value_{dow_value}")
        if dow_value_image:
            # Value is right-aligned at pixel 62
            value_x = 62 - dow_value_image.width
            self.paste_colored_text(frame, dow_value_image, value_x, Layout.STOCKS_START_Y, dow_color)
        
        # Render S&P
        sp_label_image = self.get_text_image(sp_label, Fonts.TINY_FONT, f"sp_label_{sp_label}")
        if sp_label_image:
            # Label starts at STOCKS_START_X
            self.paste_colored_text(frame, sp_label_image, Layout.STOCKS_START_X, Layout.STOCKS_START_Y + 7, Colors.WHITE)
        
        sp_value_image = self.get_text_image(sp_value, Fonts.TINY_FONT, f"sp_value_{sp_value}")
        if sp_value_image:
            # Value is right-aligned at pixel 62
            value_x = 62 - sp_value_image.width
            self.paste_colored_text(frame, sp_value_image, value_x, Layout.STOCKS_START_Y + 7, sp_color)
    
    def check_static_content_changed(self, time_data: Dict[str, Any], 
                                    weather_data: Dict[str, Any], 
                                    stock_data: Dict[str, Any]) -> bool:
        """
        Check if any static content has changed
        
        Returns:
            True if static content needs to be rebuilt
        """
        if self.static_frame_buffer is None:
            return True
        
        if time_data.get('date', '') != self.last_date:
            return True
        
        if time_data.get('time', '') != self.last_time:
            return True
        
        if time_data.get('ampm', '') != self.last_ampm:
            return True
        
        if weather_data != self.last_weather_data:
            return True
        
        if stock_data != self.last_stock_data:
            return True
        
        return False
    
    def render_frame_as_image(self, time_data: Dict[str, Any], 
                             weather_data: Dict[str, Any], 
                             stock_data: Dict[str, Any],
                             news_data: Dict[str, Any]) -> Image.Image:
        """
        Render a complete frame as a PIL Image
        
        Args:
            time_data: Dictionary with 'time', 'ampm', 'date' keys
            weather_data: Dictionary with weather information
            stock_data: Dictionary with stock information
            news_data: Dictionary with news headlines
            
        Returns:
            Complete 64x64 PIL Image ready for SetImage()
        """
        # Check if static content needs rebuilding
        if self.check_static_content_changed(time_data, weather_data, stock_data):
            self.rebuild_static_frame_buffer(time_data, weather_data, stock_data)
        
        # Copy static buffer
        if self.static_frame_buffer:
            frame = self.static_frame_buffer.copy()
        else:
            frame = Image.new('RGB', (64, 64), (0, 0, 0))
        
        # Update headlines in scroller if changed
        headlines = news_data.get("headlines", [])
        if headlines:
            self.headline_scroller.update_headlines(headlines)
        
        # Get current headline slice
        headline_slice = self.headline_scroller.get_display_slice()
        
        # Paste headline slice (the only dynamic element each frame)
        if headline_slice:
            frame.paste(headline_slice, (0, Layout.HEADLINES_START_Y))
        
        # Advance scroll for next frame
        self.headline_scroller.advance_scroll()
        
        return frame
    
    def render_frame(self, canvas, time_data: Dict[str, Any], 
                    weather_data: Dict[str, Any], 
                    stock_data: Dict[str, Any],
                    news_data: Dict[str, Any]) -> None:
        """
        Render a complete frame using SetImage
        
        Args:
            canvas: Matrix canvas
            time_data: Dictionary with 'time', 'ampm', 'date' keys
            weather_data: Dictionary with weather information
            stock_data: Dictionary with stock information
            news_data: Dictionary with news headlines
        """
        # Generate complete frame as PIL image
        frame_image = self.render_frame_as_image(time_data, weather_data, stock_data, news_data)
        
        # Use SetImage for fast bulk transfer
        canvas.SetImage(frame_image)
    
    def clear_cache(self) -> None:
        """Clear the image cache and reset static buffer"""
        self._image_cache.clear()
        self.static_frame_buffer = None
        self.static_buffer_dirty = True

# Global renderer instance
_display_renderer: Optional[OptimizedDisplayRenderer] = None

def get_display_renderer() -> OptimizedDisplayRenderer:
    """Get or create the global OptimizedDisplayRenderer instance"""
    global _display_renderer
    if _display_renderer is None:
        _display_renderer = OptimizedDisplayRenderer()
    return _display_renderer