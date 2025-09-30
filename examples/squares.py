#!/usr/bin/env python3
"""
random_squares.py
Draws random filled squares on an RGB matrix (64x64) using the
rpi-rgb-led-matrix Python bindings with settings known to work on
Pi Zero 2 + Adafruit RGB Matrix Bonnet.

Controls:
  Ctrl-C to exit cleanly.
"""

import random
import time
import signal
import sys

from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics # type: ignore

# ---------- Config you can tweak ----------
PANEL_ROWS = 64         # Your panel height
PANEL_COLS = 64         # Your panel width
BRIGHTNESS = 60         # 1..100 (lower = cooler, cleaner power)
SLOWDOWN   = 4          # 1..4 (Zero 2 often likes 3–4)
FPS        = 30         # Target frames per second
SQUARES_PER_FRAME = 3   # How many new squares to draw each frame
MIN_SIZE   = 4          # Smallest square side
MAX_SIZE   = 20         # Largest square side
CLEAR_EVERY_N_FRAMES = 0  # Set >0 to periodically clear (e.g., 600)
# -----------------------------------------

_running = True
def _signal_handler(sig, frame):
    global _running
    _running = False

signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def main():
    # Set up matrix options to match your working demo flags
    opts = RGBMatrixOptions()
    opts.rows = PANEL_ROWS
    opts.cols = PANEL_COLS
    opts.chain_length = 1
    opts.parallel = 1

    # This is the critical mapping for the Adafruit Bonnet
    # (same effect as --led-gpio-mapping=adafruit-hat)
    opts.hardware_mapping = "adafruit-hat"

    # Equivalent of --led-no-hardware-pulse
    # (Name in Python bindings is 'disable_hardware_pulsing')
    opts.disable_hardware_pulsing = True

    # Helps timing on faster CPUs like Zero 2 / Pi 4
    # (same idea as --led-slowdown-gpio=4)
    opts.gpio_slowdown = SLOWDOWN

    # Brightness and PWM bits (10 saves a bit of CPU)
    opts.brightness = BRIGHTNESS
    opts.pwm_bits = 10

    # Optional: limit refresh if you want to shave CPU
    # opts.limit_refresh_rate_hz = 120

    # Create the matrix & a double-buffered canvas
    matrix = RGBMatrix(options=opts)
    canvas = matrix.CreateFrameCanvas()

    # Start with a black screen
    canvas.Fill(0, 0, 0)
    canvas = matrix.SwapOnVSync(canvas)

    frame = 0
    frame_time = 1.0 / float(FPS)

    try:
        while _running:
            start = time.time()

            # Optionally clear every N frames
            if CLEAR_EVERY_N_FRAMES and frame % CLEAR_EVERY_N_FRAMES == 0 and frame != 0:
                canvas.Clear()

            # Draw a handful of random filled squares
            for _ in range(SQUARES_PER_FRAME):
                # Random size & position (stay fully on-screen)
                size = random.randint(MIN_SIZE, MAX_SIZE)
                x = random.randint(0, PANEL_COLS - size)
                y = random.randint(0, PANEL_ROWS - size)

                # Random color (soften max channel to avoid harsh white)
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)

                # Filled square: simple pixel fill is fastest without PIL
                x2 = x + size - 1
                y2 = y + size - 1
                # Clamp just in case
                x2 = clamp(x2, 0, PANEL_COLS - 1)
                y2 = clamp(y2, 0, PANEL_ROWS - 1)

                for yy in range(y, y2 + 1):
                    for xx in range(x, x2 + 1):
                        canvas.SetPixel(xx, yy, r, g, b)

                # (Optional) draw a 1px border around it for definition
                color = graphics.Color(0, 0, 0)
                graphics.DrawLine(canvas, x, y, x2, y, color)
                graphics.DrawLine(canvas, x, y, x, y2, color)
                graphics.DrawLine(canvas, x2, y, x2, y2, color)
                graphics.DrawLine(canvas, x, y2, x2, y2, color)

            # Swap buffers on vsync to avoid tearing
            canvas = matrix.SwapOnVSync(canvas)
            frame += 1

            # Simple FPS cap
            elapsed = time.time() - start
            to_sleep = frame_time - elapsed
            if to_sleep > 0:
                time.sleep(to_sleep)

    finally:
        # Clear on exit so the panel goes dark
        matrix.Clear()

if __name__ == "__main__":
    main()
