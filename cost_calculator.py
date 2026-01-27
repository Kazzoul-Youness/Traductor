#!/usr/bin/env python3
"""
Cost Calculator
Estimate API costs for translation projects
"""

from modules import RecipeTranslator
from rich.console import Console
from rich.table import Table

console = Console()

def calculate_costs():
    """Calculate estimated costs for different scenarios"""
    
    console.print("\n[bold cyan]💰 Translation Cost Calculator[/bold cyan]\n")
    
    # Initialize translator (no API key needed for cost estimation)
    translator = RecipeTranslator(api_key="dummy")
    
    # Scenarios
    scenarios = [
        {
            'name': 'Test batch (10 recipes, 1 langue)',
            'recipes': 10,
            'chars_per_recipe': 2000,
            'languages': 1
        },
        {
            'name': 'Petit site (100 recipes, 4 langues)',
            'recipes': 100,
            'chars_per_recipe': 2000,
            'languages': 4
        },
        {
            'name': 'Site moyen (500 recipes, 4 langues)',
            'recipes': 500,
            'chars_per_recipe': 2000,
            'languages': 4
        },
        {
            'name': 'Grand site (1000 recipes, 4 langues)',
            'recipes': 1000,
            'chars_per_recipe': 2500,
            'languages': 4
        },
        {
            'name': 'Maintenance mensuelle (50 nouvelles)',
            'recipes': 50,
            'chars_per_recipe': 2000,
            'languages': 4
        }
    ]
    
    table = Table(title="Estimation des coûts API Claude")
    table.add_column("Scénario", style="cyan")
    table.add_column("Recettes", style="yellow", justify="right")
    table.add_column("Langues", style="yellow", justify="right")
    table.add_column("Total trad.", style="yellow", justify="right")
    table.add_column("Coût total", style="green", justify="right")
    table.add_column("Par recette", style="blue", justify="right")
    
    for scenario in scenarios:
        num_recipes = scenario['recipes']
        num_langs = scenario['languages']
        chars = scenario['chars_per_recipe']
        
        # Calculate for one recipe in all languages
        cost_data = translator.estimate_cost(chars, num_langs)
        
        # Total cost for all recipes
        total_cost = cost_data['estimated_cost_usd'] * num_recipes
        total_translations = num_recipes * num_langs
        cost_per_recipe = total_cost / num_recipes
        
        table.add_row(
            scenario['name'],
            str(num_recipes),
            str(num_langs),
            str(total_translations),
            f"${total_cost:.2f}",
            f"${cost_per_recipe:.3f}"
        )
    
    console.print(table)
    
    # Additional info
    console.print("\n[bold]Notes:[/bold]")
    console.print("• Prix Claude Sonnet 4: $3/M input tokens, $15/M output tokens")
    console.print("• Estimation basée sur ~2000 caractères par recette")
    console.print("• Coûts réels peuvent varier selon la longueur du contenu")
    console.print("• Coût par traduction: ~$0.015-0.025")
    
    console.print("\n[bold green]Conclusion:[/bold green]")
    console.print("Pour 500 recettes × 4 langues = 2000 traductions")
    console.print("Coût estimé: [bold]~$30-40[/bold] (one-time)")
    console.print("Maintenance mensuelle (50 nouvelles): [bold]~$3-5/mois[/bold]")
    
    console.print("\n[yellow]💡 Tip:[/yellow] Tester d'abord avec 10-20 recettes pour valider la qualité!")


if __name__ == "__main__":
    calculate_costs()
