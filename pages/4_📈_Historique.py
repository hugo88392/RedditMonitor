"""
Page Historique - Analyse des tendances dans le temps
"""
import streamlit as st
from utils.database import get_posts
from utils.analyzer import get_time_series_data, calculate_growth_rate
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Historique", page_icon="📈", layout="wide")

user_id = st.session_state.get("user_id", "default")

st.title("📈 Historique & Tendances")
st.markdown(f"**Profil actif:** `{user_id}`")
st.divider()

# Sélection de la période
col_p1, col_p2 = st.columns([1, 3])

with col_p1:
    period_days = st.selectbox(
        "📅 Période d'analyse",
        [7, 14, 30, 60, 90],
        index=2,  # 30 jours par défaut
        format_func=lambda x: f"{x} jours"
    )

with col_p2:
    st.info(f"📊 Analyse des posts des **{period_days} derniers jours**")

# Récupération des données
posts_df = get_posts(user_id=user_id, days=period_days, limit=5000)

if posts_df.empty:
    st.warning("⚠️ **Aucune donnée historique.** Lancez quelques scans pour commencer l'analyse.")
    st.stop()

# Conversion des dates
posts_df["post_date"] = pd.to_datetime(posts_df["post_date"])
posts_df["date"] = posts_df["post_date"].dt.date

st.divider()

# Statistiques globales
st.header("📊 Vue d'ensemble")

col_s1, col_s2, col_s3, col_s4 = st.columns(4)

with col_s1:
    st.metric("📝 Total posts", len(posts_df))

with col_s2:
    st.metric("📅 Jours actifs", posts_df["date"].nunique())

with col_s3:
    posts_per_day = len(posts_df) / posts_df["date"].nunique()
    st.metric("📊 Posts/jour moyen", f"{posts_per_day:.1f}")

with col_s4:
    st.metric("🏠 Subreddits uniques", posts_df["subreddit"].nunique())

st.divider()

# Comparaison avec période précédente
st.header("📈 Croissance")

