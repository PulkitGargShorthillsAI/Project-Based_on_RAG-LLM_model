import unittest
from unittest.mock import patch, Mock, MagicMock
import os
from datetime import datetime
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from vector_storage import PineconeHandler, TextProcessor, VectorStoreUploader

class TestLogging(unittest.TestCase):
    def test_write_log_info(self):
        log_message = "Test log message"
        with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
            from vector_storage import write_log
            write_log(log_message)
            mock_file().write.assert_called_with(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO: {log_message}\n")

    def test_write_log_error(self):
        log_message = "Test error log"
        with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
            from vector_storage import write_log
            write_log(log_message, error=True)
            mock_file().write.assert_called_with(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERROR: {log_message}\n")

class TestPineconeHandler(unittest.TestCase):
    @patch("vector_storage.Pinecone")
    def test_initialize_pinecone_success(self, mock_pinecone):
        mock_pinecone.return_value.list_indexes.return_value = []
        handler = PineconeHandler("test_index")
        self.assertEqual(handler.index_name, "test_index")

    @patch("vector_storage.Pinecone")
    def test_initialize_pinecone_failure(self, mock_pinecone):
        mock_pinecone.side_effect = Exception("Pinecone init failed")
        with self.assertRaises(Exception):
            PineconeHandler("test_index")

    @patch("vector_storage.Pinecone")
    def test_index_has_data(self, mock_pinecone):
        mock_index = MagicMock()
        mock_index.describe_index_stats.return_value = {"total_vector_count": 10}
        mock_pinecone.return_value.Index.return_value = mock_index
        handler = PineconeHandler("test_index")
        self.assertTrue(handler.index_has_data())

class TestTextProcessor(unittest.TestCase):
    @patch("vector_storage.DirectoryLoader")
    @patch("vector_storage.RecursiveCharacterTextSplitter")
    def test_text_processing(self, mock_splitter, mock_loader):
        mock_loader.return_value.load.return_value = ["Document1", "Document2"]
        mock_splitter.return_value.split_documents.return_value = ["Chunk1", "Chunk2"]
        processor = TextProcessor("test_folder")
        self.assertEqual(processor.text_chunks, ["Chunk1", "Chunk2"])

class TestVectorStoreUploader(unittest.TestCase):
    @patch("vector_storage.GoogleGenerativeAIEmbeddings")
    @patch("vector_storage.PineconeVectorStore.from_documents")
    def test_upload_to_pinecone(self, mock_pinecone_upload, mock_embeddings):
        mock_handler = MagicMock()
        mock_handler.index_has_data.return_value = False
        mock_processor = MagicMock()
        mock_processor.text_chunks = ["Chunk1", "Chunk2"]
        VectorStoreUploader(mock_handler, mock_processor)
        mock_pinecone_upload.assert_called_once()

if __name__ == "__main__":
    unittest.main()
