"""
Page Scanner - Lancement de la collecte de posts Reddit (VERSION SCRAPING)

⚠️ ATTENTION : Cette version utilise du web scraping
- Scans plus lents (10-15 min pour 50 mots-clés)
- Limitez à 1-2 scans par jour maximum
- Risque de ban si usage excessif
"""
import streamlit as st
from utils.database import get_keywords, get_subreddits, save_posts, get_user_config
from utils.reddit_scraper import scan_keywords_batch, test_reddit_connection
from utils.analyzer import enrich_posts_with_engagement, generate_summary_stats
from datetime import datetime
import time

st.set_page_config(page_title="Scanner", page_icon="🔍", layout="wide")

user_id = st.session_state.get("user_id", "default")

st.title("🔍 Scanner Reddit")
st.markdown(f"**Profil actif:** `{user_id}`")
st.divider()

# Vérification de la configuration
keywords = get_keywords(user_id)
whitelist = get_subreddits("whitelist", user_id)
blacklist = get_subreddits("blacklist", user_id)
user_config = get_user_config(user_id)

# Affichage de la configuration
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🔑 Mots-clés configurés", len(keywords))

with col2:
    if whitelist:
        st.metric("✅ Subreddits en whitelist", len(whitelist))
    else:
        st.metric("🌐 Mode de recherche", "Tous les subreddits")

with col3:
    st.metric("🚫 Subreddits exclus", len(blacklist))

st.divider()

# Configuration du scan
st.header("⚙️ Paramètres du scan")

col_param1, col_param2 = st.columns(2)

with col_param1:
    time_filter = st.selectbox(
        "📅 Période de recherche",
        ["hour", "day", "week", "month", "year", "all"],
        index=2,  # "week" par défaut
        help="Filtre temporel pour limiter les posts"
    )
    
    exclude_nsfw = st.checkbox(
        "🔞 Exclure contenu NSFW",
        value=True,
        help="Exclure les posts marqués NSFW"
    )

with col_param2:
    limit_per_keyword = st.slider(
        "📊 Limite de posts par mot-clé",
        min_value=10,
        max_value=500,
        value=100,
        step=10,
        help="Nombre maximum de posts à récupérer pour chaque mot-clé"
    )
    
    min_score_filter = st.number_input(
        "⬆️ Score minimum",
        min_value=0,
        max_value=10000,
        value=0,
        step=10,
        help="Ignorer les posts avec un score inférieur"
    )

st.divider()

# Vérification avant scan
if not keywords:
    st.warning("⚠️ **Aucun mot-clé configuré.** Allez dans Configuration pour en ajouter.")
    st.stop()

# Affichage de la configuration de scan
with st.expander("📋 Récapitulatif de la configuration"):
    st.markdown(f"""
    **Mots-clés à scanner:** {len(keywords)}
    ```
    {', '.join(keywords)}
    ```
    
    **Subreddits:**
    - Whitelist: {len(whitelist) if whitelist else "Tous"}
    - Blacklist: {len(blacklist)}
    
    **Paramètres:**
    - Période: {time_filter}
    - Limite par mot-clé: {limit_per_keyword}
    - Score minimum: {min_score_filter}
    - Exclure NSFW: {exclude_nsfw}
    """)

# Bouton de lancement
st.divider()

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])

with col_btn2:
    scan_button = st.button(
        "🚀 LANCER LE SCAN",
        type="primary",
        use_container_width=True,
        help="Démarre la collecte de posts Reddit"
    )

