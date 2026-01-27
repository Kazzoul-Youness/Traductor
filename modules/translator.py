"""
Recipe Translator Module
Translate recipes using OpenRouter API with optimized prompts
"""

import httpx
from typing import Dict
import re


class RecipeTranslator:
    """Translate recipes using OpenRouter API"""
    
    # Language configurations
    LANGUAGES = {
        'fr': {
            'name': 'French',
            'locale': 'fr_FR',
            'domain': 'jelorec.com'
        },
        'es': {
            'name': 'Spanish',
            'locale': 'es_ES',
            'domain': 'dietaypeso.com'
        },
        'de': {
            'name': 'German',
            'locale': 'de_DE',
            'domain': 'allemuffins.de'
        },
        'sv': {
            'name': 'Swedish',
            'locale': 'sv_SE',
            'domain': 'allamuffins.se'
        },
        'en': {
            'name': 'English',
            'locale': 'en_US',
            'domain': 'allmuffins.com'
        }
    }
    
    # OpenRouter API endpoint
    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    def __init__(self, api_key: str):
        """
        Initialize translator with OpenRouter API key
        
        Args:
            api_key: OpenRouter API key
        """
        self.api_key = api_key
        self.model = "anthropic/claude-sonnet-4"  # Claude Sonnet via OpenRouter
    
    def translate(self, title: str, content: str, target_lang: str) -> Dict:
        """
        Translate recipe title and content
        
        Args:
            title: Recipe title
            content: Recipe content (full text)
            target_lang: Target language code (fr, es, de, sv)
            
        Returns:
            Dict with translated title, content, slug, word_count
        """
        if target_lang not in self.LANGUAGES:
            raise ValueError(f"Unsupported language: {target_lang}")
        
        lang_config = self.LANGUAGES[target_lang]
        
        # Build translation prompt
        prompt = self._build_translation_prompt(title, content, lang_config)
        
        try:
            # Call OpenRouter API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://allmuffins.com",
                "X-Title": "AllMuffins Recipe Translator"
            }
            
            payload = {
                "model": self.model,
                "max_tokens": 8000,  # Increased for HTML content
                "temperature": 0.2,  # Lower for consistent translations
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            with httpx.Client(timeout=180.0) as client:  # Longer timeout for HTML
                response = client.post(
                    self.OPENROUTER_URL,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
            
            # Parse response
            translated_text = data["choices"][0]["message"]["content"]
            
            # Extract structured data from response
            result = self._parse_translation_response(translated_text, target_lang)
            
            return result
            
        except Exception as e:
            print(f"Translation error: {e}")
            raise
    
    def _build_translation_prompt(self, title: str, content: str, lang_config: Dict) -> str:
        """Build optimized translation prompt for Claude - PRESERVES HTML"""
        
        prompt = f"""You are a professional recipe translator specializing in culinary content.

Translate the following recipe from English to {lang_config['name']}.

CRITICAL - HTML FORMATTING RULES:
1. PRESERVE ALL HTML TAGS EXACTLY: <h2>, <h3>, <p>, <ul>, <ol>, <li>, <table>, <tr>, <td>, <th>, <strong>, <em>, <a href="...">, <img src="..." alt="...">
2. DO NOT remove or modify HTML structure
3. Only translate the TEXT CONTENT between tags
4. Keep all attributes (href, src, alt, class) unchanged
5. Preserve line breaks and spacing

TRANSLATION GUIDELINES:
1. Maintain the same tone (friendly, informative)
2. Adapt cooking terms naturally (cups → metric for non-US)
3. Keep ingredient names accurate in target language
4. Make it SEO-friendly for {lang_config['name']} audience
5. Keep the recipe authentic but culturally adapted

ORIGINAL TITLE:
{title}

ORIGINAL CONTENT (HTML):
{content}

IMPORTANT SEO RULES:
1. SLUG: Keep the ORIGINAL ENGLISH slug (do NOT translate the URL slug)
2. FOCUS KEYWORD: Keep in ENGLISH (do NOT translate) - extract main keyword from title
3. META DESCRIPTION: Write in {lang_config['name']} but include the ENGLISH focus keyword

Provide your translation in this EXACT format:

TRANSLATED_TITLE:
[translated title - plain text, no HTML]

TRANSLATED_SLUG:
[KEEP ORIGINAL ENGLISH SLUG - extract from title, lowercase, hyphens only, do NOT translate]

FOCUS_KEYWORD:
[ENGLISH keyword from original title, 2-4 words, do NOT translate]

SEO_DESCRIPTION:
[meta description in {lang_config['name']}, 150-160 chars, MUST include the ENGLISH focus keyword]

TRANSLATED_CONTENT:
[full translated content WITH ALL HTML TAGS PRESERVED]

Begin translation now:"""

        return prompt
    
    def _parse_translation_response(self, response: str, target_lang: str) -> Dict:
        """Parse Claude's translation response into structured data"""
        
        # Extract title
        title_match = re.search(r'TRANSLATED_TITLE:\s*(.+?)(?=\n\n|\nTRANSLATED_SLUG:|\nFOCUS_KEYWORD:)', 
                               response, re.DOTALL)
        title = title_match.group(1).strip() if title_match else "Untitled"
        
        # Extract slug
        slug_match = re.search(r'TRANSLATED_SLUG:\s*(.+?)(?=\n\n|\nFOCUS_KEYWORD:|\nTRANSLATED_CONTENT:)', 
                              response, re.DOTALL)
        slug = slug_match.group(1).strip() if slug_match else self._generate_slug(title)
        
        # Extract focus keyword (for Rank Math SEO)
        keyword_match = re.search(r'FOCUS_KEYWORD:\s*(.+?)(?=\n\n|\nSEO_DESCRIPTION:|\nTRANSLATED_CONTENT:)', 
                                 response, re.DOTALL)
        focus_keyword = keyword_match.group(1).strip() if keyword_match else ""
        
        # Extract SEO description (for Rank Math)
        seo_desc_match = re.search(r'SEO_DESCRIPTION:\s*(.+?)(?=\n\n|\nTRANSLATED_CONTENT:)', 
                                  response, re.DOTALL)
        seo_description = seo_desc_match.group(1).strip() if seo_desc_match else ""
        
        # Extract content
        content_match = re.search(r'TRANSLATED_CONTENT:\s*(.+)', response, re.DOTALL)
        content = content_match.group(1).strip() if content_match else response
        
        # Clean up any remaining formatting
        title = title.replace('**', '').strip()
        slug = slug.replace('**', '').strip().lower()
        focus_keyword = focus_keyword.replace('**', '').strip()
        seo_description = seo_description.replace('**', '').strip()
        content = content.strip()
        
        # Ensure slug has no accents
        slug = self._generate_slug(slug) if slug else self._generate_slug(title)
        
        return {
            'title': title,
            'slug': slug,
            'content': content,
            'word_count': len(content.split()),
            'target_lang': target_lang,
            'focus_keyword': focus_keyword,
            'seo_description': seo_description
        }
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title"""
        # Convert to lowercase
        slug = title.lower()
        
        # Replace accented characters
        accents = {
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'à': 'a', 'â': 'a', 'ä': 'a',
            'ô': 'o', 'ö': 'o',
            'û': 'u', 'ü': 'u',
            'î': 'i', 'ï': 'i',
            'ç': 'c',
            'ñ': 'n',
            'ß': 'ss',
            'å': 'a', 'ä': 'a', 'ö': 'o'  # Swedish
        }
        
        for accented, plain in accents.items():
            slug = slug.replace(accented, plain)
        
        # Remove special characters
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        
        # Replace spaces with hyphens
        slug = re.sub(r'\s+', '-', slug)
        
        # Remove multiple hyphens
        slug = re.sub(r'-+', '-', slug)
        
        # Trim hyphens from ends
        slug = slug.strip('-')
        
        return slug
    
    def estimate_cost(self, content_length: int, num_translations: int = 1) -> Dict:
        """
        Estimate translation cost
        
        Args:
            content_length: Number of characters in content
            num_translations: Number of target languages
            
        Returns:
            Dict with estimated tokens and cost
        """
        # Rough estimation: 1 token ≈ 4 characters
        input_tokens = content_length // 4
        output_tokens = input_tokens * 1.2  # Translations often slightly longer
        
        total_input = input_tokens * num_translations
        total_output = output_tokens * num_translations
        
        # Claude Sonnet pricing via OpenRouter (approximate)
        input_cost_per_million = 3.0  # $3 per million input tokens
        output_cost_per_million = 15.0  # $15 per million output tokens
        
        input_cost = (total_input / 1_000_000) * input_cost_per_million
        output_cost = (total_output / 1_000_000) * output_cost_per_million
        total_cost = input_cost + output_cost
        
        return {
            'input_tokens': total_input,
            'output_tokens': total_output,
            'estimated_cost_usd': round(total_cost, 4),
            'cost_per_translation': round(total_cost / num_translations, 4)
        }
