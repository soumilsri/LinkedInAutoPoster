"""
Module to generate LinkedIn post drafts from trending topics
Supports multiple free LLM APIs: Groq, Together AI, Hugging Face
"""
import os
import random
import requests
import json
from typing import Dict, List, Optional
import config


class PostGenerator:
    """Generates LinkedIn post drafts from trending topics"""
    
    def __init__(self, use_llm: bool = False):
        self.max_length = config.MAX_POST_LENGTH
        self.min_length = config.MIN_POST_LENGTH
        self.use_llm = use_llm
        # Multiple API keys for different services (try environment first, then direct assignment)
        self.hf_api_key = os.getenv('HF_API_KEY', '')
        self.groq_api_key = os.getenv('GROQ_API_KEY', '')
        self.together_api_key = os.getenv('TOGETHER_API_KEY', '')
        # New Hugging Face router endpoint (replaces deprecated api-inference endpoint)
        self.hf_router_url = "https://router.huggingface.co/hf-inference"
        # Old endpoint (for reference, but deprecated)
        self.hf_models_url = "https://api-inference.huggingface.co/models"
        # Groq API (very fast, free tier)
        self.groq_api_url = "https://api.groq.com/openai/v1/chat/completions"
        # Together AI API (free tier)
        self.together_api_url = "https://api.together.xyz/v1/chat/completions"
    
    def generate_with_groq(self, topic: Dict) -> Optional[str]:
        """Generate post using Groq API (very fast, free tier)"""
        try:
            if not self.groq_api_key:
                return None
            
            title = topic.get("title", "")
            description = topic.get("description", "")
            
            prompt = f"""Write a professional LinkedIn post about: {title}

{description[:200] if description else ''}

Requirements:
- Professional and engaging tone
- Include a hook to grab attention
- Add personal insights or perspective
- Include relevant hashtags
- Keep it under {self.max_length} characters
- End with a call to action

LinkedIn Post:"""
            
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a professional LinkedIn content creator. Write engaging, professional posts that add value."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "model": "llama-3.1-8b-instant",  # Fast and free
                "temperature": 0.7,
                "max_tokens": 200
            }
            
            response = requests.post(self.groq_api_url, headers=headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                if generated_text:
                    post = self._format_generated_post(generated_text, topic)
                    print(f"✅ Successfully generated post using Groq API")
                    return post
            else:
                print(f"⚠️ Groq API returned status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠️ Error with Groq API: {e}")
            return None
    
    def generate_with_together(self, topic: Dict) -> Optional[str]:
        """Generate post using Together AI API (free tier)"""
        try:
            if not self.together_api_key:
                return None
            
            title = topic.get("title", "")
            description = topic.get("description", "")
            
            prompt = f"""Write a professional LinkedIn post about: {title}

{description[:200] if description else ''}

Requirements:
- Professional and engaging tone
- Include a hook to grab attention
- Add personal insights or perspective
- Include relevant hashtags
- Keep it under {self.max_length} characters
- End with a call to action

LinkedIn Post:"""
            
            headers = {
                "Authorization": f"Bearer {self.together_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "meta-llama/Llama-3-8b-chat-hf",  # Free tier model
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a professional LinkedIn content creator."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 200
            }
            
            response = requests.post(self.together_api_url, headers=headers, json=payload, timeout=20)
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                if generated_text:
                    post = self._format_generated_post(generated_text, topic)
                    print(f"✅ Successfully generated post using Together AI")
                    return post
            else:
                print(f"⚠️ Together AI returned status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠️ Error with Together AI: {e}")
            return None
    
    def generate_with_huggingface(self, topic: Dict) -> str:
        """Generate post using Hugging Face Inference API (free tier)"""
        try:
            if not self.hf_api_key:
                print("⚠️ Hugging Face API key not found. Using template generation.")
                return self._generate_template_post(topic)
            
            # Hugging Face API endpoint analysis:
            # - Old endpoint (api-inference.huggingface.co) returns 410 (deprecated)
            # - New router endpoint (router.huggingface.co/hf-inference) requires correct format
            # - Format: https://router.huggingface.co/hf-inference/models/{model_name}
            
            # Try multiple models that should work with router endpoint
            models_to_try = [
                "gpt2",              # Most reliable
                "distilgpt2",        # Smaller, faster
                "EleutherAI/gpt-neo-125M",  # Alternative
                "microsoft/DialoGPT-small",  # Conversational
            ]
            
            prompt = self._create_prompt(topic)
            
            # Try multiple authentication header formats
            headers_variants = [
                {
                    "Authorization": f"Bearer {self.hf_api_key}",
                    "Content-Type": "application/json"
                },
                {
                    "Authorization": f"Bearer {self.hf_api_key}",
                    "Content-Type": "application/json",
                    "X-API-Key": self.hf_api_key
                },
                {
                    "Authorization": f"token {self.hf_api_key}",
                    "Content-Type": "application/json"
                }
            ]
            
            # Try each model until one works
            for model_name in models_to_try:
                try:
                    # Try the new router endpoint format first
                    # Format: https://router.huggingface.co/hf-inference/models/{model_name}
                    router_url = f"{self.hf_router_url}/models/{model_name}"
                    
                    # Also keep old endpoint as fallback (though it's deprecated)
                    old_api_url = f"{self.hf_models_url}/{model_name}"
                    
                    # Format payload based on model type
                    if "gpt" in model_name.lower() or "neo" in model_name.lower():
                        # For GPT-style models - use standard format
                        payload = {
                            "inputs": prompt,
                            "parameters": {
                                "max_new_tokens": 150,
                                "temperature": 0.8,
                                "top_p": 0.9,
                                "return_full_text": False,
                                "do_sample": True,
                                "repetition_penalty": 1.2
                            }
                        }
                    elif "t5" in model_name.lower() or "flan" in model_name.lower():
                        # For T5/Flan models - instruction format
                        payload = {
                            "inputs": f"Write a LinkedIn post: {prompt}",
                            "parameters": {
                                "max_new_tokens": 150,
                                "temperature": 0.7,
                                "return_full_text": False
                            }
                        }
                    else:
                        # For other models - try simpler format
                        payload = {
                            "inputs": prompt,
                            "parameters": {
                                "max_new_tokens": 150,
                                "temperature": 0.7,
                                "return_full_text": False
                            }
                        }
                    
                    # Try the new router endpoint first with different auth formats
                    response = None
                    for header_variant in headers_variants:
                        try:
                            print(f"🔄 Trying router endpoint for {model_name} with auth variant...")
                            response = requests.post(router_url, headers=header_variant, json=payload, timeout=30)
                        
                            # If router endpoint works, use it
                            if response.status_code == 200:
                                print(f"✅ Router endpoint successful for {model_name}")
                                break  # Success! Exit the header variant loop
                            elif response.status_code == 401:
                                print(f"⚠️ Auth variant failed (401), trying next variant...")
                                continue  # Try next auth variant
                            elif response.status_code == 503:
                                print(f"⏳ Model {model_name} is loading on router endpoint...")
                                break  # Model loading, will try next model
                            elif response.status_code == 404:
                                print(f"⚠️ Model {model_name} not found on router endpoint")
                                break  # Model not found, try next model
                            else:
                                # Other error, try next variant
                                continue
                        except requests.exceptions.RequestException as e:
                            print(f"⚠️ Error with auth variant: {e}")
                            continue  # Try next auth variant
                    
                    # If all auth variants failed, try old endpoint as last resort
                    if not response or response.status_code == 401:
                        print(f"🔄 All router auth variants failed, trying old endpoint as fallback...")
                        try:
                            response = requests.post(old_api_url, headers=headers_variants[0], json=payload, timeout=30)
                        except:
                            response = None
                    
                    # If 410 error, the endpoint is deprecated
                    if response and response.status_code == 410:
                        print(f"⚠️ Endpoint deprecated for {model_name}, trying next model...")
                        continue
                    
                    # Debug: Print response details
                    if response:
                        print(f"📡 Model {model_name}: Status {response.status_code}")
                        if response.status_code == 200:
                            # Success! Process the response
                            pass  # Will be handled below
                        elif response.status_code == 401:
                            print(f"   ❌ Authentication failed - check API key format and permissions")
                            print(f"   💡 Make sure your API key starts with 'hf_' and has Inference API access")
                            # Try next model - might work with different model
                            continue
                        elif response.status_code == 503:
                            print(f"   ⏳ Model is loading - will try next model")
                            continue
                        else:
                            try:
                                error_detail = response.json()
                                print(f"   Error detail: {error_detail}")
                            except:
                                print(f"   Response text: {response.text[:200]}")
                            continue
                    else:
                        print(f"⚠️ No response from {model_name}, trying next...")
                        continue
                    
                    # Process successful response
                    if response and response.status_code == 200:
                        result = response.json()
                        generated_text = ""
                        
                        # Handle different response formats
                        if isinstance(result, list) and len(result) > 0:
                            if isinstance(result[0], dict):
                                generated_text = result[0].get('generated_text', '')
                            else:
                                generated_text = str(result[0])
                        elif isinstance(result, dict):
                            if 'generated_text' in result:
                                generated_text = result['generated_text']
                            elif 'text' in result:
                                generated_text = result['text']
                            elif len(result) > 0:
                                # Try to get first value
                                generated_text = str(list(result.values())[0])
                        
                        if generated_text and len(generated_text.strip()) > 20:
                            # Clean and format the generated text
                            post = self._format_generated_post(generated_text, topic)
                            print(f"✅ Successfully generated post using {model_name}")
                            return post
                        else:
                            print(f"⚠️ Model {model_name} returned empty/invalid text")
                            continue
                    else:
                        # Response exists but status is not 200 - already handled above
                        continue
                        
                except requests.exceptions.Timeout:
                    print(f"⏳ Timeout with {model_name}, trying next model...")
                    continue
                except Exception as e:
                    print(f"⚠️ Error with {model_name}: {e}, trying next model...")
                    continue
            
            # If all models failed, use AI-enhanced template
            print("⚠️ Hugging Face API endpoints deprecated. Using AI-enhanced template generation.")
            return self._generate_ai_enhanced_template(topic)
            
        except Exception as e:
            print(f"⚠️ Error with Hugging Face API: {e}. Using template generation.")
            return self._generate_template_post(topic)
    
    def _format_generated_post(self, generated_text: str, topic: Dict) -> str:
        """Format and clean the generated text into a LinkedIn post"""
        # Clean the text - remove prompt if it was included
        post = generated_text.strip()
        
        # Remove the prompt text if model included it
        if "Post:" in post:
            post = post.split("Post:")[-1].strip()
        if "Write a professional" in post:
            # Find where the actual post starts
            lines = post.split('\n')
            post_lines = []
            skip_prompt = True
            for line in lines:
                if "Post:" in line or (skip_prompt and line.strip() and not line.startswith("Write")):
                    skip_prompt = False
                    if "Post:" in line:
                        post_lines.append(line.split("Post:")[-1].strip())
                    else:
                        post_lines.append(line.strip())
            post = '\n\n'.join([l for l in post_lines if l])
        
        # Clean up any weird formatting
        post = post.replace('\n\n\n', '\n\n')
        post = post.strip()
        
        # Remove incomplete sentences at the end
        sentences = post.split('.')
        if len(sentences) > 1 and len(sentences[-1].strip()) < 10:
            post = '. '.join(sentences[:-1]) + '.'
        
        # Ensure minimum length
        if len(post.strip()) < 50:
            # If generated text is too short, enhance it
            post = f"{post}\n\nThis is an interesting development that's worth discussing."
        
        # Add title as header if not present
        if topic.get('title') and topic['title'] not in post[:100]:
            post = f"🔥 {topic['title']}\n\n{post}"
        
        # Add a hook if the post is too direct
        if not any(hook in post for hook in ["think", "take", "perspective", "interesting", "discuss"]):
            hooks = [
                "This got me thinking...",
                "Here's my take:",
                "Interesting development:",
            ]
            import random
            hook = random.choice(hooks)
            if topic.get('title') in post:
                # Insert hook after title
                parts = post.split('\n\n', 1)
                if len(parts) > 1:
                    post = f"{parts[0]}\n\n{hook} {parts[1]}"
        
        # Add call to action if missing
        if "perspective" not in post.lower() and "think" not in post.lower():
            post += "\n\n💭 What's your perspective on this?"
        
        # Add hashtags
        hashtags = self._generate_hashtags(topic.get('title', ''), topic.get('source', ''))
        post += f"\n\n{hashtags}"
        
        # Add URL if available
        if topic.get('url'):
            post += f"\n\n🔗 Read more: {topic['url']}"
        
        # Ensure length compliance
        if len(post) > self.max_length:
            # Truncate intelligently at sentence boundary
            truncated = post[:self.max_length - 20]
            last_period = truncated.rfind('.')
            if last_period > self.max_length * 0.7:  # If we have a good sentence break
                post = truncated[:last_period + 1] + "..."
            else:
                post = truncated + "..."
        
        return post
    
    def _create_prompt(self, topic: Dict) -> str:
        """Create a prompt for post generation"""
        title = topic.get("title", "")
        description = topic.get("description", "")
        
        # Create a more concise prompt that works better with GPT models
        prompt = f"""Write a professional LinkedIn post about: {title}

"""
        
        if description:
            prompt += f"{description[:150]}\n\n"
        
        prompt += "Post:"
        
        return prompt
    
    def _generate_ai_enhanced_template(self, topic: Dict) -> str:
        """Generate a post using AI-enhanced templates (more varied and natural)"""
        title = topic.get("title", "")
        description = topic.get("description", "")
        url = topic.get("url", "")
        source = topic.get("source", "")
        
        # More varied opening styles
        openings = [
            f"🔥 {title}",
            f"💡 Interesting development: {title}",
            f"📰 Breaking: {title}",
            f"🚀 {title}",
            f"⚡ {title}"
        ]
        
        post = random.choice(openings) + "\n\n"
        
        # Add description with variation
        if description:
            desc = description[:180]
            # Sometimes add a lead-in
            lead_ins = [
                "",
                "Here's what caught my attention: ",
                "Key points: ",
                "What this means: "
            ]
            post += random.choice(lead_ins) + desc
            if len(description) > 180:
                post += "..."
            post += "\n\n"
        
        # More varied hooks
        hooks = [
            "This got me thinking about the future of our industry...",
            "Here's my perspective on this development:",
            "Interesting implications for the tech landscape:",
            "This is worth discussing because:",
            "What stands out to me:",
            "My take on this trend:",
            "This development raises important questions:",
            "Food for thought:"
        ]
        
        # Add personal insights
        insights = [
            "The implications for businesses are significant.",
            "This could reshape how we think about technology.",
            "It's developments like this that drive innovation forward.",
            "The timing of this is particularly interesting.",
            "This aligns with broader trends we're seeing."
        ]
        
        post += f"{random.choice(hooks)}\n\n"
        post += f"{random.choice(insights)}\n\n"
        
        # Varied CTAs
        ctas = [
            "💭 What's your perspective on this?",
            "🤔 What do you think?",
            "💬 I'd love to hear your thoughts.",
            "🎯 How does this impact your work?",
            "💭 Share your thoughts below."
        ]
        
        post += random.choice(ctas) + "\n\n"
        
        # Add hashtags
        hashtags = self._generate_hashtags(title, source)
        post += hashtags
        
        if url:
            post += f"\n\n🔗 Read more: {url}"
        
        # Ensure length compliance
        if len(post) > self.max_length:
            post = post[:self.max_length - 20] + "..."
        
        return post
    
    def _generate_template_post(self, topic: Dict) -> str:
        """Generate a post using a template (fallback method)"""
        title = topic.get("title", "")
        description = topic.get("description", "")
        url = topic.get("url", "")
        source = topic.get("source", "")
        
        # Create engaging post template
        post = f"""🔥 {title}

"""
        
        if description:
            post += f"{description[:150]}...\n\n"
        
        # Add personal insight hook
        hooks = [
            "This got me thinking...",
            "Here's my take on this:",
            "Interesting development in our industry:",
            "This is worth discussing:",
            "What do you think about this trend?"
        ]
        
        post += f"{random.choice(hooks)}\n\n"
        
        # Add call to action
        post += "💭 What's your perspective on this?\n\n"
        
        # Add relevant hashtags
        hashtags = self._generate_hashtags(title, source)
        post += hashtags
        
        if url:
            post += f"\n\n🔗 Read more: {url}"
        
        # Ensure length compliance
        if len(post) > self.max_length:
            post = post[:self.max_length - 20] + "..."
        
        return post
    
    def _generate_hashtags(self, title: str, source: str) -> str:
        """Generate relevant hashtags based on title"""
        common_hashtags = ["#LinkedIn", "#Technology", "#Innovation", "#Business"]
        
        # Extract keywords from title
        keywords = title.lower().split()
        tech_keywords = ["ai", "tech", "software", "startup", "digital", "cloud", "data"]
        business_keywords = ["business", "leadership", "strategy", "growth", "entrepreneur"]
        
        hashtags = []
        for keyword in keywords:
            if keyword in tech_keywords:
                hashtags.append(f"#{keyword.title()}")
            elif keyword in business_keywords:
                hashtags.append(f"#{keyword.title()}")
        
        # Limit hashtags
        hashtags = hashtags[:3] + common_hashtags[:2]
        return " ".join(hashtags[:5])
    
    def generate_post(self, topic: Dict) -> str:
        """Generate a LinkedIn post from a topic"""
        try:
            # Use LLM if enabled and available, otherwise use template
            if self.use_llm:
                # Try multiple free LLM APIs in order of preference
                # 1. Groq (fastest, free tier)
                if self.groq_api_key:
                    print(f"🤖 Trying Groq API...")
                    result = self.generate_with_groq(topic)
                    if result:
                        return result
                
                # 2. Together AI (free tier)
                if self.together_api_key:
                    print(f"🤖 Trying Together AI...")
                    result = self.generate_with_together(topic)
                    if result:
                        return result
                
                # 3. Hugging Face (if available)
                if self.hf_api_key:
                    print(f"🤖 Trying Hugging Face API...")
                    result = self.generate_with_huggingface(topic)
                    if result and not result.startswith("🔥"):  # If it's not a template
                        return result
                
                # If all APIs failed, use AI-enhanced template
                print("⚠️ All LLM APIs failed. Using AI-enhanced template.")
                return self._generate_ai_enhanced_template(topic)
            else:
                print("📝 Using template generation (LLM disabled)")
                return self._generate_template_post(topic)
        except Exception as e:
            print(f"Error generating post: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_template_post(topic)
    
    def generate_multiple_drafts(self, topics: List[Dict], count: int = 3) -> List[Dict]:
        """Generate multiple post drafts from topics"""
        drafts = []
        
        for i, topic in enumerate(topics[:count]):
            post_content = self.generate_post(topic)
            drafts.append({
                "id": i + 1,
                "topic": topic.get("title", ""),
                "content": post_content,
                "source": topic.get("source", ""),
                "url": topic.get("url", ""),
                "length": len(post_content)
            })
        
        return drafts

