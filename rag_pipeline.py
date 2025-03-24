import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

# Define log file path
LOG_FILE = "logging/test_log_queries.log"

def write_log(message, error=False):
    """Writes log messages with timestamps. Errors are marked separately."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_type = "ERROR" if error else "INFO"
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{timestamp} - {log_type}: {message}\n")

class ChatbotRAG:
    def __init__(self, index_name: str):
        try:
            load_dotenv()
            self.gemini_api_key = os.getenv("GEMINI_API_PGARG")
            self.pinecone_api_key = os.getenv("PINECONE_API")
            os.environ["PINECONE_API_KEY"] = self.pinecone_api_key

            if not self.gemini_api_key or not self.pinecone_api_key:
                raise ValueError("API keys are missing. Check your .env file.")

            self.index_name = index_name
            self.embeddings = self._initialize_embeddings()
            self.retriever = self._initialize_retriever()
            self.llm = self._initialize_llm()
            self.rag_chain = self._initialize_rag_chain()
            
            write_log("Chatbot initialized successfully!")
        except Exception as e:
            write_log(f"Error initializing chatbot: {str(e)}", error=True)
            raise e
    
    def _initialize_embeddings(self):
        try:
            return GoogleGenerativeAIEmbeddings(
                model="models/embedding-001", 
                google_api_key=self.gemini_api_key
            )
        except Exception as e:
            write_log(f"Error initializing embeddings: {str(e)}", error=True)
            raise e
    
    def _initialize_retriever(self):
        try:
            docsearch = PineconeVectorStore.from_existing_index(
                index_name=self.index_name,
                embedding=self.embeddings
            )
            return docsearch.as_retriever(
                search_type="similarity", 
                search_kwargs={"k": 3},
            )
        except Exception as e:
            write_log(f"Error initializing retriever: {str(e)}", error=True)
            raise e
    
    def _initialize_llm(self):
        try:
            return ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                api_key=self.gemini_api_key
            )
        except Exception as e:
            write_log(f"Error initializing LLM: {str(e)}", error=True)
            raise e
    
    def _initialize_rag_chain(self):
        try:
            system_prompt = (
                "You are an assistant for question-answering tasks. "
                "Use the following pieces of retrieved context to answer "
                "the question. If you don't know the answer, say that you "
                "don't know. Use three sentences maximum and keep the "
                "answer concise."
                "\n\n"
                "{context}"
            )
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}"),
            ])
            question_answer_chain = create_stuff_documents_chain(self.llm, prompt)
            return create_retrieval_chain(self.retriever, question_answer_chain)
        except Exception as e:
            write_log(f"Error initializing RAG chain: {str(e)}", error=True)
            raise e
    
    def ask_question(self, question: str):
        try:
            if not question.strip():
                raise ValueError("Question cannot be empty.")

            response = self.rag_chain.invoke({"input": question})
            return response
        except Exception as e:
            write_log(f"Error processing question '{question}': {str(e)}", error=True)
            return "An error occurred while processing your question."


try:
    chatbot = ChatbotRAG(index_name="chatbot4")
except Exception as main_error:
    write_log(f"Unhandled error in main executio)n: {str(main_error)}", error=True)
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{'-'*40}\n")
    raise main_error

with open(LOG_FILE, "a") as log_file:
    log_file.write(f"{'-'*40}\n")
