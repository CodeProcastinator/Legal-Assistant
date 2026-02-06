"""
Report Generator Module
Generates PDF and text reports for contract analysis
"""

from datetime import datetime
from typing import Dict, List
import io

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class ReportGenerator:
    """Generates professional PDF and text reports."""
    
    def __init__(self):
        self.styles = None
        if REPORTLAB_AVAILABLE:
            self.styles = getSampleStyleSheet()
            self.styles.add(ParagraphStyle(name='RiskHigh', parent=self.styles['Normal'], textColor=colors.red))
            self.styles.add(ParagraphStyle(name='RiskMedium', parent=self.styles['Normal'], textColor=colors.orange))
            self.styles.add(ParagraphStyle(name='RiskLow', parent=self.styles['Normal'], textColor=colors.green))
    
    def generate_pdf(self, analysis_data: Dict, filename: str = None) -> bytes:
        """Generate PDF report."""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab not installed. Run: pip install reportlab")
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        story = []
        
        # Title
        story.append(Paragraph("Contract Analysis Report", self.styles['Title']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Risk Score
        score = analysis_data.get('overall_score', 0)
        risk_level = analysis_data.get('risk_level', 'unknown')
        story.append(Paragraph(f"<b>Overall Risk Score: {score}/100 ({risk_level.upper()})</b>", self.styles['Heading2']))
        story.append(Spacer(1, 15))
        
        # Summary
        summary = analysis_data.get('summary', {})
        if summary:
            story.append(Paragraph("Executive Summary", self.styles['Heading2']))
            story.append(Paragraph(summary.get('assessment', ''), self.styles['Normal']))
            story.append(Paragraph(f"<b>Recommended Action:</b> {summary.get('recommended_action', '')}", self.styles['Normal']))
            story.append(Spacer(1, 15))
        
        # Statistics
        stats = analysis_data.get('statistics', {})
        if stats:
            story.append(Paragraph("Risk Statistics", self.styles['Heading2']))
            stats_data = [
                ['Category', 'Count'],
                ['Total Risks', str(stats.get('total_risks', 0))],
                ['Critical', str(stats.get('critical_risks', 0))],
                ['High', str(stats.get('high_risks', 0))],
                ['Medium', str(stats.get('medium_risks', 0))],
                ['Low', str(stats.get('low_risks', 0))]
            ]
            table = Table(stats_data, colWidths=[2*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
            ]))
            story.append(table)
            story.append(Spacer(1, 15))
        
        # Findings
        findings = analysis_data.get('findings', [])
        if findings:
            story.append(Paragraph("Risk Findings", self.styles['Heading2']))
            for i, finding in enumerate(findings[:10], 1):
                level = finding.get('level', 'low')
                style = self.styles.get(f'Risk{level.title()}', self.styles['Normal'])
                story.append(Paragraph(f"<b>{i}. {finding.get('category', 'Unknown')}</b> [{level.upper()}]", style))
                story.append(Paragraph(finding.get('description', ''), self.styles['Normal']))
                story.append(Paragraph(f"<i>Recommendation: {finding.get('recommendation', '')}</i>", self.styles['Normal']))
                story.append(Spacer(1, 10))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_text_report(self, analysis_data: Dict) -> str:
        """Generate plain text report."""
        lines = []
        lines.append("=" * 60)
        lines.append("CONTRACT ANALYSIS REPORT")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("=" * 60)
        lines.append("")
        
        # Risk Score
        score = analysis_data.get('overall_score', 0)
        risk_level = analysis_data.get('risk_level', 'unknown')
        lines.append(f"OVERALL RISK SCORE: {score}/100 ({risk_level.upper()})")
        lines.append("")
        
        # Summary
        summary = analysis_data.get('summary', {})
        if summary:
            lines.append("-" * 40)
            lines.append("EXECUTIVE SUMMARY")
            lines.append("-" * 40)
            lines.append(summary.get('assessment', ''))
            lines.append(f"\nRecommended Action: {summary.get('recommended_action', '')}")
            lines.append("")
        
        # Statistics
        stats = analysis_data.get('statistics', {})
        if stats:
            lines.append("-" * 40)
            lines.append("RISK STATISTICS")
            lines.append("-" * 40)
            lines.append(f"Total Risks: {stats.get('total_risks', 0)}")
            lines.append(f"  - Critical: {stats.get('critical_risks', 0)}")
            lines.append(f"  - High: {stats.get('high_risks', 0)}")
            lines.append(f"  - Medium: {stats.get('medium_risks', 0)}")
            lines.append(f"  - Low: {stats.get('low_risks', 0)}")
            lines.append("")
        
        # Findings
        findings = analysis_data.get('findings', [])
        if findings:
            lines.append("-" * 40)
            lines.append("RISK FINDINGS")
            lines.append("-" * 40)
            for i, finding in enumerate(findings, 1):
                lines.append(f"\n{i}. {finding.get('category', 'Unknown')} [{finding.get('level', 'low').upper()}]")
                lines.append(f"   {finding.get('description', '')}")
                lines.append(f"   Recommendation: {finding.get('recommendation', '')}")
        
        lines.append("")
        lines.append("=" * 60)
        lines.append("END OF REPORT")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def generate_html_report(self, analysis_data: Dict) -> str:
        """Generate HTML report."""
        score = analysis_data.get('overall_score', 0)
        risk_level = analysis_data.get('risk_level', 'unknown')
        summary = analysis_data.get('summary', {})
        stats = analysis_data.get('statistics', {})
        findings = analysis_data.get('findings', [])
        
        risk_color = {'high': '#dc3545', 'medium': '#fd7e14', 'low': '#28a745'}.get(risk_level, '#6c757d')
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Contract Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; }}
        .score-box {{ background: {risk_color}; color: white; padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0; }}
        .section {{ margin: 20px 0; }}
        .finding {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid; border-radius: 4px; }}
        .finding.high {{ border-color: #dc3545; }}
        .finding.medium {{ border-color: #fd7e14; }}
        .finding.low {{ border-color: #28a745; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; border: 1px solid #ddd; text-align: left; }}
        th {{ background: #333; color: white; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Contract Analysis Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </div>
    
    <div class="score-box">
        <h2>Risk Score: {score}/100</h2>
        <p>{risk_level.upper()} RISK</p>
    </div>
    
    <div class="section">
        <h2>Executive Summary</h2>
        <p>{summary.get('assessment', 'No summary available.')}</p>
        <p><strong>Recommended Action:</strong> {summary.get('recommended_action', 'Review the contract carefully.')}</p>
    </div>
    
    <div class="section">
        <h2>Risk Statistics</h2>
        <table>
            <tr><th>Category</th><th>Count</th></tr>
            <tr><td>Total Risks</td><td>{stats.get('total_risks', 0)}</td></tr>
            <tr><td>Critical</td><td>{stats.get('critical_risks', 0)}</td></tr>
            <tr><td>High</td><td>{stats.get('high_risks', 0)}</td></tr>
            <tr><td>Medium</td><td>{stats.get('medium_risks', 0)}</td></tr>
            <tr><td>Low</td><td>{stats.get('low_risks', 0)}</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Risk Findings</h2>"""
        
        for finding in findings[:10]:
            level = finding.get('level', 'low')
            html += f"""
        <div class="finding {level}">
            <h3>{finding.get('category', 'Unknown')} [{level.upper()}]</h3>
            <p>{finding.get('description', '')}</p>
            <p><em>Recommendation: {finding.get('recommendation', '')}</em></p>
        </div>"""
        
        html += """
    </div>
</body>
</html>"""
        return html
