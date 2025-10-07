# data/weather_provider.py - Provides weather information from Open-Meteo API

import json
import urllib.request
import time
import os
from typing import Dict, Any, Optional
from datetime import datetime

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
        
        # Build API URL - now includes hourly weather codes
        self.api_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={self.latitude}&longitude={self.longitude}"
            f"&current_weather=true"
            f"&daily=temperature_2m_max,temperature_2m_min"
            f"&hourly=weather_code"
            f"&timezone=auto"
            f"&temperature_unit=fahrenheit"
            f"&forecast_hours=8"
        )
    
    def _classify_weather_code(self, code: int) -> str:
        """
        Classify WMO weather code into display category
        
        Args:
            code: WMO weather code (0-99)
            
        Returns:
            Category string: 'clear', 'partly_cloudy', 'cloudy', 'rain', 
                           'thunderstorm', 'snow', 'fog', 'freezing_rain', 'heavy_rain'
        """
         
        if code == 0:
            return 'clear'
        elif code in [1, 2]:
            return 'partly_cloudy'
        elif code == 3:
            return 'cloudy'
        elif code in [45, 48]:
            return 'fog'
        elif code in [51, 53, 55, 61, 80, 81]:
            return 'rain'
        elif code in [63, 65, 82]:
            return 'heavy_rain'
        elif code in [56, 57, 66, 67]:
            return 'freezing_rain'
        elif code in [71, 73, 75, 77, 85, 86]:
            return 'snow'
        elif code in [95, 96, 99]:
            return 'thunderstorm'
        else:
            return 'cloudy'  # default fallback
    
    def get_weighted_forecast_condition(self, current_code: int, hourly_codes: list) -> str:
        """
        Calculate weighted forecast condition based on current + next 8 hours
        
        Uses time-weighted voting where each hour contributes to the final
        decision based on the weights configured in config.Weather.FORECAST_WEIGHTS
        
        Args:
            current_code: Current weather code (WMO)
            hourly_codes: List of next 8 hourly weather codes
            
        Returns:
            Condition string for icon display (e.g., 'rain', 'clear', 'cloudy')
        """
        # Import config here to avoid circular imports
        try:
            from config import Weather as WeatherConfig
            weights = WeatherConfig.FORECAST_WEIGHTS
            current_weight = WeatherConfig.CURRENT_WEIGHT
        except ImportError:
            # Fallback to default weights if config not available
            weights = [2, 2, 4, 4, 1, 1, 1, 1]
            current_weight = 3
        
        # Weighted voting by category
        category_scores = {}
        
        # Add current weather with its own weight
        current_category = self._classify_weather_code(current_code)
        category_scores[current_category] = current_weight
        
        # Add forecasted hours with their respective weights
        for i, code in enumerate(hourly_codes[:8]):  # Only use first 8 hours
            if i >= len(weights):
                break
            
            category = self._classify_weather_code(code)
            weight = weights[i]
            category_scores[category] = category_scores.get(category, 0) + weight
        
        # Return category with highest weighted score
        if category_scores:
            return max(category_scores, key=category_scores.get)
        else:
            return 'cloudy'  # fallback
    
    def is_nighttime(self) -> bool:
        """
        Determine if it's currently nighttime
        
        Uses simple time-based heuristic from config.Weather settings
        For more accuracy, could use sunrise/sunset times from API
        
        Returns:
            True if nighttime, False if daytime
        """
        try:
            from config import Weather as WeatherConfig
            method = WeatherConfig.DAY_NIGHT_METHOD
            
            if method == 'simple':
                now = datetime.now()
                hour = now.hour
                night_start = WeatherConfig.SIMPLE_NIGHT_START
                night_end = WeatherConfig.SIMPLE_NIGHT_END
                
                # Handle wraparound (e.g., 20:00 to 6:00)
                if night_start > night_end:
                    return hour >= night_start or hour < night_end
                else:
                    return night_start <= hour < night_end
            else:
                # 'api' method would use sunrise/sunset from cached_data
                # For now, fall back to simple check
                hour = datetime.now().hour
                return hour >= 20 or hour < 6
                
        except (ImportError, AttributeError):
            # Fallback: simple 8pm-6am check
            hour = datetime.now().hour
            return hour >= 20 or hour < 6
    
    def fetch_weather_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetch current weather data from Open-Meteo API
        
        Returns:
            Dict with weather data including temps and forecast condition, or None if error
        """
        try:
            with urllib.request.urlopen(self.api_url, timeout=10) as response:
                data = json.load(response)
            
            # Extract temperature data
            current_temp = int(round(data["current_weather"]["temperature"]))
            high_temp = int(round(data["daily"]["temperature_2m_max"][0]))
            low_temp = int(round(data["daily"]["temperature_2m_min"][0]))
            
            # Extract current and hourly weather codes
            current_code = data["current_weather"]["weathercode"]
            hourly_codes = data["hourly"]["weather_code"][:8]  # Next 8 hours
            
            # Calculate weighted forecast condition
            forecast_condition = self.get_weighted_forecast_condition(
                current_code, 
                hourly_codes
            )
            
            # Determine if it's nighttime
            is_night = self.is_nighttime()
            
            # Print forecast icon selection for debugging
            day_night = "night" if is_night else "day"
            print(f"Weather updated: Icon='{forecast_condition}' ({day_night}) | Current code: {current_code} | Next 8hrs: {hourly_codes}")
            
            return {
                "current": current_temp,
                "high": high_temp,
                "low": low_temp,
                "condition": forecast_condition,
                "is_night": is_night,
                "current_code": current_code,
                "hourly_codes": hourly_codes,
                "timestamp": time.time()
            }
            
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return None
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get weather data for display
        
        Returns:
            dict: Contains formatted weather strings, icon condition, and raw data
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
                    "condition": "cloudy",
                    "is_night": self.is_nighttime(),
                    "current_code": 3,
                    "hourly_codes": [3] * 8,
                    "timestamp": current_time
                }
        
        # Format for display
        return {
            # Temperature strings
            "high_low_text": f"H{self.cached_data['high']} L{self.cached_data['low']}",
            "current_text": f"Now {self.cached_data['current']}",
            
            # Raw temperature values
            "current": self.cached_data["current"],
            "high": self.cached_data["high"],
            "low": self.cached_data["low"],
            
            # Icon information
            "condition": self.cached_data["condition"],
            "is_night": self.cached_data["is_night"],
            
            # Debug/raw data
            "current_code": self.cached_data.get("current_code", 0),
            "hourly_codes": self.cached_data.get("hourly_codes", []),
            
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