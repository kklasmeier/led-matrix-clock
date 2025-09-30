#!/bin/bash
# Startup script for LED Matrix Clock with logging

# Set the working directory
cd /home/pi/Clock

# Create logs directory if it doesn't exist
mkdir -p /home/pi/Clock/logs

# Log file with date
LOG_FILE="/home/pi/Clock/logs/clock_$(date +%Y%m%d).log"

# Start the clock with unbuffered output redirected to log file
echo "=== LED Clock started at $(date) ===" >> "$LOG_FILE"
python3 -u main.py >> "$LOG_FILE" 2>&1
