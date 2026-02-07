"""
Module de gestion de la base de données Supabase
"""
import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Optional


def get_supabase_client() -> Client:
    """
    Initialise et retourne le client Supabase
    """
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)


def init_database():
    """
    Initialise les tables de la base de données si elles n'existent pas
    
    Tables créées:
    - keywords: Liste des mots-clés à surveiller
    - subreddits: Liste des subreddits (whitelist/blacklist)
    - posts: Posts Reddit collectés
    - user_configs: Configuration par utilisateur
    """
    client = get_supabase_client()
    
    # Note: Les tables doivent être créées manuellement dans Supabase
    # Voir le fichier SQL fourni: database_schema.sql
    return True


def add_keyword(keyword: str, user_id: str = "default") -> bool:
    """
    Ajoute un mot-clé à surveiller
    """
    try:
        client = get_supabase_client()
        data = {
            "keyword": keyword.lower().strip(),
            "user_id": user_id,
            "active": True,
            "created_at": datetime.now().isoformat()
        }
        client.table("keywords").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Erreur lors de l'ajout du mot-clé: {e}")
        return False


def get_keywords(user_id: str = "default", active_only: bool = True) -> List[str]:
    """
    Récupère la liste des mots-clés
    """
    try:
        client = get_supabase_client()
        query = client.table("keywords").select("keyword").eq("user_id", user_id)
        
        if active_only:
            query = query.eq("active", True)
        
        response = query.execute()
        return [item["keyword"] for item in response.data]
    except Exception as e:
        st.error(f"Erreur lors de la récupération des mots-clés: {e}")
        return []


def delete_keyword(keyword: str, user_id: str = "default") -> bool:
    """
    Supprime un mot-clé
    """
    try:
        client = get_supabase_client()
        client.table("keywords").delete().eq("keyword", keyword).eq("user_id", user_id).execute()
        return True
    except Exception as e:
        st.error(f"Erreur lors de la suppression: {e}")
        return False


def add_subreddit(subreddit: str, list_type: str = "whitelist", user_id: str = "default") -> bool:
    """
    Ajoute un subreddit à la whitelist ou blacklist
    """
    try:
        client = get_supabase_client()
        data = {
            "subreddit": subreddit.lower().strip(),
            "list_type": list_type,
            "user_id": user_id,
            "active": True,
            "created_at": datetime.now().isoformat()
        }
        client.table("subreddits").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Erreur lors de l'ajout du subreddit: {e}")
        return False


def get_subreddits(list_type: str = "whitelist", user_id: str = "default") -> List[str]:
    """
    Récupère la liste des subreddits
    """
    try:
        client = get_supabase_client()
        response = (
            client.table("subreddits")
            .select("subreddit")
            .eq("user_id", user_id)
            .eq("list_type", list_type)
            .eq("active", True)
            .execute()
        )
        return [item["subreddit"] for item in response.data]
    except Exception as e:
        st.error(f"Erreur lors de la récupération des subreddits: {e}")
        return []


def delete_subreddit(subreddit: str, user_id: str = "default") -> bool:
    """
    Supprime un subreddit
    """
    try:
        client = get_supabase_client()
        client.table("subreddits").delete().eq("subreddit", subreddit).eq("user_id", user_id).execute()
        return True
    except Exception as e:
        st.error(f"Erreur lors de la suppression: {e}")
        return False


def save_posts(posts_data: List[Dict]) -> bool:
    """
    Sauvegarde les posts collectés dans la base de données
    """
    try:
        client = get_supabase_client()
        
        # Préparation des données
        for post in posts_data:
            post["created_at"] = datetime.now().isoformat()
        
        # Insertion par batch (éviter les doublons via post_id unique)
        client.table("posts").upsert(posts_data, on_conflict="post_id").execute()
        return True
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde des posts: {e}")
        return False


def get_posts(
    user_id: str = "default",
    days: int = 7,
    limit: int = 100,
    subreddit: Optional[str] = None,
    keyword: Optional[str] = None
) -> pd.DataFrame:
    """
    Récupère les posts de la base de données
    """
    try:
        client = get_supabase_client()
        
        # Date limite
        date_limit = (datetime.now() - timedelta(days=days)).isoformat()
        
        query = (
            client.table("posts")
            .select("*")
            .eq("user_id", user_id)
            .gte("post_date", date_limit)
            .order("engagement_score", desc=True)
            .limit(limit)
        )
        
        if subreddit:
            query = query.eq("subreddit", subreddit)
        
        if keyword:
            query = query.ilike("matched_keywords", f"%{keyword}%")
        
        response = query.execute()
        
        if response.data:
            return pd.DataFrame(response.data)
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Erreur lors de la récupération des posts: {e}")
        return pd.DataFrame()


def get_top_posts_weekly(user_id: str = "default", limit: int = 20) -> pd.DataFrame:
    """
    Récupère les top posts de la semaine
    """
    return get_posts(user_id=user_id, days=7, limit=limit)


def get_stats(user_id: str = "default", days: int = 7) -> Dict:
    """
    Récupère les statistiques globales
    """
    try:
        client = get_supabase_client()
        date_limit = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Nombre total de posts
        response = (
            client.table("posts")
            .select("*", count="exact")
            .eq("user_id", user_id)
            .gte("post_date", date_limit)
            .execute()
        )
        
        total_posts = response.count if response.count else 0
        
        # Subreddits les plus actifs
        posts_df = get_posts(user_id=user_id, days=days, limit=1000)
        
        if not posts_df.empty:
            top_subreddits = posts_df["subreddit"].value_counts().head(5).to_dict()
            avg_engagement = posts_df["engagement_score"].mean()
        else:
            top_subreddits = {}
            avg_engagement = 0
        
        return {
            "total_posts": total_posts,
            "top_subreddits": top_subreddits,
            "avg_engagement": avg_engagement,
            "period_days": days
        }
        
    except Exception as e:
        st.error(f"Erreur lors du calcul des stats: {e}")
        return {
            "total_posts": 0,
            "top_subreddits": {},
            "avg_engagement": 0,
            "period_days": days
        }


def cleanup_old_posts(days: int = 30) -> bool:
    """
    Supprime les posts plus vieux que X jours
    """
    try:
        client = get_supabase_client()
        date_limit = (datetime.now() - timedelta(days=days)).isoformat()
        
        client.table("posts").delete().lt("post_date", date_limit).execute()
        return True
    except Exception as e:
        st.error(f"Erreur lors du nettoyage: {e}")
        return False


def get_user_config(user_id: str = "default") -> Dict:
    """
    Récupère la configuration utilisateur
    """
    try:
        client = get_supabase_client()
        response = (
            client.table("user_configs")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )
        
        if response.data:
            return response.data[0]
        else:
            # Configuration par défaut
            return {
                "user_id": user_id,
                "engagement_weights": {
                    "upvotes": 1.0,
                    "comments": 2.0,
                    "awards": 5.0,
                    "upvote_ratio": 10.0
                },
                "telegram_chat_id": None
            }
    except Exception as e:
        st.error(f"Erreur lors de la récupération de la config: {e}")
        return {}


def update_user_config(user_id: str, config: Dict) -> bool:
    """
    Met à jour la configuration utilisateur
    """
    try:
        client = get_supabase_client()
        config["user_id"] = user_id
        config["updated_at"] = datetime.now().isoformat()
        
        client.table("user_configs").upsert(config, on_conflict="user_id").execute()
        return True
    except Exception as e:
        st.error(f"Erreur lors de la mise à jour: {e}")
        return False
