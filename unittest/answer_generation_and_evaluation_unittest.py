import unittest
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from answer_generation_and_evaluation import ChatbotEvaluator

class TestChatbotEvaluator(unittest.TestCase):
    
    @patch("answer_generation_and_evaluation.chatbot.ask_question")
    def setUp(self, MockAskQuestion):
        self.evaluator = ChatbotEvaluator()
        MockAskQuestion.return_value = {"answer": "Test generated response"}
    
    @patch("answer_generation_and_evaluation.chatbot.ask_question")
    def test_get_response(self, MockAskQuestion):
        MockAskQuestion.return_value = {"answer": "Sample response"}
        response = self.evaluator.get_response("What is AI?")
        self.assertEqual(response, "Sample response")
    
    @patch("answer_generation_and_evaluation.score")
    def test_evaluate_response(self, MockScore):
        MockScore.return_value = (MagicMock(), MagicMock(), MagicMock())
        MockScore.return_value[0].tolist.return_value = [0.9]
        MockScore.return_value[1].tolist.return_value = [0.85]
        MockScore.return_value[2].tolist.return_value = [0.88]
        
        P, R, F1 = self.evaluator.evaluate_response("Test response", "Actual answer")
        self.assertAlmostEqual(P, 0.9)
        self.assertAlmostEqual(R, 0.85)
        self.assertAlmostEqual(F1, 0.88)
    
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    @patch("csv.writer")
    def test_log_interaction(self, MockCSVWriter, MockOpen):
        self.evaluator.log_interaction("What is AI?", "Actual answer", "Generated response", 0.9, 0.85, 0.88)
        MockOpen.assert_called()
        MockCSVWriter.assert_called()
    
if __name__ == "__main__":
    unittest.main()
