# utils/wifi_status.py - WiFi status for on-display feedback (background polling)

import subprocess
import threading
import time
from typing import List, Optional

_CHECK_INTERVAL_CONNECTED_SEC = 30.0
_CHECK_INTERVAL_DISCONNECTED_SEC = 5.0

_lock = threading.Lock()
_cached_connected: Optional[bool] = None
_cached_headlines: Optional[List[str]] = None
_monitor_running = False
_monitor_thread: Optional[threading.Thread] = None
_refresh_event = threading.Event()


def _run_nmcli(args: List[str]) -> str:
    try:
        result = subprocess.run(
            ["nmcli", *args],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return ""
        return result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def get_wlan_state() -> str:
    """Return wlan0 state: connected, connecting, disconnected, etc."""
    output = _run_nmcli(["-t", "-f", "DEVICE,STATE", "dev", "status"])
    for line in output.splitlines():
        if line.startswith("wlan0:"):
            return line.split(":", 1)[1]
    return "unknown"


def get_saved_wifi_names() -> List[str]:
    names: List[str] = []
    output = _run_nmcli(["-t", "-f", "NAME,TYPE", "connection", "show"])
    for line in output.splitlines():
        if ":" not in line:
            continue
        name, conn_type = line.split(":", 1)
        if conn_type == "802-11-wireless":
            names.append(name)
    return names


def get_active_wifi_name() -> str:
    output = _run_nmcli(["-t", "-f", "NAME,DEVICE", "connection", "show", "--active"])
    for line in output.splitlines():
        if line.endswith(":wlan0"):
            return line.rsplit(":", 1)[0]
    return ""


def _build_wifi_headlines() -> List[str]:
    state = get_wlan_state()
    networks = get_saved_wifi_names()
    net_list = ", ".join(networks) if networks else "none saved"

    if state == "connecting":
        lead = "Connecting to WiFi..."
    elif state in ("disconnected", "unavailable"):
        lead = "Searching for WiFi..."
    else:
        lead = "Waiting for WiFi..."

    return [
        lead,
        f"Known: {net_list}",
        "Updates when online",
        "Please wait",
    ]


def _poll_wifi_status() -> None:
    global _cached_connected, _cached_headlines
    connected = get_wlan_state() == "connected"
    with _lock:
        _cached_connected = connected
        if connected:
            _cached_headlines = None
        else:
            _cached_headlines = _build_wifi_headlines()


def _monitor_loop() -> None:
    while _monitor_running:
        try:
            _poll_wifi_status()
        except Exception as exc:
            print(f"WiFi monitor error: {exc}")
        with _lock:
            interval = (
                _CHECK_INTERVAL_CONNECTED_SEC
                if _cached_connected
                else _CHECK_INTERVAL_DISCONNECTED_SEC
            )
        _refresh_event.wait(interval)
        _refresh_event.clear()


def start_wifi_monitor() -> None:
    """Start background WiFi polling (never blocks the display loop)."""
    global _monitor_running, _monitor_thread
    if _monitor_thread and _monitor_thread.is_alive():
        return
    _poll_wifi_status()
    _monitor_running = True
    _monitor_thread = threading.Thread(
        target=_monitor_loop, daemon=True, name="wifi-monitor"
    )
    _monitor_thread.start()


def stop_wifi_monitor() -> None:
    global _monitor_running
    _monitor_running = False
    _refresh_event.set()


def refresh_wifi_status() -> None:
    """Request an immediate background refresh (non-blocking)."""
    _refresh_event.set()


def is_wifi_connected() -> bool:
    with _lock:
        if _cached_connected is None:
            return False
        return _cached_connected


def get_wifi_status_headlines() -> List[str]:
    with _lock:
        if _cached_headlines is not None:
            return list(_cached_headlines)
    return [
        "Searching for WiFi...",
        "Please wait",
    ]
