"""
Module d'analyse et calcul des métriques d'engagement
"""
from typing import List, Dict
from datetime import datetime, timedelta
import pandas as pd


def calculate_engagement_score(
    post: Dict,
    weights: Dict = None
) -> float:
    """
    Calcule le score d'engagement d'un post
    
    Formule par défaut:
    Score = (upvotes × 1.0) + (comments × 2.0) + (awards × 5.0) + (upvote_ratio × 10) - age_penalty
    
    Args:
        post: Dictionnaire contenant les données du post
        weights: Poids personnalisés (optionnel)
    
    Returns:
        Score d'engagement (float)
    """
    if weights is None:
        weights = {
            "upvotes": 1.0,
            "comments": 2.0,
            "awards": 5.0,
            "upvote_ratio": 10.0,
        }
    
    # Extraction des valeurs
    upvotes = post.get("score", 0)
    comments = post.get("num_comments", 0)
    awards = post.get("awards", 0)
    upvote_ratio = post.get("upvote_ratio", 0.5)
    age_hours = post.get("age_hours", 0)
    
    # Calcul de base
    base_score = (
        upvotes * weights["upvotes"] +
        comments * weights["comments"] +
        awards * weights["awards"] +
        upvote_ratio * weights["upvote_ratio"]
    )
    
    # Pénalité d'âge (les posts récents sont favorisés)
    # Bonus de 20% pour les posts < 24h, décroissance ensuite
    if age_hours < 24:
        age_factor = 1.2
    elif age_hours < 48:
        age_factor = 1.1
    elif age_hours < 72:
        age_factor = 1.0
    else:
        age_factor = 0.9 - (age_hours / 1000)  # Décroissance lente
    
    final_score = base_score * max(age_factor, 0.5)  # Minimum 50% du score
    
    return round(final_score, 2)


def enrich_posts_with_engagement(
    posts: List[Dict],
    weights: Dict = None
) -> List[Dict]:
    """
    Enrichit une liste de posts avec leur score d'engagement
    """
    for post in posts:
        post["engagement_score"] = calculate_engagement_score(post, weights)
    
    return posts


def rank_posts_by_engagement(
    posts: List[Dict],
    top_n: int = 20
) -> List[Dict]:
    """
    Trie les posts par score d'engagement (décroissant)
    """
    sorted_posts = sorted(
        posts,
        key=lambda x: x.get("engagement_score", 0),
        reverse=True
    )
    return sorted_posts[:top_n]


def get_trending_posts(
    posts: List[Dict],
    hours_threshold: int = 24,
    min_score: int = 100
) -> List[Dict]:
    """
    Identifie les posts "trending" (récents avec bon score)
    """
    trending = [
        post for post in posts
        if post.get("age_hours", 999) <= hours_threshold
        and post.get("score", 0) >= min_score
    ]
    
    return sorted(trending, key=lambda x: x.get("engagement_score", 0), reverse=True)


def analyze_by_subreddit(posts: List[Dict]) -> pd.DataFrame:
    """
    Analyse les posts par subreddit
    """
    if not posts:
        return pd.DataFrame()
    
    df = pd.DataFrame(posts)
    
    subreddit_stats = df.groupby("subreddit").agg({
        "post_id": "count",
        "score": "mean",
        "num_comments": "mean",
        "engagement_score": "mean"
    }).reset_index()
    
    subreddit_stats.columns = [
        "Subreddit",
        "Nombre de posts",
        "Score moyen",
        "Commentaires moyens",
        "Engagement moyen"
    ]
    
    subreddit_stats = subreddit_stats.sort_values("Engagement moyen", ascending=False)
    
    return subreddit_stats


