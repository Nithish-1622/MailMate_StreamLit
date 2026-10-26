import logging
import pickle
import os
import json
from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np
from groq import Groq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import re
from config.config import Config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class EmailClassifier:
    def __init__(self):
        self.categories = Config.EMAIL_CATEGORIES
        self.groq_client = None
        self.fallback_model = None
        self.model_path = "data/email_classifier.pkl"
        if Config.GROQ_API_KEY:
            try:
                self.groq_client = Groq(api_key=Config.GROQ_API_KEY)
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {str(e)}")
        self._load_or_train_fallback_model()
    def classify_email(self, subject: str, body: str, sender: str = "") -> Tuple[str, float]:
        if self.groq_client:
            try:
                category, confidence = self._classify_with_groq(subject, body, sender)
                if category and confidence > 0.5:
                    return category, confidence
            except Exception as e:
                logger.warning(f"Groq classification failed: {str(e)}")
        return self._classify_with_fallback(subject, body, sender)
    def _classify_with_groq(self, subject: str, body: str, sender: str = "") -> Tuple[str, float]:
        email_text = f"From: {sender}\nSubject: {subject}\nBody: {body[:500]}"
        categories_str = ", ".join(self.categories)
        prompt = f"""Classify the following email into one of these categories: {categories_str}

Email:
{email_text}

Please respond with only the category name from the list above. Consider:
- Work: Professional emails, meetings, projects, business communication
- Personal: Friends, family, personal matters
- Finance: Banking, payments, invoices, financial services
- Promotions: Marketing emails, advertisements, offers, deals
- Spam: Unwanted emails, suspicious content, obvious spam
- Urgent: Time-sensitive emails with urgent keywords or from important senders

Category:"""
        try:
            completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an email classification assistant. Respond with only the category name."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.1,
                max_tokens=10
            )
            predicted_category = completion.choices[0].message.content.strip()
            if predicted_category in self.categories:
                return predicted_category, 0.9
            else:
                for category in self.categories:
                    if category.lower() in predicted_category.lower():
                        return category, 0.8
                logger.warning(f"Groq returned invalid category: {predicted_category}")
                return "", 0.0
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            return "", 0.0
    def _classify_with_fallback(self, subject: str, body: str, sender: str = "") -> Tuple[str, float]:
        if not self.fallback_model:
            return "Personal", 0.5
        try:
            email_text = f"{subject} {body[:300]}"
            prediction = self.fallback_model.predict([email_text])[0]
            probabilities = self.fallback_model.predict_proba([email_text])[0]
            confidence = max(probabilities)
            return prediction, confidence
        except Exception as e:
            logger.error(f"Fallback classification error: {str(e)}")
            return "Personal", 0.5
    def _load_or_train_fallback_model(self):
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    self.fallback_model = pickle.load(f)
                logger.info("Loaded existing fallback model")
                return
            except Exception as e:
                logger.warning(f"Failed to load model: {str(e)}")
        self._train_fallback_model()
    def _train_fallback_model(self):
        logger.info("Training fallback classification model...")
        training_data = self._create_synthetic_training_data()
        if not training_data:
            logger.error("No training data available")
            return
        df = pd.DataFrame(training_data)
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                lowercase=True,
                ngram_range=(1, 2)
            )),
            ('classifier', LogisticRegression(
                random_state=42,
                max_iter=1000
            ))
        ])
        X = df['text']
        y = df['category']
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        logger.info("Model training completed")
        logger.info(f"Test accuracy: {pipeline.score(X_test, y_test):.3f}")
        self.fallback_model = pipeline
        os.makedirs("data", exist_ok=True)
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump(pipeline, f)
            logger.info("Model saved successfully")
        except Exception as e:
            logger.error(f"Failed to save model: {str(e)}")
    def _create_synthetic_training_data(self) -> List[Dict[str, str]]:
        synthetic_data = []
        work_samples = [
            "Meeting scheduled for tomorrow project review quarterly results",
            "Please review the attached document deadline friday important",
            "Team standup meeting agenda items discussion points",
            "Project milestone deliverables client presentation",
            "HR policy update employee handbook changes",
            "Budget approval request quarterly planning session",
            "Conference call reschedule availability next week",
            "Performance review feedback development goals",
            "Onboarding new team member orientation schedule",
            "Training workshop professional development opportunity"
        ]
        personal_samples = [
            "Happy birthday celebration dinner party invitation",
            "Family reunion summer vacation planning trip",
            "Wedding invitation save the date ceremony",
            "Movie night friends weekend plans hangout",
            "Recipe sharing cooking dinner together",
            "Photo sharing vacation memories family album",
            "Birthday party planning surprise celebration",
            "Book recommendation reading club discussion",
            "Exercise workout partner gym membership",
            "Holiday plans christmas thanksgiving family"
        ]
        finance_samples = [
            "Bank statement monthly account balance summary",
            "Credit card payment due invoice billing",
            "Investment portfolio quarterly performance report",
            "Insurance premium renewal policy update",
            "Tax documents preparation annual filing",
            "Loan application approved mortgage refinancing",
            "Payment confirmation transaction processed successfully",
            "Budget tracking expenses monthly spending",
            "Retirement planning 401k contribution update",
            "Financial advisor consultation investment strategy"
        ]
        promotion_samples = [
            "Sale discount offer limited time deal",
            "Newsletter subscription exclusive deals promotions",
            "Product launch new features special pricing",
            "Flash sale 50% off everything must end",
            "Marketing campaign advertisement product showcase",
            "Coupon code free shipping online store",
            "Loyalty program rewards points redemption",
            "Seasonal sale summer winter holiday",
            "Product recommendation based on purchase history",
            "Clearance sale final markdown last chance"
        ]
        spam_samples = [
            "Nigerian prince inheritance million dollars claim",
            "Lottery winner congratulations cash prize claim",
            "Suspicious activity account verification required",
            "Click here now urgent action required",
            "Make money fast work from home",
            "Free gift cards no purchase necessary",
            "Weight loss miracle pill guaranteed results",
            "Debt consolidation bad credit approved",
            "Virus detected computer infected download",
            "Adult content explicit material warning"
        ]
        urgent_samples = [
            "URGENT server down production system failure",
            "ASAP client meeting emergency response needed",
            "Immediate action required security breach",
            "Emergency contact family hospital urgent",
            "Deadline today submission required immediate",
            "Critical bug fix production issue urgent",
            "URGENT approval needed contract signing",
            "Emergency meeting called all hands required",
            "Immediate response needed client complaint",
            "ASAP payment overdue invoice urgent attention"
        ]
        categories_data = [
            (work_samples, "Work"),
            (personal_samples, "Personal"),
            (finance_samples, "Finance"),
            (promotion_samples, "Promotions"),
            (spam_samples, "Spam"),
            (urgent_samples, "Urgent")
        ]
        for samples, category in categories_data:
            for sample in samples:
                synthetic_data.append({
                    'text': sample,
                    'category': category
                })
        return synthetic_data
    def batch_classify(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        classified_emails = []
        for email in emails:
            try:
                category, confidence = self.classify_email(
                    email.get('subject', ''),
                    email.get('body', ''),
                    email.get('sender', '')
                )
                classified_email = email.copy()
                classified_email['category'] = category
                classified_email['confidence'] = confidence
                classified_emails.append(classified_email)
            except Exception as e:
                logger.error(f"Error classifying email: {str(e)}")
                classified_email = email.copy()
                classified_email['category'] = 'Personal'
                classified_email['confidence'] = 0.5
                classified_emails.append(classified_email)
        return classified_emails
    def get_category_distribution(self, emails: List[Dict[str, Any]]) -> Dict[str, int]:
        distribution = {category: 0 for category in self.categories}
        for email in emails:
            category = email.get('category', 'Personal')
            if category in distribution:
                distribution[category] += 1
        return distribution
def test_classifier():
    classifier = EmailClassifier()
    test_emails = [
        {
            'subject': 'Team meeting tomorrow',
            'body': 'Hi team, we have a meeting scheduled for tomorrow at 10 AM to discuss the quarterly results.',
            'sender': 'manager@company.com'
        },
        {
            'subject': 'Special discount just for you!',
            'body': 'Don\'t miss out on our amazing 50% off sale! Limited time offer on all products.',
            'sender': 'sales@store.com'
        },
        {
            'subject': 'Your bank statement is ready',
            'body': 'Your monthly bank statement for account ending in 1234 is now available.',
            'sender': 'noreply@bank.com'
        }
    ]
    for email in test_emails:
        category, confidence = classifier.classify_email(
            email['subject'], 
            email['body'], 
            email['sender']
        )
        print(f"Email: {email['subject']}")
        print(f"Category: {category} (confidence: {confidence:.2f})")
        print("-" * 50)
if __name__ == "__main__":
    test_classifier()