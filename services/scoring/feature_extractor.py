"""Feature extraction for text analysis and scoring."""

import re
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import structlog
from textstat import textstat
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from models import FeatureAnalysis, TaskType

logger = structlog.get_logger()

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')


class FeatureExtractor:
    """Extract linguistic features from text for scoring."""
    
    def __init__(self):
        """Initialize feature extractor."""
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # IELTS-specific vocabulary lists (simplified)
        self.academic_words = {
            'analyze', 'approach', 'area', 'assess', 'assume', 'authority', 'available',
            'benefit', 'concept', 'consist', 'constitute', 'context', 'contract', 'create',
            'data', 'define', 'derive', 'distribute', 'economy', 'environment', 'establish',
            'estimate', 'evident', 'export', 'factor', 'finance', 'formula', 'function',
            'identify', 'income', 'indicate', 'individual', 'interpret', 'involve', 'issue',
            'labour', 'legal', 'legislate', 'major', 'method', 'occur', 'percent', 'period',
            'policy', 'principle', 'proceed', 'process', 'require', 'research', 'respond',
            'role', 'section', 'sector', 'significant', 'similar', 'source', 'specific',
            'structure', 'theory', 'vary'
        }
        
        # Common IELTS task words
        self.task_words = {
            'discuss', 'explain', 'describe', 'compare', 'contrast', 'analyze', 'evaluate',
            'examine', 'illustrate', 'outline', 'summarize', 'suggest', 'recommend',
            'propose', 'argue', 'demonstrate', 'identify', 'define', 'classify'
        }
    
    def extract_features(self, text: str, task_type: TaskType) -> FeatureAnalysis:
        """Extract comprehensive features from text."""
        start_time = time.time()
        
        # Basic text statistics
        word_count = len(word_tokenize(text))
        sentence_count = len(sent_tokenize(text))
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # Readability metrics
        readability_score = self._calculate_readability(text)
        
        # Vocabulary analysis
        vocabulary_diversity = self._calculate_vocabulary_diversity(text)
        
        # Grammar analysis (simplified)
        grammar_errors = self._detect_grammar_errors(text)
        
        # Coherence analysis
        coherence_score = self._calculate_coherence(text)
        
        # Task relevance
        task_relevance = self._calculate_task_relevance(text, task_type)
        
        # Complexity metrics
        complexity_metrics = self._calculate_complexity_metrics(text)
        
        processing_time = time.time() - start_time
        
        return FeatureAnalysis(
            word_count=word_count,
            sentence_count=sentence_count,
            avg_sentence_length=round(avg_sentence_length, 2),
            readability_score=round(readability_score, 2),
            vocabulary_diversity=round(vocabulary_diversity, 3),
            grammar_errors=grammar_errors,
            coherence_score=round(coherence_score, 2),
            task_relevance=round(task_relevance, 2),
            complexity_metrics=complexity_metrics
        )
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score using Flesch Reading Ease."""
        try:
            return textstat.flesch_reading_ease(text)
        except Exception as e:
            logger.warning(f"Failed to calculate readability: {e}")
            return 50.0  # Default middle score
    
    def _calculate_vocabulary_diversity(self, text: str) -> float:
        """Calculate vocabulary diversity (Type-Token Ratio)."""
        try:
            # Tokenize and clean words
            words = word_tokenize(text.lower())
            words = [word for word in words if word.isalpha() and word not in self.stop_words]
            
            if not words:
                return 0.0
            
            # Calculate type-token ratio
            unique_words = set(words)
            return len(unique_words) / len(words)
            
        except Exception as e:
            logger.warning(f"Failed to calculate vocabulary diversity: {e}")
            return 0.5  # Default middle score
    
    def _detect_grammar_errors(self, text: str) -> List[Dict[str, Any]]:
        """Detect common grammar errors (simplified implementation)."""
        errors = []
        
        try:
            sentences = sent_tokenize(text)
            
            for i, sentence in enumerate(sentences):
                # Check for basic grammar patterns
                
                # Subject-verb agreement (simplified)
                if self._check_subject_verb_agreement(sentence):
                    errors.append({
                        "type": "subject_verb_agreement",
                        "sentence": i + 1,
                        "description": "Possible subject-verb agreement issue",
                        "severity": "medium"
                    })
                
                # Article usage
                if self._check_article_usage(sentence):
                    errors.append({
                        "type": "article_usage",
                        "sentence": i + 1,
                        "description": "Possible article usage issue",
                        "severity": "low"
                    })
                
                # Tense consistency
                if self._check_tense_consistency(sentence):
                    errors.append({
                        "type": "tense_consistency",
                        "sentence": i + 1,
                        "description": "Possible tense consistency issue",
                        "severity": "medium"
                    })
            
        except Exception as e:
            logger.warning(f"Failed to detect grammar errors: {e}")
        
        return errors
    
    def _check_subject_verb_agreement(self, sentence: str) -> bool:
        """Check for basic subject-verb agreement issues."""
        # Simplified check - look for common patterns
        words = word_tokenize(sentence.lower())
        
        # Check for "is" with plural subjects (very basic)
        for i, word in enumerate(words):
            if word == "is" and i > 0:
                prev_word = words[i-1]
                if prev_word.endswith('s') and not prev_word.endswith('ss'):
                    return True
        
        return False
    
    def _check_article_usage(self, sentence: str) -> bool:
        """Check for article usage issues."""
        # Simplified check
        words = word_tokenize(sentence.lower())
        
        # Look for "a" before vowel sounds
        for i, word in enumerate(words):
            if word == "a" and i + 1 < len(words):
                next_word = words[i + 1]
                if next_word[0] in 'aeiou':
                    return True
        
        return False
    
    def _check_tense_consistency(self, sentence: str) -> bool:
        """Check for tense consistency issues."""
        # Simplified check
        words = word_tokenize(sentence.lower())
        
        # Look for mixed past/present forms
        has_past = any(word.endswith('ed') for word in words)
        has_present = any(word in ['is', 'are', 'am', 'have', 'has'] for word in words)
        
        return has_past and has_present
    
    def _calculate_coherence(self, text: str) -> float:
        """Calculate text coherence score."""
        try:
            sentences = sent_tokenize(text)
            if len(sentences) < 2:
                return 0.5
            
            # Calculate coherence based on:
            # 1. Logical connectors
            # 2. Topic consistency
            # 3. Sentence flow
            
            coherence_score = 0.0
            total_factors = 0
            
            # Factor 1: Logical connectors
            connectors = [
                'however', 'therefore', 'furthermore', 'moreover', 'nevertheless',
                'consequently', 'in addition', 'on the other hand', 'for example',
                'in conclusion', 'firstly', 'secondly', 'finally'
            ]
            
            connector_count = sum(1 for connector in connectors if connector in text.lower())
            connector_score = min(connector_count / len(sentences), 1.0)
            coherence_score += connector_score
            total_factors += 1
            
            # Factor 2: Topic consistency (simplified)
            # Count repeated key words
            words = word_tokenize(text.lower())
            word_freq = {}
            for word in words:
                if word.isalpha() and len(word) > 3:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Calculate topic consistency
            if word_freq:
                max_freq = max(word_freq.values())
                topic_score = min(max_freq / len(sentences), 1.0)
                coherence_score += topic_score
                total_factors += 1
            
            # Factor 3: Sentence length variation
            sentence_lengths = [len(word_tokenize(sent)) for sent in sentences]
            if sentence_lengths:
                length_variance = np.var(sentence_lengths)
                variation_score = min(length_variance / 10, 1.0)  # Normalize
                coherence_score += variation_score
                total_factors += 1
            
            return coherence_score / total_factors if total_factors > 0 else 0.5
            
        except Exception as e:
            logger.warning(f"Failed to calculate coherence: {e}")
            return 0.5
    
    def _calculate_task_relevance(self, text: str, task_type: TaskType) -> float:
        """Calculate task relevance score."""
        try:
            words = word_tokenize(text.lower())
            task_word_count = sum(1 for word in words if word in self.task_words)
            
            # Normalize by text length
            relevance_score = min(task_word_count / max(len(words), 1), 1.0)
            
            # Adjust based on task type
            if task_type in [TaskType.WRITING_TASK_1, TaskType.WRITING_TASK_2]:
                # Writing tasks should have more task-specific vocabulary
                return min(relevance_score * 1.5, 1.0)
            else:
                return relevance_score
                
        except Exception as e:
            logger.warning(f"Failed to calculate task relevance: {e}")
            return 0.5
    
    def _calculate_complexity_metrics(self, text: str) -> Dict[str, float]:
        """Calculate various complexity metrics."""
        try:
            words = word_tokenize(text.lower())
            sentences = sent_tokenize(text)
            
            # Remove stop words and non-alphabetic tokens
            content_words = [word for word in words if word.isalpha() and word not in self.stop_words]
            
            metrics = {}
            
            # Average word length
            if content_words:
                avg_word_length = sum(len(word) for word in content_words) / len(content_words)
                metrics['avg_word_length'] = round(avg_word_length, 2)
            else:
                metrics['avg_word_length'] = 0.0
            
            # Academic word ratio
            academic_word_count = sum(1 for word in content_words if word in self.academic_words)
            if content_words:
                academic_ratio = academic_word_count / len(content_words)
                metrics['academic_word_ratio'] = round(academic_ratio, 3)
            else:
                metrics['academic_word_ratio'] = 0.0
            
            # Sentence complexity (words per sentence)
            if sentences:
                avg_sentence_length = len(words) / len(sentences)
                metrics['avg_sentence_length'] = round(avg_sentence_length, 2)
            else:
                metrics['avg_sentence_length'] = 0.0
            
            # Lexical density (content words / total words)
            if words:
                lexical_density = len(content_words) / len(words)
                metrics['lexical_density'] = round(lexical_density, 3)
            else:
                metrics['lexical_density'] = 0.0
            
            # Flesch-Kincaid Grade Level
            try:
                grade_level = textstat.flesch_kincaid_grade(text)
                metrics['flesch_kincaid_grade'] = round(grade_level, 1)
            except:
                metrics['flesch_kincaid_grade'] = 0.0
            
            return metrics
            
        except Exception as e:
            logger.warning(f"Failed to calculate complexity metrics: {e}")
            return {
                'avg_word_length': 0.0,
                'academic_word_ratio': 0.0,
                'avg_sentence_length': 0.0,
                'lexical_density': 0.0,
                'flesch_kincaid_grade': 0.0
            }
    
    def get_feature_summary(self, features: FeatureAnalysis) -> str:
        """Generate a human-readable summary of features."""
        summary = f"""
        Text Analysis Summary:
        
        Basic Statistics:
        - Word count: {features.word_count}
        - Sentence count: {features.sentence_count}
        - Average sentence length: {features.avg_sentence_length} words
        
        Quality Metrics:
        - Readability score: {features.readability_score} (Flesch Reading Ease)
        - Vocabulary diversity: {features.vocabulary_diversity:.1%}
        - Coherence score: {features.coherence_score}/1.0
        - Task relevance: {features.task_relevance}/1.0
        
        Grammar Issues:
        - Total errors detected: {len(features.grammar_errors)}
        """
        
        if features.grammar_errors:
            summary += "\nGrammar Issues:\n"
            for error in features.grammar_errors[:5]:  # Show first 5
                summary += f"- {error['type']}: {error['description']}\n"
        
        if features.complexity_metrics:
            summary += f"""
        Complexity Metrics:
        - Average word length: {features.complexity_metrics.get('avg_word_length', 0)} characters
        - Academic word ratio: {features.complexity_metrics.get('academic_word_ratio', 0):.1%}
        - Lexical density: {features.complexity_metrics.get('lexical_density', 0):.1%}
        - Flesch-Kincaid Grade: {features.complexity_metrics.get('flesch_kincaid_grade', 0)}
        """
        
        return summary.strip()


# Global feature extractor instance
feature_extractor = FeatureExtractor()
