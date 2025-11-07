"""
Configuration file for LinkedIn Auto-Posting Agent
"""
import os
from dotenv import load_dotenv

load_dotenv()

# LinkedIn credentials
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL", "")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")

# Optional: Free API keys (if available)
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")  # Get free key from newsapi.org
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")

# Free LLM API Keys (for AI post generation)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")  # Get free key from console.groq.com (Recommended!)
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")  # Get free key from together.ai
HF_API_KEY = os.getenv("HF_API_KEY", "")  # Hugging Face (fallback)

# Post generation settings
MAX_POST_LENGTH = 3000  # LinkedIn character limit
MIN_POST_LENGTH = 100
POSTING_DELAY = 5  # Seconds to wait between actions

# Browser automation settings
HEADLESS_MODE = os.getenv("HEADLESS_MODE", "False").lower() == "true"
BROWSER_TIMEOUT = 30  # Seconds

# Trending topics settings
TOPICS_TO_FETCH = 5  # Number of trending topics to fetch
TRENDING_SOURCES = ["reddit", "news", "rss"]  # Available sources