def analyze_by_keyword(posts: List[Dict]) -> pd.DataFrame:
    """
    Analyse les posts par mot-clé
    """
    if not posts:
        return pd.DataFrame()
    
    df = pd.DataFrame(posts)
    
    keyword_stats = df.groupby("matched_keywords").agg({
        "post_id": "count",
        "score": "mean",
        "engagement_score": "mean"
    }).reset_index()
    
    keyword_stats.columns = [
        "Mot-clé",
        "Nombre de posts",
        "Score moyen",
        "Engagement moyen"
    ]
    
    keyword_stats = keyword_stats.sort_values("Engagement moyen", ascending=False)
    
    return keyword_stats


def get_time_series_data(posts: List[Dict], days: int = 7) -> pd.DataFrame:
    """
    Prépare les données pour une visualisation temporelle
    """
    if not posts:
        return pd.DataFrame()
    
    df = pd.DataFrame(posts)
    df["post_date"] = pd.to_datetime(df["post_date"])
    df["date"] = df["post_date"].dt.date
    
    daily_stats = df.groupby("date").agg({
        "post_id": "count",
        "score": "mean",
        "engagement_score": "mean"
    }).reset_index()
    
    daily_stats.columns = ["Date", "Nombre de posts", "Score moyen", "Engagement moyen"]
    
    return daily_stats


def calculate_growth_rate(
    current_posts: List[Dict],
    previous_posts: List[Dict]
) -> Dict:
    """
    Compare les performances actuelles vs période précédente
    """
    if not current_posts:
        return {"growth": 0, "status": "Pas de données"}
    
    current_count = len(current_posts)
    previous_count = len(previous_posts) if previous_posts else 0
    
    if previous_count == 0:
        growth_rate = 100.0
    else:
        growth_rate = ((current_count - previous_count) / previous_count) * 100
    
    current_engagement = sum(p.get("engagement_score", 0) for p in current_posts) / current_count
    previous_engagement = (
        sum(p.get("engagement_score", 0) for p in previous_posts) / previous_count
        if previous_count > 0 else 0
    )
    
    engagement_growth = (
        ((current_engagement - previous_engagement) / previous_engagement) * 100
        if previous_engagement > 0 else 0
    )
    
    return {
        "posts_current": current_count,
        "posts_previous": previous_count,
        "posts_growth": round(growth_rate, 1),
        "engagement_current": round(current_engagement, 2),
        "engagement_previous": round(previous_engagement, 2),
        "engagement_growth": round(engagement_growth, 1)
    }


def filter_posts_by_criteria(
    posts: List[Dict],
    min_score: int = 0,
    min_comments: int = 0,
    max_age_hours: int = 168,  # 7 jours par défaut
    exclude_nsfw: bool = True
) -> List[Dict]:
    """
    Filtre les posts selon des critères
    """
    filtered = posts
    
    if min_score > 0:
        filtered = [p for p in filtered if p.get("score", 0) >= min_score]
    
    if min_comments > 0:
        filtered = [p for p in filtered if p.get("num_comments", 0) >= min_comments]
    
    if max_age_hours:
        filtered = [p for p in filtered if p.get("age_hours", 999) <= max_age_hours]
    
    if exclude_nsfw:
        filtered = [p for p in filtered if not p.get("is_nsfw", False)]
    
    return filtered


def generate_summary_stats(posts: List[Dict]) -> Dict:
    """
    Génère des statistiques résumées
    """
    if not posts:
        return {
            "total_posts": 0,
            "avg_score": 0,
            "avg_comments": 0,
            "avg_engagement": 0,
            "top_subreddit": "N/A",
            "total_subreddits": 0
        }
    
    df = pd.DataFrame(posts)
    
    return {
        "total_posts": len(posts),
        "avg_score": round(df["score"].mean(), 1),
        "avg_comments": round(df["num_comments"].mean(), 1),
        "avg_engagement": round(df["engagement_score"].mean(), 2),
        "top_subreddit": df["subreddit"].value_counts().index[0],
        "total_subreddits": df["subreddit"].nunique(),
        "total_awards": df["awards"].sum()
    }
