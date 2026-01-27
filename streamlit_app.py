"""
Recipe Translator - GUI avec Publication WordPress
Configuration sauvegardée + Bouton Push to WP séparé
"""

import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path

# Configuration de la page
st.set_page_config(
    page_title="Recipe Translator",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fichier de configuration
CONFIG_FILE = "config.json"

# CSS personnalisé
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    .main { background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #0d1b2a 100%); }
    .stApp { background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #0d1b2a 100%); }
    
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif !important;
        background: linear-gradient(90deg, #00d4ff, #7b2cbf);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stTextInput > div > div > input {
        background-color: rgba(255,255,255,0.05);
        border: 2px solid #00d4ff;
        border-radius: 12px;
        color: white;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff, #7b2cbf);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-family: 'Outfit', sans-serif;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0, 212, 255, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0, 212, 255, 0.5);
    }
    
    /* Bouton WordPress special */
    .wp-publish-btn > button {
        background: linear-gradient(135deg, #21759b, #d54e21) !important;
        box-shadow: 0 4px 20px rgba(33, 117, 155, 0.4) !important;
    }
    
    code {
        font-family: 'JetBrains Mono', monospace !important;
        background: rgba(0, 212, 255, 0.15) !important;
        padding: 0.2rem 0.5rem !important;
        border-radius: 6px !important;
        color: #00d4ff !important;
    }
    
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #00d4ff, #7b2cbf);
    }
</style>
""", unsafe_allow_html=True)

# Import des modules
from modules import SitemapParser, RecipeScraper, RecipeTranslator, LinkAdapter, WordPressPublisher, ContentFormatter


def load_config() -> dict:
    """Charger la configuration sauvegardée"""
    if Path(CONFIG_FILE).exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_config(config: dict):
    """Sauvegarder la configuration"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        st.error(f"Erreur sauvegarde config: {e}")


def init_session_state():
    """Initialiser les variables de session"""
    
    # Charger config sauvegardée
    saved_config = load_config()
    
    defaults = {
        'api_key': saved_config.get('api_key', os.environ.get('OPENROUTER_API_KEY', '')),
        'wp_site_url': saved_config.get('wp_site_url', ''),
        'wp_username': saved_config.get('wp_username', ''),
        'wp_password': saved_config.get('wp_password', ''),
        'wp_connected': False,
        'wp_categories': [],
        'translation_result': None,
        'scraped_content': None,
        'published_url': None,
        'last_url': saved_config.get('last_url', ''),
        'last_lang': saved_config.get('last_lang', 'es')
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def save_current_config():
    """Sauvegarder la configuration actuelle"""
    config = {
        'api_key': st.session_state.api_key,
        'wp_site_url': st.session_state.wp_site_url,
        'wp_username': st.session_state.wp_username,
        'wp_password': st.session_state.wp_password,
        'last_url': st.session_state.get('last_url', ''),
        'last_lang': st.session_state.get('last_lang', 'es')
    }
    save_config(config)


def sidebar():
    """Barre latérale avec configuration"""
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # API Key OpenRouter
        st.markdown("### 🤖 OpenRouter API")
        api_key = st.text_input(
            "Clé API",
            value=st.session_state.api_key,
            type="password",
            key="api_key_input"
        )
        if api_key != st.session_state.api_key:
            st.session_state.api_key = api_key
            save_current_config()
        
        st.markdown("---")
        
        # WordPress Config
        st.markdown("### 📝 WordPress")
        
        wp_site = st.text_input(
            "URL du site",
            value=st.session_state.wp_site_url,
            placeholder="https://dietaypeso.com",
            key="wp_site_input"
        )
        if wp_site != st.session_state.wp_site_url:
            st.session_state.wp_site_url = wp_site
            save_current_config()
        
        wp_user = st.text_input(
            "Nom d'utilisateur",
            value=st.session_state.wp_username,
            key="wp_user_input"
        )
        if wp_user != st.session_state.wp_username:
            st.session_state.wp_username = wp_user
            save_current_config()
        
        wp_pass = st.text_input(
            "Application Password",
            value=st.session_state.wp_password,
            type="password",
            key="wp_pass_input"
        )
        if wp_pass != st.session_state.wp_password:
            st.session_state.wp_password = wp_pass
            save_current_config()
        
        # Test connection
        if st.button("🔌 Tester la connexion", use_container_width=True):
            test_wp_connection()
        
        if st.session_state.wp_connected:
            st.success("🟢 WordPress connecté")
        
        st.markdown("---")
        
        # Bouton sauvegarder
        if st.button("💾 Sauvegarder config", use_container_width=True):
            save_current_config()
            st.success("✅ Configuration sauvegardée!")
        
        st.markdown("---")
        
        # Domaines
        st.markdown("### 🌐 Domaines")
        st.markdown("""
        - 🇫🇷 `jelorec.com`
        - 🇪🇸 `dietaypeso.com`
        - 🇬🇧 `allmuffins.com`
        """)


def test_wp_connection():
    """Tester la connexion WordPress"""
    if not all([st.session_state.wp_site_url, st.session_state.wp_username, st.session_state.wp_password]):
        st.warning("⚠️ Remplissez tous les champs WordPress")
        return
    
    with st.spinner("Connexion..."):
        publisher = WordPressPublisher(
            st.session_state.wp_site_url,
            st.session_state.wp_username,
            st.session_state.wp_password
        )
        result = publisher.test_connection()
        
        if result['success']:
            st.success(f"✅ Connecté: {result['user']}")
            st.session_state.wp_connected = True
            st.session_state.wp_categories = publisher.get_categories()
        else:
            st.error(f"❌ {result['error']}")
            st.session_state.wp_connected = False


def main_content():
    """Contenu principal"""
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# 🌍 Recipe Translator")
        st.markdown("##### Traduisez et publiez vos recettes automatiquement")
    
    with col2:
        if st.session_state.wp_connected:
            st.markdown("### 🟢 WP OK")
        else:
            st.markdown("### 🔴 WP")
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🚀 Traduire", "📋 Explorer", "📊 Historique"])
    
    with tab1:
        translate_tab()
    
    with tab2:
        explore_tab()
    
    with tab3:
        history_tab()


def translate_tab():
    """Onglet de traduction"""
    
    # Input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        url = st.text_input(
            "🔗 URL de l'article source",
            value=st.session_state.get('last_url', ''),
            placeholder="https://jelorec.com/mon-article/",
            key="url_input"
        )
    
    with col2:
        target_lang = st.selectbox(
            "🎯 Langue cible",
            options=['es', 'fr', 'de', 'en'],
            index=['es', 'fr', 'de', 'en'].index(st.session_state.get('last_lang', 'es')),
            format_func=lambda x: {
                'es': '🇪🇸 Espagnol → dietaypeso.com',
                'fr': '🇫🇷 Français → jelorec.com',
                'de': '🇩🇪 Allemand',
                'en': '🇬🇧 Anglais → allmuffins.com'
            }[x],
            key="lang_select"
        )
    
    # Sauvegarder les dernières valeurs
    if url != st.session_state.get('last_url', ''):
        st.session_state.last_url = url
        save_current_config()
    
    if target_lang != st.session_state.get('last_lang', 'es'):
        st.session_state.last_lang = target_lang
        save_current_config()
    
    # Bouton Traduire (sans publier)
    st.markdown("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        translate_btn = st.button("🔄 Traduire", use_container_width=True, type="primary")
    
    if translate_btn:
        execute_translation(url, target_lang)
    
    # Afficher les résultats SI on a une traduction
    if st.session_state.translation_result:
        display_translation_result()


def execute_translation(url, target_lang):
    """Exécuter la traduction (SANS publier)"""
    
    if not url:
        st.error("❌ Entrez une URL")
        return
    
    if not st.session_state.api_key:
        st.error("❌ Configurez votre clé API OpenRouter")
        return
    
    with st.status("🔄 Traduction en cours...", expanded=True) as status:
        progress = st.progress(0)
        
        try:
            # Step 1: Scraping
            st.write("📥 **Étape 1/3:** Récupération de l'article...")
            scraper = RecipeScraper()
            recipe_data = scraper.scrape(url)
            progress.progress(33)
            
            if not recipe_data:
                st.error("❌ Impossible de récupérer l'article")
                return
            
            st.write(f"✅ **{recipe_data['title']}** ({recipe_data['word_count']} mots)")
            
            # Step 2: Translation
            st.write("🌍 **Étape 2/3:** Traduction avec Claude AI...")
            translator = RecipeTranslator(st.session_state.api_key)
            translated = translator.translate(
                title=recipe_data['title'],
                content=recipe_data['content'],
                target_lang=target_lang
            )
            progress.progress(66)
            st.write(f"✅ Traduit: **{translated['title']}**")
            
            # Step 3: Link adaptation
            st.write("🔗 **Étape 3/3:** Adaptation des liens...")
            link_adapter = LinkAdapter()
            domain_map = {
                'fr': 'jelorec.com',
                'es': 'dietaypeso.com',
                'de': 'allemuffins.de',
                'en': 'allmuffins.com'
            }
            
            adapted_content = link_adapter.adapt_links(
                translated['content'],
                target_domain=domain_map.get(target_lang),
                lang_code=target_lang
            )
            progress.progress(100)
            
            # Stocker le résultat
            st.session_state.translation_result = {
                'original': recipe_data,
                'translated': {
                    'title': translated['title'],
                    'slug': translated['slug'],
                    'content': adapted_content,
                    'word_count': translated['word_count'],
                    'target_url': f"https://{domain_map.get(target_lang)}/{translated['slug']}",
                    'focus_keyword': translated.get('focus_keyword', ''),
                    'seo_description': translated.get('seo_description', '')
                },
                'target_lang': target_lang,
                'timestamp': datetime.now().isoformat()
            }
            
            st.session_state.published_url = None  # Reset
            
            status.update(label="✅ Traduction terminée!", state="complete")
            
            # Sauvegarder automatiquement en JSON
            save_translation_json(st.session_state.translation_result)
            
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")
            status.update(label="❌ Erreur", state="error")


def save_translation_json(result):
    """Sauvegarder la traduction en JSON"""
    slug = result['translated']['slug'][:30]
    filename = f"translation_{slug}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    st.info(f"💾 Sauvegardé: `{filename}`")


def display_translation_result():
    """Afficher le résultat de la traduction avec bouton Push to WP"""
    
    result = st.session_state.translation_result
    
    st.markdown("---")
    st.markdown("## 📊 Traduction prête")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**📝 Original**")
        st.code(result['original']['title'][:35] + "...")
    
    with col2:
        st.markdown("**🌍 Traduit**")
        st.code(result['translated']['title'][:35] + "...")
    
    with col3:
        st.markdown("**📊 Mots**")
        st.markdown(f"### {result['translated']['word_count']}")
    
    with col4:
        lang_flags = {'es': '🇪🇸', 'fr': '🇫🇷', 'de': '🇩🇪', 'en': '🇬🇧'}
        st.markdown("**🎯 Langue**")
        st.markdown(f"### {lang_flags.get(result['target_lang'], '')} {result['target_lang'].upper()}")
    
    # URL cible
    st.markdown("### 🔗 URL cible")
    st.code(result['translated']['target_url'])
    
    # SEO Info
    if result['translated'].get('focus_keyword') or result['translated'].get('seo_description'):
        st.markdown("### 🎯 SEO (Rank Math)")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Focus Keyword:**")
            st.code(result['translated'].get('focus_keyword', 'N/A'))
        with col2:
            st.markdown("**Meta Description:**")
            st.text_area("", result['translated'].get('seo_description', ''), height=80, disabled=True, label_visibility="collapsed")
    
    # === SECTION PUBLICATION WORDPRESS ===
    st.markdown("---")
    st.markdown("## 📤 Publier sur WordPress")
    
    if not st.session_state.wp_connected:
        st.warning("⚠️ Connectez-vous à WordPress dans la barre latérale pour publier")
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            publish_status = st.selectbox(
                "📋 Statut",
                options=['draft', 'publish', 'pending'],
                format_func=lambda x: {
                    'draft': '📝 Brouillon',
                    'publish': '🌐 Publié',
                    'pending': '⏳ En attente'
                }[x],
                key="publish_status"
            )
        
        with col2:
            if st.session_state.wp_categories:
                category_names = ['— Aucune —'] + [c['name'] for c in st.session_state.wp_categories]
                selected_category = st.selectbox("📁 Catégorie", options=category_names, key="category_select")
            else:
                selected_category = None
                st.info("Pas de catégories chargées")
        
        with col3:
            upload_image = st.checkbox("🖼️ Transférer les images", value=True, key="upload_image")
        
        # Options de formatage
        col1, col2 = st.columns(2)
        with col1:
            use_gutenberg = st.checkbox("📦 Blocs Gutenberg", value=True, key="use_gutenberg", 
                                       help="Divise le contenu en blocs éditables")
        with col2:
            add_placeholders = st.checkbox("🖼️ Emplacements images", value=False, key="add_placeholders",
                                          help="Ajoute des espaces pour vos images")
        
        # === GROS BOUTON PUSH TO WP ===
        st.markdown("")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="wp-publish-btn">', unsafe_allow_html=True)
            push_btn = st.button("📤 PUSH TO WORDPRESS", use_container_width=True, type="primary")
            st.markdown('</div>', unsafe_allow_html=True)
        
        if push_btn:
            push_to_wordpress(result, publish_status, selected_category, upload_image, use_gutenberg, add_placeholders)
    
    # Si déjà publié
    if st.session_state.published_url:
        st.success(f"🎉 **Publié avec succès!**")
        col1, col2 = st.columns(2)
        with col1:
            st.link_button("👀 Voir l'article", st.session_state.published_url)
        with col2:
            edit_url = f"{st.session_state.wp_site_url}/wp-admin/edit.php"
            st.link_button("✏️ Modifier dans WP", edit_url)
    
    # Aperçu du contenu
    with st.expander("📄 Aperçu du contenu HTML", expanded=False):
        st.code(result['translated']['content'][:3000] + "...", language="html")
    
    # Actions de téléchargement
    st.markdown("### 💾 Télécharger")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        json_data = json.dumps(result, indent=2, ensure_ascii=False)
        st.download_button("📥 JSON", data=json_data, 
                          file_name=f"{result['translated']['slug']}.json",
                          mime="application/json")
    
    with col2:
        st.download_button("📋 HTML", data=result['translated']['content'],
                          file_name=f"{result['translated']['slug']}.html",
                          mime="text/html")
    
    with col3:
        if st.button("🔄 Nouvelle traduction"):
            st.session_state.translation_result = None
            st.session_state.published_url = None
            st.rerun()


def push_to_wordpress(result, status, category, upload_image, use_gutenberg=True, add_placeholders=False):
    """Publier sur WordPress avec SEO, images et blocs Gutenberg"""
    
    with st.spinner("📤 Publication en cours..."):
        publisher = WordPressPublisher(
            st.session_state.wp_site_url,
            st.session_state.wp_username,
            st.session_state.wp_password
        )
        
        # Catégorie
        category_ids = None
        if category and category != '— Aucune —':
            cat = next((c for c in st.session_state.wp_categories if c['name'] == category), None)
            if cat:
                category_ids = [cat['id']]
        
        # Featured Image
        featured_image = None
        if upload_image:
            featured_image = result['original'].get('featured_image')
            if not featured_image and result['original'].get('images'):
                featured_image = result['original']['images'][0]
        
        # Images du contenu
        content_images = result['original'].get('images', []) if upload_image else []
        
        # Préparer le contenu
        content = result['translated']['content']
        
        # Convertir en blocs Gutenberg si demandé
        if use_gutenberg:
            formatter = ContentFormatter()
            
            if add_placeholders:
                # Ajouter des emplacements pour images personnalisées
                content = formatter.add_image_placeholders(content, num_placeholders=3)
            
            # Convertir en blocs Gutenberg
            content = formatter.format_for_wordpress(content)
        
        # SEO fields
        focus_keyword = result['translated'].get('focus_keyword', '')
        seo_description = result['translated'].get('seo_description', '')
        seo_title = result['translated']['title']
        
        # Publication
        pub_result = publisher.publish_post(
            title=result['translated']['title'],
            content=content,
            slug=result['translated']['slug'],
            featured_image_url=featured_image,
            content_images=content_images,
            categories=category_ids,
            status=status,
            focus_keyword=focus_keyword,
            seo_title=seo_title,
            seo_description=seo_description
        )
        
        if pub_result['success']:
            st.session_state.published_url = pub_result['post_url']
            st.success(f"✅ Publié: {pub_result['post_url']}")
            st.balloons()
            st.rerun()
        else:
            st.error(f"❌ Erreur: {pub_result['error']}")


def explore_tab():
    """Onglet exploration"""
    
    st.markdown("### 🔍 Explorer les articles")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        sitemap_url = st.text_input(
            "📍 Sitemap",
            value="https://jelorec.com/sitemap_index.xml",
            key="sitemap_input"
        )
    
    with col2:
        limit = st.number_input("Limite", min_value=1, max_value=50, value=10, key="limit_input")
    
    if st.button("🔎 Charger"):
        with st.spinner("Chargement..."):
            try:
                parser = SitemapParser(sitemap_url)
                recipes = parser.get_all_recipes(limit=limit)
                
                st.success(f"✅ {len(recipes)} articles")
                
                for i, recipe in enumerate(recipes, 1):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.code(recipe['url'])
                    with col2:
                        if st.button("📝", key=f"sel_{i}", help="Utiliser cette URL"):
                            st.session_state.last_url = recipe['url']
                            save_current_config()
                            st.rerun()
                            
            except Exception as e:
                st.error(f"❌ {str(e)}")


def history_tab():
    """Onglet historique"""
    
    st.markdown("### 📊 Traductions sauvegardées")
    
    json_files = sorted(
        [f for f in os.listdir('.') if f.startswith('translation_') and f.endswith('.json')],
        key=lambda x: os.path.getmtime(x),
        reverse=True
    )
    
    if not json_files:
        st.info("📭 Aucune traduction")
        return
    
    st.markdown(f"**{len(json_files)} fichiers**")
    
    for f in json_files[:15]:
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%d/%m %H:%M")
            
            with st.expander(f"📄 {f} ({mtime})"):
                with open(f, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                
                if 'translated' in data:
                    st.markdown(f"**Titre:** {data['translated'].get('title', 'N/A')}")
                    st.markdown(f"**URL:** `{data['translated'].get('target_url', 'N/A')}`")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📂 Charger", key=f"load_{f}"):
                            st.session_state.translation_result = data
                            st.session_state.published_url = None
                            st.rerun()
                    with col2:
                        if st.button("🗑️ Supprimer", key=f"del_{f}"):
                            os.remove(f)
                            st.rerun()
                
        except Exception as e:
            st.error(f"Erreur: {e}")


def main():
    init_session_state()
    sidebar()
    main_content()


if __name__ == "__main__":
    main()
