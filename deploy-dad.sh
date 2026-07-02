#!/bin/bash
# Deploy piClock from this machine to Dad's Pi (PiClockDad).
# Preserves secrets, startup script, and Dad-specific config on the remote.
#
# Usage:
#   ./deploy-dad.sh
#   ./deploy-dad.sh pi@192.168.1.175

set -euo pipefail

HOST="${1:-pi@192.168.1.175}"
SRC="$(cd "$(dirname "$0")" && pwd)"
DST="/home/pi/Clock"

echo "Deploying piClock -> $HOST:$DST"
echo "Source: $SRC"
echo

rsync -avz --delete \
    --exclude 'secrets.json' \
    --exclude 'start_clock.sh' \
    --exclude 'config.py' \
    --exclude 'logs/' \
    --exclude '.git/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude 'nohup.out' \
    --exclude 'deploy-dad.sh' \
    "$SRC/" "$HOST:$DST/"

echo
echo "Restarting ledclock on $HOST ..."
ssh "$HOST" 'sudo systemctl restart ledclock.service && sleep 2 && systemctl is-active ledclock.service'

echo
echo "Done. Dad's secrets.json, start_clock.sh, and config.py were left unchanged."
