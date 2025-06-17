# Legislator Chatbot

The Legislator Chatbot is a chatbot that leverages Retrieval Augmented Generation (RAG) to provide up-to-date information about US legislation and policy (specifically in the Senate) using documents such as bills, hearings, and voting polls. By integrating recent data scraped from the US Congress website, the chatbot can answer policy-related questions more accurately than a standard LLM.

## Overview

- **Goal:** To enhance an LLM with the latest legislative and policy documents, allowing it to provide factual responses based on real-world data.
- **Data Sources:** US Congress website (congress.gov)
- **Data Scraped:**
  - 12,000 bills
  - 13 hearings
  - 48 voting polls

## Implementation Details

The application is built using:
- **Frontend:** React + TypeScript
- **Backend:** FastAPI + Python
- **LLM Processing:** OpenAI
- **RAG Indexing and Retrieval:** LlamaIndex
- **Web Scraping Tools:** Selenium + BeautifulSoup
- **Node.js:** Used for managing frontend dependencies and running the development server

### Initialize the RAG Model

- Upon startup, the application loads data from the `data` folder and processes additional PDFs from the provided CSVs.
- Data is indexed using LlamaIndex to create a searchable vector store.

### Chat with the Bot

- The chatbot is initiated in condense question mode with similarity top-k set to 3, ensuring that responses are contextually relevant to the user query.

## Example Interaction

**User Query:** "What recent voting polls were conducted regarding healthcare policies?"

**Response:** The model retrieves relevant data from the indexed voting poll documents and provides a detailed, factual response based on actual legislative records.

## Additional Notes

- The `additional_data` folder contains the scraped bills, which are currently being excluded from indexing to avoid excessive load times. They can be optionally included if needed for more comprehensive responses.

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate 
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd frontend
npm install
```

4. Create a `.env` file in the backend directory with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Running the Application

1. Start the backend server:
```bash
cd backend
source venv/bin/activate  
uvicorn app.main:app --reload
```

2. In a new terminal, start the frontend development server:
```bash
cd frontend
npm start
```

3. Open your browser and navigate to `http://localhost:3000`

<img width="1464" alt="Screenshot 2025-06-16 at 6 55 05 PM" src="https://github.com/user-attachments/assets/d96ed219-6e72-446a-bb0c-efe9c2567c8c" />
