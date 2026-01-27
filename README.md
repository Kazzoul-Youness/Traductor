# 🧁 AllMuffins Recipe Translator

CLI tool pour traduire automatiquement les recettes de allmuffins.com vers plusieurs langues.

## 🎯 Objectif

Traduire les recettes en FR, ES, DE, SV pour maximiser la monétisation avec des domaines séparés par langue.

## 📋 Prérequis

- Python 3.8+
- Claude API Key (obtenir sur console.anthropic.com)
- Connexion internet

## ⚙️ Installation

```bash
# 1. Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 2. Installer les dépendances
pip install -r requirements.txt
```

## 🚀 Utilisation

### 1. Lister les recettes du sitemap

```bash
python recipe_translator.py list --limit 10
```

**Résultat :**
```
🔍 Fetching recipes from sitemap...

Found 10 recipes
┏━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ № ┃ Recipe URL                          ┃ Last Modified ┃
┡━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ 1 │ https://allmuffins.com/chocolate... │ 2024-01-15    │
│ 2 │ https://allmuffins.com/blueberry... │ 2024-01-14    │
└───┴─────────────────────────────────────┴───────────────┘
```

### 2. Traduire une recette unique

```bash
python recipe_translator.py translate \
  "https://allmuffins.com/chocolate-muffins" \
  --langs fr es \
  --api-key YOUR_CLAUDE_API_KEY \
  --save
```

**Options :**
- `--langs` : Langues cibles (fr, es, de, sv)
- `--api-key` : Votre clé API Claude
- `--save` : Sauvegarder en JSON

**Résultat :**
```
🌍 Translating: https://allmuffins.com/chocolate-muffins

Step 1: Scraping recipe content...
✓ Scraped: Chocolate Muffins
   Content length: 1234 chars
   Internal links: 5

Step 2: Translating to FR...
✓ Translated to FR
   Title: Muffins au Chocolat
   Slug: muffins-au-chocolat
   Words: 856

📊 Translation Summary
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
┃ Language     ┃ Title             ┃ Word Count┃ Target URL        ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
│ EN (original)│ Chocolate Muffins │ 945       │ https://all...    │
│ FR           │ Muffins Chocolat  │ 856       │ https://tous...   │
│ ES           │ Muffins Chocolate │ 892       │ https://todos...  │
└──────────────┴───────────────────┴───────────┴───────────────────┘

✓ Saved to: translation_chocolate_muffins.json
```

### 3. Traduction en batch (plusieurs recettes)

```bash
python recipe_translator.py batch \
  --count 5 \
  --langs fr es de \
  --api-key YOUR_CLAUDE_API_KEY
```

**Résultat :**
```
🚀 Batch translating 5 recipes to fr, es, de

✓ Found 5 recipes to translate

═══ Recipe 1/5 ═══
[traduction en cours...]

═══ Recipe 2/5 ═══
[traduction en cours...]

🎉 Batch translation complete!
✓ Translated 5 recipes to 3 languages
✓ Total translations: 15
```

## 📂 Structure des fichiers générés

```
allmuffins-translator/
├── translation_chocolate_muffins.json
├── translation_blueberry_muffins.json
└── ...
```

**Format JSON :**
```json
{
  "original": {
    "url": "https://allmuffins.com/chocolate-muffins",
    "title": "Chocolate Muffins",
    "content": "...",
    "images": [...],
    "internal_links": [...]
  },
  "translations": {
    "fr": {
      "title": "Muffins au Chocolat",
      "content": "...",
      "slug": "muffins-au-chocolat",
      "target_url": "https://tousmuffins.com/muffins-au-chocolat",
      "word_count": 856
    },
    "es": {...}
  }
}
```

## 🔧 Modules disponibles

### SitemapParser
Parse le sitemap XML et extrait toutes les recettes.

```python
from modules import SitemapParser

parser = SitemapParser('https://allmuffins.com/sitemap_index.xml')
recipes = parser.get_all_recipes(limit=10)
```

### RecipeScraper
Scrape le contenu d'une recette (title, content, images, links).

```python
from modules import RecipeScraper

scraper = RecipeScraper()
recipe = scraper.scrape('https://allmuffins.com/chocolate-muffins')
```

### RecipeTranslator
Traduit le contenu via Claude API.

```python
from modules import RecipeTranslator

translator = RecipeTranslator(api_key='your-key')
result = translator.translate(
    title='Chocolate Muffins',
    content='...',
    target_lang='fr'
)
```

### LinkAdapter
Adapte les liens internes pour le domaine cible.

```python
from modules import LinkAdapter

adapter = LinkAdapter()
adapted = adapter.adapt_links(
    content='...',
    target_domain='tousmuffins.com',
    lang_code='fr'
)
```

## 💰 Estimation des coûts

```python
from modules import RecipeTranslator

translator = RecipeTranslator(api_key='your-key')

# Estimer le coût pour 500 recettes × 4 langues
cost = translator.estimate_cost(
    content_length=2000,  # 2000 chars par recette
    num_translations=4    # 4 langues
)

print(f"Coût estimé : ${cost['estimated_cost_usd']}")
# Résultat : ~$0.02 par traduction
# Total pour 500 recettes : ~$40
```

## 🎨 Fonctionnalités clés

✅ **Parse sitemap automatiquement**  
✅ **Scrape contenu complet des recettes**  
✅ **Traduction Claude API optimisée**  
✅ **Adaptation automatique des liens internes**  
✅ **Génération de slugs SEO-friendly**  
✅ **Traduction des slugs (chocolate → chocolat)**  
✅ **Support FR, ES, DE, SV**  
✅ **Export JSON pour intégration**  
✅ **Interface CLI avec Rich (couleurs, tableaux)**  
✅ **Estimation de coûts API**

## 🔜 Prochaines étapes (Production)

1. **Semaine prochaine :** Tester avec 20-50 recettes réelles
2. **Valider qualité :** Ajuster les prompts si nécessaire
3. **Migration FastAPI :** Créer l'API production
4. **Docker :** Déployer sur Hetzner
5. **Automatisation :** Cron pour nouvelles recettes

## 📊 Mapping des domaines

| Langue | Domaine            | Code |
|--------|-------------------|------|
| 🇬🇧 EN  | allmuffins.com    | en   |
| 🇫🇷 FR  | tousmuffins.com   | fr   |
| 🇪🇸 ES  | todosmuffins.com  | es   |
| 🇩🇪 DE  | allemuffins.de    | de   |
| 🇸🇪 SV  | allamuffins.se    | sv   |

## 🐛 Debug

Si erreur lors de l'exécution :

```bash
# Vérifier l'installation
pip list | grep anthropic

# Tester la connexion API
python -c "import anthropic; print('OK')"

# Vérifier le sitemap
curl https://allmuffins.com/sitemap_index.xml
```

## 📝 Notes

- Les traductions sont effectuées par Claude Sonnet 4 (meilleure qualité)
- Les liens internes sont automatiquement adaptés
- Les slugs sont traduits intelligemment (chocolate → chocolat)
- Les images restent sur le même CDN pour l'instant
- Les coûts API sont très faibles (~$0.02 par recette)

## 🤝 Support

Questions ? Problèmes ?
1. Vérifier les logs
2. Tester avec `--limit 1` d'abord
3. Vérifier la clé API Claude

---

**Ready to scale!** 🚀
