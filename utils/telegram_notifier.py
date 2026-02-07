"""
Module de notifications Telegram (optionnel)
"""
import streamlit as st
from telegram import Bot
from telegram.error import TelegramError
from typing import List, Dict
import asyncio


def get_telegram_bot():
    """
    Initialise le bot Telegram
    """
    try:
        token = st.secrets.get("telegram", {}).get("bot_token")
        if token:
            return Bot(token=token)
        return None
    except Exception as e:
        st.warning(f"Bot Telegram non configuré: {e}")
        return None


async def send_message_async(chat_id: str, message: str):
    """
    Envoie un message Telegram (async)
    """
    bot = get_telegram_bot()
    if not bot:
        return False
    
    try:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
        return True
    except TelegramError as e:
        st.error(f"Erreur Telegram: {e}")
        return False


def send_message(chat_id: str, message: str) -> bool:
    """
    Envoie un message Telegram (sync wrapper)
    """
    try:
        asyncio.run(send_message_async(chat_id, message))
        return True
    except Exception as e:
        st.error(f"Erreur lors de l'envoi: {e}")
        return False


def format_post_notification(post: Dict) -> str:
    """
    Formate un post pour notification Telegram
    """
    message = f"""
🔥 <b>Nouveau post détecté</b>

📝 <b>Titre:</b> {post['title'][:100]}...
👤 <b>Auteur:</b> u/{post['author']}
🏠 <b>Subreddit:</b> r/{post['subreddit']}
⬆️ <b>Score:</b> {post['score']} | 💬 <b>Commentaires:</b> {post['num_comments']}
📊 <b>Engagement:</b> {post['engagement_score']}

🔗 <a href="{post['url']}">Voir le post</a>
"""
    return message


def format_weekly_report(posts: List[Dict], stats: Dict) -> str:
    """
    Formate un rapport hebdomadaire pour Telegram
    """
    top_posts = sorted(posts, key=lambda x: x.get("engagement_score", 0), reverse=True)[:5]
    
    message = f"""
📊 <b>Rapport Hebdomadaire Reddit Monitor</b>

📈 <b>Statistiques:</b>
• Posts trouvés: {stats['total_posts']}
• Score moyen: {stats['avg_score']}
• Engagement moyen: {stats['avg_engagement']}
• Subreddits actifs: {stats['total_subreddits']}

🏆 <b>Top 5 Posts:</b>

"""
    
    for i, post in enumerate(top_posts, 1):
        message += f"{i}. <b>{post['title'][:50]}...</b>\n"
        message += f"   r/{post['subreddit']} • Score: {post['score']} • <a href=\"{post['url']}\">Lien</a>\n\n"
    
    return message


def send_weekly_report(chat_id: str, posts: List[Dict], stats: Dict) -> bool:
    """
    Envoie le rapport hebdomadaire
    """
    message = format_weekly_report(posts, stats)
    return send_message(chat_id, message)


def test_telegram_connection(chat_id: str) -> bool:
    """
    Test la connexion Telegram
    """
    test_message = "✅ Reddit Monitor : Connexion Telegram réussie!"
    return send_message(chat_id, test_message)
