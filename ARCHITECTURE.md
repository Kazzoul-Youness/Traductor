# 🏗️ Architecture Technique

Documentation de l'architecture du système de traduction AllMuffins.

## 📊 Vue d'ensemble

```
┌─────────────────────────────────────────────────────────┐
│                    PHASE 1: CLI/Streamlit               │
│                      (Test & Validation)                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐      ┌──────────────┐              │
│  │   Sitemap    │─────▶│   Recipe     │              │
│  │   Parser     │      │   Scraper    │              │
│  └──────────────┘      └──────────────┘              │
│         │                      │                       │
│         │                      ▼                       │
│         │              ┌──────────────┐              │
│         │              │   Claude     │              │
│         │              │  Translator  │              │
│         │              └──────────────┘              │
│         │                      │                       │
│         └──────────────────────┴──────────────┐      │
│                                                │      │
│                                        ┌──────────────┐│
│                                        │     Link     ││
│                                        │   Adapter    ││
│                                        └──────────────┘│
│                                                │      │
│                                        ┌──────────────┐│
│                                        │    JSON      ││
│                                        │   Export     ││
│                                        └──────────────┘│
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    PHASE 2: Production                  │
│                  (Hetzner + Docker)                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌────────────────────────────────────────────────┐   │
│  │             FastAPI REST API                    │   │
│  ├────────────────────────────────────────────────┤   │
│  │  POST /translate                                │   │
│  │  GET  /status/{job_id}                         │   │
│  │  GET  /translations                             │   │
│  └────────────────────────────────────────────────┘   │
│                       │                                 │
│         ┌─────────────┼─────────────┐                 │
│         │             │             │                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │PostgreSQL│  │  Redis   │  │  Celery  │           │
│  │          │  │  Queue   │  │ Workers  │           │
│  └──────────┘  └──────────┘  └──────────┘           │
│                                     │                  │
│                             ┌──────────────┐          │
│                             │  WordPress   │          │
│                             │  REST API    │          │
│                             └──────────────┘          │
└─────────────────────────────────────────────────────────┘
```

## 🔧 Composants Principaux

### 1. **SitemapParser** (`modules/sitemap_parser.py`)

**Responsabilité:** Parser le sitemap XML et extraire les URLs des recettes.

**Fonctionnalités:**
- Parse sitemap index et sous-sitemaps
- Filtre les URLs non-recettes (catégories, tags, etc.)
- Gère la pagination et limites
- Support sitemap imbriqués

**Utilisation:**
```python
parser = SitemapParser('https://allmuffins.com/sitemap_index.xml')
recipes = parser.get_all_recipes(limit=100)
```

**Dépendances:**
- `requests` - HTTP requests
- `xml.etree.ElementTree` - XML parsing

---

### 2. **RecipeScraper** (`modules/recipe_scraper.py`)

**Responsabilité:** Extraire le contenu complet d'une recette.

**Fonctionnalités:**
- Extraction titre, contenu, meta description
- Extraction images avec URLs et alt text
- Détection liens internes allmuffins.com
- Support Schema.org JSON-LD (recettes structurées)
- Nettoyage et normalisation du texte

**Utilisation:**
```python
scraper = RecipeScraper()
recipe = scraper.scrape('https://allmuffins.com/chocolate-muffins')
```

**Dépendances:**
- `beautifulsoup4` - HTML parsing
- `requests` - HTTP requests
- `lxml` - Parser XML/HTML

**Données extraites:**
```json
{
  "url": "...",
  "title": "...",
  "content": "...",
  "meta_description": "...",
  "images": [...],
  "internal_links": [...],
  "recipe_data": {...},
  "word_count": 945
}
```

---

### 3. **RecipeTranslator** (`modules/translator.py`)

**Responsabilité:** Traduire le contenu via Claude API.

**Fonctionnalités:**
- Traduction optimisée pour contenu culinaire
- Génération slugs SEO-friendly
- Support 4 langues (FR, ES, DE, SV)
- Adaptation unités de mesure
- Estimation coûts API

**Architecture prompt:**
```
System: Expert culinaire + SEO
Temperature: 0.3 (consistance)
Format: Structuré (TITLE/SLUG/CONTENT)
```

**Utilisation:**
```python
translator = RecipeTranslator(api_key='sk-ant-...')
result = translator.translate(
    title='Chocolate Muffins',
    content='...',
    target_lang='fr'
)
```

**Modèle:** Claude Sonnet 4 (`claude-sonnet-4-20250514`)

**Coûts:**
- Input: $3/M tokens
- Output: $15/M tokens
- ~$0.02 par recette traduite

---

### 4. **LinkAdapter** (`modules/link_adapter.py`)

**Responsabilité:** Adapter liens internes pour domaines cibles.

**Fonctionnalités:**
- Remplacement domaine (allmuffins.com → tousmuffins.com)
- Traduction slugs (chocolate → chocolat)
- Génération hreflang tags
- Validation liens
- Language switcher URLs

**Mapping domaines:**
```python
{
  'en': 'allmuffins.com',
  'fr': 'tousmuffins.com',
  'es': 'todosmuffins.com',
  'de': 'allemuffins.de',
  'sv': 'allamuffins.se'
}
```

**Utilisation:**
```python
adapter = LinkAdapter()
adapted = adapter.adapt_links(
    content='<a href="https://allmuffins.com/chocolate-muffins">...',
    target_domain='tousmuffins.com',
    lang_code='fr'
)
# Résultat: <a href="https://tousmuffins.com/muffins-chocolat">...
```

---

## 🎯 Workflow Complet

### Phase 1: CLI (Actuel)

