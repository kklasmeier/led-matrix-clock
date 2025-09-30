#!/bin/bash
# Stop the LED Matrix Clock service

echo "Stopping LED Matrix Clock..."
sudo systemctl stop ledclock.service

# Wait a moment and check status
sleep 1

if sudo systemctl is-active --quiet ledclock.service; then
    echo "Failed to stop the clock service."
    exit 1
else
    echo "LED Clock stopped successfully."
    echo "Lock file cleaned: /tmp/led_clock.pid"
fi
