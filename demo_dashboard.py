"""
MailMate Demo Dashboard
Demo version that uses sample data instead of live email connection
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

# Custom CSS for professional appearance
st.set_page_config(
    page_title="MailMate Demo - AI Email Management",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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
    
    .demo-badge {
        background: linear-gradient(90deg, #ff6b6b, #ffa726);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
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
if 'demo_emails' not in st.session_state:
    st.session_state.demo_emails = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def load_demo_data():
    """Load demo data from JSON file"""
    try:
        with open('data/demo_results.json', 'r', encoding='utf-8') as f:
            demo_data = json.load(f)
        
        # Convert timestamp strings back to datetime objects
        for email in demo_data:
            if 'timestamp' in email:
                email['timestamp'] = datetime.fromisoformat(email['timestamp'])
        
        return demo_data
    except FileNotFoundError:
        # Return sample data if file doesn't exist
        return generate_sample_demo_data()
    except Exception as e:
        st.error(f"Error loading demo data: {e}")
        return generate_sample_demo_data()

def generate_sample_demo_data():
    """Generate sample demo data if file is missing"""
    return [
        {
            'id': '1',
            'sender': 'sarah.johnson@techcorp.com',
            'subject': 'URGENT: Project Deadline Tomorrow',
            'body': 'Hi Team, We need to finalize the quarterly project deliverables by tomorrow...',
            'timestamp': datetime.now() - timedelta(hours=2),
            'category': 'Urgent',
            'priority_score': 8.5,
            'priority_label': 'Critical',
            'summary': 'Project deadline tomorrow - need to finalize quarterly deliverables'
        },
        {
            'id': '2',
            'sender': 'noreply@deals.com',
            'subject': '🔥 Flash Sale - 70% Off!',
            'body': 'Don\'t miss our incredible flash sale...',
            'timestamp': datetime.now() - timedelta(hours=1),
            'category': 'Promotions',
            'priority_score': 2.1,
            'priority_label': 'Low',
            'summary': 'Flash sale with 70% discount on all products'
        }
    ]

def create_category_pie_chart(emails: List[Dict[str, Any]]):
    """Create pie chart for email categories"""
    if not emails:
        return None
    
    category_counts = {}
    for email in emails:
        category = email.get('category', 'Uncategorized')
        category_counts[category] = category_counts.get(category, 0) + 1
    
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

def create_priority_distribution_chart(emails: List[Dict[str, Any]]):
    """Create bar chart for priority distribution"""
    if not emails:
        return None
    
    priority_counts = {}
    for email in emails:
        priority = email.get('priority_label', 'Low')
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    priority_order = ['Critical', 'High', 'Medium', 'Low', 'Very Low']
    colors = ['#dc2626', '#ef4444', '#f59e0b', '#10b981', '#6b7280']
    
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
    """Display top priority emails"""
    if not emails:
        st.info("No emails to display")
        return
    
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
        
        if priority_label in ['Critical', 'High']:
            priority_class = 'priority-high'
        elif priority_label == 'Medium':
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
            
            col1, col2, col3 = st.columns([1, 1, 4])
            with col1:
                if st.button(f"🔊 Speak", key=f"speak_{i}"):
                    st.info("🔊 In real mode, this would speak the email summary!")
            
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
    """Demo email chatbot interface"""
    st.subheader("🤖 Email Assistant (Demo)")
    
    user_input = st.text_input("Ask about your emails:", placeholder="e.g., 'Show urgent emails from today'", key="chat_input")
    
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Demo responses
        demo_responses = {
            "urgent": "In demo mode: Found 2 urgent emails - 1 project deadline and 1 meeting reminder.",
            "today": "In demo mode: You received 5 emails today across Work, Finance, and Promotions categories.",
            "work": "In demo mode: You have 3 work emails including performance review and team standup.",
            "summary": "In demo mode: Total 10 emails with 3 high priority. Categories: Work(3), Finance(2), Promotions(3), Urgent(1), Spam(1)."
        }
        
        response = "In demo mode: This chatbot would analyze your real emails and provide intelligent responses based on AI processing."
        for keyword, demo_response in demo_responses.items():
            if keyword in user_input.lower():
                response = demo_response
                break
        
        st.session_state.chat_history.append({"role": "bot", "content": response})
    
    if st.session_state.chat_history:
        st.markdown("### 💬 Conversation")
        for message in st.session_state.chat_history[-6:]:
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
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

def main():
    """Main demo dashboard"""
    
    # Header with demo badge
    st.markdown('<h1 class="main-header">📧 MailMate - AI Email Management</h1>', unsafe_allow_html=True)
    st.markdown('<div class="demo-badge">🎮 DEMO MODE - Using Sample Data</div>', unsafe_allow_html=True)
    
    # Info about demo mode
    st.info("🎯 **Demo Mode Active**: This demo uses sample email data to showcase MailMate's features. To use with real emails, set up Gmail App Password in your .env file.")
    
    # Load demo data
    if not st.session_state.demo_emails:
        with st.spinner("Loading demo data..."):
            st.session_state.demo_emails = load_demo_data()
    
    emails = st.session_state.demo_emails
    
    if not emails:
        st.error("No demo data available. Please run setup_demo.py first.")
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Demo Control Panel")
        
        if st.button("🔄 Reload Demo Data", use_container_width=True):
            st.session_state.demo_emails = load_demo_data()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 Demo Stats")
        st.write(f"📧 **Total Emails:** {len(emails)}")
        
        categories = {}
        priorities = {}
        for email in emails:
            cat = email.get('category', 'Unknown')
            pri = email.get('priority_label', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
            priorities[pri] = priorities.get(pri, 0) + 1
        
        st.write("🏷️ **Categories:**")
        for cat, count in categories.items():
            st.write(f"  • {cat}: {count}")
        
        st.write("⭐ **Priorities:**")
        for pri, count in priorities.items():
            st.write(f"  • {pri}: {count}")
        
        st.markdown("---")
        st.markdown("### 🚀 Real Mode Setup")
        st.info("To use with real emails:\n1. Get Gmail App Password\n2. Update .env file\n3. Run: python main.py dashboard")
    
    # Main dashboard metrics
    st.markdown("### 📊 Dashboard Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_emails = len(emails)
    high_priority = sum(1 for e in emails if e.get('priority_score', 0) >= 6.0)
    categories_count = len(set(e.get('category', 'Unknown') for e in emails))
    recent_emails = sum(1 for e in emails if (datetime.now() - e.get('timestamp', datetime.now())).days <= 1)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{total_emails}</div>
            <div class="metric-label">Demo Emails</div>
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
            <div class="metric-value">{categories_count}</div>
            <div class="metric-label">Categories</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{recent_emails}</div>
            <div class="metric-label">Recent</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        fig_pie = create_category_pie_chart(emails)
        if fig_pie:
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        fig_priority = create_priority_distribution_chart(emails)
        if fig_priority:
            st.plotly_chart(fig_priority, use_container_width=True)
    
    st.markdown("---")
    
    # Two-column layout for emails and chatbot
    col1, col2 = st.columns([2, 1])
    
    with col1:
        display_top_priority_emails(emails)
    
    with col2:
        email_chatbot()

if __name__ == "__main__":
    main()
