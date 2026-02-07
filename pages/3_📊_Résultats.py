"""
Page Résultats - Visualisation et filtrage des posts collectés
"""
import streamlit as st
from utils.database import get_posts, get_stats
from utils.analyzer import analyze_by_subreddit, analyze_by_keyword
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Résultats", page_icon="📊", layout="wide")

user_id = st.session_state.get("user_id", "default")

st.title("📊 Résultats des scans")
st.markdown(f"**Profil actif:** `{user_id}`")
st.divider()

# Paramètres de filtrage
st.header("🔍 Filtres")

col_f1, col_f2, col_f3, col_f4 = st.columns(4)

with col_f1:
    days_filter = st.selectbox(
        "📅 Période",
        [1, 3, 7, 14, 30],
        index=2,  # 7 jours par défaut
        format_func=lambda x: f"{x} jour{'s' if x > 1 else ''}"
    )

with col_f2:
    limit_posts = st.selectbox(
        "📊 Nombre de posts",
        [20, 50, 100, 200, 500],
        index=2  # 100 par défaut
    )

with col_f3:
    sort_by = st.selectbox(
        "🔽 Trier par",
        ["engagement_score", "score", "num_comments", "post_date"],
        format_func=lambda x: {
            "engagement_score": "Engagement",
            "score": "Score Reddit",
            "num_comments": "Commentaires",
            "post_date": "Date"
        }.get(x, x)
    )

with col_f4:
    # Liste dynamique des subreddits
    all_posts_temp = get_posts(user_id, days=30, limit=1000)
    
    if not all_posts_temp.empty:
        unique_subreddits = ["Tous"] + sorted(all_posts_temp["subreddit"].unique().tolist())
    else:
        unique_subreddits = ["Tous"]
    
    subreddit_filter = st.selectbox(
        "🏠 Subreddit",
        unique_subreddits
    )

# Récupération des données
subreddit_param = None if subreddit_filter == "Tous" else subreddit_filter
posts_df = get_posts(
    user_id=user_id,
    days=days_filter,
    limit=limit_posts,
    subreddit=subreddit_param
)

st.divider()

# Vérification des données
if posts_df.empty:
    st.warning("⚠️ **Aucun post trouvé.** Lancez un scan dans la section Scanner.")
    st.stop()

# Tri des données
posts_df = posts_df.sort_values(by=sort_by, ascending=False)

# Stats globales
st.header("📈 Statistiques globales")

col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)

with col_s1:
    st.metric("📝 Total posts", len(posts_df))

with col_s2:
    st.metric("⬆️ Score moyen", f"{posts_df['score'].mean():.0f}")

with col_s3:
    st.metric("💬 Commentaires moyens", f"{posts_df['num_comments'].mean():.0f}")

with col_s4:
    st.metric("📊 Engagement moyen", f"{posts_df['engagement_score'].mean():.1f}")

with col_s5:
    st.metric("🏠 Subreddits", posts_df["subreddit"].nunique())

st.divider()

# Tabs pour différentes vues
tab1, tab2, tab3 = st.tabs(["📋 Liste des posts", "📊 Analyse par subreddit", "🔑 Analyse par mot-clé"])

# ============= TAB 1: LISTE DES POSTS =============
with tab1:
    st.subheader(f"🏆 Top {len(posts_df)} posts")
    
    # Recherche textuelle
    search_query = st.text_input(
        "🔍 Rechercher dans les titres",
        placeholder="Ex: crypto, AI, marketing..."
    )
    
    # Filtrage par recherche
    if search_query:
        filtered_df = posts_df[posts_df["title"].str.contains(search_query, case=False, na=False)]
        st.caption(f"**{len(filtered_df)}** résultats pour '{search_query}'")
    else:
        filtered_df = posts_df
    
    # Affichage des posts
    for idx, post in filtered_df.iterrows():
        with st.container():
            col_a, col_b = st.columns([3, 1])
            
            with col_a:
                # Titre cliquable
                st.markdown(f"### [{post['title']}]({post['url']})")
                
                # Métadonnées
                st.markdown(
                    f"🏠 **r/{post['subreddit']}** · "
                    f"👤 u/{post['author']} · "
                    f"🔑 `{post['matched_keywords']}` · "
                    f"📅 {post['post_date'][:10]}"
                )
                
                # Contenu (aperçu)
                if post.get('content') and len(post['content']) > 0:
                    content_preview = post['content'][:200] + "..." if len(post['content']) > 200 else post['content']
                    with st.expander("📄 Aperçu du contenu"):
                        st.markdown(content_preview)
            
            with col_b:
                # Métriques
                st.metric("📊 Engagement", f"{post['engagement_score']:.1f}")
                st.metric("⬆️ Score", post['score'])
                st.metric("💬 Commentaires", post['num_comments'])
                
                # Ratio upvote (barre de progression)
                upvote_ratio = post.get('upvote_ratio', 0) * 100
                st.progress(post.get('upvote_ratio', 0))
                st.caption(f"👍 {upvote_ratio:.0f}% upvoted")
            
            st.divider()
    
    # Export CSV
    st.subheader("💾 Export des données")
    
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="📥 Télécharger en CSV",
        data=csv_data,
        file_name=f"reddit_posts_{user_id}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

# ============= TAB 2: ANALYSE PAR SUBREDDIT =============
with tab2:
    st.subheader("📊 Performance par subreddit")
    
    subreddit_stats = analyze_by_subreddit(posts_df.to_dict('records'))
    
    if not subreddit_stats.empty:
        # Affichage du tableau
        st.dataframe(
            subreddit_stats.style.format({
                "Score moyen": "{:.1f}",
                "Commentaires moyens": "{:.1f}",
                "Engagement moyen": "{:.2f}"
            }),
            use_container_width=True,
            hide_index=True
        )
        
        st.divider()
        
        # Graphiques
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown("#### 📊 Nombre de posts par subreddit")
            chart_data = subreddit_stats.set_index("Subreddit")["Nombre de posts"].head(10)
            st.bar_chart(chart_data)
        
        with col_g2:
            st.markdown("#### 🚀 Engagement moyen par subreddit")
            chart_engagement = subreddit_stats.set_index("Subreddit")["Engagement moyen"].head(10)
            st.bar_chart(chart_engagement)
    else:
        st.info("Pas assez de données pour l'analyse")

# ============= TAB 3: ANALYSE PAR MOT-CLÉ =============
with tab3:
    st.subheader("🔑 Performance par mot-clé")
    
    keyword_stats = analyze_by_keyword(posts_df.to_dict('records'))
    
    if not keyword_stats.empty:
        # Affichage du tableau
        st.dataframe(
            keyword_stats.style.format({
                "Score moyen": "{:.1f}",
                "Engagement moyen": "{:.2f}"
            }),
            use_container_width=True,
            hide_index=True
        )
        
        st.divider()
        
        # Graphiques
        col_k1, col_k2 = st.columns(2)
        
        with col_k1:
            st.markdown("#### 📈 Posts par mot-clé")
            chart_kw = keyword_stats.set_index("Mot-clé")["Nombre de posts"].head(10)
            st.bar_chart(chart_kw)
        
        with col_k2:
            st.markdown("#### 🎯 Engagement par mot-clé")
            chart_kw_eng = keyword_stats.set_index("Mot-clé")["Engagement moyen"].head(10)
            st.bar_chart(chart_kw_eng)
    else:
        st.info("Pas assez de données pour l'analyse")

# Footer
st.divider()
st.caption("💡 **Astuce**: Utilisez les filtres pour affiner votre recherche. Les données sont mises à jour après chaque scan.")
