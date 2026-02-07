"""
Page Configuration - Gestion des mots-clés, subreddits et paramètres
"""
import streamlit as st
from utils.database import (
    add_keyword, get_keywords, delete_keyword,
    add_subreddit, get_subreddits, delete_subreddit,
    get_user_config, update_user_config
)

st.set_page_config(page_title="Configuration", page_icon="⚙️", layout="wide")

# User ID depuis session
user_id = st.session_state.get("user_id", "default")

st.title("⚙️ Configuration")
st.markdown(f"**Profil actif:** `{user_id}`")
st.divider()

# Tabs pour organisation
tab1, tab2, tab3 = st.tabs(["🔑 Mots-clés", "🏠 Subreddits", "📊 Scoring"])

# ============= TAB 1: MOTS-CLÉS =============
with tab1:
    st.header("🔑 Gestion des mots-clés")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Ajouter un mot-clé")
        
        new_keyword = st.text_input(
            "Nouveau mot-clé",
            placeholder="Ex: crypto, AI, marketing...",
            help="Le mot-clé sera converti en minuscules"
        )
        
        if st.button("➕ Ajouter", type="primary", use_container_width=True):
            if new_keyword:
                if add_keyword(new_keyword.strip(), user_id):
                    st.success(f"✅ Mot-clé '{new_keyword}' ajouté!")
                    st.rerun()
                else:
                    st.error("❌ Erreur lors de l'ajout")
            else:
                st.warning("⚠️ Veuillez saisir un mot-clé")
    
    with col2:
        st.subheader("Import batch")
        keywords_text = st.text_area(
            "Importer plusieurs mots-clés",
            placeholder="Un mot-clé par ligne",
            height=100
        )
        
        if st.button("📥 Importer tous", use_container_width=True):
            if keywords_text:
                keywords_list = [k.strip() for k in keywords_text.split("\n") if k.strip()]
                added = 0
                for kw in keywords_list:
                    if add_keyword(kw, user_id):
                        added += 1
                st.success(f"✅ {added}/{len(keywords_list)} mots-clés ajoutés!")
                st.rerun()
    
    st.divider()
    
    # Liste des mots-clés existants
    st.subheader("📋 Mots-clés actifs")
    keywords = get_keywords(user_id)
    
    if keywords:
        st.info(f"**{len(keywords)}** mots-clés configurés")
        
        # Affichage en colonnes
        cols = st.columns(4)
        for i, keyword in enumerate(keywords):
            with cols[i % 4]:
                with st.container():
                    st.markdown(f"**{keyword}**")
                    if st.button(f"🗑️ Supprimer", key=f"del_kw_{keyword}", use_container_width=True):
                        if delete_keyword(keyword, user_id):
                            st.success("Supprimé!")
                            st.rerun()
    else:
        st.warning("⚠️ Aucun mot-clé configuré. Ajoutez-en pour commencer!")

# ============= TAB 2: SUBREDDITS =============
with tab2:
    st.header("🏠 Gestion des Subreddits")
    
    # Choix whitelist ou blacklist
    list_mode = st.radio(
        "Mode de liste",
        ["whitelist", "blacklist"],
        horizontal=True,
        help="**Whitelist**: Scanner uniquement ces subreddits | **Blacklist**: Exclure ces subreddits"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"Ajouter à la {list_mode}")
        
        new_subreddit = st.text_input(
            "Nom du subreddit",
            placeholder="Ex: python, france, technology...",
            help="Sans le 'r/' devant"
        )
        
        if st.button("➕ Ajouter subreddit", type="primary", use_container_width=True):
            if new_subreddit:
                if add_subreddit(new_subreddit.strip(), list_mode, user_id):
                    st.success(f"✅ r/{new_subreddit} ajouté à la {list_mode}!")
                    st.rerun()
                else:
                    st.error("❌ Erreur lors de l'ajout")
            else:
                st.warning("⚠️ Veuillez saisir un subreddit")
    
    with col2:
        st.subheader("Import batch")
        subreddits_text = st.text_area(
            "Importer plusieurs subreddits",
            placeholder="Un subreddit par ligne",
            height=100,
            key="subreddit_batch"
        )
        
        if st.button("📥 Importer subreddits", use_container_width=True):
            if subreddits_text:
                subreddits_list = [s.strip() for s in subreddits_text.split("\n") if s.strip()]
                added = 0
                for sr in subreddits_list:
                    if add_subreddit(sr, list_mode, user_id):
                        added += 1
                st.success(f"✅ {added}/{len(subreddits_list)} subreddits ajoutés!")
                st.rerun()
    
    st.divider()
    
    # Affichage des listes
    col_w, col_b = st.columns(2)
    
    with col_w:
        st.subheader("✅ Whitelist")
        whitelist = get_subreddits("whitelist", user_id)
        
        if whitelist:
            st.info(f"**{len(whitelist)}** subreddits en whitelist")
            for subreddit in whitelist:
                col_sr, col_btn = st.columns([3, 1])
                with col_sr:
                    st.markdown(f"• r/{subreddit}")
                with col_btn:
                    if st.button("🗑️", key=f"del_w_{subreddit}"):
                        if delete_subreddit(subreddit, user_id):
                            st.rerun()
        else:
            st.caption("Aucun subreddit en whitelist (recherche globale)")
    
    with col_b:
        st.subheader("🚫 Blacklist")
        blacklist = get_subreddits("blacklist", user_id)
        
        if blacklist:
            st.info(f"**{len(blacklist)}** subreddits exclus")
            for subreddit in blacklist:
                col_sr, col_btn = st.columns([3, 1])
                with col_sr:
                    st.markdown(f"• r/{subreddit}")
                with col_btn:
                    if st.button("🗑️", key=f"del_b_{subreddit}"):
                        if delete_subreddit(subreddit, user_id):
                            st.rerun()
        else:
            st.caption("Aucun subreddit exclu")

