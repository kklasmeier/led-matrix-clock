#!/bin/bash
# -----------------------------------------------------------------------------
# mem_logger.sh – log memory usage of the LED Clock process once per minute
# -----------------------------------------------------------------------------

LOG_DIR="/home/pi/Clock/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/memory_usage_$(date +%Y%m%d).log"

# The process name or PID to watch
PROC_NAME="python3"     # adjust if your service name changes

echo "=== Memory logger started at $(date) ===" >> "$LOG_FILE"

while true; do
    # Grab the PID of the clock's python process
    PID=$(pgrep -f "main.py")
    if [[ -n "$PID" ]]; then
        # Get RSS (resident set) in KiB and %MEM from ps
        STATS=$(ps -p "$PID" -o pid,%cpu,%mem,rss,etime,cmd --no-headers)
        echo "$(date '+%Y-%m-%d %H:%M:%S')  $STATS" >> "$LOG_FILE"
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S')  [no process found]" >> "$LOG_FILE"
    fi
    sleep 60
done

