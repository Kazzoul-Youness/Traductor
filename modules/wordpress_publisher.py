"""
WordPress Publisher Module
Publish translated content to WordPress via REST API
"""

import httpx
import base64
from typing import Dict, List, Optional
from urllib.parse import urlparse
import re


class WordPressPublisher:
    """Publish translated content to WordPress via REST API"""
    
    def __init__(self, site_url: str, username: str, app_password: str):
        """
        Initialize WordPress publisher
        
        Args:
            site_url: WordPress site URL (e.g., https://dietaypeso.com)
            username: WordPress username
            app_password: Application password (generated in WP admin)
        """
        self.site_url = site_url.rstrip('/')
        self.username = username
        self.app_password = app_password
        self.api_base = f"{self.site_url}/wp-json/wp/v2"
        
        # Create auth header
        credentials = f"{username}:{app_password}"
        self.auth_header = base64.b64encode(credentials.encode()).decode()
        
        self.headers = {
            "Authorization": f"Basic {self.auth_header}",
            "Content-Type": "application/json",
            "User-Agent": "RecipeTranslator/1.0 (WordPress Publisher)"
        }
    
    def test_connection(self) -> Dict:
        """Test the WordPress connection"""
        try:
            with httpx.Client(timeout=15.0) as client:
                # Test authenticated access
                response = client.get(
                    f"{self.api_base}/users/me",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    user = response.json()
                    return {
                        'success': True,
                        'user': user.get('name', 'Unknown'),
                        'site': self.site_url
                    }
                else:
                    return {
                        'success': False,
                        'error': f"HTTP {response.status_code}"
                    }
                    
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def publish_post(
        self, 
        title: str, 
        content: str, 
        slug: str,
        excerpt: str = "",
        featured_image_url: str = None,
        content_images: List[str] = None,
        categories: List[int] = None,
        tags: List[int] = None,
        status: str = 'draft',
        meta: Dict = None,
        # Rank Math SEO fields
        focus_keyword: str = None,
        seo_title: str = None,
        seo_description: str = None
    ) -> Dict:
        """
        Publish a new post to WordPress with Rank Math SEO support
        
        Args:
            title: Post title
            content: Post content (HTML)
            slug: URL slug
            excerpt: Post excerpt
            featured_image_url: URL of featured image to upload
            content_images: List of image URLs in content to upload
            categories: List of category IDs
            tags: List of tag IDs
            status: 'draft', 'publish', 'pending', 'private'
            meta: Additional meta fields
            focus_keyword: Rank Math focus keyword
            seo_title: Rank Math SEO title
            seo_description: Rank Math meta description
            
        Returns:
            Response dict with post ID and URL
        """
        try:
            with httpx.Client(timeout=120.0) as client:
                
                # Upload and replace content images
                if content_images:
                    content = self._process_content_images(client, content, content_images)
                
                # Prepare post data
                data = {
                    'title': title,
                    'content': content,
                    'slug': slug,
                    'status': status
                }
                
                if excerpt:
                    data['excerpt'] = excerpt
                
                if categories:
                    data['categories'] = categories
                
                if tags:
                    data['tags'] = tags
                
                # Rank Math SEO meta fields
                rank_math_meta = {}
                if focus_keyword:
                    rank_math_meta['rank_math_focus_keyword'] = focus_keyword
                if seo_title:
                    rank_math_meta['rank_math_title'] = seo_title
                if seo_description:
                    rank_math_meta['rank_math_description'] = seo_description
                
                if rank_math_meta:
                    data['meta'] = {**(meta or {}), **rank_math_meta}
                elif meta:
                    data['meta'] = meta
                
                # Upload featured image if provided
                if featured_image_url:
                    media_result = self._upload_image_from_url(client, featured_image_url)
                    if media_result.get('success'):
                        data['featured_media'] = media_result['media_id']
                
                # Create post
                response = client.post(
                    f"{self.api_base}/posts",
                    headers=self.headers,
                    json=data
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    return {
                        'success': True,
                        'post_id': result['id'],
                        'post_url': result['link'],
                        'edit_url': f"{self.site_url}/wp-admin/post.php?post={result['id']}&action=edit",
                        'status': result['status']
                    }
                else:
                    return {
                        'success': False,
                        'error': f"HTTP {response.status_code}: {response.text[:500]}"
                    }
                    
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _process_content_images(self, client: httpx.Client, content: str, image_urls: List[str]) -> str:
        """Upload images from content and replace URLs with new WordPress URLs"""
        
        for old_url in image_urls:
            if not old_url:
                continue
                
            # Skip if already on target domain
            if self.site_url.replace('https://', '').replace('http://', '') in old_url:
                continue
            
            # Upload image
            result = self._upload_image_from_url(client, old_url)
            
            if result.get('success') and result.get('media_url'):
                # Replace old URL with new WordPress URL
                content = content.replace(old_url, result['media_url'])
        
        return content
    
    def _upload_image_from_url(self, client: httpx.Client, image_url: str) -> Dict:
        """Upload image from URL to WordPress media library"""
        try:
            # Download image
            img_response = client.get(image_url, timeout=30.0)
            img_response.raise_for_status()
            
            # Get filename from URL
            parsed = urlparse(image_url)
            filename = parsed.path.split('/')[-1] or 'image.jpg'
            
            # Determine content type
            content_type = img_response.headers.get('content-type', 'image/jpeg')
            
            # Upload to WordPress
            upload_headers = {
                "Authorization": f"Basic {self.auth_header}",
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": content_type
            }
            
            response = client.post(
                f"{self.api_base}/media",
                headers=upload_headers,
                content=img_response.content
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                return {
                    'success': True,
                    'media_id': result['id'],
                    'media_url': result.get('source_url', '')
                }
            else:
                return {'success': False, 'error': f"Upload failed: {response.status_code}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def upload_image(self, image_path: str, alt_text: str = "") -> Dict:
        """Upload a local image file to WordPress"""
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            filename = image_path.split('/')[-1].split('\\')[-1]
            
            # Determine content type
            ext = filename.lower().split('.')[-1]
            content_types = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif',
                'webp': 'image/webp'
            }
            content_type = content_types.get(ext, 'image/jpeg')
            
            upload_headers = {
                "Authorization": f"Basic {self.auth_header}",
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": content_type
            }
            
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.api_base}/media",
                    headers=upload_headers,
                    content=image_data
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    
                    # Update alt text if provided
                    if alt_text:
                        client.post(
                            f"{self.api_base}/media/{result['id']}",
                            headers=self.headers,
                            json={'alt_text': alt_text}
                        )
                    
                    return {
                        'success': True,
                        'media_id': result['id'],
                        'media_url': result.get('source_url', '')
                    }
                else:
                    return {'success': False, 'error': f"Upload failed: {response.status_code}"}
                    
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_categories(self) -> List[Dict]:
        """Get all categories from WordPress"""
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(
                    f"{self.api_base}/categories",
                    headers=self.headers,
                    params={'per_page': 100}
                )
                response.raise_for_status()
                
                return [
                    {'id': cat['id'], 'name': cat['name'], 'slug': cat['slug']}
                    for cat in response.json()
                ]
                
        except Exception as e:
            return []
    
    def get_tags(self) -> List[Dict]:
        """Get all tags from WordPress"""
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(
                    f"{self.api_base}/tags",
                    headers=self.headers,
                    params={'per_page': 100}
                )
                response.raise_for_status()
                
                return [
                    {'id': tag['id'], 'name': tag['name'], 'slug': tag['slug']}
                    for tag in response.json()
                ]
                
        except Exception as e:
            return []
    
    def create_category(self, name: str, slug: str = None, parent: int = 0) -> Dict:
        """Create a new category"""
        try:
            data = {
                'name': name,
                'slug': slug or self._slugify(name),
                'parent': parent
            }
            
            with httpx.Client(timeout=15.0) as client:
                response = client.post(
                    f"{self.api_base}/categories",
                    headers=self.headers,
                    json=data
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    return {'success': True, 'category_id': result['id']}
                else:
                    return {'success': False, 'error': response.text}
                    
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_tag(self, name: str, slug: str = None) -> Dict:
        """Create a new tag"""
        try:
            data = {
                'name': name,
                'slug': slug or self._slugify(name)
            }
            
            with httpx.Client(timeout=15.0) as client:
                response = client.post(
                    f"{self.api_base}/tags",
                    headers=self.headers,
                    json=data
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    return {'success': True, 'tag_id': result['id']}
                else:
                    return {'success': False, 'error': response.text}
                    
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_post_by_slug(self, slug: str) -> Optional[Dict]:
        """Check if a post with this slug already exists"""
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(
                    f"{self.api_base}/posts",
                    headers=self.headers,
                    params={'slug': slug}
                )
                response.raise_for_status()
                
                posts = response.json()
                if posts:
                    return posts[0]
                return None
                
        except Exception as e:
            return None
    
    def update_post(self, post_id: int, **kwargs) -> Dict:
        """Update an existing post"""
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.api_base}/posts/{post_id}",
                    headers=self.headers,
                    json=kwargs
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        'success': True,
                        'post_id': result['id'],
                        'post_url': result['link']
                    }
                else:
                    return {'success': False, 'error': response.text}
                    
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug"""
        # Lowercase
        slug = text.lower()
        
        # Replace accented characters
        accents = {
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'à': 'a', 'â': 'a', 'ä': 'a', 'á': 'a',
            'ô': 'o', 'ö': 'o', 'ó': 'o',
            'û': 'u', 'ü': 'u', 'ú': 'u',
            'î': 'i', 'ï': 'i', 'í': 'i',
            'ç': 'c', 'ñ': 'n', 'ß': 'ss'
        }
        
        for accented, plain in accents.items():
            slug = slug.replace(accented, plain)
        
        # Remove special characters
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        
        # Replace spaces with hyphens
        slug = re.sub(r'\s+', '-', slug)
        
        # Remove multiple hyphens
        slug = re.sub(r'-+', '-', slug)
        
        return slug.strip('-')
