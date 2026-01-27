#!/usr/bin/env python3
"""
AllMuffins Recipe Translator CLI
Test script pour valider la logique de traduction avant production
"""

import argparse
import json
import os
import sys

# Fix Windows console encoding
if sys.platform == "win32":
    os.system("chcp 65001 > nul 2>&1")
    sys.stdout.reconfigure(encoding='utf-8')

from modules.sitemap_parser import SitemapParser
from modules.recipe_scraper import RecipeScraper
from modules.translator import RecipeTranslator
from modules.link_adapter import LinkAdapter
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

console = Console(force_terminal=True)

def main():
    parser = argparse.ArgumentParser(description='AllMuffins Recipe Translator')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Command: list
    list_parser = subparsers.add_parser('list', help='List all recipes from sitemap')
    list_parser.add_argument('--limit', type=int, default=10, help='Number of recipes to show')
    
    # Command: translate
    translate_parser = subparsers.add_parser('translate', help='Translate a recipe')
    translate_parser.add_argument('url', help='Recipe URL to translate')
    translate_parser.add_argument('--langs', nargs='+', default=['fr', 'es'], 
                                  help='Target languages (fr, es, de, sv)')
    translate_parser.add_argument('--api-key', default=os.environ.get('OPENROUTER_API_KEY'), 
                                  help='OpenRouter API key (or set OPENROUTER_API_KEY env var)')
    translate_parser.add_argument('--save', action='store_true', help='Save translation to JSON')
    
    # Command: batch
    batch_parser = subparsers.add_parser('batch', help='Translate multiple recipes')
    batch_parser.add_argument('--count', type=int, default=5, help='Number of recipes to translate')
    batch_parser.add_argument('--langs', nargs='+', default=['fr'], help='Target languages')
    batch_parser.add_argument('--api-key', default=os.environ.get('OPENROUTER_API_KEY'),
                              help='OpenRouter API key (or set OPENROUTER_API_KEY env var)')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_recipes(args.limit)
    elif args.command == 'translate':
        if not args.api_key:
            console.print("[red]✗ Error: API key required![/red]")
            console.print("  Set OPENROUTER_API_KEY env var or use --api-key")
            sys.exit(1)
        translate_recipe(args.url, args.langs, args.api_key, args.save)
    elif args.command == 'batch':
        if not args.api_key:
            console.print("[red]✗ Error: API key required![/red]")
            console.print("  Set OPENROUTER_API_KEY env var or use --api-key")
            sys.exit(1)
        batch_translate(args.count, args.langs, args.api_key)
    else:
        parser.print_help()


def list_recipes(limit=10):
    """List recipes from sitemap"""
    console.print("\n[bold cyan]🔍 Fetching recipes from sitemap...[/bold cyan]\n")
    
    parser = SitemapParser('https://allmuffins.com/sitemap_index.xml')
    recipes = parser.get_all_recipes(limit=limit)
    
    table = Table(title=f"Found {len(recipes)} recipes")
    table.add_column("№", style="cyan", width=5)
    table.add_column("Recipe URL", style="green")
    table.add_column("Last Modified", style="yellow")
    
    for idx, recipe in enumerate(recipes, 1):
        table.add_row(
            str(idx),
            recipe['url'],
            recipe.get('lastmod', 'N/A')
        )
    
    console.print(table)
    console.print(f"\n[green]✓[/green] Total: {len(recipes)} recipes\n")


