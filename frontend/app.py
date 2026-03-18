"""
AI Chatbot Pro v3 - Advanced Frontend with 3D Effects
Features:
- ChatGPT-like interface
- Web Search integration
- AI Insights engine
- Document upload & Q&A
- 3D effects & animations
- Real-time responses
"""

import streamlit as st
import requests
import json
from datetime import datetime
import time
from typing import Dict, List

# ============================================================================
# Configuration
# ============================================================================

st.set_page_config(
    page_title="🤖 AI Chatbot Pro v3",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://localhost:8000"

# ============================================================================
# Advanced CSS with 3D Effects
# ============================================================================

st.markdown("""
<style>
/* Revolutionary 3D Design System */
:root {
    --primary: #667eea;
    --secondary: #764ba2;
    --accent: #f093fb;
    --dark: #0f0c29;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* Main Background - Deep 3D Gradient */
.main {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    min-height: 100vh;
    perspective: 1200px;
}

/* Header with 3D Transform */
.header-3d {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 40px;
    border-radius: 20px;
    color: white;
    text-align: center;
    margin-bottom: 30px;
    box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
    transform: perspective(1000px) rotateX(0deg);
    animation: float 6s ease-in-out infinite;
    position: relative;
    overflow: hidden;
}

.header-3d::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at 30% 50%, rgba(255,255,255,0.1), transparent);
    border-radius: 20px;
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-15px); }
}

.header-title {
    font-size: 3em;
    font-weight: 900;
    margin-bottom: 10px;
    background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 0 4px 15px rgba(0,0,0,0.2);
    z-index: 1;
    position: relative;
}

.header-subtitle {
    font-size: 1.2em;
    opacity: 0.95;
    z-index: 1;
    position: relative;
}

/* 3D Cards */
.card-3d {
    background: white;
    border-radius: 15px;
    padding: 25px;
    margin: 15px 0;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    border: 2px solid rgba(102, 126, 234, 0.1);
    transform: perspective(1000px) rotateY(0deg);
    transition: all 0.5s cubic-bezier(0.23, 1, 0.320, 1);
    position: relative;
}

.card-3d:hover {
    transform: perspective(1000px) rotateY(-5deg) rotateX(2deg) translateY(-5px);
    box-shadow: 0 20px 50px rgba(102, 126, 234, 0.3);
    border-left: 5px solid #667eea;
}

.card-3d::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(240, 147, 251, 0.05));
    border-radius: 15px;
    z-index: -1;
}

/* Chat Messages - 3D Depth */
.chat-message {
    margin: 15px 0;
    animation: slideIn 0.4s ease-out;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(-20px) perspective(500px) rotateY(45deg);
    }
    to {
        opacity: 1;
        transform: translateX(0) perspective(500px) rotateY(0deg);
    }
}

.user-message {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 15px 20px;
    border-radius: 15px;
    margin-left: 50px;
    text-align: right;
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    transform: perspective(1000px) rotateZ(-1deg);
}

.bot-message {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    color: #333;
    padding: 15px 20px;
    border-radius: 15px;
    margin-right: 50px;
    text-align: left;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    transform: perspective(1000px) rotateZ(1deg);
    border-left: 4px solid #667eea;
}

.insight-message {
    background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
    color: white;
    padding: 15px 20px;
    border-radius: 15px;
    margin: 15px 25px;
    box-shadow: 0 5px 20px rgba(255, 216, 155, 0.4);
    border-left: 4px solid #ff9800;
}

.search-result {
    background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
    color: #1a5276;
    padding: 15px 20px;
    border-radius: 12px;
    margin: 10px 0;
    box-shadow: 0 5px 15px rgba(132, 250, 176, 0.3);
    transform: perspective(1000px) rotateX(-2deg);
    transition: all 0.3s cubic-bezier(0.23, 1, 0.320, 1);
}

.search-result:hover {
    transform: perspective(1000px) rotateX(2deg) translateY(-3px);
    box-shadow: 0 8px 25px rgba(132, 250, 176, 0.4);
}

/* 3D Buttons */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 30px !important;
    font-weight: bold !important;
    box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3) !important;
    transform: perspective(1000px) rotateZ(0deg) !important;
    transition: all 0.3s cubic-bezier(0.23, 1, 0.320, 1) !important;
    position: relative !important;
    overflow: hidden !important;
}

.stButton > button:hover {
    box-shadow: 0 15px 40px rgba(102, 126, 234, 0.5) !important;
    transform: perspective(1000px) translateY(-3px) !important;
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
}

.stButton > button:active {
    transform: perspective(1000px) translateY(-1px) !important;
}

.stButton > button::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.5);
    transform: translate(-50%, -50%);
    transition: width 0.6s, height 0.6s;
}

.stButton > button:active::after {
    width: 300px;
    height: 300px;
}

/* Tabs - 3D Effect */
.stTabs [data-baseweb="tab-list"] {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(240, 147, 251, 0.1) 100%);
    border-radius: 15px;
    padding: 10px;
    gap: 5px;
}

.stTabs [data-baseweb="tab"] {
    background: white;
    border-radius: 10px;
    color: #667eea !important;
    font-weight: bold;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    transform: perspective(1000px) rotateY(0deg);
    transition: all 0.3s cubic-bezier(0.23, 1, 0.320, 1);
}

.stTabs [data-baseweb="tab"]:hover {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white !important;
    transform: perspective(1000px) rotateY(-5deg) translateY(-2px);
    box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
}

/* Status Badges - 3D */
.status-badge {
    display: inline-block;
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: bold;
    font-size: 0.9em;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    transform: perspective(1000px) rotateX(0deg);
    margin: 5px;
}

.status-online {
    background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
    color: #1a5276;
}

.status-demo {
    background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
    color: white;
}

.status-error {
    background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    color: white;
}

/* Input Fields - 3D */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: white !important;
    border: 2px solid #667eea !important;
    border-radius: 10px !important;
    padding: 12px 15px !important;
    font-size: 1em !important;
    transform: perspective(1000px) rotateX(0deg) !important;
    transition: all 0.3s cubic-bezier(0.23, 1, 0.320, 1) !important;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05) !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #764ba2 !important;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3) !important;
    transform: perspective(1000px) translateY(-2px) !important;
}

/* File Upload - 3D */
.stFileUploadDropzone {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(240, 147, 251, 0.1) 100%) !important;
    border: 2px dashed #667eea !important;
    border-radius: 15px !important;
    padding: 30px !important;
    transform: perspective(1000px) rotateY(0deg) !important;
    transition: all 0.3s cubic-bezier(0.23, 1, 0.320, 1) !important;
}

.stFileUploadDropzone:hover {
    border-color: #764ba2 !important;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(240, 147, 251, 0.15) 100%) !important;
    transform: perspective(1000px) rotateY(-3deg) translateY(-5px) !important;
    box-shadow: 0 15px 40px rgba(102, 126, 234, 0.2) !important;
}

/* Sidebar - 3D */
.stSidebar {
    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
}

.stSidebar .stMarkdown {
    color: white !important;
}

/* Metrics - 3D */
.metric-card {
    background: white;
    border-radius: 15px;
    padding: 20px;
    margin: 10px 0;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    text-align: center;
    transform: perspective(1000px) rotateY(0deg);
    transition: all 0.3s cubic-bezier(0.23, 1, 0.320, 1);
}

.metric-card:hover {
    transform: perspective(1000px) rotateY(-8deg) translateY(-5px);
    box-shadow: 0 20px 50px rgba(102, 126, 234, 0.3);
}

.metric-number {
    font-size: 2.5em;
    font-weight: 900;
    color: #667eea;
    margin: 10px 0;
}

.metric-label {
    font-size: 1em;
    color: #666;
    font-weight: bold;
}

/* Animations */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.loading {
    animation: pulse 1.5s ease-in-out infinite;
}

/* Responsive */
@media (max-width: 768px) {
    .header-title { font-size: 2em; }
    .user-message { margin-left: 20px; }
    .bot-message { margin-right: 20px; }
}

</style>
""", unsafe_allow_html=True)

# ============================================================================
# Session State Management
# ============================================================================

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'documents' not in st.session_state:
    st.session_state.documents = []

if 'search_results' not in st.session_state:
    st.session_state.search_results = []

if 'insights' not in st.session_state:
    st.session_state.insights = []

if 'total_queries' not in st.session_state:
    st.session_state.total_queries = 0


# ============================================================================
# Utility Functions
# ============================================================================

def safe_api_call(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Safely call API with error handling"""
    try:
        url = f"{API_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code}"}
    
    except Exception as e:
        return {"error": f"Connection Error: {str(e)[:50]}"}


def display_3d_card(title: str, content: str, card_type: str = "default"):
    """Display 3D styled card"""
    if card_type == "insight":
        st.markdown(f'<div class="insight-message"><b>{title}</b><br>{content}</div>', 
                   unsafe_allow_html=True)
    elif card_type == "search":
        st.markdown(f'<div class="search-result"><b>{title}</b><br>{content}</div>', 
                   unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="card-3d"><b>{title}</b><br>{content}</div>', 
                   unsafe_allow_html=True)


def format_response(response: Dict) -> str:
    """Format API response for display"""
    if "error" in response:
        return f"❌ Error: {response['error']}"
    
    text = response.get("answer", response.get("text", "No response"))
    return text


# ============================================================================
# Header
# ============================================================================

st.markdown("""
<div class="header-3d">
    <div class="header-title">🤖 AI Chatbot Pro v3</div>
    <div class="header-subtitle">Advanced AI with Web Search, Insights & Document Q&A</div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# Main Content - Tabs
# ============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Chat",
    "🔍 Web Search",
    "💡 AI Insights",
    "📄 Document Q&A",
    "ℹ️ About"
])


