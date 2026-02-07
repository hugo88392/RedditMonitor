# 📡 Reddit Monitor - VERSION SCRAPING

## ⚠️ AVERTISSEMENT IMPORTANT

**Cette version utilise du web scraping** au lieu de l'API officielle Reddit.

### Risques et limitations :

🔴 **Risques légaux** :
- Le scraping viole les Terms of Service de Reddit
- Risque de ban de compte ou d'IP (temporaire)
- Utilisez à vos propres risques

🟡 **Limitations techniques** :
- Scans **beaucoup plus lents** (10-15 min pour 50 mots-clés)
- Moins de posts par scan (~1000-2000 max vs 5000 avec API)
- Risque de captchas ou blocages

⚠️ **Précautions obligatoires** :
- **Maximum 1-2 scans par jour**
- Délai de 10-15 secondes entre requêtes (automatique)
- Usage personnel uniquement (pas commercial)
- Arrêtez immédiatement si Reddit vous bloque

---

## 🚀 Installation

### Prérequis

Cette version **NE nécessite PAS** de credentials Reddit API !

- Python 3.9+
- Compte Supabase (gratuit)
- Connexion internet stable

### Setup rapide

1. **Extraire l'archive**
```bash
unzip reddit-monitor-scraping.zip
cd reddit-monitor
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configurer Supabase**

Créez un compte sur https://supabase.com et :
- Nouveau projet
- Exécutez `database_schema.sql` dans SQL Editor
- Récupérez URL et clé dans Settings > API

4. **Créer `.streamlit/secrets.toml`**

```toml
[supabase]
url = "https://votre-projet.supabase.co"
key = "VOTRE_CLE_ANON"

# PLUS BESOIN DE CREDENTIALS REDDIT !
```

5. **Lancer l'app**
```bash
streamlit run app.py
```

---

## 📊 Différences avec la version API

| Feature | Version API | Version Scraping |
|---------|-------------|------------------|
| **Setup** | Nécessite app Reddit | ❌ Aucun setup Reddit |
| **Vitesse scan** | 2-5 minutes | ⚠️ 10-20 minutes |
| **Posts par scan** | ~5000 | ⚠️ ~1000-2000 |
| **Fréquence** | Plusieurs/jour | ⚠️ 1-2 max/jour |
| **Fiabilité** | 99% | ⚠️ 90-95% |
| **Légalité** | ✅ 100% légal | ⚠️ Zone grise |
| **Risque ban** | ❌ Aucun | ⚠️ Faible mais existant |

---

## 🛡️ Précautions d'usage

### Rate limiting automatique

Le code intègre des **délais automatiques** :
- 10-15 secondes entre chaque requête
- User-Agent rotation
- Gestion des erreurs 429 (rate limit)

### Fréquence recommandée

**Maximum par jour** :
- 1 scan avec 20-30 mots-clés
- OU 2 scans avec 10-15 mots-clés chacun

**Évitez** :
- Scans multiples rapprochés
- Plus de 50 mots-clés actifs
- Scans pendant les heures de pointe Reddit

### Si vous êtes bloqué

**Symptômes** :
- Erreur 429 (Rate Limit)
- Captchas répétés
- Timeouts

**Solutions** :
1. **Arrêtez immédiatement** de scanner
2. Attendez 1-24 heures
3. Réduisez le nombre de mots-clés
4. Espacez davantage vos scans

### Bonnes pratiques

✅ **À FAIRE** :
- Limiter à 20-30 mots-clés max
- 1 scan par jour
- Utiliser whitelist de subreddits
- Surveiller les logs d'erreurs

❌ **À ÉVITER** :
- Scans automatiques (cron)
- Usage commercial
- Partage/revente des données
- Scans pendant maintenance Reddit

---

## 🔧 Comment ça marche

### Méthode utilisée

L'app utilise **l'API JSON publique de Reddit** :

```python
url = "https://www.reddit.com/search.json"
params = {'q': keyword, 't': time_filter}
```

Cette méthode est :
- Plus fiable que le parsing HTML
- Moins détectable
- Mais toujours dans une zone grise légale

### Headers et protection

Le code utilise :
- User-Agents réalistes rotatifs
- Headers HTTP standards
- Délais aléatoires (10-15s)
- Gestion robuste des erreurs

---

## 📝 Configuration recommandée

### Pour usage optimal

**Mots-clés** :
- 15-20 mots-clés ciblés
- Spécifiques (pas trop génériques)

**Subreddits** :
- Whitelist de 5-10 subreddits pertinents
- Évite le bruit et accélère le scan

**Paramètres** :
- Période : "week" (compromis vitesse/résultats)
- Score minimum : 50+ (filtre le spam)

### Exemple config

```
Mots-clés (15) :
- crypto, bitcoin, ethereum
- AI, machine learning, chatgpt
- python, javascript, react
- SEO, marketing, content
- startup, entrepreneur, saas

