import streamlit as st
import requests
from dotenv import load_dotenv
import time
from datetime import datetime
import threading

load_dotenv()

# Page config
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with 3D effects and advanced design
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* Main background with gradient animation */
    .main {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        min-height: 100vh;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Uniform card sizing */
    .card-uniform {
        min-height: 180px;
        max-height: 200px;
        aspect-ratio: 1 / 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    /* Status indicator */
    .status-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9em;
        animation: pulse-badge 2s ease-in-out infinite;
    }
    
    .status-online {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: #2d5016;
        box-shadow: 0 0 20px rgba(132, 250, 176, 0.5);
    }
    
    .status-offline {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: #7d2e1f;
        box-shadow: 0 0 20px rgba(250, 112, 154, 0.5);
    }
    
    @keyframes pulse-badge {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Status card */
    .status-card {
        background: white;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .status-card:hover {
        transform: translateX(5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    }
    
    .status-card-online {
        border-left-color: #84fab0;
    }
    
    .status-card-offline {
        border-left-color: #fa709a;
    }
    
    /* Header styling */
    .header-container {
        perspective: 1000px;
        margin-bottom: 30px;
    }
    
    .header-3d {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px 30px;
        border-radius: 20px;
        color: white;
        text-align: center;
        box-shadow: 
            0 20px 40px rgba(102, 126, 234, 0.3),
            0 0 60px rgba(102, 126, 234, 0.2);
        position: relative;
        overflow: hidden;
        transform: rotateX(5deg) rotateZ(0.5deg);
        transition: all 0.3s ease;
    }
    
    .header-3d:hover {
        transform: rotateX(8deg) rotateZ(1deg);
        box-shadow: 
            0 30px 60px rgba(102, 126, 234, 0.4),
            0 0 80px rgba(102, 126, 234, 0.3);
    }
    
    .header-3d::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        animation: shine 3s infinite;
    }
    
    @keyframes shine {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .header-title {
        font-size: 2.5em;
        font-weight: 900;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        letter-spacing: 1px;
    }
    
    .header-subtitle {
        font-size: 1.1em;
        opacity: 0.95;
        letter-spacing: 0.5px;
    }
    
    /* 3D Stat boxes with uniform sizing */
    .stat-box-3d {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin: 10px 0;
        position: relative;
        transform: perspective(1000px) rotateX(-10deg) rotateY(5deg);
        transition: all 0.5s cubic-bezier(0.23, 1, 0.320, 1);
        box-shadow: 
            0 20px 40px rgba(102, 126, 234, 0.3),
            inset -2px -2px 5px rgba(0, 0, 0, 0.2),
            inset 2px 2px 5px rgba(255, 255, 255, 0.1);
        overflow: hidden;
        min-height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .stat-box-3d::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translate(-20%, -20%) rotate(0deg); }
        100% { transform: translate(20%, 20%) rotate(360deg); }
    }
    
    .stat-box-3d:hover {
        transform: perspective(1000px) rotateX(-15deg) rotateY(8deg) scale(1.05);
        box-shadow: 
            0 30px 60px rgba(102, 126, 234, 0.4),
            0 0 40px rgba(102, 126, 234, 0.2),
            inset -2px -2px 5px rgba(0, 0, 0, 0.2),
            inset 2px 2px 5px rgba(255, 255, 255, 0.1);
    }
    
    .stat-number {
        font-size: 2.2em;
        font-weight: 900;
        margin: 5px 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    /* Document upload card */
    .upload-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.1);
        border: 2px dashed #667eea;
        transition: all 0.3s ease;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .upload-card:hover {
        border-color: #764ba2;
        box-shadow: 0 20px 50px rgba(102, 126, 234, 0.2);
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
    }
    
    /* Document item */
    .doc-item {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 15px;
        border-radius: 10px;
        margin: 8px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .doc-item:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .doc-status-verified {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 8px 12px;
        border-radius: 8px;
        font-weight: bold;
        color: #2d5016;
        font-size: 0.85em;
    }
    
    .doc-status-pending {
        background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
        padding: 8px 12px;
        border-radius: 8px;
        font-weight: bold;
        color: white;
        font-size: 0.85em;
    }
    
    /* Message styling with 3D depth */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 16px 20px;
        border-radius: 20px;
        margin: 12px 0;
        border-bottom-left-radius: 5px;
        display: block;
        text-align: right;
        box-shadow: 
            0 10px 25px rgba(102, 126, 234, 0.3),
            0 0 20px rgba(102, 126, 234, 0.1),
            inset -1px -1px 0 rgba(0, 0, 0, 0.1);
        animation: slideInRight 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        word-wrap: break-word;
        transform: perspective(1000px) rotateY(-5deg);
        transition: all 0.3s ease;
        max-width: 80%;
        margin-left: auto;
    }
    
    .user-message:hover {
        transform: perspective(1000px) rotateY(-8deg) scale(1.02);
        box-shadow: 
            0 15px 40px rgba(102, 126, 234, 0.4),
            0 0 30px rgba(102, 126, 234, 0.2),
            inset -1px -1px 0 rgba(0, 0, 0, 0.1);
    }
    
    .bot-message {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        color: #333;
        padding: 16px 20px;
        border-radius: 20px;
        margin: 12px 0;
        border-bottom-right-radius: 5px;
        display: block;
        text-align: left;
        box-shadow: 
            0 10px 25px rgba(0, 0, 0, 0.1),
            0 0 20px rgba(0, 0, 0, 0.05),
            inset 1px 1px 0 rgba(255, 255, 255, 0.3);
        animation: slideInLeft 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        word-wrap: break-word;
        transform: perspective(1000px) rotateY(5deg);
        transition: all 0.3s ease;
        max-width: 80%;
    }
    
    .bot-message:hover {
        transform: perspective(1000px) rotateY(8deg) scale(1.02);
        box-shadow: 
            0 15px 40px rgba(0, 0, 0, 0.15),
            0 0 30px rgba(0, 0, 0, 0.08),
            inset 1px 1px 0 rgba(255, 255, 255, 0.3);
    }
    
    .gemini-message {
        background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
        color: white;
        padding: 16px 20px;
        border-radius: 20px;
        margin: 12px 0;
        border-bottom-right-radius: 5px;
        display: block;
        text-align: left;
        box-shadow: 
            0 10px 25px rgba(26, 188, 156, 0.3),
            0 0 20px rgba(26, 188, 156, 0.1),
            inset 1px 1px 0 rgba(255, 255, 255, 0.3);
        animation: slideInLeft 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        word-wrap: break-word;
        transform: perspective(1000px) rotateY(5deg);
        transition: all 0.3s ease;
        max-width: 80%;
    }
    
    .gemini-message:hover {
        transform: perspective(1000px) rotateY(8deg) scale(1.02);
        box-shadow: 
            0 15px 40px rgba(26, 188, 156, 0.4),
            0 0 30px rgba(26, 188, 156, 0.2),
            inset 1px 1px 0 rgba(255, 255, 255, 0.3);
    }
    
    .error-message {
        background: linear-gradient(135deg, #ffe0e0 0%, #ffcccc 100%);
        color: #c41e14;
        padding: 16px 20px;
        border-radius: 15px;
        border-left: 5px solid #c41e14;
        margin: 12px 0;
        box-shadow: 
            0 10px 25px rgba(196, 30, 20, 0.2),
            0 0 20px rgba(196, 30, 20, 0.1);
        animation: shake 0.5s ease-in-out;
        transform: perspective(1000px) rotateZ(-1deg);
    }
    
    @keyframes shake {
        0%, 100% { transform: perspective(1000px) rotateZ(-1deg) translateX(0); }
        25% { transform: perspective(1000px) rotateZ(-1deg) translateX(-5px); }
        75% { transform: perspective(1000px) rotateZ(-1deg) translateX(5px); }
    }
    
    /* Info cards with 3D flip effect */
    .info-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 
            0 15px 40px rgba(0, 0, 0, 0.1),
            0 0 1px rgba(0, 0, 0, 0.1);
        position: relative;
        transform: perspective(1000px) rotateX(-5deg);
        transition: all 0.5s cubic-bezier(0.23, 1, 0.320, 1);
        overflow: hidden;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .info-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0) 0%, rgba(102, 126, 234, 0.1) 100%);
        transform: translateX(-100%);
        transition: transform 0.5s ease;
    }
    
    .info-card:hover {
        transform: perspective(1000px) rotateX(5deg) scale(1.05);
        box-shadow: 
            0 25px 60px rgba(0, 0, 0, 0.15),
            0 0 40px rgba(102, 126, 234, 0.1);
    }
    
    .info-card:hover::before {
        transform: translateX(0);
    }
    
    .info-card h4 {
        color: #667eea;
        margin-bottom: 10px;
        font-size: 1.2em;
    }
    
    /* Feature list */
    .feature-item {
        padding: 12px;
        margin: 8px 0;
        border-left: 4px solid #667eea;
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.05) 0%, transparent 100%);
        border-radius: 5px;
        transition: all 0.3s ease;
        transform: translateX(0);
    }
    
    .feature-item:hover {
        transform: translateX(10px);
        border-left-color: #764ba2;
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.1) 0%, transparent 100%);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 35px !important;
        font-weight: bold !important;
        font-size: 1em !important;
        box-shadow: 
            0 10px 30px rgba(102, 126, 234, 0.4),
            0 0 20px rgba(102, 126, 234, 0.2) !important;
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        position: relative;
        overflow: hidden !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton>button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton>button:hover {
        transform: translateY(-5px) scale(1.05) !important;
        box-shadow: 
            0 20px 50px rgba(102, 126, 234, 0.6),
            0 0 40px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Text input */
    .stTextInput>div>div>input {
        border-radius: 12px !important;
        border: 2px solid #e0e0e0 !important;
        padding: 14px 18px !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        background: white !important;
        color: #333 !important;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #667eea !important;
        box-shadow: 
            0 0 0 4px rgba(102, 126, 234, 0.1),
            0 5px 20px rgba(102, 126, 234, 0.2) !important;
        transform: scale(1.02);
    }
    
    /* File uploader styling */
    .stFileUploader {
        border-radius: 15px !important;
    }
    
    /* Success/Error alerts */
    .stSuccess {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%) !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 30px rgba(132, 250, 176, 0.3) !important;
        animation: popIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    
    .stError {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%) !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 30px rgba(250, 112, 154, 0.3) !important;
        animation: shake 0.5s ease-in-out;
    }
    
    @keyframes popIn {
        0% { transform: scale(0.8) opacity(0); }
        100% { transform: scale(1) opacity(1); }
    }
    
    /* Animations */
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: perspective(1000px) translateX(50px) rotateY(20deg);
        }
        to {
            opacity: 1;
            transform: perspective(1000px) translateX(0) rotateY(-5deg);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: perspective(1000px) translateX(-50px) rotateY(-20deg);
        }
        to {
            opacity: 1;
            transform: perspective(1000px) translateX(0) rotateY(5deg);
        }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .user-message, .bot-message {
            max-width: 95%;
        }
        
        .header-title {
            font-size: 1.8em;
        }
        
        .stat-box-3d {
            transform: perspective(1000px) rotateX(-5deg) rotateY(0deg);
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "gemini_messages" not in st.session_state:
    st.session_state.gemini_messages = []

if "uploaded_documents" not in st.session_state:
    st.session_state.uploaded_documents = []

if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0

if "backend_status" not in st.session_state:
    st.session_state.backend_status = False

if "endee_status" not in st.session_state:
    st.session_state.endee_status = False

# Health check functions
def check_backend_status():
    """Check if backend is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        return response.status_code == 200, True
    except:
        return False, False

def check_endee_status():
    """Check if vector database is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code == 200:
            data = response.json()
            return data.get("endee_connected", False), True
        return False, False
    except:
        return False, False

def verify_document(filename):
    """Verify document is valid"""
    valid_extensions = ('.pdf', '.txt', '.md', '.doc', '.docx')
    return filename.lower().endswith(valid_extensions)

# Sidebar with enhanced design
with st.sidebar:
    st.markdown("### 🤖 AI Assistant Control Panel")
    st.markdown("---")
    
    # Live Status Section
    st.markdown("### 🔴 System Status")
    
    backend_status, backend_accessible = check_backend_status()
    status_text = "🟢 Online" if backend_status else "🔴 Offline"
    status_class = "status-online" if backend_status else "status-offline"
    st.markdown(f"""
    <div class="status-card {'status-card-online' if backend_status else 'status-card-offline'}">
        <strong>Backend Server</strong><br>
        <span class="status-badge {status_class}">{status_text}</span><br>
        <small>http://localhost:8000</small>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.backend_status = backend_status
    
    endee_status, endee_accessible = check_endee_status()
    status_text_endee = "🟢 Connected" if endee_status else "🔴 Disconnected"
    status_class_endee = "status-online" if endee_status else "status-offline"
    st.markdown(f"""
    <div class="status-card {'status-card-online' if endee_status else 'status-card-offline'}">
        <strong>Vector Database</strong><br>
        <span class="status-badge {status_class_endee}">{status_text_endee}</span><br>
        <small>Endee @ localhost:9000</small>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.endee_status = endee_status
    
    st.markdown("---")
    
    # Stats with 3D effect
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stat-box-3d">
            <h3 style="margin: 0; font-size: 0.85em;">📊 Queries</h3>
            <div class="stat-number">{st.session_state.total_queries}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-box-3d">
            <h3 style="margin: 0; font-size: 0.85em;">📄 Docs</h3>
            <div class="stat-number">{len(st.session_state.uploaded_documents)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Features
    st.markdown("### ✨ Features")
    features = [
        ("🚀", "OpenAI (Primary)"),
        ("🌟", "Gemini (Specialized)"),
        ("📄", "Doc Upload"),
        ("⚡", "Real-time Response"),
        ("💾", "Message History"),
        ("🔒", "Secure & Private")
    ]
    for icon, feature in features:
        st.markdown(f"""
        <div class="feature-item">
            <strong>{icon} {feature}</strong>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧹 Clear All", use_container_width=True):
            st.session_state.messages = []
            st.session_state.gemini_messages = []
            st.session_state.uploaded_documents = []
            st.success("✅ Cleared!")
            st.rerun()
    
    with col2:
        if st.button("⟳ Refresh", use_container_width=True):
            st.rerun()

# Main header with 3D effect
st.markdown("""
<div class="header-container">
    <div class="header-3d">
        <div class="header-title">🚀 AI Chatbot Pro</div>
        <div class="header-subtitle">✨ Powered by OpenAI + Gemini | Document Management | 3D UI</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Status overview
col1, col2, col3, col4 = st.columns(4)
with col1:
    backend_emoji = "✅" if st.session_state.backend_status else "❌"
    st.markdown(f"### {backend_emoji} Backend")
    st.caption("Online" if st.session_state.backend_status else "Offline")

with col2:
    endee_emoji = "✅" if st.session_state.endee_status else "❌"
    st.markdown(f"### {endee_emoji} Vector DB")
    st.caption("Ready" if st.session_state.endee_status else "Unavailable")

with col3:
    st.markdown(f"### 📊 Queries")
    st.caption(f"{st.session_state.total_queries} Total")

with col4:
    st.markdown(f"### 📄 Documents")
    st.caption(f"{len(st.session_state.uploaded_documents)} Uploaded")

st.markdown("---")

# Tabs for different sections
tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "🌟 Gemini", "📄 Documents", "ℹ️ About"])

with tab1:
    st.markdown("### 💬 Hybrid Chat (OpenAI Primary → Gemini Fallback)")
    
    if not st.session_state.backend_status:
        st.warning("⚠️ Backend server is offline. Chat may not work.")
    
    if st.session_state.messages:
        st.markdown("**Conversation:**")
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div style="text-align: right;">
                    <div class="user-message">
                        <strong>👤 You:</strong> {message["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                if "error" in message.get("type", ""):
                    st.markdown(f"""
                    <div style="text-align: left;">
                        <div class="error-message">
                            <strong>⚠️ Error:</strong> {message["content"][:200]}...
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="text-align: left;">
                        <div class="bot-message">
                            <strong>🤖 {message.get('source', 'Unknown')}:</strong><br>
                            {message["content"]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input("Your message...", placeholder="Ask anything!", key="chat1")
    with col2:
        if st.button("📤", key="send1", use_container_width=True):
            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.session_state.total_queries += 1
                with st.spinner("🤖 Thinking..."):
                    try:
                        response = requests.post("http://localhost:8000/chat", json={"question": user_input}, timeout=30)
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": data.get("response", "No response"),
                                "source": data.get("source", "Unknown"),
                                "type": "normal" if data.get("source") != "Error" else "error"
                            })
                            st.success(f"✅ Got response from {data.get('source', 'Unknown')}")
                    except Exception as e:
                        st.session_state.messages.append({"role": "assistant", "content": str(e), "type": "error"})
                        st.error(f"Error: {str(e)[:100]}")
                    st.rerun()

with tab2:
    st.markdown("### 🌟 Gemini Specialized Chat")
    
    if st.session_state.gemini_messages:
        st.markdown("**Gemini Conversation:**")
        for message in st.session_state.gemini_messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div style="text-align: right;">
                    <div class="user-message">
                        <strong>👤 You:</strong> {message["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="text-align: left;">
                    <div class="gemini-message">
                        <strong>🌟 Gemini:</strong><br>
                        {message["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([5, 1])
    with col1:
        gemini_input = st.text_input("Ask Gemini...", placeholder="Creative tasks!", key="chat2")
    with col2:
        if st.button("📤", key="send2", use_container_width=True):
            if gemini_input:
                st.session_state.gemini_messages.append({"role": "user", "content": gemini_input})
                st.session_state.total_queries += 1
                with st.spinner("🌟 Gemini thinking..."):
                    try:
                        response = requests.post("http://localhost:8000/chat", json={"question": f"[GEMINI] {gemini_input}"}, timeout=30)
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.gemini_messages.append({
                                "role": "assistant",
                                "content": data.get("response", "No response")
                            })
                            st.success("✅ Gemini responded")
                    except Exception as e:
                        st.error(f"Error: {str(e)[:100]}")
                    st.rerun()

with tab3:
    st.markdown("### 📄 Document Management")
    
    st.markdown("#### 📁 Upload Documents")
    st.markdown("""
    <div class="upload-card">
        <p style="text-align: center; color: #667eea; font-size: 1.2em; font-weight: bold;">
            🗂️ Drop your documents here
        </p>
        <p style="text-align: center; color: #999; font-size: 0.9em;">
            Supported: PDF, TXT, MD, DOC, DOCX
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True, type=["pdf", "txt", "md", "doc", "docx"])
    
    if uploaded_files:
        for file in uploaded_files:
            if verify_document(file.name):
                doc_data = {
                    "name": file.name,
                    "size": f"{file.size / 1024:.2f}KB",
                    "status": "✅ Verified",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                if doc_data not in st.session_state.uploaded_documents:
                    st.session_state.uploaded_documents.append(doc_data)
                    st.success(f"✅ {file.name} uploaded successfully!")
    
    if st.session_state.uploaded_documents:
        st.markdown("#### 📋 Uploaded Documents")
        for doc in st.session_state.uploaded_documents:
            st.markdown(f"""
            <div class="doc-item">
                <div>
                    <strong>📄 {doc['name']}</strong><br>
                    <small>Size: {doc['size']} | {doc['timestamp']}</small>
                </div>
                <div class="doc-status-verified">{doc['status']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📁 No documents uploaded yet. Upload your first document!")

with tab4:
    st.markdown("### ℹ️ About This Application")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h4>🚀 Features</h4>
            <p>Dual AI engines, document management, real-time chat, 3D UI, live monitoring</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h4>🤖 AI Models</h4>
            <p>OpenAI GPT-4 Mini (primary) + Google Gemini (fallback/specialized)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-card">
            <h4>🔒 Security</h4>
            <p>Secure API calls, encrypted data, private conversations, enterprise-grade</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.info("""
    **📌 System Information:**
    - Backend: FastAPI + Uvicorn
    - Frontend: Streamlit
    - Database: Endee Vector DB
    - LLMs: OpenAI + Google Gemini
    - UI: Advanced 3D CSS + Animations
    
    **✨ Version:** 2.0 Pro
    **🏗️ Built with:** ❤️ Modern Tech Stack
    """)

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #999; padding: 20px;">
    <p><strong>AI Chatbot Pro v2.0</strong> | 2026 | Made with ✨</p>
</div>
""", unsafe_allow_html=True)

# Custom CSS with 3D effects and advanced design
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* Main background with gradient animation */
    .main {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        min-height: 100vh;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Glass morphism effect */
    .glass {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    
    /* Status indicator */
    .status-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9em;
        animation: pulse-badge 2s ease-in-out infinite;
    }
    
    .status-online {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: #2d5016;
        box-shadow: 0 0 20px rgba(132, 250, 176, 0.5);
    }
    
    .status-offline {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: #7d2e1f;
        box-shadow: 0 0 20px rgba(250, 112, 154, 0.5);
    }
    
    @keyframes pulse-badge {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Status card */
    .status-card {
        background: white;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .status-card:hover {
        transform: translateX(5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    }
    
    .status-card-online {
        border-left-color: #84fab0;
    }
    
    .status-card-offline {
        border-left-color: #fa709a;
    }
    
    /* Header styling */
    .header-container {
        perspective: 1000px;
        margin-bottom: 30px;
    }
    
    .header-3d {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px 30px;
        border-radius: 20px;
        color: white;
        text-align: center;
        box-shadow: 
            0 20px 40px rgba(102, 126, 234, 0.3),
            0 0 60px rgba(102, 126, 234, 0.2);
        position: relative;
        overflow: hidden;
        transform: rotateX(5deg) rotateZ(0.5deg);
        transition: all 0.3s ease;
    }
    
    .header-3d:hover {
        transform: rotateX(8deg) rotateZ(1deg);
        box-shadow: 
            0 30px 60px rgba(102, 126, 234, 0.4),
            0 0 80px rgba(102, 126, 234, 0.3);
    }
    
    .header-3d::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        animation: shine 3s infinite;
    }
    
    @keyframes shine {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .header-title {
        font-size: 2.5em;
        font-weight: 900;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        letter-spacing: 1px;
    }
    
    .header-subtitle {
        font-size: 1.1em;
        opacity: 0.95;
        letter-spacing: 0.5px;
    }
    
    /* 3D Stat boxes */
    .stat-box-3d {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin: 15px 0;
        position: relative;
        transform: perspective(1000px) rotateX(-10deg) rotateY(5deg);
        transition: all 0.5s cubic-bezier(0.23, 1, 0.320, 1);
        box-shadow: 
            0 20px 40px rgba(102, 126, 234, 0.3),
            inset -2px -2px 5px rgba(0, 0, 0, 0.2),
            inset 2px 2px 5px rgba(255, 255, 255, 0.1);
        overflow: hidden;
    }
    
    .stat-box-3d::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translate(-20%, -20%) rotate(0deg); }
        100% { transform: translate(20%, 20%) rotate(360deg); }
    }
    
    .stat-box-3d:hover {
        transform: perspective(1000px) rotateX(-15deg) rotateY(8deg) scale(1.05);
        box-shadow: 
            0 30px 60px rgba(102, 126, 234, 0.4),
            0 0 40px rgba(102, 126, 234, 0.2),
            inset -2px -2px 5px rgba(0, 0, 0, 0.2),
            inset 2px 2px 5px rgba(255, 255, 255, 0.1);
    }
    
    .stat-number {
        font-size: 2.5em;
        font-weight: 900;
        margin: 10px 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    /* Chat container */
    .chat-container {
        background: white;
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.15),
            0 0 1px rgba(0, 0, 0, 0.1);
        position: relative;
        transform: translateZ(0);
        transition: all 0.3s ease;
    }
    
    .chat-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
        border-radius: 20px 20px 0 0;
        animation: slideRight 3s infinite;
    }
    
    @keyframes slideRight {
        0% { transform: translateX(-100%); }
        50% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    
    /* Message styling with 3D depth */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 16px 20px;
        border-radius: 20px;
        margin: 12px 0;
        border-bottom-left-radius: 5px;
        display: inline-block;
        max-width: 85%;
        margin-left: auto;
        margin-right: 0;
        display: block;
        text-align: right;
        box-shadow: 
            0 10px 25px rgba(102, 126, 234, 0.3),
            0 0 20px rgba(102, 126, 234, 0.1),
            inset -1px -1px 0 rgba(0, 0, 0, 0.1);
        animation: slideInRight 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        word-wrap: break-word;
        transform: perspective(1000px) rotateY(-5deg);
        transition: all 0.3s ease;
    }
    
    .user-message:hover {
        transform: perspective(1000px) rotateY(-8deg) scale(1.02);
        box-shadow: 
            0 15px 40px rgba(102, 126, 234, 0.4),
            0 0 30px rgba(102, 126, 234, 0.2),
            inset -1px -1px 0 rgba(0, 0, 0, 0.1);
    }
    
    .bot-message {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        color: #333;
        padding: 16px 20px;
        border-radius: 20px;
        margin: 12px 0;
        border-bottom-right-radius: 5px;
        display: inline-block;
        max-width: 85%;
        margin-left: 0;
        box-shadow: 
            0 10px 25px rgba(0, 0, 0, 0.1),
            0 0 20px rgba(0, 0, 0, 0.05),
            inset 1px 1px 0 rgba(255, 255, 255, 0.3);
        animation: slideInLeft 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        word-wrap: break-word;
        transform: perspective(1000px) rotateY(5deg);
        transition: all 0.3s ease;
    }
    
    .bot-message:hover {
        transform: perspective(1000px) rotateY(8deg) scale(1.02);
        box-shadow: 
            0 15px 40px rgba(0, 0, 0, 0.15),
            0 0 30px rgba(0, 0, 0, 0.08),
            inset 1px 1px 0 rgba(255, 255, 255, 0.3);
    }
    
    .gemini-message {
        background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
        color: white;
        padding: 16px 20px;
        border-radius: 20px;
        margin: 12px 0;
        border-bottom-right-radius: 5px;
        display: inline-block;
        max-width: 85%;
        margin-left: 0;
        box-shadow: 
            0 10px 25px rgba(26, 188, 156, 0.3),
            0 0 20px rgba(26, 188, 156, 0.1),
            inset 1px 1px 0 rgba(255, 255, 255, 0.3);
        animation: slideInLeft 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        word-wrap: break-word;
        transform: perspective(1000px) rotateY(5deg);
        transition: all 0.3s ease;
    }
    
    .gemini-message:hover {
        transform: perspective(1000px) rotateY(8deg) scale(1.02);
        box-shadow: 
            0 15px 40px rgba(26, 188, 156, 0.4),
            0 0 30px rgba(26, 188, 156, 0.2),
            inset 1px 1px 0 rgba(255, 255, 255, 0.3);
    }
    
    .error-message {
        background: linear-gradient(135deg, #ffe0e0 0%, #ffcccc 100%);
        color: #c41e14;
        padding: 16px 20px;
        border-radius: 15px;
        border-left: 5px solid #c41e14;
        margin: 12px 0;
        box-shadow: 
            0 10px 25px rgba(196, 30, 20, 0.2),
            0 0 20px rgba(196, 30, 20, 0.1);
        animation: shake 0.5s ease-in-out;
        transform: perspective(1000px) rotateZ(-1deg);
    }
    
    @keyframes shake {
        0%, 100% { transform: perspective(1000px) rotateZ(-1deg) translateX(0); }
        25% { transform: perspective(1000px) rotateZ(-1deg) translateX(-5px); }
        75% { transform: perspective(1000px) rotateZ(-1deg) translateX(5px); }
    }
    
    /* Info cards with 3D flip effect */
    .info-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 
            0 15px 40px rgba(0, 0, 0, 0.1),
            0 0 1px rgba(0, 0, 0, 0.1);
        position: relative;
        transform: perspective(1000px) rotateX(-5deg);
        transition: all 0.5s cubic-bezier(0.23, 1, 0.320, 1);
        overflow: hidden;
    }
    
    .info-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0) 0%, rgba(102, 126, 234, 0.1) 100%);
        transform: translateX(-100%);
        transition: transform 0.5s ease;
    }
    
    .info-card:hover {
        transform: perspective(1000px) rotateX(5deg) scale(1.05);
        box-shadow: 
            0 25px 60px rgba(0, 0, 0, 0.15),
            0 0 40px rgba(102, 126, 234, 0.1);
    }
    
    .info-card:hover::before {
        transform: translateX(0);
    }
    
    .info-card h4 {
        color: #667eea;
        margin-bottom: 10px;
        font-size: 1.3em;
    }
    
    /* Feature list */
    .feature-item {
        padding: 12px;
        margin: 8px 0;
        border-left: 4px solid #667eea;
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.05) 0%, transparent 100%);
        border-radius: 5px;
        transition: all 0.3s ease;
        transform: translateX(0);
    }
    
    .feature-item:hover {
        transform: translateX(10px);
        border-left-color: #764ba2;
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.1) 0%, transparent 100%);
    }
    
    /* Input area */
    .input-area {
        background: white;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.15),
            0 0 1px rgba(0, 0, 0, 0.1);
        position: relative;
        transform: perspective(1000px) rotateX(-3deg);
        transition: all 0.3s ease;
    }
    
    .input-area:focus-within {
        transform: perspective(1000px) rotateX(2deg);
        box-shadow: 
            0 25px 70px rgba(0, 0, 0, 0.2),
            0 0 50px rgba(102, 126, 234, 0.1);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 35px !important;
        font-weight: bold !important;
        font-size: 1em !important;
        box-shadow: 
            0 10px 30px rgba(102, 126, 234, 0.4),
            0 0 20px rgba(102, 126, 234, 0.2) !important;
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        position: relative;
        overflow: hidden !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton>button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton>button:hover {
        transform: translateY(-5px) scale(1.05) !important;
        box-shadow: 
            0 20px 50px rgba(102, 126, 234, 0.6),
            0 0 40px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton>button:active {
        transform: translateY(-2px) !important;
    }
    
    /* Text input */
    .stTextInput>div>div>input {
        border-radius: 12px !important;
        border: 2px solid #e0e0e0 !important;
        padding: 14px 18px !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        background: white !important;
        color: #333 !important;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #667eea !important;
        box-shadow: 
            0 0 0 4px rgba(102, 126, 234, 0.1),
            0 5px 20px rgba(102, 126, 234, 0.2) !important;
        transform: scale(1.02);
    }
    
    /* Slider */
    .stSlider>div>div>div>div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    /* Success/Error alerts */
    .stSuccess {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%) !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 30px rgba(132, 250, 176, 0.3) !important;
        animation: popIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    
    .stError {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%) !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 30px rgba(250, 112, 154, 0.3) !important;
        animation: shake 0.5s ease-in-out;
    }
    
    @keyframes popIn {
        0% { transform: scale(0.8) opacity(0); }
        100% { transform: scale(1) opacity(1); }
    }
    
    /* Animations */
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: perspective(1000px) translateX(50px) rotateY(20deg);
        }
        to {
            opacity: 1;
            transform: perspective(1000px) translateX(0) rotateY(-5deg);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: perspective(1000px) translateX(-50px) rotateY(-20deg);
        }
        to {
            opacity: 1;
            transform: perspective(1000px) translateX(0) rotateY(5deg);
        }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .user-message, .bot-message {
            max-width: 95%;
        }
        
        .header-title {
            font-size: 1.8em;
        }
        
        .stat-box-3d {
            transform: perspective(1000px) rotateX(-5deg) rotateY(0deg);
        }
    }
