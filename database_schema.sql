-- =====================================================
-- SCHEMA SQL POUR REDDIT MONITOR (Supabase)
-- =====================================================
-- À exécuter dans l'éditeur SQL de Supabase
-- =====================================================

-- Table: keywords
-- Stocke les mots-clés à surveiller par utilisateur
CREATE TABLE IF NOT EXISTS keywords (
    id BIGSERIAL PRIMARY KEY,
    keyword TEXT NOT NULL,
    user_id TEXT NOT NULL DEFAULT 'default',
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(keyword, user_id)
);

-- Index pour recherche rapide
CREATE INDEX IF NOT EXISTS idx_keywords_user ON keywords(user_id, active);
CREATE INDEX IF NOT EXISTS idx_keywords_keyword ON keywords(keyword);

-- =====================================================

-- Table: subreddits
-- Stocke les subreddits (whitelist/blacklist)
CREATE TABLE IF NOT EXISTS subreddits (
    id BIGSERIAL PRIMARY KEY,
    subreddit TEXT NOT NULL,
    list_type TEXT NOT NULL CHECK (list_type IN ('whitelist', 'blacklist')),
    user_id TEXT NOT NULL DEFAULT 'default',
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(subreddit, user_id, list_type)
);

-- Index
CREATE INDEX IF NOT EXISTS idx_subreddits_user ON subreddits(user_id, list_type, active);

-- =====================================================

-- Table: posts
-- Stocke les posts Reddit collectés
CREATE TABLE IF NOT EXISTS posts (
    id BIGSERIAL PRIMARY KEY,
    post_id TEXT NOT NULL UNIQUE,  -- ID Reddit du post
    user_id TEXT NOT NULL DEFAULT 'default',
    title TEXT NOT NULL,
    content TEXT,
    author TEXT,
    subreddit TEXT NOT NULL,
    url TEXT NOT NULL,
    post_date TIMESTAMPTZ NOT NULL,
    score INTEGER DEFAULT 0,
    upvote_ratio DECIMAL(3,2) DEFAULT 0.5,
    num_comments INTEGER DEFAULT 0,
    awards INTEGER DEFAULT 0,
    is_nsfw BOOLEAN DEFAULT FALSE,
    matched_keywords TEXT,  -- Mots-clés qui ont matché (CSV)
    age_hours DECIMAL(10,2),
    engagement_score DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour performances
CREATE INDEX IF NOT EXISTS idx_posts_user ON posts(user_id);
CREATE INDEX IF NOT EXISTS idx_posts_date ON posts(post_date DESC);
CREATE INDEX IF NOT EXISTS idx_posts_engagement ON posts(engagement_score DESC);
CREATE INDEX IF NOT EXISTS idx_posts_subreddit ON posts(subreddit);
CREATE INDEX IF NOT EXISTS idx_posts_post_id ON posts(post_id);

-- Index pour recherche full-text
CREATE INDEX IF NOT EXISTS idx_posts_title ON posts USING gin(to_tsvector('english', title));

-- =====================================================

-- Table: user_configs
-- Stocke la configuration par utilisateur
CREATE TABLE IF NOT EXISTS user_configs (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE,
    engagement_weights JSONB DEFAULT '{
        "upvotes": 1.0,
        "comments": 2.0,
        "awards": 5.0,
        "upvote_ratio": 10.0
    }'::jsonb,
    telegram_chat_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_user_configs_user ON user_configs(user_id);

-- =====================================================

-- Function: Mise à jour automatique du updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour user_configs
DROP TRIGGER IF EXISTS update_user_configs_updated_at ON user_configs;
CREATE TRIGGER update_user_configs_updated_at
    BEFORE UPDATE ON user_configs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================

-- Vues utiles pour statistiques

-- Vue: Stats par subreddit
CREATE OR REPLACE VIEW v_subreddit_stats AS
SELECT 
    user_id,
    subreddit,
    COUNT(*) as total_posts,
    AVG(score) as avg_score,
    AVG(num_comments) as avg_comments,
    AVG(engagement_score) as avg_engagement,
    MAX(post_date) as last_post_date
FROM posts
GROUP BY user_id, subreddit
ORDER BY avg_engagement DESC;

-- Vue: Stats par mot-clé
CREATE OR REPLACE VIEW v_keyword_stats AS
SELECT 
    user_id,
    matched_keywords,
    COUNT(*) as total_posts,
    AVG(score) as avg_score,
    AVG(engagement_score) as avg_engagement
FROM posts
WHERE matched_keywords IS NOT NULL
GROUP BY user_id, matched_keywords
ORDER BY avg_engagement DESC;

-- =====================================================

-- Données de test (optionnel)
-- Décommentez pour insérer des exemples

/*
-- Utilisateur par défaut
INSERT INTO user_configs (user_id) 
VALUES ('default')
ON CONFLICT (user_id) DO NOTHING;

-- Quelques mots-clés exemples
INSERT INTO keywords (keyword, user_id) VALUES 
    ('crypto', 'default'),
    ('ai', 'default'),
    ('python', 'default')
ON CONFLICT DO NOTHING;

-- Quelques subreddits exemples
INSERT INTO subreddits (subreddit, list_type, user_id) VALUES 
    ('python', 'whitelist', 'default'),
    ('learnprogramming', 'whitelist', 'default'),
    ('cryptocurrency', 'whitelist', 'default')
ON CONFLICT DO NOTHING;
*/

-- =====================================================
-- FIN DU SCHEMA
-- =====================================================

-- Vérification des tables créées
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE'
ORDER BY table_name;
