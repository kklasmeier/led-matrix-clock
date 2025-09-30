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
    
    # Divider: Rows 36-37 (2px) - moved up 2 pixels (was 38-39)
    TIME_DIVIDER_Y = 36
    TIME_DIVIDER_HEIGHT = 2
    
    # Weather Section: Rows 40-51, Left half (12px height, 32px wide) - moved up 1 pixel
    WEATHER_START_Y = 40
    WEATHER_START_X = 1
    WEATHER_WIDTH = 32
    WEATHER_HEIGHT = 12
    
    # Stocks Section: Rows 40-51, Right half (12px height, 32px wide) - moved up 1 pixel
    STOCKS_START_Y = 40
    STOCKS_START_X = 34  # moved right 1 pixel (was 33)
    STOCKS_WIDTH = 30   # adjusted width to accommodate shift
    STOCKS_HEIGHT = 12
    
    # Vertical Divider: Column 31-32 between weather/stocks - extended to connect horizontal lines
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