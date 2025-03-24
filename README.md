# 🌍 GlobeGuide AI - Intelligent Travel Assistant

GlobeGuide AI is an advanced travel assistant chatbot that leverages Retrieval-Augmented Generation (RAG) to provide users with accurate and up-to-date travel information for locations worldwide. The chatbot processes user queries, retrieves relevant information from a structured knowledge base, and generates concise, informative responses.

---

## 🎯 Key Features
- **RAG-Powered Responses**: Retrieves the most relevant travel information using Pinecone vector storage and LangChain.
- **Integration with Gemini AI**: Utilizes Google’s Gemini models for natural language understanding and text generation.
- **Multi-Language Support**: Handles queries in multiple languages for a global user base.
- **Efficient Query Handling**: Ensures quick response times using optimized retrieval and generation pipelines.
- **Interactive Chat History**: Logs interactions for user reference and continuous improvement.

---

## 🎯 Objectives
- Provide instant and reliable travel-related information.
- Improve user experience through context-aware responses.
- Integrate with APIs for real-time travel updates.
- Optimize retrieval processes for faster responses.

---

## 👨‍💻 Architecture Diagram
1. User enters a travel-related query in the chatbot.
2. The chatbot processes the input and retrieves relevant data from Pinecone vector storage.
3. The RAG pipeline generates a response using Gemini AI.
4. The chatbot presents the final response to the user in an interactive UI.
5. The query and response are logged for future reference.

![Screenshot from 2025-03-17 15-12-02](https://github.com/user-attachments/assets/6a64d39c-259c-427a-91d1-c966c5c96a1e)


---

## 💡 Technologies Used
- **Python** – Primary programming language.
- **LangChain** – Used for building the RAG pipeline.
- **Pinecone** – Vector database for efficient retrieval.
- **Google Gemini AI** – For embedding generation and response formulation.
- **Streamlit** – Provides an intuitive frontend for user interaction.
- **CSV/Excel Logging** – Maintains a record of user queries and responses.

---

## 📊 Evaluation Parameters  

GlobeGuide AI evaluates chatbot performance using **BERTScore**, **NLI-based Similarity**, and **Cosine Similarity** to compare the generated responses with expected answers.  

### **1️⃣ BERTScore Metrics**
- **Precision (P)**: Measures how many relevant words from the actual answer are present in the generated response.  
- **Recall (R)**: Measures how many words from the generated response match the actual answer.  
- **F1-Score**: The harmonic mean of Precision and Recall, providing an overall effectiveness score.  

### **2️⃣ NLI-Based Similarity**  
Natural Language Inference (NLI) helps determine the relationship between the expected and generated answers:  
- **Entailment**: The generated response strongly supports the expected answer.  
- **Contradiction**: The generated response contradicts the expected answer.  
- **Neutrality**: The generated response is neither supporting nor contradicting the expected answer.  

### **3️⃣ Cosine Similarity**  
- Measures the semantic similarity between the generated and expected answers by comparing their vector representations.  
- Helps understand how closely the generated response matches the expected answer in meaning.  

These evaluation metrics help fine-tune GlobeGuide AI, improving accuracy, relevance, and overall chatbot performance. 🚀  



---

## 🖼️ UI Screenshots
![chatbot_UI](https://github.com/user-attachments/assets/7565ab1c-20ae-41b7-9485-2b2be29b0867)



---

## 💡 Test Cases
Detailed test case documentation: [Test Cases](https://shorthillstech-my.sharepoint.com/:x:/g/personal/pulkit_garg_shorthills_ai/EWi7LXBJ0IpDljKzxS5tWOYBcMAvU0rk6yXucC2alHlLjw?e=0htaxT)

---

## 💡 Future Enhancements
- **Summarization with Chains**: Implement OpenAI's GPT-4-Turbo or LangChain summarization chains for handling longer context.
- **Real-Time Travel Alerts**: Integrate APIs for live updates on weather, flights, and accommodations.
- **Voice & Image Recognition**: Incorporate Whisper AI for voice inputs and image-based location detection.
- **Multi-Platform Deployment**: Extend chatbot support to mobile applications and social media platforms.

---

GlobeGuide AI aims to revolutionize travel assistance by providing users with instant, AI-powered insights into any destination worldwide! 🌍✈️

