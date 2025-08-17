"""
Weather-related tools for Krishi Sahayak AI
Provides weather forecast, air pollution, and UV index data
"""

from datetime import datetime
from langchain_core.tools import tool
from pyowm import OWM

from app.config import Config

# Initialize OWM only if API key is available
owm = OWM(Config.OPEN_WEATHER_API_KEY)
mgr = owm.weather_manager()
air_mgr = owm.airpollution_manager()
uv_mgr = owm.uvindex_manager()


@tool
def get_weather_forecast(latitude: float, longitude: float) -> str:
    """Gets a detailed 5-day weather forecast for agricultural planning."""
    if not mgr: 
        return "Weather service is not available. Please check your OpenWeatherMap API key."
    
    print(f"--- Calling Weather Tool for Lat: {latitude}, Lon: {longitude} ---")
    try:
        # Use 5-day forecast (free tier) with 3-hour intervals
        forecast = mgr.forecast_at_coords(latitude, longitude, '3h')
        
        summary = "5-Day Weather Forecast:\n"
        summary += "=" * 40 + "\n"
        
        # Group forecasts by date
        daily_forecasts = {}
        for weather in forecast.forecast.weathers:
            date_str = datetime.fromtimestamp(weather.reference_time()).strftime('%Y-%m-%d')
            if date_str not in daily_forecasts:
                daily_forecasts[date_str] = []
            daily_forecasts[date_str].append(weather)
        
        # Get daily summaries (first 5 days)
        for i, (date_str, weathers) in enumerate(list(daily_forecasts.items())[:5], 1):
            # Get min/max temperatures for the day
            temps = [w.temperature('celsius')['temp'] for w in weathers]
            min_temp = min(temps)
            max_temp = max(temps)
            
            # Get most common weather condition
            conditions = [w.detailed_status for w in weathers]
            most_common_condition = max(set(conditions), key=conditions.count)
            
            summary += f"\nDay {i} ({date_str}):\n"
            summary += f"  Min Temp: {min_temp:.1f}°C\n"
            summary += f"  Max Temp: {max_temp:.1f}°C\n"
            summary += f"  Condition: {most_common_condition}\n"
        
        summary += f"\nNote: Best farming times are early morning (5-10 AM) and late afternoon (4-7 PM)"
        return summary
        
    except Exception as e:
        return f"An error occurred while fetching the weather forecast: {e}"

@tool
def get_air_pollution_data(latitude: float, longitude: float) -> str:
    """Gets current air pollution data for crop health assessment."""
    if not air_mgr: 
        return "Air pollution service is not available. Please check your OpenWeatherMap API key."
    
    print(f"--- Calling Air Pollution Tool for Lat: {latitude}, Lon: {longitude} ---")
    try:
        air_status = air_mgr.air_quality_at_coords(lat=latitude, lon=longitude)
        aqi = air_status.aqi
        
        # Provide agricultural context for AQI
        if aqi == 1:
            advice = "Excellent air quality. Safe for all outdoor farming activities."
        elif aqi == 2:
            advice = "Good air quality. Normal farming activities can continue."
        elif aqi == 3:
            advice = "Moderate air quality. Sensitive crops may be affected."
        elif aqi == 4:
            advice = "Poor air quality. Consider protective measures for crops and workers."
        else:  # aqi == 5
            advice = "Very poor air quality. Avoid heavy outdoor work, protect sensitive crops."
        
        summary = f"Current Air Quality: AQI is {aqi} (1=Good, 5=Very Poor).\n{advice}"
        return summary
        
    except Exception as e:
        return f"An error occurred while fetching air pollution data: {e}"

@tool
def get_uv_index(latitude: float, longitude: float) -> str:
    """Gets the current UV Index for worker safety and crop protection."""
    if not uv_mgr: 
        return "UV Index service is not available. Please check your OpenWeatherMap API key."
    
    print(f"--- Calling UV Index Tool for Lat: {latitude}, Lon: {longitude} ---")
    try:
        uv_index = uv_mgr.uvindex_around_coords(lat=latitude, lon=longitude)
        risk = uv_index.get_exposure_risk()
        uv_value = uv_index.value
        
        # Provide agricultural context for UV levels
        if uv_value <= 2:
            advice = "Low UV. Safe for extended outdoor work. Good for transplanting delicate seedlings."
        elif uv_value <= 5:
            advice = "Moderate UV. Use sun protection for workers. Normal farming activities."
        elif uv_value <= 7:
            advice = "High UV. Limit midday exposure. Consider shade for sensitive crops."
        elif uv_value <= 10:
            advice = "Very high UV. Avoid 10 AM - 4 PM work. Protect workers and sensitive plants."
        else:
            advice = "Extreme UV. Minimize outdoor exposure. Use protective coverings for crops."
        
        summary = f"Current UV Index: {uv_value} (Exposure Risk: {risk})\n{advice}"
        return summary
        
    except Exception as e:
        return f"An error occurred while fetching UV Index data: {e}"