Whitelist (8 subreddits) :
- cryptocurrency, bitcoin, ethereum
- artificial, machinelearning
- python, javascript
- SEO, Entrepreneur
```

**Temps de scan** : ~8-10 minutes
**Posts attendus** : ~800-1200

---

## 🐛 Dépannage

### Erreur 429 (Rate Limit)

```
⚠️ Rate limit atteint
```

**Solution** :
- L'app attend automatiquement 60 secondes
- Si répété : stoppez et attendez 1-24h

### Aucun post trouvé

```
⚠️ Aucun post trouvé pour 'keyword'
```

**Causes possibles** :
- Mot-clé trop spécifique
- Période trop courte (essayez "month")
- Reddit a changé son format JSON

**Solution** :
- Élargir la recherche
- Vérifier sur Reddit.com que le mot-clé donne des résultats

### Timeout

```
❌ Timeout pour 'keyword'
```

**Solution** :
- Connexion internet instable
- Relancez le scan
- Réduisez le nombre de mots-clés

---

## ⚖️ Aspects légaux (Important)

### Ce que dit Reddit

**Reddit Terms of Service (Section 5)** :

> "You may not access or search the Services by any means other than our publicly supported interfaces"

Le scraping viole techniquement ces termes.

### Risques réels

**Probabilité de conséquences** :

| Action | Probabilité | Conséquence |
|--------|-------------|-------------|
| Ban IP temporaire | 5-10% | Pause 1-24h |
| Ban compte Reddit | 1-2% | Compte bloqué |
| Poursuites légales | <0.01% | Très rare |

### Utilisation responsable

Pour **minimiser les risques** :
- Usage strictement personnel
- Pas de revente de données
- Respecter rate limits
- Arrêter si demandé

### Alternatives légales

Si vous voulez du 100% légal :
- RSS Feeds Reddit (limité à 25 posts)
- Services tiers payants (SocialData, Brand24)
- API officielle (si Reddit approuve votre demande)

---

## 💡 Recommandations finales

### Pour TON usage (4 amis)

**Configuration optimale** :
- Chaque utilisateur : 15-20 mots-clés max
- 1 scan par personne par jour
- Total : 4 scans/jour max sur l'app

**Résultat attendu** :
- ~800-1000 posts par scan
- ~3000-4000 posts/jour au total
- Risque très faible

### Si vous voulez jouer safe

**Option prudente** :
- 10 mots-clés par personne
- 1 scan tous les 2 jours
- Whitelist de 5 subreddits

**Résultat** :
- ~400-500 posts par scan
- Pratiquement aucun risque

---

## 🆘 Support

### En cas de problème

1. **Vérifiez les logs** dans Streamlit
2. **Consultez** les issues GitHub
3. **Testez** avec 1-2 mots-clés d'abord

### Évolution vers l'API

Si Reddit approuve votre demande d'API plus tard :
1. Réinstallez PRAW : `pip install praw`
2. Remplacez `reddit_scraper.py` par `reddit_client.py`
3. Ajoutez credentials dans `secrets.toml`

---

## 📚 Documentation complète

- **README.md** : Documentation générale
- **QUICKSTART.md** : Setup rapide
- **database_schema.sql** : Structure BDD

---

**Utilisez cette version de façon responsable ! 🙏**

*En cas de doute, préférez les RSS Feeds ou une solution payante légale.*
