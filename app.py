import streamlit as st
from PyPDF2 import PdfReader
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
import os

st.set_page_config(page_title="PDF Q&A", page_icon="📄")
st.header("Chat with your PDF 📄 (Auto-Detect Model)")

api_key = st.text_input("Enter your Google API Key:", type="password")

if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
    # Google API ko configure kar rahe hain
    genai.configure(api_key=api_key)
    
    pdf = st.file_uploader("Upload a PDF file", type="pdf")
    
    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
            
        st.success("PDF load ho gaya! Chalo ab sawal pucho.")
        
        user_question = st.text_input("Ask anything from the PDF:")
        
        if user_question:
            # 1. Zinda models ki list nikalo
            valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            if not valid_models:
                st.error("Tumhari API key me koi active model nahi mila!")
            else:
                # 2. Model select karo
                best_model = next((m for m in valid_models if "flash" in m), valid_models[0])
                st.info(f"(System: Auto-selected {best_model} model)")
                
                # 3. Model ko call karo (English output ke sath)
                llm = ChatGoogleGenerativeAI(model=best_model, temperature=0.3)
                prompt = f"Read the following document and answer the user's question strictly based on the text. Always provide your final answer in English.\n\nDocument Text:\n{text}\n\nQuestion: {user_question}"
                
                response = llm.invoke(prompt)
                st.write("**Answer:**", response.content)