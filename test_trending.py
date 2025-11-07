"""
Quick test script for trending topics functionality
"""
from trending_finder import TrendingFinder
from rich.console import Console
from rich.table import Table

console = Console()

def test_trending_topics():
    """Test the trending topics finder"""
    console.print("\n[bold cyan]🔍 Testing Trending Topics Finder...[/bold cyan]\n")
    
    finder = TrendingFinder()
    
    # Test Reddit trending
    console.print("[yellow]Testing Reddit trending...[/yellow]")
    reddit_topics = finder.get_reddit_trending(limit=3)
    console.print(f"[green]✅ Found {len(reddit_topics)} Reddit topics[/green]\n")
    
    # Test RSS trending
    console.print("[yellow]Testing RSS feeds...[/yellow]")
    rss_topics = finder.get_rss_trending(limit=3)
    console.print(f"[green]✅ Found {len(rss_topics)} RSS topics[/green]\n")
    
    # Test combined
    console.print("[yellow]Testing combined trending topics...[/yellow]")
    all_topics = finder.get_trending_topics(limit=5)
    console.print(f"[green]✅ Found {len(all_topics)} total topics[/green]\n")
    
    # Display results
    if all_topics:
        table = Table(title="📊 Trending Topics Found", show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("Title", style="cyan", width=60)
        table.add_column("Source", style="green", width=10)
        table.add_column("URL", style="blue", width=40)
        
        for i, topic in enumerate(all_topics, 1):
            title = topic.get("title", "")[:57] + "..." if len(topic.get("title", "")) > 60 else topic.get("title", "")
            url = topic.get("url", "")[:37] + "..." if len(topic.get("url", "")) > 40 else topic.get("url", "")
            table.add_row(str(i), title, topic.get("source", "unknown"), url)
        
        console.print(table)
        console.print(f"\n[bold green]✅ Successfully fetched {len(all_topics)} trending topics![/bold green]")
    else:
        console.print("[red]❌ No topics found. Please check your internet connection.[/red]")

if __name__ == "__main__":
    test_trending_topics()

