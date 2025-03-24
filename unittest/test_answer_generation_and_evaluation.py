import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from answer_generation_and_evaluation import ChatbotEvaluator, write_log
import csv
import os
import torch

class TestChatbotEvaluator(unittest.TestCase):
    def setUp(self):
        self.evaluator = ChatbotEvaluator()
    
    @patch("answer_generation_and_evaluation.chatbot.ask_question", return_value={"answer": "Test answer"})
    def test_get_response_success(self, mock_chatbot):
        response = self.evaluator.get_response("What is AI?")
        self.assertEqual(response, "Test answer")
    
    @patch("answer_generation_and_evaluation.chatbot.ask_question", side_effect=Exception("Processing error"))
    def test_get_response_failure(self, mock_chatbot):
        response = self.evaluator.get_response("What is AI?")
        self.assertEqual(response, "Error: Unable to retrieve response.")
    
    @patch("answer_generation_and_evaluation.score", return_value=(
            torch.tensor([0.9]), 
            torch.tensor([0.85]), 
            torch.tensor([0.87]),
        )
    )
    def test_evaluate_response_success(self, mock_score):  # Accepts mock argument
        """Test if evaluate_response correctly calculates scores."""

        evaluator = ChatbotEvaluator()
        P, R, F1 = evaluator.evaluate_response("Generated answer", "Actual answer")

        # Allow small floating-point precision differences
        self.assertAlmostEqual(P, 0.9, places=4)
        self.assertAlmostEqual(R, 0.85, places=4)
        self.assertAlmostEqual(F1, 0.87, places=4)


    
    @patch("answer_generation_and_evaluation.score", side_effect=Exception("BERTScore error"))
    def test_evaluate_response_failure(self, mock_score):
        P, R, F1 = self.evaluator.evaluate_response("Test answer", "Actual answer")
        self.assertEqual((P, R, F1), (0.0, 0.0, 0.0))
    
    def test_log_interaction(self):
        log_file = "test_log_queries.log"
        log_csv = "test_log_queries.csv"
        self.evaluator.log_file = log_file
        self.evaluator.log_file_csv = log_csv
        
        self.evaluator.log_interaction("What is AI?", "Actual answer", "Test answer", 0.9, 0.85, 0.87,0.9)
        
        with open(log_file, "r") as file:
            content = file.read()
            self.assertIn("What is AI?", content)
        
        with open(log_csv, "r") as file:
            reader = csv.reader(file)
            rows = list(reader)
            self.assertEqual(rows[-1], ["What is AI?", "Actual answer", "Test answer", "0.9", "0.85", "0.87",'0.9'])
        
        os.remove(log_file)
        os.remove(log_csv)
    
    @patch("answer_generation_and_evaluation.context_questions", [{"question": "What is AI?", "answer": "Artificial Intelligence"}])
    @patch("answer_generation_and_evaluation.ChatbotEvaluator.get_response", return_value="Artificial Intelligence")
    @patch("answer_generation_and_evaluation.ChatbotEvaluator.evaluate_response", return_value=(0.9, 0.85, 0.87))
    @patch("answer_generation_and_evaluation.ChatbotEvaluator.log_interaction")
    def test_run_evaluation_success(self, mock_log, mock_evaluate, mock_get_response):
        self.evaluator.run_evaluation()
        mock_get_response.assert_called_once_with("What is AI?")
        mock_evaluate.assert_called_once_with("Artificial Intelligence", "Artificial Intelligence")
        mock_log.assert_called_once()
    
    @patch("answer_generation_and_evaluation.write_log")
    def test_write_log(self, mock_log):
        """Test if write_log is called correctly."""
        message = "Test log message"

        from answer_generation_and_evaluation import write_log
        write_log(message)
        mock_log.assert_called_with(message)


if __name__ == "__main__":
    unittest.main()