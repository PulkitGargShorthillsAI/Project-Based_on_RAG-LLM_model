from pinecone import Pinecone, ServerlessSpec
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pinecone import ServerlessSpec, Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader

from dotenv import load_dotenv
load_dotenv()

print("🔄 Loading environment variables...")
GEMINI_API = os.getenv("GEMINI_API")
PINECONE_API_KEY = os.getenv("PINECONE_API")

if not PINECONE_API_KEY:
    raise ValueError("❌ PINECONE_API_KEY is not set. Please check your environment variables.")

# Initialize Pinecone
print("✅ Pinecone API Key loaded successfully!")
pc = Pinecone(api_key=PINECONE_API_KEY)

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY  # Explicitly set the API key

# Create or connect to an index
index_name = "quickstart1"
print(f"🔍 Checking if Pinecone index '{index_name}' exists...")

if index_name not in pc.list_indexes():
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
    print(f"✅ Pinecone index '{index_name}' already exists!")

index = pc.Index(index_name)

# Initialize Gemini embeddings
# print("🔄 Initializing Gemini embeddings...")
# embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=GEMINI_API)
# print("✅ Gemini embeddings initialized!")

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
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    text_chunks=text_splitter.split_documents(extracted_data)
    return text_chunks
 
 
text_chunks = text_split(extracted_data)
#Download the Embeddings from HuggingFace
def embeddings():
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API)
    return embeddings
 
docsearch = PineconeVectorStore.from_documents(
    documents=text_chunks,
    index_name=index_name,
    embedding=embeddings(),
)
 
 
 
# Embed each chunk and upsert the embeddings into your Pinecone index.
docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings()
)
 
retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k":3})
 
 
 







# for file in os.listdir(folder_path):
#     if file.endswith(".txt"):
#         print(f"📄 Processing file: {file}")
#         loader = TextLoader(os.path.join(folder_path, file), encoding="utf-8")
#         text_documents.extend(loader.load())

# print(f"✅ Loaded {len(text_documents)} documents!")

# # Split text into chunks
# print("🔄 Splitting text into chunks...")
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
# chunks = text_splitter.split_documents(text_documents)
# print(f"✅ Text split into {len(chunks)} chunks!")

# # Generate embeddings for each chunk
# print("🔄 Generating embeddings for text chunks...")
# chunk_texts = [chunk.page_content for chunk in chunks]
# chunk_embeddings = embeddings.embed_documents(chunk_texts)  # Returns a list of vectors
# print(f"✅ Generated {len(chunk_embeddings)} embeddings!")

# # Check embedding size
# print(f"🧐 Checking embedding dimensions...")
# embedding_dim = len(chunk_embeddings[0])
# print(f"📏 Embedding dimension: {embedding_dim} (Expected: 768)")
# assert embedding_dim == 768, "❌ Embedding dimension mismatch! Expected 768."

# # Prepare vectors for uploading
# print("📤 Preparing vectors for Pinecone...")
# vectors = [
#     (str(i), chunk_embeddings[i], {"text": chunk_texts[i]})  # (id, embedding, metadata)
#     for i in range(len(chunk_embeddings))
# ]
# print(f"✅ Prepared {len(vectors)} vectors!")

# # Upsert the vectors into Pinecone
# print("🚀 Uploading vectors to Pinecone...")
# index.upsert(vectors)
# print("🎉 ✅ Vectorized data uploaded to Pinecone successfully!")
