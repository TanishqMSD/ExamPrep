from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import re

@dataclass
class ProcessedContent:
    title: str
    summary: str
    eli5_explanation: str
    key_concepts: List[Dict[str, str]]
    quiz_questions: List[Dict[str, str]]
    study_milestones: List[Dict[str, str]]
    bookmarked_insights: List[Dict[str, str]]
    estimated_duration: int

class ContentProcessor:
    @staticmethod
    def generate_summary(content: str, max_length: int = 500) -> str:
        # Split content into sentences and select key ones
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        # Select most representative sentences
        summary_sentences = sentences[:5]  # For now, just take first 5 sentences
        summary = '. '.join(summary_sentences)
        
        return summary[:max_length] + '...' if len(summary) > max_length else summary

    @staticmethod
    def extract_key_concepts(content: str) -> List[Dict[str, str]]:
        # For now, use basic pattern matching to find potential key concepts
        # In production, this would use more sophisticated NLP techniques
        concepts = []
        lines = content.split('\n')
        
        for line in lines:
            # Look for lines that might define concepts
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2 and len(parts[0].strip()) < 50:
                    concepts.append({
                        'concept': parts[0].strip(),
                        'definition': parts[1].strip()
                    })
        
        return concepts[:10]  # Return up to 10 key concepts

    @staticmethod
    def generate_eli5(content: str, max_length: int = 300) -> str:
        # Simplified version for now
        # In production, this would use more sophisticated NLP
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if sentences:
            simple_explanation = sentences[0]  # Take first sentence as base
            return f"Imagine this: {simple_explanation}"
        return "Sorry, couldn't generate a simple explanation."

    @staticmethod
    def generate_quiz_questions(content: str) -> List[Dict[str, str]]:
        # Basic implementation - in production would use more sophisticated NLP
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        questions = []
        for i, sentence in enumerate(sentences[:5]):  # Generate 5 questions
            # Very basic question generation
            question = {
                'question': f"Which of the following best describes {sentence.split()[0:5]}...?",
                'correct_answer': sentence,
                'option1': sentence,
                'option2': sentences[(i + 1) % len(sentences)],
                'option3': sentences[(i + 2) % len(sentences)],
                'option4': sentences[(i + 3) % len(sentences)]
            }
            questions.append(question)
        
        return questions

    @staticmethod
    def generate_study_milestones(content: str) -> List[Dict[str, str]]:
        # Split content into logical sections
        paragraphs = content.split('\n\n')
        milestones = []
        
        for i, para in enumerate(paragraphs[:5], 1):  # Create up to 5 milestones
            milestone = {
                'title': f"Milestone {i}",
                'description': para[:100] + '...' if len(para) > 100 else para,
                'order': i,
                'xp_reward': 10 * i  # Increase XP for later milestones
            }
            milestones.append(milestone)
        
        return milestones

    @staticmethod
    def extract_bookmarked_insights(content: str) -> List[Dict[str, str]]:
        sentences = re.split(r'[.!?]+', content)
        insights = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            # Look for sentences that might contain key insights
            if any(keyword in sentence.lower() for keyword in ['important', 'key', 'essential', 'crucial']):
                if len(sentence) > 20:
                    insights.append({
                        'content': sentence,
                        'importance_level': 5  # High importance for matched keywords
                    })
        
        return insights[:5]  # Return up to 5 insights

    @staticmethod
    def estimate_study_duration(content: str) -> int:
        # Rough estimation based on content length
        word_count = len(content.split())
        # Assume average reading speed of 200 words per minute
        minutes = max(5, word_count // 200)
        return minutes

    @classmethod
    def process_content(cls, content: str, title: str) -> ProcessedContent:
        summary = cls.generate_summary(content)
        eli5 = cls.generate_eli5(content)
        key_concepts = cls.extract_key_concepts(content)
        quiz_questions = cls.generate_quiz_questions(content)
        study_milestones = cls.generate_study_milestones(content)
        bookmarked_insights = cls.extract_bookmarked_insights(content)
        estimated_duration = cls.estimate_study_duration(content)
        
        return ProcessedContent(
            title=title,
            summary=summary,
            eli5_explanation=eli5,
            key_concepts=key_concepts,
            quiz_questions=quiz_questions,
            study_milestones=study_milestones,
            bookmarked_insights=bookmarked_insights,
            estimated_duration=estimated_duration
        )