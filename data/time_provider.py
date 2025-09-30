# data/time_provider.py - Provides current time and date information

import time
from datetime import datetime
from typing import Dict, Any

class TimeProvider:
    """Provides current time and date information for the LED clock display"""
    
    def __init__(self):
        self.last_update = 0
        self.cached_data = {}
    
    def get_current_time(self) -> str:
        """
        Get current time in 12-hour format (HH:MM)
        
        Returns:
            str: Time in format like "10:47"
        """
        now = datetime.now()
        return now.strftime("%I:%M").lstrip('0')  # Remove leading zero from hour
    
    def get_current_ampm(self) -> str:
        """
        Get current AM/PM indicator
        
        Returns:
            str: "AM" or "PM"
        """
        now = datetime.now()
        return now.strftime("%p")
    
    def get_current_date(self) -> str:
        """
        Get current date in "Day Mon DD YYYY" format
        
        Returns:
            str: Date in format like "Mon Sep 29 2025"
        """
        now = datetime.now()
        # %a = abbreviated day name (Mon, Tue, etc.)
        # %b = abbreviated month name (Jan, Feb, etc.)
        # %d = day of month (01-31)
        # %Y = four-digit year
        return now.strftime("%a %b %d %Y").replace(' 0', ' ')  # Remove leading zero from day
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get all time-related data for display
        
        Returns:
            dict: Contains 'time', 'ampm', 'date', and 'timestamp'
        """
        current_time = time.time()
        
        # Always return fresh data for time (it changes every second)
        data = {
            'time': self.get_current_time(),
            'ampm': self.get_current_ampm(),
            'date': self.get_current_date(),
            'timestamp': current_time
        }
        
        self.cached_data = data
        self.last_update = current_time
        
        return data
    
    def is_stale(self, max_age_seconds: int = 1) -> bool:
        """
        Check if cached data is older than max_age_seconds
        
        Args:
            max_age_seconds: Maximum age in seconds before data is considered stale
            
        Returns:
            bool: True if data needs refresh
        """
        return (time.time() - self.last_update) > max_age_seconds
    
    def update(self) -> None:
        """
        Force update of time data (for compatibility with provider interface)
        """
        self.get_data()

# Global instance for easy access
_time_provider = None

def get_time_provider() -> TimeProvider:
    """Get or create the global TimeProvider instance"""
    global _time_provider
    if _time_provider is None:
        _time_provider = TimeProvider()
    return _time_provider