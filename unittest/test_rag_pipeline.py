import unittest
from unittest.mock import patch, MagicMock
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from rag_pipeline import ChatbotRAG, write_log
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

class TestChatbotRAG(unittest.TestCase):

    @patch.dict(os.environ, {"GEMINI_API_PGARG": "test_gemini_key", "PINECONE_API": "test_pinecone_key"})
    @patch("rag_pipeline.PineconeVectorStore.from_existing_index")
    @patch("rag_pipeline.GoogleGenerativeAIEmbeddings")
    @patch("rag_pipeline.ChatGoogleGenerativeAI")
    @patch("rag_pipeline.create_retrieval_chain")
    @patch("rag_pipeline.create_stuff_documents_chain")
    def test_initialization_success(self, mock_create_stuff, mock_create_retrieval, mock_chat_llm, mock_embeddings, mock_vectorstore):
        mock_vectorstore.return_value.as_retriever.return_value = MagicMock()
        mock_chat_llm.return_value = MagicMock()
        mock_embeddings.return_value = MagicMock()
        mock_create_retrieval.return_value = MagicMock()
        mock_create_stuff.return_value = MagicMock()

        chatbot = ChatbotRAG(index_name="test_index")

        self.assertIsInstance(chatbot.embeddings, MagicMock)
        self.assertIsInstance(chatbot.retriever, MagicMock)
        self.assertIsInstance(chatbot.llm, MagicMock)
        self.assertIsInstance(chatbot.rag_chain, MagicMock)

    @patch.dict(os.environ, {"GEMINI_API_PGARG": "test_gemini_key", "PINECONE_API": "test_pinecone_key"})
    @patch("rag_pipeline.PineconeVectorStore.from_existing_index")
    @patch("rag_pipeline.GoogleGenerativeAIEmbeddings")
    @patch("rag_pipeline.ChatGoogleGenerativeAI")
    @patch("rag_pipeline.create_retrieval_chain")
    @patch("rag_pipeline.create_stuff_documents_chain")
    def test_initialization_failure_embeddings(self, mock_create_stuff, mock_create_retrieval, mock_chat_llm, mock_embeddings, mock_vectorstore):
        mock_embeddings.side_effect = Exception("Embeddings error")

        with self.assertRaises(Exception) as context:
            ChatbotRAG(index_name="test_index")
        self.assertEqual(str(context.exception), "Embeddings error")

    @patch.dict(os.environ, {"GEMINI_API_PGARG": "test_gemini_key", "PINECONE_API": "test_pinecone_key"})
    @patch("rag_pipeline.PineconeVectorStore.from_existing_index")
    @patch("rag_pipeline.GoogleGenerativeAIEmbeddings")
    @patch("rag_pipeline.ChatGoogleGenerativeAI")
    @patch("rag_pipeline.create_retrieval_chain")
    @patch("rag_pipeline.create_stuff_documents_chain")
    def test_initialization_failure_retriever(self, mock_create_stuff, mock_create_retrieval, mock_chat_llm, mock_embeddings, mock_vectorstore):
        mock_vectorstore.side_effect = Exception("Retriever error")

        with self.assertRaises(Exception) as context:
            ChatbotRAG(index_name="test_index")
        self.assertEqual(str(context.exception), "Retriever error")

    @patch.dict(os.environ, {"GEMINI_API_PGARG": "test_gemini_key", "PINECONE_API": "test_pinecone_key"})
    @patch("rag_pipeline.PineconeVectorStore.from_existing_index")
    @patch("rag_pipeline.GoogleGenerativeAIEmbeddings")
    @patch("rag_pipeline.ChatGoogleGenerativeAI")
    @patch("rag_pipeline.create_retrieval_chain")
    @patch("rag_pipeline.create_stuff_documents_chain")
    def test_initialization_failure_llm(self, mock_create_stuff, mock_create_retrieval, mock_chat_llm, mock_embeddings, mock_vectorstore):
        mock_chat_llm.side_effect = Exception("LLM error")

        with self.assertRaises(Exception) as context:
            ChatbotRAG(index_name="test_index")
        self.assertEqual(str(context.exception), "LLM error")

    @patch.dict(os.environ, {"GEMINI_API_PGARG": "test_gemini_key", "PINECONE_API": "test_pinecone_key"})
    @patch("rag_pipeline.PineconeVectorStore.from_existing_index")
    @patch("rag_pipeline.GoogleGenerativeAIEmbeddings")
    @patch("rag_pipeline.ChatGoogleGenerativeAI")
    @patch("rag_pipeline.create_retrieval_chain")
    @patch("rag_pipeline.create_stuff_documents_chain")
    def test_initialization_failure_rag_chain(self, mock_create_stuff, mock_create_retrieval, mock_chat_llm, mock_embeddings, mock_vectorstore):
        mock_create_retrieval.side_effect = Exception("RAG chain error")

        with self.assertRaises(Exception) as context:
            ChatbotRAG(index_name="test_index")
        self.assertEqual(str(context.exception), "RAG chain error")

    @patch.dict(os.environ, {"GEMINI_API_PGARG": "test_gemini_key", "PINECONE_API": "test_pinecone_key"})
    @patch("rag_pipeline.PineconeVectorStore.from_existing_index")
    @patch("rag_pipeline.GoogleGenerativeAIEmbeddings")
    @patch("rag_pipeline.ChatGoogleGenerativeAI")
    @patch("rag_pipeline.create_retrieval_chain")
    @patch("rag_pipeline.create_stuff_documents_chain")
    def test_ask_question_success(self, mock_create_stuff, mock_create_retrieval, mock_chat_llm, mock_embeddings, mock_vectorstore):
        mock_vectorstore.return_value.as_retriever.return_value = MagicMock()
        mock_chat_llm.return_value = MagicMock()
        mock_embeddings.return_value = MagicMock()
        mock_create_retrieval.return_value.invoke.return_value = {"answer": "Test Answer"}

        chatbot = ChatbotRAG(index_name="test_index")
        response = chatbot.ask_question("Test Question")

        self.assertEqual(response, {"answer": "Test Answer"})

    @patch.dict(os.environ, {"GEMINI_API_PGARG": "test_gemini_key", "PINECONE_API": "test_pinecone_key"})
    @patch("rag_pipeline.PineconeVectorStore.from_existing_index")
    @patch("rag_pipeline.GoogleGenerativeAIEmbeddings")
    @patch("rag_pipeline.ChatGoogleGenerativeAI")
    @patch("rag_pipeline.create_retrieval_chain")
    @patch("rag_pipeline.create_stuff_documents_chain")
    def test_ask_question_empty_question(self, mock_create_stuff, mock_create_retrieval, mock_chat_llm, mock_embeddings, mock_vectorstore):
        mock_vectorstore.return_value.as_retriever.return_value = MagicMock()
        mock_chat_llm.return_value = MagicMock()
        mock_embeddings.return_value = MagicMock()
        mock_create_retrieval.return_value = MagicMock()

        chatbot = ChatbotRAG(index_name="test_index")
        response = chatbot.ask_question("  ")

        self.assertEqual(response, "An error occurred while processing your question.")


if __name__ == '__main__':
    unittest.main()