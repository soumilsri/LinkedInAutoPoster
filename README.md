# 🚀 LinkedIn Auto-Posting Agent

A zero-cost AI agent that automatically finds trending LinkedIn topics, drafts engaging posts, and allows manual approval before publishing.

## ✨ Features

- **🔍 Find Topics**: Discover trending topics from Reddit, RSS feeds, and news sources
- **✍️ Generate Drafts**: Create LinkedIn post drafts from trending topics using AI
- **🤖 Edit with Jarvis**: Refine posts using AI-powered custom prompts
- **📤 Auto-Post**: Automatically post to LinkedIn (with manual approval)

## 🎯 Key Capabilities

### AI-Powered Generation
- **Groq API** (Recommended - Fast & Free)
- **Together AI** (Alternative free tier)
- **Hugging Face** (Fallback option)
- **Template-based** fallback when AI is unavailable

### Custom Prompt Editor (Jarvis)
- Quick prompt templates for common modifications
- Custom prompt input for specific changes
- Real-time preview updates
- Multiple refinement iterations

### Manual Topic Input
- Generate posts from custom topics
- Quick topic examples
- Additional context support

## 🛠️ Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd linkedin-autoposter
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## 🚀 Usage

### Web Interface (Recommended)
```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

### Command Line Interface
```bash
python main.py
```

## 📋 Configuration

### Required (for posting)
- `LINKEDIN_EMAIL`: Your LinkedIn email
- `LINKEDIN_PASSWORD`: Your LinkedIn password

### Optional (for AI generation)
- `GROQ_API_KEY`: Get free key from [console.groq.com](https://console.groq.com) (Recommended!)
- `TOGETHER_API_KEY`: Get free key from [together.ai](https://together.ai)
- `HF_API_KEY`: Get free key from [huggingface.co](https://huggingface.co/settings/tokens)

## 📖 Workflow

1. **Find Topics** (Tab 1):
   - Find trending topics, OR
   - Generate post from custom topic

2. **Generate Drafts** (Tab 2):
   - Generate drafts from trending topics

3. **Edit with Jarvis** (Tab 3):
   - Select a draft
   - Use quick prompts or custom prompts
   - Refine with AI

4. **Post to LinkedIn** (Tab 4):
   - Review and post your final draft

## 🎨 Features in Detail

### Find Topics
- **Option 1**: Find trending topics from multiple sources
- **Option 2**: Generate post immediately from custom topic

### Generate Drafts
- AI-powered generation (when API keys are provided)
- Template-based fallback
- Batch generation from multiple topics

### Edit with Jarvis
- Side-by-side view: Current post | Prompt editor
- Quick prompts: More Professional, Make Shorter, Add Question, etc.
- Custom prompts for specific modifications
- Real-time preview updates

## 🔒 Security

- API keys are stored in session state (not persisted)
- LinkedIn credentials are only used for posting
- `.env` file is gitignored

## 📝 License

This project is open source and available for personal use.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚠️ Disclaimer

This tool is for educational purposes. Please ensure compliance with LinkedIn's Terms of Service when using automated posting features.

