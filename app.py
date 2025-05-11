import streamlit as st
from llama_index.core import VectorStoreIndex, ServiceContext, Document, Settings
from llama_index.llms.openai import OpenAI
import openai
from llama_index.core import SimpleDirectoryReader
import pandas as pd
import requests
import tempfile
import os
from pathlib import Path
from llama_index.readers.file import PDFReader

Settings.chunk_size = 2048
Settings.chunk_overlap = 100

st.set_page_config(page_title="Legislator Chatbot (Updated 2024)", page_icon="", layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = st.secrets["openai_key"]
st.title("Legislator Chatbot (Updated 2024)")
st.info("Ask questions regarding current Senate legislature and receive up-to-date answers based on real documents (bills, hearings, and voting history)", icon="📃")
         
if "messages" not in st.session_state.keys()
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question!"}
    ]

def download_and_process_pdf(url, temp_dir):
    try:
        response = requests.get(url)
        if response.status_code == 200:

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir=temp_dir)
            temp_file.write(response.content)
            temp_file.close()
            
            pdf_reader = PDFReader()
            documents = pdf_reader.load_data(temp_file.name)
            
            os.unlink(temp_file.name)
            return documents
    except Exception as e:
        st.warning(f"Failed to process PDF from {url}: {str(e)}")
        return []

def extract_pdf_urls_from_csv():
    pdf_docs = []
    temp_dir = tempfile.mkdtemp()

    csv_file = "data/hearings.csv"
    try:
        df = pd.read_csv(csv_file)
        for col in df.columns:
            if df[col].astype(str).str.contains('pdf').any():
                pdf_urls = df[df[col].astype(str).str.contains('pdf')][col].unique()
                for url in pdf_urls:
                    if isinstance(url, str) and url.endswith('.pdf'):
                        print(f"Processing PDF from {url}")
                        pdf_docs.extend(download_and_process_pdf(url, temp_dir))
    except Exception as e:
        st.warning(f"Error processing {csv_file}: {str(e)}")
    
    return pdf_docs

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading all available information. This might take up to 5-10 minutes."):
        # Load local files
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()
        pdf_docs = extract_pdf_urls_from_csv()
        docs.extend(pdf_docs)
        Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.5, system_prompt="You are an expert on the 118th Congress's Senate Hearings and your job is to answer technical questions. Assume that all questions are related to the Senate hearings. Keep your answers technical and based on facts – do not hallucinate features.")
        index = VectorStoreIndex.from_documents(docs)
        return index

index = load_data()

if "chat_engine" not in st.session_state.keys(): 
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True, similarity_top_k = 15)

if prompt := st.chat_input("Your question"): 
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: 
    with st.chat_message(message["role"]):
        st.write(message["content"])

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) 
