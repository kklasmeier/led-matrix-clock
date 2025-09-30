# data/weather_provider.py - Provides weather information from Open-Meteo API

import json
import urllib.request
import time
import os
from typing import Dict, Any, Optional

def load_secrets() -> Dict[str, Any]:
    """
    Load secrets from secrets.json file
    
    Returns:
        Dictionary of secrets
        
    Raises:
        FileNotFoundError: If secrets.json doesn't exist
        json.JSONDecodeError: If secrets.json is invalid
    """
    # Get the path to secrets.json (in project root, one level up from data/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    secrets_path = os.path.join(current_dir, '..', 'secrets.json')
    
    with open(secrets_path, 'r') as f:
        return json.load(f)

class WeatherProvider:
    """Provides current weather information for the LED clock display"""
    
    def __init__(self, latitude: Optional[float] = None, longitude: Optional[float] = None):
        """
        Initialize weather provider
        
        Args:
            latitude: Location latitude (optional, reads from secrets.json if not provided)
            longitude: Location longitude (optional, reads from secrets.json if not provided)
            
        Raises:
            ValueError: If latitude/longitude not found in secrets.json or parameters
            FileNotFoundError: If secrets.json doesn't exist
        """
        # Try to get location from parameters first, then from secrets.json
        if latitude is not None and longitude is not None:
            self.latitude = latitude
            self.longitude = longitude
        else:
            try:
                secrets = load_secrets()
                self.latitude = secrets.get('LATITUDE')
                self.longitude = secrets.get('LONGITUDE')
                
                if self.latitude is None or self.longitude is None:
                    raise ValueError(
                        "LATITUDE and LONGITUDE not found in secrets.json. "
                        "Please add them to secrets.json (see secrets.example.json)"
                    )
            except FileNotFoundError:
                raise FileNotFoundError(
                    "secrets.json not found. "
                    "Please create it from secrets.example.json and add your location"
                )
        
        self.last_update = 0
        self.cached_data = {}
        self.update_interval = 900  # 15 minutes
        
        # Build API URL
        self.api_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={self.latitude}&longitude={self.longitude}"
            f"&current_weather=true"
            f"&daily=temperature_2m_max,temperature_2m_min"
            f"&timezone=auto"
            f"&temperature_unit=fahrenheit"
        )
    
    def fetch_weather_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetch current weather data from Open-Meteo API
        
        Returns:
            Dict with weather data or None if error
        """
        try:
            with urllib.request.urlopen(self.api_url, timeout=10) as response:
                data = json.load(response)
            
            # Extract the data we need
            current_temp = int(round(data["current_weather"]["temperature"]))
            high_temp = int(round(data["daily"]["temperature_2m_max"][0]))
            low_temp = int(round(data["daily"]["temperature_2m_min"][0]))
            
            return {
                "current": current_temp,
                "high": high_temp,
                "low": low_temp,
                "timestamp": time.time()
            }
            
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return None
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get weather data for display
        
        Returns:
            dict: Contains formatted weather strings and raw data
        """
        current_time = time.time()
        
        # Update if cache is stale or empty
        if self.is_stale() or not self.cached_data:
            fresh_data = self.fetch_weather_data()
            if fresh_data:
                self.cached_data = fresh_data
                self.last_update = current_time
            elif not self.cached_data:
                # If no cached data and API fails, return default
                self.cached_data = {
                    "current": 70,
                    "high": 75,
                    "low": 65,
                    "timestamp": current_time
                }
        
        # Format for display
        return {
            "high_low_text": f"H{self.cached_data['high']} L{self.cached_data['low']}",
            "current_text": f"Now {self.cached_data['current']}",
            "current": self.cached_data["current"],
            "high": self.cached_data["high"],
            "low": self.cached_data["low"],
            "timestamp": self.cached_data["timestamp"]
        }
    
    def is_stale(self, max_age_seconds: Optional[int] = None) -> bool:
        """
        Check if cached data is older than update interval
        
        Args:
            max_age_seconds: Override default update interval
            
        Returns:
            bool: True if data needs refresh
        """
        max_age = max_age_seconds or self.update_interval
        return (time.time() - self.last_update) > max_age
    
    def update(self) -> None:
        """
        Force update of weather data
        """
        self.fetch_weather_data()

# Global instance for easy access
_weather_provider: Optional[WeatherProvider] = None

def get_weather_provider() -> WeatherProvider:
    """Get or create the global WeatherProvider instance"""
    global _weather_provider
    if _weather_provider is None:
        _weather_provider = WeatherProvider()
    return _weather_provider