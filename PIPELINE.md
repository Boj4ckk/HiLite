# ============================================================================
# HiLite - Pipeline de traitement des clips Twitch
# ============================================================================

## 📊 Architecture globale

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PIPELINE HILITE                              │
└─────────────────────────────────────────────────────────────────────┘

[1] WEBHOOK RECEIVER (Flask)
    ↓
    Reçoit stream.offline de Twitch EventSub
    ↓
    Attend 10 min (laisser Twitch traiter les clips)
    ↓
    Twitch API: GET /clips?broadcaster_id=X&started_at=Y&ended_at=Z
    ↓
    FILTRER en Python : si editor_id NOT IN whitelist → SKIP (ne touche pas la BDD)
    ↓
    INSERT INTO clips (clip_id, status='pending', ...) 
        - Si clip_id existe déjà (IntegrityError) → SKIP
   
        
[2] DOWNLOAD WORKER (download_worker.py - tourne en continu)
    ↓   
    SELECT * FROM clips 
    WHERE status = 'pending' 
    AND download_attempts < 3
    LIMIT 5
    ↓
    Pour chaque clip:
        ├─ Télécharger avec l'endpoint clips/downloads (brodcaster_id, editor_id, clip_id)        nécessite l'oauth du streamer.
        |
        ├─ Enregistrer dans data/downloaded_clips/
        ├─ UPDATE clips SET status='downloaded', downloaded_path=X
        └─ En cas d'erreur: download_attempts++
    
    
[3] EDIT WORKER (edit_worker.py - tourne en continu)
    ↓
    SELECT * FROM clips 
    WHERE status = 'downloaded' 
    AND edit_attempts < 3
    LIMIT 3
    ↓
    Pour chaque clip:
        ├─ Transcription ElevenLabs → SRT
        ├─ Overlay sous-titres avec MoviePy
        ├─ Enregistrer dans data/edited_clips/
        ├─ UPDATE clips SET status='edited', edited_path=X
        ├─ Supprimer downloaded_clips/ (économiser espace)
        └─ En cas d'erreur: edit_attempts++


[4] PUBLISH WORKER (publish_worker.py - cron quotidien 17h)
    ↓
    Arguments: python publish_worker.py worker_a
    ↓
    SELECT * FROM clips 
    WHERE status = 'edited'
    AND clip_id NOT IN (
        SELECT clip_id FROM publications 
        WHERE worker_id = 'worker_a' 
        AND post_status = 'success'
    )
    LIMIT 3  -- max_clips_per_day
    ↓
    Pour chaque clip:
        ├─ INSERT INTO publications (clip_id, worker_id, platform='youtube', post_status='pending')
        ├─ INSERT INTO publications (clip_id, worker_id, platform='tiktok', post_status='pending')
        ├─ INSERT INTO publications (clip_id, worker_id, platform='instagram', post_status='pending')
        │
        ├─ Upload YouTube → UPDATE publications SET post_status='success', platform_video_id=X
        ├─ Upload TikTok → UPDATE publications SET post_status='success'
        ├─ Upload Instagram → UPDATE publications SET post_status='success'
        │
        ├─ Si les 3 uploads réussissent:
        │   ├─ os.remove(edited_path)
        │   └─ UPDATE clips SET status='published'
        │
        └─ Si au moins 1 échec:
            ├─ Garder le fichier edited_clips/
            └─ Retry demain (post_status reste 'pending' ou 'failed')


[5] CLEANUP WORKER (cleanup_worker.py - cron hebdomadaire)
    ↓
    Supprimer les fichiers orphelins:
        - downloaded_clips/ > 7 jours ET status != 'pending'
        - edited_clips/ > 30 jours ET status = 'published'
    ↓
    Archiver les vieux clips en BDD (optionnel)
