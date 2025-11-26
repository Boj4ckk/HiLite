-- ============================================================================
-- HiLite Database Schema
-- Pipeline: Twitch Clips → Download → Edit → Multi-Platform Publish
-- ============================================================================

-- Table principale : tous les clips du pipeline
CREATE TABLE IF NOT EXISTS clips (
    -- Identifiants
    clip_id TEXT PRIMARY KEY,           -- ID unique Twitch
    broadcaster_id TEXT NOT NULL,       -- ID du streamer
    editor_id TEXT NOT NULL,            -- ID de l'éditeur du clip (pour whitelist)
    
    -- Métadonnées Twitch
    url TEXT NOT NULL,                  -- URL du clip Twitch
    embed_url TEXT,                     -- URL embed
    title TEXT NOT NULL,
    game_id TEXT,
    language TEXT,
    duration REAL NOT NULL,             -- Durée en secondes
    view_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,           -- ISO 8601 datetime
    thumbnail_url TEXT,
    
    -- Chemins des fichiers locaux
    downloaded_path TEXT,               -- Ex: data/downloaded_clips/123abc.mp4
    edited_path TEXT,                   -- Ex: data/edited_clips/123abc_edited.mp4
    
    -- États du pipeline
    status TEXT NOT NULL DEFAULT 'pending',  -- 'pending', 'downloaded', 'edited', 'published', 'failed'
    
    -- Compteurs de tentatives (max 3 par étape)
    download_attempts INTEGER DEFAULT 0,
    edit_attempts INTEGER DEFAULT 0,
    
    -- Timestamps
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    downloaded_at TIMESTAMP,
    edited_at TIMESTAMP,
    published_at TIMESTAMP,
    
    -- Logs d'erreurs
    error_log TEXT,
    
    -- Contraintes
    CHECK (status IN ('pending', 'downloaded', 'edited', 'published', 'failed')),
    CHECK (download_attempts >= 0 AND download_attempts <= 3),
    CHECK (edit_attempts >= 0 AND edit_attempts <= 3)
);

-- Index pour requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_clips_status ON clips(status);
CREATE INDEX IF NOT EXISTS idx_clips_editor_id ON clips(editor_id);
CREATE INDEX IF NOT EXISTS idx_clips_fetched_at ON clips(fetched_at DESC);


-- Table des publications (tracking multi-plateforme par worker)
CREATE TABLE IF NOT EXISTS publications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Identifiants
    clip_id TEXT NOT NULL,              -- Référence au clip
    worker_id TEXT NOT NULL,            -- Ex: 'worker_a', 'worker_b'
    platform TEXT NOT NULL,             -- 'youtube', 'tiktok', 'instagram'
    
    -- État de la publication
    post_status TEXT NOT NULL DEFAULT 'pending',  -- 'pending', 'success', 'failed'
    post_attempts INTEGER DEFAULT 0,
    
    -- Métadonnées de publication
    published_at TIMESTAMP,
    platform_video_id TEXT,             -- ID retourné par la plateforme (ex: YouTube video ID)
    platform_url TEXT,                  -- URL complète de la vidéo postée
    
    -- Statistiques (optionnel, à remplir plus tard)
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    
    -- Logs
    error_log TEXT,
    
    -- Contraintes
    FOREIGN KEY (clip_id) REFERENCES clips(clip_id) ON DELETE CASCADE,
    UNIQUE(clip_id, worker_id, platform),  -- Un worker ne peut poster qu'une fois par plateforme
    CHECK (platform IN ('youtube', 'tiktok', 'instagram')),
    CHECK (post_status IN ('pending', 'success', 'failed')),
    CHECK (post_attempts >= 0)
);

-- Index pour requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_publications_clip_id ON publications(clip_id);
CREATE INDEX IF NOT EXISTS idx_publications_worker_id ON publications(worker_id);
CREATE INDEX IF NOT EXISTS idx_publications_status ON publications(post_status);
CREATE INDEX IF NOT EXISTS idx_publications_published_at ON publications(published_at DESC);


-- Table whitelist des éditeurs autorisés
CREATE TABLE IF NOT EXISTS editor_whitelist (
    editor_id TEXT PRIMARY KEY,         -- ID Twitch de l'éditeur
    editor_name TEXT,                   -- Nom d'affichage (optionnel)
    is_active BOOLEAN DEFAULT 1,        -- Actif/Inactif
    notes TEXT,                         -- Notes libres
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour whitelist
CREATE INDEX IF NOT EXISTS idx_whitelist_active ON editor_whitelist(is_active);


-- Table des workers (configuration multi-compte)
CREATE TABLE IF NOT EXISTS workers (
    worker_id TEXT PRIMARY KEY,         -- Ex: 'worker_a'
    
    -- Comptes par plateforme (chemins vers fichiers credentials)
    youtube_credentials_path TEXT,      -- Ex: credentials/worker_a_youtube.json
    tiktok_credentials_path TEXT,
    instagram_credentials_path TEXT,
    
    -- Limites quotidiennes
    max_clips_per_day INTEGER DEFAULT 3,
    
    -- État
    is_active BOOLEAN DEFAULT 1,
    last_post_at TIMESTAMP,
    
    -- Métadonnées
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);


-- ============================================================================
-- Views utiles pour monitoring
-- ============================================================================

-- Vue : clips par statut (monitoring rapide)
CREATE VIEW IF NOT EXISTS v_clips_by_status AS
SELECT 
    status,
    COUNT(*) as count,
    COUNT(CASE WHEN downloaded_at >= datetime('now', '-24 hours') THEN 1 END) as last_24h
FROM clips
GROUP BY status;


-- Vue : publications par worker et plateforme
CREATE VIEW IF NOT EXISTS v_publications_summary AS
SELECT 
    worker_id,
    platform,
    COUNT(*) as total_posts,
    SUM(CASE WHEN post_status = 'success' THEN 1 ELSE 0 END) as successful,
    SUM(CASE WHEN post_status = 'failed' THEN 1 ELSE 0 END) as failed,
    MAX(published_at) as last_post
FROM publications
GROUP BY worker_id, platform;


-- Vue : clips prêts à être postés (pour les workers)
CREATE VIEW IF NOT EXISTS v_clips_ready_to_publish AS
SELECT 
    c.clip_id,
    c.title,
    c.edited_path,
    c.duration,
    c.view_count,
    COUNT(p.id) as already_posted_count
FROM clips c
LEFT JOIN publications p ON c.clip_id = p.clip_id AND p.post_status = 'success'
WHERE c.status = 'edited'
GROUP BY c.clip_id
HAVING already_posted_count < (SELECT COUNT(DISTINCT worker_id) FROM workers WHERE is_active = 1);
