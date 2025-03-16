from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from questions_list import context_questions
import csv
import time
import os
from dotenv import load_dotenv
from bert_score import score

load_dotenv()


GEMINI_API = os.getenv("GEMINI_API_PGARG")
# GEMINI_API = os.getenv("GEMINI_API")
PINECONE_API_KEY = os.getenv("PINECONE_API")


index_name = "chatbot"
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001", 
    google_api_key=os.getenv("GEMINI_API"),
)

docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
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



def log_interaction(question: str, answer: str,generated_answer:str,P,R,F1):
    """Logs the user query and response in both a text file and a CSV file."""
    with open("log_queries.txt", "a") as txt_file:
        txt_file.write(f"Q: {question}\nActual answer: {answer}\nA: {generated_answer}\nP: {P}\nR: {R}\nF1: {F1}\n{'-'*40}\n")
    
    with open("log_queries.csv", "a", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([question, answer, generated_answer,P,R,F1])

    
for question in context_questions:
    response = rag_chain.invoke({"input": question['question']})
    time.sleep(6)
    P, R, F1 = score([response['answer']], [question['answer']], lang="en", rescale_with_baseline=True)
    log_interaction(question['question'],question['answer'],response['answer'],P.tolist()[0],R.tolist()[0],F1.tolist()[0])
