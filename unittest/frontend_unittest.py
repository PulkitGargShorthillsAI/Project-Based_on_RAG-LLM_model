import unittest
from unittest.mock import patch, mock_open, MagicMock
import csv
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from datetime import datetime
from frontend import get_rag_response, log_interaction, load_chat_history

class TestFrontend(unittest.TestCase):

    @patch("frontend.chatbot.ask_question", return_value={"answer": "Test response"})
    def test_get_rag_response(self, mock_chatbot):
        """Test if RAG response is retrieved correctly."""
        response = get_rag_response("What is AI?")
        self.assertEqual(response, "Test response")
        mock_chatbot.assert_called_once_with("What is AI?")

    @patch("builtins.open", new_callable=mock_open)
    @patch("frontend.csv.writer")
    def test_log_interaction(self, mock_csv_writer, mock_file):
        """Test if chat interaction is logged correctly in both log files."""
        question = "What is AI?"
        answer = "Artificial Intelligence"
        log_interaction(question, answer)

        # Verify file writes
        mock_file.assert_any_call("logging/log_chatbot.log", "a")
        mock_file.assert_any_call("logging/log_chatbot.csv", "a", newline="")

        # Check log file content
        mock_file().write.assert_any_call(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nQ: {question}\nA: {answer}\n{'-'*40}\n")

        # Check CSV writer was called
        mock_csv_writer().writerow.assert_called_once_with([question, answer])

    @patch("builtins.open", new_callable=mock_open, read_data="What is AI?,Artificial Intelligence\nHow's the weather?,Sunny\n")
    def test_load_chat_history(self, mock_file):
        """Test if chat history loads correctly from CSV."""
        history = load_chat_history()
        
        expected_history = [
            {"question": "What is AI?", "answer": "Artificial Intelligence"},
            {"question": "How's the weather?", "answer": "Sunny"}
        ]
        self.assertEqual(history, expected_history)


    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_chat_history_file_not_found(self, mock_open):
        """Test loading chat history when CSV file does not exist."""
        history = load_chat_history()
        self.assertEqual(history, []) 

if __name__ == "__main__":
    unittest.main()
