# ⚡ Quick Start Guide

Guide de démarrage rapide pour tester le translator en 5 minutes.

## 📦 Installation (2 minutes)

```bash
# 1. Créer environnement virtuel
python3 -m venv venv
source venv/bin/activate

# 2. Installer dépendances
pip install -r requirements.txt
```

## 🧪 Tests sans API (1 minute)

Tester que tout fonctionne AVANT d'utiliser l'API:

```bash
python test_quick.py
```

**Résultat attendu:**
```
✓ PASS - Sitemap Parser
✓ PASS - Recipe Scraper
✓ PASS - Link Adapter

Results: 3/3 tests passed
All tests passed! ✓
```

## 💰 Calculer les coûts (30 secondes)

```bash
python cost_calculator.py
```

Voir combien ça coûtera pour traduire ton site.

## 🎯 Premier test avec API (2 minutes)

### Option 1: Tester UNE recette

```bash
export CLAUDE_API_KEY="sk-ant-your-key-here"

python recipe_translator.py translate \
  "https://allmuffins.com/chocolate-muffins" \
  --langs fr \
  --api-key $CLAUDE_API_KEY \
  --save
```

### Option 2: Tester 3 recettes

```bash
python recipe_translator.py batch \
  --count 3 \
  --langs fr \
  --api-key $CLAUDE_API_KEY
```

## 📊 Vérifier le résultat

Les traductions sont sauvegardées en JSON:

```bash
ls -la translation_*.json
cat translation_chocolate_muffins.json | jq '.translations.fr.title'
```

## ✅ Checklist de validation

Après ton premier test, vérifie:

- [ ] Le titre est bien traduit en français
- [ ] Le contenu est naturel (pas littéral)
- [ ] Les liens internes pointent vers tousmuffins.com
- [ ] Le slug est SEO-friendly (muffins-au-chocolat)
- [ ] Les unités sont adaptées (cups → grammes si pertinent)

## 🚀 Prochaines étapes

1. **Valider qualité** → Tester 10-20 recettes
2. **Ajuster prompts** → Si besoin (voir modules/translator.py)
3. **Batch complet** → Lancer tout le site
4. **Production** → Migration vers FastAPI + Docker

## 🐛 Problèmes courants

**Erreur "No module named 'anthropic'"**
```bash
pip install anthropic
```

**Erreur "API key invalid"**
- Vérifier que la clé commence par `sk-ant-`
- Vérifier sur console.anthropic.com

**Sitemap vide**
- Vérifier que allmuffins.com/sitemap_index.xml est accessible
- Essayer avec curl: `curl https://allmuffins.com/sitemap_index.xml`

**Scraping échoue**
- Certains sites ont des protections anti-scraping
- Ajouter délais entre requêtes: `time.sleep(2)`

## 💡 Tips

- **Commencer petit:** 3-5 recettes pour tester
- **Vérifier qualité:** Lire les traductions manuellement
- **Ajuster prompts:** modules/translator.py ligne 65
- **Coûts:** ~$0.02 par recette traduite

## 📞 Support

Si tu bloques:
1. Lancer `python test_quick.py` → identifier le problème
2. Vérifier les logs
3. Tester avec une seule recette d'abord

---

**Temps total:** ⏱️ 5-10 minutes pour tout tester

**Prêt à scaler!** 🚀
