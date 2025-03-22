import unittest
from unittest.mock import Mock,patch, MagicMock
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from rag_pipeline import ChatbotRAG

class TestChatbotRAG(unittest.TestCase):
    def setUp(self):
        self.chatbot = ChatbotRAG(index_name="chatbot")

    @patch("rag_pipeline.load_dotenv")
    @patch("rag_pipeline.GoogleGenerativeAIEmbeddings")
    @patch("rag_pipeline.PineconeVectorStore")
    @patch("rag_pipeline.ChatGoogleGenerativeAI")
    @patch("rag_pipeline.create_retrieval_chain")
    @patch("rag_pipeline.create_stuff_documents_chain")
    def setUp(self, mock_create_stuff, mock_create_retrieval, mock_chat_llm, mock_pinecone, mock_embeddings, mock_load_dotenv):
        """Setup mocks for API keys and components"""
        os.environ["GEMINI_API_PGARG"] = "test_gemini_api_key"
        os.environ["PINECONE_API"] = "test_pinecone_api_key"
        
        # Mock embeddings
        mock_embeddings_instance = MagicMock()
        mock_embeddings.return_value = mock_embeddings_instance
        
        # Mock Pinecone retriever
        mock_pinecone_instance = MagicMock()
        mock_pinecone.from_existing_index.return_value = mock_pinecone_instance
        mock_pinecone_instance.as_retriever.return_value = mock_pinecone_instance
        
        # Mock Chat model
        mock_chat_instance = MagicMock()
        mock_chat_llm.return_value = mock_chat_instance
        
        # Mock RAG Chain
        mock_create_stuff.return_value = "mock_stuff_chain"
        mock_create_retrieval.return_value = "mock_rag_chain"
        
        self.chatbot = ChatbotRAG(index_name="test_index")

    def test_initialization_success(self):
        """Test that the chatbot initializes successfully"""
        self.assertIsNotNone(self.chatbot.embeddings)
        self.assertIsNotNone(self.chatbot.retriever)
        self.assertIsNotNone(self.chatbot.llm)
        self.assertIsNotNone(self.chatbot.rag_chain)

    @patch("rag_pipeline.GoogleGenerativeAIEmbeddings", side_effect=Exception("Embeddings error"))
    def test_initialize_embeddings_failure(self, mock_embeddings):
        """Test that an error during embeddings initialization is handled"""
        with self.assertRaises(Exception) as context:
            ChatbotRAG(index_name="test_index")
        self.assertIn("Embeddings error", str(context.exception))

    @patch("rag_pipeline.PineconeVectorStore.from_existing_index", side_effect=Exception("Pinecone error"))
    def test_initialize_retriever_failure(self, mock_pinecone):
        """Test that an error during retriever initialization is handled"""
        with self.assertRaises(Exception) as context:
            ChatbotRAG(index_name="test_index")
        self.assertIn("Pinecone error", str(context.exception))
    
    @patch("rag_pipeline.ChatGoogleGenerativeAI", side_effect=Exception("LLM error"))
    def test_initialize_llm_failure(self, mock_chat_llm):
        """Test that an error during LLM initialization is handled"""
        with self.assertRaises(Exception) as context:
            ChatbotRAG(index_name="test_index")
        self.assertIn("Unauthorized", str(context.exception))

    
    @patch("rag_pipeline.create_retrieval_chain", side_effect=Exception("RAG Chain error"))
    def test_initialize_rag_chain_failure(self, mock_create_retrieval):
        """Test that an error during RAG chain initialization is handled"""
        with self.assertRaises(Exception) as context:
            ChatbotRAG(index_name="test_index")
        self.assertIn("Invalid API Key", str(context.exception))

    
    def test_ask_question_success(self):
        """Test chatbot response handling with a valid question"""
        self.chatbot.rag_chain = Mock()
        self.chatbot.rag_chain.invoke.return_value = "Test response"

        response = self.chatbot.ask_question("What is AI?")
        self.assertEqual(response, "Test response")
    
    def test_ask_question_empty_input(self):
        """Test chatbot handling of empty question input"""
        response = self.chatbot.ask_question("")
        self.assertEqual(response, "An error occurred while processing your question.")
    
    @patch("rag_pipeline.ChatbotRAG.ask_question", side_effect=Exception("Processing error"))
    def test_ask_question_failure(self, mock_ask_question):
        """Test that chatbot handles question processing errors properly"""
        with self.assertRaises(Exception) as context:
            self.chatbot.ask_question("What is AI?")

        self.assertEqual(str(context.exception), "Processing error")


if __name__ == "__main__":
    unittest.main()