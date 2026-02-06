"""
GenAI Legal Assistant - Main Streamlit Application
AI-powered contract analysis for Indian SMEs
"""

import streamlit as st
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import utilities
from utils.document_parser import DocumentParser
from utils.nlp_processor import NLPProcessor
from utils.risk_analyzer import RiskAnalyzer
from utils.llm_analyzer import LLMAnalyzer
from utils.report_generator import ReportGenerator

# Page configuration
st.set_page_config(
    page_title="Legal Assistant - AI Contract Analysis",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .risk-high { background-color: #fee2e2; border-left: 4px solid #dc2626; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; }
    .risk-medium { background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; }
    .risk-low { background-color: #d1fae5; border-left: 4px solid #10b981; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; }
    .metric-card { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 1.5rem; border-radius: 1rem; text-align: center; }
    .stTabs [data-baseweb="tab-list"] { gap: 2rem; }
    .stTabs [data-baseweb="tab"] { font-size: 1.1rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    # Prioritize environment variable
    env_key = os.getenv('GEMINI_API_KEY')
    
    defaults = {
        'contract_text': '',
        'analysis_result': None,
        'nlp_result': None,
        'ai_result': None,
        'contract_type': 'general',
        'api_key': env_key if env_key else ''
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar():
    """Render sidebar with settings."""
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/law.png", width=80)
        st.markdown("## ⚖️ Legal Assistant")
        st.markdown("AI-powered contract analysis for Indian SMEs")
        st.divider()
        
        # API Key configuration
        st.markdown("### 🔑 API Configuration")
        
        # Check if key is configured (either in session or env)
        has_key = bool(st.session_state.api_key)
        
        if has_key:
            st.success("✅ API Key Configured")
            st.markdown("Using secure key from environment.")
            
            # Option to change key
            with st.expander("Change API Key"):
                new_key = st.text_input(
                    "Enter new key",
                    type="password",
                    help="Overrides the environment key for this session"
                )
                if new_key:
                    st.session_state.api_key = new_key
                    os.environ['GEMINI_API_KEY'] = new_key
                    st.rerun()
        else:
            api_key = st.text_input(
                "Gemini API Key",
                type="password",
                help="Get free API key from Google AI Studio"
            )
            
            if api_key:
                st.session_state.api_key = api_key
                os.environ['GEMINI_API_KEY'] = api_key
                st.rerun()
            
            st.warning("⚠️ Add API key for AI features")
            st.markdown("[Get Free API Key →](https://makersuite.google.com/app/apikey)")
        
        st.divider()
        
        # Contract type selector
        st.markdown("### 📋 Contract Type")
        contract_types = ['General', 'Employment', 'Vendor', 'Service', 'Lease', 'NDA', 'Partnership']
        st.session_state.contract_type = st.selectbox(
            "Select type for better analysis",
            contract_types
        ).lower()
        
        st.divider()
        st.markdown("### 📊 About")
        st.info("Built for Indian SMEs. Analyzes contracts for risks, extracts key terms, and provides AI-powered recommendations.")
        st.markdown("Made with ❤️ for GUVI Hackathon 2026")


def render_upload_tab():
    """Render contract upload tab."""
    st.markdown("## 📤 Upload Contract")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload your contract",
            type=['pdf', 'docx', 'txt'],
            help="Supported: PDF, DOCX, TXT files"
        )
        
        if uploaded_file:
            parser = DocumentParser()
            content = uploaded_file.read()
            result = parser.parse(content, uploaded_file.name)
            
            if result['success']:
                st.session_state.contract_text = result['text']
                st.success(f"✅ Parsed successfully! {result['metadata'].get('word_count', 0)} words")
                
                # Show metadata
                with st.expander("📊 Document Info"):
                    cols = st.columns(3)
                    cols[0].metric("Words", result['metadata'].get('word_count', 0))
                    cols[1].metric("Characters", result['metadata'].get('char_count', 0))
                    cols[2].metric("Est. Pages", result['metadata'].get('page_estimate', 1))
            else:
                st.error(f"❌ Error: {result['error']}")
    
    with col2:
        st.markdown("### Or paste text:")
        pasted_text = st.text_area(
            "Contract text",
            height=200,
            placeholder="Paste your contract text here..."
        )
        if pasted_text:
            st.session_state.contract_text = pasted_text
    
    # Preview
    if st.session_state.contract_text:
        st.divider()
        st.markdown("### 📄 Contract Preview")
        with st.expander("View full contract", expanded=False):
            st.text(st.session_state.contract_text[:5000] + ("..." if len(st.session_state.contract_text) > 5000 else ""))
        
        if st.button("🔍 Analyze Contract", type="primary", use_container_width=True):
            analyze_contract()


def analyze_contract():
    """Run full contract analysis."""
    with st.spinner("Analyzing contract..."):
        # Risk Analysis
        risk_analyzer = RiskAnalyzer()
        st.session_state.analysis_result = risk_analyzer.analyze(
            st.session_state.contract_text,
            st.session_state.contract_type
        )
        
        # NLP Analysis
        nlp_processor = NLPProcessor()
        st.session_state.nlp_result = nlp_processor.analyze(st.session_state.contract_text)
        
        # AI Analysis
        if st.session_state.api_key:
            llm = LLMAnalyzer(st.session_state.api_key)
            st.session_state.ai_result = llm.analyze_contract(
                st.session_state.contract_text,
                st.session_state.contract_type
            )
        
        st.success("✅ Analysis complete! Check the tabs for results.")
        st.rerun()


def render_analysis_tab():
    """Render risk analysis results."""
    st.markdown("## 📊 Risk Analysis")
    
    if not st.session_state.analysis_result:
        st.info("📤 Upload a contract first to see analysis")
        return
    
    result = st.session_state.analysis_result
    
    # Score display
    col1, col2, col3, col4 = st.columns(4)
    
    score = result.get('overall_score', 0)
    risk_level = result.get('risk_level', 'unknown')
    stats = result.get('statistics', {})
    
    with col1:
        score_color = '#dc2626' if score >= 70 else '#f59e0b' if score >= 40 else '#10b981'
        st.markdown(f"""
        <div style="background: {score_color}; color: white; padding: 2rem; border-radius: 1rem; text-align: center;">
            <h1 style="margin: 0; font-size: 3rem;">{score}</h1>
            <p style="margin: 0;">Risk Score / 100</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.metric("Total Risks", stats.get('total_risks', 0))
    with col3:
        st.metric("Critical/High", f"{stats.get('critical_risks', 0)}/{stats.get('high_risks', 0)}")
    with col4:
        st.metric("Medium/Low", f"{stats.get('medium_risks', 0)}/{stats.get('low_risks', 0)}")
    
    # Summary
    st.divider()
    summary = result.get('summary', {})
    if summary:
        st.markdown("### 📋 Assessment")
        st.info(summary.get('assessment', ''))
        st.warning(f"**Recommended Action:** {summary.get('recommended_action', '')}")
    
    # Findings
    st.divider()
    st.markdown("### ⚠️ Risk Findings")
    
    findings = result.get('findings', [])
    if findings:
        for finding in findings:
            level = finding.get('level', 'low')
            css_class = f"risk-{level}"
            st.markdown(f"""
            <div class="{css_class}">
                <strong>{finding.get('category', 'Unknown')}</strong> [{level.upper()}]<br>
                {finding.get('description', '')}<br>
                <em>💡 {finding.get('recommendation', '')}</em>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No significant risks found!")


def render_insights_tab():
    """Render NLP and AI insights."""
    st.markdown("## 🧠 AI Insights")
    
    if not st.session_state.nlp_result:
        st.info("📤 Upload a contract first")
        return
    
    nlp = st.session_state.nlp_result
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Dates
        st.markdown("### 📅 Key Dates")
        dates = nlp.get('dates', [])
        if dates:
            for d in dates[:5]:
                st.markdown(f"- **{d.get('type', 'Date').replace('_', ' ').title()}**: {d.get('value', '')}")
        else:
            st.info("No dates found")
        
        # Monetary Values
        st.markdown("### 💰 Financial Terms")
        values = nlp.get('monetary_values', [])
        if values:
            for v in values[:5]:
                st.markdown(f"- {v.get('currency', '')} {v.get('amount', 0):,.2f}")
        else:
            st.info("No monetary values found")
    
    with col2:
        # Statistics
        st.markdown("### 📊 Document Stats")
        stats = nlp.get('statistics', {})
        st.metric("Words", stats.get('word_count', 0))
        st.metric("Sentences", stats.get('sentence_count', 0))
        
        # Language
        lang = nlp.get('language_detection', {})
        st.markdown(f"**Language**: {lang.get('primary', 'English')}")
    
    # AI Analysis
    if st.session_state.ai_result:
        st.divider()
        st.markdown("### 🤖 AI Analysis")
        ai = st.session_state.ai_result
        
        if ai.get('status') != 'ai_unavailable':
            if ai.get('summary'):
                st.markdown("**Summary:**")
                st.write(ai.get('summary', ''))
            
            if ai.get('risks'):
                st.markdown("**AI-Identified Risks:**")
                for risk in ai.get('risks', [])[:5]:
                    st.warning(f"⚠️ {risk.get('issue', '')}: {risk.get('explanation', '')}")
            
            if ai.get('recommendations'):
                st.markdown("**Recommendations:**")
                for rec in ai.get('recommendations', [])[:5]:
                    st.success(f"💡 {rec}")
        else:
            st.info("Configure API key in sidebar for AI insights")


def render_templates_tab():
    """Render contract templates."""
    st.markdown("## 📝 Contract Templates")
    
    # Load templates
    try:
        with open('prompts/templates.json', 'r') as f:
            templates_data = json.load(f)
            templates = templates_data.get('templates', {})
    except:
        st.error("Could not load templates")
        return
    
    template_names = list(templates.keys())
    selected = st.selectbox(
        "Choose a template",
        template_names,
        format_func=lambda x: templates[x].get('name', x)
    )
    
    if selected:
        template = templates[selected]
        
        st.markdown(f"### {template.get('name', '')}")
        st.write(template.get('description', ''))
        
        st.markdown("**Suitable for:**")
        for item in template.get('suitable_for', []):
            st.markdown(f"- {item}")
        
        st.divider()
        st.markdown("### Template Content")
        st.text_area(
            "Contract Template",
            value=template.get('content', ''),
            height=400
        )
        
        st.download_button(
            "📥 Download Template",
            template.get('content', ''),
            file_name=f"{selected}_template.txt",
            mime="text/plain"
        )


def render_export_tab():
    """Render export options."""
    st.markdown("## 📥 Export Report")
    
    if not st.session_state.analysis_result:
        st.info("📤 Upload and analyze a contract first")
        return
    
    generator = ReportGenerator()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📄 Text Report")
        text_report = generator.generate_text_report(st.session_state.analysis_result)
        st.download_button(
            "📥 Download Text Report",
            text_report,
            file_name=f"contract_analysis_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        with st.expander("Preview Text Report"):
            st.text(text_report[:2000])
    
    with col2:
        st.markdown("### 🌐 HTML Report")
        html_report = generator.generate_html_report(st.session_state.analysis_result)
        st.download_button(
            "📥 Download HTML Report",
            html_report,
            file_name=f"contract_analysis_{datetime.now().strftime('%Y%m%d')}.html",
            mime="text/html",
            use_container_width=True
        )
    
    st.divider()
    
    # PDF (if available)
    st.markdown("### 📑 PDF Report")
    try:
        pdf_bytes = generator.generate_pdf(st.session_state.analysis_result)
        st.download_button(
            "📥 Download PDF Report",
            pdf_bytes,
            file_name=f"contract_analysis_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except ImportError:
        st.warning("Install reportlab for PDF export: `pip install reportlab`")
    except Exception as e:
        st.error(f"PDF generation error: {e}")


def main():
    """Main application entry point."""
    init_session_state()
    render_sidebar()
    
    # Header
    st.markdown('<h1 class="main-header">⚖️ GenAI Legal Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">AI-Powered Contract Analysis for Indian SMEs</p>', unsafe_allow_html=True)
    
    # Main tabs
    tabs = st.tabs(["📤 Upload", "📊 Analysis", "🧠 Insights", "📝 Templates", "📥 Export"])
    
    with tabs[0]:
        render_upload_tab()
    
    with tabs[1]:
        render_analysis_tab()
    
    with tabs[2]:
        render_insights_tab()
    
    with tabs[3]:
        render_templates_tab()
    
    with tabs[4]:
        render_export_tab()
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #888; padding: 1rem;">
        <p>⚖️ GenAI Legal Assistant | Built for Indian SMEs | GUVI Hackathon 2026</p>
        <p>⚠️ This tool provides guidance only. Consult a legal professional for important decisions.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
