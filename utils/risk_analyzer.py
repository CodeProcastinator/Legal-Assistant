"""
Risk Analyzer Module
Identifies and scores risks in legal contracts
"""

import re
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskItem:
    category: str
    level: RiskLevel
    description: str
    clause_text: str
    recommendation: str
    score: float


class RiskAnalyzer:
    """Analyzes contracts for legal and business risks."""
    
    RISK_PATTERNS = {
        'unlimited_liability': {
            'patterns': [r'unlimited\s+liability', r'liable\s+for\s+(?:any|all)'],
            'level': RiskLevel.CRITICAL,
            'description': 'Unlimited liability clauses expose your business to significant risk.',
            'recommendation': 'Negotiate a liability cap, typically 1-2x the contract value.'
        },
        'one_sided_termination': {
            'patterns': [r'may\s+terminate\s+(?:at\s+)?(?:any\s+time|without\s+cause)', r'sole\s+discretion\s+to\s+terminate'],
            'level': RiskLevel.HIGH,
            'description': 'One party has disproportionate termination rights.',
            'recommendation': 'Ensure mutual termination rights with adequate notice period.'
        },
        'automatic_renewal': {
            'patterns': [r'automatic(?:ally)?\s+renew', r'auto[\s-]?renew'],
            'level': RiskLevel.MEDIUM,
            'description': 'Contract auto-renews which may lock you into unfavorable terms.',
            'recommendation': 'Add a clause requiring written notice before renewal.'
        },
        'broad_indemnification': {
            'patterns': [r'indemnify\s+(?:and\s+)?hold\s+harmless', r'indemnify\s+against\s+(?:any|all)'],
            'level': RiskLevel.HIGH,
            'description': 'Broad indemnification may require covering unlimited claims.',
            'recommendation': 'Limit indemnification to direct damages caused by your breach.'
        },
        'ip_assignment': {
            'patterns': [r'assign\s+(?:all\s+)?(?:intellectual\s+property|ip)', r'work[\s-]?for[\s-]?hire'],
            'level': RiskLevel.HIGH,
            'description': 'You may be giving away intellectual property rights.',
            'recommendation': 'Exclude pre-existing IP. Consider licensing instead.'
        },
        'non_compete': {
            'patterns': [r'non[\s-]?compete', r'shall\s+not\s+compete'],
            'level': RiskLevel.MEDIUM,
            'description': 'Non-compete clauses may restrict future business opportunities.',
            'recommendation': 'Limit scope, geography, and duration.'
        },
        'penalty_clauses': {
            'patterns': [r'penalty\s+(?:of|amount)', r'liquidated\s+damages'],
            'level': RiskLevel.MEDIUM,
            'description': 'Contract contains penalty provisions.',
            'recommendation': 'Ensure penalties are proportionate. Add cure periods.'
        },
        'warranty_disclaimer': {
            'patterns': [r'as[\s-]?is', r'disclaim\s+(?:all\s+)?warrant'],
            'level': RiskLevel.HIGH,
            'description': 'Seller disclaims warranties, leaving no recourse for defects.',
            'recommendation': 'Request fitness for purpose warranty.'
        },
        'unfavorable_payment': {
            'patterns': [r'payment\s+(?:within|by)\s+(?:7|five|5)\s+days', r'payment\s+in\s+advance'],
            'level': RiskLevel.MEDIUM,
            'description': 'Payment terms may strain cash flow.',
            'recommendation': 'Negotiate 30-45 day payment terms.'
        },
        'foreign_jurisdiction': {
            'patterns': [r'jurisdiction\s+of\s+(?!.*india)', r'governed\s+by\s+(?:the\s+)?laws?\s+of\s+(?!.*india)'],
            'level': RiskLevel.HIGH,
            'description': 'Dispute resolution outside India increases legal complexity.',
            'recommendation': 'Negotiate for Indian jurisdiction.'
        }
    }
    
    def __init__(self):
        self.findings = []
        self.overall_score = 0
    
    def analyze(self, text: str, contract_type: str = 'general') -> Dict:
        self.findings = []
        text_lower = text.lower()
        
        for risk_id, config in self.RISK_PATTERNS.items():
            for pattern in config['patterns']:
                if re.search(pattern, text_lower):
                    match = re.search(pattern, text_lower)
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 100)
                    
                    self.findings.append(RiskItem(
                        category=risk_id,
                        level=config['level'],
                        description=config['description'],
                        clause_text=text[start:end].strip(),
                        recommendation=config['recommendation'],
                        score=self._level_to_score(config['level'])
                    ))
                    break
        
        self.overall_score = self._calculate_overall_score()
        
        return {
            'findings': [self._to_dict(f) for f in self.findings],
            'overall_score': self.overall_score,
            'risk_level': self._score_to_level(self.overall_score),
            'summary': self._generate_summary(contract_type),
            'statistics': {
                'total_risks': len(self.findings),
                'critical_risks': sum(1 for f in self.findings if f.level == RiskLevel.CRITICAL),
                'high_risks': sum(1 for f in self.findings if f.level == RiskLevel.HIGH),
                'medium_risks': sum(1 for f in self.findings if f.level == RiskLevel.MEDIUM),
                'low_risks': sum(1 for f in self.findings if f.level == RiskLevel.LOW)
            }
        }
    
    def _level_to_score(self, level: RiskLevel) -> float:
        return {RiskLevel.LOW: 0.2, RiskLevel.MEDIUM: 0.4, RiskLevel.HIGH: 0.7, RiskLevel.CRITICAL: 1.0}.get(level, 0.5)
    
    def _score_to_level(self, score: float) -> str:
        if score >= 70: return 'high'
        elif score >= 40: return 'medium'
        return 'low'
    
    def _calculate_overall_score(self) -> float:
        if not self.findings: return 15
        weights = {RiskLevel.CRITICAL: 4, RiskLevel.HIGH: 3, RiskLevel.MEDIUM: 2, RiskLevel.LOW: 1}
        total_weight = sum(weights[f.level] for f in self.findings)
        weighted_score = sum(f.score * weights[f.level] for f in self.findings)
        return min(100, round((weighted_score / max(total_weight, 1)) * 100 * min(1.5, 1 + len(self.findings) * 0.05)))
    
    def _generate_summary(self, contract_type: str) -> Dict:
        critical = sum(1 for f in self.findings if f.level == RiskLevel.CRITICAL)
        high = sum(1 for f in self.findings if f.level == RiskLevel.HIGH)
        
        if critical > 0:
            assessment = "Critical risk clauses require immediate attention."
            action = "Do not sign without addressing critical issues."
        elif high >= 2:
            assessment = "Multiple high-risk clauses should be renegotiated."
            action = "Negotiate key terms before signing."
        else:
            assessment = "Contract appears reasonably balanced."
            action = "Review carefully before signing."
        
        return {'assessment': assessment, 'recommended_action': action, 'risk_score': self.overall_score}
    
    def _to_dict(self, item: RiskItem) -> Dict:
        return {
            'category': item.category.replace('_', ' ').title(),
            'level': item.level.value,
            'description': item.description,
            'clause_text': item.clause_text[:500],
            'recommendation': item.recommendation,
            'score': round(item.score * 100)
        }
    
    def get_clause_risk(self, clause_text: str) -> Dict:
        text_lower = clause_text.lower()
        risks = []
        
        for risk_id, config in self.RISK_PATTERNS.items():
            for pattern in config['patterns']:
                if re.search(pattern, text_lower):
                    risks.append({'type': risk_id.replace('_', ' ').title(), 'level': config['level'].value, 'recommendation': config['recommendation']})
                    break
        
        if not risks:
            return {'has_risks': False, 'risk_level': 'low', 'risks': []}
        
        return {'has_risks': True, 'risk_level': max(r['level'] for r in risks), 'risks': risks}
