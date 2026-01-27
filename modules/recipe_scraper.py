"""
Recipe Scraper Module
Scrape recipe content from WordPress pages - PRESERVES HTML FORMATTING
"""

import requests
from bs4 import BeautifulSoup, NavigableString
from typing import Dict, List, Optional
import re


class RecipeScraper:
    """Scrape recipe content from WordPress pages - Preserves HTML formatting"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Elements to remove (ads, scripts, etc.)
        self.remove_tags = [
            'script', 'style', 'noscript', 'iframe', 'nav', 'footer', 
            'aside', 'form', 'button', 'input', 'select', 'textarea',
            'comment', 'header'
        ]
        
        # Classes to remove (ads, share buttons, etc.)
        self.remove_classes = [
            'share', 'social', 'comment', 'related', 'sidebar', 'widget',
            'advertisement', 'ad-', 'newsletter', 'subscribe', 'popup',
            'author-box', 'post-navigation', 'breadcrumb', 'menu'
        ]
    
    def scrape(self, url: str) -> Optional[Dict]:
        """
        Scrape recipe content from URL - PRESERVES HTML
        
        Args:
            url: Recipe URL to scrape
            
        Returns:
            Dict with title, content (HTML), images, internal_links, etc.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract main content WITH HTML FORMATTING
            content_html = self._extract_content_html(soup)
            
            # Extract featured image
            featured_image = self._extract_featured_image(soup)
            
            # Extract all images
            images = self._extract_images(soup, url)
            
            # Extract internal links
            internal_links = self._extract_internal_links(soup, url)
            
            # Extract meta description
            meta_desc = self._extract_meta_description(soup)
            
            # Extract recipe schema data if available
            recipe_data = self._extract_recipe_schema(soup)
            
            # Count words in text (not HTML)
            text_only = BeautifulSoup(content_html, 'html.parser').get_text()
            word_count = len(text_only.split())
            
            return {
                'url': url,
                'title': title,
                'content': content_html,  # NOW PRESERVES HTML!
                'meta_description': meta_desc,
                'featured_image': featured_image,
                'images': images,
                'internal_links': internal_links,
                'recipe_data': recipe_data,
                'word_count': word_count
            }
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        # Try h1 first
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
        
        # Fallback to title tag
        title = soup.find('title')
        if title:
            return title.get_text(strip=True).split('|')[0].strip()
        
        return "Untitled Recipe"
    
    def _extract_content_html(self, soup: BeautifulSoup) -> str:
        """Extract main recipe content PRESERVING HTML FORMATTING"""
        
        # Find main content area
        content_selectors = [
            {'class_': 'entry-content'},
            {'class_': 'post-content'},
            {'class_': 'article-content'},
            {'class_': 'content-area'},
            {'class_': 'single-content'},
            {'id': 'content'},
            {'class_': 'wprm-recipe'},
            'article',
            'main'
        ]
        
        content_div = None
        
        for selector in content_selectors:
            if isinstance(selector, dict):
                content_div = soup.find('div', selector)
                if not content_div:
                    content_div = soup.find('article', selector)
            else:
                content_div = soup.find(selector)
            
            if content_div:
                break
        
        if not content_div:
            # Fallback: wrap all paragraphs
            paragraphs = soup.find_all(['p', 'h2', 'h3', 'h4', 'ul', 'ol', 'table'])
            content_div = BeautifulSoup('<div></div>', 'html.parser').div
            for p in paragraphs:
                content_div.append(p.__copy__())
        
        # Clean the content
        cleaned = self._clean_html(content_div)
        
        return str(cleaned)
    
    def _clean_html(self, element) -> BeautifulSoup:
        """Clean HTML content - remove unwanted elements but KEEP formatting"""
        
        # Make a copy to avoid modifying original
        element = BeautifulSoup(str(element), 'html.parser')
        
        # Remove unwanted tags
        for tag_name in self.remove_tags:
            for tag in element.find_all(tag_name):
                tag.decompose()
        
        # Remove elements with unwanted classes
        for class_pattern in self.remove_classes:
            for tag in element.find_all(class_=re.compile(class_pattern, re.I)):
                tag.decompose()
        
        # Remove empty tags (but keep br, hr, img)
        for tag in element.find_all():
            if tag.name not in ['br', 'hr', 'img', 'source', 'picture']:
                if not tag.get_text(strip=True) and not tag.find('img'):
                    tag.decompose()
        
        # Remove inline styles that might cause issues
        for tag in element.find_all(style=True):
            del tag['style']
        
        # Clean up image sources - keep only src and alt
        for img in element.find_all('img'):
            # Keep essential attributes
            src = img.get('src', '') or img.get('data-src', '') or img.get('data-lazy-src', '')
            alt = img.get('alt', '')
            
            # Clear all attributes
            img.attrs = {}
            
            # Set back essential attributes
            if src:
                img['src'] = src
            if alt:
                img['alt'] = alt
            img['loading'] = 'lazy'
        
        # Clean up links - keep href only
        for a in element.find_all('a'):
            href = a.get('href', '')
            text = a.get_text()
            
            # Clear attributes but keep href
            a.attrs = {}
            if href:
                a['href'] = href
        
        return element
    
    def _extract_featured_image(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract featured/hero image URL"""
        
        # Try og:image first (most reliable for featured image)
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image['content']
        
        # Try twitter:image
        twitter_image = soup.find('meta', {'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            return twitter_image['content']
        
        # Try featured image class
        featured = soup.find('img', class_=re.compile('featured|hero|post-thumbnail', re.I))
        if featured and featured.get('src'):
            return featured['src']
        
        # Try first image in content
        content = soup.find('div', class_='entry-content')
        if content:
            first_img = content.find('img')
            if first_img and first_img.get('src'):
                return first_img['src']
        
        return None
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all image URLs from the page"""
        images = []
        
        # Find content area first
        content = soup.find('div', class_='entry-content') or soup.find('article') or soup
        
        for img in content.find_all('img'):
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            
            if src and not any(x in src.lower() for x in ['avatar', 'icon', 'logo', 'emoji', 'gravatar']):
                # Skip tiny images (likely icons)
                width = img.get('width', '999')
                height = img.get('height', '999')
                
                try:
                    if int(width) > 100 and int(height) > 100:
                        images.append(src)
                except:
                    images.append(src)
        
        return list(dict.fromkeys(images))  # Remove duplicates, keep order
    
    def _extract_internal_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract internal links"""
        internal_links = []
        
        # Domains to consider as internal
        internal_domains = ['allmuffins.com', 'jelorec.com', 'dietaypeso.com']
        
        content = soup.find('div', class_='entry-content') or soup.find('article') or soup
        
        for a in content.find_all('a', href=True):
            href = a['href']
            if any(domain in href for domain in internal_domains):
                internal_links.append(href)
        
        return list(set(internal_links))
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        meta = soup.find('meta', {'name': 'description'})
        if meta and meta.get('content'):
            return meta['content']
        
        og_desc = soup.find('meta', {'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc['content']
        
        return ""
    
    def _extract_recipe_schema(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract recipe schema.org data if available"""
        schema_scripts = soup.find_all('script', {'type': 'application/ld+json'})
        
        for script in schema_scripts:
            try:
                import json
                data = json.loads(script.string)
                
                if isinstance(data, dict) and data.get('@type') == 'Recipe':
                    return {
                        'name': data.get('name'),
                        'description': data.get('description'),
                        'prepTime': data.get('prepTime'),
                        'cookTime': data.get('cookTime'),
                        'totalTime': data.get('totalTime'),
                        'recipeYield': data.get('recipeYield'),
                        'ingredients': data.get('recipeIngredient', []),
                        'instructions': data.get('recipeInstructions', [])
                    }
                    
                # Handle @graph format
                if isinstance(data, dict) and '@graph' in data:
                    for item in data['@graph']:
                        if item.get('@type') == 'Recipe':
                            return {
                                'name': item.get('name'),
                                'description': item.get('description'),
                                'prepTime': item.get('prepTime'),
                                'cookTime': item.get('cookTime'),
                                'totalTime': item.get('totalTime'),
                                'recipeYield': item.get('recipeYield'),
                                'ingredients': item.get('recipeIngredient', []),
                                'instructions': item.get('recipeInstructions', [])
                            }
            except:
                continue
        
        return None
