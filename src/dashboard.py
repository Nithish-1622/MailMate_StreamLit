"""
MailMate Dashboard
Professional Streamlit interface for AI-driven email management system
Features: Email visualization, priority management, summarization, and chatbot
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json
from typing import List, Dict, Any
import time

# Import MailMate modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import EmailDataLoader
from src.classifier import EmailClassifier
from src.priority import PriorityScorer
from src.summarizer import EmailSummarizer
from src.tts import TTSEngine
from config.config import Config

# Page configuration
st.set_page_config(
    page_title="MailMate - AI Email Management",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #3b82f6;
        margin-bottom: 2rem;
    }
    
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    .priority-high {
        border-left: 4px solid #ef4444;
        padding-left: 1rem;
        background-color: #fef2f2;
    }
    
    .priority-medium {
        border-left: 4px solid #f59e0b;
        padding-left: 1rem;
        background-color: #fffbeb;
    }
    
    .priority-low {
        border-left: 4px solid #10b981;
        padding-left: 1rem;
        background-color: #f0fdf4;
    }
    
    .email-card {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: white;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .sidebar-section {
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .chat-message {
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        max-width: 80%;
    }
    
    .user-message {
        background-color: #3b82f6;
        color: white;
        margin-left: auto;
        text-align: right;
    }
    
    .bot-message {
        background-color: #f3f4f6;
        color: #374151;
        margin-right: auto;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'emails_data' not in st.session_state:
    st.session_state.emails_data = []
if 'processed_emails' not in st.session_state:
    st.session_state.processed_emails = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = None

# Initialize components
@st.cache_resource
def initialize_components():
    """Initialize all MailMate components"""
    return {
        'loader': EmailDataLoader(),
        'classifier': EmailClassifier(),
        'prioritizer': PriorityScorer(),
        'summarizer': EmailSummarizer(),
        'tts': TTSEngine()
    }

def check_configuration():
    """Check if all required configurations are available"""
    config_status = Config.validate_config()
    missing_configs = Config.get_missing_configs()
    
    if not config_status['all_ready']:
        st.error("⚠️ Configuration Required")
        st.warning("Please configure the following before using MailMate:")
        for config in missing_configs:
            st.write(f"• {config}")
        
        st.info("""
        **Setup Instructions:**
        1. Copy `.env.example` to `.env`
        2. Add your API keys and email credentials
        3. Restart the application
        """)
        
        with st.expander("Configuration Help"):
            st.write("""
            **Groq API Key:** Get free API key from https://console.groq.com
            **Gemini API Key:** Get free API key from https://makersuite.google.com
            **Email Setup:** For Gmail, use App Password instead of regular password
            """)
        
        return False
    
    return True

def load_and_process_emails(days: int = 7, force_refresh: bool = False):
    """Load emails and process them through the pipeline"""
    
    if not force_refresh and st.session_state.processed_emails:
        return st.session_state.processed_emails
    
    components = initialize_components()
    
    with st.spinner("🔄 Loading emails..."):
        # Load emails
        emails = components['loader'].fetch_recent_emails(days=days)
        
        if not emails:
            st.warning("No emails found. Please check your email configuration.")
            return []
        
        st.session_state.emails_data = emails
    
    with st.spinner("🤖 Processing emails with AI..."):
        # Classify emails
        classified_emails = components['classifier'].batch_classify(emails)
        
        # Prioritize emails
        prioritized_emails = components['prioritizer'].prioritize_emails(classified_emails)
        
        # Summarize emails
        final_emails = components['summarizer'].batch_summarize(prioritized_emails)
        
        st.session_state.processed_emails = final_emails
        st.session_state.last_refresh = datetime.now()
    
    return final_emails

def create_category_pie_chart(emails: List[Dict[str, Any]]):
    """Create pie chart for email categories"""
    if not emails:
        return None
    
    category_counts = {}
    for email in emails:
        category = email.get('category', 'Uncategorized')
        category_counts[category] = category_counts.get(category, 0) + 1
    
    # Define colors for categories
    color_map = {
        'Work': '#3b82f6',
        'Personal': '#10b981',
        'Finance': '#f59e0b',
        'Promotions': '#ef4444',
        'Spam': '#6b7280',
        'Urgent': '#dc2626',
        'Uncategorized': '#9ca3af'
    }
    
    colors = [color_map.get(cat, '#9ca3af') for cat in category_counts.keys()]
    
    fig = px.pie(
        values=list(category_counts.values()),
        names=list(category_counts.keys()),
        title="Email Distribution by Category",
        color_discrete_sequence=colors
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        font=dict(size=12),
        showlegend=True,
        height=400,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    return fig

def create_timeline_chart(emails: List[Dict[str, Any]]):
    """Create timeline chart for email trends"""
    if not emails:
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(emails)
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    
    # Group by date and category
    daily_counts = df.groupby(['date', 'category']).size().reset_index(name='count')
    
    fig = px.bar(
        daily_counts,
        x='date',
        y='count',
        color='category',
        title="Daily Email Trends by Category",
        labels={'date': 'Date', 'count': 'Number of Emails'},
        color_discrete_map={
            'Work': '#3b82f6',
            'Personal': '#10b981',
            'Finance': '#f59e0b',
            'Promotions': '#ef4444',
            'Spam': '#6b7280',
            'Urgent': '#dc2626'
        }
    )
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Number of Emails",
        height=400,
        hovermode='x unified'
    )
    
    return fig

def create_priority_distribution_chart(emails: List[Dict[str, Any]]):
    """Create bar chart for priority distribution"""
    if not emails:
        return None
    
    priority_counts = {}
    for email in emails:
        priority = email.get('priority_label', 'Low')
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    # Define order and colors
    priority_order = ['Critical', 'High', 'Medium', 'Low', 'Very Low']
    colors = ['#dc2626', '#ef4444', '#f59e0b', '#10b981', '#6b7280']
    
    # Filter and sort data
    sorted_data = []
    sorted_colors = []
    for priority in priority_order:
        if priority in priority_counts:
            sorted_data.append((priority, priority_counts[priority]))
            sorted_colors.append(colors[priority_order.index(priority)])
    
    if not sorted_data:
        return None
    
    priorities, counts = zip(*sorted_data)
    
    fig = go.Figure(data=[
        go.Bar(
            x=priorities,
            y=counts,
            marker_color=sorted_colors,
            text=counts,
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="Email Priority Distribution",
        xaxis_title="Priority Level",
        yaxis_title="Number of Emails",
        height=400,
        showlegend=False
    )
    
    return fig

def display_top_priority_emails(emails: List[Dict[str, Any]], limit: int = 5):
    """Display top priority emails in a formatted table"""
    if not emails:
        st.info("No emails to display")
        return
    
    # Sort by priority score
    top_emails = sorted(emails, key=lambda x: x.get('priority_score', 0), reverse=True)[:limit]
    
    st.subheader(f"🎯 Top {limit} Priority Emails")
    
    for i, email in enumerate(top_emails, 1):
        priority_score = email.get('priority_score', 0)
        priority_label = email.get('priority_label', 'Low')
        sender = email.get('sender', 'Unknown')
        subject = email.get('subject', 'No Subject')
        summary = email.get('summary', 'No summary available')
        timestamp = email.get('timestamp', datetime.now())
        category = email.get('category', 'Uncategorized')
        
        # Determine priority styling
        if priority_label == 'Critical':
            priority_class = 'priority-high'
        elif priority_label in ['High', 'Medium']:
            priority_class = 'priority-medium'
        else:
            priority_class = 'priority-low'
        
        with st.container():
            st.markdown(f"""
            <div class="email-card {priority_class}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <h4 style="margin: 0; color: #1f2937;">#{i} - {subject}</h4>
                    <span style="background-color: #3b82f6; color: white; padding: 0.2rem 0.5rem; border-radius: 12px; font-size: 0.8rem;">
                        {priority_label} ({priority_score:.1f})
                    </span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; color: #6b7280; font-size: 0.9rem;">
                    <span>📧 {sender}</span>
                    <span>🏷️ {category}</span>
                    <span>⏰ {timestamp.strftime('%m/%d %H:%M')}</span>
                </div>
                <div style="color: #374151; font-size: 0.95rem; line-height: 1.4;">
                    <strong>Summary:</strong> {summary}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            col1, col2, col3 = st.columns([1, 1, 4])
            with col1:
                if st.button(f"🔊 Speak", key=f"speak_{i}"):
                    components = initialize_components()
                    success = components['tts'].speak_email_summary(email)
                    if success:
                        st.success("Playing audio...")
                    else:
                        st.error("TTS failed")
            
            with col2:
                if st.button(f"📋 Details", key=f"details_{i}"):
                    with st.expander(f"Full Details - Email #{i}"):
                        st.write(f"**From:** {sender}")
                        st.write(f"**Subject:** {subject}")
                        st.write(f"**Category:** {category}")
                        st.write(f"**Priority:** {priority_label} ({priority_score:.2f})")
                        st.write(f"**Time:** {timestamp}")
                        st.write(f"**Body Preview:**")
                        st.text(email.get('body', 'No body')[:500] + "..." if len(email.get('body', '')) > 500 else email.get('body', ''))

