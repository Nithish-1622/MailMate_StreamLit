# 🚀 MailMate - AI Email Management System

## Streamlit Cloud Deployment Guide

### Prerequisites
1. **GitHub Repository**: Push your MailMate project to a GitHub repository
2. **API Keys**: Get your API keys from:
   - [Groq API](https://console.groq.com/keys) - For AI chat functionality
   - [Google AI Studio](https://makersuite.google.com/app/apikey) - For additional AI features

### Deployment Steps

#### 1. Prepare Your Repository
```bash
git init
git add .
git commit -m "Initial MailMate deployment"
git remote add origin https://github.com/your-username/mailmate.git
git push -u origin main
```

#### 2. Deploy to Streamlit Cloud
1. Visit [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your MailMate repository
5. Set main file path: `dashboard.py`
6. Click "Deploy!"

#### 3. Configure Secrets
In Streamlit Cloud dashboard:
1. Go to your app settings
2. Click "Secrets"
3. Add your API keys:
```toml
GROQ_API_KEY = "your_groq_api_key_here"
GOOGLE_API_KEY = "your_google_api_key_here"
```

#### 4. Update Requirements (if needed)
The app will automatically use `requirements_streamlit.txt` for dependencies.

### Features Available in Cloud Deployment
✅ **Full UI/UX**: Enterprise-grade dashboard with glassmorphism design  
✅ **AI Chat**: Intelligent email assistant powered by Groq  
✅ **Analytics**: Advanced email insights and visualizations  
✅ **Email Management**: Priority scoring and categorization  
✅ **Demo Data**: Pre-loaded sample emails for testing  

⚠️ **Limited Features in Cloud**:
- Audio/TTS features (hardware dependent)
- Local file system access
- Real email integration (requires IMAP setup)

### Local Development
```bash
# Clone and setup
git clone https://github.com/your-username/mailmate.git
cd mailmate
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Add your API keys to .env file
echo "GROQ_API_KEY=your_key_here" > .env
echo "GOOGLE_API_KEY=your_key_here" >> .env

# Run locally
streamlit run dashboard.py
```

### Troubleshooting
- **Secrets not working**: Ensure proper formatting in Streamlit Cloud secrets
- **Import errors**: Check requirements_streamlit.txt for cloud-compatible versions
- **Performance**: Streamlit Cloud has resource limits, optimize for cloud usage

### Support
For deployment issues, check:
- [Streamlit Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [Community Forum](https://discuss.streamlit.io)

---
**MailMate v2.0** - Enterprise AI Email Management System
