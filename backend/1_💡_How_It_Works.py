import streamlit as st
import requests
import json
import time

st.set_page_config(page_title="How It Works - AI Agent", page_icon="💡", layout="wide")

# Advanced CSS for Pipeline Animations and Glassmorphism
st.markdown("""
<style>
.pipeline-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 40px 0;
    flex-wrap: wrap;
}
.pipeline-step {
    background: rgba(30, 41, 59, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 20px;
    width: 18%;
    min-width: 180px;
    text-align: center;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}
.pipeline-step:hover {
    transform: translateY(-5px);
    border-color: rgba(99, 102, 241, 0.5);
    box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.2);
}
.step-icon {
    font-size: 32px;
    margin-bottom: 10px;
}
.step-title {
    font-size: 16px;
    font-weight: 600;
    color: #f8fafc;
    margin-bottom: 5px;
}
.step-desc {
    font-size: 12px;
    color: #94a3b8;
}
.arrow {
    color: #6366f1;
    font-size: 24px;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0% { opacity: 0.5; transform: translateX(0); }
    50% { opacity: 1; transform: translateX(5px); }
    100% { opacity: 0.5; transform: translateX(0); }
}
.result-card {
    background: linear-gradient(145deg, #1e1e2f, #252542);
    border-left: 4px solid #6366f1;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 The Intelligence Pipeline")
st.markdown("Discover exactly how your prompts are transformed into intelligent, context-aware responses using our Vector Database and Retrieval-Augmented Generation (RAG) architecture.")

# Visual Diagram
st.markdown("""
<div class="pipeline-container">
    <div class="pipeline-step">
        <div class="step-icon">💬</div>
        <div class="step-title">1. User Input</div>
        <div class="step-desc">Your raw text query</div>
    </div>
    <div class="arrow">➔</div>
    <div class="pipeline-step">
        <div class="step-icon">🔢</div>
        <div class="step-title">2. Embedding</div>
        <div class="step-desc">Text to mathematical vector</div>
    </div>
    <div class="arrow">➔</div>
    <div class="pipeline-step">
        <div class="step-icon">🗄️</div>
        <div class="step-title">3. Vector Search</div>
        <div class="step-desc">Find similar memories</div>
    </div>
    <div class="arrow">➔</div>
    <div class="pipeline-step">
        <div class="step-icon">🧩</div>
        <div class="step-title">4. Context Assembly</div>
        <div class="step-desc">Combine data + prompt</div>
    </div>
    <div class="arrow">➔</div>
    <div class="pipeline-step">
        <div class="step-icon">✨</div>
        <div class="step-title">5. AI Response</div>
        <div class="step-title">Generate Answer</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

st.header("Interactive Pipeline Demo")
st.markdown("Enter a query below. We will expose the inner workings of the RAG pipeline in real-time.")

demo_query = st.text_input("Test Query:", value="What insights do you remember from previous documents?")

if st.button("Run Pipeline Demonstration", type="primary"):
    with st.spinner("Executing Pipeline..."):
        try:
            # Point this to your backend
            res = requests.post(
                "http://localhost:8000/how-it-works/demo", 
                json={"query": demo_query, "top_k": 3}
            )
            data = res.json()
            
            st.success(f"Pipeline executed successfully in {data.get('execution_time_ms', 0)}ms!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Step 1: Embedding Vector")
                st.info(f"Model generated a {data['vector_dimensions']}-dimensional vector.")
                sample_v = [round(v, 4) for v in data['embedding_sample']]
                st.code(f"[{sample_v[0]}, {sample_v[1]}, {sample_v[2]}, {sample_v[3]}, {sample_v[4]} ...]", language="json")
                
                st.subheader("Step 2: Vector Search Results")
                if data['retrieved_context']:
                    for idx, ctx in enumerate(data['retrieved_context']):
                        score = round(ctx['score'], 3)
                        mem_type = ctx['metadata'].get('memory_type', 'Unknown').upper()
                        st.markdown(f"**Match {idx+1} ({mem_type})** - Score: `{score}`\n> _{ctx['text'][:150]}..._")
                else:
                    st.warning("No relevant memory found in the Vector DB. Try chatting or uploading documents first!")
                    
            with col2:
                st.subheader("Step 3 & 4: LLM Context & Generation")
                st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                st.markdown("### 🤖 Final AI Output")
                st.write(data['final_response'])
                st.markdown("</div>", unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Error connecting to backend pipeline: {e}")
            st.info("Ensure the FastAPI backend is running on port 8000.")