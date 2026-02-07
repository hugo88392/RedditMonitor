"""
Reddit Monitor - Page d'accueil (VERSION SCRAPING)

⚠️ Cette version utilise du web scraping au lieu de l'API officielle Reddit
Application de collecte et analyse de posts Reddit
"""
import streamlit as st
from utils.database import get_stats, cleanup_old_posts
from utils.reddit_scraper import test_reddit_connection
from config.settings import RETENTION_DAYS

# Configuration de la page
st.set_page_config(
    page_title="Reddit Monitor",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #FF4500;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stat-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #FF4500;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #FF4500;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation de la session
if "user_id" not in st.session_state:
    st.session_state.user_id = "default"

# Header
st.markdown('<h1 class="main-header">📡 Reddit Monitor</h1>', unsafe_allow_html=True)
st.markdown("**Collecte et analyse automatisée de posts Reddit**")
st.divider()

# Sidebar - Sélection utilisateur
with st.sidebar:
    st.title("⚙️ Paramètres")
    
    # Sélection utilisateur
    user_options = ["default", "user1", "user2", "user3", "user4"]
    selected_user = st.selectbox(
        "👤 Profil utilisateur",
        user_options,
        index=user_options.index(st.session_state.user_id)
    )
    
    if selected_user != st.session_state.user_id:
        st.session_state.user_id = selected_user
        st.rerun()
    
    st.divider()
    
    # Test connexion Reddit
    st.subheader("🔗 Connexion Reddit")
    if st.button("Tester connexion", use_container_width=True):
        with st.spinner("Test en cours..."):
            if test_reddit_connection():
                st.success("✅ Connexion réussie!")
            else:
                st.error("❌ Échec de la connexion")
    
    st.divider()
    
    # Nettoyage automatique
    st.subheader("🧹 Maintenance")
    st.caption(f"Rétention: {RETENTION_DAYS} jours")
    if st.button("Nettoyer anciens posts", use_container_width=True):
        with st.spinner("Nettoyage en cours..."):
            if cleanup_old_posts(RETENTION_DAYS):
                st.success("✅ Nettoyage effectué!")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🚀 Démarrage rapide")
    
    st.markdown("""
    ### Comment utiliser Reddit Monitor ?
    
    1. **⚙️ Configuration** : Ajoutez vos mots-clés et subreddits à surveiller
    2. **🔍 Scanner** : Lancez manuellement la collecte de posts
    3. **📊 Résultats** : Consultez les posts triés par engagement
    4. **📈 Historique** : Analysez les tendances dans le temps
    
    ---
    
    ### 📌 Navigation
    
    Utilisez la **barre latérale** pour naviguer entre les pages :
    
    - **⚙️ Configuration** : Gérez vos paramètres de recherche
    - **🔍 Scanner** : Lancez la collecte de posts Reddit
    - **📊 Résultats** : Visualisez et filtrez les posts collectés
    - **📈 Historique** : Explorez l'évolution des données
    """)

with col2:
    st.header("📊 Statistiques")
    
    # Récupération des stats
    stats = get_stats(user_id=st.session_state.user_id, days=7)
    
    # Affichage des métriques
    st.markdown('<div class="stat-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-value">{stats["total_posts"]}</div>', unsafe_allow_html=True)
    st.markdown('<div class="stat-label">Posts (7 derniers jours)</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("")
    
    st.markdown('<div class="stat-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-value">{stats["avg_engagement"]:.1f}</div>', unsafe_allow_html=True)
    st.markdown('<div class="stat-label">Engagement moyen</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("")
    
    if stats["top_subreddits"]:
        st.subheader("🏆 Top Subreddits")
        for subreddit, count in list(stats["top_subreddits"].items())[:5]:
            st.metric(f"r/{subreddit}", f"{count} posts")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <small>
    Reddit Monitor v1.0 | Créé avec Streamlit & PRAW<br>
    Profil actif: <b>{}</b>
    </small>
</div>
""".format(st.session_state.user_id), unsafe_allow_html=True)

# Affichage d'avertissements si configuration manquante (VERSION SCRAPING - pas besoin de Reddit)
try:
    if "supabase" not in st.secrets:
        st.warning("⚠️ Configuration incomplète. Veuillez ajouter vos secrets Supabase dans `.streamlit/secrets.toml`")
except:
    st.error("❌ Fichier secrets.toml manquant. Voir la documentation.")
