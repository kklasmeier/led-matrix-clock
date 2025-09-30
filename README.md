# LED Matrix Clock

A Raspberry Pi-powered 64x64 RGB LED matrix display showing real-time information: current time/date, local weather, stock market data, and scrolling news headlines.

## Features

- **Large Clock Display**: Easy-to-read time in 12-hour format with AM/PM indicator
- **Current Date**: Full date display with day of week
- **Live Weather**: Current temperature plus daily high/low (Open-Meteo API)
- **Stock Market**: DOW and S&P 500 daily changes with color-coded indicators (green/red)
- **News Headlines**: Continuously scrolling headlines from multiple news sources
- **High Performance**: ~170 FPS rendering with optimized static frame buffers

## Hardware Requirements

- Raspberry Pi Zero 2W (or any Pi with 40-pin GPIO header)
- 64x64 RGB LED Matrix Panel with HUB75 interface
- Adafruit RGB Matrix Bonnet (#3211)
- 5V 10A Power Supply (minimum 5V 4A)
- MicroSD card (8GB minimum)

## Software Requirements

- Raspberry Pi OS (Debian-based Linux)
- Python 3.7 or higher
- Pillow (PIL Fork)
- hzeller/rpi-rgb-led-matrix library

## Installation

### 1. Clone the Repository

```bash
git clone git@github.com:kklasmeier/led-matrix-clock.git
cd led-matrix-clock
```

### 2. Install System Dependencies

```bash
sudo apt update
sudo apt install python3-pil
```

### 3. Install RGB Matrix Library

```bash
cd ~
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix
make build-python HARDWARE_DESC=adafruit-hat-pwm
sudo make install-python
```

### 4. Configure Secrets

Copy the example secrets file and add your credentials:

```bash
cd ~/led-matrix-clock
cp secrets.example.json secrets.json
nano secrets.json
```

Edit `secrets.json` with:
- **STOCK_API_KEY**: Free API key from [Financial Modeling Prep](https://financialmodelingprep.com/register)
- **LATITUDE**: Your location latitude (e.g., 39.35 for Wetherington, OH)
- **LONGITUDE**: Your location longitude (e.g., -84.31)

Find your coordinates at [latlong.net](https://www.latlong.net/)

### 5. Run the Clock

```bash
cd ~/led-matrix-clock
sudo python3 main.py
```

Press `Ctrl+C` to stop the display.

## Configuration

All configuration is in `config.py`:

- **Colors**: Customize RGB values for clock, weather, stocks, and headlines
- **Layout**: Adjust pixel positions for each display section
- **Update Intervals**: Change how often data refreshes (weather, stocks, news)
- **Hardware Settings**: GPIO slowdown, brightness, PWM bits

## News Sources

Currently aggregates headlines from:
- Fox News
- Breitbart
- NY Post
- The Blaze
- Washington Examiner
- Daily Wire (when feed is available)

To modify sources, edit `data/news_provider.py` and adjust the `self.rss_sources` list.

## Display Layout

```
┌─────────────────────────────────────────────┐
│              Mon Sep 29 2025                │  Date (cyan)
├─────────────────────────────────────────────┤
│  10:47                              PM      │  Time (red)
├──────────────────────┬──────────────────────┤
│  H86          L57    │  DOW            25   │  Weather (blue/cyan)
│  Now          85     │  S&P             2   │  Stocks (green/red)
├──────────────────────┴──────────────────────┤
│  ◄ Breaking news scrolling continuously     │  Headlines (yellow)
└─────────────────────────────────────────────┘
```

## Performance Characteristics

- **Frame Rate**: 170+ FPS main loop
- **CPU Usage**: ~40% on Raspberry Pi Zero 2W (1.5 of 4 cores)
- **Memory**: ~150 MB RAM
- **Display Updates**: 25% of frames (only when content changes or scrolling)
- **Power Draw**: Approximately 15W (5V @ 3A typical)

## Troubleshooting

### "Another instance is already running"

Only one instance can access the GPIO pins at a time. Remove the lock file:

```bash
rm /tmp/led_clock.pid
```

Or use the cleanup script if available:

```bash
./cleanup_lock.sh
```

### Display Flickering or Wrong Colors

Adjust the GPIO slowdown value in `config.py`:

```python
class Hardware:
    GPIO_SLOWDOWN = 4  # Try values 2-4
```

Also verify your power supply provides at least 5V 4A (10A recommended).

### Weather or Stock Data Not Updating

1. Verify `secrets.json` exists and contains valid values
2. Check internet connection
3. Review console output for API error messages
4. For stocks: updates only occur during market hours (9:15 AM - 4:15 PM ET, weekdays)

### News Headlines Not Showing

Some RSS feeds occasionally have issues. Check the console output during startup to see which sources succeeded. The system will continue with available headlines even if some sources fail.

## Project Structure

```
led-matrix-clock/
├── main.py                    # Application entry point and main loop
├── config.py                  # Configuration: layout, colors, settings
├── secrets.json               # API keys and location (NOT in git)
├── secrets.example.json       # Template for secrets.json
├── gitsync.sh                 # Git helper script
├── fonts/
│   ├── font_manager.py        # Font loading system
│   ├── bitmap_font.py         # Bitmap font renderer
│   ├── tiny64_font.txt        # Small text (3x5 pixels)
│   └── clock64_font.txt       # Large digits (9x15 pixels)
├── display/
│   ├── matrix.py              # LED matrix initialization
│   ├── renderer.py            # Frame rendering with PIL
│   └── headline_scroller.py   # Strip-based scrolling
├── data/
│   ├── time_provider.py       # System time/date
│   ├── weather_provider.py    # Open-Meteo integration
│   ├── stock_provider.py      # Financial Modeling Prep API
│   ├── news_provider.py       # RSS feed aggregation
│   └── data_manager.py        # Background data fetching
└── utils/
    └── process_lock.py        # Single-instance enforcement
```

## Technical Details

For detailed architecture information, development guidelines, and implementation details, see [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md).

Key technical features:
- **Threaded Architecture**: Background data fetching never blocks display
- **Static Frame Buffers**: Date/time/weather/stocks rendered once, reused until data changes
- **Strip-Based Scrolling**: Headlines pre-rendered to wide image, viewport scrolled
- **Image Caching**: Text rendered once, cached for reuse
- **Process Locking**: Prevents multiple instances from accessing GPIO

## Auto-Start on Boot (Optional)

To run the clock automatically when the Pi boots:

```bash
sudo nano /etc/systemd/system/ledclock.service
```

Add:

```ini
[Unit]
Description=LED Matrix Clock
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/led-matrix-clock
ExecStart=/usr/bin/python3 /home/pi/led-matrix-clock/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ledclock.service
sudo systemctl start ledclock.service
```

Check status:

```bash
sudo systemctl status ledclock.service
```

## Development

### Git Workflow

Use the included `gitsync.sh` script for easy Git operations:

```bash
./gitsync.sh
```

Or manually:

```bash
git add .
git commit -m "Your commit message"
git push
```

### Adding New Data Sources

1. Create a provider in `data/` (e.g., `crypto_provider.py`)
2. Implement `get_data()`, `fetch_X_data()`, and `is_stale()` methods
3. Add to `data_manager.py` background thread
4. Update `renderer.py` to display the new data
5. Adjust layout in `config.py` if needed

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Acknowledgments

- [hzeller/rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) - Excellent LED matrix driver library
- [Open-Meteo](https://open-meteo.com/) - Free weather API with no key required
- [Financial Modeling Prep](https://financialmodelingprep.com/) - Stock market data API
- Various news outlets for RSS feeds

## Author

Created by kklasmeier for personal use in Wetherington, Ohio.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.