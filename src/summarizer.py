import logging
import re
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from transformers import pipeline
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from config.config import Config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass
class EmailSummarizer:
    def __init__(self):
        self.gemini_client = None
        self.bart_summarizer = None
        self.max_length = Config.SUMMARIZATION_MAX_LENGTH
        if Config.GEMINI_API_KEY:
            try:
                genai.configure(api_key=Config.GEMINI_API_KEY)
                self.gemini_client = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("Gemini client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {str(e)}")
        self._init_fallback_summarizers()
    def _init_fallback_summarizers(self):
        try:
            self.bart_summarizer = pipeline(
                "summarization", 
                model="facebook/bart-large-cnn",
                device=-1
            )
            logger.info("BART summarizer loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load BART summarizer: {str(e)}")
            self.bart_summarizer = None
    def summarize_email(self, subject: str, body: str, sender: str = "") -> str:
        cleaned_body = self._clean_text(body)
        if len(cleaned_body.split()) < 10:
            return subject if subject else "Short message"
        if self.gemini_client:
            try:
                summary = self._summarize_with_gemini(subject, cleaned_body, sender)
                if summary and len(summary) > 10:
                    return summary
            except Exception as e:
                logger.warning(f"Gemini summarization failed: {str(e)}")
        if self.bart_summarizer:
            try:
                summary = self._summarize_with_bart(cleaned_body)
                if summary:
                    return summary
            except Exception as e:
                logger.warning(f"BART summarization failed: {str(e)}")
        return self._summarize_with_textrank(cleaned_body, subject)
    def _summarize_with_gemini(self, subject: str, body: str, sender: str = "") -> str:
        body = body[:1500] if len(body) > 1500 else body
        prompt = f"""Summarize the following email in a single, concise headline-style sentence. 
Focus on the main action, request, or key information. Keep it under 15 words.

From: {sender}
Subject: {subject}
Body: {body}

Summary:"""
        try:
            response = self.gemini_client.generate_content(prompt)
            summary = response.text.strip()
            summary = re.sub(r'^(Summary|Here\'s|This email)', '', summary, flags=re.IGNORECASE)
            summary = summary.strip(' :.-')
            if len(summary.split()) <= 20:
                return summary
            else:
                words = summary.split()[:15]
                return ' '.join(words) + '...'
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return ""
    def _summarize_with_bart(self, body: str) -> str:
        try:
            if len(body.split()) < 20:
                return body[:100] + "..." if len(body) > 100 else body
            input_text = body[:1024] if len(body) > 1024 else body
            summary = self.bart_summarizer(
                input_text,
                max_length=50,
                min_length=10,
                do_sample=False
            )[0]['summary_text']
            return summary.strip()
        except Exception as e:
            logger.error(f"BART summarization error: {str(e)}")
            return ""
    def _summarize_with_textrank(self, body: str, subject: str = "") -> str:
        try:
            if subject and len(body.split()) < 30:
                return subject
            sentences = sent_tokenize(body)
            if len(sentences) <= 2:
                return sentences[0] if sentences else body[:100] + "..."
            vectorizer = TfidfVectorizer(stop_words='english', lowercase=True)
            sentence_vectors = vectorizer.fit_transform(sentences)
            similarity_matrix = cosine_similarity(sentence_vectors)
            graph = nx.from_numpy_array(similarity_matrix)
            scores = nx.pagerank(graph)
            top_sentence_idx = max(scores, key=scores.get)
            summary = sentences[top_sentence_idx]
            if len(summary.split()) > 20:
                words = summary.split()[:15]
                summary = ' '.join(words) + '...'
            return summary
        except Exception as e:
            logger.error(f"TextRank summarization error: {str(e)}")
            sentences = sent_tokenize(body)
            if sentences:
                first_sentence = sentences[0]
                if len(first_sentence.split()) > 20:
                    words = first_sentence.split()[:15]
                    return ' '.join(words) + '...'
                return first_sentence
            else:
                return body[:100] + "..." if len(body) > 100 else body
    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub(r'\S+@\S+', '', text)
        text = re.sub(r'\s+', ' ', text)
        signature_patterns = [
            r'--\s*\n.*',
            r'Sent from my.*',
            r'Best regards.*',
            r'Sincerely.*',
            r'Thanks.*\n.*@.*',
            r'This email.*confidential.*'
        ]
        for pattern in signature_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
        return text.strip()
    def batch_summarize(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        summarized_emails = []
        for email in emails:
            try:
                summary = self.summarize_email(
                    email.get('subject', ''),
                    email.get('body', ''),
                    email.get('sender', '')
                )
                email_with_summary = email.copy()
                email_with_summary['summary'] = summary
                summarized_emails.append(email_with_summary)
            except Exception as e:
                logger.error(f"Error summarizing email: {str(e)}")
                email_with_summary = email.copy()
                email_with_summary['summary'] = email.get('subject', 'No summary available')
                summarized_emails.append(email_with_summary)
        return summarized_emails
    def get_daily_digest_summary(self, emails: List[Dict[str, Any]], 
                                max_emails: int = 10) -> str:
        if not emails:
            return "No emails to summarize today."
        if 'priority_score' in emails[0]:
            top_emails = sorted(emails, key=lambda x: x.get('priority_score', 0), reverse=True)[:max_emails]
        else:
            top_emails = emails[:max_emails]
        digest_parts = [f"Daily Email Digest - {len(top_emails)} important emails:\n"]
        for i, email in enumerate(top_emails, 1):
            sender = email.get('sender', 'Unknown sender')
            summary = email.get('summary', self.summarize_email(
                email.get('subject', ''),
                email.get('body', ''),
                sender
            ))
            priority_label = email.get('priority_label', 'Medium')
            digest_parts.append(f"{i}. {priority_label} priority from {sender}: {summary}")
        return "\n".join(digest_parts)
    def analyze_summary_quality(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not emails:
            return {}
        summaries = [email.get('summary', '') for email in emails]
        avg_summary_length = sum(len(summary.split()) for summary in summaries) / len(summaries)
        summary_coverage = sum(1 for summary in summaries if len(summary) > 5) / len(summaries)
        quality_metrics = {
            'total_emails': len(emails),
            'avg_summary_length_words': round(avg_summary_length, 1),
            'summary_coverage': round(summary_coverage * 100, 1),
            'summarization_method_used': {
                'gemini': bool(self.gemini_client),
                'bart': bool(self.bart_summarizer),
                'textrank': True
            }
        }
        return quality_metrics
    def generate_category_summaries(self, emails: List[Dict[str, Any]]) -> Dict[str, str]:
        category_emails = {}
        for email in emails:
            category = email.get('category', 'Uncategorized')
            if category not in category_emails:
                category_emails[category] = []
            category_emails[category].append(email)
        category_summaries = {}
        for category, cat_emails in category_emails.items():
            if len(cat_emails) == 0:
                continue
            if len(cat_emails) == 1:
                summary = f"1 {category.lower()} email: {cat_emails[0].get('summary', 'No summary')}"
            else:
                top_3 = cat_emails[:3]
                email_summaries = [email.get('summary', 'No summary') for email in top_3]
                summary = f"{len(cat_emails)} {category.lower()} emails including: {'; '.join(email_summaries[:2])}"
                if len(cat_emails) > 2:
                    summary += f" and {len(cat_emails) - 2} more."
            category_summaries[category] = summary
        return category_summaries
def test_summarizer():
    summarizer = EmailSummarizer()
    test_emails = [
        {
            'subject': 'Project Update Required',
            'body': '''Hi team,
            
            I hope this email finds you well. I wanted to reach out regarding the quarterly project update that we discussed in our last meeting. As you know, we have been working on the client deliverables for the past few weeks, and I believe it's time to provide a comprehensive status update to our stakeholders.
            
            Could you please prepare a detailed report including the current progress, any challenges we've faced, and the expected timeline for completion? This information will be crucial for our upcoming board presentation.
            
            The deadline for this report is Friday, so please prioritize this task accordingly.
            
            Best regards,
            John''',
            'sender': 'john@company.com'
        },
        {
            'subject': 'Weekend Sale - 50% Off Everything!',
            'body': '''Don't miss our amazing weekend sale! Get 50% off on all products. Limited time offer. Shop now and save big! Free shipping on orders over $50.''',
            'sender': 'sales@store.com'
        }
    ]
    for email in test_emails:
        summary = summarizer.summarize_email(
            email['subject'], 
            email['body'], 
            email['sender']
        )
        print(f"Subject: {email['subject']}")
        print(f"Summary: {summary}")
        print("-" * 50)
if __name__ == "__main__":
    test_summarizer()