```

---

## 🗄️ Tables de la base de données

### **1. `clips` - Table principale**
Stocke tous les clips du pipeline avec leur état.

| Colonne | Type | Description |
|---------|------|-------------|
| `clip_id` | TEXT PK | ID unique Twitch |
| `broadcaster_id` | TEXT | ID du streamer |
| `editor_id` | TEXT | ID de l'éditeur (pour whitelist) |
| `url` | TEXT | URL du clip |
| `title` | TEXT | Titre du clip |
| `duration` | REAL | Durée en secondes |
| `view_count` | INTEGER | Nombre de vues |
| `created_at` | TEXT | Date création Twitch (ISO 8601) |
| `downloaded_path` | TEXT | Chemin fichier brut |
| `edited_path` | TEXT | Chemin fichier monté |
| **`status`** | TEXT | **'pending' → 'downloaded' → 'edited' → 'published'** |
| `download_attempts` | INTEGER | Compteur tentatives DL (max 3) |
| `edit_attempts` | INTEGER | Compteur tentatives montage (max 3) |
| `fetched_at` | TIMESTAMP | Quand le clip a été détecté |
| `downloaded_at` | TIMESTAMP | Quand téléchargé |
| `edited_at` | TIMESTAMP | Quand monté |
| `published_at` | TIMESTAMP | Quand publié |
| `error_log` | TEXT | Logs d'erreurs |

**Statuts possibles** :
- `pending` : Clip détecté, pas encore téléchargé
- `downloaded` : Fichier brut dans `downloaded_clips/`
- `edited` : Fichier monté dans `edited_clips/`, prêt à poster
- `published` : Posté sur les 3 plateformes, fichier supprimé
- `failed` : Échec après 3 tentatives

---

### **2. `publications` - Tracking multi-plateforme**
Une ligne par publication (1 clip × 1 worker × 1 plateforme).

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | INTEGER PK | Autoincrement |
| `clip_id` | TEXT FK | Référence à `clips.clip_id` |
| `worker_id` | TEXT | Ex: 'worker_a' |
| `platform` | TEXT | 'youtube', 'tiktok', 'instagram' |
| **`post_status`** | TEXT | **'pending', 'success', 'failed'** |
| `post_attempts` | INTEGER | Compteur tentatives post |
| `published_at` | TIMESTAMP | Date de publication |
| `platform_video_id` | TEXT | ID retourné par la plateforme |
| `platform_url` | TEXT | URL de la vidéo postée |
| `error_log` | TEXT | Logs d'erreurs |

**Contrainte UNIQUE** : `(clip_id, worker_id, platform)`
→ Impossible pour un worker de poster 2 fois sur la même plateforme.

**Exemple** :
```sql
-- Worker_a poste clip_123 sur 3 plateformes
clip_id='123', worker_id='worker_a', platform='youtube',   post_status='success'
clip_id='123', worker_id='worker_a', platform='tiktok',    post_status='success'
clip_id='123', worker_id='worker_a', platform='instagram', post_status='failed'

-- Worker_b peut poster le même clip_123
clip_id='123', worker_id='worker_b', platform='youtube',   post_status='success'
```

---

### **3. `editor_whitelist` - Filtrage des éditeurs**
Liste des éditeurs Twitch autorisés (optionnelle).

| Colonne | Type | Description |
|---------|------|-------------|
| `editor_id` | TEXT PK | ID Twitch de l'éditeur |
| `editor_name` | TEXT | Nom d'affichage |
| `is_active` | BOOLEAN | Actif/Inactif |
| `notes` | TEXT | Notes libres |
| `added_at` | TIMESTAMP | Date d'ajout |

**Usage** :
```python
# Au démarrage : charger en cache (1 fois)
whitelist = set(db.execute("SELECT editor_id FROM editor_whitelist WHERE is_active = 1"))

# Dans le webhook : filtrer AVANT d'insérer
if whitelist and editor_id not in whitelist:
    continue  # Ce clip n'ira jamais en BDD
