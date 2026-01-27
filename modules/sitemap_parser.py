"""
Sitemap Parser Module
Parse sitemap XML and extract recipe URLs
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict
from urllib.parse import urljoin


class SitemapParser:
    """Parse AllMuffins sitemap and extract recipe URLs"""
    
    def __init__(self, sitemap_url: str):
        self.sitemap_url = sitemap_url
        self.recipes = []
    
    def get_all_recipes(self, limit: int = None) -> List[Dict]:
        """
        Parse sitemap index and all sub-sitemaps to get recipe URLs
        
        Args:
            limit: Maximum number of recipes to return
            
        Returns:
            List of dicts with 'url' and 'lastmod' keys
        """
        try:
            # Fetch main sitemap index
            response = requests.get(self.sitemap_url, timeout=10)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            
            # Check if this is a sitemap index or a regular sitemap
            if self._is_sitemap_index(root):
                return self._parse_sitemap_index(root, limit)
            else:
                return self._parse_sitemap(root, limit)
                
        except Exception as e:
            print(f"Error parsing sitemap: {e}")
            return []
    
    def _is_sitemap_index(self, root: ET.Element) -> bool:
        """Check if XML is a sitemap index"""
        # Sitemap index uses <sitemap> tags, regular sitemap uses <url> tags
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        sitemaps = root.findall('ns:sitemap', namespace)
        return len(sitemaps) > 0
    
    def _parse_sitemap_index(self, root: ET.Element, limit: int = None) -> List[Dict]:
        """Parse sitemap index and fetch all sub-sitemaps"""
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        sitemap_urls = []
        
        # Get all sitemap URLs
        for sitemap in root.findall('ns:sitemap', namespace):
            loc = sitemap.find('ns:loc', namespace)
            if loc is not None:
                sitemap_urls.append(loc.text)
        
        print(f"Found {len(sitemap_urls)} sub-sitemaps")
        
        # Parse each sub-sitemap
        all_recipes = []
        for sitemap_url in sitemap_urls:
            try:
                response = requests.get(sitemap_url, timeout=10)
                response.raise_for_status()
                sub_root = ET.fromstring(response.content)
                recipes = self._parse_sitemap(sub_root, limit=None)
                all_recipes.extend(recipes)
                
                print(f"  - Parsed {sitemap_url}: {len(recipes)} recipes")
                
                if limit and len(all_recipes) >= limit:
                    break
                    
            except Exception as e:
                print(f"  - Error parsing {sitemap_url}: {e}")
                continue
        
        # Apply limit if specified
        if limit:
            all_recipes = all_recipes[:limit]
        
        return all_recipes
    
    def _parse_sitemap(self, root: ET.Element, limit: int = None) -> List[Dict]:
        """Parse a regular sitemap"""
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        recipes = []
        
        for url_element in root.findall('ns:url', namespace):
            loc = url_element.find('ns:loc', namespace)
            lastmod = url_element.find('ns:lastmod', namespace)
            
            if loc is not None:
                recipe = {
                    'url': loc.text,
                    'lastmod': lastmod.text if lastmod is not None else None
                }
                recipes.append(recipe)
                
                if limit and len(recipes) >= limit:
                    break
        
        return recipes
    
    def filter_recipe_urls(self, urls: List[str]) -> List[str]:
        """
        Filter to keep only actual recipe URLs (exclude homepage, categories, etc.)
        
        Args:
            urls: List of URLs
            
        Returns:
            Filtered list of recipe URLs
        """
        # Common patterns for non-recipe pages
        exclude_patterns = [
            '/category/',
            '/tag/',
            '/page/',
            '/author/',
            '/about',
            '/contact',
            '/privacy',
            '/sitemap'
        ]
        
        filtered = []
        for url in urls:
            # Skip if matches exclude pattern
            if any(pattern in url for pattern in exclude_patterns):
                continue
            
            # Skip homepage
            if url.rstrip('/').endswith('.com'):
                continue
                
            filtered.append(url)
        
        return filtered
