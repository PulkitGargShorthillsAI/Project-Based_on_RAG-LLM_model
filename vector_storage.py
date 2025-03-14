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

for index in pc.list_indexes():
    if index_name == index['name']:
        print("Index already exists")
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
embeddings1 = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GEMINI_API"))

# Upload documents to Pinecone
# print("📤 Uploading documents to Pinecone...")
# docsearch = PineconeVectorStore.from_documents(
#     documents=text_chunks,  
#     index_name=index_name,
#     embedding=embeddings  # No parentheses here
# )
# print("✅ Documents stored in Pinecone!")

docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings1
)

# Initialize retriever
retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})
print("🔍 Retriever initialized successfully!")



llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    api_key=GEMINI_API
)



system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use three sentences maximum and keep the "
    "answer concise."
    "\n\n"
    "{context}"
)


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)


question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)



response = rag_chain.invoke({"input": "famous places in delhi?"})
print(response["answer"])