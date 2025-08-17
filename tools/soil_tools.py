"""
Soil-related tools for Krishi Sahayak AI
Provides soil moisture and irrigation guidance
"""

import requests
from langchain_core.tools import tool

from app.config import Config

@tool
def get_soil_moisture_data(district: str, state: str = "") -> str:
    """
    Gets real-time soil moisture data and irrigation guidance using government weather data.
    
    Args:
        district (str): The district name (e.g., "Delhi", "Bangalore", "Hisar").
        state (str, optional): The state name for more specific search.

    Returns:
        str: A string with soil moisture levels and irrigation recommendations.
    """
    try:
        # Government weather API endpoint for soil moisture data
        base_url = Config.SOIL_API_URL

        # API parameters
        params = {
            "api-key": Config.GOV_IN_API_KEY,
            "format": "json",
            "limit": 10,
            "offset": 0
        }
        
        # Add district filter
        if district and district.strip():
            params["filters[district.keyword]"] = district
        if state and state.strip():
            params["filters[state.keyword]"] = state
            
        # Make API request
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if not data or "records" not in data or not data["records"]:
            # Provide fallback irrigation guidance
            return f"""No specific soil moisture data found for {district}{f', {state}' if state else ''}.

General Irrigation Guidelines:
================================

**Crop Stage-wise Water Requirements:**
- Germination: Light, frequent watering
- Vegetative growth: Moderate watering 
- Flowering/Fruiting: Increased water needs
- Maturity: Reduced watering

**Soil Moisture Indicators:**
- Sandy soil: Water when top 2-3 inches are dry
- Clay soil: Water when top 1-2 inches are dry
- Loamy soil: Water when top 2 inches are dry

**General Recommendations:**
- Early morning (6-8 AM) is best time for irrigation
- Avoid watering during hot afternoon hours
- Use drip irrigation for water efficiency
- Mulching helps retain soil moisture
- Check weather forecast before irrigation

**Water Conservation Tips:**
- Monitor soil moisture with simple finger test
- Use moisture-retaining organic matter
- Practice crop rotation for soil health
- Consider rainwater harvesting"""
        
        records = data["records"]
        
        # Format the response
        moisture_info = f"Soil Moisture Data for {district}:\n"
        moisture_info += "=" * 50 + "\n"
        
        for i, record in enumerate(records[:5], 1):
            state_name = record.get("state", "N/A")
            district_name = record.get("district", "N/A")
            date = record.get("date", "N/A")
            rainfall = record.get("rainfall_mm", "N/A")
            temperature_max = record.get("max_temp_c", "N/A")
            temperature_min = record.get("min_temp_c", "N/A")
            humidity = record.get("humidity_percent", "N/A")
            
            moisture_info += f"\n{i}. Weather Data - {district_name}, {state_name}\n"
            moisture_info += f"   Date: {date}\n"
            moisture_info += f"   Rainfall: {rainfall} mm\n"
            moisture_info += f"   Temperature: {temperature_min}°C - {temperature_max}°C\n"
            moisture_info += f"   Humidity: {humidity}%\n"
            
            # Provide irrigation guidance based on data
            try:
                rainfall_val = float(rainfall) if str(rainfall).replace('.', '').isdigit() else 0
                humidity_val = float(humidity) if str(humidity).replace('.', '').isdigit() else 50
                
                if rainfall_val > 10:
                    irrigation_advice = "Recent good rainfall - irrigation may not be needed"
                elif rainfall_val > 5:
                    irrigation_advice = "Moderate rainfall - check soil moisture before irrigation"
                elif humidity_val < 40:
                    irrigation_advice = "Low humidity - increased irrigation may be needed"
                elif humidity_val > 80:
                    irrigation_advice = "High humidity - monitor for fungal diseases, reduce irrigation"
                else:
                    irrigation_advice = "Normal conditions - follow regular irrigation schedule"
                    
                moisture_info += f"   Irrigation Advice: {irrigation_advice}\n"
            except:
                moisture_info += f"   Irrigation Advice: Check soil moisture manually\n"
        
        moisture_info += f"\n**General Irrigation Guidelines:**\n"
        moisture_info += f"• Best time: Early morning (6-8 AM) or evening (6-8 PM)\n"
        moisture_info += f"• Avoid midday watering to prevent water loss\n"
        moisture_info += f"• Use finger test: Insert finger 2-3 inches into soil\n"
        moisture_info += f"• Dry soil = irrigation needed, moist soil = wait\n"
        moisture_info += f"• Consider weather forecast before irrigation\n"
        moisture_info += f"\nData source: Government weather monitoring stations"
        
        return moisture_info
        
    except requests.exceptions.RequestException as e:
        return f"Error connecting to government weather data API: {str(e)}"
    except Exception as e:
        return f"An error occurred while fetching soil moisture data: {str(e)}"