```
1. User lance commande
   └─▶ python recipe_translator.py translate <URL>

2. SitemapParser
   └─▶ Parse sitemap
   └─▶ Retourne liste URLs

3. RecipeScraper
   └─▶ Scrape URL
   └─▶ Extrait titre, contenu, images, liens

4. RecipeTranslator
   └─▶ Appel Claude API
   └─▶ Traduction + génération slug

5. LinkAdapter
   └─▶ Adaptation liens internes
   └─▶ Remplacement domaines

6. Export JSON
   └─▶ Sauvegarde translation_*.json
   └─▶ Prêt pour import WordPress
```

### Phase 2: Production (Future)

```
1. Cron job quotidien
   └─▶ Check nouveau contenu sitemap
   └─▶ Queue nouvelles recettes

2. Celery Worker
   └─▶ Process queue async
   └─▶ Scrape + Translate + Adapt

3. PostgreSQL
   └─▶ Store mapping URLs
   └─▶ Track status traductions

4. WordPress REST API
   └─▶ Publish automatiquement
   └─▶ Upload images
   └─▶ Set categories/tags

5. Monitoring
   └─▶ Dashboard stats
   └─▶ Alertes erreurs
   └─▶ Coûts API
```

---

## 🗄️ Base de Données (Phase 2)

### Schema PostgreSQL

```sql
-- Table: recipes
CREATE TABLE recipes (
    id SERIAL PRIMARY KEY,
    original_url VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table: translations
CREATE TABLE translations (
    id SERIAL PRIMARY KEY,
    recipe_id INTEGER REFERENCES recipes(id),
    lang_code VARCHAR(5) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    slug VARCHAR(255) NOT NULL,
    target_url VARCHAR(255),
    target_post_id INTEGER,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    published_at TIMESTAMP,
    UNIQUE(recipe_id, lang_code)
);

-- Table: translation_jobs
CREATE TABLE translation_jobs (
    id SERIAL PRIMARY KEY,
    recipe_id INTEGER REFERENCES recipes(id),
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Index
CREATE INDEX idx_translations_recipe ON translations(recipe_id);
CREATE INDEX idx_translations_status ON translations(status);
CREATE INDEX idx_jobs_status ON translation_jobs(status);
```

---

## 🐳 Docker Stack (Phase 2)

### Services

```yaml
1. api (FastAPI)
   - Port: 8000
   - Resources: 2 CPU, 4GB RAM
   - Replicas: 2 (HA)

2. worker (Celery)
   - Queues: translation, publishing
   - Concurrency: 4
   - Replicas: 2

3. redis
   - Port: 6379
   - Persistence: AOF
   - Max memory: 2GB

4. postgres
   - Port: 5432
   - Storage: 100GB SSD
   - Backups: Daily

5. nginx
   - Port: 80/443
   - SSL: Let's Encrypt
   - Rate limiting
```

---

## 📈 Scalabilité

### Limites actuelles (CLI)

- **Throughput:** ~1 recette/10s (API latency)
- **Concurrent:** 1 (sequential)
- **Batch:** 500 recettes = ~1.5h

### Optimisations Phase 2

- **Throughput:** 10-20 recettes/s (async workers)
- **Concurrent:** 10+ workers parallèles
- **Batch:** 500 recettes = ~5-10min

**Bottlenecks:**
1. Claude API rate limits (50 req/min)
2. WordPress API (peut ralentir)
3. Scraping (ajouter delays anti-ban)

**Solutions:**
- Queue management (Redis)
- Rate limiting intelligent
- Retry logic avec backoff
- Cache résultats intermédiaires

---

## 🔐 Sécurité

### API Keys
- Stockage: Variables d'environnement
- Rotation: Mensuelle recommandée
- Scoping: Minimum nécessaire

### WordPress
- Application passwords (pas mot de passe principal)
- HTTPS obligatoire
- Rate limiting
- Input validation

### Data
- Sanitization HTML
- SQL injection prevention (ORM)
- XSS prevention

---

## 📊 Monitoring

### Métriques clés

```
- Translations/day
- Success rate %
- API cost/day
- Average translation time
- Error rate by type
- Queue depth
```

### Alertes

```
- API cost > $X/day
- Error rate > Y%
- Queue depth > Z
- Worker down
- Database full
```

---

## 🚀 Déploiement

### Hetzner Setup

```bash
# 1. Créer serveur
hcloud server create \
  --name allmuffins-translator \
  --type cpx31 \
  --image ubuntu-22.04 \
  --ssh-key my-key

# 2. Install Docker
ssh root@<IP>
curl -fsSL https://get.docker.com | sh

# 3. Deploy stack
git clone <repo>
cd allmuffins-prod
docker-compose up -d

# 4. Monitor
docker-compose logs -f
```

### CI/CD Pipeline

```yaml
1. Git push → main
2. GitHub Actions trigger
3. Build Docker images
4. Push to registry
5. SSH to Hetzner
6. Pull latest images
7. Rolling restart
8. Health check
```

---

## 📝 Maintenance

### Backup quotidien

```bash
# Database
pg_dump translator > backup_$(date +%Y%m%d).sql

# Translations JSON
tar -czf translations_$(date +%Y%m%d).tar.gz translation_*.json
```

### Updates

```bash
# API dependencies
pip install --upgrade -r requirements.txt

# Docker images
docker-compose pull
docker-compose up -d
```

---

## 🎓 Best Practices

1. **Toujours tester** avec 5-10 recettes avant batch complet
2. **Monitorer coûts** API en temps réel
3. **Valider qualité** manuellement régulièrement
4. **Backup avant** déploiement production
5. **Rate limiting** pour éviter bans
6. **Logging exhaustif** pour debug
7. **Documentation à jour** des prompts

---

Prêt pour la phase production ! 🚀
