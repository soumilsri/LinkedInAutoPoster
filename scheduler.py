"""
Scheduler module for automated LinkedIn posting
"""
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from threading import Thread
import schedule
from trending_finder import TrendingFinder
from post_generator import PostGenerator
from linkedin_poster import LinkedInPoster
import config


class PostScheduler:
    """Manages scheduled LinkedIn posts"""
    
    def __init__(self):
        self.scheduled_posts_file = "scheduled_posts.json"
        self.scheduled_posts = self.load_scheduled_posts()
        self.running = False
        self.scheduler_thread = None
        
    def load_scheduled_posts(self) -> List[Dict]:
        """Load scheduled posts from file"""
        if os.path.exists(self.scheduled_posts_file):
            try:
                with open(self.scheduled_posts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_scheduled_posts(self):
        """Save scheduled posts to file"""
        try:
            with open(self.scheduled_posts_file, 'w', encoding='utf-8') as f:
                json.dump(self.scheduled_posts, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error saving scheduled posts: {e}")
    
    def add_scheduled_post(self, post_content: str, schedule_time: str, topic: str = "", use_llm: bool = False) -> bool:
        """Add a post to the schedule
        
        Args:
            post_content: The post content to publish
            schedule_time: Time in format "HH:MM" (24-hour) or "YYYY-MM-DD HH:MM"
            topic: Optional topic description
            use_llm: Whether to use LLM for generation (if post_content is empty)
        """
        try:
            # Parse schedule time
            if len(schedule_time) == 5:  # HH:MM format - schedule for today or tomorrow
                hour, minute = map(int, schedule_time.split(':'))
                now = datetime.now()
                scheduled_datetime = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # If time has passed today, schedule for tomorrow
                if scheduled_datetime < now:
                    scheduled_datetime += timedelta(days=1)
            else:  # Full datetime format
                scheduled_datetime = datetime.strptime(schedule_time, "%Y-%m-%d %H:%M")
            
            # If post_content is empty and use_llm is True, we'll generate it at schedule time
            post_id = f"post_{int(time.time())}"
            
            scheduled_post = {
                "id": post_id,
                "content": post_content,
                "topic": topic,
                "scheduled_time": scheduled_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "scheduled",
                "use_llm": use_llm,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.scheduled_posts.append(scheduled_post)
            self.save_scheduled_posts()
            
            print(f"✅ Post scheduled for {scheduled_datetime.strftime('%Y-%m-%d %H:%M')}")
            return True
            
        except Exception as e:
            print(f"❌ Error scheduling post: {e}")
            return False
    
    def remove_scheduled_post(self, post_id: str) -> bool:
        """Remove a scheduled post"""
        try:
            self.scheduled_posts = [p for p in self.scheduled_posts if p.get('id') != post_id]
            self.save_scheduled_posts()
            print(f"✅ Scheduled post {post_id} removed")
            return True
        except Exception as e:
            print(f"❌ Error removing scheduled post: {e}")
            return False
    
    def get_scheduled_posts(self) -> List[Dict]:
        """Get all scheduled posts"""
        # Filter out past posts
        now = datetime.now()
        active_posts = []
        for post in self.scheduled_posts:
            try:
                scheduled_time = datetime.strptime(post['scheduled_time'], "%Y-%m-%d %H:%M:%S")
                if scheduled_time > now and post.get('status') == 'scheduled':
                    active_posts.append(post)
                elif scheduled_time <= now:
                    # Mark as expired
                    post['status'] = 'expired'
            except:
                continue
        
        # Save updated statuses
        if active_posts != self.scheduled_posts:
            self.save_scheduled_posts()
        
        return active_posts
    
    def execute_post(self, post_data: Dict) -> bool:
        """Execute a scheduled post"""
        try:
            post_id = post_data.get('id')
            print(f"\n📤 Executing scheduled post: {post_id}")
            
            # Generate post if needed
            post_content = post_data.get('content', '')
            if not post_content and post_data.get('use_llm'):
                print("🤖 Generating post using AI...")
                topic = post_data.get('topic', '')
                if topic:
                    topic_dict = {
                        "title": topic,
                        "description": "",
                        "url": "",
                        "source": "scheduled",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    use_llm = post_data.get('use_llm', False)
                    generator = PostGenerator(use_llm=use_llm)
                    
                    # Set API keys if available
                    if use_llm:
                        import os
                        generator.groq_api_key = os.getenv('GROQ_API_KEY', '')
                        generator.together_api_key = os.getenv('TOGETHER_API_KEY', '')
                        generator.hf_api_key = os.getenv('HF_API_KEY', '')
                    
                    post_content = generator.generate_post(topic_dict)
                else:
                    print("⚠️ No topic provided for post generation")
                    post_data['status'] = 'failed'
                    self.save_scheduled_posts()
                    return False
            
            if not post_content:
                print("⚠️ No post content available")
                post_data['status'] = 'failed'
                self.save_scheduled_posts()
                return False
            
            # Post to LinkedIn
            print("🔐 Logging into LinkedIn...")
            poster = LinkedInPoster()
            poster.setup_driver()
            
            if not poster.login():
                print("❌ Login failed")
                post_data['status'] = 'failed'
                self.save_scheduled_posts()
                poster.close()
                return False
            
            print("📝 Posting to LinkedIn (automated mode)...")
            success = poster.post_content(post_content, automated=True)
            
            poster.close()
            
            if success:
                post_data['status'] = 'posted'
                post_data['posted_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"✅ Post {post_id} published successfully!")
            else:
                post_data['status'] = 'failed'
                post_data['error'] = "Posting failed"
                print(f"❌ Post {post_id} failed to publish")
            
            self.save_scheduled_posts()
            return success
            
        except Exception as e:
            print(f"❌ Error executing post: {e}")
            import traceback
            traceback.print_exc()
            post_data['status'] = 'failed'
            post_data['error'] = str(e)
            self.save_scheduled_posts()
            return False
    
    def check_and_execute_posts(self):
        """Check for posts that need to be executed and execute them"""
        now = datetime.now()
        
        for post in self.scheduled_posts:
            if post.get('status') != 'scheduled':
                continue
            
            try:
                scheduled_time = datetime.strptime(post['scheduled_time'], "%Y-%m-%d %H:%M:%S")
                
                # Execute if scheduled time has passed (within 1 minute tolerance)
                if now >= scheduled_time - timedelta(minutes=1) and now <= scheduled_time + timedelta(minutes=5):
                    self.execute_post(post)
                    
            except Exception as e:
                print(f"⚠️ Error checking post {post.get('id')}: {e}")
    
    def start_scheduler(self):
        """Start the scheduler in a background thread"""
        if self.running:
            print("⚠️ Scheduler is already running")
            return
        
        self.running = True
        
        # Schedule the check function to run every minute
        schedule.every(1).minutes.do(self.check_and_execute_posts)
        
        def run_scheduler():
            print("🚀 Scheduler started. Checking for scheduled posts every minute...")
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        
        self.scheduler_thread = Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        print("✅ Scheduler thread started")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        schedule.clear()
        print("🛑 Scheduler stopped")
    
    def schedule_daily_post(self, time_str: str, topic: str = "", use_llm: bool = False, generate_from_trending: bool = False):
        """Schedule a daily recurring post
        
        Args:
            time_str: Time in "HH:MM" format
            topic: Topic for post generation (optional)
            use_llm: Whether to use LLM for generation
            generate_from_trending: Whether to generate from trending topics
        """
        def job():
            print(f"📅 Daily post job triggered at {datetime.now()}")
            
            # Generate post
            post_content = ""
            if generate_from_trending:
                print("🔍 Fetching trending topics...")
                finder = TrendingFinder()
                topics = finder.get_trending_topics(limit=1)
                if topics:
                    topic_dict = topics[0]
                    generator = PostGenerator(use_llm=use_llm)
                    if use_llm:
                        import os
                        generator.groq_api_key = os.getenv('GROQ_API_KEY', '')
                        generator.together_api_key = os.getenv('TOGETHER_API_KEY', '')
                        generator.hf_api_key = os.getenv('HF_API_KEY', '')
                    post_content = generator.generate_post(topic_dict)
            elif topic:
                topic_dict = {
                    "title": topic,
                    "description": "",
                    "url": "",
                    "source": "daily_scheduled",
                    "timestamp": datetime.now().isoformat()
                }
                generator = PostGenerator(use_llm=use_llm)
                if use_llm:
                    import os
                    generator.groq_api_key = os.getenv('GROQ_API_KEY', '')
                    generator.together_api_key = os.getenv('TOGETHER_API_KEY', '')
                    generator.hf_api_key = os.getenv('HF_API_KEY', '')
                post_content = generator.generate_post(topic_dict)
            
            if post_content:
                # Execute post immediately
                post_data = {
                    "id": f"daily_{int(time.time())}",
                    "content": post_content,
                    "topic": topic,
                    "scheduled_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "scheduled",
                    "use_llm": use_llm,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                self.execute_post(post_data)
            else:
                print("⚠️ Could not generate post content")
        
        # Schedule the job
        schedule.every().day.at(time_str).do(job)
        print(f"✅ Daily post scheduled for {time_str} every day")
        
        # Start scheduler if not running
        if not self.running:
            self.start_scheduler()

