"""
Streamlit web interface for LinkedIn Auto-Posting Agent
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
if 'topics' not in st.session_state:
    st.session_state.topics = []
if 'drafts' not in st.session_state:
    st.session_state.drafts = []
if 'selected_draft' not in st.session_state:
    st.session_state.selected_draft = None
if 'use_llm' not in st.session_state:
    st.session_state.use_llm = False
# Persist API keys even when toggle is off
if 'groq_api_key' not in st.session_state:
    st.session_state.groq_api_key = ''
if 'together_api_key' not in st.session_state:
    st.session_state.together_api_key = ''
if 'hf_api_key' not in st.session_state:
    st.session_state.hf_api_key = ''
# Store last generated post from manual topic
if 'last_generated_post' not in st.session_state:
    st.session_state.last_generated_post = None
if 'last_generated_topic' not in st.session_state:
    st.session_state.last_generated_topic = ''
# Track modifications to force preview refresh
if 'draft_modification_count' not in st.session_state:
    st.session_state.draft_modification_count = {}
# Store the latest modified post for immediate preview
if 'latest_modified_post' not in st.session_state:
    st.session_state.latest_modified_post = {}

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
    .feature-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    .draft-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 2px solid #0077b5;
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
        # Use key parameter to bind directly to session state for auto-saving
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
        
        # Save keys to session state immediately when changed
        # Streamlit will update session state automatically via key parameter, but we'll also sync manually
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
            # Always update environment variables with current session state values
            if st.session_state.get('groq_api_key'):
                os.environ['GROQ_API_KEY'] = st.session_state['groq_api_key']
            if st.session_state.get('together_api_key'):
                os.environ['TOGETHER_API_KEY'] = st.session_state['together_api_key']
            if st.session_state.get('hf_api_key'):
                os.environ['HF_API_KEY'] = st.session_state['hf_api_key']
            
            st.session_state['use_llm'] = True
            st.success("✅ API key(s) configured")
            
            # Show which keys are saved
            saved_keys = []
            if st.session_state.get('groq_api_key'):
                saved_keys.append("Groq")
            if st.session_state.get('together_api_key'):
                saved_keys.append("Together AI")
            if st.session_state.get('hf_api_key'):
                saved_keys.append("Hugging Face")
            
            if saved_keys:
                st.info(f"💾 Saved keys: {', '.join(saved_keys)}")
            st.info("💡 **Get free API keys:**\n- Groq: https://console.groq.com (Fastest!)\n- Together AI: https://together.ai\n- Hugging Face: https://huggingface.co/settings/tokens")
        else:
            st.warning("⚠️ Enter at least one API key to use AI generation")
            st.info("💡 **Recommended:** Get a free Groq API key at https://console.groq.com - it's the fastest!")
            st.session_state['use_llm'] = False
    else:
        st.info("ℹ️ Using template-based generation (no API key needed)")
        # Don't clear API keys when toggle is off - they'll be saved for next time
        # Show saved keys status
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

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Find Topics", "✍️ Generate Drafts", "🤖 Edit with Jarvis", "📤 Post to LinkedIn"])

# Tab 1: Find Topics (with two options)
with tab1:
    st.header("🔍 Find Topics")
    st.markdown("Find trending topics or generate posts from your custom topics.")
    
    # Option 1: Find Trending Topics
    st.markdown("### 📊 Option 1: Find Trending Topics")
    st.markdown("Search for trending topics from Reddit, RSS feeds, and news sources.")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("🔍 Find Trending Topics", type="primary", use_container_width=True):
            with st.spinner("Fetching trending topics from various sources..."):
                finder = get_finder()
                st.session_state.topics = finder.get_trending_topics(limit=topics_count)
                
            if st.session_state.topics:
                st.success(f"✅ Found {len(st.session_state.topics)} trending topics!")
            else:
                st.error("❌ No topics found. Please try again.")
    
    with col2:
        if st.session_state.topics:
            st.metric("Topics Found", len(st.session_state.topics))
    
    if st.session_state.topics:
        st.markdown("#### 📊 Trending Topics Found")
        for i, topic in enumerate(st.session_state.topics, 1):
            with st.expander(f"📌 {topic.get('title', 'Untitled')[:80]}...", expanded=False):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Source:** {topic.get('source', 'unknown').upper()}")
                    if topic.get('description'):
                        st.write(f"**Description:** {topic.get('description', '')[:200]}...")
                    if topic.get('url'):
                        st.markdown(f"**Link:** [{topic.get('url', '')}]({topic.get('url', '')})")
                with col2:
                    st.metric("Topic #", i)
    
    # Option 2: Generate from Custom Topic
    st.markdown("---")
    st.markdown("### ✨ Option 2: Generate from Custom Topic")
    st.markdown("Enter your own topic to generate a LinkedIn post immediately.")
    
    # Quick topic examples
    example_topics = [
        "The future of AI in healthcare",
        "Remote work trends in 2024",
        "Sustainable technology solutions",
        "Leadership in the digital age",
        "Innovation in fintech"
    ]
    st.markdown("**Quick Examples (Click to use):**")
    cols = st.columns(5)
    for i, example in enumerate(example_topics):
        with cols[i]:
            if st.button(f"📌 {example[:20]}...", key=f"example_btn_tab1_{i}", use_container_width=True):
                st.session_state['selected_topic_tab1'] = example
                st.rerun()
    
    # Pre-fill topic if one was selected
    initial_topic = ""
    if 'selected_topic_tab1' in st.session_state:
        initial_topic = st.session_state['selected_topic_tab1']
        del st.session_state['selected_topic_tab1']
    
    manual_topic = st.text_area(
        "Enter your topic/agenda",
        value=initial_topic if initial_topic else "",
        placeholder="e.g., The future of AI in healthcare",
        height=80,
        key="manual_topic_input_tab1"
    )
    
    manual_description = st.text_area(
        "Additional context (optional)",
        placeholder="Add any specific points or context...",
        height=60,
        key="manual_description_tab1"
    )
    
    if st.button("✨ Generate Post from Custom Topic", type="primary", use_container_width=True):
        manual_topic_value = st.session_state.get('manual_topic_input_tab1', '')
        manual_description_value = st.session_state.get('manual_description_tab1', '')
        
        if manual_topic_value:
            manual_topic_dict = {
                "title": manual_topic_value,
                "description": manual_description_value,
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
                    
                    if 'drafts' not in st.session_state:
                        st.session_state.drafts = []
                    
                    new_draft = {
                        "id": len(st.session_state.drafts) + 1,
                        "topic": manual_topic_value,
                        "content": generated_post,
                        "source": "manual",
                        "url": "",
                        "length": len(generated_post)
                    }
                    st.session_state.drafts.append(new_draft)
                    st.success("✅ Post generated! Go to 'Edit with Jarvis' tab to refine it.")
                    st.rerun()
            else:
                with st.spinner("Generating post..."):
                    generator = PostGenerator(use_llm=False)
                    generated_post = generator.generate_post(manual_topic_dict)
                    
                    if 'drafts' not in st.session_state:
                        st.session_state.drafts = []
                    
                    new_draft = {
                        "id": len(st.session_state.drafts) + 1,
                        "topic": manual_topic_value,
                        "content": generated_post,
                        "source": "manual",
                        "url": "",
                        "length": len(generated_post)
                    }
                    st.session_state.drafts.append(new_draft)
                    st.success("✅ Post generated! Go to 'Edit with Jarvis' tab to refine it.")
                    st.rerun()
        else:
            st.warning("⚠️ Please enter a topic first")

# Tab 2: Generate Drafts (only from trending topics)
with tab2:
    st.header("✍️ Generate Drafts")
    st.markdown("Generate LinkedIn post drafts from the trending topics you found.")
    
    if not st.session_state.topics:
        st.warning("⚠️ Please find trending topics first (Tab 1)")
    else:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if st.button("✍️ Generate Drafts from Topics", type="primary", use_container_width=True):
                # Get LLM setting from sidebar
                use_llm = st.session_state.get('use_llm', False)
                
                if use_llm:
                    # Get all API keys from session state
                    groq_key = st.session_state.get('groq_api_key', '')
                    together_key = st.session_state.get('together_api_key', '')
                    hf_key = st.session_state.get('hf_api_key', '')
                    
                    if groq_key or together_key or hf_key:
                        with st.spinner("🤖 Generating AI-powered LinkedIn post drafts..."):
                            import os
                            # Set environment variables
                            if groq_key:
                                os.environ['GROQ_API_KEY'] = groq_key
                            if together_key:
                                os.environ['TOGETHER_API_KEY'] = together_key
                            if hf_key:
                                os.environ['HF_API_KEY'] = hf_key
                            
                            # Create generator with all keys
                            generator = PostGenerator(use_llm=True)
                            generator.groq_api_key = groq_key
                            generator.together_api_key = together_key
                            generator.hf_api_key = hf_key
                            
                            st.session_state.drafts = generator.generate_multiple_drafts(
                                st.session_state.topics, 
                                count=len(st.session_state.topics)
                            )
                        st.success(f"✅ Generated {len(st.session_state.drafts)} AI-powered draft(s)!")
                        st.info("💡 Go to 'Edit with Jarvis' tab to refine your drafts.")
                    else:
                        st.warning("⚠️ Please add an API key in the sidebar to use AI generation")
                else:
                    with st.spinner("Generating LinkedIn post drafts using templates..."):
                        generator = get_generator(use_llm=False)
                        st.session_state.drafts = generator.generate_multiple_drafts(
                            st.session_state.topics, 
                            count=len(st.session_state.topics)
                        )
                    st.success(f"✅ Generated {len(st.session_state.drafts)} template-based draft(s)!")
                    st.info("💡 Go to 'Edit with Jarvis' tab to refine your drafts.")
        
        with col2:
            if st.session_state.drafts:
                st.metric("Drafts", len(st.session_state.drafts))
        
        if st.session_state.drafts:
            st.markdown("---")
            st.markdown("### 📝 Generated Drafts Preview")
            for i, draft in enumerate(st.session_state.drafts[:3], 1):  # Show first 3
                with st.expander(f"Draft {i}: {draft['topic'][:50]}...", expanded=False):
                    st.text_area(f"Content", draft['content'], height=150, disabled=True, key=f"preview_{i}")
                    st.caption(f"Length: {draft['length']} chars | Source: {draft['source']}")
            if len(st.session_state.drafts) > 3:
                st.caption(f"... and {len(st.session_state.drafts) - 3} more draft(s)")

# Tab 3: Edit with Jarvis (Custom Prompt Editor)
with tab3:
    st.header("🤖 Edit with Jarvis")
    st.markdown("Use AI-powered prompts to refine and perfect your LinkedIn posts.")
    
    if not st.session_state.drafts:
        st.info("ℹ️ Generate drafts first (Tab 1 or Tab 2), then use Jarvis to refine them here.")
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Select draft to modify
            draft_options = [f"Draft {i+1}: {d['topic'][:40]}..." for i, d in enumerate(st.session_state.drafts)]
            selected_draft_idx = st.selectbox(
                "Select draft to refine",
                range(len(st.session_state.drafts)),
                format_func=lambda x: draft_options[x],
                key="prompt_editor_draft_merged"
            )
            
            if selected_draft_idx is not None:
                selected_draft = st.session_state.drafts[selected_draft_idx]
                
                # Check if there's a latest modified version
                if selected_draft_idx in st.session_state.latest_modified_post:
                    current_post_content = st.session_state.latest_modified_post[selected_draft_idx]
                else:
                    current_post_content = selected_draft['content']
                
                mod_count = st.session_state.draft_modification_count.get(selected_draft_idx, 0)
                
                if mod_count > 0:
                    st.info(f"📝 Modified {mod_count} time(s)")
                
                st.markdown("**Current Post:**")
                content_hash = hash(current_post_content) % 10000
                st.text_area(
                    "Current Post Content",
                    current_post_content,
                    height=200,
                    disabled=True,
                    key=f"current_post_display_merged_{selected_draft_idx}_{mod_count}_{content_hash}",
                    label_visibility="visible"
                )
        
        with col2:
            st.markdown("**AI Prompt Editor**")
            
            if selected_draft_idx is not None:
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
                        if st.button(label, key=f"prompt_btn_merged_{i}", use_container_width=True):
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
                    key="custom_prompt_input_merged"
                )
                
                if st.button("🔄 Apply AI Prompt", type="primary", use_container_width=True):
                    current_prompt = st.session_state.get('custom_prompt_input_merged', '')
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
                                
                                latest_draft = st.session_state.drafts[selected_draft_idx]
                                original_post_content = latest_draft['content']
                                
                                modified_post = apply_custom_prompt_with_llm(
                                    original_post_content,
                                    current_prompt,
                                    groq_key,
                                    together_key,
                                    hf_key
                                )
                                
                                print(f"🔍 DEBUG: Modified post received: {modified_post[:100] if modified_post else 'None'}...")
                                
                                if modified_post and len(modified_post.strip()) > 0:
                                    st.session_state.drafts[selected_draft_idx]['content'] = modified_post
                                    st.session_state.drafts[selected_draft_idx]['length'] = len(modified_post)
                                    st.session_state.latest_modified_post[selected_draft_idx] = modified_post
                                    
                                    if selected_draft_idx not in st.session_state.draft_modification_count:
                                        st.session_state.draft_modification_count[selected_draft_idx] = 0
                                    st.session_state.draft_modification_count[selected_draft_idx] += 1
                                    
                                    st.success("✅ Post refined successfully!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to refine post. Try again or check API keys.")
                        else:
                            st.warning("⚠️ Enable AI and add an API key to use prompts")
                    else:
                        st.warning("⚠️ Please enter a prompt")

# Tab 4: Post to LinkedIn
with tab4:
    st.header("Post to LinkedIn")
    st.markdown("Automatically post your selected draft to LinkedIn.")
    
    if not linkedin_email or not linkedin_password:
        st.warning("⚠️ Please configure your LinkedIn credentials in the sidebar")
    
    if not st.session_state.drafts:
        st.warning("⚠️ No drafts available. Please generate drafts first")
    else:
        # Draft selector for posting
        draft_options_post = [f"Draft {i+1}: {d['topic'][:50]}..." for i, d in enumerate(st.session_state.drafts)]
        selected_post_idx = st.selectbox("Select Draft to Post", range(len(st.session_state.drafts)),
                                        format_func=lambda x: draft_options_post[x], key="post_selector")
        
        if selected_post_idx is not None:
            draft_to_post = st.session_state.drafts[selected_post_idx]
            
            st.markdown("### 📋 Post Preview")
            st.markdown(f"**Topic:** {draft_to_post['topic']}")
            st.text_area("Content", draft_to_post['content'], height=200, disabled=True, key="post_preview")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Length", f"{draft_to_post['length']} chars")
            with col2:
                st.metric("Source", draft_to_post['source'])
            
            st.markdown("---")
            
            # Post button
            if linkedin_email and linkedin_password:
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
                                if poster.post_content(draft_to_post['content']):
                                    st.success("✅ Successfully posted to LinkedIn!")
                                    st.balloons()
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
            else:
                st.info("ℹ️ Please enter your LinkedIn credentials in the sidebar to enable posting")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>Made with ❤️ for zero-cost automation</div>", unsafe_allow_html=True)

