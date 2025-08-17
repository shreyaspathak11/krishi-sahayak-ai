"""
Market-related tools for Krishi Sahayak AI
Provides real-time crop prices from government sources
"""

import requests
from langchain_core.tools import tool

from app.config import Config

@tool
def get_market_prices(crop: str, market: str = "", state: str = "") -> str:
    """
    Gets real-time crop prices from specific markets using the official data.gov.in API.
    
    Args:
        crop (str): The name of the crop/commodity (e.g., "Wheat", "Rice", "Potato", "Tomato").
        market (str, optional): The name of the market/mandi (e.g., "Hisar", "Delhi", "Bangalore").
                               If empty, will search across all markets.
        state (str, optional): The state name (e.g., "Haryana", "Delhi", "Karnataka").
                              If empty, will search across all states.

    Returns:
        str: A string with the current price information from government data.
    """
    print(f"--- Calling Market Price Tool for Crop: {crop}" + 
          (f", Market: {market}" if market else "") + 
          (f", State: {state}" if state else "") + " ---")
    
    try:
        # Official data.gov.in API endpoint
        base_url = Config.MARKET_PRICE_API_URL

        # API parameters
        params = {
            "api-key": Config.GOV_IN_API_KEY,
            "format": "json",
            "limit": 20,
            "offset": 0
        }
        
        # Add filters for more specific search
        if market and market.strip():
            params["filters[market]"] = market
        if crop and crop.strip():
            params["filters[commodity]"] = crop
        if state and state.strip():
            params["filters[state.keyword]"] = state
            
        # Make API request
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if not data or "records" not in data or not data["records"]:
            return f"No price data found for {crop}" + (f" in {state}" if state else "") 

        records = data["records"]
        
        # Format the response
        price_info = f"Market Prices for {crop}:\n"
        price_info += "=" * 50 + "\n"
        
        for i, record in enumerate(records[:10], 1):  # Show top 10 results
            state_name = record.get("state", "N/A")
            district_name = record.get("district", "N/A")
            market_name = record.get("market", "N/A")
            commodity = record.get("commodity", "N/A")
            variety = record.get("variety", "N/A")
            grade = record.get("grade", "N/A")
            arrival_date = record.get("arrival_date", "N/A")
            min_price = record.get("min_price", "N/A")
            max_price = record.get("max_price", "N/A")
            modal_price = record.get("modal_price", "N/A")
            
            price_info += f"\n{i}. {market_name}, {district_name}, {state_name}\n"
            price_info += f"   Commodity: {commodity}"
            if variety != "N/A" and variety:
                price_info += f" ({variety})"
            if grade != "N/A" and grade:
                price_info += f" - Grade: {grade}"
            price_info += f"\n"
            price_info += f"   Date: {arrival_date}\n"
            price_info += f"   Min Price: ₹{min_price}/quintal\n"
            price_info += f"   Max Price: ₹{max_price}/quintal\n"
            price_info += f"   Modal Price: ₹{modal_price}/quintal\n"
            
        price_info += f"\nNote: Prices are in Indian Rupees per quintal (100 kg)"
        price_info += f"\nData source: Government of India - data.gov.in"
        
        return price_info
        
    except requests.exceptions.RequestException as e:
        return f"Error connecting to government price data API: {str(e)}"
    except Exception as e:
        return f"An error occurred while fetching market prices: {str(e)}"