def email_chatbot():
    """Email chatbot interface"""
    st.subheader("🤖 Email Assistant")
    
    # Chat input
    user_input = st.text_input("Ask about your emails:", placeholder="e.g., 'Show urgent emails from last week'", key="chat_input")
    
    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Process query
        response = process_email_query(user_input, st.session_state.processed_emails)
        
        # Add bot response to chat history
        st.session_state.chat_history.append({"role": "bot", "content": response})
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### 💬 Conversation")
        for message in st.session_state.chat_history[-6:]:  # Show last 6 messages
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    👤 {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message bot-message">
                    🤖 {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

def process_email_query(query: str, emails: List[Dict[str, Any]]) -> str:
    """Process natural language queries about emails"""
    query_lower = query.lower()
    
    if not emails:
        return "No emails available to search through."
    
    try:
        # Query handlers
        if 'urgent' in query_lower or 'critical' in query_lower:
            urgent_emails = [e for e in emails if e.get('priority_label') in ['Critical', 'High']]
            if urgent_emails:
                count = len(urgent_emails)
                top_sender = urgent_emails[0].get('sender', 'Unknown')
                return f"You have {count} urgent emails. Top priority is from {top_sender}: {urgent_emails[0].get('summary', 'No summary')}"
            else:
                return "No urgent emails found in your inbox."
        
        elif 'today' in query_lower:
            today = datetime.now().date()
            today_emails = [e for e in emails if e.get('timestamp', datetime.now()).date() == today]
            if today_emails:
                categories = {}
                for email in today_emails:
                    cat = email.get('category', 'Uncategorized')
                    categories[cat] = categories.get(cat, 0) + 1
                cat_summary = ', '.join([f"{count} {cat}" for cat, count in categories.items()])
                return f"You received {len(today_emails)} emails today: {cat_summary}. Top priority: {today_emails[0].get('summary', 'No summary')}"
            else:
                return "No emails received today."
        
        elif 'finance' in query_lower or 'bank' in query_lower or 'payment' in query_lower:
            finance_emails = [e for e in emails if e.get('category') == 'Finance']
            if finance_emails:
                count = len(finance_emails)
                summaries = [e.get('summary', 'No summary') for e in finance_emails[:3]]
                return f"You have {count} finance-related emails. Recent ones include: {'; '.join(summaries)}"
            else:
                return "No finance-related emails found."
        
        elif 'work' in query_lower or 'meeting' in query_lower:
            work_emails = [e for e in emails if e.get('category') == 'Work']
            if work_emails:
                count = len(work_emails)
                high_priority_work = [e for e in work_emails if e.get('priority_score', 0) >= 5.0]
                return f"You have {count} work emails, {len(high_priority_work)} are high priority. Latest: {work_emails[0].get('summary', 'No summary')}"
            else:
                return "No work-related emails found."
        
        elif 'summary' in query_lower or 'digest' in query_lower:
            total = len(emails)
            categories = {}
            high_priority = 0
            
            for email in emails:
                cat = email.get('category', 'Uncategorized')
                categories[cat] = categories.get(cat, 0) + 1
                if email.get('priority_score', 0) >= 6.0:
                    high_priority += 1
            
            top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]
            cat_text = ', '.join([f"{count} {cat}" for cat, count in top_categories])
            
            return f"Email summary: {total} total emails with {high_priority} high priority. Distribution: {cat_text}. Top priority: {emails[0].get('summary', 'No summary')}"
        
        elif 'count' in query_lower or 'how many' in query_lower:
            return f"You have {len(emails)} emails in your current view."
        
        else:
            # Generic search in email content
            search_terms = query_lower.split()
            matching_emails = []
            
            for email in emails:
                email_text = f"{email.get('subject', '')} {email.get('body', '')} {email.get('sender', '')}".lower()
                if any(term in email_text for term in search_terms):
                    matching_emails.append(email)
            
            if matching_emails:
                count = len(matching_emails)
                top_match = matching_emails[0]
                return f"Found {count} emails matching your search. Top result from {top_match.get('sender', 'Unknown')}: {top_match.get('summary', 'No summary')}"
            else:
                return "No emails found matching your search terms."
    
    except Exception as e:
        return f"Sorry, I encountered an error processing your query: {str(e)}"

def main():
    """Main dashboard application"""
    
    # Header
    st.markdown('<h1 class="main-header">📧 MailMate - AI Email Management</h1>', unsafe_allow_html=True)
    
    # Check configuration
    if not check_configuration():
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Control Panel")
        
        # Refresh controls
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh", use_container_width=True):
                load_and_process_emails(force_refresh=True)
                st.rerun()
        
        with col2:
            days_to_fetch = st.selectbox("📅 Days", [1, 3, 7, 14], index=2)
        
        # Last refresh info
        if st.session_state.last_refresh:
            st.caption(f"Last updated: {st.session_state.last_refresh.strftime('%H:%M:%S')}")
        
        st.markdown("---")
        
        # TTS Controls
        st.markdown("### 🔊 Audio Controls")
        if st.button("📻 Daily Digest", use_container_width=True):
            if st.session_state.processed_emails:
                components = initialize_components()
                top_emails = sorted(st.session_state.processed_emails, 
                                  key=lambda x: x.get('priority_score', 0), 
                                  reverse=True)[:5]
                
                digest_text = components['tts']._generate_digest_script(top_emails)
                
                with st.spinner("🎵 Generating audio..."):
                    success = components['tts'].speak_text(digest_text)
                    if success:
                        st.success("Playing daily digest!")
                    else:
                        st.error("Audio playback failed")
            else:
                st.warning("No emails to read")
        
        st.markdown("---")
        
        # Settings
        st.markdown("### ⚙️ Settings")
        
        # VIP Senders management
        with st.expander("👑 VIP Senders"):
            st.text_area("Add VIP email addresses (one per line):", 
                        value="\n".join(Config.VIP_SENDERS),
                        key="vip_senders")
            
            if st.button("💾 Update VIP List"):
                new_vips = st.session_state.vip_senders.strip().split('\n')
                new_vips = [vip.strip() for vip in new_vips if vip.strip()]
                Config.VIP_SENDERS = new_vips
                st.success("VIP list updated!")
    
    # Load emails
    emails = load_and_process_emails(days=days_to_fetch)
    
    if not emails:
        st.info("No emails found. Please check your email configuration or try refreshing.")
        return
    
    # Main dashboard
    
    # Key metrics
    st.markdown("### 📊 Dashboard Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_emails = len(emails)
    high_priority = sum(1 for e in emails if e.get('priority_score', 0) >= 6.0)
    categories = len(set(e.get('category', 'Unknown') for e in emails))
    today_emails = sum(1 for e in emails if e.get('timestamp', datetime.now()).date() == datetime.now().date())
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{total_emails}</div>
            <div class="metric-label">Total Emails</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{high_priority}</div>
            <div class="metric-label">High Priority</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{categories}</div>
            <div class="metric-label">Categories</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{today_emails}</div>
            <div class="metric-label">Today</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        # Category pie chart
        fig_pie = create_category_pie_chart(emails)
        if fig_pie:
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Priority distribution
        fig_priority = create_priority_distribution_chart(emails)
        if fig_priority:
            st.plotly_chart(fig_priority, use_container_width=True)
    
    # Timeline chart
    fig_timeline = create_timeline_chart(emails)
    if fig_timeline:
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    st.markdown("---")
    
    # Two-column layout for emails and chatbot
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Top priority emails
        display_top_priority_emails(emails)
    
    with col2:
        # Email chatbot
        email_chatbot()

if __name__ == "__main__":
    main()
