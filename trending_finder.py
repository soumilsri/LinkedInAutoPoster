"""
Module to find trending topics from free sources
"""
import requests
import feedparser
from typing import List, Dict
from datetime import datetime
import config


class TrendingFinder:
    """Finds trending topics from various free sources"""
    
    def __init__(self):
        self.sources = config.TRENDING_SOURCES
    
    def get_reddit_trending(self, limit: int = 5) -> List[Dict]:
        """Fetch trending topics from Reddit (free, no auth required for public data)"""
        topics = []
        try:
            # Using Reddit's public JSON API (no auth needed for reading)
            subreddits = ["technology", "programming", "business", "startups", "entrepreneur"]
            
            for subreddit in subreddits[:limit]:
                try:
                    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=3"
                    headers = {"User-Agent": "LinkedIn-AutoPoster/1.0"}
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        for post in data.get("data", {}).get("children", [])[:2]:
                            post_data = post.get("data", {})
                            topics.append({
                                "title": post_data.get("title", ""),
                                "url": post_data.get("url", ""),
                                "score": post_data.get("score", 0),
                                "subreddit": subreddit,
                                "source": "reddit",
                                "timestamp": datetime.now().isoformat()
                            })
                except Exception as e:
                    print(f"Error fetching from r/{subreddit}: {e}")
                    continue
        except Exception as e:
            print(f"Error fetching Reddit trends: {e}")
        
        return topics[:limit]
    
    def get_news_trending(self, limit: int = 5) -> List[Dict]:
        """Fetch trending tech/business news from NewsAPI (free tier available)"""
        topics = []
        try:
            if config.NEWSAPI_KEY:
                url = "https://newsapi.org/v2/top-headlines"
                params = {
                    "category": "technology",
                    "language": "en",
                    "pageSize": limit,
                    "apiKey": config.NEWSAPI_KEY
                }
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    for article in data.get("articles", []):
                        topics.append({
                            "title": article.get("title", ""),
                            "url": article.get("url", ""),
                            "description": article.get("description", ""),
                            "source": "newsapi",
                            "timestamp": datetime.now().isoformat()
                        })
            else:
                # Fallback to RSS feeds if no API key
                return self.get_rss_trending(limit)
        except Exception as e:
            print(f"Error fetching news trends: {e}")
        
        return topics[:limit]
    
    def get_rss_trending(self, limit: int = 5) -> List[Dict]:
        """Fetch trending topics from RSS feeds (completely free)"""
        topics = []
        rss_feeds = [
            "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
            "https://feeds.feedburner.com/oreilly/radar",
            "https://techcrunch.com/feed/"
        ]
        
        try:
            for feed_url in rss_feeds[:limit]:
                try:
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:2]:
                        topics.append({
                            "title": entry.get("title", ""),
                            "url": entry.get("link", ""),
                            "description": entry.get("description", ""),
                            "source": "rss",
                            "timestamp": datetime.now().isoformat()
                        })
                except Exception as e:
                    print(f"Error parsing RSS feed {feed_url}: {e}")
                    continue
        except Exception as e:
            print(f"Error fetching RSS trends: {e}")
        
        return topics[:limit]
    
    def get_trending_topics(self, limit: int = None) -> List[Dict]:
        """Get trending topics from all available sources"""
        if limit is None:
            limit = config.TOPICS_TO_FETCH
        
        all_topics = []
        
        if "reddit" in self.sources:
            all_topics.extend(self.get_reddit_trending(limit))
        
        if "news" in self.sources:
            all_topics.extend(self.get_news_trending(limit))
        
        if "rss" in self.sources or not all_topics:
            all_topics.extend(self.get_rss_trending(limit))
        
        # Remove duplicates and sort by relevance
        unique_topics = []
        seen_titles = set()
        for topic in all_topics:
            title_lower = topic["title"].lower()
            if title_lower not in seen_titles and len(title_lower) > 10:
                seen_titles.add(title_lower)
                unique_topics.append(topic)
        
        return unique_topics[:limit]

