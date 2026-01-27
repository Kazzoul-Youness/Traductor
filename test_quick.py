#!/usr/bin/env python3
"""
Quick Test Script
Test the translation pipeline without API calls
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == "win32":
    os.system("chcp 65001 > nul 2>&1")
    sys.stdout.reconfigure(encoding='utf-8')

from modules import SitemapParser, RecipeScraper, LinkAdapter
from rich.console import Console

console = Console(force_terminal=True)

def test_sitemap_parser():
    """Test sitemap parsing"""
    console.print("\n[bold cyan]Testing Sitemap Parser...[/bold cyan]")
    
    try:
        parser = SitemapParser('https://allmuffins.com/sitemap_index.xml')
        recipes = parser.get_all_recipes(limit=3)
        
        console.print(f"[green]✓[/green] Found {len(recipes)} recipes")
        for i, recipe in enumerate(recipes, 1):
            console.print(f"  {i}. {recipe['url']}")
        
        return True
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        return False


def test_recipe_scraper():
    """Test recipe scraping"""
    console.print("\n[bold cyan]Testing Recipe Scraper...[/bold cyan]")
    
    try:
        scraper = RecipeScraper()
        
        # Get first recipe from sitemap
        parser = SitemapParser('https://allmuffins.com/sitemap_index.xml')
        recipes = parser.get_all_recipes(limit=1)
        
        if not recipes:
            console.print("[yellow]⚠[/yellow] No recipes found in sitemap")
            return False
        
        url = recipes[0]['url']
        console.print(f"Testing with: {url}")
        
        recipe = scraper.scrape(url)
        
        if recipe:
            console.print(f"[green]✓[/green] Scraped successfully")
            console.print(f"  Title: {recipe['title']}")
            console.print(f"  Content length: {len(recipe['content'])} chars")
            console.print(f"  Images: {len(recipe['images'])}")
            console.print(f"  Internal links: {len(recipe['internal_links'])}")
            return True
        else:
            console.print("[red]✗[/red] Failed to scrape")
            return False
            
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        return False


def test_link_adapter():
    """Test link adaptation"""
    console.print("\n[bold cyan]Testing Link Adapter...[/bold cyan]")
    
    try:
        adapter = LinkAdapter()
        
        # Test content with links
        test_content = """
        Check out our other recipes:
        <a href="https://allmuffins.com/chocolate-muffins">Chocolate Muffins</a>
        <a href="https://allmuffins.com/blueberry-muffins">Blueberry Muffins</a>
        """
        
        # Adapt to French
        adapted = adapter.adapt_links(test_content, 'tousmuffins.com', 'fr')
        
        console.print(f"[green]✓[/green] Links adapted")
        console.print(f"  Original: allmuffins.com/chocolate-muffins")
        console.print(f"  Adapted:  tousmuffins.com/chocolat-muffins")
        
        # Extract internal links
        links = adapter.extract_internal_links(test_content)
        console.print(f"  Found {len(links)} internal links")
        
        return True
        
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        return False


def main():
    console.print("\n[bold]🧪 AllMuffins Translator - Quick Tests[/bold]\n")
    
    results = []
    
    # Test 1: Sitemap Parser
    results.append(("Sitemap Parser", test_sitemap_parser()))
    
    # Test 2: Recipe Scraper
    results.append(("Recipe Scraper", test_recipe_scraper()))
    
    # Test 3: Link Adapter
    results.append(("Link Adapter", test_link_adapter()))
    
    # Summary
    console.print("\n[bold cyan]Test Summary[/bold cyan]")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[green]✓ PASS[/green]" if result else "[red]✗ FAIL[/red]"
        console.print(f"  {status} - {name}")
    
    console.print(f"\n[bold]Results: {passed}/{total} tests passed[/bold]")
    
    if passed == total:
        console.print("[bold green]All tests passed! ✓[/bold green]")
        console.print("\n[yellow]Next step:[/yellow] Run with your OpenRouter API key:")
        console.print("  python recipe_translator.py translate <URL> --api-key YOUR_OPENROUTER_KEY")
    else:
        console.print("[bold red]Some tests failed![/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
