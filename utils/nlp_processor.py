"""
NLP Processor Module
Handles natural language processing for contract analysis using spaCy
"""

import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from collections import defaultdict

try:
    import spacy
    from spacy.tokens import Doc
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    import nltk
    from nltk.tokenize import sent_tokenize
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False


class NLPProcessor:
    """
    NLP Processor for legal document analysis.
    Uses spaCy for entity extraction and text analysis.
    """
    
    # Indian-specific patterns
    INDIAN_AMOUNT_PATTERN = r'(?:Rs\.?|INR|₹)\s*[\d,]+(?:\.\d{2})?(?:\s*(?:lakhs?|crores?|thousands?))?'
    PAN_PATTERN = r'[A-Z]{5}\d{4}[A-Z]'
    GSTIN_PATTERN = r'\d{2}[A-Z]{5}\d{4}[A-Z]\d[Z][A-Z\d]'
    CIN_PATTERN = r'[LU]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}'
    
    # Date patterns
    DATE_PATTERNS = [
        r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',  # DD-MM-YYYY
        r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',  # YYYY-MM-DD
        r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
        r'\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',
        r'\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}',
    ]
    
    # Legal terms
    LEGAL_KEYWORDS = {
        'obligations': ['shall', 'must', 'obligated', 'required to', 'duty to', 'responsible for'],
        'rights': ['may', 'entitled to', 'right to', 'option to', 'permitted to'],
        'prohibitions': ['shall not', 'must not', 'prohibited', 'forbidden', 'restricted'],
        'conditions': ['provided that', 'subject to', 'conditional upon', 'in the event'],
        'termination': ['terminate', 'termination', 'expiry', 'expire', 'end of term'],
        'indemnity': ['indemnify', 'indemnification', 'hold harmless', 'indemnity'],
        'liability': ['liability', 'liable', 'damages', 'compensation', 'remedy'],
        'confidentiality': ['confidential', 'non-disclosure', 'proprietary', 'trade secret'],
        'dispute': ['dispute', 'arbitration', 'jurisdiction', 'governing law', 'legal proceedings'],
        'payment': ['payment', 'consideration', 'fee', 'remuneration', 'compensation']
    }
    
    def __init__(self):
        self.nlp = None
        self._load_nlp_model()
        
        if NLTK_AVAILABLE:
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                try:
                    nltk.download('punkt', quiet=True)
                except:
                    pass
    
    def _load_nlp_model(self):
        """Load spaCy model."""
        if not SPACY_AVAILABLE:
            return
        
        # Try different models
        models_to_try = ['en_core_web_sm', 'en_core_web_md', 'en_core_web_lg']
        
        for model in models_to_try:
            try:
                self.nlp = spacy.load(model)
                return
            except OSError:
                continue
        
        # If no model found, try to download
        try:
            import subprocess
            subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'], 
                         capture_output=True, timeout=120)
            self.nlp = spacy.load('en_core_web_sm')
        except:
            self.nlp = None
    
    def analyze(self, text: str) -> Dict:
        """
        Perform comprehensive NLP analysis on text.
        
        Args:
            text: Document text to analyze
            
        Returns:
            Dict containing entities, clauses, and analysis results
        """
        result = {
            'entities': self._extract_entities(text),
            'clauses': self._extract_clauses(text),
            'key_terms': self._extract_legal_terms(text),
            'dates': self._extract_dates(text),
            'monetary_values': self._extract_monetary_values(text),
            'statistics': self._compute_statistics(text),
            'language_detection': self._detect_language(text)
        }
        
        return result
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text."""
        entities = defaultdict(list)
        
        # Use spaCy if available
        if self.nlp:
            # Process in chunks to handle large documents
            max_length = 100000
            chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
            
            for chunk in chunks:
                try:
                    doc = self.nlp(chunk)
                    for ent in doc.ents:
                        if ent.text.strip() and len(ent.text) > 1:
                            entities[ent.label_].append(ent.text.strip())
                except:
                    pass
        
        # Extract Indian-specific entities
        entities['PAN'].extend(re.findall(self.PAN_PATTERN, text))
        entities['GSTIN'].extend(re.findall(self.GSTIN_PATTERN, text))
        entities['CIN'].extend(re.findall(self.CIN_PATTERN, text))
        
        # Deduplicate
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return dict(entities)
    
    def _extract_clauses(self, text: str) -> List[Dict]:
        """Extract and categorize contract clauses."""
        clauses = []
        
        # Split into sentences
        if NLTK_AVAILABLE:
            try:
                sentences = sent_tokenize(text)
            except:
                sentences = re.split(r'[.!?]+', text)
        else:
            sentences = re.split(r'[.!?]+', text)
        
        # Section patterns
        section_pattern = re.compile(
            r'^(?:\d+\.?\s*|\(?[a-z]\)\s*|\(?[ivxlc]+\)\s*)?(.+)$',
            re.IGNORECASE
        )
        
        current_section = "General"
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence or len(sentence) < 10:
                continue
            
            # Check if this is a section header
            if self._is_section_header(sentence):
                current_section = sentence[:100]
                continue
            
            # Categorize clause
            clause_type = self._categorize_clause(sentence)
            importance = self._calculate_importance(sentence)
            
            clauses.append({
                'id': i + 1,
                'text': sentence,
                'section': current_section,
                'type': clause_type,
                'importance': importance,
                'word_count': len(sentence.split())
            })
        
        return clauses
    
    def _is_section_header(self, text: str) -> bool:
        """Check if text is a section header."""
        text = text.strip()
        
        # Short text with pattern
        if len(text) < 100:
            patterns = [
                r'^(?:ARTICLE|SECTION|CLAUSE|PART|SCHEDULE)\s+[IVXLCDM\d]+',
                r'^\d+\.\s+[A-Z]',
                r'^[A-Z][A-Z\s]+$',  # All caps
            ]
            return any(re.match(p, text) for p in patterns)
        
        return False
    
    def _categorize_clause(self, text: str) -> str:
        """Categorize a clause based on its content."""
        text_lower = text.lower()
        
        for category, keywords in self.LEGAL_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                return category
        
        return 'general'
    
    def _calculate_importance(self, text: str) -> str:
        """Calculate importance level of a clause."""
        text_lower = text.lower()
        
        high_importance_indicators = [
            'indemnify', 'liability', 'terminate', 'breach', 'penalty',
            'damages', 'forfeit', 'confidential', 'non-compete',
            'exclusive', 'irrevocable', 'perpetual', 'unlimited'
        ]
        
        medium_importance_indicators = [
            'shall', 'must', 'agree', 'obligated', 'required',
            'payment', 'deliver', 'warranty', 'guarantee'
        ]
        
        high_count = sum(1 for kw in high_importance_indicators if kw in text_lower)
        medium_count = sum(1 for kw in medium_importance_indicators if kw in text_lower)
        
        if high_count >= 2:
            return 'high'
        elif high_count >= 1 or medium_count >= 2:
            return 'medium'
        return 'low'
    
    def _extract_legal_terms(self, text: str) -> Dict[str, int]:
        """Extract and count legal terms."""
        text_lower = text.lower()
        term_counts = {}
        
        all_keywords = []
        for keywords in self.LEGAL_KEYWORDS.values():
            all_keywords.extend(keywords)
        
        for term in set(all_keywords):
            count = text_lower.count(term)
            if count > 0:
                term_counts[term] = count
        
        # Sort by count
        return dict(sorted(term_counts.items(), key=lambda x: x[1], reverse=True))
    
    def _extract_dates(self, text: str) -> List[Dict]:
        """Extract dates from text."""
        dates = []
        
        for pattern in self.DATE_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_str = match.group()
                context = text[max(0, match.start()-50):min(len(text), match.end()+50)]
                
                # Try to determine date context
                date_type = 'general'
                context_lower = context.lower()
                
                if any(kw in context_lower for kw in ['effective', 'commencement', 'start']):
                    date_type = 'effective_date'
                elif any(kw in context_lower for kw in ['expiry', 'end', 'termination', 'expire']):
                    date_type = 'expiry_date'
                elif any(kw in context_lower for kw in ['execution', 'signed', 'signature']):
                    date_type = 'execution_date'
                elif any(kw in context_lower for kw in ['payment', 'due', 'payable']):
                    date_type = 'payment_date'
                
                dates.append({
                    'value': date_str,
                    'type': date_type,
                    'context': context.strip()
                })
        
        # Deduplicate by value
        seen = set()
        unique_dates = []
        for d in dates:
            if d['value'] not in seen:
                seen.add(d['value'])
                unique_dates.append(d)
        
        return unique_dates
    
    def _extract_monetary_values(self, text: str) -> List[Dict]:
        """Extract monetary values from text."""
        values = []
        
        # Indian amount patterns
        patterns = [
            (r'(?:Rs\.?|INR|₹)\s*([\d,]+(?:\.\d{2})?)\s*(?:(lakhs?|crores?|thousands?))?', 'INR'),
            (r'\$\s*([\d,]+(?:\.\d{2})?)\s*(?:(million|thousand|billion))?', 'USD'),
            (r'([\d,]+(?:\.\d{2})?)\s*(?:rupees|indian rupees)', 'INR'),
        ]
        
        for pattern, currency in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = float(amount_str)
                except ValueError:
                    continue
                
                # Apply multiplier
                multiplier_map = {
                    'thousand': 1000, 'thousands': 1000,
                    'lakh': 100000, 'lakhs': 100000,
                    'crore': 10000000, 'crores': 10000000,
                    'million': 1000000, 'billion': 1000000000
                }
                
                if match.lastindex and match.lastindex >= 2 and match.group(2):
                    multiplier = multiplier_map.get(match.group(2).lower(), 1)
                    amount *= multiplier
                
                context = text[max(0, match.start()-50):min(len(text), match.end()+50)]
                
                values.append({
                    'original': match.group(),
                    'amount': amount,
                    'currency': currency,
                    'context': context.strip()
                })
        
        return values
    
    def _compute_statistics(self, text: str) -> Dict:
        """Compute text statistics."""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return {
            'character_count': len(text),
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_word_length': sum(len(w) for w in words) / max(len(words), 1),
            'avg_sentence_length': len(words) / max(len(sentences), 1),
            'paragraph_count': text.count('\n\n') + 1
        }
    
    def _detect_language(self, text: str) -> Dict:
        """Detect language of the text."""
        # Simple heuristic-based detection
        hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        total_chars = max(hindi_chars + english_chars, 1)
        
        hindi_ratio = hindi_chars / total_chars
        english_ratio = english_chars / total_chars
        
        if hindi_ratio > 0.3:
            primary_language = 'Hindi' if hindi_ratio > english_ratio else 'Mixed (English-Hindi)'
        else:
            primary_language = 'English'
        
        return {
            'primary': primary_language,
            'english_ratio': round(english_ratio, 2),
            'hindi_ratio': round(hindi_ratio, 2),
            'is_multilingual': hindi_ratio > 0.1 and english_ratio > 0.1
        }
    
    def identify_parties(self, text: str) -> List[Dict]:
        """Identify parties mentioned in the contract."""
        parties = []
        
        # Common party introduction patterns
        patterns = [
            r'(?:between|by and between)\s+([A-Z][A-Za-z\s,]+?)(?:\s*\(|,?\s*(?:hereinafter|a company|an individual|having))',
            r'(?:Party|PARTY)\s*(?:A|1|ONE|of the First Part)[:\s]+([A-Za-z\s]+)',
            r'(?:Party|PARTY)\s*(?:B|2|TWO|of the Second Part)[:\s]+([A-Za-z\s]+)',
            r'"([^"]+)"\s*(?:hereinafter|herein after)',
            r'([A-Z][A-Za-z\s]+(?:LLP|Pvt\.?\s*Ltd\.?|Private Limited|Limited|Inc\.?|LLC|Corporation|Corp\.?))',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text[:5000])  # Focus on beginning
            for match in matches:
                party_name = match.group(1).strip()
                if party_name and len(party_name) > 2 and len(party_name) < 100:
                    # Determine party type
                    party_type = 'organization'
                    if any(kw in party_name.lower() for kw in ['mr.', 'mrs.', 'ms.', 'dr.', 'individual']):
                        party_type = 'individual'
                    
                    parties.append({
                        'name': party_name,
                        'type': party_type,
                        'context': text[max(0, match.start()-20):min(len(text), match.end()+100)]
                    })
        
        # Deduplicate
        seen = set()
        unique_parties = []
        for p in parties:
            name_normalized = p['name'].lower().strip()
            if name_normalized not in seen:
                seen.add(name_normalized)
                unique_parties.append(p)
        
        return unique_parties


# For testing
if __name__ == "__main__":
    processor = NLPProcessor()
    
    sample_text = """
    VENDOR AGREEMENT
    
    This Agreement is entered into between ABC Technologies Pvt. Ltd. 
    (hereinafter referred to as "Company") and XYZ Suppliers 
    (hereinafter referred to as "Vendor") on 15th January 2024.
    
    1. TERM: This agreement shall be effective from January 15, 2024 
    and shall remain valid until December 31, 2024.
    
    2. PAYMENT: The Company shall pay Rs. 5,00,000 (Five Lakhs) 
    within 30 days of invoice receipt.
    
    3. TERMINATION: Either party may terminate this agreement 
    with 60 days written notice. In case of breach, the defaulting 
    party shall pay damages of Rs. 1,00,000.
    
    4. CONFIDENTIALITY: Both parties shall maintain confidentiality 
    of all proprietary information shared during this engagement.
    
    GSTIN: 27AABCU9603R1ZM
    """
    
    result = processor.analyze(sample_text)
    
    print("=== NLP Analysis Results ===\n")
    print(f"Statistics: {result['statistics']}")
    print(f"\nDates Found: {len(result['dates'])}")
    for d in result['dates']:
        print(f"  - {d['value']} ({d['type']})")
    print(f"\nMonetary Values: {len(result['monetary_values'])}")
    for v in result['monetary_values']:
        print(f"  - {v['original']} = {v['currency']} {v['amount']:,.2f}")
    print(f"\nLanguage: {result['language_detection']}")
    print(f"\nKey Terms: {list(result['key_terms'].keys())[:10]}")
