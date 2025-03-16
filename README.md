# Project-Based_on_RAG-LLM_model

# Chatbot with Retrieval-Augmented Generation (RAG)

This project implements a chatbot using **Retrieval-Augmented Generation (RAG)** with **Pinecone** as a vector database and **Google's Gemini LLM** for answering user queries based on stored document data. The system includes:
- **Vector Storage** (Pinecone) for efficient document retrieval
- **RAG Pipeline** for retrieving relevant context and generating answers
- **Streamlit Frontend** for user interaction
- **Evaluation & Logging** to track chatbot performance

## Features
- Loads and processes text files to create vector embeddings
- Stores vectorized data in Pinecone
- Retrieves relevant documents using similarity search
- Uses Google's Gemini model to generate responses
- Logs interactions for analysis and improvement

## Project Structure
```
📂 project_root/
├── vector_storage.py  # Handles data loading and vectorization
├── rag_pipeline.py    # Implements retrieval and answer generation
├── frontend.py        # Streamlit-based chatbot UI
├── questions_list.py  # Predefined questions for evaluation
├── .env               # Environment variables for API keys
├── log_queries.txt    # Logs chatbot interactions
├── log_queries.csv    # CSV log of responses
└── README.md          # Project documentation
```

## Installation
### Prerequisites
- Python 3.8+
- API keys for **Pinecone** and **Google Gemini**


## Usage
1. **Set up environment variables**
   - Create a `.env` file and add your API keys:
     ```
     GEMINI_API=your_google_api_key
     PINECONE_API=your_pinecone_api_key
     ```

2. **Run the vector storage script** to process and store document embeddings:
   ```bash
   python vector_storage.py
   ```

3. **Run the RAG pipeline script** to enable document retrieval and chatbot response generation:
   ```bash
   python rag_pipeline.py
   ```

4. **Start the chatbot UI** using Streamlit:
   ```bash
   streamlit run frontend.py
   ```

## How It Works
1. **Document Processing:** `vector_storage.py` loads text files, splits them into chunks, converts them into embeddings, and uploads them to Pinecone.
2. **Retrieval & Generation:** `rag_pipeline.py` retrieves relevant documents and generates responses using the Gemini LLM.
3. **User Interaction:** `frontend.py` provides a simple interface where users can ask questions and receive answers based on stored knowledge.
4. **Logging & Evaluation:** Queries and responses are logged in `log_queries.txt` and `log_queries.csv`, allowing for performance tracking.

## Example Query
**User Input:** "What is the population of New York?"

**Chatbot Response:** "Based on the retrieved data, the population of New York is approximately 8.5 million."

## Contributing
Feel free to fork this repository and make improvements! If you find any issues, please open an issue or submit a pull request.

## License
This project is open-source and available under the **MIT License**.

