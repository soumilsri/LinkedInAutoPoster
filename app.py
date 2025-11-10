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
                    "max_tokens": 500
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
                        # Clean the response - remove any prefixes like "Modified Post:" or "Post:"
                        cleaned_text = modified_text.strip()
                        # Remove common prefixes that LLMs might add
                        prefixes_to_remove = ["Modified Post:", "Post:", "Here's the modified post:", "Modified version:"]
                        for prefix in prefixes_to_remove:
                            if cleaned_text.startswith(prefix):
                                cleaned_text = cleaned_text[len(prefix):].strip()
                        print(f"✅ Groq: Modified post received ({len(cleaned_text)} chars)")
                        return cleaned_text
                else:
                    print(f"⚠️ Groq API returned status {response.status_code}")
            except Exception as e:
                print(f"⚠️ Groq error: {e}")
        
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
                    "max_tokens": 500
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
                        # Clean the response - remove any prefixes like "Modified Post:" or "Post:"
                        cleaned_text = modified_text.strip()
                        # Remove common prefixes that LLMs might add
                        prefixes_to_remove = ["Modified Post:", "Post:", "Here's the modified post:", "Modified version:"]
                        for prefix in prefixes_to_remove:
                            if cleaned_text.startswith(prefix):
                                cleaned_text = cleaned_text[len(prefix):].strip()
                        print(f"✅ Together AI: Modified post received ({len(cleaned_text)} chars)")
                        return cleaned_text
                else:
                    print(f"⚠️ Together AI API returned status {response.status_code}")
            except Exception as e:
                print(f"⚠️ Together AI error: {e}")
        
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

