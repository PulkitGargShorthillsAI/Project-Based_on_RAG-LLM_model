import streamlit as st
import csv
from rag_pipeline import chatbot
from datetime import datetime

# Function to get response from the RAG pipeline
def get_rag_response(user_input: str) -> str:
    response = chatbot.ask_question(user_input)
    return response["answer"]

# Function to log interaction
def log_interaction(question: str, answer: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("logging/log_chatbot.log", "a") as txt_file:
        txt_file.write(f"{timestamp}\nQ: {question}\nA: {answer}\n{'-'*40}\n")

    with open("logging/log_chatbot.csv", "a", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([question, answer])

# Function to load chat history
def load_chat_history():
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

# Streamlit UI
st.set_page_config(page_title="GlobeGuide AI", page_icon="🌍", layout="wide")

st.markdown("<h1 style='text-align: center; color: #4CAF50;'>GlobeGuide AI 🌍</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Your AI-powered travel assistant</p>", unsafe_allow_html=True)

# Sidebar with chat history
with st.sidebar:
    st.subheader("📜 Chat History")
    chat_history = load_chat_history()
    for chat in chat_history[::-1]:  # Show latest first
        with st.expander(f"🔹 {chat['question']}"):
            st.write(f"**Answer:** {chat['answer']}")

# Chat interface
st.subheader("💬 Ask your travel questions")

# User input field
user_query = st.text_area("Type your question here:", height=100, placeholder="e.g., What are the best places to visit in Paris?")

if st.button("Submit"):
    if user_query.strip():
        with st.spinner("Thinking... 🤔"):
            answer = get_rag_response(user_query)

        # Display chat message
        with st.chat_message("user"):
            st.write(user_query)

        with st.chat_message("assistant"):
            st.write(answer)

        # Log the interaction
        log_interaction(user_query, answer)
    else:
        st.warning("Please enter a question before submitting.")