def translate_recipe(url, target_langs, api_key, save=False):
    """Translate a single recipe"""
    console.print(f"\n[bold cyan]🌍 Translating: {url}[/bold cyan]\n")
    
    # Step 1: Scrape recipe content
    console.print("[yellow]Step 1:[/yellow] Scraping recipe content...")
    scraper = RecipeScraper()
    recipe_data = scraper.scrape(url)
    
    if not recipe_data:
        console.print("[red]✗ Failed to scrape recipe![/red]")
        return
    
    console.print(f"[green]✓[/green] Scraped: {recipe_data['title']}")
    console.print(f"   Content length: {len(recipe_data['content'])} chars")
    console.print(f"   Internal links: {len(recipe_data['internal_links'])}")
    
    # Step 2: Translate
    translator = RecipeTranslator(api_key)
    link_adapter = LinkAdapter()
    
    results = {}
    
    for lang in target_langs:
        console.print(f"\n[yellow]Step 2:[/yellow] Translating to {lang.upper()}...")
        
        with Progress() as progress:
            task = progress.add_task(f"[cyan]Translating to {lang}...", total=100)
            
            # Translate content
            translated = translator.translate(
                title=recipe_data['title'],
                content=recipe_data['content'],
                target_lang=lang
            )
            progress.update(task, advance=50)
            
            # Adapt internal links
            domain_map = {
                'fr': 'jelorec.com',
                'es': 'dietaypeso.com',
                'de': 'allemuffins.de',
                'sv': 'allamuffins.se',
                'en': 'allmuffins.com'
            }
            
            adapted_content = link_adapter.adapt_links(
                translated['content'],
                target_domain=domain_map.get(lang, 'allmuffins.com'),
                lang_code=lang
            )
            progress.update(task, advance=50)
        
        results[lang] = {
            'title': translated['title'],
            'content': adapted_content,
            'word_count': translated['word_count'],
            'target_url': f"https://{domain_map.get(lang)}/{translated['slug']}"
        }
        
        console.print(f"[green]✓[/green] Translated to {lang.upper()}")
        console.print(f"   Title: {translated['title']}")
        console.print(f"   Slug: {translated['slug']}")
        console.print(f"   Words: {translated['word_count']}")
    
    # Step 3: Display comparison
    console.print("\n[bold cyan]📊 Translation Summary[/bold cyan]\n")
    
    comparison_table = Table()
    comparison_table.add_column("Language", style="cyan")
    comparison_table.add_column("Title", style="green")
    comparison_table.add_column("Word Count", style="yellow")
    comparison_table.add_column("Target URL", style="blue")
    
    # Original
    comparison_table.add_row(
        "EN (original)",
        recipe_data['title'],
        str(len(recipe_data['content'].split())),
        url
    )
    
    # Translations
    for lang, data in results.items():
        comparison_table.add_row(
            lang.upper(),
            data['title'],
            str(data['word_count']),
            data['target_url']
        )
    
    console.print(comparison_table)
    
    # Step 4: Save if requested
    if save:
        filename = f"translation_{recipe_data['title'].lower().replace(' ', '_')[:30]}.json"
        output_data = {
            'original': recipe_data,
            'translations': results,
            'timestamp': str(json.dumps(None))  # Will be current time
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        console.print(f"\n[green]✓[/green] Saved to: {filename}")
    
    console.print("\n[bold green]✓ Translation complete![/bold green]\n")


def batch_translate(count, target_langs, api_key):
    """Translate multiple recipes"""
    console.print(f"\n[bold cyan]🚀 Batch translating {count} recipes to {', '.join(target_langs)}[/bold cyan]\n")
    
    # Get recipes
    parser = SitemapParser('https://allmuffins.com/sitemap_index.xml')
    recipes = parser.get_all_recipes(limit=count)
    
    console.print(f"[green]✓[/green] Found {len(recipes)} recipes to translate\n")
    
    # Translate each
    for idx, recipe in enumerate(recipes, 1):
        console.print(f"\n[bold]═══ Recipe {idx}/{len(recipes)} ═══[/bold]")
        translate_recipe(recipe['url'], target_langs, api_key, save=True)
    
    console.print("\n[bold green]🎉 Batch translation complete![/bold green]")
    console.print(f"[green]✓[/green] Translated {len(recipes)} recipes to {len(target_langs)} languages")
    console.print(f"[green]✓[/green] Total translations: {len(recipes) * len(target_langs)}\n")


if __name__ == "__main__":
    main()
