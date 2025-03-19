import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from frontend import get_rag_response, log_interaction, load_chat_history

class TestStreamlitChatbot(unittest.TestCase):
    
    @patch("frontend.chatbot.ask_question")
    def test_get_rag_response(self, MockAskQuestion):
        MockAskQuestion.return_value = {"answer": "Sample response"}
        response = get_rag_response("What is AI?")
        self.assertEqual(response, "Sample response")
    
    @patch("builtins.open", new_callable=mock_open)
    @patch("csv.writer")
    def test_log_interaction(self, MockCSVWriter, MockOpen):
        log_interaction("What is AI?", "AI is artificial intelligence.")
        MockOpen.assert_called()
        MockCSVWriter.assert_called()
    
    @patch("builtins.open", new_callable=mock_open, read_data="What is AI?,AI is artificial intelligence.\n")
    @patch("csv.reader")
    def test_load_chat_history(self, MockCSVReader, MockOpen):
        MockCSVReader.return_value = [["What is AI?", "AI is artificial intelligence."]]
        history = load_chat_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["question"], "What is AI?")
        self.assertEqual(history[0]["answer"], "AI is artificial intelligence.")
    
    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_chat_history_file_not_found(self, MockOpen):
        history = load_chat_history()
        self.assertEqual(history, [])

if __name__ == "__main__":
    unittest.main()
