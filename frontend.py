import streamlit as st
import csv
from rag_pipeline import rag_chain

def get_rag_response(user_input: str) -> str:
    """
    Takes user input, retrieves relevant documents using the RAG chain,
    and returns the generated response.
    """
    response = rag_chain.invoke({"input": user_input})
    return response["answer"]

def log_interaction(question: str, answer: str):
    """Logs the user query and response in both a text file and a CSV file."""
    with open("log.txt", "a") as txt_file:
        txt_file.write(f"Q: {question}\nA: {answer}\n{'-'*40}\n")
    
    with open("log.csv", "a", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([question, answer])

st.title("Chatbot with RAG")

user_query = st.text_input("Ask me anything:")

if st.button("Submit") and user_query:
    answer = get_rag_response(user_query)
    st.write("**Answer:**", answer)
    
    # Log question and answer
    log_interaction(user_query, answer)
