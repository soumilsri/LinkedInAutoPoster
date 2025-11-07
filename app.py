"""
Streamlit web interface for LinkedIn Auto-Posting Agent
Simplified single-page flow
"""
import streamlit as st
from trending_finder import TrendingFinder
from post_generator import PostGenerator
from linkedin_poster import LinkedInPoster
import time
import requests


def apply_custom_prompt_with_llm(original_post: str, custom_prompt: str, groq_key: str = "", together_key: str = "", hf_key: str = "") -> str:
    """Apply custom prompt to modify a post using LLM"""
    try:
        # Create modification prompt
        modification_prompt = f"""Original LinkedIn Post:
{original_post}

User's Request: {custom_prompt}

Please modify the post according to the user's request while maintaining:
- Professional LinkedIn tone
- Original key information
- Proper formatting
- Under 3000 characters

Modified Post:"""
        
        # Try Groq first
        if groq_key:
            try:
                headers = {
                    "Authorization": f"Bearer {groq_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional LinkedIn content editor. Modify posts according to user requests while maintaining quality and professionalism."
                        },
                        {
                            "role": "user",
                            "content": modification_prompt
                        }
                    ],
                    "model": "llama-3.1-8b-instant",
                    "temperature": 0.7,
                    "max_tokens": 300
                }
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=15
                )
                if response.status_code == 200:
                    result = response.json()
                    modified_text = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                    if modified_text:
                        return modified_text.strip()
            except Exception as e:
                print(f"Groq error: {e}")
        
        # Try Together AI
        if together_key:
            try:
                headers = {
                    "Authorization": f"Bearer {together_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "meta-llama/Llama-3-8b-chat-hf",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional LinkedIn content editor."
                        },
                        {
                            "role": "user",
                            "content": modification_prompt
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 300
                }
                response = requests.post(
                    "https://api.together.xyz/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=20
                )
                if response.status_code == 200:
                    result = response.json()
                    modified_text = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                    if modified_text:
                        return modified_text.strip()
            except Exception as e:
                print(f"Together AI error: {e}")
        
        return None
    except Exception as e:
        print(f"Error applying custom prompt: {e}")
        return None

