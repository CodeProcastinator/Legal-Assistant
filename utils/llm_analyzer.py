"""
LLM Analyzer Module
Integration with Google Gemini API for AI-powered contract analysis
"""

import os
import json
from typing import Dict, List, Optional

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class LLMAnalyzer:
    """AI-powered contract analysis using Google Gemini."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        self.model = None
        self.is_configured = False
        
        if self.api_key and GENAI_AVAILABLE:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.is_configured = True
            except Exception as e:
                print(f"Error configuring Gemini: {e}")
    
    def analyze_contract(self, text: str, contract_type: str = 'general') -> Dict:
        """Comprehensive AI analysis of contract."""
        if not self.is_configured:
            return self._get_fallback_response("Contract analysis", text)
        
        prompt = f"""Analyze this {contract_type} contract for an Indian SME. Provide:

1. **Summary**: 2-3 sentence plain language overview
2. **Key Terms**: List 5-7 most important terms
3. **Risks**: Identify potential risks for the SME
4. **Recommendations**: Negotiation suggestions
5. **Red Flags**: Any concerning clauses

Contract Text:
{text[:8000]}

Respond in JSON format:
{{
    "summary": "...",
    "key_terms": ["term1", "term2"],
    "risks": [{{"issue": "...", "severity": "high/medium/low", "explanation": "..."}}],
    "recommendations": ["..."],
    "red_flags": ["..."],
    "overall_assessment": "favorable/neutral/unfavorable"
}}"""
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_json_response(response.text, "analysis")
        except Exception as e:
            return self._get_fallback_response("Contract analysis", str(e))
    
    def explain_clause(self, clause_text: str) -> Dict:
        """Explain a specific clause in plain language."""
        if not self.is_configured:
            return self._get_fallback_response("Clause explanation", clause_text)
        
        prompt = f"""Explain this legal clause in simple terms for a small business owner in India:

Clause: "{clause_text}"

Provide:
1. Plain language explanation (2-3 sentences)
2. What this means for you practically
3. Any concerns to watch for
4. Suggested modifications if unfavorable

Respond in JSON:
{{
    "explanation": "...",
    "practical_impact": "...",
    "concerns": ["..."],
    "suggested_changes": "..."
}}"""
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_json_response(response.text, "explanation")
        except Exception as e:
            return self._get_fallback_response("Clause explanation", str(e))
    
    def compare_clauses(self, original: str, proposed: str) -> Dict:
        """Compare two versions of a clause."""
        if not self.is_configured:
            return self._get_fallback_response("Clause comparison", "")
        
        prompt = f"""Compare these two contract clause versions:

ORIGINAL: "{original}"

PROPOSED: "{proposed}"

Analyze:
1. Key differences
2. Which is more favorable for SME
3. Risk changes
4. Recommendation

Respond in JSON:
{{
    "differences": ["..."],
    "more_favorable": "original/proposed/neutral",
    "risk_change": "increased/decreased/same",
    "explanation": "...",
    "recommendation": "..."
}}"""
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_json_response(response.text, "comparison")
        except Exception as e:
            return self._get_fallback_response("Clause comparison", str(e))
    
    def suggest_alternative_clause(self, clause_text: str, concern: str) -> Dict:
        """Suggest alternative clause wording."""
        if not self.is_configured:
            return self._get_fallback_response("Alternative clause", clause_text)
        
        prompt = f"""Suggest an alternative clause that addresses this concern:

Original Clause: "{clause_text}"
Concern: "{concern}"

Provide a revised clause that:
1. Is more balanced for both parties
2. Addresses the concern
3. Is legally sound for Indian contracts

Respond in JSON:
{{
    "alternative_clause": "...",
    "changes_made": ["..."],
    "explanation": "...",
    "negotiation_tip": "..."
}}"""
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_json_response(response.text, "alternative")
        except Exception as e:
            return self._get_fallback_response("Alternative clause", str(e))
    
    def ask_question(self, question: str, contract_text: str) -> Dict:
        """Answer questions about the contract."""
        if not self.is_configured:
            return self._get_fallback_response("Question", question)
        
        prompt = f"""Based on this contract, answer the question:

Contract: {contract_text[:6000]}

Question: {question}

Provide a clear, helpful answer for a small business owner. If the answer isn't in the contract, say so.

Respond in JSON:
{{
    "answer": "...",
    "relevant_clauses": ["..."],
    "confidence": "high/medium/low",
    "additional_context": "..."
}}"""
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_json_response(response.text, "answer")
        except Exception as e:
            return self._get_fallback_response("Question", str(e))
    
    def generate_summary_report(self, analysis_data: Dict) -> str:
        """Generate a comprehensive summary report."""
        if not self.is_configured:
            return self._generate_basic_report(analysis_data)
        
        prompt = f"""Create a professional summary report for this contract analysis:

Analysis Data: {json.dumps(analysis_data, indent=2)[:4000]}

Write a clear, professional report that:
1. Summarizes key findings
2. Highlights risks
3. Provides actionable recommendations
4. Uses simple language

Format as markdown with headers."""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except:
            return self._generate_basic_report(analysis_data)
    
    def _parse_json_response(self, text: str, response_type: str) -> Dict:
        """Parse JSON from LLM response."""
        try:
            # Extract JSON from response
            text = text.strip()
            if text.startswith('```'):
                text = text.split('```')[1]
                if text.startswith('json'):
                    text = text[4:]
            return json.loads(text)
        except:
            return {"raw_response": text, "type": response_type, "parsed": False}
    
    def _get_fallback_response(self, operation: str, context: str) -> Dict:
        """Provide fallback when AI is unavailable."""
        return {
            "status": "ai_unavailable",
            "message": f"AI analysis unavailable. Configure GEMINI_API_KEY for {operation}.",
            "fallback_advice": "Review the contract manually or consult a legal professional.",
            "api_configured": self.is_configured
        }
    
    def _generate_basic_report(self, data: Dict) -> str:
        """Generate basic report without AI."""
        return f"""# Contract Analysis Report

## Overview
This report summarizes the analysis of the uploaded contract.

## Risk Score: {data.get('overall_score', 'N/A')}/100

## Key Findings
- Total risks identified: {data.get('statistics', {}).get('total_risks', 0)}
- Critical risks: {data.get('statistics', {}).get('critical_risks', 0)}
- High risks: {data.get('statistics', {}).get('high_risks', 0)}

## Recommendations
Review all highlighted clauses and consider consulting a legal professional.

---
*Note: AI-powered insights unavailable. Configure API key for detailed analysis.*
"""
    
    def check_status(self) -> Dict:
        """Check API configuration status."""
        return {
            "configured": self.is_configured,
            "api_key_present": bool(self.api_key),
            "library_available": GENAI_AVAILABLE,
            "model": "gemini-1.5-flash" if self.is_configured else None
        }
