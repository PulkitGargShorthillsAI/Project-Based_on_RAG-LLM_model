import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain.document_loaders import DirectoryLoader

load_dotenv()

GEMINI_API = os.getenv("GEMINI_API")
PINECONE_API_KEY = os.getenv("PINECONE_API")

if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY is not set. Please check your environment variables.")

# Explicitly set the API key
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

class PineconeHandler:
    def __init__(self, index_name="chatbot1"):
        self.index_name = index_name
        if not PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY is not set. Please check your environment variables.")
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.index = self._initialize_index()
        
    def _initialize_index(self):
        print(f"Checking if Pinecone index '{self.index_name}' exists...")
        
        index_exists = any(idx['name'] == self.index_name for idx in self.pc.list_indexes())
        
        if not index_exists:
            print(f"Creating a new Pinecone index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=768,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
        else:
            print("Index already exists")
        
        return self.pc.Index(self.index_name)

class TextProcessor:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.text_chunks = self._process_text_files()
    
    def _load_txt_files(self):
        loader = DirectoryLoader(self.folder_path, glob="*.txt", loader_cls=TextLoader)
        return loader.load()
    
    def _split_text(self, documents):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        return text_splitter.split_documents(documents)
    
    def _process_text_files(self):
        extracted_data = self._load_txt_files()
        return self._split_text(extracted_data)
    
class VectorStoreUploader:
    def __init__(self, pinecone_handler, text_processor):
        self.pinecone_handler = pinecone_handler
        self.text_chunks = text_processor.text_chunks
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001", 
            google_api_key=GEMINI_API,
        )
        self._upload_to_pinecone()
    
    def _upload_to_pinecone(self):
        print("Uploading documents to Pinecone...")
        PineconeVectorStore.from_documents(
            documents=self.text_chunks,
            index_name=self.pinecone_handler.index_name,
            embedding=self.embeddings
        )
        print("Documents stored in Pinecone!")

if __name__ == "__main__":
    folder_path = "/home/shtlp_0101/Documents/Project-Based_on_RAG-LLM_model/scraped_city_data"
    pinecone_handler = PineconeHandler()
    text_processor = TextProcessor(folder_path)
    vector_store_uploader = VectorStoreUploader(pinecone_handler, text_processor)
