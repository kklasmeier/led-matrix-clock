# display/weather_icons.py - 8x8 multi-color weather icons for LED display

"""
Weather icon bitmap definitions for 64x64 LED matrix display.

Each icon is 8x8 pixels, with each pixel represented by a digit 0-9
corresponding to a color in the WeatherIconPalette:

0 = Black/transparent (off)
1 = White (clouds, snow)
2 = Light gray (cloud highlights)
3 = Medium gray (cloud shadows)
4 = Yellow (sun)
5 = Orange (sun glow, storm warning)
6 = Blue (rain, water)
7 = Light blue (light rain, sky)
8 = Dark blue (night sky)
9 = Pale yellow (moon, lightning)

Icons are stored as lists of 8 strings, each string representing one row.
"""

WEATHER_ICONS = {
    'clear_day': [
        "00044000",
        "04444440",
        "04555540",
        "45555554",
        "45555554",
        "04555540",
        "04444440",
        "00044000"
    ],
    
    'clear_night': [
        "01990010",
        "00199000",
        "00019901",
        "00019900",
        "10019900",
        "00199001",
        "01990000",
        "00001000"
    ],

    'partly_cloudy_day': [
        "00000000",
        "00440000",
        "04554000",
        "44555220",
        "02222221",
        "02333321",
        "00222210",
        "00000000"
    ],

    'partly_cloudy_night': [
        "01990000",
        "00199000",
        "00019900",
        "02332900",
        "23333333",
        "00123023",
        "01990000",
        "00000000"
    ],
    
    'cloudy': [
        "00000000",
        "00222200",
        "02333320",
        "23333333",
        "02330230",
        "00320020",
        "00000000",
        "00000000"
    ],

    'rain': [
        "00222200",
        "02333320",
        "23333332",
        "02222220",
        "06060600",
        "60606060",
        "06060600",
        "00000000"
    ],
    
    'thunderstorm': [
        "00333300",
        "03333330",
        "33333333",
        "03333330",
        "00099000",
        "00090000",
        "00900000",
        "00000000"
    ],
    
    'snow': [
        "00222200",
        "02333320",
        "23333332",
        "02222220",
        "01010100",
        "10101010",
        "01010100",
        "00000000"
    ],
    
    'heavy_rain': [
        "03333300",
        "33333333",
        "33333333",
        "03333330",
        "66666660",
        "06666600",
        "66666660",
        "06060600"
    ],
    
    'fog': [
        "00000000",
        "02323230",
        "00000000",
        "23232323",
        "00000000",
        "32323200",
        "00000000",
        "00032323"
    ],
    
    'windy': [
        "00000000",
        "02222200",
        "00000000",
        "03333330",
        "00000000",
        "02222000",
        "00000000",
        "00000000"
    ],
    
    'freezing_rain': [
        "00222200",
        "02333320",
        "23333332",
        "02222220",
        "01616100",
        "70607070",
        "01716100",
        "00000000"
    ]
}


# Color palette mapping (indices 0-9)
class WeatherIconPalette:
    """Color palette for weather icons"""
    COLORS = {
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


def get_icon_data(condition: str, is_night: bool = False) -> list:
    """
    Get icon bitmap data for a weather condition
    
    Args:
        condition: Weather condition string (e.g., 'clear', 'rain', 'cloudy')
        is_night: Whether it's nighttime (affects clear and partly_cloudy icons)
        
    Returns:
        List of 8 strings, each 8 characters long, representing the icon
    """
    # Handle day/night variants
    if condition == 'clear':
        icon_key = 'clear_night' if is_night else 'clear_day'
    elif condition == 'partly_cloudy':
        icon_key = 'partly_cloudy_night' if is_night else 'partly_cloudy_day'
    else:
        icon_key = condition
    
    # Return icon data, defaulting to 'cloudy' if not found
    return WEATHER_ICONS.get(icon_key, WEATHER_ICONS['cloudy'])


def draw_icon(image, x: int, y: int, condition: str, is_night: bool = False):
    """
    Draw an 8x8 weather icon on a PIL Image
    
    Args:
        image: PIL Image object to draw on
        x: X coordinate of top-left corner
        y: Y coordinate of top-left corner
        condition: Weather condition string
        is_night: Whether it's nighttime
    """
    icon_data = get_icon_data(condition, is_night)
    
    # Draw each pixel
    for row_idx, row in enumerate(icon_data):
        for col_idx, pixel_char in enumerate(row):
            color_index = int(pixel_char)
            if color_index > 0:  # Skip 0 (transparent/black)
                color = WeatherIconPalette.COLORS[color_index]
                image.putpixel((x + col_idx, y + row_idx), color)


# Valid condition strings that can be passed to get_icon_data() or draw_icon()
VALID_CONDITIONS = [
    'clear',           # Will use clear_day or clear_night based on is_night
    'partly_cloudy',   # Will use partly_cloudy_day or partly_cloudy_night
    'cloudy',
    'rain',
    'heavy_rain',
    'thunderstorm',
    'snow',
    'fog',
    'windy',
    'freezing_rain'
]