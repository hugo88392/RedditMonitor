# 📡 Reddit Monitor

**Application de collecte et analyse automatisée de posts Reddit**

Outil Streamlit pour surveiller des mots-clés sur Reddit, analyser l'engagement des posts, et suivre les tendances dans le temps.

## 🎯 Fonctionnalités

- ✅ **Collecte manuelle** de posts Reddit par mots-clés
- 🔍 **Recherche ciblée** avec whitelist/blacklist de subreddits
- 📊 **Scoring d'engagement** personnalisable
- 📈 **Analyse de tendances** avec graphiques interactifs
- 💾 **Historique persistant** dans PostgreSQL (Supabase)
- 👥 **Multi-utilisateurs** (jusqu'à 4 profils)
- 🔗 **Liens cliquables** vers posts et subreddits
- 📥 **Export CSV** des résultats

---

## 🚀 Installation & Setup

### 1️⃣ Prérequis

- Python 3.9+
- Compte Reddit (pour créer l'app API)
- Compte Supabase (gratuit)
- Compte Streamlit Cloud (gratuit, optionnel pour le déploiement)

### 2️⃣ Cloner le projet

```bash
git clone https://github.com/VOTRE_USERNAME/reddit-monitor.git
cd reddit-monitor
```

### 3️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### 🔑 A. Créer l'application Reddit API

1. Allez sur [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. Cliquez sur **"Create App"** ou **"Create Another App"**
3. Remplissez le formulaire :
   - **Name** : `Reddit Monitor` (ou autre)
   - **App type** : Sélectionnez **"script"**
   - **Description** : `Mon app de monitoring Reddit`
   - **About URL** : Laissez vide
   - **Redirect URI** : `http://localhost:8501` (obligatoire même si non utilisé)
4. Cliquez sur **"Create app"**
5. **Notez vos credentials** :
   - `client_id` : sous le nom de l'app (chaine alphanumérique courte)
   - `client_secret` : à droite de "secret"

### 🗄️ B. Configurer Supabase (Base de données)

1. Créez un compte sur [https://supabase.com](https://supabase.com) (gratuit)
2. Créez un nouveau projet :
   - **Nom** : `reddit-monitor`
   - **Database Password** : choisissez un mot de passe fort
   - **Region** : Europe (ou proche de vous)
3. Attendez ~2 minutes que le projet se créé
4. Allez dans **SQL Editor** (menu de gauche)
5. Créez une **New Query** et collez le contenu du fichier `database_schema.sql`
6. Cliquez sur **"Run"** pour créer les tables
7. Récupérez vos credentials dans **Settings > API** :
   - `URL` : Project URL (ex: `https://abcdefgh.supabase.co`)
   - `anon public` key : Copiez la clé publique

### 🔐 C. Configurer les secrets

#### Pour utilisation locale :

1. Créez le fichier `.streamlit/secrets.toml` :

```bash
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

2. Éditez `.streamlit/secrets.toml` et remplissez vos credentials :

```toml
[reddit]
client_id = "VOTRE_CLIENT_ID"
client_secret = "VOTRE_CLIENT_SECRET"

[supabase]
url = "https://votre-projet.supabase.co"
key = "VOTRE_SUPABASE_ANON_KEY"

[telegram]
bot_token = ""  # Optionnel
```

3. **Important** : Ajoutez `.streamlit/secrets.toml` dans `.gitignore` :

```bash
echo ".streamlit/secrets.toml" >> .gitignore
```

---

## 🖥️ Lancement local

```bash
streamlit run app.py
```

L'application s'ouvre dans votre navigateur à `http://localhost:8501`

---

## ☁️ Déploiement sur Streamlit Cloud

### 1️⃣ Préparer le repository

1. Créez un repository GitHub
2. Poussez votre code :

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/VOTRE_USERNAME/reddit-monitor.git
git push -u origin main
```

### 2️⃣ Déployer sur Streamlit Cloud

1. Allez sur [https://share.streamlit.io](https://share.streamlit.io)
2. Connectez-vous avec GitHub
3. Cliquez sur **"New app"**
4. Sélectionnez :
   - **Repository** : `VOTRE_USERNAME/reddit-monitor`
   - **Branch** : `main`
   - **Main file path** : `app.py`
5. Cliquez sur **"Advanced settings"**
6. Dans **"Secrets"**, collez le contenu de votre fichier `secrets.toml` :

```toml
[reddit]
client_id = "VOTRE_CLIENT_ID"
client_secret = "VOTRE_CLIENT_SECRET"

[supabase]
url = "https://votre-projet.supabase.co"
key = "VOTRE_SUPABASE_ANON_KEY"
```

7. Cliquez sur **"Deploy!"**
8. Attendez ~5 minutes que l'app démarre
9. **Votre URL publique** : `https://VOTRE_APP.streamlit.app`

### 3️⃣ Partager avec vos amis

Envoyez-leur simplement le lien de l'app !

---

## 📖 Guide d'utilisation

### 1. Configuration (⚙️)

**Ajouter des mots-clés :**
- Allez dans **Configuration**
- Section "Mots-clés"
- Ajoutez vos mots-clés un par un ou en batch
- Exemple : `crypto`, `AI`, `python`, `marketing`

**Configurer les subreddits :**
- Section "Subreddits"
- **Whitelist** : Scanner uniquement ces subreddits (recommandé)
- **Blacklist** : Exclure certains subreddits
- Exemple whitelist : `python`, `learnprogramming`, `datascience`

**Ajuster le scoring :**
- Section "Scoring"
- Modifiez les poids selon vos priorités
- Plus le poids est élevé, plus la métrique compte dans le classement

### 2. Scanner (🔍)

**Lancer un scan :**
1. Allez dans **Scanner**
2. Configurez les paramètres :
   - **Période** : `week` pour posts récents
   - **Limite** : 100 posts par mot-clé
   - **Score minimum** : 0 (ou filtrez les posts peu populaires)
3. Cliquez sur **"LANCER LE SCAN"**
4. Attendez que le scan se termine (barre de progression)
5. Consultez le résumé et les top posts

**Fréquence recommandée :**
- 1 scan par jour minimum
- 2-3 scans par jour pour suivre l'actualité

### 3. Résultats (📊)

**Explorer les posts :**
- Utilisez les filtres : période, subreddit, tri
- Recherchez dans les titres
- Cliquez sur les titres pour accéder aux posts Reddit
- Exportez en CSV pour analyse externe

**Analyses disponibles :**
- Top posts par engagement
- Performance par subreddit
- Performance par mot-clé

### 4. Historique (📈)

**Analyser les tendances :**
- Graphiques d'évolution dans le temps
- Comparaison avec période précédente
- Heatmap d'activité (jours/heures)
- Distribution des scores

---

## 🎨 Personnalisation

### Changer le scoring d'engagement

Par défaut, le score est calculé ainsi :

```python
Score = (upvotes × 1.0) + 
        (comments × 2.0) + 
        (awards × 5.0) + 
        (upvote_ratio × 10.0) × 
        facteur_âge
```

Vous pouvez modifier les poids dans **Configuration > Scoring**.

### Ajouter de nouveaux profils utilisateurs

Dans le code (`app.py`), ligne ~45 :

```python
user_options = ["default", "user1", "user2", "user3", "user4"]
```

Ajoutez autant d'utilisateurs que nécessaire.

---

## 🔧 Maintenance

### Nettoyage automatique

Les posts plus vieux que 30 jours sont automatiquement supprimés (configurable dans `config/settings.py`).

Pour nettoyer manuellement :
- Page d'accueil > Sidebar > **"Nettoyer anciens posts"**

### Limites API Reddit

- **60 requêtes par minute** maximum
- Délai de 1 seconde entre requêtes appliqué automatiquement
- Si erreur "Rate limit", attendez quelques minutes

### Supabase gratuit

- **500 MB** de stockage
- Suffisant pour ~1-2 mois d'historique avec usage intensif
- Augmentez la période de rétention si besoin dans `config/settings.py`

---

## 🐛 Dépannage

### Erreur "Connection failed" (Reddit)

✅ **Vérifiez** :
- Client ID et secret corrects dans `secrets.toml`
- L'app Reddit est bien de type **"script"**
- Connexion internet stable

### Erreur "Supabase connection failed"

✅ **Vérifiez** :
- URL et clé Supabase correctes
- Le schéma SQL a bien été exécuté
- Le projet Supabase est actif

### Aucun post trouvé après scan

✅ **Causes possibles** :
- Mots-clés trop spécifiques
- Whitelist trop restrictive
- Période trop courte (essayez "month")
- Score minimum trop élevé

### App lente sur Streamlit Cloud

✅ **Solutions** :
- Limitez le nombre de posts par scan (max 100)
- Réduisez la période d'historique
- Nettoyez régulièrement les anciens posts

---

## 📚 Structure du projet

```
reddit-monitor/
├── app.py                      # Page d'accueil
├── pages/
│   ├── 1_⚙️_Configuration.py  # Config mots-clés, subreddits
│   ├── 2_🔍_Scanner.py        # Scan Reddit
│   ├── 3_📊_Résultats.py      # Visualisation posts
│   └── 4_📈_Historique.py     # Analyses temporelles
├── utils/
│   ├── database.py            # Gestion Supabase
│   ├── reddit_client.py       # API Reddit (PRAW)
│   ├── analyzer.py            # Calcul engagement
│   └── telegram_notifier.py   # Notifs (optionnel)
├── config/
│   └── settings.py            # Configuration globale
├── requirements.txt           # Dépendances Python
├── database_schema.sql        # Schéma SQL Supabase
└── README.md                  # Ce fichier
```

---

## 🔮 Améliorations futures

### Actuellement disponible

- ✅ Collecte manuelle
- ✅ Multi-utilisateurs
- ✅ Scoring personnalisable
- ✅ Historique & graphiques
- ✅ Export CSV

### Roadmap

- ⏳ Notifications Telegram automatiques
- ⏳ Scan automatique via GitHub Actions
- ⏳ Analyse de sentiment (NLP)
- ⏳ Détection de posts viraux en temps réel
- ⏳ Comparaison de comptes Reddit

---

## 🤝 Contribution

Les contributions sont les bienvenues !

1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

---

## 📄 Licence

Ce projet est sous licence MIT. Voir `LICENSE` pour plus de détails.

---

## 👤 Auteur

**Créé avec ❤️ par Nicolas**

- Développé avec Streamlit, PRAW, Supabase
- Hébergement : Streamlit Cloud (gratuit)

---

## ⭐ Support

Si ce projet vous aide, n'hésitez pas à mettre une étoile ⭐ sur GitHub !

Pour toute question : ouvrez une issue sur GitHub.

---

**Happy Reddit Monitoring! 🚀**
