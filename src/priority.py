import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import pandas as pd
from collections import defaultdict, Counter
from config.config import Config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class PriorityScorer:
    def __init__(self):
        self.priority_keywords = Config.PRIORITY_KEYWORDS
        self.vip_senders = set(Config.VIP_SENDERS)
        self.sender_frequency = defaultdict(int)
        self.communication_history = defaultdict(list)
    def calculate_priority_score(self, email: Dict[str, Any], 
                               sender_history: List[Dict[str, Any]] = None) -> float:
        score = 0.0
        sender_score = self._calculate_sender_score(email.get('sender', ''))
        score += sender_score
        keyword_score = self._calculate_keyword_score(
            email.get('subject', ''), 
            email.get('body', '')
        )
        score += keyword_score
        frequency_score = self._calculate_frequency_score(
            email.get('sender', ''), 
            sender_history or []
        )
        score += frequency_score
        time_score = self._calculate_time_sensitivity_score(email)
        score += time_score
        normalized_score = min(score, 10.0)
        return round(normalized_score, 2)
    def _calculate_sender_score(self, sender: str) -> float:
        if not sender:
            return 0.0
        sender_lower = sender.lower()
        for vip in self.vip_senders:
            if vip.lower() in sender_lower:
                return 3.0
        domain_scores = {
            '@gmail.com': 0.5,
            '@outlook.com': 0.5,
            '@yahoo.com': 0.5,
            '@hotmail.com': 0.5,
            '@company.com': 2.5,
            '@work.com': 2.5,
            '@corp.com': 2.5,
            '@org': 2.0,
            '@edu': 2.0,
            '@gov': 2.5
        }
        for domain, score in domain_scores.items():
            if domain in sender_lower:
                return score
        work_keywords = ['hr', 'admin', 'support', 'manager', 'director', 'ceo', 'cto']
        for keyword in work_keywords:
            if keyword in sender_lower:
                return 2.0
        return 1.0
    def _calculate_keyword_score(self, subject: str, body: str) -> float:
        text = f"{subject} {body}".lower()
        max_score = 0.0
        for keyword, score in self.priority_keywords.items():
            if keyword.lower() in text:
                max_score = max(max_score, score)
        urgent_patterns = [
            r'\burgent\b',
            r'\basap\b',
            r'\bimmediate\b',
            r'\bemergency\b',
            r'\bdeadline.*today\b',
            r'\bdue.*today\b',
            r'\btime.?sensitive\b',
            r'!!+',
            r'\bACTION REQUIRED\b'
        ]
        for pattern in urgent_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                max_score = max(max_score, 2.5)
        return min(max_score, 3.0)
    def _calculate_frequency_score(self, sender: str, sender_history: List[Dict[str, Any]]) -> float:
        if not sender or not sender_history:
            return 0.5
        sender_emails = [email for email in sender_history if email.get('sender', '').lower() == sender.lower()]
        frequency = len(sender_emails)
        if frequency >= 20:
            return 2.0
        elif frequency >= 10:
            return 1.5
        elif frequency >= 5:
            return 1.0
        elif frequency >= 2:
            return 0.7
        else:
            return 0.3
    def _calculate_time_sensitivity_score(self, email: Dict[str, Any]) -> float:
        timestamp = email.get('timestamp')
        if not timestamp:
            return 0.0
        now = datetime.now()
        if timestamp.tzinfo:
            now = now.replace(tzinfo=timestamp.tzinfo)
        time_diff = now - timestamp
        if time_diff < timedelta(hours=1):
            return 2.0
        elif time_diff < timedelta(hours=6):
            return 1.5
        elif time_diff < timedelta(hours=24):
            return 1.0
        elif time_diff < timedelta(days=3):
            return 0.5
        else:
            return 0.0
    def prioritize_emails(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for email in emails:
            email['priority_score'] = self.calculate_priority_score(email, emails)
        prioritized_emails = sorted(emails, key=lambda x: x['priority_score'], reverse=True)
        for i, email in enumerate(prioritized_emails):
            score = email['priority_score']
            if score >= 8.0:
                priority_label = "Critical"
            elif score >= 6.0:
                priority_label = "High"
            elif score >= 4.0:
                priority_label = "Medium"
            elif score >= 2.0:
                priority_label = "Low"
            else:
                priority_label = "Very Low"
            email['priority_label'] = priority_label
            email['rank'] = i + 1
        return prioritized_emails
    def get_top_priority_emails(self, emails: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
        prioritized = self.prioritize_emails(emails)
        return prioritized[:limit]
    def get_priority_distribution(self, emails: List[Dict[str, Any]]) -> Dict[str, int]:
        distribution = {
            "Critical": 0,
            "High": 0,
            "Medium": 0,
            "Low": 0,
            "Very Low": 0
        }
        for email in emails:
            priority_label = email.get('priority_label', 'Low')
            if priority_label in distribution:
                distribution[priority_label] += 1
        return distribution
    def update_vip_senders(self, new_vip_senders: List[str]):
        self.vip_senders.update(new_vip_senders)
        logger.info(f"Updated VIP senders list: {len(self.vip_senders)} senders")
    def analyze_sender_patterns(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        sender_stats = defaultdict(lambda: {
            'count': 0,
            'avg_priority': 0.0,
            'categories': Counter(),
            'recent_count': 0
        })
        recent_threshold = datetime.now() - timedelta(days=7)
        for email in emails:
            sender = email.get('sender', '')
            priority_score = email.get('priority_score', 0.0)
            category = email.get('category', '')
            timestamp = email.get('timestamp', datetime.now())
            stats = sender_stats[sender]
            stats['count'] += 1
            stats['avg_priority'] = ((stats['avg_priority'] * (stats['count'] - 1)) + priority_score) / stats['count']
            stats['categories'][category] += 1
            if timestamp > recent_threshold:
                stats['recent_count'] += 1
        return {sender: dict(stats) for sender, stats in sender_stats.items()}
    def get_priority_insights(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not emails:
            return {}
        prioritized = self.prioritize_emails(emails)
        insights = {
            'total_emails': len(emails),
            'avg_priority_score': sum(email['priority_score'] for email in emails) / len(emails),
            'priority_distribution': self.get_priority_distribution(emails),
            'top_priority_senders': self._get_top_priority_senders(emails),
            'urgent_keywords_found': self._get_urgent_keywords_found(emails),
            'recommendations': self._generate_recommendations(emails)
        }
        return insights
    def _get_top_priority_senders(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        sender_priorities = defaultdict(list)
        for email in emails:
            sender = email.get('sender', '')
            priority = email.get('priority_score', 0.0)
            sender_priorities[sender].append(priority)
        sender_avg = []
        for sender, priorities in sender_priorities.items():
            avg_priority = sum(priorities) / len(priorities)
            sender_avg.append({
                'sender': sender,
                'avg_priority': round(avg_priority, 2),
                'email_count': len(priorities)
            })
        return sorted(sender_avg, key=lambda x: x['avg_priority'], reverse=True)[:10]
    def _get_urgent_keywords_found(self, emails: List[Dict[str, Any]]) -> Dict[str, int]:
        keyword_counts = defaultdict(int)
        for email in emails:
            text = f"{email.get('subject', '')} {email.get('body', '')}".lower()
            for keyword in self.priority_keywords:
                if keyword.lower() in text:
                    keyword_counts[keyword] += 1
        return dict(sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True))
    def _generate_recommendations(self, emails: List[Dict[str, Any]]) -> List[str]:
        recommendations = []
        high_priority_count = sum(1 for email in emails if email.get('priority_score', 0) >= 6.0)
        total_emails = len(emails)
        if high_priority_count > total_emails * 0.3:
            recommendations.append("You have many high-priority emails. Consider reviewing your VIP sender list.")
        if total_emails > 50:
            recommendations.append("Consider setting up email filters to automatically categorize emails.")
        urgent_count = sum(1 for email in emails if email.get('priority_label') == 'Critical')
        if urgent_count > 5:
            recommendations.append(f"You have {urgent_count} critical emails that need immediate attention.")
        return recommendations
def test_priority_scorer():
    scorer = PriorityScorer()
    test_emails = [
        {
            'sender': 'boss@company.com',
            'subject': 'URGENT: Project deadline today',
            'body': 'We need to submit the project ASAP. This is very important.',
            'timestamp': datetime.now() - timedelta(hours=1)
        },
        {
            'sender': 'friend@gmail.com',
            'subject': 'Weekend plans',
            'body': 'Hey, want to hang out this weekend?',
            'timestamp': datetime.now() - timedelta(days=1)
        },
        {
            'sender': 'bank@bank.com',
            'subject': 'Payment due reminder',
            'body': 'Your payment is due in 3 days.',
            'timestamp': datetime.now() - timedelta(hours=12)
        }
    ]
    prioritized = scorer.prioritize_emails(test_emails)
    print("Prioritized emails:")
    for email in prioritized:
        print(f"From: {email['sender']}")
        print(f"Subject: {email['subject']}")
        print(f"Priority Score: {email['priority_score']}")
        print(f"Priority Label: {email['priority_label']}")
        print("-" * 50)
if __name__ == "__main__":
    test_priority_scorer()