# ============= TAB 3: SCORING =============
with tab3:
    st.header("📊 Configuration du Scoring d'Engagement")
    
    st.markdown("""
    ### Formule de calcul
    
    Le **score d'engagement** est calculé selon la formule :
    
    ```
    Score = (upvotes × poids_upvotes) + 
            (comments × poids_comments) + 
            (awards × poids_awards) + 
            (upvote_ratio × poids_ratio) × 
            facteur_âge
    ```
    """)
    
    # Récupération config actuelle
    config = get_user_config(user_id)
    current_weights = config.get("engagement_weights", {
        "upvotes": 1.0,
        "comments": 2.0,
        "awards": 5.0,
        "upvote_ratio": 10.0
    })
    
    st.subheader("⚖️ Poids des métriques")
    
    col1, col2 = st.columns(2)
    
    with col1:
        weight_upvotes = st.number_input(
            "⬆️ Poids Upvotes",
            min_value=0.0,
            max_value=10.0,
            value=current_weights.get("upvotes", 1.0),
            step=0.1,
            help="Importance des upvotes dans le score"
        )
        
        weight_comments = st.number_input(
            "💬 Poids Commentaires",
            min_value=0.0,
            max_value=10.0,
            value=current_weights.get("comments", 2.0),
            step=0.1,
            help="Importance du nombre de commentaires"
        )
    
    with col2:
        weight_awards = st.number_input(
            "🏆 Poids Awards",
            min_value=0.0,
            max_value=20.0,
            value=current_weights.get("awards", 5.0),
            step=0.5,
            help="Importance des récompenses"
        )
        
        weight_ratio = st.number_input(
            "📊 Poids Upvote Ratio",
            min_value=0.0,
            max_value=20.0,
            value=current_weights.get("upvote_ratio", 10.0),
            step=1.0,
            help="Importance du ratio upvote/downvote"
        )
    
    st.divider()
    
    # Exemple de calcul
    st.subheader("🧮 Exemple de calcul")
    
    example_post = {
        "upvotes": 1000,
        "comments": 150,
        "awards": 5,
        "upvote_ratio": 0.95
    }
    
    example_score = (
        example_post["upvotes"] * weight_upvotes +
        example_post["comments"] * weight_comments +
        example_post["awards"] * weight_awards +
        example_post["upvote_ratio"] * weight_ratio
    )
    
    st.markdown(f"""
    **Post exemple:**
    - Upvotes: {example_post['upvotes']}
    - Commentaires: {example_post['comments']}
    - Awards: {example_post['awards']}
    - Upvote ratio: {example_post['upvote_ratio']}
    
    **→ Score d'engagement: `{example_score:.1f}`**
    """)
    
    # Sauvegarde
    if st.button("💾 Sauvegarder configuration", type="primary", use_container_width=True):
        new_config = {
            "engagement_weights": {
                "upvotes": weight_upvotes,
                "comments": weight_comments,
                "awards": weight_awards,
                "upvote_ratio": weight_ratio
            }
        }
        
        if update_user_config(user_id, new_config):
            st.success("✅ Configuration sauvegardée!")
            st.balloons()
        else:
            st.error("❌ Erreur lors de la sauvegarde")

# Footer
st.divider()
st.caption("💡 **Astuce**: Ajustez les poids selon vos priorités. Poids élevé = plus d'importance dans le classement.")
