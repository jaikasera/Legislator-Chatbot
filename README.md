# Policy RAG Chatbot (Legislator Chatbot)

The Policy RAG Chatbot leverages Retrieval Augmented Generation (RAG) to provide up-to-date information about US legislation and policy using documents such as bills, hearings, and voting polls. By integrating recent data scraped from the US Congress website, the chatbot can answer policy-related questions more accurately than a standard LLM.

###  Overview

- **Goal:** To enhance an LLM with the latest legislative and policy documents, allowing it to provide factual responses based on real-world data.
- **Data Sources:** US Congress website (congress.gov)
- **Data Scraped:**
  - 12,000 bills
  - 13 hearings
  - 48 voting polls

###  Implementation Details

The application is built using Streamlit for the frontend, OpenAI for LLM processing, and LlamaIndex for RAG indexing and retrieval.

- **Web Scraping Tools:** Selenium, BeautifulSoup
- **Data Processing:** Extracts PDF links from CSV files and processes them using a PDFReader.
- **Data Storage:** Data is processed and indexed using LlamaIndex to create a vector store that is queried during interactions.

###  Usage

1. **Run the Application:**
   - Ensure all dependencies are installed using `pip install -r requirements.txt`.
   - Set the OpenAI API key in the Streamlit secrets file.

2. **Initialize the RAG Model:**
   - Upon startup, the application loads data from the `data` folder and processes additional PDFs from provided CSVs.
   - Data is indexed using LlamaIndex to create a searchable vector store.

3. **Chat with the Bot:**
   - The chatbot is initiated in condense question mode with similarity top-k set to 15, ensuring that responses are contextually relevant to the user query.

###  Example Interaction
- **User Query:** "What recent voting polls were conducted regarding healthcare policies?"
- **Response:** The model retrieves relevant data from the indexed voting poll documents and provides a detailed, factual response based on actual legislative records.

###  Additional Notes
- The `additional_data` folder contains the scraped bills, which are not indexed by default to avoid excessive load times. They can be optionally included if needed for more comprehensive responses.