# Page configuration
st.set_page_config(
    page_title="LinkedIn Auto-Posting Agent",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'current_post' not in st.session_state:
    st.session_state.current_post = None
if 'current_topic' not in st.session_state:
    st.session_state.current_topic = None
if 'topics' not in st.session_state:
    st.session_state.topics = []
if 'selected_topic_idx' not in st.session_state:
    st.session_state.selected_topic_idx = None
if 'use_llm' not in st.session_state:
    st.session_state.use_llm = False
# Persist API keys even when toggle is off
if 'groq_api_key' not in st.session_state:
    st.session_state.groq_api_key = ''
if 'together_api_key' not in st.session_state:
    st.session_state.together_api_key = ''
if 'hf_api_key' not in st.session_state:
    st.session_state.hf_api_key = ''
# Track modifications
if 'modification_count' not in st.session_state:
    st.session_state.modification_count = 0

# Initialize components
@st.cache_resource
def get_finder():
    return TrendingFinder()

def get_generator(use_llm=False):
    return PostGenerator(use_llm=use_llm)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0077b5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .step-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 2px solid #0077b5;
        margin: 1rem 0;
        background-color: #f8f9fa;
    }
    .post-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 2px solid #28a745;
        margin: 1rem 0;
        background-color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🚀 LinkedIn Auto-Posting Agent</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    st.markdown("### LinkedIn Credentials")
    linkedin_email = st.text_input("Email", type="default", help="Your LinkedIn email")
    linkedin_password = st.text_input("Password", type="password", help="Your LinkedIn password")
    
    st.markdown("---")
    st.markdown("### Settings")
    topics_count = st.slider("Number of topics to fetch", 1, 10, 5)
    headless_mode = st.checkbox("Headless Browser Mode", value=False, help="Run browser in background")
    
    st.markdown("---")
    st.markdown("### 🤖 AI Generation (Free LLM APIs)")
    use_llm = st.toggle("Enable AI-Powered Post Generation", value=False, 
                       help="Use free LLM APIs for more creative and natural posts")
    
    if use_llm:
        st.markdown("**Choose your free LLM provider:**")
        
        # Groq API (Recommended - fastest)
        groq_api_key = st.text_input("Groq API Key (Recommended - Fast & Free)", type="password", 
                                    help="Get free API key from console.groq.com",
                                    placeholder="gsk_xxxxxxxxxxxx",
                                    value=st.session_state.get('groq_api_key', ''),
                                    key='groq_key_input')
        
        # Together AI
        together_api_key = st.text_input("Together AI API Key (Alternative)", type="password", 
                                         help="Get free API key from together.ai",
                                         placeholder="xxxxxxxxxxxx",
                                         value=st.session_state.get('together_api_key', ''),
                                         key='together_key_input')
        
        # Hugging Face (fallback)
        hf_api_key = st.text_input("Hugging Face API Key (Fallback)", type="password", 
                                  help="Get free API key from huggingface.co/settings/tokens",
                                  placeholder="hf_xxxxxxxxxxxx",
                                  value=st.session_state.get('hf_api_key', ''),
                                  key='hf_key_input')
        
        # Save keys to session state
        if 'groq_key_input' in st.session_state:
            st.session_state['groq_api_key'] = st.session_state['groq_key_input']
        if 'together_key_input' in st.session_state:
            st.session_state['together_api_key'] = st.session_state['together_key_input']
        if 'hf_key_input' in st.session_state:
            st.session_state['hf_api_key'] = st.session_state['hf_key_input']
        
        # Check if any key is configured
        has_any_key = (st.session_state.get('groq_api_key', '') or 
                      st.session_state.get('together_api_key', '') or 
                      st.session_state.get('hf_api_key', ''))
        
        if has_any_key:
            import os
            if st.session_state.get('groq_api_key'):
                os.environ['GROQ_API_KEY'] = st.session_state['groq_api_key']
            if st.session_state.get('together_api_key'):
                os.environ['TOGETHER_API_KEY'] = st.session_state['together_api_key']
            if st.session_state.get('hf_api_key'):
                os.environ['HF_API_KEY'] = st.session_state['hf_api_key']
            
            st.session_state['use_llm'] = True
            st.success("✅ API key(s) configured")
            
            saved_keys = []
            if st.session_state.get('groq_api_key'):
                saved_keys.append("Groq")
            if st.session_state.get('together_api_key'):
                saved_keys.append("Together AI")
            if st.session_state.get('hf_api_key'):
                saved_keys.append("Hugging Face")
            
            if saved_keys:
                st.info(f"💾 Saved keys: {', '.join(saved_keys)}")
        else:
            st.warning("⚠️ Enter at least one API key to use AI generation")
            st.session_state['use_llm'] = False
    else:
        st.info("ℹ️ Using template-based generation (no API key needed)")
        saved_keys = []
        if st.session_state.get('groq_api_key'):
            saved_keys.append("Groq")
        if st.session_state.get('together_api_key'):
            saved_keys.append("Together AI")
        if st.session_state.get('hf_api_key'):
            saved_keys.append("Hugging Face")
        
        if saved_keys:
            st.success(f"💾 Your API keys are saved: {', '.join(saved_keys)}. Toggle ON to use them.")
        st.session_state['use_llm'] = False
    
    st.markdown("---")
    st.markdown("### About")
    st.info("""
    **Zero-Cost AI Agent**
    
    • Find trending topics
    • Generate post drafts
    • Review & edit
    • Auto-post to LinkedIn
    
    All without paid APIs! 🎉
    """)

# Main content - Single page flow
st.markdown("### Step 1: Choose Your Topic")

# Two options side by side
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📊 Option 1: Find Trending Topics")
    if st.button("🔍 Find Trending Topics", type="primary", use_container_width=True):
        with st.spinner("Fetching trending topics from various sources..."):
            finder = get_finder()
            st.session_state.topics = finder.get_trending_topics(limit=topics_count)
        
        if st.session_state.topics:
            st.success(f"✅ Found {len(st.session_state.topics)} trending topics!")
            st.session_state.selected_topic_idx = 0  # Auto-select first topic