</style>
""", unsafe_allow_html=True)

# Health check functions
def check_backend_status():
    """Check if backend is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        return response.status_code == 200, True
    except:
        return False, False

def check_endee_status():
    """Check if vector database is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code == 200:
            data = response.json()
            return data.get("endee_connected", False), True
        return False, False
    except:
        return False, False

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "gemini_messages" not in st.session_state:
    st.session_state.gemini_messages = []

if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0

if "backend_status" not in st.session_state:
    st.session_state.backend_status = False

if "endee_status" not in st.session_state:
    st.session_state.endee_status = False

# Sidebar with enhanced design
with st.sidebar:
    st.markdown("### 🤖 AI Assistant Control Panel")
    st.markdown("---")
    
    # Live Status Section
    st.markdown("### 🔴 System Status")
    
    # Backend Status
    col1, col2 = st.columns([3, 1])
    with col1:
        backend_status, backend_accessible = check_backend_status()
        status_text = "🟢 Online" if backend_status else "🔴 Offline"
        status_class = "status-online" if backend_status else "status-offline"
        st.markdown(f"""
        <div class="status-card {'status-card-online' if backend_status else 'status-card-offline'}">
            <strong>Backend Server</strong><br>
            <span class="status-badge {status_class}">{status_text}</span><br>
            <small>http://localhost:8000</small>
        </div>
        """, unsafe_allow_html=True)
        st.session_state.backend_status = backend_status
    
    # Vector DB Status
    endee_status, endee_accessible = check_endee_status()
    status_text_endee = "🟢 Connected" if endee_status else "🔴 Disconnected"
    status_class_endee = "status-online" if endee_status else "status-offline"
    st.markdown(f"""
    <div class="status-card {'status-card-online' if endee_status else 'status-card-offline'}">
        <strong>Vector Database</strong><br>
        <span class="status-badge {status_class_endee}">{status_text_endee}</span><br>
        <small>Endee @ localhost:9000</small>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.endee_status = endee_status
    
    st.markdown("---")
    
    # Stats with 3D effect
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stat-box-3d">
            <h3 style="margin: 0; font-size: 0.9em;">📊 Total Queries</h3>
            <div class="stat-number">{st.session_state.total_queries}</div>
            <p style="margin: 0; font-size: 0.85em; opacity: 0.9;">Conversations</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-box-3d">
            <h3 style="margin: 0; font-size: 0.9em;">💬 Messages</h3>
            <div class="stat-number">{len(st.session_state.messages)}</div>
            <p style="margin: 0; font-size: 0.85em; opacity: 0.9;">Total Msgs</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Features
    st.markdown("### ✨ Features")
    features = [
        ("🚀", "OpenAI (Primary)"),
        ("🌟", "Gemini (Specialized)"),
        ("⚡", "Real-time Response"),
        ("💾", "Chat History"),
        ("🎨", "Modern 3D UI"),
        ("🔒", "Secure & Private")
    ]
    for icon, feature in features:
        st.markdown(f"""
        <div class="feature-item">
            <strong>{icon} {feature}</strong>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Settings
    st.markdown("### ⚙️ Smart Settings")
    temperature = st.slider(
        "🌡️ Temperature",
        0.0, 1.0, 0.7,
        help="Lower = focused, Higher = creative"
    )
    max_tokens = st.slider(
        "📝 Max Tokens",
        100, 2000, 1000,
        help="Response length limit"
    )
    
    st.markdown("---")
    
    # Actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧹 Clear", use_container_width=True):
            st.session_state.messages = []
            st.session_state.gemini_messages = []
            st.success("✅ Cleared!")
            st.rerun()
    
    with col2:
        if st.button("⟳ Refresh", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # About
    st.markdown("### 📋 About")
    st.markdown("""
    **AI Chatbot Pro v2.0**
    
    🤖 Powered by:
    - OpenAI GPT-4 Mini
    - Google Gemini
    
    ✨ Features:
    - 3D UI Effects
    - Real-time Chat
    - Dual AI Engine
    - Message History
    - Live Status Monitor
    
    Made with ❤️
    """)

# Main header with 3D effect
st.markdown("""
<div class="header-container">
    <div class="header-3d">
        <div class="header-title">🚀 AI Chatbot Pro</div>
        <div class="header-subtitle">✨ Powered by OpenAI + Gemini with 3D UI & Live Monitoring</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Status overview
col1, col2, col3 = st.columns(3)
with col1:
    backend_emoji = "✅" if st.session_state.backend_status else "❌"
    st.markdown(f"### {backend_emoji} Backend")
    st.caption("FastAPI Server" if st.session_state.backend_status else "Currently Offline")

with col2:
    endee_emoji = "✅" if st.session_state.endee_status else "❌"
    st.markdown(f"### {endee_emoji} Vector DB")
    st.caption("Endee Online" if st.session_state.endee_status else "Not Connected")

with col3:
    st.markdown("### 📊 System")
    st.caption(f"{st.session_state.total_queries} Queries • {len(st.session_state.messages)} Messages")

st.markdown("---")

# Tabs for different chat modes
tab1, tab2 = st.tabs(["💬 OpenAI + Gemini Chat", "🌟 Gemini Only Chat"])

# Tab 1: Mixed Chat (OpenAI Primary + Gemini Fallback)
with tab1:
    st.markdown("### 💬 Hybrid Chat (OpenAI Primary → Gemini Fallback)")
    
    if not st.session_state.backend_status:
        st.warning("⚠️ Backend server is offline. Chat may not work. Please ensure backend is running on port 8000.")
    
    if st.session_state.messages:
        st.markdown("**Conversation:**")
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div style="text-align: right; margin-right: 10px;">
                    <div class="user-message">
                        <strong>👤 You:</strong> {message["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                if "error" in message.get("type", ""):
                    st.markdown(f"""
                    <div style="text-align: left; margin-left: 10px;">
                        <div class="error-message">
                            <strong>⚠️ Error:</strong> {message["content"]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="text-align: left; margin-left: 10px;">
                        <div class="bot-message">
                            <strong>🤖 Assistant ({message.get('source', 'Unknown')}):</strong><br>
                            {message["content"]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            "Type your message...",
            placeholder="Ask me anything! ✨",
            label_visibility="collapsed",
            key="tab1_input"
        )
    with col2:
        send_button = st.button("📤", use_container_width=True, key="tab1_send")
    
    if send_button and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.total_queries += 1
        
        with st.spinner("🤖 Thinking... 💭"):
            try:
                response = requests.post(
                    "http://localhost:8000/chat",
                    json={"question": user_input},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    bot_response = data.get("response", "No response received.")
                    source = data.get("source", "Unknown")
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": bot_response,
                        "source": source,
                        "type": "normal" if source != "Error" else "error"
                    })
                    
                    if source != "Error":
                        st.success(f"✅ Response from {source}", icon="✨")
            except Exception as e:
                error_msg = f"Connection error: {str(e)}"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "type": "error"
                })
                st.error(f"🔴 {error_msg}")
        
        st.rerun()

# Tab 2: Gemini Only Chat
with tab2:
    st.markdown("### 🌟 Gemini Specialized Chat")
    st.info("This section is dedicated to Gemini API responses only. Use this for specific AI tasks.")
    
    if st.session_state.gemini_messages:
        st.markdown("**Gemini Conversation:**")
        for message in st.session_state.gemini_messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div style="text-align: right; margin-right: 10px;">
                    <div class="user-message">
                        <strong>👤 You:</strong> {message["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                if "error" in message.get("type", ""):
                    st.markdown(f"""
                    <div style="text-align: left; margin-left: 10px;">
                        <div class="error-message">
                            <strong>⚠️ Error:</strong> {message["content"]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="text-align: left; margin-left: 10px;">
                        <div class="gemini-message">
                            <strong>🌟 Gemini Assistant:</strong><br>
                            {message["content"]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([5, 1])
    with col1:
        gemini_input = st.text_input(
            "Ask Gemini something...",
            placeholder="Gemini specializes in creative tasks! ✨",
            label_visibility="collapsed",
            key="tab2_input"
        )
    with col2:
        gemini_send = st.button("📤", use_container_width=True, key="tab2_send")
    
    if gemini_send and gemini_input:
        st.session_state.gemini_messages.append({"role": "user", "content": gemini_input})
        st.session_state.total_queries += 1
        
        with st.spinner("🌟 Gemini is thinking... 💭"):
            try:
                response = requests.post(
                    "http://localhost:8000/chat",
                    json={"question": f"[GEMINI_ONLY] {gemini_input}"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    bot_response = data.get("response", "No response received.")
                    source = data.get("source", "Unknown")
                    
                    st.session_state.gemini_messages.append({
                        "role": "assistant",
                        "content": bot_response,
                        "source": source,
                        "type": "normal" if source != "Error" else "error"
                    })
                    
                    if source != "Error":
                        st.success(f"✅ Response from {source}", icon="🌟")
            except Exception as e:
                error_msg = f"Connection error: {str(e)}"
                st.session_state.gemini_messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "type": "error"
                })
                st.error(f"🔴 {error_msg}")
        
        st.rerun()

st.markdown("---")

# Footer with enhanced design
st.markdown("""
<div style="text-align: center; color: #999; padding: 30px 20px; background: linear-gradient(180deg, transparent 0%, rgba(0, 0, 0, 0.05) 100%); border-radius: 20px; margin-top: 40px;">
    <h3 style="color: #667eea; margin-bottom: 15px;">🌟 Experience the Future of AI</h3>
    <p><strong>AI Chatbot Pro v2.0</strong></p>
    <p style="font-size: 0.9em;">Built with ❤️ using Streamlit, FastAPI & Advanced 3D CSS</p>
    <p style="font-size: 0.85em; margin-top: 15px;">© 2026 AI Assistant with Live System Monitoring | Made with ✨ Powered by Modern Tech Stack</p>
</div>
""", unsafe_allow_html=True)