# Clean, Professional CSS Styling
st.markdown("""
<style>
    /* Import Google Fonts - Clean Sans */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Main Container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header Styling - Clean and Professional */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0077b5;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.01em;
    }
    
    /* Button Styling - Clean and Modern */
    .stButton > button {
        background: #0077b5;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0, 119, 181, 0.2);
    }
    
    .stButton > button:hover {
        background: #005885;
        box-shadow: 0 4px 8px rgba(0, 119, 181, 0.3);
    }
    
    /* Primary Button */
    button[kind="primary"] {
        background: #0077b5 !important;
        box-shadow: 0 2px 6px rgba(0, 119, 181, 0.25) !important;
    }
    
    button[kind="primary"]:hover {
        background: #005885 !important;
        box-shadow: 0 4px 10px rgba(0, 119, 181, 0.35) !important;
    }
    
    /* Secondary Buttons */
    .stButton > button:not([kind="primary"]) {
        background: #f8f9fa;
        color: #495057;
        border: 1px solid #dee2e6;
    }
    
    .stButton > button:not([kind="primary"]):hover {
        background: #e9ecef;
        border-color: #adb5bd;
    }
    
    /* Text Input Styling - Clean */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 6px;
        border: 1px solid #ced4da;
        padding: 0.6rem 0.9rem;
        transition: border-color 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #0077b5;
        outline: none;
        box-shadow: 0 0 0 2px rgba(0, 119, 181, 0.1);
    }
    
    /* Selectbox Styling */
    .stSelectbox > div > div {
        border-radius: 6px;
        border: 1px solid #ced4da;
    }
    
    /* Sidebar Styling - Clean */
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e9ecef;
    }
    
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #212529;
        font-weight: 600;
    }
    
    /* Section Headers - Clean */
    h2, h3 {
        color: #212529;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
    
    h2 {
        font-size: 1.5rem;
        border-bottom: 2px solid #e9ecef;
        padding-bottom: 0.5rem;
    }
    
    h3 {
        font-size: 1.25rem;
        color: #495057;
    }
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] {
        font-size: 1.75rem;
        font-weight: 600;
        color: #0077b5;
    }
    
    /* Divider - Clean */
    hr {
        border: none;
        height: 1px;
        background: #e9ecef;
        margin: 1.5rem 0;
    }
    
    /* Text Area Styling */
    textarea {
        border-radius: 6px !important;
        border: 1px solid #ced4da !important;
        padding: 0.75rem !important;
        font-size: 0.95rem !important;
        line-height: 1.5 !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #6c757d;
        padding: 1.5rem 0;
        margin-top: 2rem;
        border-top: 1px solid #e9ecef;
        font-size: 0.875rem;
    }
    
    /* Improve spacing */
    .element-container {
        margin-bottom: 1rem;
    }
    
    /* Clean scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #adb5bd;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #868e96;
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
        
        # Use dynamic key to force refresh when content changes
        content_hash = hash(st.session_state.current_post) % 10000
        mod_count = st.session_state.modification_count
        dynamic_key = f"current_post_display_{mod_count}_{content_hash}"
        
        st.text_area(
            "Post Content",
            st.session_state.current_post,
            height=300,
            disabled=True,
            key=dynamic_key,
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
                        
                        print(f"🔍 Applying prompt: {current_prompt[:50]}...")
                        print(f"🔍 Original post length: {len(st.session_state.current_post)} chars")
                        
                        modified_post = apply_custom_prompt_with_llm(
                            st.session_state.current_post,
                            current_prompt,
                            groq_key,
                            together_key,
                            hf_key
                        )
                        
                        if modified_post and len(modified_post.strip()) > 0:
                            print(f"✅ Modified post received: {len(modified_post)} chars")
                            print(f"🔍 First 100 chars: {modified_post[:100]}...")
                            st.session_state.current_post = modified_post
                            st.session_state.modification_count += 1
                            st.success("✅ Post refined successfully!")
                            st.rerun()
                        else:
                            print(f"❌ Modified post is empty or None")
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
        
        st.info("💡 **Manual Confirmation Mode:** Choose to either open LinkedIn with post pre-filled, or copy to clipboard for manual pasting.")
        
        col_post1, col_post2 = st.columns(2)
        
        with col_post1:
            if st.button("📤 Open LinkedIn (Pre-filled)", type="primary", use_container_width=True):
                with st.spinner("Opening LinkedIn and pre-filling post..."):
                    try:
                        # Update config with credentials
                        import config
                        import os
                        os.environ['LINKEDIN_EMAIL'] = linkedin_email
                        os.environ['LINKEDIN_PASSWORD'] = linkedin_password
                        os.environ['HEADLESS_MODE'] = "False"  # Always show browser for manual confirmation
                        
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
                                st.success("✅ Browser opened with post pre-filled!")
                                st.info("""
                                **📋 Next Steps:**
                                1. ✅ Review the post in the opened browser window
                                2. ✏️ Make any final edits if needed
                                3. 📤 Click the 'Post' button in LinkedIn
                                4. ✅ Come back here once you've posted
                                """)
                                
                                # Don't close the browser - let user complete manually
                                # Store poster in session state so browser stays open
                                if 'linkedin_poster' not in st.session_state:
                                    st.session_state.linkedin_poster = poster
                                
                                # Option to close browser after posting
                                if st.button("🔒 I've Posted - Close Browser", key="close_browser_btn", use_container_width=True):
                                    if 'linkedin_poster' in st.session_state:
                                        st.session_state.linkedin_poster.close()
                                        del st.session_state.linkedin_poster
                                    st.success("✅ Browser closed. Post should be live on LinkedIn!")
                                    
                                    # Optionally clear the post after successful posting
                                    if st.button("🔄 Create New Post", key="new_post_btn", use_container_width=True):
                                        st.session_state.current_post = None
                                        st.session_state.current_topic = None
                                        st.session_state.modification_count = 0
                                        st.rerun()
                            else:
                                st.error("❌ Failed to prepare post. Please try again.")
                                if 'linkedin_poster' in st.session_state:
                                    st.session_state.linkedin_poster.close()
                                    del st.session_state.linkedin_poster
                        else:
                            st.error("❌ Login failed. Please check your credentials.")
                            if 'linkedin_poster' in st.session_state:
                                st.session_state.linkedin_poster.close()
                                del st.session_state.linkedin_poster
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
                        st.info("💡 Tip: Make sure Chrome/Chromium is installed and try again.")
                        if 'linkedin_poster' in st.session_state:
                            try:
                                st.session_state.linkedin_poster.close()
                            except:
                                pass
                            del st.session_state.linkedin_poster
        
        with col_post2:
            st.markdown("**Or copy manually:**")
            # Display post in a copyable text area
            st.text_area(
                "Click and select all, then copy (Ctrl+C / Cmd+C)",
                st.session_state.current_post,
                height=200,
                key="copyable_post",
                help="Select all text and copy it, then paste into LinkedIn"
            )

# Footer
st.markdown("---")
st.markdown("""
<div class="footer">
    <p style="font-size: 0.9rem; margin: 0;">
        Made with <span style="color: #e74c3c;">❤️</span> for zero-cost automation
    </p>
    <p style="font-size: 0.75rem; color: #6c757d; margin-top: 0.5rem;">
        Powered by AI • Built with Streamlit
    </p>
</div>
""", unsafe_allow_html=True)
