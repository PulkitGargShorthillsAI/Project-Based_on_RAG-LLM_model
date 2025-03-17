import os
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

class ChatbotRAG:
    def __init__(self, index_name: str):
        load_dotenv()
        self.gemini_api_key = os.getenv("GEMINI_API_PGARG")
        self.pinecone_api_key = os.getenv("PINECONE_API")
        os.environ["PINECONE_API_KEY"] = self.pinecone_api_key
        
        self.index_name = index_name
        self.embeddings = self._initialize_embeddings()
        self.retriever = self._initialize_retriever()
        self.llm = self._initialize_llm()
        self.rag_chain = self._initialize_rag_chain()
        print("Chatbot initialized successfully!")
    
    def _initialize_embeddings(self):
        return GoogleGenerativeAIEmbeddings(
            model="models/embedding-001", 
            google_api_key=self.gemini_api_key
        )
    
    def _initialize_retriever(self):
        docsearch = PineconeVectorStore.from_existing_index(
            index_name=self.index_name,
            embedding=self.embeddings
        )
        return docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    
    def _initialize_llm(self):
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            api_key=self.gemini_api_key
        )
    
    def _initialize_rag_chain(self):
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
    
    def ask_question(self, question: str):
        return self.rag_chain.invoke({"input": question})

chatbot = ChatbotRAG(index_name="chatbot")
