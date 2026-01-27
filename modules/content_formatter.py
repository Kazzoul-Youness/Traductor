"""
Content Formatter Module
Convert HTML to WordPress Gutenberg blocks
"""

import re
from bs4 import BeautifulSoup
from typing import List, Tuple


class ContentFormatter:
    """Convert HTML content to WordPress Gutenberg blocks"""
    
    def __init__(self):
        pass
    
    def html_to_gutenberg(self, html_content: str) -> str:
        """
        Convert HTML to Gutenberg blocks format
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Content formatted as Gutenberg blocks
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        blocks = []
        
        # Process each element
        for element in soup.children:
            if element.name:
                block = self._element_to_block(element)
                if block:
                    blocks.append(block)
        
        return '\n\n'.join(blocks)
    
    def _element_to_block(self, element) -> str:
        """Convert a single HTML element to Gutenberg block"""
        
        tag = element.name
        
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = tag[1]
            text = str(element)
            return f'<!-- wp:heading {{"level":{level}}} -->\n{text}\n<!-- /wp:heading -->'
        
        elif tag == 'p':
            text = str(element)
            return f'<!-- wp:paragraph -->\n{text}\n<!-- /wp:paragraph -->'
        
        elif tag == 'ul':
            text = str(element)
            return f'<!-- wp:list -->\n{text}\n<!-- /wp:list -->'
        
        elif tag == 'ol':
            text = str(element)
            return f'<!-- wp:list {{"ordered":true}} -->\n{text}\n<!-- /wp:list -->'
        
        elif tag == 'blockquote':
            text = str(element)
            return f'<!-- wp:quote -->\n{text}\n<!-- /wp:quote -->'
        
        elif tag == 'table':
            text = str(element)
            return f'<!-- wp:table -->\n<figure class="wp-block-table">{text}</figure>\n<!-- /wp:table -->'
        
        elif tag in ['figure', 'img']:
            return self._image_to_block(element)
        
        elif tag == 'div':
            # Process div contents recursively
            inner_blocks = []
            for child in element.children:
                if child.name:
                    block = self._element_to_block(child)
                    if block:
                        inner_blocks.append(block)
            return '\n\n'.join(inner_blocks)
        
        elif tag == 'hr':
            return '<!-- wp:separator -->\n<hr class="wp-block-separator"/>\n<!-- /wp:separator -->'
        
        else:
            # Generic HTML block
            text = str(element)
            if text.strip():
                return f'<!-- wp:html -->\n{text}\n<!-- /wp:html -->'
        
        return ''
    
    def _image_to_block(self, element) -> str:
        """Convert image element to Gutenberg image block"""
        
        if element.name == 'img':
            src = element.get('src', '')
            alt = element.get('alt', '')
            return f'<!-- wp:image -->\n<figure class="wp-block-image"><img src="{src}" alt="{alt}"/></figure>\n<!-- /wp:image -->'
        
        elif element.name == 'figure':
            img = element.find('img')
            if img:
                src = img.get('src', '')
                alt = img.get('alt', '')
                caption = element.find('figcaption')
                caption_text = str(caption) if caption else ''
                
                return f'<!-- wp:image -->\n<figure class="wp-block-image"><img src="{src}" alt="{alt}"/>{caption_text}</figure>\n<!-- /wp:image -->'
        
        return ''
    
    def split_into_sections(self, html_content: str, num_sections: int = 6) -> List[str]:
        """
        Split content into multiple sections for easier editing
        
        Args:
            html_content: HTML content
            num_sections: Target number of sections
            
        Returns:
            List of HTML sections
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Collect all top-level elements
        elements = [el for el in soup.children if el.name]
        
        if not elements:
            return [html_content]
        
        # Calculate elements per section
        total = len(elements)
        per_section = max(1, total // num_sections)
        
        sections = []
        current_section = []
        
        for i, element in enumerate(elements):
            current_section.append(str(element))
            
            # Start new section at headings or after reaching target size
            is_heading = element.name in ['h2', 'h3']
            reached_target = len(current_section) >= per_section
            
            if (is_heading and len(current_section) > 1) or (reached_target and i < total - 1):
                if is_heading:
                    # Keep heading for next section
                    heading = current_section.pop()
                    sections.append('\n'.join(current_section))
                    current_section = [heading]
                else:
                    sections.append('\n'.join(current_section))
                    current_section = []
        
        # Add remaining elements
        if current_section:
            sections.append('\n'.join(current_section))
        
        return sections
    
    def format_for_wordpress(self, html_content: str, split_sections: bool = True) -> str:
        """
        Format content for WordPress with Gutenberg blocks
        
        Args:
            html_content: Raw HTML content
            split_sections: Whether to add separator blocks between sections
            
        Returns:
            WordPress-ready content
        """
        # Clean the HTML first
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove any wrapper divs that might cause issues
        # Find the actual content
        content_div = soup.find('div', class_='entry-content')
        if content_div:
            soup = content_div
        
        blocks = []
        
        for element in soup.children:
            if not element.name:
                continue
            
            block = self._element_to_block(element)
            if block:
                blocks.append(block)
        
        # Join with double newlines
        result = '\n\n'.join(blocks)
        
        # If no blocks were created, wrap in HTML block
        if not blocks:
            result = f'<!-- wp:html -->\n{html_content}\n<!-- /wp:html -->'
        
        return result
    
    def create_placeholder_image_block(self, position: int = 1) -> str:
        """Create a placeholder block for adding custom images"""
        return f'''<!-- wp:image -->
<figure class="wp-block-image">
<!-- 🖼️ AJOUTER VOTRE IMAGE ICI - Position {position} -->
</figure>
<!-- /wp:image -->'''
    
    def add_image_placeholders(self, content: str, num_placeholders: int = 3) -> str:
        """Add placeholder blocks for custom images throughout content"""
        
        # Split into sections
        sections = self.split_into_sections(content, num_sections=num_placeholders + 1)
        
        result_parts = []
        for i, section in enumerate(sections):
            result_parts.append(section)
            
            # Add image placeholder between sections (not after last)
            if i < len(sections) - 1 and i < num_placeholders:
                placeholder = self.create_placeholder_image_block(i + 1)
                result_parts.append(f'\n\n{placeholder}\n\n')
        
        return ''.join(result_parts)
