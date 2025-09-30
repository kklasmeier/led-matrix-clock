# data/news_provider.py - RSS news provider for scrolling headlines

import time
import urllib.request
import subprocess
import xml.etree.ElementTree as ET
from urllib import request as urllib_request
from urllib import error as urllib_error
from typing import Dict, Any, List, Optional, Tuple
from html import unescape

# Try to import requests library for better compatibility
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

class NewsProvider:
    """Provides news headlines from RSS feeds for scrolling display"""
    
    def __init__(self):
        """Initialize news provider with conservative RSS sources"""
        # Store sources with friendly names for logging
        # Newsmax uses curl due to compatibility issues with Python requests
        # Placed first to avoid network contention issues
        self.rss_sources = [
#            ("Newsmax", "https://www.newsmax.com/rss/Newsfront/16/"),
            ("Fox News", "https://feeds.foxnews.com/foxnews/latest"),
            ("Breitbart", "https://feeds.feedburner.com/breitbart"),
#            ("Daily Wire", "https://www.dailywire.com/rss.xml"),
            ("NY Post", "https://nypost.com/news/feed/"),
            ("The Blaze", "https://www.theblaze.com/feeds/feed.rss"),
            ("Washington Examiner", "https://www.washingtonexaminer.com/feed")
        ]
        
        self.last_update = 0
        self.cached_headlines = []
        self.update_interval = 1800  # 30 minutes
        self.max_headlines = 200      # Limit number of headlines
        self.max_headline_length = 200  # Max characters per headline
        
    def fetch_rss_headlines(self, source_name: str, rss_url: str) -> Tuple[List[str], int]:
        """
        Fetch headlines from a single RSS feed
        
        Args:
            source_name: Friendly name of the source
            rss_url: URL of the RSS feed
            
        Returns:
            Tuple of (list of headline strings, count fetched)
        """
        headlines = []
        
        # Use curl for Newsmax, requests for others if available, urllib as fallback
        use_curl = 'newsmax' in rss_url.lower()
        use_requests = HAS_REQUESTS and not use_curl
        
        try:
            if use_curl:
                # Use curl subprocess for sites that block Python requests
                # Force HTTP/1.1 to avoid HTTP/2 connection issues
                result = subprocess.run(
                    ['curl', '-s', '--http1.1', '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', rss_url],
                    capture_output=True,
                    timeout=30,  # Newsmax needs longer timeout
                    text=False  # Get bytes, not string
                )
                
                if result.returncode != 0:
                    print(f"Curl failed for {source_name} with return code {result.returncode}")
                    return [], 0
                
                xml_data = result.stdout
                
            elif use_requests:
                # Use requests library for better compatibility
                response = requests.get(
                    rss_url,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    },
                    timeout=15
                )
                response.raise_for_status()
                xml_data = response.content
            else:
                # Use urllib for other feeds
                req = urllib.request.Request(
                    rss_url,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                )
                
                timeout = 15
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    xml_data = response.read()
            
            # Parse XML with error recovery
            try:
                # Try standard parsing first
                root = ET.fromstring(xml_data)
            except ET.ParseError as e:
                # If parsing fails, try with recover mode using iterparse
                from io import BytesIO
                try:
                    # Parse what we can, ignoring errors
                    parser = ET.XMLParser(encoding='utf-8')
                    root = ET.fromstring(xml_data, parser=parser)
                except:
                    print(f"Could not parse XML from {source_name} even with recovery: {e}")
                    return [], 0
            
            # Find all item elements (works for most RSS formats)
            items = root.findall('.//item')
            
            for item in items:
                # Get title
                title_elem = item.find('title')
                if title_elem is not None and title_elem.text:
                    # Clean up the title - handle CDATA and HTML entities
                    title = title_elem.text.strip()
                    
                    # Remove CDATA markers if present
                    if title.startswith('<![CDATA['):
                        title = title.replace('<![CDATA[', '').replace(']]>', '')
                    
                    # Unescape HTML entities
                    title = unescape(title.strip())
                    
                    # Truncate if too long
                    if len(title) > self.max_headline_length:
                        title = title[:self.max_headline_length-3] + "..."
                    
                    headlines.append(title)
                    
                    # Limit headlines per source
                    if len(headlines) >= 50:
                        break
            
            return headlines, len(headlines)
            
        except urllib_error.URLError as e:
            if hasattr(e, 'reason'):
                print(f"Error fetching RSS from {source_name}: {e.reason}")
            else:
                print(f"Error fetching RSS from {source_name}: {e}")
            return [], 0
        except Exception as e:
            print(f"Error fetching RSS from {source_name} ({rss_url}): {e}")
            return [], 0
    
    def fetch_all_headlines(self) -> List[str]:
        """
        Fetch headlines from all RSS sources with per-source logging
        
        Returns:
            Combined list of headlines from all sources
        """
        all_headlines = []
        source_counts = []
        
        print("Fetching news headlines from RSS sources...")
        
        for source_name, rss_url in self.rss_sources:
            headlines, count = self.fetch_rss_headlines(source_name, rss_url)
            
            if count > 0:
                all_headlines.extend(headlines)
                source_counts.append(f"{source_name}: {count}")
            else:
                source_counts.append(f"{source_name}: 0 (failed)")
            
            # Stop if we have enough headlines
            if len(all_headlines) >= self.max_headlines:
                break
        
        # Log summary
        total = len(all_headlines)
        print(f"News fetch complete: {total} total headlines")
        for source_info in source_counts:
            print(f"  - {source_info}")
        
        # Limit to max headlines
        return all_headlines[:self.max_headlines]
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get news data for display
        
        Returns:
            Dict containing list of headlines and metadata
        """
        current_time = time.time()
        
        # Update if cache is stale or empty
        if self.is_stale() or not self.cached_headlines:
            fresh_headlines = self.fetch_all_headlines()
            if fresh_headlines:
                self.cached_headlines = fresh_headlines
                self.last_update = current_time
            elif not self.cached_headlines:
                # If no cached data and fetch fails, return default
                self.cached_headlines = [
                    "Breaking news updates coming soon...",
                    "Stay tuned for the latest headlines",
                    "News feed temporarily unavailable"
                ]
                print("News fetch failed - using default headlines")
        
        return {
            "headlines": self.cached_headlines,
            "count": len(self.cached_headlines),
            "timestamp": self.last_update
        }
    
    def is_stale(self, max_age_seconds: Optional[int] = None) -> bool:
        """
        Check if cached data is older than update interval
        
        Args:
            max_age_seconds: Override default update interval
            
        Returns:
            bool: True if data needs refresh
        """
        max_age = max_age_seconds or self.update_interval
        return (time.time() - self.last_update) > max_age
    
    def force_update(self) -> None:
        """Force update of news data"""
        self.last_update = 0  # Reset to force update on next get_data call

# Global instance
_news_provider: Optional[NewsProvider] = None

def get_news_provider() -> NewsProvider:
    """Get or create the global NewsProvider instance"""
    global _news_provider
    if _news_provider is None:
        _news_provider = NewsProvider()
    return _news_provider