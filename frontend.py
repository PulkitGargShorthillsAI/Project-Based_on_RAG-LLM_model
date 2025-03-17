import streamlit as st
import csv
from rag_pipeline import chatbot

def get_rag_response(user_input: str) -> str:
    """
    Takes user input, retrieves relevant documents using the RAG chain,
    and returns the generated response.
    """
    response = chatbot.ask_question(user_input)
    return response["answer"]

def log_interaction(question: str, answer: str):
    """Logs the user query and response in both a text file and a CSV file."""
    with open("logging/log_chatbot.txt", "a") as txt_file:
        txt_file.write(f"Q: {question}\nA: {answer}\n{'-'*40}\n")
    
    with open("logging/log_chatbot.csv", "a", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([question, answer])

def load_chat_history():
    """Loads previous chat history from the log file."""
    history = []
    try:
        with open("logging/log_chatbot.csv", "r") as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                if len(row) == 2:
                    history.append({"question": row[0], "answer": row[1]})
    except FileNotFoundError:
        pass
    return history

st.title("GlobeGuide AI")

chat_history = load_chat_history()

# Display previous chat history
st.subheader("Chat History")
for chat in chat_history:
    with st.expander(f"Q: {chat['question']}"):
        st.write(f"**A:** {chat['answer']}")

# User input
user_query = st.text_input("Ask me anything:")

if st.button("Submit") and user_query:
    answer = get_rag_response(user_query)
    st.write("**Answer:**", answer)
    
    # Log question and answer
    log_interaction(user_query, answer)
    
    # Refresh chat history
    chat_history.append({"question": user_query, "answer": answer})
