import streamlit as st
from PyPDF2 import PdfReader
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
import os

# 1. Page Config
st.set_page_config(page_title="DocuMind AI", page_icon="✨", layout="centered")

# 2. Aggressive CSS Hack (Bypassing Streamlit Cache)
st.markdown("""
    <style>
    /* Hide Default Header/Footer */
    #MainMenu, footer, header {visibility: hidden !important;}

    /* Deep Premium Dark Mode */
    .stApp {
        background-color: #0B0E14 !important;
        color: #E2E8F0 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Hero Section */
    .hero-container {
        text-align: center;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FF512F, #DD2476);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #94A3B8;
        margin-bottom: 2rem;
    }

    /* --- NUCLEAR CSS FOR UPLOADER --- */
    /* 1. Hiding the 200MB text by targeting the exact 'small' HTML tag */
    div[data-testid="stFileUploader"] small {
        display: none !important;
        opacity: 0 !important;
        visibility: hidden !important;
    }

    /* 2. Styling the upload box */
    div[data-testid="stFileUploader"] section {
        border: 2px dashed #DD2476 !important;
        border-radius: 16px !important;
        background-color: rgba(221, 36, 118, 0.05) !important;
        padding: 2rem !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    /* 3. Button Customization */
    div[data-testid="stFileUploader"] button {
        background-color: #DD2476 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        transition: 0.3s !important;
    }
    div[data-testid="stFileUploader"] button:hover {
        background-color: #FF512F !important;
    }

    /* Chat Input Styling */
    .stTextInput>div>div>input {
        border-radius: 12px !important;
        border: 1px solid #334155 !important;
        background-color: #1E293B !important;
        color: white !important;
        padding: 16px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Custom Title
st.markdown("""
    <div class="hero-container">
        <h1 class="hero-title">DocuMind AI</h1>
        <p class="hero-subtitle">Upload any PDF and extract intelligent insights instantly.</p>
    </div>
""", unsafe_allow_html=True)

# 4. Backend
api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    st.error("⚠️ API Key is missing. Please configure it in Hugging Face Secrets.")
else:
    genai.configure(api_key=api_key)
    
    pdf = st.file_uploader("", type="pdf")
    
    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
            
        st.success("✨ Document processed successfully. Ready for analysis.")
        
        user_question = st.text_input("Ask a question about this document...")
        
        if user_question:
            with st.spinner("Analyzing document..."):
                valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                if not valid_models:
                    st.error("No active model found for this API key!")
                else:
                    best_model = next((m for m in valid_models if "flash" in m), valid_models[0])
                    llm = ChatGoogleGenerativeAI(model=best_model, temperature=0.3)
                    
                    prompt = f"Read the following document and answer the user's question strictly based on the text. Always provide your final answer in English.\n\nDocument Text:\n{text}\n\nQuestion: {user_question}"
                    
                    response = llm.invoke(prompt)
                    
                    st.markdown("---")
                    st.markdown(f"### 💡 AI Insight\n{response.content}")
