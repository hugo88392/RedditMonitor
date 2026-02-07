"""
Module de scraping Reddit (alternative à l'API officielle)

⚠️ AVERTISSEMENT :
Ce module utilise du web scraping, ce qui viole techniquement les TOS de Reddit.
Utilisez à vos risques et périls, de façon responsable et modérée.

Recommandations :
- Maximum 1-2 scans par jour
- Délai de 10 secondes entre requêtes
- Ne pas utiliser à des fins commerciales
- Arrêter si vous recevez des warnings
"""

import requests
from bs4 import BeautifulSoup
import streamlit as st
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time
import random
import json
import re

# Liste de User-Agents réalistes pour rotation
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# Configuration du rate limiting
MIN_DELAY_BETWEEN_REQUESTS = 10  # secondes
MAX_DELAY_BETWEEN_REQUESTS = 15  # secondes


def get_random_user_agent() -> str:
    """Retourne un User-Agent aléatoire"""
    return random.choice(USER_AGENTS)


def get_headers() -> Dict:
    """Génère des headers HTTP réalistes"""
    return {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }


def safe_sleep():
    """Délai aléatoire pour éviter la détection"""
    delay = random.uniform(MIN_DELAY_BETWEEN_REQUESTS, MAX_DELAY_BETWEEN_REQUESTS)
    time.sleep(delay)


def parse_reddit_time(time_str: str) -> datetime:
    """Parse le format de temps Reddit (ex: "5 hours ago", "2 days ago")"""
    try:
        time_str = time_str.lower().strip()
        now = datetime.now()
        
        if 'just now' in time_str or 'now' in time_str:
            return now
        
        numbers = re.findall(r'\d+', time_str)
        if not numbers:
            return now
        
        value = int(numbers[0])
        
        if 'second' in time_str:
            return now - timedelta(seconds=value)
        elif 'minute' in time_str:
            return now - timedelta(minutes=value)
        elif 'hour' in time_str:
            return now - timedelta(hours=value)
        elif 'day' in time_str:
            return now - timedelta(days=value)
        elif 'week' in time_str:
            return now - timedelta(weeks=value)
        elif 'month' in time_str:
            return now - timedelta(days=value * 30)
        elif 'year' in time_str:
            return now - timedelta(days=value * 365)
        else:
            return now
            
    except Exception as e:
        return datetime.now()


def parse_score(score_str: str) -> int:
    """Parse le score (ex: "1.2k" -> 1200, "500" -> 500)"""
    try:
        score_str = score_str.lower().strip().replace('points', '').replace('point', '').strip()
        
        if 'k' in score_str:
            return int(float(score_str.replace('k', '')) * 1000)
        elif 'm' in score_str:
            return int(float(score_str.replace('m', '')) * 1000000)
        else:
            return int(float(re.sub(r'[^\d.]', '', score_str)))
    except:
        return 0


def scrape_reddit_search(
    keyword: str,
    time_filter: str = "week",
    limit: int = 50
) -> List[Dict]:
    """Scrape les résultats de recherche Reddit pour un mot-clé"""
    posts = []
    
    try:
        url = f"https://www.reddit.com/search.json"
        params = {
            'q': keyword,
            't': time_filter,
            'sort': 'relevance',
            'limit': min(limit, 100)
        }
        
        response = requests.get(
            url,
            params=params,
            headers=get_headers(),
            timeout=30
        )
        
        if response.status_code == 429:
            st.warning(f"⚠️ Rate limit atteint pour '{keyword}'. Pause de 60 secondes...")
            time.sleep(60)
            return []
        
        if response.status_code != 200:
            st.warning(f"⚠️ Erreur HTTP {response.status_code} pour '{keyword}'")
            return []
        
        # Parse JSON API
        data = response.json()
        
        if 'data' in data and 'children' in data['data']:
            for item in data['data']['children']:
                post_data = item.get('data', {})
                
                posts.append({
                    'post_id': post_data.get('id', ''),
                    'title': post_data.get('title', ''),
                    'content': post_data.get('selftext', ''),
                    'author': post_data.get('author', '[deleted]'),
                    'subreddit': post_data.get('subreddit', ''),
                    'url': f"https://www.reddit.com{post_data.get('permalink', '')}",
                    'post_date': datetime.fromtimestamp(post_data.get('created_utc', 0)).isoformat(),
                    'score': post_data.get('score', 0),
                    'upvote_ratio': post_data.get('upvote_ratio', 0.5),
                    'num_comments': post_data.get('num_comments', 0),
                    'awards': post_data.get('total_awards_received', 0),
                    'is_nsfw': post_data.get('over_18', False),
                    'matched_keywords': keyword,
                    'age_hours': (datetime.now() - datetime.fromtimestamp(post_data.get('created_utc', 0))).total_seconds() / 3600,
                    'engagement_score': 0
                })
        
        if not posts:
            st.warning(f"⚠️ Aucun post trouvé pour '{keyword}'")
        
    except requests.Timeout:
        st.error(f"❌ Timeout pour '{keyword}'")
    except Exception as e:
        st.error(f"❌ Erreur lors du scraping de '{keyword}': {e}")
    
    return posts


def scan_keywords_batch(
    keywords: List[str],
    subreddits: Optional[List[str]] = None,
    blacklist: Optional[List[str]] = None,
    time_filter: str = "week",
    progress_callback=None
) -> List[Dict]:
    """Scanne plusieurs mots-clés avec rate limiting strict"""
    all_posts = []
    total_keywords = len(keywords)
    
    st.warning("⏳ Scraping en cours... Cela peut prendre 10-15 minutes. Patience !")
    st.info("🛡️ Rate limiting actif : 10-15 secondes entre chaque requête pour éviter les bans.")
    
    for i, keyword in enumerate(keywords):
        if progress_callback:
            progress_callback(i, total_keywords, keyword)
        
        # Si whitelist de subreddits
        if subreddits:
            for subreddit in subreddits:
                search_query = f"{keyword} subreddit:{subreddit}"
                posts = scrape_reddit_search(search_query, time_filter, limit=25)
                all_posts.extend(posts)
                safe_sleep()
        else:
            posts = scrape_reddit_search(keyword, time_filter, limit=50)
            all_posts.extend(posts)
        
        if i < total_keywords - 1:
            safe_sleep()
    
    # Filtrer blacklist
    if blacklist:
        all_posts = [p for p in all_posts if p["subreddit"].lower() not in [b.lower() for b in blacklist]]
    
    # Dédupliquer
    seen_ids = set()
    unique_posts = []
    for post in all_posts:
        if post["post_id"] not in seen_ids:
            seen_ids.add(post["post_id"])
            unique_posts.append(post)
    
    if progress_callback:
        progress_callback(total_keywords, total_keywords, f"Terminé! {len(unique_posts)} posts uniques")
    
    return unique_posts


def test_reddit_connection() -> bool:
    """Test de connexion (version scraping)"""
    try:
        st.info("🧪 Test du scraper...")
        posts = scrape_reddit_search("test", "day", limit=5)
        
        if posts:
            st.success(f"✅ Scraping fonctionnel! {len(posts)} posts récupérés.")
            return True
        else:
            st.warning("⚠️ Aucun post trouvé lors du test.")
            return False
            
    except Exception as e:
        st.error(f"❌ Erreur test scraping: {e}")
        return False