# Calcul périodes (avec timezone UTC pour compatibilité)
from datetime import timezone
current_cutoff = datetime.now(timezone.utc) - timedelta(days=period_days // 2)
current_posts = posts_df[posts_df["post_date"] >= current_cutoff]
previous_posts = posts_df[posts_df["post_date"] < current_cutoff]

growth = calculate_growth_rate(
    current_posts.to_dict('records'),
    previous_posts.to_dict('records')
)

col_g1, col_g2, col_g3, col_g4 = st.columns(4)

with col_g1:
    st.metric(
        "📝 Posts (période actuelle)",
        growth["posts_current"],
        delta=f"{growth['posts_growth']:+.1f}%"
    )

with col_g2:
    st.metric(
        "📝 Posts (période précédente)",
        growth["posts_previous"]
    )

with col_g3:
    st.metric(
        "📊 Engagement actuel",
        f"{growth['engagement_current']:.1f}",
        delta=f"{growth['engagement_growth']:+.1f}%"
    )

with col_g4:
    st.metric(
        "📊 Engagement précédent",
        f"{growth['engagement_previous']:.1f}"
    )

st.divider()

# Graphiques temporels
st.header("📊 Évolution dans le temps")

# Agrégation par jour
daily_stats = posts_df.groupby("date").agg({
    "post_id": "count",
    "score": "mean",
    "num_comments": "mean",
    "engagement_score": "mean"
}).reset_index()

daily_stats.columns = ["Date", "Nombre de posts", "Score moyen", "Commentaires moyens", "Engagement moyen"]

# Graphique 1: Nombre de posts par jour
st.subheader("📅 Posts collectés par jour")

fig_posts = px.line(
    daily_stats,
    x="Date",
    y="Nombre de posts",
    markers=True,
    title="Évolution du nombre de posts"
)
fig_posts.update_traces(line_color="#FF4500", marker_color="#FF4500")
st.plotly_chart(fig_posts, use_container_width=True)

# Graphique 2: Engagement moyen par jour
st.subheader("📊 Engagement moyen par jour")

fig_engagement = px.line(
    daily_stats,
    x="Date",
    y="Engagement moyen",
    markers=True,
    title="Évolution de l'engagement"
)
fig_engagement.update_traces(line_color="#1E88E5", marker_color="#1E88E5")
st.plotly_chart(fig_engagement, use_container_width=True)

# Graphique 3: Score et commentaires
st.subheader("⬆️ Score & commentaires moyens")

fig_multi = go.Figure()

fig_multi.add_trace(go.Scatter(
    x=daily_stats["Date"],
    y=daily_stats["Score moyen"],
    mode='lines+markers',
    name='Score moyen',
    line=dict(color='#4CAF50')
))

fig_multi.add_trace(go.Scatter(
    x=daily_stats["Date"],
    y=daily_stats["Commentaires moyens"],
    mode='lines+markers',
    name='Commentaires moyens',
    line=dict(color='#FFC107'),
    yaxis='y2'
))

fig_multi.update_layout(
    title="Comparaison Score vs Commentaires",
    yaxis=dict(title="Score moyen"),
    yaxis2=dict(title="Commentaires moyens", overlaying='y', side='right')
)

st.plotly_chart(fig_multi, use_container_width=True)

st.divider()

# Analyse par subreddit dans le temps
st.header("🏠 Top subreddits dans le temps")

top_subreddits = posts_df["subreddit"].value_counts().head(5).index.tolist()

subreddit_time = posts_df[posts_df["subreddit"].isin(top_subreddits)].groupby(
    ["date", "subreddit"]
).size().reset_index(name="count")

fig_subreddit = px.line(
    subreddit_time,
    x="date",
    y="count",
    color="subreddit",
    markers=True,
    title=f"Évolution des {len(top_subreddits)} subreddits les plus actifs"
)

st.plotly_chart(fig_subreddit, use_container_width=True)

st.divider()

# Heatmap des posts par jour de la semaine et heure
st.header("🔥 Heatmap d'activité")

posts_df["day_of_week"] = posts_df["post_date"].dt.day_name()
posts_df["hour"] = posts_df["post_date"].dt.hour

# Mapping français des jours
day_mapping = {
    "Monday": "Lundi",
    "Tuesday": "Mardi",
    "Wednesday": "Mercredi",
    "Thursday": "Jeudi",
    "Friday": "Vendredi",
    "Saturday": "Samedi",
    "Sunday": "Dimanche"
}

posts_df["day_of_week_fr"] = posts_df["day_of_week"].map(day_mapping)

# Ordre des jours
day_order = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

heatmap_data = posts_df.groupby(["day_of_week_fr", "hour"]).size().reset_index(name="count")

# Pivot pour heatmap
heatmap_pivot = heatmap_data.pivot(index="day_of_week_fr", columns="hour", values="count").fillna(0)
heatmap_pivot = heatmap_pivot.reindex(day_order)

fig_heatmap = px.imshow(
    heatmap_pivot,
    labels=dict(x="Heure", y="Jour", color="Nombre de posts"),
    x=heatmap_pivot.columns,
    y=heatmap_pivot.index,
    color_continuous_scale="Reds",
    title="Distribution des posts par jour et heure"
)

st.plotly_chart(fig_heatmap, use_container_width=True)

st.divider()

# Distribution des scores
st.header("📊 Distribution des métriques")

col_d1, col_d2 = st.columns(2)

with col_d1:
    st.subheader("⬆️ Distribution des scores")
    fig_score_dist = px.histogram(
        posts_df,
        x="score",
        nbins=50,
        title="Répartition des scores"
    )
    st.plotly_chart(fig_score_dist, use_container_width=True)

with col_d2:
    st.subheader("📊 Distribution de l'engagement")
    fig_eng_dist = px.histogram(
        posts_df,
        x="engagement_score",
        nbins=50,
        title="Répartition de l'engagement"
    )
    st.plotly_chart(fig_eng_dist, use_container_width=True)

st.divider()

# Export des données temporelles
st.header("💾 Export des données")

csv_data = daily_stats.to_csv(index=False).encode('utf-8')

st.download_button(
    label="📥 Télécharger statistiques journalières (CSV)",
    data=csv_data,
    file_name=f"reddit_daily_stats_{user_id}_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv",
    use_container_width=True
)

# Footer
st.divider()
st.caption("📈 Les graphiques sont interactifs : survolez, zoomez, téléchargez-les en image.")
