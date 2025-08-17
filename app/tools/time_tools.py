"""
Time and date tools for Krishi Sahayak AI
Provides current time with agricultural context
"""

from datetime import datetime
import pytz

from langchain_core.tools import tool

@tool
def get_current_datetime(timezone: str = "Asia/Kolkata") -> str:
    """
    Gets the current date and time with agricultural activity recommendations.
    
    Args:
        timezone (str): The timezone for the date/time. Default is "Asia/Kolkata" for India.
                       Common options: "Asia/Kolkata", "UTC", "US/Eastern", etc.

    Returns:
        str: Current date, time, and relevant agricultural timing guidance.
    """
    print(f"--- Calling Current DateTime Tool for timezone: {timezone} ---")
    
    try:
        # Get current time in specified timezone
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        
        # Format the basic time information
        formatted_time = current_time.strftime("%A, %B %d, %Y at %I:%M %p %Z")
        
        # Get hour for activity recommendations
        hour = current_time.hour
        month = current_time.month
        day_of_week = current_time.strftime("%A")
        season = ""
        
        # Determine season (for Northern Hemisphere/India)
        if month in [12, 1, 2]:
            season = "Winter"
        elif month in [3, 4, 5]:
            season = "Spring"
        elif month in [6, 7, 8]:
            season = "Monsoon/Summer"
        else:
            season = "Post-Monsoon/Autumn"
        
        # Time-based agricultural recommendations
        time_recommendations = ""
        if 5 <= hour < 8:
            time_recommendations = "🌅 **Early Morning (5-8 AM)** - Ideal time for:\n"
            time_recommendations += "• Irrigation and watering\n"
            time_recommendations += "• Harvesting (crops are fresh and cool)\n"
            time_recommendations += "• Applying pesticides (less wind, better absorption)\n"
            time_recommendations += "• Farm inspections and planning\n"
        elif 8 <= hour < 11:
            time_recommendations = "🌞 **Morning (8-11 AM)** - Good time for:\n"
            time_recommendations += "• Field work and cultivation\n"
            time_recommendations += "• Transplanting seedlings\n"
            time_recommendations += "• Fertilizer application\n"
            time_recommendations += "• Equipment maintenance\n"
        elif 11 <= hour < 15:
            time_recommendations = "**Midday (11 AM-3 PM)** - Avoid heavy work, but suitable for:\n"
            time_recommendations += "• Indoor farm activities\n"
            time_recommendations += "• Planning and record keeping\n"
            time_recommendations += "• Drying harvested crops\n"
            time_recommendations += "• Market visits (avoid irrigation during this time)\n"
        elif 15 <= hour < 18:
            time_recommendations = "**Afternoon (3-6 PM)** - Good time for:\n"
            time_recommendations += "• Field preparations\n"
            time_recommendations += "• Weeding and pruning\n"
            time_recommendations += "• Seed treatment and preparation\n"
            time_recommendations += "• Animal care activities\n"
        elif 18 <= hour < 20:
            time_recommendations = "🌆 **Evening (6-8 PM)** - Ideal time for:\n"
            time_recommendations += "• Second irrigation session\n"
            time_recommendations += "• Harvesting leafy vegetables\n"
            time_recommendations += "• Organic pesticide application\n"
            time_recommendations += "• Planning next day's activities\n"
        else:
            time_recommendations = "🌙 **Night Time** - Rest period for farmers and crops:\n"
            time_recommendations += "• Avoid disturbing plants\n"
            time_recommendations += "• Good time for planning and learning\n"
            time_recommendations += "• Check weather forecasts\n"
            time_recommendations += "• Prepare for next day's work\n"
        
        # Season-based recommendations
        seasonal_advice = f"\n🍃 **{season} Season Guidance:**\n"
        if season == "Winter":
            seasonal_advice += "• Focus on winter crops (wheat, peas, mustard)\n"
            seasonal_advice += "• Reduce irrigation frequency\n"
            seasonal_advice += "• Protect crops from frost\n"
            seasonal_advice += "• Good time for soil preparation\n"
        elif season == "Spring":
            seasonal_advice += "• Prepare for summer crops\n"
            seasonal_advice += "• Start irrigation systems\n"
            seasonal_advice += "• Plant heat-tolerant varieties\n"
            seasonal_advice += "• Monitor for pest emergence\n"
        elif season == "Monsoon/Summer":
            seasonal_advice += "• Plant monsoon crops (rice, cotton, sugarcane)\n"
            seasonal_advice += "• Ensure proper drainage\n"
            seasonal_advice += "• Monitor for waterlogging\n"
            seasonal_advice += "• Pest and disease management\n"
        else:  # Post-Monsoon/Autumn
            seasonal_advice += "• Harvest monsoon crops\n"
            seasonal_advice += "• Prepare for winter sowing\n"
            seasonal_advice += "• Post-harvest processing\n"
            seasonal_advice += "• Field preparation for next cycle\n"
        
        # Day-specific recommendations
        day_advice = f"\n📅 **{day_of_week} Recommendations:**\n"
        if day_of_week in ["Monday", "Tuesday", "Wednesday", "Thursday"]:
            day_advice += "• Regular farm work and field activities\n"
            day_advice += "• Good days for heavy agricultural tasks\n"
            day_advice += "• Market visits for supplies\n"
        elif day_of_week == "Friday":
            day_advice += "• Complete weekly farm tasks\n"
            day_advice += "• Plan for weekend activities\n"
            day_advice += "• Equipment cleaning and maintenance\n"
        elif day_of_week == "Saturday":
            day_advice += "• Market day - sell produce\n"
            day_advice += "• Community farming activities\n"
            day_advice += "• Learn new farming techniques\n"
        else:  # Sunday
            day_advice += "• Rest day for farmers\n"
            day_advice += "• Light activities like planning\n"
            day_advice += "• Farm equipment rest day\n"
        
        # Combine all information
        result = f"📅 **Current Date & Time:**\n{formatted_time}\n\n"
        result += time_recommendations
        result += seasonal_advice
        result += day_advice
        result += f"\n⏰ **Agricultural Timing Tips:**\n"
        result += f"• Best irrigation: Early morning (6-8 AM) or evening (6-8 PM)\n"
        result += f"• Avoid spraying during hot midday hours\n"
        result += f"• Morning dew helps in pest control observations\n"
        result += f"• Evening time is ideal for foliar sprays\n"
        
        return result
        
    except Exception as e:
        return f"An error occurred while getting current time: {str(e)}"
