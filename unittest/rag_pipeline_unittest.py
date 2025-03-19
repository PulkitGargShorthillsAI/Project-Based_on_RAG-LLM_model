import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rag_pipeline import ChatbotRAG


class TestChatbotRAG(unittest.TestCase):
    @patch("rag_pipeline.GoogleGenerativeAIEmbeddings")
    @patch("rag_pipeline.PineconeVectorStore.from_existing_index")
    @patch("rag_pipeline.ChatGoogleGenerativeAI")
    def setUp(self, MockLLM, MockPineconeVectorStore, MockEmbeddings):
        self.mock_embeddings = MockEmbeddings.return_value
        self.mock_retriever = MockPineconeVectorStore.return_value.as_retriever.return_value
        self.mock_llm = MockLLM.return_value

        self.chatbot = ChatbotRAG(index_name="test_index")
        
        MockEmbeddings.assert_called_once()
        MockPineconeVectorStore.assert_called_once_with(index_name="test_index", embedding=self.mock_embeddings)
        MockLLM.assert_called_once()
    
    def test_initialize_rag_chain(self):
        self.assertIsNotNone(self.chatbot.rag_chain)
    
    @patch("rag_pipeline.ChatbotRAG.ask_question")
    def test_ask_question(self, MockAskQuestion):
        MockAskQuestion.return_value = "This is a test answer."
        response = self.chatbot.ask_question("What is LangChain?")
        self.assertEqual(response, "This is a test answer.")
        MockAskQuestion.assert_called_once_with("What is LangChain?")

if __name__ == "__main__":
    unittest.main()