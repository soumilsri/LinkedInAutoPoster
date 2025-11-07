"""
Test the full workflow: Find topics -> Generate drafts
"""
from trending_finder import TrendingFinder
from post_generator import PostGenerator
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def test_full_workflow():
    """Test the complete workflow"""
    console.print("\n[bold cyan]🚀 Testing Full Workflow: Trending Topics → Post Generation[/bold cyan]\n")
    
    # Step 1: Find trending topics
    console.print("[yellow]Step 1: Finding trending topics...[/yellow]")
    finder = TrendingFinder()
    topics = finder.get_trending_topics(limit=3)
    
    if not topics:
        console.print("[red]❌ No topics found. Exiting.[/red]")
        return
    
    console.print(f"[green]✅ Found {len(topics)} topics[/green]\n")
    
    # Display topics
    table = Table(title="📊 Trending Topics", show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=3)
    table.add_column("Title", style="cyan")
    table.add_column("Source", style="green")
    console.print(table)
    
    for i, topic in enumerate(topics, 1):
        title = topic.get("title", "")[:60] + "..." if len(topic.get("title", "")) > 60 else topic.get("title", "")
        table.add_row(str(i), title, topic.get("source", "unknown"))
    
    console.print(table)
    console.print()
    
    # Step 2: Generate post drafts
    console.print("[yellow]Step 2: Generating post drafts...[/yellow]")
    generator = PostGenerator()
    drafts = generator.generate_multiple_drafts(topics, count=len(topics))
    console.print(f"[green]✅ Generated {len(drafts)} draft(s)[/green]\n")
    
    # Display drafts
    for draft in drafts:
        console.print(Panel(
            f"[bold]{draft['topic']}[/bold]\n\n{draft['content']}\n\n[dim]Length: {draft['length']} characters[/dim]",
            title=f"📝 Draft #{draft['id']}",
            border_style="blue"
        ))
        console.print()
    
    console.print("[bold green]✅ Full workflow test complete![/bold green]")
    console.print("[dim]You can now use the main app (python main.py) to edit and post these drafts.[/dim]\n")

if __name__ == "__main__":
    test_full_workflow()

