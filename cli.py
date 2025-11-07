"""
Interactive CLI for managing LinkedIn posts
"""
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from typing import List, Dict
from trending_finder import TrendingFinder
from post_generator import PostGenerator
from linkedin_poster import LinkedInPoster

console = Console()


class LinkedInAutoPosterCLI:
    """Interactive CLI for LinkedIn Auto-Posting Agent"""
    
    def __init__(self):
        self.trending_finder = TrendingFinder()
        self.post_generator = PostGenerator()
        self.linkedin_poster = None
        self.drafts = []
    
    def display_welcome(self):
        """Display welcome message"""
        welcome_text = """
🚀 LinkedIn Auto-Posting Agent

This agent helps you:
• Find trending topics
• Generate engaging post drafts
• Review and edit before posting
• Automatically publish to LinkedIn

All without paid APIs! 🎉
        """
        console.print(Panel(welcome_text, title="Welcome", border_style="green"))
    
    def find_trending_topics(self):
        """Find and display trending topics"""
        console.print("\n[cyan]🔍 Finding trending topics...[/cyan]")
        
        topics = self.trending_finder.get_trending_topics()
        
        if not topics:
            console.print("[red]❌ No trending topics found. Please try again later.[/red]")
            return []
        
        # Display topics in a table
        table = Table(title="📊 Trending Topics Found", show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("Title", style="cyan")
        table.add_column("Source", style="green")
        
        for i, topic in enumerate(topics, 1):
            title = topic.get("title", "")[:60] + "..." if len(topic.get("title", "")) > 60 else topic.get("title", "")
            table.add_row(str(i), title, topic.get("source", "unknown"))
        
        console.print(table)
        return topics
    
    def generate_drafts(self, topics: List[Dict]):
        """Generate post drafts from topics"""
        console.print("\n[cyan]✍️  Generating post drafts...[/cyan]")
        
        if not topics:
            console.print("[red]❌ No topics available to generate drafts from.[/red]")
            return
        
        # Generate drafts
        self.drafts = self.post_generator.generate_multiple_drafts(topics, count=len(topics))
        
        console.print(f"[green]✅ Generated {len(self.drafts)} draft(s)[/green]\n")
    
    def display_drafts(self):
        """Display all drafts"""
        if not self.drafts:
            console.print("[yellow]⚠️  No drafts available. Please generate drafts first.[/yellow]")
            return
        
        for draft in self.drafts:
            content = draft["content"]
            length = draft["length"]
            
            # Create a panel for each draft
            panel_content = f"[bold]{draft['topic']}[/bold]\n\n{content}\n\n[dim]Length: {length} characters[/dim]"
            console.print(Panel(panel_content, title=f"Draft #{draft['id']}", border_style="blue"))
            console.print()
    
    def edit_draft(self, draft_id: int) -> bool:
        """Edit a specific draft"""
        draft = next((d for d in self.drafts if d["id"] == draft_id), None)
        
        if not draft:
            console.print(f"[red]❌ Draft #{draft_id} not found.[/red]")
            return False
        
        console.print(f"\n[cyan]Editing Draft #{draft_id}[/cyan]")
        console.print(Panel(draft["content"], title="Current Content", border_style="yellow"))
        
        new_content = Prompt.ask("\nEnter new content (or press Enter to keep current)", default=draft["content"])
        
        draft["content"] = new_content
        draft["length"] = len(new_content)
        
        console.print("[green]✅ Draft updated![/green]")
        return True
    
    def select_draft_to_post(self) -> Dict:
        """Let user select a draft to post"""
        if not self.drafts:
            console.print("[red]❌ No drafts available.[/red]")
            return None
        
        # Display summary table
        table = Table(title="📝 Available Drafts", show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("Topic", style="cyan", width=40)
        table.add_column("Length", style="green")
        
        for draft in self.drafts:
            topic = draft["topic"][:37] + "..." if len(draft["topic"]) > 40 else draft["topic"]
            table.add_row(str(draft["id"]), topic, str(draft["length"]))
        
        console.print(table)
        
        # Get user selection
        try:
            choice = int(Prompt.ask("\nSelect draft number to post", choices=[str(d["id"]) for d in self.drafts]))
            selected_draft = next((d for d in self.drafts if d["id"] == choice), None)
            
            if selected_draft:
                return selected_draft
            else:
                console.print("[red]❌ Invalid selection.[/red]")
                return None
        except ValueError:
            console.print("[red]❌ Invalid input.[/red]")
            return None
    
    def post_to_linkedin(self, draft: Dict):
        """Post draft to LinkedIn"""
        console.print("\n[cyan]📤 Posting to LinkedIn...[/cyan]")
        
        # Show final preview
        console.print(Panel(draft["content"], title="Final Preview", border_style="green"))
        
        if not Confirm.ask("\nDo you want to proceed with posting?"):
            console.print("[yellow]Posting cancelled.[/yellow]")
            return
        
        try:
            # Initialize LinkedIn poster
            self.linkedin_poster = LinkedInPoster()
            self.linkedin_poster.setup_driver()
            
            # Login
            if not self.linkedin_poster.login():
                console.print("[red]❌ Failed to login. Please check your credentials.[/red]")
                return
            
            # Post content
            if self.linkedin_poster.post_content(draft["content"]):
                console.print("[green]✅ Successfully posted to LinkedIn![/green]")
            else:
                console.print("[red]❌ Failed to post. Please try again or post manually.[/red]")
            
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
        finally:
            if self.linkedin_poster:
                self.linkedin_poster.close()
    
    def run(self):
        """Main CLI loop"""
        self.display_welcome()
        
        while True:
            console.print("\n[bold]📋 Main Menu[/bold]")
            console.print("1. Find trending topics")
            console.print("2. Generate post drafts")
            console.print("3. View all drafts")
            console.print("4. Edit a draft")
            console.print("5. Post to LinkedIn")
            console.print("6. Exit")
            
            choice = Prompt.ask("\nSelect an option", choices=["1", "2", "3", "4", "5", "6"])
            
            if choice == "1":
                topics = self.find_trending_topics()
                if topics and Confirm.ask("\nGenerate drafts from these topics?"):
                    self.generate_drafts(topics)
            
            elif choice == "2":
                if not self.drafts:
                    topics = self.find_trending_topics()
                    if topics:
                        self.generate_drafts(topics)
                else:
                    console.print("[yellow]⚠️  Drafts already exist. Use option 1 to find new topics.[/yellow]")
            
            elif choice == "3":
                self.display_drafts()
            
            elif choice == "4":
                if self.drafts:
                    try:
                        draft_id = int(Prompt.ask("Enter draft number to edit", choices=[str(d["id"]) for d in self.drafts]))
                        self.edit_draft(draft_id)
                    except ValueError:
                        console.print("[red]❌ Invalid input.[/red]")
                else:
                    console.print("[yellow]⚠️  No drafts available.[/yellow]")
            
            elif choice == "5":
                draft = self.select_draft_to_post()
                if draft:
                    self.post_to_linkedin(draft)
            
            elif choice == "6":
                console.print("\n[green]👋 Goodbye![/green]")
                break


if __name__ == "__main__":
    cli = LinkedInAutoPosterCLI()
    cli.run()

