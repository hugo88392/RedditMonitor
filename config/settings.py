"""
Configuration globale de l'application Reddit Monitor
"""

# Configuration Reddit API
REDDIT_USER_AGENT = "reddit-monitor:v1.0.0 (by /u/YourUsername)"

# Configuration scoring d'engagement
ENGAGEMENT_WEIGHTS = {
    "upvotes": 1.0,
    "comments": 2.0,
    "awards": 5.0,
    "upvote_ratio": 10.0,
}

# Configuration analyse
MAX_POSTS_PER_SCAN = 1000  # Limite par mot-clé
POST_AGE_DAYS = 7  # Posts de moins de X jours
RETENTION_DAYS = 30  # Garder l'historique X jours

# Configuration Reddit rate limiting
REQUESTS_PER_MINUTE = 60
SLEEP_BETWEEN_REQUESTS = 1  # secondes

# Configuration Telegram (optionnel)
TELEGRAM_ENABLED = False

# Configuration dashboard
POSTS_PER_PAGE = 50
DEFAULT_TIME_RANGE = 7  # jours
