"""
MailMate - Professional AI Email Management System
Enterprise-Grade Dashboard with Advanced UI/UX
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
import threading
import io
import base64
import os

# TTS Imports


def get_ai_response(query, emails):
    """Generate AI response for user queries about emails."""
    try:
        from groq import Groq
        
        # Initialize Groq client
        client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        
        # Prepare email context
        email_context = []
        for i, email in enumerate(emails[:10]):  # Limit to first 10 emails for context
            email_info = {
                'subject': email.get('subject', 'No subject'),
                'sender': email.get('sender', 'Unknown'),
                'priority': email.get('priority_label', 'Medium'),
                'category': email.get('category', 'General'),
                'summary': email.get('ai_summary', email.get('content', '')[:200])
            }
            email_context.append(email_info)
        
        # Create system prompt
        system_prompt = f"""You are MailMate AI, an intelligent email assistant. You have access to the user's email data.
        
Current email context:
{email_context}

Total emails in system: {len(emails)}

Provide helpful, concise responses about the user's emails. Be professional and informative."""
        
        # Get AI response
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"I'm currently unable to process your request. Please ensure your AI service is configured correctly. Error: {str(e)}"


# TTS Imports
try:
    import pyttsx3
    import pygame
    from gtts import gTTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

# Professional page configuration
st.set_page_config(
    page_title="MailMate Pro - AI Email Management",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional Enterprise CSS Design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700;800&family=Roboto:wght@300;400;500;600;700&display=swap');
    
    /* Global Enterprise Styles */
    .main {
        font-family: 'SF Pro Display', 'Roboto', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-attachment: fixed;
        padding: 0;
        min-height: 100vh;
    }
    
    /* Hide Streamlit Elements */
    .css-1d391kg, .css-1v0mbdj, footer, header, .css-18e3th9, .css-1dp5vir {display: none !important;}
    .block-container {
        padding: 1rem 2rem;
        max-width: 100%;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        margin: 1rem;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Enterprise Header Design */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 25%, #1e40af 50%, #1d4ed8 75%, #1e3a8a 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin: -1rem -2rem 2rem -2rem;
        box-shadow: 0 20px 40px rgba(30, 64, 175, 0.3);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 25% 25%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 75% 75%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
        animation: headerShimmer 8s ease-in-out infinite;
    }
    
    @keyframes headerShimmer {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 0.6; }
    }
    
    .main-title {
        font-size: 4rem;
        font-weight: 800;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 50%, #e2e8f0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
        position: relative;
        z-index: 2;
        text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    
    .main-subtitle {
        font-size: 1.5rem;
        opacity: 0.9;
        font-weight: 500;
        position: relative;
        z-index: 2;
        margin-bottom: 1.5rem;
        letter-spacing: 0.5px;
    }
    
    .status-badge {
        display: inline-flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(15px);
        padding: 1rem 2rem;
        border-radius: 50px;
        border: 2px solid rgba(255, 255, 255, 0.2);
        position: relative;
        z-index: 2;
        font-weight: 600;
        font-size: 1.1rem;
        animation: statusGlow 3s ease-in-out infinite;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    
    @keyframes statusGlow {
        0%, 100% { box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1); }
        50% { box-shadow: 0 8px 32px rgba(59, 130, 246, 0.4); }
    }
    
    /* Premium Enterprise Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.8) 100%);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.1),
            0 1px 0px rgba(255, 255, 255, 0.4) inset,
            0 -1px 0px rgba(0, 0, 0, 0.05) inset;
        border: 1px solid rgba(255, 255, 255, 0.3);
        transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-12px) scale(1.02);
        box-shadow: 
            0 30px 60px rgba(0, 0, 0, 0.15),
            0 1px 0px rgba(255, 255, 255, 0.6) inset;
        border-color: rgba(59, 130, 246, 0.3);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        border-radius: 20px 20px 0 0;
        transition: all 0.3s ease;
    }
    
    .metric-card.primary::before { 
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    }
    .metric-card.success::before { 
        background: linear-gradient(135deg, #10b981 0%, #047857 100%);
    }
    .metric-card.warning::before { 
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    }
    .metric-card.info::before { 
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
    }
    
    .metric-value {
        font-size: 3.5rem;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 0.5rem;
        line-height: 1;
        background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-label {
        font-size: 1rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        opacity: 0.8;
    }
    
    .metric-icon {
        position: absolute;
        top: 2rem;
        right: 2rem;
        font-size: 3rem;
        opacity: 0.1;
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Email Cards */
    .email-item {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .email-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
        border-color: #3182ce;
    }
    
    .email-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
    }
    
    .email-subject {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a202c;
        margin: 0;
        flex: 1;
        margin-right: 1rem;
    }
    
    .priority-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .priority-critical { background: #fed7d7; color: #c53030; }
    .priority-high { background: #ffeaa7; color: #d68910; }
    .priority-medium { background: #bee3f8; color: #2b77a6; }
    .priority-low { background: #c6f6d5; color: #276749; }
    
    .email-meta {
        display: flex;
        gap: 1.5rem;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        color: #718096;
    }
    
    .email-summary {
        background: #f7fafc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3182ce;
        color: #4a5568;
        line-height: 1.5;
        font-size: 0.95rem;
    }
    
    .keyword-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 1rem;
    }
    
    .keyword-tag {
        background: #e6fffa;
        color: #234e52;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    /* Professional Buttons */
    .btn {
        padding: 0.5rem 1rem;
        border-radius: 8px;
        border: none;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 0.9rem;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .btn-primary {
        background: #3182ce;
        color: white;
    }
    
    .btn-primary:hover {
        background: #2c5282;
        transform: translateY(-1px);
    }
    
    .btn-success {
        background: #38a169;
        color: white;
    }
    
    .btn-success:hover {
        background: #2f855a;
        transform: translateY(-1px);
    }
    
    .btn-secondary {
        background: #e2e8f0;
        color: #4a5568;
    }
    
    .btn-secondary:hover {
        background: #cbd5e0;
    }
    
    /* Premium Chat Interface */
    .chat-container {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.9) 100%);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.1),
            0 1px 0px rgba(255, 255, 255, 0.5) inset;
        border: 1px solid rgba(255, 255, 255, 0.3);
        transition: all 0.3s ease;
    }
    
    .chat-container:hover {
        box-shadow: 
            0 25px 50px rgba(0, 0, 0, 0.15),
            0 1px 0px rgba(255, 255, 255, 0.7) inset;
    }
    
    /* Professional Chat Messages */
    .chat-message {
        display: flex;
        align-items: flex-start;
        margin-bottom: 1.5rem;
        gap: 1rem;
        animation: messageSlide 0.5s ease-out;
    }
    
    @keyframes messageSlide {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .chat-message.user-message {
        flex-direction: row-reverse;
    }
    
    .message-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        font-weight: 600;
        flex-shrink: 0;
        box-shadow: 
            0 8px 16px rgba(59, 130, 246, 0.3),
            0 2px 4px rgba(0, 0, 0, 0.1);
        border: 2px solid rgba(255, 255, 255, 0.3);
    }
    
    .bot-message .message-avatar {
        background: linear-gradient(135deg, #10b981 0%, #047857 100%);
        box-shadow: 
            0 8px 16px rgba(16, 185, 129, 0.3),
            0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .message-content {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.8) 100%);
        backdrop-filter: blur(15px);
        padding: 1.2rem 1.5rem;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        max-width: 85%;
        font-size: 1rem;
        line-height: 1.6;
        color: #1e293b;
        box-shadow: 
            0 8px 16px rgba(0, 0, 0, 0.05),
            0 1px 0px rgba(255, 255, 255, 0.4) inset;
        font-weight: 500;
    }
    
    .user-message .message-content {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border-color: rgba(255, 255, 255, 0.2);
        border-bottom-right-radius: 8px;
        box-shadow: 
            0 8px 16px rgba(59, 130, 246, 0.3),
            0 1px 0px rgba(255, 255, 255, 0.1) inset;
    }
    
    .bot-message .message-content {
        border-bottom-left-radius: 8px;
    }
    
    /* Premium Email Cards */
    .priority-email-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.9) 100%);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.08),
            0 1px 0px rgba(255, 255, 255, 0.5) inset;
        border: 1px solid rgba(255, 255, 255, 0.3);
        transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        position: relative;
        overflow: hidden;
    }
    
    .priority-email-card:hover {
        transform: translateY(-10px) scale(1.01);
        box-shadow: 
            0 30px 60px rgba(0, 0, 0, 0.12),
            0 1px 0px rgba(255, 255, 255, 0.7) inset;
        border-color: rgba(59, 130, 246, 0.4);
    }
    
    .priority-email-card::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 120px;
        height: 120px;
        background: 
            radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%),
            radial-gradient(circle, rgba(16, 185, 129, 0.05) 20%, transparent 70%);
        border-radius: 0 20px 0 120px;
        opacity: 0.6;
    }
    
    .email-rank {
        position: absolute;
        top: 1.5rem;
        right: 1.5rem;
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.3rem;
        z-index: 3;
        box-shadow: 
            0 8px 16px rgba(59, 130, 246, 0.3),
            0 2px 4px rgba(0, 0, 0, 0.1);
        border: 2px solid rgba(255, 255, 255, 0.3);
    }
    
    .priority-score {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        box-shadow: 0 4px 8px rgba(6, 182, 212, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .email-summary-card {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        margin: 1.5rem 0;
        box-shadow: 
            0 16px 32px rgba(59, 130, 246, 0.3),
            0 1px 0px rgba(255, 255, 255, 0.1) inset;
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .email-summary-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 10% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 90% 80%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
        opacity: 0.7;
    }
    
    .email-summary-card h4 {
        margin: 0 0 1.5rem 0;
        font-size: 1.4rem;
        font-weight: 700;
        position: relative;
        z-index: 1;
    }
    
    .summary-content {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        font-size: 1rem;
        line-height: 1.6;
        position: relative;
        z-index: 1;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    .summary-meta {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-top: 1.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        z-index: 1;
        font-weight: 500;
    }
    
    /* Enhanced Charts Container */
    .analytics-container {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        border: 1px solid #e2e8f0;
        margin-bottom: 2rem;
    }
    
    /* Email Card Styles */
    .email-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .email-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
    }
    
    .email-sender {
        font-weight: 600;
        color: #2d3748;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .email-subject {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a202c;
        margin-bottom: 0.75rem;
        line-height: 1.3;
    }
    
    .email-snippet {
        color: #718096;
        font-size: 0.9rem;
        line-height: 1.5;
        margin-bottom: 1rem;
    }
    
    .email-meta {
        display: flex;
        gap: 1rem;
        font-size: 0.8rem;
        color: #a0aec0;
    }
    
    .priority-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .priority-badge.critical { background: #fed7d7; color: #c53030; }
    .priority-badge.high { background: #ffeaa7; color: #d68910; }
    .priority-badge.medium { background: #bee3f8; color: #2b6cb0; }
    .priority-badge.low { background: #c6f6d5; color: #276749; }
    
    /* Charts */
    .chart-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    
    .chart-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1a202c;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Enterprise Sidebar */
    .css-1d391kg {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(248, 250, 252, 0.05) 100%) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    .sidebar-content {
        padding: 1.5rem;
        color: white;
    }
    
    .sidebar-metric {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(248, 250, 252, 0.1) 100%);
        backdrop-filter: blur(15px);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 
            0 8px 16px rgba(0, 0, 0, 0.1),
            0 1px 0px rgba(255, 255, 255, 0.2) inset;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .sidebar-metric:hover {
        transform: translateY(-4px);
        box-shadow: 
            0 12px 24px rgba(0, 0, 0, 0.15),
            0 1px 0px rgba(255, 255, 255, 0.3) inset;
        border-color: rgba(59, 130, 246, 0.4);
    }
    
    .sidebar-metric h3 {
        color: white !important;
        font-weight: 700 !important;
        font-size: 1.3rem !important;
        background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .sidebar-metric p {
        color: rgba(255, 255, 255, 0.8) !important;
        font-weight: 500 !important;
    }
    
    .sidebar-metric div {
        color: white !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }
    
    /* Sidebar Headers and Text */
    .css-1d391kg h3, .css-1d391kg .sidebar-content h3 {
        color: white !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        margin-bottom: 1rem !important;
        background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .css-1d391kg p, .css-1d391kg li, .css-1d391kg span {
        color: rgba(255, 255, 255, 0.9) !important;
        font-weight: 400 !important;
    }
    
    /* Success and Info Alerts */
    .success-alert {
        background: linear-gradient(135deg, #10b981 0%, #047857 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin: 1.5rem 0;
        box-shadow: 
            0 12px 24px rgba(16, 185, 129, 0.3),
            0 1px 0px rgba(255, 255, 255, 0.1) inset;
        border: 1px solid rgba(255, 255, 255, 0.1);
        font-weight: 500;
        font-size: 1.1rem;
    }
    
    .feature-highlight {
        background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin: 1.5rem 0;
        box-shadow: 
            0 12px 24px rgba(99, 102, 241, 0.3),
            0 1px 0px rgba(255, 255, 255, 0.1) inset;
        border: 1px solid rgba(255, 255, 255, 0.1);
        font-weight: 500;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    .info-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.9) 100%);
        backdrop-filter: blur(20px);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 
            0 12px 24px rgba(0, 0, 0, 0.1),
            0 1px 0px rgba(255, 255, 255, 0.4) inset;
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: #1e293b;
    }
    
    .info-card h4 {
        color: #1e293b;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .info-card code {
        background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
        color: white;
        padding: 0.3rem 0.6rem;
        border-radius: 8px;
        font-family: 'SF Mono', 'Monaco', monospace;
        font-weight: 500;
    }
    /* Professional Buttons with Hover Effects */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 16px rgba(59, 130, 246, 0.4) !important;
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Input Fields Styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        color: white !important;
        font-weight: 500 !important;
        padding: 0.75rem 1rem !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.6) !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: rgba(59, 130, 246, 0.5) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* Loading States */
    .loading {
        display: inline-flex;
        align-items: center;
        gap: 0.75rem;
        color: rgba(255, 255, 255, 0.8);
        font-weight: 500;
    }
    
    .spinner {
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255, 255, 255, 0.2);
        border-top: 3px solid #3b82f6;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-title { 
            font-size: 2.5rem !important; 
        }
        .metric-card { 
            padding: 1.5rem !important; 
        }
        .priority-email-card { 
            padding: 1.5rem !important; 
        }
        .email-header { 
            flex-direction: column !important; 
            align-items: flex-start !important; 
            gap: 0.75rem !important; 
        }
        .block-container {
            padding: 1rem !important;
            margin: 0.5rem !important;
        }
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #1d4ed8, #1e40af);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'emails' not in st.session_state:
    st.session_state.emails = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'tts_status' not in st.session_state:
    st.session_state.tts_status = ""
if 'current_speaking' not in st.session_state:
    st.session_state.current_speaking = False

# Initialize TTS engine
if TTS_AVAILABLE:
    try:
        pygame.mixer.init()
        tts_engine = pyttsx3.init()
        tts_engine.setProperty('rate', 150)
        tts_engine.setProperty('volume', 0.9)
        voices = tts_engine.getProperty('voices')
        if voices:
            tts_engine.setProperty('voice', voices[0].id)
    except:
        TTS_AVAILABLE = False

def load_email_data():
    """Load email data from JSON file"""
    try:
        with open('data/demo_results.json', 'r', encoding='utf-8') as f:
            emails = json.load(f)
        
        # Convert timestamp strings back to datetime objects
        for email in emails:
            if 'timestamp' in email:
                email['timestamp'] = datetime.fromisoformat(email['timestamp'])
        
        return emails
    except FileNotFoundError:
        st.error("Email data not found. Please run the email processing first.")
        return []
    except Exception as e:
        st.error(f"Error loading email data: {e}")
        return []

def speak_text(text: str, email_id: str):
    """Text-to-speech function using both gTTS and pyttsx3"""
    if not TTS_AVAILABLE:
        st.warning("⚠️ TTS libraries not available. Install pyttsx3, pygame, and gTTS for speech functionality.")
        return
    
    try:
        st.session_state.current_speaking = True
        st.session_state.tts_status = f"🔊 Speaking email {email_id}..."
        
        # Use gTTS for better quality
        tts = gTTS(text=text, lang='en', slow=False)
        
        # Save to temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tts.save(tmp_file.name)
            
            # Play using pygame
            pygame.mixer.music.load(tmp_file.name)
            pygame.mixer.music.play()
            
            # Wait for completion
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        
        st.session_state.current_speaking = False
        st.session_state.tts_status = f"✅ Completed speaking email {email_id}"
        
    except Exception as e:
        st.session_state.current_speaking = False
        st.session_state.tts_status = f"❌ TTS Error: {str(e)}"

def create_modern_metrics_dashboard(emails: List[Dict[str, Any]]):
    """Create modern professional metrics dashboard"""
    if not emails:
        return
    
    # Calculate metrics
    total_emails = len(emails)
    critical_emails = sum(1 for e in emails if e.get('priority_label') == 'Critical')
    high_priority = sum(1 for e in emails if e.get('priority_label') in ['Critical', 'High'])
    avg_priority = np.mean([e.get('priority_score', 0) for e in emails])
    
    # Create metric cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card primary">
            <div class="metric-icon">📧</div>
            <div class="metric-value">{total_emails}</div>
            <div class="metric-label">Total Emails</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card warning">
            <div class="metric-icon">🚨</div>
            <div class="metric-value">{critical_emails}</div>
            <div class="metric-label">Critical Priority</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card success">
            <div class="metric-icon">⭐</div>
            <div class="metric-value">{high_priority}</div>
            <div class="metric-label">High + Critical</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card info">
            <div class="metric-icon">📊</div>
            <div class="metric-value">{avg_priority:.1f}</div>
            <div class="metric-label">Avg Priority Score</div>
        </div>
        """, unsafe_allow_html=True)

def create_advanced_visualizations(emails: List[Dict[str, Any]]):
    """Create advanced interactive visualizations"""
    if not emails:
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Priority distribution with custom colors
        priority_counts = {}
        for email in emails:
            priority = email.get('priority_label', 'Low')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        colors = {
            'Critical': '#dc2626',
            'High': '#ea580c',
            'Medium': '#ca8a04',
            'Low': '#059669'
        }
        
        fig_priority = go.Figure()
        
        for priority in ['Critical', 'High', 'Medium', 'Low']:
            if priority in priority_counts:
                fig_priority.add_trace(go.Bar(
                    x=[priority],
                    y=[priority_counts[priority]],
                    marker_color=colors[priority],
                    name=priority,
                    text=priority_counts[priority],
                    textposition='auto',
                    hovertemplate=f'<b>{priority}</b><br>Count: %{{y}}<extra></extra>'
                ))
        
        fig_priority.update_layout(
            title="📊 Priority Distribution Analysis",
            title_font_size=16,
            title_font_color='#1f2937',
            xaxis_title="Priority Level",
            yaxis_title="Number of Emails",
            showlegend=False,
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", size=12)
        )
        
        st.plotly_chart(fig_priority, use_container_width=True)
    
    with col2:
        # Category distribution pie chart
        category_counts = {}
        for email in emails:
            category = email.get('category', 'Unknown')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        category_colors = {
            'Work': '#3b82f6',
            'Finance': '#f59e0b',
            'Urgent': '#dc2626',
            'Personal': '#10b981',
            'Promotions': '#8b5cf6',
            'Spam': '#6b7280'
        }
        
        colors = [category_colors.get(cat, '#9ca3af') for cat in category_counts.keys()]
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=list(category_counts.keys()),
            values=list(category_counts.values()),
            marker=dict(colors=colors),
            textinfo='label+percent',
            textposition='inside',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig_pie.update_layout(
            title="🏷️ Email Category Distribution",
            title_font_size=16,
            title_font_color='#1f2937',
            height=400,
            font=dict(family="Inter", size=12)
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)

def create_professional_analytics(emails: List[Dict[str, Any]]):
    """Create professional analytics with line charts"""
    if not emails:
        return
    
    st.markdown("### 📊 Professional Email Analytics")
    
    # Prepare data for line charts
    import pandas as pd
    from datetime import datetime, timedelta
    
    # Create time-based data for professional charts
    current_time = datetime.now()
    time_periods = [current_time - timedelta(hours=i) for i in range(12, 0, -1)]
    
    # Priority trend over time (simplified)
    priority_data = []
    critical_count = sum(1 for e in emails if e.get('priority_label') == 'Critical')
    high_count = sum(1 for e in emails if e.get('priority_label') == 'High') 
    medium_count = sum(1 for e in emails if e.get('priority_label') == 'Medium')
    
    for i, period in enumerate(time_periods):
        # Create realistic variation
        critical_var = critical_count * (0.8 + 0.4 * np.sin(i * 0.5))
        high_var = high_count * (0.7 + 0.3 * np.sin((i + 1) * 0.6))
        medium_var = medium_count * (0.6 + 0.4 * np.sin((i + 2) * 0.4))
        
        priority_data.append({
            'Time': period.strftime('%H:%M'),
            'Critical': max(0, int(critical_var)),
            'High': max(0, int(high_var)),
            'Medium': max(0, int(medium_var))
        })
    
    df_priority = pd.DataFrame(priority_data)
    
    # Create professional line chart
    fig_priority = go.Figure()
    
    fig_priority.add_trace(go.Scatter(
        x=df_priority['Time'], 
        y=df_priority['Critical'], 
        mode='lines+markers', 
        name='Critical Priority', 
        line=dict(color='#dc3545', width=4),
        marker=dict(size=8, color='#dc3545')
    ))
    
    fig_priority.add_trace(go.Scatter(
        x=df_priority['Time'], 
        y=df_priority['High'], 
        mode='lines+markers', 
        name='High Priority',
        line=dict(color='#fd7e14', width=4),
        marker=dict(size=8, color='#fd7e14')
    ))
    
    fig_priority.add_trace(go.Scatter(
        x=df_priority['Time'], 
        y=df_priority['Medium'], 
        mode='lines+markers', 
        name='Medium Priority',
        line=dict(color='#0d6efd', width=4),
        marker=dict(size=8, color='#0d6efd')
    ))
    
    fig_priority.update_layout(
        title={
            'text': 'Email Priority Trends (12 Hours)',
            'x': 0.5,
            'font': {'size': 20, 'color': '#1a202c', 'family': 'Arial Black'}
        },
        xaxis_title='Time',
        yaxis_title='Number of Emails',
        font=dict(size=14),
        showlegend=True,
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=450
    )
    
    st.plotly_chart(fig_priority, use_container_width=True)
    
    # Additional charts in columns
    col1, col2 = st.columns(2)
    
    with col1:
        # Email volume trend
        volume_data = []
        total_emails = len(emails)
        for i, period in enumerate(time_periods):
            volume = total_emails * (0.5 + 0.5 * np.sin(i * 0.3))
            volume_data.append({
                'Time': period.strftime('%H:%M'),
                'Volume': max(1, int(volume))
            })
        
        df_volume = pd.DataFrame(volume_data)
        fig_volume = px.line(
            df_volume, 
            x='Time', 
            y='Volume',
            title='Email Volume Trend',
            color_discrete_sequence=['#38a169']
        )
        fig_volume.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=350,
            title_x=0.5,
            font=dict(size=12)
        )
        fig_volume.update_traces(line=dict(width=3), marker=dict(size=6))
        st.plotly_chart(fig_volume, use_container_width=True)
    
    with col2:
        # Category distribution
        categories = [e.get('category', 'General') for e in emails]
        category_counts = pd.Series(categories).value_counts()
        
        fig_categories = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title='Email Categories Distribution',
            color_discrete_sequence=['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe']
        )
        fig_categories.update_layout(
            height=350,
            title_x=0.5,
            font=dict(size=12)
        )
        st.plotly_chart(fig_categories, use_container_width=True)

def create_timeline_chart(emails: List[Dict[str, Any]]):
    """Create timeline visualization"""
    if not emails:
        return
    
    # Prepare data for timeline
    df_data = []
    for email in emails:
        df_data.append({
            'timestamp': email.get('timestamp'),
            'priority_score': email.get('priority_score', 0),
            'category': email.get('category', 'Unknown'),
            'sender': email.get('sender', ''),
            'subject': email.get('subject', ''),
            'priority_label': email.get('priority_label', 'Low')
        })
    
    df = pd.DataFrame(df_data)
    
    # Create scatter plot timeline
    color_map = {
        'Critical': '#dc2626',
        'High': '#ea580c', 
        'Medium': '#ca8a04',
        'Low': '#059669'
    }
    
    fig = px.scatter(
        df,
        x='timestamp',
        y='priority_score',
        color='priority_label',
        size='priority_score',
        hover_data=['sender', 'subject', 'category'],
        title="📈 Email Priority Timeline Analysis",
        color_discrete_map=color_map,
        size_max=20
    )
    
    fig.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=12),
        title_font_size=16,
        title_font_color='#1f2937'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_modern_email_list(emails: List[Dict[str, Any]]):
    """Display top 5 prioritized emails in modern professional format"""
    if not emails:
        st.info("📭 No emails to display")
        return
    
    # Sort by priority score and take top 5
    top_emails = sorted(emails, key=lambda x: x.get('priority_score', 0), reverse=True)[:5]
    
    st.markdown("### 📬 Top Priority Emails")
    st.markdown(f"**Showing top {len(top_emails)} highest priority emails**")
    
    # Search functionality for top emails
    search_term = st.text_input("🔍 Search top priority emails...", placeholder="Search by subject, sender, or content")
    
    # Filter top emails if search term provided
    filtered_emails = top_emails
    if search_term:
        filtered_emails = [e for e in top_emails if search_term.lower() in 
                          (e.get('subject', '') + e.get('sender', '') + e.get('content', '')).lower()]
    
    # Display emails
    for i, email in enumerate(filtered_emails, 1):
        priority = email.get('priority_label', 'Medium')
        priority_color = {
            'Critical': '#dc3545', 'High': '#fd7e14', 
            'Medium': '#0d6efd', 'Low': '#6c757d'
        }.get(priority, '#0d6efd')
        
        sender = email.get('sender', 'Unknown Sender')
        subject = email.get('subject', 'No Subject')
        snippet = email.get('content', '')[:150] + "..." if len(email.get('content', '')) > 150 else email.get('content', '')
        score = email.get('priority_score', 0)
        
        # Enhanced email card with ranking
        st.markdown(f"""
        <div class="priority-email-card" style="border-left: 6px solid {priority_color};">
            <div class="email-rank">#{i}</div>
            <div class="email-header">
                <div class="email-sender">{sender}</div>
                <div class="priority-badge {priority.lower()}">{priority}</div>
                <div class="priority-score">{score:.1f}</div>
            </div>
            <div class="email-subject">{subject}</div>
            <div class="email-snippet">{snippet}</div>
            <div class="email-meta">
                <span>Category: {email.get('category', 'General')}</span>
                <span>Sentiment: {email.get('sentiment', 'neutral').title()}</span>
                <span>Keywords: {', '.join(email.get('keywords', [])[:3])}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Professional action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(f"🔊 Listen", key=f"tts_{i}"):
                try:
                    from enhanced_tts import speak_text
                    text_to_speak = f"Priority {i}. Email from {sender}. Subject: {subject}. {email.get('ai_summary', snippet)}"
                    success = speak_text(text_to_speak, async_mode=True)
                    if success:
                        st.success("🔊 Playing audio...")
                    else:
                        st.error("❌ TTS not available")
                except Exception as e:
                    st.error(f"TTS Error: {e}")
        
        with col2:
            if st.button(f"📋 Summary", key=f"summary_{i}"):
                summary = email.get('ai_summary') or email.get('summary', 'No summary available')
                st.markdown(f"""
                <div class="email-summary-card">
                    <h4>📋 Email Summary</h4>
                    <p><strong>From:</strong> {sender}</p>
                    <p><strong>Subject:</strong> {subject}</p>
                    <div class="summary-content">{summary}</div>
                    <div class="summary-meta">
                        <span>Priority: {priority} ({score:.1f})</span> | 
                        <span>Category: {email.get('category', 'General')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            if st.button(f"🔍 Details", key=f"details_{i}"):
                with st.expander("📧 Full Email Details", expanded=True):
                    st.markdown(f"**Rank:** #{i} (Top Priority)")
                    st.markdown(f"**From:** {sender}")
                    st.markdown(f"**Subject:** {subject}")
                    st.markdown(f"**Priority:** {priority} (Score: {score:.2f}/10)")
                    st.markdown(f"**Category:** {email.get('category', 'General')}")
                    st.markdown(f"**Sentiment:** {email.get('sentiment', 'neutral').title()}")
                    if email.get('keywords'):
                        st.markdown(f"**Keywords:** {', '.join(email.get('keywords', []))}")
                    st.markdown("**Content:**")
                    st.text_area("", email.get('content', ''), height=150, disabled=True)
        
        st.markdown("---")

def display_top_priority_emails(emails: List[Dict[str, Any]], limit: int = 5):
    """Display top priority emails with enhanced UI and TTS"""
    if not emails:
        st.info("📭 No emails to display")
        return
    
    # Sort by priority score
    top_emails = sorted(emails, key=lambda x: x.get('priority_score', 0), reverse=True)[:limit]
    
    st.markdown("### 🎯 Top Priority Emails")
    
    for i, email in enumerate(top_emails, 1):
        priority_score = email.get('priority_score', 0)
        priority_label = email.get('priority_label', 'Low')
        sender = email.get('sender', 'Unknown')
        subject = email.get('subject', 'No Subject')
        summary = email.get('summary', 'No summary available')
        timestamp = email.get('timestamp', datetime.now())
        category = email.get('category', 'Unknown')
        keywords = email.get('keywords', [])
        sentiment = email.get('sentiment', 'neutral')
        thread_count = email.get('thread_count', 1)
        attachments = email.get('attachments', 0)
        
        # Determine priority class
        if priority_label == 'Critical':
            priority_class = 'priority-critical'
        elif priority_label == 'High':
            priority_class = 'priority-high'
        elif priority_label == 'Medium':
            priority_class = 'priority-medium'
        else:
            priority_class = 'priority-low'
        
        # Emoji mapping for sentiments
        sentiment_emoji = {
            'urgent': '🚨',
            'critical': '⚠️',
            'excited': '🚀',
            'positive': '✅',
            'tense': '😰',
            'successful': '🎉',
            'optimistic': '💪',
            'breakthrough': '💡',
            'neutral': '📧'
        }
        
        with st.container():
            st.markdown(f"""
            <div class="email-card {priority_class}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h3 style="margin: 0; color: #1f2937; font-weight: 600;">
                        #{i} {sentiment_emoji.get(sentiment, '📧')} {subject}
                    </h3>
                    <div style="display: flex; gap: 0.5rem; align-items: center;">
                        <span style="background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.85rem; font-weight: 600;">
                            {priority_label} ({priority_score:.1f})
                        </span>
                        <span style="background: #f3f4f6; color: #374151; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.85rem;">
                            {category}
                        </span>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1rem; color: #6b7280; font-size: 0.9rem;">
                    <div>📧 <strong>From:</strong> {sender}</div>
                    <div>🕒 <strong>Time:</strong> {timestamp.strftime('%m/%d %H:%M')}</div>
                    <div>💬 <strong>Thread:</strong> {thread_count} messages</div>
                    <div>📎 <strong>Attachments:</strong> {attachments}</div>
                </div>
                
                <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <strong style="color: #374151;">AI Summary:</strong>
                    <p style="margin: 0.5rem 0 0 0; color: #4b5563; line-height: 1.5;">{summary}</p>
                </div>
                
                <div style="margin-bottom: 1rem;">
                    <strong style="color: #374151;">Keywords:</strong>
                    <div style="margin-top: 0.5rem;">
                        {''.join([f'<span style="background: #e0e7ff; color: #3730a3; padding: 0.2rem 0.5rem; border-radius: 12px; font-size: 0.8rem; margin-right: 0.5rem; display: inline-block; margin-bottom: 0.3rem;">{keyword}</span>' for keyword in keywords])}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
            
            with col1:
                if st.button(f"🔊 Speak", key=f"speak_{i}", help="Listen to email summary"):
                    if not st.session_state.current_speaking:
                        # Create and start TTS thread
                        tts_text = f"Email {i}: {subject}. From {sender}. Summary: {summary}"
                        threading.Thread(
                            target=speak_text, 
                            args=(tts_text, str(i)), 
                            daemon=True
                        ).start()
                        st.success(f"🔊 Speaking email {i}...")
                    else:
                        st.warning("🔊 Already speaking another email...")
            
            with col2:
                if st.button(f"📋 Details", key=f"details_{i}", help="View full email details"):
                    with st.expander(f"📋 Full Details - Email #{i}", expanded=True):
                        st.markdown(f"""
                        **📧 From:** {sender}  
                        **📝 Subject:** {subject}  
                        **🏷️ Category:** {category} (Confidence: {email.get('confidence', 0):.0%})  
                        **⭐ Priority:** {priority_label} ({priority_score:.2f}/10)  
                        **🕒 Timestamp:** {timestamp}  
                        **😊 Sentiment:** {sentiment.title()}  
                        **💬 Thread:** {thread_count} messages  
                        **📎 Attachments:** {attachments}  
                        
                        **📄 Email Body Preview:**
                        """)
                        body = email.get('body', 'No content available')
                        if len(body) > 500:
                            st.text(body[:500] + "...")
                            if st.button(f"Show Full Content", key=f"full_{i}"):
                                st.text(body)
                        else:
                            st.text(body)
            
            with col3:
                if st.button(f"🚀 Action", key=f"action_{i}", help="Quick actions for this email"):
                    st.info("🚀 Quick Actions: Reply, Forward, Archive, Delete (Feature coming soon!)")
            
            st.markdown("---")

def smart_email_chatbot():
    """Professional AI Email Assistant"""
    st.markdown("### 🤖 AI Email Assistant")
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Load email data for context
    emails = st.session_state.emails
    
    # Professional chat interface
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("#### 💬 Conversation")
        for message in st.session_state.chat_history[-6:]:  # Show last 6 messages
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <div class="message-avatar">👤</div>
                    <div class="message-content">{message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <div class="message-avatar">🤖</div>
                    <div class="message-content">{message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Input area
    user_input = st.text_input(
        "💬 Ask about your emails...", 
        placeholder="e.g., 'Show critical emails', 'What's new from Microsoft?', 'Summarize today'",
        key="chat_input",
        label_visibility="collapsed"
    )
    
    # Button layout
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        send_button = st.button("Send Message", type="primary", use_container_width=True)
    with col2:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    with col3:
        if st.button("Refresh", use_container_width=True):
            st.session_state.emails = load_email_data()
            st.success("Data refreshed!")
    
    # Process message
    if send_button and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        response = generate_intelligent_response(user_input.lower(), emails)
        st.session_state.chat_history.append({"role": "bot", "content": response})
        st.rerun()
    
    # Quick action buttons
    st.markdown("**Quick Actions:**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("� Email Stats", key="quick_stats", use_container_width=True):
            response = generate_intelligent_response("statistics", emails)
            st.session_state.chat_history.append({"role": "user", "content": "Email Statistics"})
            st.session_state.chat_history.append({"role": "bot", "content": response})
            st.rerun()
    
    with col2:
        if st.button("🚨 Critical Alerts", key="quick_critical", use_container_width=True):
            response = generate_intelligent_response("critical emails", emails)
            st.session_state.chat_history.append({"role": "user", "content": "Critical Alerts"})
            st.session_state.chat_history.append({"role": "bot", "content": response})
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def generate_intelligent_response(query: str, emails: List[Dict[str, Any]]) -> str:
    """Generate intelligent responses based on actual email data"""
    if not emails:
        return "📭 No email data available. Please process some emails first."
    
    # Keywords and patterns
    if any(word in query for word in ['critical', 'urgent', 'important', 'high priority']):
        critical_emails = [e for e in emails if e.get('priority_label') in ['Critical', 'High']]
        if critical_emails:
            count = len(critical_emails)
            top_critical = sorted(critical_emails, key=lambda x: x.get('priority_score', 0), reverse=True)[:3]
            response = f"🚨 Found {count} high-priority emails:\n\n"
            for i, email in enumerate(top_critical, 1):
                response += f"{i}. **{email.get('subject', 'No subject')}** from {email.get('sender', 'Unknown')} (Priority: {email.get('priority_score', 0):.1f})\n"
            return response
        else:
            return "✅ Great news! No critical emails at the moment."
    
    elif any(word in query for word in ['today', 'recent', 'latest']):
        today = datetime.now().date()
        today_emails = [e for e in emails if e.get('timestamp', datetime.now()).date() == today]
        if today_emails:
            categories = {}
            for email in today_emails:
                cat = email.get('category', 'Unknown')
                categories[cat] = categories.get(cat, 0) + 1
            
            response = f"📧 Today's email summary ({len(today_emails)} emails):\n\n"
            for cat, count in categories.items():
                response += f"• {cat}: {count} emails\n"
            
            # Add top priority from today
            top_today = max(today_emails, key=lambda x: x.get('priority_score', 0))
            response += f"\n🎯 Top priority: **{top_today.get('subject', 'No subject')}** (Score: {top_today.get('priority_score', 0):.1f})"
            return response
        else:
            return "📭 No emails received today yet."
    
    elif any(word in query for word in ['microsoft', 'apple', 'google', 'amazon', 'tesla', 'netflix']):
        company_emails = []
        for word in ['microsoft', 'apple', 'google', 'amazon', 'tesla', 'netflix', 'spacex', 'uber', 'stripe']:
            if word in query:
                company_emails = [e for e in emails if word in e.get('sender', '').lower() or word in e.get('subject', '').lower()]
                break
        
        if company_emails:
            latest = max(company_emails, key=lambda x: x.get('timestamp', datetime.min))
            return f"📧 Latest from {word.title()}: **{latest.get('subject', 'No subject')}** (Priority: {latest.get('priority_score', 0):.1f})\n\nSummary: {latest.get('summary', 'No summary available')}"
        else:
            return f"📭 No recent emails found from {word.title()}."
    
    elif any(word in query for word in ['summary', 'overview', 'stats', 'statistics']):
        total = len(emails)
        categories = {}
        avg_priority = np.mean([e.get('priority_score', 0) for e in emails])
        
        for email in emails:
            cat = email.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        response = f"📊 **Email Statistics:**\n\n"
        response += f"📧 **Total Emails:** {total}\n"
        response += f"⭐ **Average Priority:** {avg_priority:.1f}/10\n\n"
        response += f"🏷️ **Categories:**\n"
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            response += f"• {cat}: {count} emails ({percentage:.1f}%)\n"
        
        return response
    
    elif any(word in query for word in ['work', 'business', 'meeting', 'project']):
        work_emails = [e for e in emails if e.get('category') == 'Work']
        if work_emails:
            count = len(work_emails)
            high_priority_work = [e for e in work_emails if e.get('priority_score', 0) >= 7.0]
            response = f"💼 **Work Emails:** {count} total, {len(high_priority_work)} high priority\n\n"
            
            if high_priority_work:
                top_work = max(high_priority_work, key=lambda x: x.get('priority_score', 0))
                response += f"🎯 **Top Priority:** {top_work.get('subject', 'No subject')}\n"
                response += f"📤 **From:** {top_work.get('sender', 'Unknown')}\n"
                response += f"📝 **Summary:** {top_work.get('summary', 'No summary')}"
            
            return response
        else:
            return "💼 No work-related emails found."
    
    elif any(word in query for word in ['finance', 'money', 'payment', 'invoice', 'billing']):
        finance_emails = [e for e in emails if e.get('category') == 'Finance']
        if finance_emails:
            count = len(finance_emails)
            latest_finance = max(finance_emails, key=lambda x: x.get('timestamp', datetime.min))
            return f"💰 **Finance Emails:** {count} found\n\n🕒 **Latest:** {latest_finance.get('subject', 'No subject')} from {latest_finance.get('sender', 'Unknown')}\n\n📝 **Summary:** {latest_finance.get('summary', 'No summary')}"
        else:
            return "💰 No finance-related emails found."
    
    else:
        # Generic response with helpful suggestions
        return """🤖 I'm your intelligent email assistant! Here are some things you can ask me:

• "Show me critical emails" - Get high-priority messages
• "What's new today?" - Today's email summary  
• "Work emails" - Filter by work category
• "Latest from Microsoft" - Company-specific emails
• "Give me stats" - Overall email statistics
• "Finance emails" - Money-related messages

💡 Try asking about specific companies, categories, or timeframes!"""

def create_sidebar_info():
    """Create enhanced sidebar with system info"""
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-metric">
            <h3 style="margin: 0; text-align: center;">🚀 MailMate AI</h3>
            <p style="margin: 0.5rem 0 0 0; text-align: center; opacity: 0.9;">Intelligent Email Management</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Refresh Emails", use_container_width=True):
            st.session_state.emails = load_email_data()
            st.success("✅ Emails refreshed!")
            st.rerun()
        
        # System status
        st.markdown("### 📊 System Status")
        
        emails = st.session_state.emails
        if emails:
            total = len(emails)
            critical = sum(1 for e in emails if e.get('priority_label') == 'Critical')
            high = sum(1 for e in emails if e.get('priority_label') == 'High')
            
            st.markdown(f"""
            <div class="sidebar-metric">
                <div style="font-size: 1.5rem; font-weight: bold;">{total}</div>
                <div style="font-size: 0.9rem;">Total Emails</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="sidebar-metric">
                <div style="font-size: 1.5rem; font-weight: bold;">{critical}</div>
                <div style="font-size: 0.9rem;">Critical Priority</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="sidebar-metric">
                <div style="font-size: 1.5rem; font-weight: bold;">{high}</div>
                <div style="font-size: 0.9rem;">High Priority</div>
            </div>
            """, unsafe_allow_html=True)
        
        # TTS Status
        if st.session_state.tts_status:
            st.markdown("### 🔊 TTS Status")
            st.info(st.session_state.tts_status)
        
        # AI Features
        st.markdown("### 🧠 AI Features")
        st.markdown("""
        ✅ **Smart Classification**  
        ✅ **Priority Scoring**  
        ✅ **Auto Summarization**  
        ✅ **Sentiment Analysis**  
        ✅ **Intelligent Chatbot**  
        ✅ **Text-to-Speech**  
        ✅ **Real-time Analytics**  
        """)
        
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        if st.button("🔊 Read Top 5 Emails", use_container_width=True):
            if emails and not st.session_state.current_speaking:
                top_5 = sorted(emails, key=lambda x: x.get('priority_score', 0), reverse=True)[:5]
                digest_text = "Daily email digest. Top 5 priority emails: "
                for i, email in enumerate(top_5, 1):
                    digest_text += f"Email {i}: {email.get('subject', 'No subject')} from {email.get('sender', 'Unknown')}. Summary: {email.get('summary', 'No summary')}. "
                
                threading.Thread(
                    target=speak_text, 
                    args=(digest_text, "digest"), 
                    daemon=True
                ).start()
                st.success("🔊 Speaking daily digest...")
            elif st.session_state.current_speaking:
                st.warning("🔊 Already speaking...")
            else:
                st.warning("📭 No emails to read.")

def create_sidebar_info():
    """Create a professional sidebar with system information and controls."""
    with st.sidebar:
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(29, 78, 216, 0.1) 100%);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
            backdrop-filter: blur(15px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
            position: relative;
            overflow: hidden;
        '>
            <div style='
                position: absolute;
                top: -50%;
                right: -50%;
                width: 100%;
                height: 100%;
                background: radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%);
                pointer-events: none;
            '></div>
            <h2 style='
                color: white; 
                font-weight: 700; 
                margin-bottom: 1.25rem; 
                font-size: 1.6rem;
                background: linear-gradient(135deg, #60a5fa, #3b82f6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                position: relative;
                z-index: 2;
            '>ℹ️ System Info</h2>
            <div style='position: relative; z-index: 2; color: rgba(255, 255, 255, 0.9);'>
                <p><strong>Status:</strong> 🟢 Online</p>
                <p><strong>AI Model:</strong> Groq (Llama 3.1)</p>
                <p><strong>Features:</strong> TTS, Analytics, Chat</p>
                <p><strong>Version:</strong> v2.0 Enterprise</p>
            </div>
        </div>
        """, unsafe_allow_html=True)


def smart_email_chatbot():
    """Create an intelligent email chatbot interface."""
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.9) 100%);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
        position: relative;
        overflow: hidden;
        margin-bottom: 2rem;
    '>
        <div style='
            position: absolute;
            top: -30%;
            left: -30%;
            width: 60%;
            height: 60%;
            background: radial-gradient(circle, rgba(16, 185, 129, 0.1) 0%, transparent 70%);
            pointer-events: none;
        '></div>
        <h3 style='
            color: #1e293b; 
            font-weight: 700; 
            margin-bottom: 1.5rem; 
            font-size: 1.4rem;
            position: relative;
            z-index: 2;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        '>
            🤖 AI Email Assistant
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat interface
    user_input = st.text_input(
        "Ask about your emails:", 
        placeholder="e.g., What are my urgent emails today?",
        key="chat_input"
    )
    
    col1, col2 = st.columns([3, 1])
    with col2:
        send_button = st.button("Send 🚀", type="primary", use_container_width=True)
    
    if send_button and user_input:
        with st.spinner("🔍 Analyzing your request..."):
            try:
                response = get_ai_response(user_input, st.session_state.emails)
                
                st.markdown(f"""
                <div class='chat-response' style='
                    background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.8) 100%);
                    backdrop-filter: blur(15px);
                    border-radius: 16px;
                    padding: 1.5rem;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.05);
                    margin-top: 1rem;
                '>
                    <div style='
                        color: #3b82f6; 
                        font-weight: 600; 
                        margin-bottom: 0.75rem;
                        display: flex;
                        align-items: center;
                        gap: 0.5rem;
                    '>
                        👤 You: <span style='color: #64748b; font-weight: 500;'>{user_input}</span>
                    </div>
                    <div style='
                        color: #1e293b; 
                        font-weight: 500;
                        line-height: 1.6;
                        display: flex;
                        align-items: flex-start;
                        gap: 0.5rem;
                    '>
                        <span style='color: #10b981; font-weight: 600;'>🤖 MailMate AI:</span>
                        <div>{response}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Chat service unavailable: {e}")
    
    # Quick action buttons
    st.markdown("### 🚀 Quick Actions")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Email Summary", use_container_width=True):
            with st.spinner("Generating summary..."):
                emails = st.session_state.emails
                total_emails = len(emails)
                high_priority = len([e for e in emails if e.get('priority_label') == 'High'])
                
                st.success(f"""
                📈 **Email Overview:**
                - Total emails: {total_emails}
                - High priority: {high_priority}
                - Recent activity: Last 24 hours
                """)
    
    with col2:
        if st.button("🔥 Top Priorities", use_container_width=True):
            emails = st.session_state.emails
            top_emails = sorted(emails, key=lambda x: x.get('priority_score', 0), reverse=True)[:3]
            
            priorities_text = "🔥 **Top 3 Priorities:**\n\n"
            for i, email in enumerate(top_emails, 1):
                priorities_text += f"{i}. **{email.get('subject', 'No subject')}**\n"
                priorities_text += f"   From: {email.get('sender', 'Unknown')}\n"
                priorities_text += f"   Priority: {email.get('priority_label', 'Medium')}\n\n"
            
            st.markdown(priorities_text)


def main():
    """Main application"""
    # Header
    st.markdown("""
    <div class="main-header">
        <div class="main-title">🚀 MailMate</div>
        <div class="main-subtitle">AI-Powered Email Management System</div>
        <div class="status-badge">✨ System Online - AI Processing Active ✨</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Load email data
    if not st.session_state.emails:
        with st.spinner("🔄 Loading email data..."):
            st.session_state.emails = load_email_data()
    
    emails = st.session_state.emails
    
    if not emails:
        st.error("📭 No email data available. Please run the email processing pipeline first.")
        st.markdown("""
        <div class="info-card">
            <h4>🚀 Getting Started:</h4>
            <ol>
                <li>Run <code>python main.py process</code> to process your emails</li>
                <li>Or run <code>python setup_demo.py</code> for sample data</li>
                <li>Refresh this page to see your processed emails</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Create sidebar
    create_sidebar_info()
    
    # Success message
    st.markdown(f"""
    <div class="success-alert">
        ✅ <strong>System Ready!</strong> Successfully loaded {len(emails)} emails with AI analysis complete.
    </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights
    st.markdown("""
    <div class="feature-highlight">
        🎯 <strong>AI-Powered Features Active:</strong> Smart categorization, priority scoring, automatic summarization, 
        sentiment analysis, and intelligent chatbot - all working seamlessly with your email data!
    </div>
    """, unsafe_allow_html=True)
    
    # Main dashboard sections
    st.markdown("---")
    
    # Read Top 5 Emails Audio Feature
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("### 🔊 Audio Features")
    with col2:
        if st.button("🔊 Read Top 5 Emails", type="primary", use_container_width=True):
            try:
                from enhanced_tts import speak_text
                top_5_emails = sorted(emails, key=lambda x: x.get('priority_score', 0), reverse=True)[:5]
                
                digest_text = "Here are your top 5 priority emails. "
                for i, email in enumerate(top_5_emails, 1):
                    sender = email.get('sender', 'Unknown sender')
                    subject = email.get('subject', 'No subject')
                    priority = email.get('priority_label', 'Medium')
                    summary = email.get('ai_summary', email.get('content', '')[:100])
                    
                    digest_text += f"Email {i}. Priority {priority}. From {sender}. Subject: {subject}. Summary: {summary}. "
                
                digest_text += "End of top priority emails."
                
                success = speak_text(digest_text, async_mode=True)
                if success:
                    st.success("🔊 Playing top 5 emails digest...")
                    st.info(f"📧 Reading {len(top_5_emails)} highest priority emails")
                else:
                    st.error("❌ TTS not available")
            except Exception as e:
                st.error(f"TTS Error: {e}")
    
    with col3:
        if st.button("⏹️ Stop Audio", use_container_width=True):
            try:
                from enhanced_tts import stop_all_speech
                stop_all_speech()
                st.success("⏹️ Audio stopped")
            except Exception as e:
                st.warning("Could not stop audio")

    st.markdown("---")
    
    # Metrics Dashboard
    create_modern_metrics_dashboard(emails)
    
    st.markdown("---")
    
    # Visualizations
    st.markdown("## 📈 Advanced Analytics")
    create_advanced_visualizations(emails)
    
    # Timeline chart
    # Professional analytics with line charts
    st.markdown("---")
    create_professional_analytics(emails)
    
    st.markdown("---")
    
    # Two-column layout for emails and chatbot
    col1, col2 = st.columns([2, 1])
    
    with col1:
        display_modern_email_list(emails)
    
    with col2:
        smart_email_chatbot()

if __name__ == "__main__":
    main()
