#!/usr/bin/env python3
"""
WordPress Exporter (FUTURE USE)
Export translations to WordPress sites via REST API

This is a template for when you're ready to automate publishing
"""

import requests
import json
from typing import Dict
from rich.console import Console

console = Console()


class WordPressPublisher:
    """Publish translated content to WordPress via REST API"""
    
    def __init__(self, site_url: str, username: str, app_password: str):
        """
        Initialize WordPress publisher
        
        Args:
            site_url: WordPress site URL (e.g., https://tousmuffins.com)
            username: WordPress username
            app_password: Application password (generated in WP admin)
        """
        self.site_url = site_url.rstrip('/')
        self.username = username
        self.app_password = app_password
        self.api_base = f"{self.site_url}/wp-json/wp/v2"
    
    def publish_post(self, title: str, content: str, slug: str, 
                    featured_image_url: str = None,
                    categories: list = None,
                    status: str = 'draft') -> Dict:
        """
        Publish a new post to WordPress
        
        Args:
            title: Post title
            content: Post content (HTML)
            slug: URL slug
            featured_image_url: URL of featured image
            categories: List of category IDs
            status: 'draft' or 'publish'
            
        Returns:
            Response dict with post ID and URL
        """
        endpoint = f"{self.api_base}/posts"
        
        # Prepare data
        data = {
            'title': title,
            'content': content,
            'slug': slug,
            'status': status
        }
        
        if categories:
            data['categories'] = categories
        
        if featured_image_url:
            # Upload image first, then attach
            media_id = self._upload_image(featured_image_url)
            if media_id:
                data['featured_media'] = media_id
        
        # Make request
        try:
            response = requests.post(
                endpoint,
                json=data,
                auth=(self.username, self.app_password),
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return {
                'success': True,
                'post_id': result['id'],
                'post_url': result['link'],
                'status': result['status']
            }
            
        except Exception as e:
            console.print(f"[red]Error publishing post:[/red] {e}")
            return {'success': False, 'error': str(e)}
    
    def _upload_image(self, image_url: str) -> int:
        """Upload image to WordPress media library"""
        try:
            # Download image
            img_response = requests.get(image_url, timeout=10)
            img_response.raise_for_status()
            
            # Upload to WordPress
            endpoint = f"{self.api_base}/media"
            
            files = {
                'file': ('image.jpg', img_response.content, 'image/jpeg')
            }
            
            response = requests.post(
                endpoint,
                files=files,
                auth=(self.username, self.app_password),
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result['id']
            
        except Exception as e:
            console.print(f"[yellow]Warning: Could not upload image:[/yellow] {e}")
            return None
    
    def update_post(self, post_id: int, title: str = None, 
                   content: str = None, status: str = None) -> Dict:
        """Update an existing post"""
        endpoint = f"{self.api_base}/posts/{post_id}"
        
        data = {}
        if title:
            data['title'] = title
        if content:
            data['content'] = content
        if status:
            data['status'] = status
        
        try:
            response = requests.post(
                endpoint,
                json=data,
                auth=(self.username, self.app_password),
                timeout=30
            )
            response.raise_for_status()
            
            return {'success': True, 'post_id': post_id}
            
        except Exception as e:
            console.print(f"[red]Error updating post:[/red] {e}")
            return {'success': False, 'error': str(e)}
    
    def get_categories(self) -> list:
        """Get all categories from WordPress"""
        endpoint = f"{self.api_base}/categories"
        
        try:
            response = requests.get(
                endpoint,
                auth=(self.username, self.app_password),
                timeout=10
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            console.print(f"[red]Error fetching categories:[/red] {e}")
            return []
    
    def create_category(self, name: str, slug: str = None) -> int:
        """Create a new category"""
        endpoint = f"{self.api_base}/categories"
        
        data = {
            'name': name,
            'slug': slug or name.lower().replace(' ', '-')
        }
        
        try:
            response = requests.post(
                endpoint,
                json=data,
                auth=(self.username, self.app_password),
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            return result['id']
            
        except Exception as e:
            console.print(f"[red]Error creating category:[/red] {e}")
            return None


def example_usage():
    """Example of how to use the WordPress publisher"""
    
    console.print("\n[bold cyan]WordPress Publisher - Example Usage[/bold cyan]\n")
    
    # Configuration
    SITE_URL = "https://tousmuffins.com"
    USERNAME = "your-username"
    APP_PASSWORD = "your-app-password"  # Generate in WP Admin → Users → Application Passwords
    
    # Initialize publisher
    publisher = WordPressPublisher(SITE_URL, USERNAME, APP_PASSWORD)
    
    # Example: Publish a translated recipe
    result = publisher.publish_post(
        title="Muffins au Chocolat",
        content="<p>Voici la recette des délicieux muffins au chocolat...</p>",
        slug="muffins-au-chocolat",
        featured_image_url="https://allmuffins.com/wp-content/uploads/chocolate-muffins.jpg",
        status='draft'  # Use 'publish' to publish immediately
    )
    
    if result['success']:
        console.print(f"[green]✓[/green] Post published!")
        console.print(f"  Post ID: {result['post_id']}")
        console.print(f"  URL: {result['post_url']}")
    else:
        console.print(f"[red]✗ Failed to publish[/red]")


def batch_publish_from_json(json_file: str, site_config: Dict):
    """
    Publish multiple translations from JSON file
    
    Args:
        json_file: Path to translation JSON file
        site_config: Dict with site_url, username, app_password
    """
    console.print(f"\n[bold cyan]Publishing from {json_file}...[/bold cyan]\n")
    
    # Load translations
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Initialize publisher
    publisher = WordPressPublisher(
        site_config['site_url'],
        site_config['username'],
        site_config['app_password']
    )
    
    # Publish each translation
    results = []
    
    for lang, translation in data.get('translations', {}).items():
        console.print(f"Publishing {lang.upper()}...")
        
        result = publisher.publish_post(
            title=translation['title'],
            content=translation['content'],
            slug=translation['slug'],
            status='draft'
        )
        
        results.append((lang, result))
        
        if result['success']:
            console.print(f"  [green]✓[/green] {result['post_url']}")
        else:
            console.print(f"  [red]✗[/red] Failed")
    
    # Summary
    successful = sum(1 for _, r in results if r['success'])
    console.print(f"\n[bold]Summary:[/bold] {successful}/{len(results)} published successfully")


if __name__ == "__main__":
    console.print("\n[yellow]⚠ This is a template script for future use[/yellow]")
    console.print("\nTo use this script:")
    console.print("1. Generate Application Password in WordPress Admin")
    console.print("2. Update configuration in the script")
    console.print("3. Run: python wordpress_publisher.py")
    console.print("\nFor now, focus on testing translations with recipe_translator.py")
