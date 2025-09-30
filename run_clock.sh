#!/bin/bash
# Start the LED Matrix Clock service

echo "Starting LED Matrix Clock..."
sudo systemctl start ledclock.service

# Wait a moment and check status
sleep 2

if sudo systemctl is-active --quiet ledclock.service; then
    echo "LED Clock started successfully."
    echo "View logs: tail -f ~/Clock/logs/clock_$(date +%Y%m%d).log"
    echo "Check status: sudo systemctl status ledclock.service"
else
    echo "Failed to start the clock service."
    echo "Check logs for errors: journalctl -u ledclock.service -n 20"
    exit 1
fi