```

**Avantages** :
- ✅ BDD `clips` contient **uniquement** les clips whitelisted
- ✅ Gestion centralisée (ajouter/retirer des éditeurs sans code)
- ✅ Historique et notes sur chaque éditeur
- ✅ Si table vide → mode "accepter tous les clips"

---

### **4. `workers` - Configuration multi-compte**
Liste des workers (bots) avec leurs credentials.

| Colonne | Type | Description |
|---------|------|-------------|
| `worker_id` | TEXT PK | Ex: 'worker_a' |
| `youtube_credentials_path` | TEXT | Chemin vers .json |
| `tiktok_credentials_path` | TEXT | Chemin vers .json |
| `instagram_credentials_path` | TEXT | Chemin vers .json |
| `max_clips_per_day` | INTEGER | Limite quotidienne (défaut: 3) |
| `is_active` | BOOLEAN | Actif/Inactif |
| `last_post_at` | TIMESTAMP | Dernière publication |

**Exemple** :
```sql
INSERT INTO workers VALUES 
('worker_a', 'credentials/worker_a_youtube.json', 'credentials/worker_a_tiktok.json', 'credentials/worker_a_instagram.json', 3, 1, NULL, NULL),
('worker_b', 'credentials/worker_b_youtube.json', 'credentials/worker_b_tiktok.json', 'credentials/worker_b_instagram.json', 3, 1, NULL, NULL);
```

---

## 🔄 Flux détaillé par worker

### **Webhook Handler (webhook_server.py)**
```python
# Au démarrage du serveur : charger la whitelist en cache
whitelist_cache = set(db.execute("SELECT editor_id FROM editor_whitelist WHERE is_active = 1").fetchall())

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    # Vérifier signature HMAC...
    
    # Attendre 10 min pour que Twitch traite les clips
    time.sleep(600)
    
    # Fetch clips du stream
    clips = twitch_api.get_clips(broadcaster_id, started_at, ended_at)
    
    for clip_data in clips:
        editor_id = clip_data['creator_id']
        
        # ✅ FILTRER AVANT d'insérer (ne pollue pas la BDD avec des clips non-WL)
        if whitelist_cache and editor_id not in whitelist_cache:
            continue  # Skip ce clip complètement
        
        try:
            db.execute("""
                INSERT INTO clips (clip_id, editor_id, url, title, duration, status, ...)
                VALUES (?, ?, ?, ?, ?, 'pending', ...)
            """, (clip_data['id'], editor_id, clip_data['url'], ...))
        except IntegrityError:
            # clip_id existe déjà → skip silencieusement
            pass
    
    return jsonify({'status': 'ok'})
```

**✅ Avantages** :
- Whitelist chargée **1 fois en mémoire** (ultra rapide)
- Seulement les clips WL entrent dans la BDD
- BDD plus propre, requêtes plus rapides
- Si `whitelist_cache` vide → tous les clips acceptés (mode sans filtre)

---

### **Worker 1 : Download (download_worker.py)**
```python
while True:
    clips = db.query("""
        SELECT clip_id, url FROM clips 
        WHERE status = 'pending' 
        AND download_attempts < 3
        LIMIT 5
    """)
    
    for clip in clips:
        try:
            path = selenium_download(clip.url)
            db.execute("UPDATE clips SET status='downloaded', downloaded_path=? WHERE clip_id=?", 
                      (path, clip.clip_id))
        except:
            db.execute("UPDATE clips SET download_attempts = download_attempts + 1 WHERE clip_id=?",
                      (clip.clip_id,))
    
    time.sleep(60)  # Check toutes les minutes
```

---

### **Worker 2 : Edit (edit_worker.py)**
```python
while True:
    clips = db.query("""
        SELECT clip_id, downloaded_path FROM clips 
        WHERE status = 'downloaded' 
        AND edit_attempts < 3
        LIMIT 3
    """)
    
    for clip in clips:
        try:
            edited_path = subtitle_video(clip.downloaded_path)
            db.execute("UPDATE clips SET status='edited', edited_path=? WHERE clip_id=?",
                      (edited_path, clip.clip_id))
            os.remove(clip.downloaded_path)  # Libérer espace
        except:
            db.execute("UPDATE clips SET edit_attempts = edit_attempts + 1 WHERE clip_id=?",
                      (clip.clip_id,))
    
    time.sleep(120)  # Check toutes les 2 minutes
