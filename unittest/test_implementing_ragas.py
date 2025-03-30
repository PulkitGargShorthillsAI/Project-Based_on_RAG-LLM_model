import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
import pandas as pd
import numpy as np
from ragas_implementation_on_general_set.implementing_ragas import ChatbotRAG, RagasEvaluator

class TestChatbotRAG(unittest.TestCase):

    @patch.dict(os.environ, {"GEMINI_API1": "fake_gemini_key", "PINECONE_API": "fake_pinecone_key"})
    @patch("ragas_implementation_on_general_set.implementing_ragas.GoogleGenerativeAIEmbeddings")
    @patch("ragas_implementation_on_general_set.implementing_ragas.PineconeVectorStore")
    @patch("ragas_implementation_on_general_set.implementing_ragas.ChatGoogleGenerativeAI")
    def setUp(self, mock_llm, mock_pinecone, mock_embeddings):
        self.mock_llm = mock_llm
        self.mock_pinecone = mock_pinecone
        self.mock_embeddings = mock_embeddings
        
        self.mock_retriever = MagicMock()
        mock_pinecone.from_existing_index.return_value.as_retriever.return_value = self.mock_retriever

        self.chatbot = ChatbotRAG(index_name="test_index")
        self.chatbot.rag_chain = MagicMock()


    def test_chatbot_initialization(self):
        """Test chatbot initializes with correct components."""
        self.assertIsNotNone(self.chatbot.embeddings)
        self.assertIsNotNone(self.chatbot.retriever)
        self.assertIsNotNone(self.chatbot.llm)
        self.assertIsNotNone(self.chatbot.rag_chain)

    @patch.object(ChatbotRAG, 'rag_chain')
    def test_ask_question_valid(self, mock_rag_chain):
        """Test chatbot response to a valid question."""
        mock_rag_chain.invoke.return_value = {"output": "Mock response"}
        response = self.chatbot.ask_question("What is AI?")
        self.assertEqual(response, {"output": "Mock response"})

    def test_ask_question_empty(self):
        """Test chatbot handles empty question properly."""
        response = self.chatbot.ask_question("")
        self.assertEqual(response, "An error occurred while processing your question.")


class TestRagasEvaluator(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data="[]")
    @patch("os.path.exists", return_value=True)
    @patch("pandas.read_csv")
    def setUp(self, mock_read_csv, mock_exists, mock_file):
        """Setup mock RagasEvaluator instance."""
        self.mock_chatbot = MagicMock()
        self.mock_chatbot.retriever.invoke.return_value = [MagicMock(page_content="Mock document")]

        # Ensure a non-empty DataFrame is returned
        mock_read_csv.return_value = pd.DataFrame({
            0: ["What is AI?"], 
            1: ["Artificial Intelligence is the simulation of human intelligence."], 
            2: ["AI is the ability of a machine to perform tasks."]
        })

        self.evaluator = RagasEvaluator(
            chatbot=self.mock_chatbot,
            json_file="test_log.json",
            csv_file="test_queries.csv"
        )

    def test_load_existing_results(self):
        """Test loading existing evaluation results from JSON file."""
        self.assertEqual(self.evaluator.evaluation_results, [])

    @patch("ragas_implementation_on_general_set.implementing_ragas.EvaluationDataset.from_list")
    @patch("ragas_implementation_on_general_set.implementing_ragas.evaluate")
    @patch("builtins.open", new_callable=mock_open)
    def test_evaluate_ragas(self, mock_file, mock_evaluate, mock_from_list):
        """Test evaluation process."""
        mock_evaluate.return_value.scores = [{"context_recall": 0.9, "faithfulness": 0.85, "semantic_similarity": 0.88, "answer_correctness": 0.9}]

        self.evaluator.evaluate_ragas()

        # Ensure evaluation results are stored correctly
        self.assertGreater(len(self.evaluator.evaluation_results), 0)
        self.assertIn("question", self.evaluator.evaluation_results[0])
        self.assertIn("eval", self.evaluator.evaluation_results[0])

        # Ensure JSON file is written
        mock_file().write.assert_called()


if __name__ == "__main__":
    unittest.main()
