"""
News tools for fetching latest agriculture news
"""

import requests
from typing import List, Dict, Any
from langchain.tools import tool
from app.config import Config


@tool
def get_agriculture_news(country: str = "in", language: str = "en", max_articles: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch latest agriculture news from reliable sources.
    
    Args:
        country: Country code (default: "in" for India)
        language: Language code (default: "en" for English)
        max_articles: Maximum number of articles to return (default: 5)
    
    Returns:
        List of news articles with title, description, source, url, and publish date
    """
    try:
        url = Config.GNEWS_URL
        
        params = {
            "q": "agriculture OR farming OR crops OR agricultural technology OR farming techniques OR crop yield OR agricultural policy OR farm subsidies",
            "lang": language,
            "country": country,
            "max": max_articles,
            "apikey": Config.GNEWS_API_KEY,
            "sortby": "publishedAt"  # Sort by latest first
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        articles = data.get("articles", [])
        
        # Format articles for better readability
        formatted_articles = []
        for article in articles:
            formatted_article = {
                "title": article.get("title", "No title"),
                "description": article.get("description", "No description"),
                "source": article.get("source", {}).get("name", "Unknown source"),
                "url": article.get("url", ""),
                "published_at": article.get("publishedAt", "Unknown date"),
                "image": article.get("image", "")
            }
            formatted_articles.append(formatted_article)
        
        return formatted_articles
        
    except requests.exceptions.RequestException as e:
        return [{"error": f"Failed to fetch news: Network error - {str(e)}"}]
    except Exception as e:
        return [{"error": f"Failed to fetch agriculture news: {str(e)}"}]


@tool
def get_farming_technology_news(country: str = "in", language: str = "en", max_articles: int = 3) -> List[Dict[str, Any]]:
    """
    Fetch latest farming technology and innovation news.
    
    Args:
        country: Country code (default: "in" for India)
        language: Language code (default: "en" for English)
        max_articles: Maximum number of articles to return (default: 3)
    
    Returns:
        List of news articles about farming technology and innovations
    """
    try:
        url = Config.GNEWS_URL

        params = {
            "q": "agricultural technology OR smart farming OR precision agriculture OR drone farming OR AI agriculture OR agricultural innovation OR farm automation",
            "lang": language,
            "country": country,
            "max": max_articles,
            "apikey": Config.GNEWS_API_KEY,
            "sortby": "publishedAt"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        articles = data.get("articles", [])
        
        formatted_articles = []
        for article in articles:
            formatted_article = {
                "title": article.get("title", "No title"),
                "description": article.get("description", "No description"),
                "source": article.get("source", {}).get("name", "Unknown source"),
                "url": article.get("url", ""),
                "published_at": article.get("publishedAt", "Unknown date"),
                "category": "Technology"
            }
            formatted_articles.append(formatted_article)
        
        return formatted_articles
        
    except requests.exceptions.RequestException as e:
        return [{"error": f"Failed to fetch technology news: Network error - {str(e)}"}]
    except Exception as e:
        return [{"error": f"Failed to fetch farming technology news: {str(e)}"}]


@tool
def get_market_agriculture_news(country: str = "in", language: str = "en", max_articles: int = 3) -> List[Dict[str, Any]]:
    """
    Fetch latest agriculture market and commodity news.
    
    Args:
        country: Country code (default: "in" for India)
        language: Language code (default: "en" for English)
        max_articles: Maximum number of articles to return (default: 3)
    
    Returns:
        List of news articles about agriculture markets and commodity prices
    """
    try:
        url = Config.GNEWS_URL

        params = {
            "q": "agricultural market OR crop prices OR commodity prices OR agricultural exports OR farm income OR agricultural trade OR mandi prices",
            "lang": language,
            "country": country,
            "max": max_articles,
            "apikey": Config.GNEWS_API_KEY,
            "sortby": "publishedAt"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        articles = data.get("articles", [])
        
        formatted_articles = []
        for article in articles:
            formatted_article = {
                "title": article.get("title", "No title"),
                "description": article.get("description", "No description"),
                "source": article.get("source", {}).get("name", "Unknown source"),
                "url": article.get("url", ""),
                "published_at": article.get("publishedAt", "Unknown date"),
                "category": "Market"
            }
            formatted_articles.append(formatted_article)
        
        return formatted_articles
        
    except requests.exceptions.RequestException as e:
        return [{"error": f"Failed to fetch market news: Network error - {str(e)}"}]
    except Exception as e:
        return [{"error": f"Failed to fetch agriculture market news: {str(e)}"}]


@tool
def get_weather_agriculture_news(country: str = "in", language: str = "en", max_articles: int = 3) -> List[Dict[str, Any]]:
    """
    Fetch latest weather-related agriculture news and alerts.
    
    Args:
        country: Country code (default: "in" for India)
        language: Language code (default: "en" for English)
        max_articles: Maximum number of articles to return (default: 3)
    
    Returns:
        List of news articles about weather impacts on agriculture
    """
    try:
        url = Config.GNEWS_URL

        params = {
            "q": "weather agriculture OR climate farming OR drought crops OR rainfall farming OR agricultural weather OR climate change agriculture OR monsoon farming",
            "lang": language,
            "country": country,
            "max": max_articles,
            "apikey": Config.GNEWS_API_KEY,
            "sortby": "publishedAt"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        articles = data.get("articles", [])
        
        formatted_articles = []
        for article in articles:
            formatted_article = {
                "title": article.get("title", "No title"),
                "description": article.get("description", "No description"),
                "source": article.get("source", {}).get("name", "Unknown source"),
                "url": article.get("url", ""),
                "published_at": article.get("publishedAt", "Unknown date"),
                "category": "Weather"
            }
            formatted_articles.append(formatted_article)
        
        return formatted_articles
        
    except requests.exceptions.RequestException as e:
        return [{"error": f"Failed to fetch weather news: Network error - {str(e)}"}]
    except Exception as e:
        return [{"error": f"Failed to fetch weather agriculture news: {str(e)}"}]
