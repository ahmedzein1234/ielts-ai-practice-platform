"""Text processing utilities for OCR results."""

import re
import unicodedata
from typing import List, Optional, Tuple

from .models import SpellCheckOptions, TextCleaningOptions


class TextProcessor:
    """Text cleaning and processing utilities."""
    
    @staticmethod
    def clean_text(text: str, options: Optional[TextCleaningOptions] = None) -> str:
        """Clean and normalize OCR text."""
        if not text:
            return ""
        
        if options is None:
            options = TextCleaningOptions()
        
        cleaned = text
        
        try:
            # Normalize unicode
            if options.normalize_unicode:
                cleaned = unicodedata.normalize('NFKC', cleaned)
            
            # Fix encoding issues
            if options.fix_encoding:
                cleaned = TextProcessor._fix_encoding_issues(cleaned)
            
            # Remove extra whitespace
            if options.remove_extra_whitespace:
                cleaned = re.sub(r'\s+', ' ', cleaned)
                cleaned = cleaned.strip()
            
            # Fix line breaks
            if options.fix_line_breaks:
                cleaned = TextProcessor._fix_line_breaks(cleaned)
            
            # Remove special characters if requested
            if options.remove_special_chars:
                cleaned = re.sub(r'[^\w\s\.,!?;:\-\'"()]', '', cleaned)
            
            return cleaned
            
        except Exception:
            # Return original text if cleaning fails
            return text
    
    @staticmethod
    def _fix_encoding_issues(text: str) -> str:
        """Fix common encoding issues in OCR text."""
        # Common OCR character substitutions
        replacements = {
            'â€™': "'",  # Smart apostrophe
            'â€œ': '"',  # Smart quote left
            'â€': '"',   # Smart quote right
            'â€"': '—',  # Em dash
            'â€"': '–',  # En dash
            'Â': '',     # Non-breaking space artifacts
            'â€¢': '•',  # Bullet point
            'â€¦': '...',# Ellipsis
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    @staticmethod
    def _fix_line_breaks(text: str) -> str:
        """Fix line breaks and paragraph structure."""
        # Replace multiple line breaks with double line breaks
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Fix broken words across lines
        text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)
        
        # Join lines that don't end with punctuation
        lines = text.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                fixed_lines.append('')
                continue
            
            # If line doesn't end with punctuation and next line doesn't start with capital
            if (i < len(lines) - 1 and 
                not re.search(r'[.!?:;]$', line) and 
                lines[i + 1].strip() and 
                not lines[i + 1].strip()[0].isupper()):
                # Join with next line
                continue
            else:
                # Add any accumulated text
                if i > 0 and not re.search(r'[.!?:;]$', lines[i-1].strip()):
                    if fixed_lines:
                        fixed_lines[-1] += ' ' + line
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    @staticmethod
    def extract_sentences(text: str) -> List[str]:
        """Extract sentences from text."""
        if not text:
            return []
        
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 3:  # Minimum sentence length
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    @staticmethod
    def extract_words(text: str) -> List[str]:
        """Extract words from text."""
        if not text:
            return []
        
        # Extract words (letters, numbers, apostrophes, hyphens)
        words = re.findall(r"\b[\w'-]+\b", text.lower())
        
        # Filter out very short words and numbers-only
        filtered_words = []
        for word in words:
            if len(word) >= 2 and not word.isdigit():
                filtered_words.append(word)
        
        return filtered_words
    
    @staticmethod
    def calculate_readability_stats(text: str) -> dict:
        """Calculate basic readability statistics."""
        if not text:
            return {
                "word_count": 0,
                "sentence_count": 0,
                "character_count": 0,
                "avg_words_per_sentence": 0.0,
                "avg_characters_per_word": 0.0
            }
        
        words = TextProcessor.extract_words(text)
        sentences = TextProcessor.extract_sentences(text)
        
        word_count = len(words)
        sentence_count = len(sentences)
        character_count = len(text.replace(' ', ''))
        
        avg_words_per_sentence = word_count / sentence_count if sentence_count > 0 else 0.0
        avg_characters_per_word = character_count / word_count if word_count > 0 else 0.0
        
        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "character_count": character_count,
            "avg_words_per_sentence": round(avg_words_per_sentence, 2),
            "avg_characters_per_word": round(avg_characters_per_word, 2)
        }
    
    @staticmethod
    def detect_language(text: str) -> str:
        """Simple language detection based on character patterns."""
        if not text:
            return "unknown"
        
        # Very basic language detection
        # In production, you'd use a proper language detection library
        
        # Count character types
        latin_chars = len(re.findall(r'[a-zA-Z]', text))
        total_chars = len(re.findall(r'[a-zA-Z\u00C0-\u017F\u0100-\u024F]', text))
        
        if total_chars == 0:
            return "unknown"
        
        latin_ratio = latin_chars / total_chars
        
        if latin_ratio > 0.8:
            return "en"  # Assume English for high Latin character ratio
        else:
            return "unknown"
    
    @staticmethod
    def format_for_ielts(text: str) -> str:
        """Format text according to IELTS writing conventions."""
        if not text:
            return ""
        
        # Clean the text first
        cleaned = TextProcessor.clean_text(text)
        
        # Ensure proper paragraph structure
        paragraphs = cleaned.split('\n\n')
        formatted_paragraphs = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if paragraph:
                # Ensure paragraph starts with capital letter
                if paragraph[0].islower():
                    paragraph = paragraph[0].upper() + paragraph[1:]
                
                # Ensure paragraph ends with punctuation
                if not re.search(r'[.!?]$', paragraph):
                    paragraph += '.'
                
                formatted_paragraphs.append(paragraph)
        
        return '\n\n'.join(formatted_paragraphs)
    
    @staticmethod
    def extract_key_phrases(text: str, max_phrases: int = 10) -> List[str]:
        """Extract key phrases from text."""
        if not text:
            return []
        
        # Simple key phrase extraction
        # In production, you'd use NLP libraries like spaCy or NLTK
        
        words = TextProcessor.extract_words(text)
        
        # Find common word combinations (bigrams, trigrams)
        phrases = []
        
        # Bigrams
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}"
            phrases.append(phrase)
        
        # Trigrams
        for i in range(len(words) - 2):
            phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
            phrases.append(phrase)
        
        # Count frequency and return most common
        from collections import Counter
        phrase_counts = Counter(phrases)
        
        return [phrase for phrase, count in phrase_counts.most_common(max_phrases)]
