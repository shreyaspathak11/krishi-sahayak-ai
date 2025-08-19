"""
Tools Package - Krishi Sahayak AI
"""

# Weather tools
from .weather_tools import (
    get_weather_forecast,
    get_air_pollution_data,
    get_uv_index
)

# Market tools  
from .market_tools import (
    get_market_prices
)

# Soil tools
from .soil_tools import (
    get_soil_and_irrigation_advice
)

# Time tools
from .time_tools import (
    get_current_datetime
)

# Knowledge tools
from .knowledge_tools import (
    get_crop_advisory,
    get_vector_store
)

# News tools
from .news_tools import (
    get_agricultural_news
)

__all__ = [
    # Weather
    "get_weather_forecast",
    "get_air_pollution_data", 
    "get_uv_index",
    # Market
    "get_market_prices",
    # Soil
    "get_soil_and_irrigation_advice",
    # Time
    "get_current_datetime",
    # Knowledge
    "get_crop_advisory",
    "get_vector_store",
    # News
    "get_agricultural_news"
]