# Processus de scan
if scan_button:
    st.divider()
    st.header("📡 Scan en cours...")
    
    # Conteneurs pour l'affichage
    progress_bar = st.progress(0)
    status_text = st.empty()
    stats_container = st.empty()
    
    # Timer
    start_time = time.time()
    
    # Callback pour mise à jour progression
    def update_progress(current, total, keyword):
        progress = int((current / total) * 100)
        progress_bar.progress(progress)
        status_text.markdown(f"**Scan en cours:** `{keyword}` ({current}/{total})")
    
    # Lancement du scan
    try:
        all_posts = scan_keywords_batch(
            keywords=keywords,
            subreddits=whitelist if whitelist else None,
            blacklist=blacklist,
            time_filter=time_filter,
            progress_callback=update_progress
        )
        
        # Filtrage NSFW
        if exclude_nsfw:
            all_posts = [p for p in all_posts if not p.get("is_nsfw", False)]
        
        # Filtrage score minimum
        if min_score_filter > 0:
            all_posts = [p for p in all_posts if p.get("score", 0) >= min_score_filter]
        
        # Calcul des scores d'engagement
        status_text.markdown("**Calcul des scores d'engagement...**")
        engagement_weights = user_config.get("engagement_weights", {
            "upvotes": 1.0,
            "comments": 2.0,
            "awards": 5.0,
            "upvote_ratio": 10.0
        })
        
        all_posts = enrich_posts_with_engagement(all_posts, engagement_weights)
        
        # Ajout du user_id
        for post in all_posts:
            post["user_id"] = user_id
        
        # Sauvegarde dans la base de données
        status_text.markdown("**Sauvegarde dans la base de données...**")
        
        if all_posts:
            success = save_posts(all_posts)
            
            if success:
                # Calcul du temps écoulé
                elapsed_time = time.time() - start_time
                
                # Statistiques
                stats = generate_summary_stats(all_posts)
                
                progress_bar.progress(100)
                
                st.success(f"✅ **Scan terminé avec succès!** ({elapsed_time:.1f}s)")
                
                # Affichage des résultats
                st.balloons()
                
                st.header("📊 Résultats du scan")
                
                col_r1, col_r2, col_r3, col_r4 = st.columns(4)
                
                with col_r1:
                    st.metric("📝 Posts collectés", stats["total_posts"])
                
                with col_r2:
                    st.metric("⬆️ Score moyen", f"{stats['avg_score']:.0f}")
                
                with col_r3:
                    st.metric("💬 Commentaires moyens", f"{stats['avg_comments']:.0f}")
                
                with col_r4:
                    st.metric("📊 Engagement moyen", f"{stats['avg_engagement']:.1f}")
                
                st.divider()
                
                # Top 10 posts
                st.subheader("🏆 Top 10 Posts")
                
                top_posts = sorted(all_posts, key=lambda x: x["engagement_score"], reverse=True)[:10]
                
                for i, post in enumerate(top_posts, 1):
                    with st.expander(f"#{i} - {post['title'][:80]}..."):
                        col_a, col_b = st.columns([2, 1])
                        
                        with col_a:
                            st.markdown(f"**Subreddit:** r/{post['subreddit']}")
                            st.markdown(f"**Auteur:** u/{post['author']}")
                            st.markdown(f"**Mot-clé:** {post['matched_keywords']}")
                            st.markdown(f"[🔗 Voir le post]({post['url']})")
                        
                        with col_b:
                            st.metric("⬆️ Score", post['score'])
                            st.metric("💬 Commentaires", post['num_comments'])
                            st.metric("📊 Engagement", f"{post['engagement_score']:.1f}")
                
                st.divider()
                
                st.info("💡 **Astuce:** Allez dans **Résultats** pour explorer tous les posts avec filtres et exports.")
                
            else:
                st.error("❌ Erreur lors de la sauvegarde des posts.")
        
        else:
            st.warning("⚠️ Aucun post trouvé avec ces critères. Essayez d'élargir la recherche.")
    
    except Exception as e:
        st.error(f"❌ **Erreur lors du scan:** {e}")
        st.exception(e)

# Guide d'utilisation
with st.expander("ℹ️ Comment optimiser vos scans ?"):
    st.markdown("""
    ### Conseils pour de meilleurs résultats :
    
    1. **Mots-clés spécifiques** : Utilisez des termes précis plutôt que génériques
    2. **Whitelist ciblée** : Limitez à quelques subreddits pertinents pour éviter le bruit
    3. **Période adaptée** : 
       - "day" ou "week" pour les sujets d'actualité
       - "month" ou "year" pour les sujets evergreen
    4. **Score minimum** : Filtrez les posts peu populaires (ex: 50+)
    5. **Lancez des scans réguliers** : 1-2 fois par jour pour suivre les tendances
    
    ### Limitations API Reddit :
    
    - Maximum **60 requêtes par minute**
    - Délai automatique entre requêtes appliqué
    - Si erreur "Rate limit", attendez quelques minutes
    """)

# Footer
st.divider()
st.caption("📡 Reddit Monitor | Scan manuel optimisé pour 4 utilisateurs")