# ============================================================================
# Tab 1: Chat
# ============================================================================

with tab1:
    st.markdown("### 💬 Advanced Chat Interface")
    
    col1, col2 = st.columns([0.85, 0.15])
    
    with col1:
        user_input = st.text_input(
            "Ask me anything...",
            placeholder="Type your question here...",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("📤 Send", use_container_width=True)
    
    # Enable web search and insights options
    col_a, col_b = st.columns(2)
    with col_a:
        use_web_search = st.checkbox("🔍 Include Web Search", value=True)
    with col_b:
        use_insights = st.checkbox("💡 Include AI Insights", value=False)
    
    if send_button and user_input:
        with st.spinner("Thinking..."):
            st.session_state.total_queries += 1
            
            # Call API
            response = safe_api_call(
                "/chat",
                "POST",
                {
                    "question": user_input,
                    "use_web_search": use_web_search,
                    "use_insights": use_insights
                }
            )
            
            if "error" not in response:
                # Display main answer
                st.markdown(f"""
                <div class="bot-message">
                    <b>AI Response ({response.get('model', 'AI')})</b><br>
                    {response.get('answer', 'No response')}
                </div>
                """, unsafe_allow_html=True)
                
                # Display web search results if available
                if "web_search" in response and response["web_search"]:
                    st.markdown("### 🔍 Web Search Results")
                    for idx, result in enumerate(response["web_search"][:3], 1):
                        st.markdown(f"""
                        <div class="search-result">
                            <b>{idx}. {result.get('title', 'Result')}</b><br>
                            {result.get('snippet', '')}
                        </div>
                        """, unsafe_allow_html=True)
                
                # Display insights if available
                if "insights" in response and response["insights"]:
                    st.markdown("### 💡 AI Insights")
                    st.markdown(f"""
                    <div class="insight-message">
                        {response["insights"]}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Store in history
                st.session_state.chat_history.append({
                    "user": user_input,
                    "bot": format_response(response),
                    "timestamp": datetime.now().isoformat()
                })
            else:
                st.error(response["error"])
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### 📜 Chat History")
        for msg in st.session_state.chat_history[-5:]:  # Show last 5
            st.markdown(f'<div class="user-message">👤 {msg["user"]}</div>', 
                       unsafe_allow_html=True)
            st.markdown(f'<div class="bot-message">🤖 {msg["bot"][:200]}...</div>', 
                       unsafe_allow_html=True)


# ============================================================================
# Tab 2: Web Search
# ============================================================================

with tab2:
    st.markdown("### 🔍 Real-Time Web Search")
    
    search_query = st.text_input(
        "Search the web...",
        placeholder="Enter search query...",
        label_visibility="collapsed"
    )
    
    num_results = st.slider("Number of results:", 1, 10, 5)
    
    if search_query:
        with st.spinner("Searching..."):
            response = safe_api_call(
                "/search",
                "POST",
                {"query": search_query, "num_results": num_results}
            )
            
            if "error" not in response:
                st.markdown(f"**Found {len(response.get('results', []))} results for: {search_query}**")
                
                for idx, result in enumerate(response.get('results', []), 1):
                    st.markdown(f"""
                    <div class="search-result">
                        <b>{idx}. {result.get('title', 'Result')}</b><br>
                        <small>{result.get('url', '')}</small><br>
                        {result.get('snippet', '')}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error(response["error"])


# ============================================================================
# Tab 3: AI Insights
# ============================================================================

with tab3:
    st.markdown("### 💡 AI Insights Engine (UNIQUE FEATURE)")
    st.info("Generate deep AI-powered insights on any topic - not available in other AI agents!")
    
    topic = st.text_input(
        "Topic for analysis...",
        placeholder="What topic would you like insights on?",
        label_visibility="collapsed"
    )
    
    depth = st.select_slider("Analysis Depth:", options=["light", "medium", "deep"], value="medium")
    
    if topic and st.button("🔍 Generate Insights"):
        with st.spinner("Analyzing..."):
            response = safe_api_call(
                "/insights",
                "POST",
                {"topic": topic, "depth": depth}
            )
            
            if "error" not in response:
                st.markdown(f"""
                <div class="insight-message">
                    <h4>📊 {response.get('topic', 'Insights')}</h4>
                    <small>Depth: {response.get('depth', 'medium').upper()} | Model: {response.get('model', 'AI')}</small><br><br>
                    {response.get('insight', 'No insights generated')}
                </div>
                """, unsafe_allow_html=True)
                
                st.session_state.insights.append({
                    "topic": topic,
                    "insight": response.get("insight", ""),
                    "timestamp": datetime.now().isoformat()
                })
            else:
                st.error(response["error"])


# ============================================================================
# Tab 4: Document Q&A
# ============================================================================

with tab4:
    st.markdown("### 📄 Document Upload & Q&A")
    st.info("Upload documents and ask questions about their content!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Upload Document**")
        uploaded_file = st.file_uploader(
            "Choose a file (PDF, TXT, MD, DOCX)",
            type=["pdf", "txt", "md", "docx"],
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            with st.spinner("Processing document..."):
                files = {"file": uploaded_file}
                try:
                    response = requests.post(
                        f"{API_URL}/upload-document",
                        files=files,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        doc_data = response.json()
                        st.success(f"✅ Uploaded: {uploaded_file.name}")
                        st.markdown(f"**Preview:** {doc_data.get('preview', '')[:200]}...")
                        
                        st.session_state.documents.append({
                            "name": uploaded_file.name,
                            "content": doc_data.get("content", ""),
                            "type": doc_data.get("type", "document")
                        })
                    else:
                        st.error("Failed to process document")
                except Exception as e:
                    st.error(f"Upload error: {str(e)[:50]}")
    
    with col2:
        st.markdown("**Uploaded Documents**")
        if st.session_state.documents:
            for doc in st.session_state.documents:
                st.markdown(f"📄 {doc['name']}")
    
    # Q&A section
    st.markdown("---")
    st.markdown("**Ask Questions About Documents**")
    
    if st.session_state.documents:
        doc_question = st.text_area(
            "Your question...",
            placeholder="Ask anything about your documents...",
            label_visibility="collapsed"
        )
        
        if st.button("❓ Get Answer") and doc_question:
            with st.spinner("Finding answer..."):
                response = safe_api_call(
                    "/document-qa",
                    "POST",
                    {
                        "question": doc_question,
                        "document_content": st.session_state.documents[0]["content"],
                        "document_name": st.session_state.documents[0]["name"]
                    }
                )
                
                if "error" not in response:
                    st.markdown(f"""
                    <div class="bot-message">
                        <b>Answer (from {response.get('document', 'document')})</b><br>
                        {response.get('answer', 'No answer found')}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(response["error"])
    else:
        st.warning("📁 Please upload a document first")


# ============================================================================
# Tab 5: About & System Info
# ============================================================================

with tab5:
    st.markdown("### ℹ️ About AI Chatbot Pro v3")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{st.session_state.total_queries}</div>
            <div class="metric-label">Total Queries</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{len(st.session_state.documents)}</div>
            <div class="metric-label">Documents</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{len(st.session_state.chat_history)}</div>
            <div class="metric-label">Messages</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 🌟 Advanced Features")
    st.markdown("""
    ✅ **Web Search** - Real-time internet search results
    ✅ **AI Insights** - Deep analysis on any topic (UNIQUE!)
    ✅ **Document Q&A** - Ask questions about uploaded files
    ✅ **Dual AI** - OpenAI + Gemini with fallback
    ✅ **3D Effects** - Modern, immersive 3D UI
    ✅ **ChatGPT-like** - Familiar, intuitive interface
    ✅ **Real-time** - Live responses and updates
    """)
    
    st.markdown("---")
    
    st.markdown("### 🤖 AI Models")
    
    health = safe_api_call("/health")
    
    if "error" not in health:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="card-3d">
                <b>Primary AI:</b> OpenAI GPT-3.5-turbo<br>
                <small>Latest language model for chat</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="card-3d">
                <b>Fallback AI:</b> Google Gemini 2.0 Flash<br>
                <small>Advanced multimodal reasoning</small>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 📊 System Status")
    
    if "error" not in health:
        st.markdown(f"""
        <span class="status-badge status-online">
            ✅ {health.get('service', 'Service')} Online
        </span>
        """, unsafe_allow_html=True)
        st.caption(f"Version: {health.get('version', '3.0.0')}")
    else:
        st.markdown(f"""
        <span class="status-badge status-error">
            ❌ Service Offline
        </span>
        """, unsafe_allow_html=True)


# ============================================================================
# Sidebar
# ============================================================================

with st.sidebar:
    st.markdown("### ⚙️ System Controls")
    
    if st.button("🔄 Refresh All", use_container_width=True):
        st.rerun()
    
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.documents = []
        st.session_state.search_results = []
        st.session_state.insights = []
        st.session_state.total_queries = 0
        st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 📈 Statistics")
    st.markdown(f"**Total Queries:** {st.session_state.total_queries}")
    st.markdown(f"**Documents:** {len(st.session_state.documents)}")
    st.markdown(f"**Chat Messages:** {len(st.session_state.chat_history)}")
    
    st.markdown("---")
    
    st.markdown("### 💡 Tips")
    st.markdown("""
    • Use Web Search for latest info
    • Try Insights for deep analysis
    • Upload PDFs for Q&A
    • Check About tab for features
    """)
    
    st.markdown("---")
    
    st.markdown("""
    <div style="text-align: center; padding: 20px; color: white;">
        <small>AI Chatbot Pro v3 | Made with ❤️</small>
    </div>
    """, unsafe_allow_html=True)
