"""
Soil and Irrigation Advisory Tool for Krishi Sahayak AI.
Provides soil moisture-derived insights and irrigation guidance using government data.
"""
import requests
from langchain_core.tools import tool
from app.config import Config

# --- PRIVATE HELPER FUNCTIONS ---

def _fetch_soil_api_data(district: str, state: str) -> dict:
    """A private helper to handle the API call and return the first valid record."""
    params = {
        "api-key": Config.GOV_IN_API_KEY,
        "format": "json",
        "limit": 5, # Fetch a few recent records to find the latest valid one
        "filters[district.keyword]": district
    }
    if state:
        params["filters[state.keyword]"] = state
    
    response = requests.get(Config.SOIL_API_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    return data.get("records", [{}])[0] if data.get("records") else {}

def _get_irrigation_advice(record: dict) -> str:
    """Derives a simple irrigation recommendation from a data record."""
    try:
        rainfall = float(record.get("rainfall_mm", 0))
        humidity = float(record.get("humidity_percent", 50))

        if rainfall > 10:
            return "Significant recent rainfall detected. Irrigation is likely not needed. Check soil manually."
        elif rainfall > 5:
            return "Some recent rainfall. Check soil moisture before irrigating."
        elif humidity < 40:
            return "Low humidity and little rain. Crops may need increased irrigation."
        elif humidity > 80:
            return "High humidity. Reduce irrigation and monitor for fungal diseases."
        else:
            return "Conditions are normal. Follow your regular irrigation schedule based on crop needs."
    except (ValueError, TypeError):
        return "Data not available for a specific recommendation. Check soil moisture manually."

def _get_fallback_guidance() -> str:
    """Provides generic, useful irrigation advice when no specific data is available."""
    return (
        "No specific soil moisture data could be found for your location.\n\n"
        "**General Irrigation Best Practices:**\n"
        "- The best time to water is early morning (before 10 AM).\n"
        "- Check soil moisture by inserting a finger 2-3 inches deep. If it's dry, it's time to water.\n"
        "- Consider using mulch around your crops to help the soil retain moisture.\n"
        "- Always check the local weather forecast before planning your irrigation schedule."
    )

# --- THE SIMPLIFIED TOOL ---

@tool
def get_soil_and_irrigation_advice(district: str, state: str = "") -> str:
    """
    Gets the latest available soil moisture and weather data for a given district
    and provides a specific irrigation recommendation.

    Args:
        district (str): The district name (e.g., "Hisar", "Ludhiana").
        state (str, optional): The state name for a more specific search (e.g., "Haryana").
    """
    print(f"--- Calling Soil Tool for District: {district}, State: {state} ---")
    try:
        latest_record = _fetch_soil_api_data(district, state)

        if not latest_record:
            return _get_fallback_guidance()

        # Extract key data points from the record
        date = latest_record.get("date", "N/A")
        rainfall = latest_record.get("rainfall_mm", "N/A")
        temp_min = latest_record.get("min_temp_c", "N/A")
        temp_max = latest_record.get("max_temp_c", "N/A")
        
        # Get a specific recommendation based on the data
        irrigation_advice = _get_irrigation_advice(latest_record)

        # Assemble a clean, readable summary
        summary = (
            f"Based on the latest data for {district} (on {date}):\n"
            f"- Recent Rainfall: {rainfall} mm\n"
            f"- Temperature Range: {temp_min}°C to {temp_max}°C\n\n"
            f"**Irrigation Advice:** {irrigation_advice}"
        )
        return summary

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to soil data API: {e}")
        return "I am having trouble connecting to the government's soil and weather data service right now."
    except Exception as e:
        print(f"An error occurred in the soil tool: {e}")
        return "An unexpected error occurred while fetching soil data."