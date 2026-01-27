"""
Link Adapter Module
Adapt internal links from source domain to target domain
"""

import re
from typing import Dict, List
from urllib.parse import urlparse, urljoin


class LinkAdapter:
    """Adapt internal links for translated versions"""
    
    # Domain mapping
    DOMAIN_MAP = {
        'en': 'allmuffins.com',
        'fr': 'jelorec.com',
        'es': 'dietaypeso.com',
        'de': 'allemuffins.de',
        'sv': 'allamuffins.se'
    }
    
    # Source domains to replace
    SOURCE_DOMAINS = ['allmuffins.com', 'jelorec.com', 'dietaypeso.com']
    
    # Common slug translations (can be extended)
    SLUG_TRANSLATIONS = {
        'fr': {
            'recipe': 'recette',
            'recipes': 'recettes',
            'muffins': 'muffins',
            'chocolate': 'chocolat',
            'vanilla': 'vanille',
            'strawberry': 'fraise',
            'blueberry': 'myrtille',
            'banana': 'banane',
            'apple': 'pomme',
            'cinnamon': 'cannelle',
            'easy': 'facile',
            'quick': 'rapide',
            'best': 'meilleur',
            'homemade': 'fait-maison'
        },
        'es': {
            'recipe': 'receta',
            'recipes': 'recetas',
            'muffins': 'muffins',
            'chocolate': 'chocolate',
            'vanilla': 'vainilla',
            'strawberry': 'fresa',
            'blueberry': 'arandano',
            'banana': 'platano',
            'apple': 'manzana',
            'cinnamon': 'canela',
            'easy': 'facil',
            'quick': 'rapido',
            'best': 'mejor',
            'homemade': 'casero'
        },
        'de': {
            'recipe': 'rezept',
            'recipes': 'rezepte',
            'muffins': 'muffins',
            'chocolate': 'schokolade',
            'vanilla': 'vanille',
            'strawberry': 'erdbeere',
            'blueberry': 'heidelbeere',
            'banana': 'banane',
            'apple': 'apfel',
            'cinnamon': 'zimt',
            'easy': 'einfach',
            'quick': 'schnell',
            'best': 'beste',
            'homemade': 'hausgemacht'
        },
        'sv': {
            'recipe': 'recept',
            'recipes': 'recept',
            'muffins': 'muffins',
            'chocolate': 'choklad',
            'vanilla': 'vanilj',
            'strawberry': 'jordgubbe',
            'blueberry': 'blabar',
            'banana': 'banan',
            'apple': 'apple',
            'cinnamon': 'kanel',
            'easy': 'enkel',
            'quick': 'snabb',
            'best': 'basta',
            'homemade': 'hemlagad'
        }
    }
    
    def adapt_links(self, content: str, target_domain: str, lang_code: str) -> str:
        """
        Adapt all internal links in content to target domain
        
        Args:
            content: HTML/text content with links
            target_domain: Target domain (e.g., dietaypeso.com)
            lang_code: Language code for slug translation
            
        Returns:
            Content with adapted links
        """
        adapted_content = content
        
        # Replace links from all source domains
        for source_domain in self.SOURCE_DOMAINS:
            pattern = rf'https?://(?:www\.)?{re.escape(source_domain)}/([^"\'\s<>]*)'
            
            def replace_link(match):
                original_path = match.group(1)
                
                # Translate slug if possible
                translated_path = self._translate_slug(original_path, lang_code)
                
                # Build new URL
                new_url = f"https://{target_domain}/{translated_path}"
                
                return new_url
            
            # Replace all matches
            adapted_content = re.sub(pattern, replace_link, adapted_content)
        
        return adapted_content
    
    def _translate_slug(self, slug: str, lang_code: str) -> str:
        """
        Translate URL slug to target language
        
        Args:
            slug: Original English slug
            lang_code: Target language code
            
        Returns:
            Translated slug
        """
        if lang_code not in self.SLUG_TRANSLATIONS:
            return slug
        
        translations = self.SLUG_TRANSLATIONS[lang_code]
        
        # Split slug into parts
        parts = slug.split('/')
        translated_parts = []
        
        for part in parts:
            # Split by hyphens
            words = part.split('-')
            translated_words = []
            
            for word in words:
                # Translate if we have a translation
                translated = translations.get(word.lower(), word)
                translated_words.append(translated)
            
            # Rejoin
            translated_part = '-'.join(translated_words)
            translated_parts.append(translated_part)
        
        return '/'.join(translated_parts)
    
    def extract_internal_links(self, content: str) -> List[str]:
        """
        Extract all internal links from content (all source domains)
        
        Args:
            content: HTML/text content
            
        Returns:
            List of internal links
        """
        all_matches = []
        for source_domain in self.SOURCE_DOMAINS:
            pattern = rf'https?://(?:www\.)?{re.escape(source_domain)}/([^"\'\s<>]*)'
            matches = re.findall(pattern, content)
            all_matches.extend(matches)
        return list(set(all_matches))  # Remove duplicates
    
    def generate_hreflang_tags(self, base_slug: str) -> List[str]:
        """
        Generate hreflang tags for all language versions
        
        Args:
            base_slug: Base URL slug (English)
            
        Returns:
            List of hreflang HTML tags
        """
        tags = []
        
        # English (original)
        tags.append(
            f'<link rel="alternate" hreflang="en" href="https://allmuffins.com/{base_slug}" />'
        )
        
        # Other languages
        for lang_code, domain in self.DOMAIN_MAP.items():
            if lang_code == 'en':
                continue
                
            translated_slug = self._translate_slug(base_slug, lang_code)
            tags.append(
                f'<link rel="alternate" hreflang="{lang_code}" '
                f'href="https://{domain}/{translated_slug}" />'
            )
        
        # x-default (fallback)
        tags.append(
            f'<link rel="alternate" hreflang="x-default" href="https://allmuffins.com/{base_slug}" />'
        )
        
        return tags
    
    def build_language_switcher(self, current_url: str, current_lang: str) -> Dict[str, str]:
        """
        Build language switcher URLs for a page
        
        Args:
            current_url: Current page URL
            current_lang: Current language code
            
        Returns:
            Dict mapping language codes to URLs
        """
        # Extract path from current URL
        parsed = urlparse(current_url)
        path = parsed.path.lstrip('/')
        
        switcher = {}
        
        for lang_code, domain in self.DOMAIN_MAP.items():
            if lang_code == current_lang:
                switcher[lang_code] = current_url
            else:
                # Translate path to target language
                translated_path = self._translate_slug(path, lang_code)
                switcher[lang_code] = f"https://{domain}/{translated_path}"
        
        return switcher
    
    def validate_links(self, content: str) -> Dict:
        """
        Validate all links in content
        
        Args:
            content: Content with links
            
        Returns:
            Dict with validation results
        """
        all_links = re.findall(r'https?://[^\s<>"\']+', content)
        
        internal_domains = ['allmuffins.com', 'jelorec.com', 'dietaypeso.com',
                           'tousmuffins.com', 'todosmuffins.com',
                           'allemuffins.de', 'allamuffins.se']
        
        internal_links = [l for l in all_links if any(d in l for d in internal_domains)]
        
        external_links = [l for l in all_links if l not in internal_links]
        
        return {
            'total_links': len(all_links),
            'internal_links': len(internal_links),
            'external_links': len(external_links),
            'internal_link_list': internal_links,
            'external_link_list': external_links
        }
