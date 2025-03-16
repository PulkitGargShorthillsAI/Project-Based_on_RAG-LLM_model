from pinecone import Pinecone, ServerlessSpec
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pinecone import ServerlessSpec, Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv
load_dotenv()


print("🔄 Loading environment variables...")
GEMINI_API = os.getenv("GEMINI_API")
PINECONE_API_KEY = os.getenv("PINECONE_API")

if not PINECONE_API_KEY:
    raise ValueError("❌ PINECONE_API_KEY is not set. Please check your environment variables.")


print("✅ Pinecone API Key loaded successfully!")
pc = Pinecone(api_key=PINECONE_API_KEY)


index_name = "chatbot"

print(f"🔍 Checking if Pinecone index '{index_name}' exists...")

if len(pc.list_indexes()):
    flag = True
    for index in pc.list_indexes():
        if index_name == index['name']:
            print("Index already exists")
            flag = False
            break
    if flag:
        print(f"🆕 Creating a new Pinecone index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=768,
            metric="cosine",  # Replace with your model metric
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
else:
    print(f"🆕 Creating a new Pinecone index: {index_name}")
    pc.create_index(
        name=index_name,
        dimension=768,
        metric="cosine",  # Replace with your model metric
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

index = pc.Index(index_name)


from langchain.document_loaders import PyPDFLoader, DirectoryLoader

# Load text files
folder_path = "/home/shtlp_0101/Documents/Project-Based_on_RAG-LLM_model/scraped_city_data"
print(f"📂 Loading text files from: {folder_path}")
text_documents = []



 
 
#Extract Data From the PDF File
def load_txt_file(data):
    loader= DirectoryLoader(data,
                            glob="*.txt",
                            loader_cls=TextLoader)
 
    documents=loader.load()
 
    return documents
 
 
extracted_data = load_txt_file(folder_path)
 
#Split the Data into Text Chunks
def text_split(extracted_data):
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    text_chunks=text_splitter.split_documents(extracted_data)
    return text_chunks
 
 
text_chunks = text_split(extracted_data)



from langchain_pinecone import PineconeVectorStore

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY  # Explicitly set the API key
# Correcting the embeddings initialization
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GEMINI_API"),)

# Upload documents to Pinecone
print("📤 Uploading documents to Pinecone...")
docsearch = PineconeVectorStore.from_documents(
    documents=text_chunks,  
    index_name=index_name,
    embedding=embeddings  # No parentheses here
)
print("✅ Documents stored in Pinecone!")
