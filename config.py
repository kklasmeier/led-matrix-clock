# config.py - Layout configuration for 64x64 LED Clock
# Display dimensions
MATRIX_WIDTH = 64
MATRIX_HEIGHT = 64

# Color definitions
class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    
    # Dimmer colors for dividers and accents
    DIM_WHITE = (128, 128, 128)  # Dimmer divider lines
    ORANGE = (255, 165, 0)       # Alternative color
    PURPLE = (128, 0, 128)       # Alternative color
    
    # Weather icon palette (0-9 indices for multi-color icons)
    # Note: Full palette defined in display/weather_icons.py
    WEATHER_PALETTE = {
        0: (0, 0, 0),         # Black/transparent (off)
        1: (255, 255, 255),   # White (clouds, snow)
        2: (200, 200, 200),   # Light gray (cloud highlights)
        3: (120, 120, 120),   # Medium gray (cloud shadows)
        4: (255, 220, 0),     # Yellow (sun)
        5: (255, 160, 0),     # Orange (sun glow, storm warning)
        6: (60, 120, 220),    # Blue (rain, water)
        7: (100, 180, 255),   # Light blue (light rain, sky)
        8: (40, 40, 100),     # Dark blue (night sky)
        9: (255, 255, 100),   # Pale yellow (moon, lightning)
    }

# Layout sections (y-coordinates)
class Layout:
    # Date Section: Rows 2-14 (13px height) - moved down 2 pixels
    DATE_START_Y = 3
    DATE_HEIGHT = 13
    
    # Divider: Rows 11-12 (2px) - moved up 2 pixels
    DATE_DIVIDER_Y = 11
    DATE_DIVIDER_HEIGHT = 2
    
    # Time Section: Rows 15-29 (15px height)
    TIME_START_Y = 17   # moved down 2 pixels (was 15)
    TIME_HEIGHT = 15
    TIME_START_X = 2    # moved left 1 pixel (was 3)
    
    # AM/PM Section: Same rows as time, right side
    AMPM_START_Y = 17   # moved down 2 pixels to match time (was 15)
    AMPM_START_X = 53   # moved left 1 pixel (was 54)
    AMPM_WIDTH = 7
    
    # Weather Icon Box: 11x8 pixel box on right side above time divider
    ICON_BOX_X = 53       # Left edge of box
    ICON_BOX_Y = 28       # Top edge of box (moved down 3 pixels)
    ICON_BOX_WIDTH = 11   # Box width (includes 1px border)
    ICON_BOX_HEIGHT = 8   # Box height (3 pixels shorter)
    
    # Weather Icon: 8x8 pixel icon inside box
    WEATHER_ICON_X = 55   # Icon X position (box edge + border + padding)
    WEATHER_ICON_Y = 30   # Icon Y position (moved down 3 pixels)
    WEATHER_ICON_SIZE = 8
    
    # Divider: Rows 36-37 (2px) - now stops at x=52 to make room for icon box
    TIME_DIVIDER_Y = 36
    TIME_DIVIDER_HEIGHT = 2
    TIME_DIVIDER_END_X = 52  # Divider stops here (icon box border at x=53)
    
    # SWAPPED: Stocks Section now on LEFT: Rows 40-51, Left half
    STOCKS_START_Y = 40
    STOCKS_START_X = 1      # Now on left side
    STOCKS_WIDTH = 30       # Width of stocks section
    STOCKS_HEIGHT = 12
    
    # SWAPPED: Weather Section now on RIGHT: Rows 40-51, Right half
    WEATHER_START_Y = 40
    WEATHER_START_X = 34    # Now on right side (after vertical divider)
    WEATHER_WIDTH = 30      # Width of weather section
    WEATHER_HEIGHT = 12
    
    # Weather Text: Positioned at start of weather section (no icon inside section)
    WEATHER_TEXT_X = 34     # Start at beginning of weather section
    
    # Vertical Divider: Column 31-32 between stocks/weather - extended to connect horizontal lines
    VERTICAL_DIVIDER_X = 31
    VERTICAL_DIVIDER_WIDTH = 2
    VERTICAL_DIVIDER_START_Y = 37  # Start from first horizontal line
    VERTICAL_DIVIDER_END_Y = 53    # Extended down 1 pixel to meet new bottom divider
    
    # Divider: Row 54 (1px) - moved down 1 pixel (was 53)
    BOTTOM_DIVIDER_Y = 54
    BOTTOM_DIVIDER_HEIGHT = 1
    
    # Scrolling Headlines: Rows 56-63 (8px height) - moved down 2 pixels
    HEADLINES_START_Y = 56
    HEADLINES_HEIGHT = 8   # adjusted height to fit (was 10)
    HEADLINES_WIDTH = 64

# Font configurations
class Fonts:
    TINY_FONT = "tiny64_font"
    CLOCK_FONT = "clock64_font"
    
    # Font sizes (for compatibility, actual size determined by bitmap)
    TINY_SIZE = 5
    CLOCK_SIZE = 15

# Update intervals (in seconds)
class UpdateIntervals:
    TIME_UPDATE = 1      # Update time every second
    WEATHER_UPDATE = 900 # Update weather every 15 minutes
    STOCKS_UPDATE = 300  # Update stocks every 5 minutes
    NEWS_UPDATE = 1800   # Update news every 30 minutes
    SCROLL_FPS = 30      # Legacy - now using frame-based scrolling

# Weather forecast configuration
class Weather:
    """Weather forecast configuration and tuning parameters"""
    
    # Time-weighted forecast weights for hours 1-8
    # These control how much each future hour influences the displayed icon
    # Adjust these values to tune the forecast behavior
    # Current settings: prioritize hours 3-4, then hours 1-2, then hours 5-8
    FORECAST_WEIGHTS = [2, 2, 4, 4, 1, 1, 1, 1]
    
    # Current weather weight (applied separately from hourly weights)
    # Higher value = current conditions matter more than forecast
    CURRENT_WEIGHT = 3
    
    # Enable/disable icon display
    SHOW_ICON = True
    
    # Sunrise/sunset detection method
    # 'api' = use sunrise/sunset times from Open-Meteo API (most accurate)
    # 'simple' = use simple time-based heuristic (8pm-6am = night)
    DAY_NIGHT_METHOD = 'simple'
    SIMPLE_NIGHT_START = 20  # 8 PM
    SIMPLE_NIGHT_END = 6     # 6 AM

# Hardware configuration
class Hardware:
    GPIO_SLOWDOWN = 4    # Adjust if display flickers
    PWM_BITS = 11        # Color depth
    BRIGHTNESS = 100     # LED brightness (0-100)
    
    # HUB75 pin configuration (for Adafruit RGB Matrix Bonnet)
    # These are typically handled by the library, but can be customized
    ROWS = 64
    COLS = 64
    CHAIN_LENGTH = 1
    PARALLEL = 1