#!/bin/bash
# Check LED Matrix Clock status

echo "=== LED Matrix Clock Status ==="
sudo systemctl status ledclock.service --no-pager

echo ""
echo "=== Recent Log Entries ==="
tail -n 10 ~/Clock/logs/clock_$(date +%Y%m%d).log 2>/dev/null || echo "No logs found for today"
