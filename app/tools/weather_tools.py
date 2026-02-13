"""
Consolidated Weather and Environmental Tools for Krishi Sahayak.
Provides weather forecast, air pollution, and UV index data using location names.
Lazy-loads pyowm to speed up application startup (~2.5s saved).
"""

from datetime import datetime
import re
from langchain_core.tools import tool
from app.config import Config

# --- LAZY INITIALIZATION ---
# pyowm is imported lazily because it loads a huge city ID registry at import time (~2.5s)
_mgr = None
_owm_initialized = False
_NotFoundError = None


def _get_weather_manager():
    """Lazily initialize the OpenWeatherMap client on first use."""
    global _mgr, _owm_initialized, _NotFoundError
    if not _owm_initialized:
        _owm_initialized = True
        try:
            from pyowm import OWM
            from pyowm.commons.exceptions import NotFoundError
            _NotFoundError = NotFoundError
            owm = OWM(Config.OPEN_WEATHER_API_KEY)
            _mgr = owm.weather_manager()
        except Exception as e:
            print(f"CRITICAL: Failed to initialize OpenWeatherMap client. Check API key. Error: {e}")
            _mgr = None
    return _mgr

def _extract_clean_location(location_param: str) -> str:
    """
    Extracts clean location value from tool parameter.
    Removes context text like 'location = "Hisar"' and returns just 'Hisar'
    """
    if not location_param:
        return None
    
    # Remove 'location = ' prefix if present
    if 'location' in location_param.lower() and '=' in location_param:
        # Extract the quoted or unquoted value after '='
        match = re.search(r'=\s*["\']?([^"\'\n]+)["\']?', location_param)
        if match:
            location_param = match.group(1).strip()
    
    # Remove any trailing context text (e.g., " (default location...")
    location_param = re.sub(r'\s*\([^)]*\).*$', '', location_param)
    location_param = location_param.strip('\'"')
    
    return location_param if location_param else None

# --- PRIMARY TOOLS ---

@tool
def get_weather_forecast(location: str) -> str:
    """
    Gets a detailed 5-day weather forecast for a location (city name or GPS coordinates).
    This is the primary tool for all weather-related queries.

    Args:
        location (str): Either a city name (e.g., "Hisar", "Ludhiana", "Pune") 
                       or GPS coordinates as "latitude,longitude" (e.g., "23.49,87.33")
    """
    mgr = _get_weather_manager()
    if not mgr:
        return "Weather service is currently unavailable. Please try again later."
    
    # Clean location parameter - remove context text if present
    location = _extract_clean_location(location) or location
    
    print(f"--- Calling Weather Tool for Location: {location} ---")
    
    # Check if location is coordinates (contains comma with numbers)
    location_display = location
    try:
        if ',' in location:
            parts = location.split(',')
            if len(parts) == 2:
                lat, lon = float(parts[0].strip()), float(parts[1].strip())
                # Use coordinates to get forecast
                forecast = mgr.forecast_at_coords(lat, lon, '3h').forecast
                location_display = f"coordinates ({lat}, {lon})"
            else:
                # Not valid coordinates, treat as city name
                forecast = mgr.forecast_at_place(location, '3h').forecast
        else:
            # Treat as city name
            forecast = mgr.forecast_at_place(location, '3h').forecast
    except Exception as e:
        if _NotFoundError and isinstance(e, _NotFoundError):
            return f"I'm sorry, I could not find the location '{location}'. Please provide a valid city name or GPS coordinates."
        return f"Error fetching weather for {location}: {e}"
    
    daily_forecasts = {}

    for weather in forecast.weathers:
        try:
            date_str = datetime.fromtimestamp(weather.reference_time()).strftime('%Y-%m-%d')
            if date_str not in daily_forecasts:
                daily_forecasts[date_str] = {'temps': [], 'conditions': [], 'rain_chance': False}
            
            # Safely get temperature
            temp_data = weather.temperature('celsius')
            if isinstance(temp_data, dict) and 'temp' in temp_data:
                daily_forecasts[date_str]['temps'].append(temp_data['temp'])
            
            # Safely get weather status
            if hasattr(weather, 'detailed_status') and weather.detailed_status:
                daily_forecasts[date_str]['conditions'].append(weather.detailed_status)
                
                # Check for rain in the weather status
                status = weather.detailed_status.lower()
                if 'rain' in status or 'drizzle' in status or 'shower' in status:
                    daily_forecasts[date_str]['rain_chance'] = True
                    
        except Exception as e:
            print(f"Error processing weather data point: {e}")
            continue

    # Check if we have any valid data
    if not daily_forecasts:
        return f"I'm sorry, I couldn't get weather data for {location_display}. Please try with a different location."

    summary = f"Here is the 5-day weather forecast for {location_display}:\n"
    for date, data in list(daily_forecasts.items())[:5]:
        if not data['temps'] or not data['conditions']:
            continue
        min_temp, max_temp = min(data['temps']), max(data['temps'])
        most_common_condition = max(set(data['conditions']), key=data['conditions'].count)
        day_str = f"- {date}: Min Temp: {min_temp:.1f}C, Max Temp: {max_temp:.1f}C. General condition: {most_common_condition}."
        if data['rain_chance']:
            day_str += " There is a chance of rain."
        summary += day_str + "\n"
    
    return summary.strip()