with col2:
    st.markdown("#### ✨ Option 2: Enter Custom Topic")
    manual_topic = st.text_area(
        "Enter your topic/agenda",
        placeholder="e.g., The future of AI in healthcare",
        height=80,
        key="manual_topic_input"
    )
    
    if st.button("✨ Generate from Custom Topic", type="primary", use_container_width=True):
        manual_topic_value = st.session_state.get('manual_topic_input', '')
        
        if manual_topic_value:
            manual_topic_dict = {
                "title": manual_topic_value,
                "description": "",
                "url": "",
                "source": "manual",
                "timestamp": "manual"
            }
            
            use_llm = st.session_state.get('use_llm', False)
            groq_key = st.session_state.get('groq_api_key', '')
            together_key = st.session_state.get('together_api_key', '')
            hf_key = st.session_state.get('hf_api_key', '')
            
            if use_llm and (groq_key or together_key or hf_key):
                with st.spinner("🤖 Generating AI-powered post..."):
                    import os
                    if groq_key:
                        os.environ['GROQ_API_KEY'] = groq_key
                    if together_key:
                        os.environ['TOGETHER_API_KEY'] = together_key
                    if hf_key:
                        os.environ['HF_API_KEY'] = hf_key
                    
                    generator = PostGenerator(use_llm=True)
                    generator.groq_api_key = groq_key
                    generator.together_api_key = together_key
                    generator.hf_api_key = hf_key
                    
                    generated_post = generator.generate_post(manual_topic_dict)
                    st.session_state.current_post = generated_post
                    st.session_state.current_topic = manual_topic_value
                    st.session_state.modification_count = 0
                    st.success("✅ Post generated!")
                    st.rerun()
            else:
                with st.spinner("Generating post..."):
                    generator = PostGenerator(use_llm=False)
                    generated_post = generator.generate_post(manual_topic_dict)
                    st.session_state.current_post = generated_post
                    st.session_state.current_topic = manual_topic_value
                    st.session_state.modification_count = 0
                    st.success("✅ Post generated!")
                    st.rerun()
        else:
            st.warning("⚠️ Please enter a topic first")

# Show trending topics if available
if st.session_state.topics:
    st.markdown("---")
    st.markdown("#### 📊 Select a Trending Topic")
    
    topic_options = [f"{i+1}. {t.get('title', 'Untitled')[:60]}..." for i, t in enumerate(st.session_state.topics)]
    selected_idx = st.selectbox(
        "Choose a topic to generate post",
        range(len(st.session_state.topics)),
        format_func=lambda x: topic_options[x],
        key="topic_selector",
        index=st.session_state.selected_topic_idx if st.session_state.selected_topic_idx is not None else 0
    )
    
    if st.button("✍️ Generate Post from Selected Topic", type="primary", use_container_width=True):
        selected_topic = st.session_state.topics[selected_idx]
        
        use_llm = st.session_state.get('use_llm', False)
        groq_key = st.session_state.get('groq_api_key', '')
        together_key = st.session_state.get('together_api_key', '')
        hf_key = st.session_state.get('hf_api_key', '')
        
        if use_llm and (groq_key or together_key or hf_key):
            with st.spinner("🤖 Generating AI-powered post..."):
                import os
                if groq_key:
                    os.environ['GROQ_API_KEY'] = groq_key
                if together_key:
                    os.environ['TOGETHER_API_KEY'] = together_key
                if hf_key:
                    os.environ['HF_API_KEY'] = hf_key
                
                generator = PostGenerator(use_llm=True)
                generator.groq_api_key = groq_key
                generator.together_api_key = together_key
                generator.hf_api_key = hf_key
                
                generated_post = generator.generate_post(selected_topic)
                st.session_state.current_post = generated_post
                st.session_state.current_topic = selected_topic.get('title', '')
                st.session_state.modification_count = 0
                st.success("✅ Post generated!")
                st.rerun()
        else:
            with st.spinner("Generating post..."):
                generator = PostGenerator(use_llm=False)
                generated_post = generator.generate_post(selected_topic)
                st.session_state.current_post = generated_post
                st.session_state.current_topic = selected_topic.get('title', '')
                st.session_state.modification_count = 0
                st.success("✅ Post generated!")
                st.rerun()