```

---

### **Worker 3 : Publish (publish_worker.py)**
```python
# Lancé par cron: python publish_worker.py worker_a
worker_id = sys.argv[1]
max_clips = 3

clips = db.query("""
    SELECT c.clip_id, c.edited_path FROM clips c
    WHERE c.status = 'edited'
    AND c.clip_id NOT IN (
        SELECT clip_id FROM publications 
        WHERE worker_id = ? AND post_status = 'success'
    )
    LIMIT ?
""", (worker_id, max_clips))

for clip in clips:
    platforms = ['youtube', 'tiktok', 'instagram']
    success_count = 0
    
    for platform in platforms:
        try:
            video_id = upload_to_platform(platform, clip.edited_path)
            db.execute("""
                INSERT INTO publications (clip_id, worker_id, platform, post_status, platform_video_id)
                VALUES (?, ?, ?, 'success', ?)
            """, (clip.clip_id, worker_id, platform, video_id))
            success_count += 1
        except:
            db.execute("""
                INSERT INTO publications (clip_id, worker_id, platform, post_status, error_log)
                VALUES (?, ?, ?, 'failed', ?)
            """, (clip.clip_id, worker_id, platform, str(e)))
    
    # Si les 3 plateformes OK
    if success_count == 3:
        os.remove(clip.edited_path)
        db.execute("UPDATE clips SET status='published', published_at=CURRENT_TIMESTAMP WHERE clip_id=?",
                  (clip.clip_id,))
```

---

## 📅 Planification (Cron/Tâches)

```bash
# Flask webhook (toujours actif)
python webhook_server.py

# Workers en continu
python download_worker.py &
python edit_worker.py &

# Workers quotidiens (17h)
0 17 * * * python publish_worker.py worker_a
0 17 * * * python publish_worker.py worker_b
0 17 * * * python publish_worker.py worker_c

# Nettoyage hebdomadaire (dimanche 3h)
0 3 * * 0 python cleanup_worker.py
```

---

## ✅ Garanties du système

| Problème | Solution |
|----------|----------|
| Re-télécharger un clip déjà DL | ❌ `WHERE status = 'pending'` |
| Re-monter un clip déjà monté | ❌ `WHERE status = 'downloaded'` |
| Re-poster un clip déjà posté | ❌ UNIQUE(clip_id, worker_id, platform) |
| Perte clip si montage échoue | ✅ Fichier conservé, retry max 3× |
| Perte clip si upload échoue | ✅ Fichier conservé, retry demain |
| Deux workers postent le même clip | ✅ Chaque worker voit seulement ses clips non postés |
| Webhook reçu 2× / Refetch clips | ❌ PRIMARY KEY clip_id empêche doublons |

---

---

## 🗄️ Structure simplifiée - 4 tables uniquement

Le pipeline utilise **4 tables** :

1. **`clips`** - Pipeline principal avec statuts (contient UNIQUEMENT les clips whitelisted)
2. **`publications`** - Tracking multi-plateforme par worker
3. **`editor_whitelist`** - Filtrage des éditeurs (optionnel, chargé en cache au démarrage)
4. **`workers`** - Configuration multi-compte

**Points clés** :
- ✅ **Pas besoin de table `streams`** : La `PRIMARY KEY clip_id` empêche déjà les doublons
- ✅ **Filtrage AVANT insertion** : Seulement les clips WL entrent dans la BDD
- ✅ **Cache whitelist** : Chargée 1 fois en mémoire pour performance maximale

---

## 🎯 Prochaines étapes

1. ✅ Créer la BDD : `python init_db.py`
2. ✅ Adapter tes services existants pour utiliser SQLite
3. ✅ Créer les 3 workers
4. ✅ Setup webhook Flask
5. ✅ Tester le pipeline end-to-end
