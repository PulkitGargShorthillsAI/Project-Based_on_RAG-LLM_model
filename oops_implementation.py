import os
import time
import csv
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain, create_stuff_documents_chain
from bert_score import score
import streamlit as st
from questions_list import context_questions

load_dotenv()

class PineconeManager:
    def __init__(self, index_name="chatbot"):
        self.index_name = index_name
        self.api_key = os.getenv("PINECONE_API")
        if not self.api_key:
            raise ValueError("❌ PINECONE_API_KEY is not set.")
        self.pc = Pinecone(api_key=self.api_key)
        self._initialize_index()

    def _initialize_index(self):
        if not any(index['name'] == self.index_name for index in self.pc.list_indexes()):
            print(f"🆕 Creating Pinecone index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name, dimension=768, metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
        self.index = self.pc.Index(self.index_name)

class DocumentProcessor:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.text_chunks = self._load_and_split_documents()

    def _load_and_split_documents(self):
        loader = DirectoryLoader(self.folder_path, glob="*.txt", loader_cls=TextLoader)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        return text_splitter.split_documents(documents)

class VectorStoreManager:
    def __init__(self, index_name, text_chunks):
        self.index_name = index_name
        self.text_chunks = text_chunks
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GEMINI_API"))
        self._store_documents()

    def _store_documents(self):
        PineconeVectorStore.from_documents(documents=self.text_chunks, index_name=self.index_name, embedding=self.embeddings)
        print("✅ Documents stored in Pinecone!")

class RAGPipeline:
    def __init__(self, index_name):
        self.index_name = index_name
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GEMINI_API"))
        self.docsearch = PineconeVectorStore.from_existing_index(index_name=index_name, embedding=self.embeddings)
        self.retriever = self.docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=os.getenv("GEMINI_API"))
        self._initialize_chain()
    
    def _initialize_chain(self):
        system_prompt = """
        You are an assistant for question-answering tasks. 
        Use the retrieved context to answer the question concisely.
        """
        prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", "{input}")])
        question_answer_chain = create_stuff_documents_chain(self.llm, prompt)
        self.rag_chain = create_retrieval_chain(self.retriever, question_answer_chain)

    def get_response(self, query):
        return self.rag_chain.invoke({"input": query})["answer"]

class Logger:
    @staticmethod
    def log_interaction(question, actual_answer, generated_answer, P, R, F1):
        with open("log_queries.txt", "a") as txt_file:
            txt_file.write(f"Q: {question}\nActual answer: {actual_answer}\nA: {generated_answer}\nP: {P}\nR: {R}\nF1: {F1}\n{'-'*40}\n")
        with open("log_queries.csv", "a", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([question, actual_answer, generated_answer, P, R, F1])

class ChatbotFrontend:
    def __init__(self, rag_pipeline):
        self.rag_pipeline = rag_pipeline
        st.title("Chatbot with RAG")
        self.run()
    
    def run(self):
        user_query = st.text_input("Ask me anything:")
        if st.button("Submit") and user_query:
            answer = self.rag_pipeline.get_response(user_query)
            st.write("**Answer:**", answer)
            Logger.log_interaction(user_query, "N/A", answer, "N/A", "N/A", "N/A")

if __name__ == "__main__":
    index_name = "chatbot"
    folder_path = "/home/shtlp_0101/Documents/Project-Based_on_RAG-LLM_model/scraped_city_data"
    
    PineconeManager(index_name)
    text_processor = DocumentProcessor(folder_path)
    VectorStoreManager(index_name, text_processor.text_chunks)
    rag_pipeline = RAGPipeline(index_name)
    
    for question in context_questions:
        generated_answer = rag_pipeline.get_response(question['question'])
        time.sleep(6)
        P, R, F1 = score([generated_answer], [question['answer']], lang="en", rescale_with_baseline=True)
        Logger.log_interaction(question['question'], question['answer'], generated_answer, P.tolist()[0], R.tolist()[0], F1.tolist()[0])
    
    ChatbotFrontend(rag_pipeline)