# Step 2: Show generated post and editing options
if st.session_state.current_post:
    st.markdown("---")
    st.markdown("### Step 2: Review & Edit Your Post")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 📝 Current Post")
        if st.session_state.modification_count > 0:
            st.info(f"📝 Modified {st.session_state.modification_count} time(s)")
        
        st.text_area(
            "Post Content",
            st.session_state.current_post,
            height=300,
            disabled=True,
            key="current_post_display",
            label_visibility="visible"
        )
        
        st.caption(f"Length: {len(st.session_state.current_post)} characters")
    
    with col2:
        st.markdown("#### 🤖 Edit with Jarvis")
        st.markdown("Use AI-powered prompts to refine your post.")
        
        # Quick prompt templates
        st.markdown("**Quick Prompts:**")
        prompt_templates = {
            "📊 More Professional": "Make this post more professional and business-focused",
            "✂️ Make Shorter": "Make this post shorter and more concise while keeping key points",
            "❓ Add Question": "Add an engaging question at the end to encourage discussion",
            "💡 Add Insights": "Add more personal insights and analysis to this post",
            "🎯 More Engaging": "Make this post more engaging and attention-grabbing",
            "📈 Add Data": "Add relevant statistics or data points to support the message"
        }
        
        col_q1, col_q2, col_q3 = st.columns(3)
        buttons = list(prompt_templates.items())
        for i, (label, prompt_text) in enumerate(buttons):
            col = [col_q1, col_q2, col_q3][i % 3]
            with col:
                if st.button(label, key=f"prompt_btn_{i}", use_container_width=True):
                    st.session_state['selected_prompt'] = prompt_text
                    st.rerun()
        
        # Pre-fill prompt if one was selected
        initial_prompt = ""
        if 'selected_prompt' in st.session_state:
            initial_prompt = st.session_state['selected_prompt']
            del st.session_state['selected_prompt']
        
        custom_prompt = st.text_area(
            "Enter your custom prompt",
            value=initial_prompt,
            placeholder="e.g., Make it more professional, Add technical details, Make it shorter...",
            height=100,
            key="custom_prompt_input"
        )
        
        if st.button("🔄 Apply AI Prompt", type="primary", use_container_width=True):
            current_prompt = st.session_state.get('custom_prompt_input', '')
            if current_prompt:
                use_llm = st.session_state.get('use_llm', False)
                groq_key = st.session_state.get('groq_api_key', '')
                together_key = st.session_state.get('together_api_key', '')
                hf_key = st.session_state.get('hf_api_key', '')
                
                if use_llm and (groq_key or together_key or hf_key):
                    with st.spinner("🤖 Applying AI prompt..."):
                        import os
                        if groq_key:
                            os.environ['GROQ_API_KEY'] = groq_key
                        if together_key:
                            os.environ['TOGETHER_API_KEY'] = together_key
                        if hf_key:
                            os.environ['HF_API_KEY'] = hf_key
                        
                        modified_post = apply_custom_prompt_with_llm(
                            st.session_state.current_post,
                            current_prompt,
                            groq_key,
                            together_key,
                            hf_key
                        )
                        
                        if modified_post and len(modified_post.strip()) > 0:
                            st.session_state.current_post = modified_post
                            st.session_state.modification_count += 1
                            st.success("✅ Post refined successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to refine post. Try again or check API keys.")
                else:
                    st.warning("⚠️ Enable AI and add an API key to use prompts")
            else:
                st.warning("⚠️ Please enter a prompt")
    
    # Step 3: Post to LinkedIn
    st.markdown("---")
    st.markdown("### Step 3: Post to LinkedIn")
    
    if not linkedin_email or not linkedin_password:
        st.warning("⚠️ Please configure your LinkedIn credentials in the sidebar to enable posting")
    else:
        st.markdown("**Final Post Preview:**")
        st.text_area(
            "Post to be published",
            st.session_state.current_post,
            height=200,
            disabled=True,
            key="final_post_preview",
            label_visibility="visible"
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.metric("Length", f"{len(st.session_state.current_post)} chars")
        with col2:
            st.metric("Topic", st.session_state.current_topic[:30] + "..." if len(st.session_state.current_topic) > 30 else st.session_state.current_topic)
        
        if st.button("📤 Post to LinkedIn", type="primary", use_container_width=True):
            with st.spinner("Posting to LinkedIn..."):
                try:
                    # Update config with credentials
                    import config
                    import os
                    os.environ['LINKEDIN_EMAIL'] = linkedin_email
                    os.environ['LINKEDIN_PASSWORD'] = linkedin_password
                    os.environ['HEADLESS_MODE'] = str(headless_mode)
                    
                    # Reload config to get new values
                    import importlib
                    importlib.reload(config)
                    
                    # Create a new poster instance with updated config
                    poster = LinkedInPoster()
                    poster.email = linkedin_email
                    poster.password = linkedin_password
                    poster.setup_driver()
                    
                    if poster.login():
                        if poster.post_content(st.session_state.current_post):
                            st.success("✅ Successfully posted to LinkedIn!")
                            st.balloons()
                            # Optionally clear the post after successful posting
                            if st.button("🔄 Create New Post", use_container_width=True):
                                st.session_state.current_post = None
                                st.session_state.current_topic = None
                                st.session_state.modification_count = 0
                                st.rerun()
                        else:
                            st.error("❌ Failed to post. Please try again.")
                    else:
                        st.error("❌ Login failed. Please check your credentials.")
                    
                    poster.close()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
                    st.info("💡 Tip: LinkedIn's interface may have changed. You may need to post manually.")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>Made with ❤️ for zero-cost automation</div>", unsafe_allow_html=True)
