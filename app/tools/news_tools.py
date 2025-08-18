"""
Consolidated News Tool for Krishi Sahayak 
Fetches the latest, most relevant agricultural news on a specified topic.
"""
import requests
from langchain_core.tools import tool
from app.config import Config

# --- PRIVATE HELPER FUNCTION ---

def _fetch_gnews_articles(query: str, max_articles: int) -> list:
    """A private helper function to handle the actual API call and error handling."""
    if not Config.GNEWS_API_KEY:
        raise ValueError("GNews API key is not configured.")

    params = {
        "q": query,
        "lang": "en",
        "country": "in", # Hardcode for India as it's the target audience
        "max": max_articles,
        "apikey": Config.GNEWS_API_KEY,
        "sortby": "publishedAt"
    }
    
    try:
        response = requests.get(Config.GNEWS_URL, params=params, timeout=10)
        response.raise_for_status() # Raises an exception for bad status codes (4xx or 5xx)
        return response.json().get("articles", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news from GNews API: {e}")
        return [] 

# --- THE ONLY NEWS TOOL YOU NEED ---

@tool
def get_agricultural_news(topic: str) -> str:
    """
    Fetches the latest news about a specific agricultural topic. Use this tool
    to find information on market trends, new technologies, weather impacts,
    or general farming news.

    Args:
        topic (str): The specific category of news to fetch. Must be one of
                     ["general", "technology", "market", "weather"].
    """
    print(f"--- Calling News Tool for Topic: '{topic}' ---")

    # A dictionary to map simple topics to complex search queries.
    # This keeps the logic clean and easy to extend.
    topic_keywords = {
        "general": "agriculture OR farming OR crops OR \"farm subsidies\"",
        "technology": "\"agricultural technology\" OR \"smart farming\" OR \"precision agriculture\" OR \"drone farming\"",
        "market": "\"agricultural market\" OR \"crop prices\" OR \"commodity prices\" OR \"mandi prices\"",
        "weather": "\"weather agriculture\" OR \"drought crops\" OR \"monsoon farming\" OR \"climate change agriculture\""
    }

    # Validate the input topic
    if topic not in topic_keywords:
        return f"Invalid topic '{topic}'. Please use one of the following: {list(topic_keywords.keys())}"

    query = topic_keywords[topic]
    articles = _fetch_gnews_articles(query, max_articles=4)

    if not articles:
        return f"I could not find any recent news on the topic of '{topic}'."

    # Format the articles into a clean, human-readable string for the AI
    summary = f"Here are the top news headlines regarding '{topic}':\n"
    for article in articles:
        title = article.get("title", "No Title")
        source = article.get("source", {}).get("name", "Unknown Source")
        summary += f"- {title} (Source: {source})\n"
        
    return summary.strip()