# ⚡ Guide de démarrage rapide - Reddit Monitor

## 🎯 Setup en 10 minutes

### Étape 1 : Reddit API (3 min)

1. Va sur https://www.reddit.com/prefs/apps
2. Clique **"Create App"**
3. Remplis :
   - Name : `Reddit Monitor`
   - Type : **script**
   - Redirect URI : `http://localhost:8501`
4. Note ton `client_id` et `client_secret`

### Étape 2 : Supabase (4 min)

1. Crée un compte sur https://supabase.com
2. **New project** → attends 2 min
3. **SQL Editor** → colle le contenu de `database_schema.sql` → **Run**
4. **Settings > API** → note l'URL et la clé `anon public`

### Étape 3 : Configuration (2 min)

Crée `.streamlit/secrets.toml` :

```toml
[reddit]
client_id = "TON_CLIENT_ID_ICI"
client_secret = "TON_SECRET_ICI"

[supabase]
url = "https://ton-projet.supabase.co"
key = "TA_CLE_ANON_ICI"
```

### Étape 4 : Lancement (1 min)

```bash
pip install -r requirements.txt
streamlit run app.py
```

✅ **C'est prêt !** L'app s'ouvre dans ton navigateur.

---

## 🚀 Premier scan

1. **Configuration** → Ajoute des mots-clés (ex: `crypto`, `AI`, `python`)
2. **Scanner** → Clique **"LANCER LE SCAN"**
3. **Résultats** → Explore les posts !

---

## ☁️ Déployer sur Streamlit Cloud (5 min)

1. Pousse ton code sur GitHub
2. Va sur https://share.streamlit.io
3. **New app** → sélectionne ton repo
4. **Advanced settings** → colle le contenu de `secrets.toml`
5. **Deploy!**

📌 **Partage le lien** avec tes amis !

---

## 💡 Astuces

- Lance 1-2 scans par jour
- Utilise une whitelist de 5-10 subreddits
- Ajuste le scoring selon tes besoins
- Exporte en CSV pour analyse externe

---

**Besoin d'aide ?** Consulte le [README.md](README.md) complet.
