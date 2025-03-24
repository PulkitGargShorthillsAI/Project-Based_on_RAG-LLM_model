import os
from datetime import datetime
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore

# Load environment variables
load_dotenv()

GEMINI_API = os.getenv("GEMINI_API")
PINECONE_API_KEY = os.getenv("PINECONE_API")
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

# Define log file path
LOG_FILE = "logging/log_queries.log"

def write_log(message, error=False):
    """Writes log messages with timestamps. Errors are marked separately."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_type = "ERROR" if error else "INFO"
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{timestamp} - {log_type}: {message}\n")

# Check API key
if not PINECONE_API_KEY:
    write_log("PINECONE_API_KEY is not set. Please check your environment variables.", error=True)
    raise ValueError("PINECONE_API_KEY is not set. Please check your environment variables.")

# Initialize Pinecone
try:
    pc = Pinecone(api_key=PINECONE_API_KEY)
except Exception as e:
    write_log(f"Failed to initialize Pinecone: {str(e)}", error=True)
    raise e

class PineconeHandler:
    def __init__(self, index_name="chatbot4"):
        self.index_name = index_name
        self.pc = None
        self.index = None
        try:
            self.pc = Pinecone(api_key=PINECONE_API_KEY)
            self.index = self._initialize_index()
        except Exception as e:
            write_log(f"Failed to initialize PineconeHandler: {str(e)}", error=True)
            raise e
        
    def _initialize_index(self):
        try:
            write_log(f"Checking if Pinecone index '{self.index_name}' exists...")

            index_exists = any(idx['name'] == self.index_name for idx in self.pc.list_indexes())

            if not index_exists:
                write_log(f"Creating a new Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=768,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1")
                )
            else:
                write_log("Index already exists.")

            return self.pc.Index(self.index_name)
        except Exception as e:
            write_log(f"Error initializing index '{self.index_name}': {str(e)}", error=True)
            raise e

    def index_has_data(self):
        """Checks if the index already contains data to prevent unnecessary re-uploading."""
        try:
            stats = self.index.describe_index_stats()
            num_vectors = stats.get("total_vector_count", 0)
            write_log(f"Current index contains {num_vectors} vectors.")
            return num_vectors > 0
        except Exception as e:
            write_log(f"Failed to retrieve index stats: {str(e)}", error=True)
            return False

class TextProcessor:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.text_chunks = []
        try:
            self.text_chunks = self._process_text_files()
        except Exception as e:
            write_log(f"Error processing text files: {str(e)}", error=True)
            raise e
    
    def _load_txt_files(self):
        try:
            loader = DirectoryLoader(self.folder_path, glob="*.txt", loader_cls=TextLoader)
            return loader.load()
        except Exception as e:
            write_log(f"Error loading text files: {str(e)}", error=True)
            raise e
    
    def _split_text(self, documents):
        try:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            return text_splitter.split_documents(documents)
        except Exception as e:
            write_log(f"Error splitting text: {str(e)}", error=True)
            raise e
    
    def _process_text_files(self):
        extracted_data = self._load_txt_files()
        return self._split_text(extracted_data)

class VectorStoreUploader:
    def __init__(self, pinecone_handler: PineconeHandler, text_processor: TextProcessor):
        self.pinecone_handler = pinecone_handler
        self.text_chunks = text_processor.text_chunks
        self.embeddings = None
        try:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001", 
                google_api_key=GEMINI_API,
            )
        except Exception as e:
            write_log(f"Error initializing GoogleGenerativeAIEmbeddings: {str(e)}", error=True)
            raise e
        
        try:
            self._upload_to_pinecone()
        except Exception as e:
            write_log(f"Error uploading documents to Pinecone: {str(e)}", error=True)
            raise e
    
    def _upload_to_pinecone(self):
        if self.pinecone_handler.index_has_data():
            write_log("Index already contains data. Skipping re-upload.")
            return
        
        try:
            write_log("Uploading documents to Pinecone...")
            PineconeVectorStore.from_documents(
                documents=self.text_chunks,
                index_name=self.pinecone_handler.index_name,
                embedding=self.embeddings
            )
            write_log("Documents successfully stored in Pinecone.")
        except Exception as e:
            write_log(f"Error during Pinecone upload: {str(e)}", error=True)
            raise e

if __name__ == "__main__":
    try:
        folder_path = "scraped_city_data"
        pinecone_handler = PineconeHandler()
        text_processor = TextProcessor(folder_path)
        vector_store_uploader = VectorStoreUploader(pinecone_handler, text_processor)
    except Exception as main_error:
        write_log(f"Unhandled error in main execution: {str(main_error)}", error=True)
        with open(LOG_FILE, "a") as log_file:
            log_file.write(f"{'-'*40}\n")
        raise main_error
    
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{'-'*40}\n")

