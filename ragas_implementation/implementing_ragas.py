import json
import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from ragas import EvaluationDataset, evaluate
from ragas.metrics import (
    LLMContextRecall, Faithfulness, SemanticSimilarity, AnswerCorrectness
)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper


# ------------------------------- Logging Setup ------------------------------- #
LOG_FILE = "ragas_implementation/log_queries2.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")


def write_log(message, error=False):
    """Writes log messages with timestamps. Errors are marked separately."""
    log_type = "ERROR" if error else "INFO"
    logging.log(logging.ERROR if error else logging.INFO, message)


# ------------------------------- Chatbot RAG Class ------------------------------- #
class ChatbotRAG:
    """Implements a Retrieval-Augmented Generation (RAG) chatbot using LangChain & Pinecone."""
    
    def __init__(self, index_name: str):
        try:
            load_dotenv()
            self.gemini_api_key = os.getenv("GEMINI_API3")
            self.pinecone_api_key = os.getenv("PINECONE_API")
            os.environ["PINECONE_API_KEY"] = self.pinecone_api_key

            if not self.gemini_api_key or not self.pinecone_api_key:
                raise ValueError("API keys are missing. Check your .env file.")

            self.index_name = index_name
            self.embeddings = self._initialize_embeddings()
            self.retriever = self._initialize_retriever()
            self.llm = self._initialize_llm()
            self.rag_chain = self._initialize_rag_chain()
            
            write_log("Chatbot initialized successfully!")
        except Exception as e:
            write_log(f"Error initializing chatbot: {str(e)}", error=True)
            raise e

    def _initialize_embeddings(self):
        """Initializes Google Generative AI embeddings."""
        try:
            return GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=self.gemini_api_key
            )
        except Exception as e:
            write_log(f"Error initializing embeddings: {str(e)}", error=True)
            raise e

    def _initialize_retriever(self):
        """Initializes the Pinecone retriever for document search."""
        try:
            docsearch = PineconeVectorStore.from_existing_index(
                index_name=self.index_name,
                embedding=self.embeddings
            )
            return docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        except Exception as e:
            write_log(f"Error initializing retriever: {str(e)}", error=True)
            raise e

    def _initialize_llm(self):
        """Initializes the Gemini model for response generation."""
        try:
            return ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                api_key=self.gemini_api_key
            )
        except Exception as e:
            write_log(f"Error initializing LLM: {str(e)}", error=True)
            raise e

    def _initialize_rag_chain(self):
        """Creates the RAG retrieval chain."""
        try:
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
        except Exception as e:
            write_log(f"Error initializing RAG chain: {str(e)}", error=True)
            raise e

    def ask_question(self, question: str):
        """Processes user queries using the RAG pipeline."""
        try:
            if not question.strip():
                raise ValueError("Question cannot be empty.")

            response = self.rag_chain.invoke({"input": question})
            return response
        except Exception as e:
            write_log(f"Error processing question '{question}': {str(e)}", error=True)
            return "An error occurred while processing your question."


# ------------------------------- RAGAS Evaluation Class ------------------------------- #
class RagasEvaluator:
    """Handles the evaluation of RAG responses using the RAGAS framework."""
    
    def __init__(self, chatbot: ChatbotRAG, json_file: str, csv_file: str):
        self.chatbot = chatbot
        self.json_file = json_file
        self.csv_file = csv_file
        self.evaluation_results = self._load_existing_results()

    def _load_existing_results(self):
        """Loads the existing evaluation results from a JSON file."""
        if os.path.exists(self.json_file):
            with open(self.json_file, "r") as file:
                return json.load(file)
        return []

    def _replace_nan(self, value):
        """Replaces NaN values with 'N/A'."""
        return "N/A" if isinstance(value, (float, np.float32, np.float64)) and np.isnan(value) else value

    def evaluate_ragas(self):
        """Performs evaluation on chatbot responses using RAGAS."""
        df = pd.read_csv(self.csv_file)

        for index, row in df.iterrows():
            if index < len(self.evaluation_results):
                continue

            query = row[0]
            reference = row[1]
            response = row[2]

            dataset = []
            relevant_docs = self.chatbot.retriever.invoke(query)
            dataset.append({
                "user_input": query,
                "retrieved_contexts": [rdoc.page_content for rdoc in relevant_docs],
                "response": response,
                "reference": reference,
            })

            evaluation_dataset = EvaluationDataset.from_list(dataset)
            eval_llm = self.chatbot.llm
            evaluator_llm = LangchainLLMWrapper(eval_llm)
            embeddings = LangchainEmbeddingsWrapper(self.chatbot.embeddings)

            result = evaluate(
                dataset=evaluation_dataset,
                embeddings=embeddings,
                metrics=[LLMContextRecall(), Faithfulness(), SemanticSimilarity(), AnswerCorrectness()],
                llm=evaluator_llm,
            )

            eval_scores = [{
                "context_recall": self._replace_nan(score.get("context_recall", 0)),
                "faithfulness": self._replace_nan(score.get("faithfulness", 0)),
                "semantic_similarity": self._replace_nan(score.get("semantic_similarity", 0)),
                "answer_correctness": self._replace_nan(score.get("answer_correctness", 0))
            } for score in result.scores]

            for item, score in zip(dataset, eval_scores):
                item["evaluation_result"] = score
                self.evaluation_results.append({'question': query, 'eval': item['evaluation_result']})

            with open(self.json_file, 'w') as f:
                json.dump(self.evaluation_results, f, indent=4)

        write_log("RAGAS evaluation completed successfully!")


# ------------------------------- Main Execution ------------------------------- #
if __name__ == "__main__":
    try:
        chatbot = ChatbotRAG(index_name="chatbot4")
        evaluator = RagasEvaluator(chatbot, json_file="ragas_implementation/log_queries2.json", csv_file="ragas_implementation/log_queries2.csv")
        evaluator.evaluate_ragas()
    except Exception as main_error:
        write_log(f"Unhandled error in main execution: {str(main_error)}", error=True)
        raise main_error
