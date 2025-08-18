"""
Multilingual support service for Krishi Sahayak AI
Handles language detection, translation, and localized responses.
"""

import json
from typing import Dict, Optional, List
from pathlib import Path


class LanguageService:
    """Service to handle multilingual support for the AI assistant."""
    
    def __init__(self):
        self.supported_languages = {
            "en": "English",
            "hi": "हिंदी (Hindi)",
            "pa": "ਪੰਜਾਬੀ (Punjabi)",
            "bn": "বাংলা (Bengali)",
            "gu": "ગુજરાતી (Gujarati)",
            "mr": "मराठी (Marathi)",
            "ta": "தமிழ் (Tamil)",
            "te": "తెలుగు (Telugu)",
            "kn": "ಕನ್ನಡ (Kannada)",
            "ml": "മലയാളം (Malayalam)",
            "or": "ଓଡ଼ିଆ (Odia)",
            "as": "অসমীয়া (Assamese)"
        }
        
        # Language-specific farming terms and greetings
        self.language_templates = {
            "en": {
                "greeting": "Hello! I'm Krishi Sahayak AI, your agricultural assistant.",
                "error": "Sorry, I'm experiencing technical difficulties. Please try again later.",
                "weather_intro": "Here's the weather information for your location:",
                "market_intro": "Here are the current market prices:",
                "soil_intro": "Based on your soil analysis:",
                "farewell": "Thank you for using Krishi Sahayak AI. Happy farming!"
            },
            "hi": {
                "greeting": "नमस्ते! मैं कृषि सहायक AI हूं, आपका कृषि सहायक।",
                "error": "क्षमा करें, मुझे तकनीकी समस्या का सामना करना पड़ रहा है। कृपया बाद में पुनः प्रयास करें।",
                "weather_intro": "आपके स्थान की मौसम जानकारी:",
                "market_intro": "वर्तमान बाज़ार की कीमतें:",
                "soil_intro": "आपके मिट्टी विश्लेषण के आधार पर:",
                "farewell": "कृषि सहायक AI का उपयोग करने के लिए धन्यवाद। खुशहाल खेती!"
            },
            "pa": {
                "greeting": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਕ੍ਰਿਸ਼ੀ ਸਹਾਇਕ AI ਹਾਂ, ਤੁਹਾਡਾ ਖੇਤੀਬਾੜੀ ਸਹਾਇਕ।",
                "error": "ਮਾਫ਼ ਕਰਨਾ, ਮੈਨੂੰ ਤਕਨੀਕੀ ਸਮੱਸਿਆ ਦਾ ਸਾਮ੍ਹਣਾ ਕਰਨਾ ਪੈ ਰਿਹਾ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਬਾਅਦ ਵਿੱਚ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
                "weather_intro": "ਤੁਹਾਡੇ ਸਥਾਨ ਦੀ ਮੌਸਮ ਜਾਣਕਾਰੀ:",
                "market_intro": "ਮੌਜੂਦਾ ਮੰਡੀ ਦੇ ਭਾਅ:",
                "soil_intro": "ਤੁਹਾਡੇ ਮਿੱਟੀ ਵਿਸ਼ਲੇਸ਼ਣ ਦੇ ਆਧਾਰ 'ਤੇ:",
                "farewell": "ਕ੍ਰਿਸ਼ੀ ਸਹਾਇਕ AI ਦੀ ਵਰਤੋਂ ਕਰਨ ਲਈ ਧੰਨਵਾਦ। ਖੁਸ਼ਹਾਲ ਖੇਤੀ!"
            },
            "bn": {
                "greeting": "নমস্কার! আমি কৃষি সহায়ক AI, আপনার কৃষি সহায়ক।",
                "error": "দুঃখিত, আমি প্রযুক্তিগত সমস্যার সম্মুখীন হচ্ছি। অনুগ্রহ করে পরে আবার চেষ্টা করুন।",
                "weather_intro": "আপনার এলাকার আবহাওয়ার তথ্য:",
                "market_intro": "বর্তমান বাজারের দাম:",
                "soil_intro": "আপনার মাটি বিশ্লেষণের ভিত্তিতে:",
                "farewell": "কৃষি সহায়ক AI ব্যবহার করার জন্য ধন্যবাদ। সুখী চাষাবাদ!"
            }
        }
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages."""
        return self.supported_languages
    
    def is_language_supported(self, language_code: str) -> bool:
        """Check if a language is supported."""
        return language_code.lower() in self.supported_languages
    
    def get_language_name(self, language_code: str) -> str:
        """Get the full language name from language code."""
        return self.supported_languages.get(language_code.lower(), "English")
    
    def detect_language(self, text: str) -> str:
        """
        Detect language from input text.
        This is a simple implementation - in production, you might want to use
        a more sophisticated language detection library.
        """
        # Simple keyword-based detection
        hindi_indicators = ['क', 'ख', 'ग', 'घ', 'च', 'छ', 'ज', 'झ', 'नमस्ते', 'धन्यवाद', 'कृपया']
        punjabi_indicators = ['ਅ', 'ਆ', 'ਇ', 'ਈ', 'ਉ', 'ਊ', 'ਸਤ ਸ੍ਰੀ ਅਕਾਲ', 'ਧੰਨਵਾਦ']
        bengali_indicators = ['অ', 'আ', 'ই', 'ঈ', 'উ', 'ঊ', 'নমস্কার', 'ধন্যবাদ']
        
        text_lower = text.lower()
        
        # Check for script-specific characters
        for char in text:
            if any(indicator in char for indicator in hindi_indicators):
                return "hi"
            elif any(indicator in char for indicator in punjabi_indicators):
                return "pa"
            elif any(indicator in char for indicator in bengali_indicators):
                return "bn"
        
        # Default to English if no specific script detected
        return "en"
    
    def get_template(self, language_code: str, template_key: str) -> str:
        """Get a localized template string."""
        if language_code not in self.language_templates:
            language_code = "en"  # Fallback to English
        
        templates = self.language_templates[language_code]
        return templates.get(template_key, self.language_templates["en"].get(template_key, ""))
    
    def format_response_with_language(self, content: str, language_code: str, context_type: str = None) -> str:
        """
        Format response with appropriate language-specific formatting.
        """
        if not self.is_language_supported(language_code):
            language_code = "en"
        
        # Add context-specific intro if provided
        if context_type:
            intro = self.get_template(language_code, f"{context_type}_intro")
            if intro:
                content = f"{intro}\n\n{content}"
        
        return content
    
    def build_system_prompt_with_language(self, language_code: str, farmer_context: Dict = None) -> str:
        """
        Build a simplified system prompt that instructs the AI to respond in the specified language.
        """
        language_name = self.supported_languages.get(language_code, "English")
        
        base_prompt = f"""
        You are Krishi Sahayak AI, an expert agricultural assistant for Indian farmers. 
        Always respond in {language_name} language (language code: {language_code}).

        Important instructions:
        1. Always use {language_name} for your responses
        2. Use appropriate agricultural terminology in {language_name}
        3. Be culturally sensitive and relevant to Indian farming practices
        4. Provide practical, actionable advice
        5. Use simple, clear language that farmers can easily understand

        Remember: Always respond in {language_name} language only.
        """
        
        return base_prompt
    
    def get_language_specific_keywords(self, language_code: str) -> Dict[str, List[str]]:
        """
        Get language-specific keywords for better context understanding.
        """
        keywords = {
            "en": {
                "weather": ["weather", "rain", "temperature", "humidity", "forecast"],
                "crops": ["crop", "plant", "seed", "harvest", "yield"],
                "market": ["price", "market", "sell", "buy", "cost"],
                "soil": ["soil", "fertilizer", "nutrients", "pH", "organic"],
                "pests": ["pest", "insect", "disease", "fungus", "spray"]
            },
            "hi": {
                "weather": ["मौसम", "बारिश", "तापमान", "आर्द्रता", "पूर्वानुमान"],
                "crops": ["फसल", "पौधा", "बीज", "कटाई", "उत्पादन"],
                "market": ["कीमत", "बाज़ार", "बेचना", "खरीदना", "लागत"],
                "soil": ["मिट्टी", "खाद", "पोषक तत्व", "pH", "जैविक"],
                "pests": ["कीट", "कीड़े", "रोग", "फफूंद", "छिड़काव"]
            },
            "pa": {
                "weather": ["ਮੌਸਮ", "ਮੀਂਹ", "ਤਾਪਮਾਨ", "ਨਮੀ", "ਪੂਰਵ ਅਨੁਮਾਨ"],
                "crops": ["ਫਸਲ", "ਪੌਧਾ", "ਬੀਜ", "ਵਾਢੀ", "ਪੈਦਾਵਾਰ"],
                "market": ["ਕੀਮਤ", "ਮੰਡੀ", "ਵੇਚਣਾ", "ਖਰੀਦਣਾ", "ਲਾਗਤ"],
                "soil": ["ਮਿੱਟੀ", "ਖਾਦ", "ਪੋਸ਼ਕ ਤੱਤ", "pH", "ਜੈਵਿਕ"],
                "pests": ["ਕੀੜੇ", "ਕੀਟ", "ਰੋਗ", "ਉੱਲੀ", "ਛਿੜਕਾਅ"]
            },
            "bn": {
                "weather": ["আবহাওয়া", "বৃষ্টি", "তাপমাত্রা", "আর্দ্রতা", "পূর্বাভাস"],
                "crops": ["ফসল", "গাছ", "বীজ", "ফসল কাটা", "ফলন"],
                "market": ["দাম", "বাজার", "বিক্রি", "কেনা", "খরচ"],
                "soil": ["মাটি", "সার", "পুষ্টি উপাদান", "pH", "জৈব"],
                "pests": ["পোকা", "কীট", "রোগ", "ছত্রাক", "স্প্রে"]
            }
        }
        
        return keywords.get(language_code, keywords["en"])

    def translate_to(self, text: str, language_code: str) -> str:
        """
        Translate text to specified language.
        For now, this is a simple implementation that returns the text as-is.
        In production, you would integrate with a translation service.
        """
        # For English or unsupported languages, return as-is
        if language_code.lower() in ["en", "english"] or not self.is_language_supported(language_code):
            return text
        
        # For now, return the text with a language indicator
        # In production, integrate with Google Translate API or similar
        language_name = self.get_language_name(language_code)
        return text  # Return original text for now


# Global instance
language_service = LanguageService()