@tool
def get_air_pollution_data(location: str) -> str:
    """
    Gets current air pollution data for a location to assess crop and worker health.

    Args:
        location (str): The city or district name, e.g., "Hisar", "Ludhiana", "Pune".
    """
    mgr = _get_weather_manager()
    if not mgr:
        return "Environmental services are currently unavailable."
    
    print(f"--- Calling Air Pollution Tool for Location: {location} ---")
    try:
        # First, find the coordinates for the given location
        observation = mgr.weather_at_place(location)
        lat, lon = observation.location.lat, observation.location.lon
        
        # Now, get the air pollution data for those coordinates
        air_status = mgr.air_pollution_at(lat=lat, lon=lon)
        aqi = air_status.aqi

        if aqi == 1: advice = "Excellent air quality (AQI 1). Safe for all farming activities."
        elif aqi == 2: advice = "Good air quality (AQI 2). Normal farming activities can continue."
        elif aqi == 3: advice = "Moderate air quality (AQI 3). Sensitive crops may show minor stress."
        elif aqi == 4: advice = "Poor air quality (AQI 4). Consider protective measures for workers."
        else: advice = "Very poor air quality (AQI 5). Avoid heavy outdoor work if possible."
        
        return f"The current Air Quality Index (AQI) in {location} is {aqi}. {advice}"
        
    except Exception as e:
        if _NotFoundError and isinstance(e, _NotFoundError):
            return f"I'm sorry, I could not find a location named '{location}' to check the air quality."
        return f"An error occurred while fetching air pollution data for {location}: {e}"

@tool
def get_uv_index(location: str) -> str:
    """
    Gets the current UV Index for a location to assess worker safety and crop stress.

    Args:
        location (str): The city or district name, e.g., "Hisar", "Ludhiana", "Pune".
    """
    mgr = _get_weather_manager()
    if not mgr:
        return "Environmental services are currently unavailable."
        
    print(f"--- Calling UV Index Tool for Location: {location} ---")
    try:
        # First, find the coordinates for the given location
        observation = mgr.weather_at_place(location)
        lat, lon = observation.location.lat, observation.location.lon
        
        # Now, get the UV index for those coordinates
        uv_index = mgr.uvindex_around_coords(lat=lat, lon=lon)
        uv_value = uv_index.value
        risk = uv_index.get_exposure_risk()

        advice = ""
        if uv_value <= 2: advice = "Low risk. Good for transplanting delicate seedlings."
        elif uv_value <= 5: advice = "Moderate risk. Sun protection is recommended for workers."
        elif uv_value <= 7: advice = "High risk. Limit midday exposure for workers and sensitive crops."
        else: advice = "Very high to extreme risk. Minimize outdoor work between 10 AM and 4 PM."
        
        return f"The current UV Index in {location} is {uv_value:.1f} ({risk}). {advice}"
        
    except Exception as e:
        if _NotFoundError and isinstance(e, _NotFoundError):
            return f"I'm sorry, I could not find a location named '{location}' to check the UV index."
        return f"An error occurred while fetching UV Index data for {location}: {e}"