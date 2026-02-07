"""
Script de test de la configuration Reddit Monitor
Permet de vérifier que Reddit API et Supabase sont bien configurés
"""

import sys
import os

# Ajout du path pour imports locaux
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_reddit_api():
    """Test de la connexion à l'API Reddit"""
    print("🔍 Test de l'API Reddit...")
    
    try:
        import praw
        import streamlit as st
        
        # Chargement des secrets
        if not os.path.exists(".streamlit/secrets.toml"):
            print("❌ Fichier secrets.toml manquant")
            print("➡️ Créez le fichier .streamlit/secrets.toml avec vos credentials")
            return False
        
        # Import manuel des secrets (sans Streamlit)
        import toml
        secrets = toml.load(".streamlit/secrets.toml")
        
        reddit = praw.Reddit(
            client_id=secrets["reddit"]["client_id"],
            client_secret=secrets["reddit"]["client_secret"],
            user_agent="reddit-monitor:v1.0.0 (test)"
        )
        
        # Test simple
        subreddit = reddit.subreddit("test")
        for post in subreddit.hot(limit=1):
            print(f"✅ Connexion Reddit réussie!")
            print(f"   Test post: {post.title[:50]}...")
            return True
            
    except FileNotFoundError:
        print("❌ Module toml manquant")
        print("➡️ Installez avec: pip install toml")
        return False
    except Exception as e:
        print(f"❌ Erreur de connexion Reddit: {e}")
        print("➡️ Vérifiez vos credentials dans .streamlit/secrets.toml")
        return False

def test_supabase():
    """Test de la connexion à Supabase"""
    print("\n🔍 Test de Supabase...")
    
    try:
        from supabase import create_client
        import toml
        
        secrets = toml.load(".streamlit/secrets.toml")
        
        url = secrets["supabase"]["url"]
        key = secrets["supabase"]["key"]
        
        client = create_client(url, key)
        
        # Test simple : récupérer les tables
        response = client.table("keywords").select("*").limit(1).execute()
        
        print("✅ Connexion Supabase réussie!")
        print(f"   Database URL: {url}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion Supabase: {e}")
        print("➡️ Vérifiez:")
        print("   - L'URL et la clé dans secrets.toml")
        print("   - Le schéma SQL a été exécuté dans Supabase")
        return False

def test_dependencies():
    """Test des dépendances Python"""
    print("\n🔍 Test des dépendances...")
    
    required_packages = [
        "streamlit",
        "praw",
        "supabase",
        "pandas",
        "plotly"
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} manquant")
            missing.append(package)
    
    if missing:
        print(f"\n➡️ Installez les packages manquants:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True

def main():
    """Fonction principale"""
    print("=" * 50)
    print("🧪 TEST DE CONFIGURATION REDDIT MONITOR")
    print("=" * 50)
    
    # Test des dépendances
    deps_ok = test_dependencies()
    
    if not deps_ok:
        print("\n❌ Installation des dépendances requise")
        print("   Exécutez: pip install -r requirements.txt")
        return
    
    # Test Reddit
    reddit_ok = test_reddit_api()
    
    # Test Supabase
    supabase_ok = test_supabase()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    print(f"Dépendances: {'✅ OK' if deps_ok else '❌ Erreur'}")
    print(f"Reddit API:  {'✅ OK' if reddit_ok else '❌ Erreur'}")
    print(f"Supabase:    {'✅ OK' if supabase_ok else '❌ Erreur'}")
    
    if reddit_ok and supabase_ok:
        print("\n🎉 TOUT EST PRÊT!")
        print("   Lancez l'app avec: streamlit run app.py")
    else:
        print("\n⚠️ Configuration incomplète")
        print("   Consultez le README.md pour les instructions")

if __name__ == "__main__":
    main()
