from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from llama_index.indices.vector_store import VectorStoreIndex
from llama_index.indices.service_context import ServiceContext
from llama_index.schema import Document
from llama_index.llms.openai import OpenAI
import openai
from llama_index.readers import SimpleDirectoryReader
import pandas as pd
import requests
import tempfile
from pathlib import Path
from llama_index.readers.file.base import PDFReader
import chromadb


load_dotenv()
app = FastAPI(title="Legislator Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize ChromaDB client
chroma_client = chromadb.Client()

# Create a collection
collection = chroma_client.create_collection(name='legislator_data')

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

index = None
chat_engine = None

def process_all_pdfs():

    pdf_docs = []
    temp_dir = tempfile.mkdtemp()
    csv_file = "../data/hearings.csv"
    pdf_count = 0
    try:
        df = pd.read_csv(csv_file, header=None)
        for row in df.itertuples(index=False):
            for cell in row:
                if isinstance(cell, str) and cell.endswith('.pdf'):
                    print(f"Processing PDF {pdf_count + 1}: {cell}")
                    response = requests.get(cell)
                    if response.status_code == 200:
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir=temp_dir)
                        temp_file.write(response.content)
                        temp_file.close()
                        
                        pdf_reader = PDFReader()
                        documents = pdf_reader.load_data(temp_file.name)
                        os.unlink(temp_file.name)
                        pdf_docs.extend(documents)
                        pdf_count += 1
    except Exception as e:
        print(f"Error processing PDFs: {str(e)}")
    return pdf_docs

def initialize_index():
    global index, chat_engine
    if index is None:
        try:
            print("Loading documents from data directory...")
            reader = SimpleDirectoryReader(input_dir="../data", recursive=True)
            docs = reader.load_data()
            print(f"Loaded {len(docs)} documents from data directory")
            
            # Process all PDFs
            pdf_docs = process_all_pdfs()
            print(f"Loaded {len(pdf_docs)} PDF documents")
            docs.extend(pdf_docs)
            
            print("Initializing OpenAI model...")
            llm = OpenAI(
                model="gpt-3.5-turbo",
                temperature=0.7,
                system_prompt="""You are an expert on the 118th Congress's Senate Hearings. 
                Your role is to provide detailed, accurate information about legislation, hearings, and congressional activities.
                When asked about specific legislation or hearings, provide relevant details from the documents.
                If you don't know something, say so rather than making up information.
                Keep your answers focused on the actual content from the Senate hearings."""
            )
            
            print("Creating vector store index...")
            service_context = ServiceContext.from_defaults(llm=llm)
            index = VectorStoreIndex.from_documents(docs, service_context=service_context)
            print("Creating chat engine...")
            chat_engine = index.as_chat_engine(
                chat_mode="context",
                verbose=True,
                similarity_top_k=3,
                system_prompt="""You are an expert on the 118th Congress's Senate Hearings. 
                Your role is to provide detailed, accurate information about legislation, hearings, and congressional activities.
                When asked about specific legislation or hearings, provide relevant details from the documents.
                If you don't know something, say so rather than making up information.
                Keep your answers focused on the actual content from the Senate hearings."""
            )
            print("Initialization complete!")
        except Exception as e:
            print(f"Error during initialization: {str(e)}")
            raise

@app.on_event("startup")
async def startup_event():
    initialize_index()

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if chat_engine is None:
        print("Error: Chat engine not initialized")
        raise HTTPException(status_code=500, detail="Chat engine not initialized")
    
    try:
        print("\n" + "="*50)
        print(f"Received question: {request.message}")
        print("="*50)
        
        response = chat_engine.chat(request.message)
        
        print("\n" + "-"*50)
        print("Chatbot Response:")
        print(response.response)
        print("-"*50 + "\n")
        
        # Store the chat message and response in ChromaDB
        add_data_to_collection(request.message)
        add_data_to_collection(response.response)
        
        return ChatResponse(response=response.response)
    except Exception as e:
        print(f"\nError during chat: {str(e)}")
        print("="*50 + "\n")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "Server is running!"}

def add_data_to_collection(data):
    collection.add(
        documents=[data],
        metadatas=[{'source': 'legislator_data'}],
        ids=['1']
    )

def query_data_from_collection(query):
    results = collection.query(
        query_texts=[query],
        n_results=1
    )
    return results
