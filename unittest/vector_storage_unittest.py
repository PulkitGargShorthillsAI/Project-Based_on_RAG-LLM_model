import os
import unittest
from unittest.mock import patch, MagicMock
import sys
from langchain_core.documents import Document  

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from vector_storage import PineconeHandler, TextProcessor, VectorStoreUploader, write_log

class TestPineconeHandler(unittest.TestCase):

    @patch("vector_storage.Pinecone")
    def test_pinecone_initialization_success(self, mock_pinecone):
        """Test successful initialization of PineconeHandler"""
        mock_pinecone.return_value.list_indexes.return_value = [{"name": "chatbot3"}]
        handler = PineconeHandler(index_name="chatbot3")
        self.assertIsNotNone(handler.index)

    @patch("vector_storage.Pinecone")
    def test_pinecone_initialization_failure(self, mock_pinecone):
        """Test PineconeHandler failure when Pinecone API is down"""
        mock_pinecone.side_effect = Exception("API failure")
        with self.assertRaises(Exception):
            PineconeHandler(index_name="chatbot3")

    @patch("vector_storage.Pinecone")
    def test_pinecone_index_already_exists(self, mock_pinecone):
        """Test behavior when index already exists"""
        mock_pinecone.return_value.list_indexes.return_value = [{"name": "chatbot3"}]
        handler = PineconeHandler(index_name="chatbot3")
        self.assertTrue(handler.index)

    @patch("vector_storage.Pinecone")
    def test_pinecone_create_index_if_missing(self, mock_pinecone):
        """Test index creation when it does not exist"""
        mock_pinecone.return_value.list_indexes.return_value = []
        mock_pinecone.return_value.create_index = MagicMock()
        handler = PineconeHandler(index_name="chatbot3")
        mock_pinecone.return_value.create_index.assert_called_once()

    @patch("vector_storage.Pinecone")
    def test_pinecone_index_has_data(self, mock_pinecone):
        """Test index_has_data when vectors are present"""
        mock_index = MagicMock()
        mock_index.describe_index_stats.return_value = {"total_vector_count": 10}
        mock_pinecone.return_value.Index.return_value = mock_index

        handler = PineconeHandler(index_name="chatbot3")
        self.assertTrue(handler.index_has_data())

    @patch("vector_storage.Pinecone")
    def test_pinecone_index_empty(self, mock_pinecone):
        """Test index_has_data when index is empty"""
        mock_index = MagicMock()
        mock_index.describe_index_stats.return_value = {"total_vector_count": 0}
        mock_pinecone.return_value.Index.return_value = mock_index

        handler = PineconeHandler(index_name="chatbot3")
        self.assertFalse(handler.index_has_data())

class TestTextProcessor(unittest.TestCase):

    @patch("vector_storage.DirectoryLoader")
    def test_text_processing_success(self, mock_loader):
        """Test successful text processing with valid document objects"""
        mock_documents = [
            Document(page_content="This is a test document."),
            Document(page_content="Another test document."),
        ]
        mock_loader_instance = MagicMock()
        mock_loader_instance.load.return_value = mock_documents
        mock_loader.return_value = mock_loader_instance
        processor = TextProcessor(folder_path="mock_folder")

        self.assertTrue(processor.text_chunks)
        self.assertTrue(all(isinstance(doc, Document) for doc in processor.text_chunks))



    @patch("vector_storage.DirectoryLoader")
    def test_text_processing_failure(self, mock_loader):
        """Test error handling when text loading fails"""
        mock_loader.return_value.load.side_effect = Exception("File read error")
        with self.assertRaises(Exception):
            TextProcessor(folder_path="mock_folder")

class TestVectorStoreUploader(unittest.TestCase):

    @patch("vector_storage.GoogleGenerativeAIEmbeddings")
    @patch("vector_storage.PineconeVectorStore.from_documents")
    def test_successful_upload(self, mock_from_documents, mock_embeddings):
        """Test successful upload to Pinecone"""
        mock_handler = MagicMock()
        mock_handler.index_has_data.return_value = False
        mock_text_processor = MagicMock()
        mock_text_processor.text_chunks = ["chunk1", "chunk2"]

        uploader = VectorStoreUploader(mock_handler, mock_text_processor)
        mock_from_documents.assert_called_once()

    @patch("vector_storage.GoogleGenerativeAIEmbeddings")
    @patch("vector_storage.PineconeVectorStore.from_documents")
    def test_skip_upload_if_index_not_empty(self, mock_from_documents, mock_embeddings):
        """Test skipping upload if index is not empty"""
        mock_handler = MagicMock()
        mock_handler.index_has_data.return_value = True
        mock_text_processor = MagicMock()
        mock_text_processor.text_chunks = ["chunk1", "chunk2"]

        uploader = VectorStoreUploader(mock_handler, mock_text_processor)
        mock_from_documents.assert_not_called()

    @patch("vector_storage.GoogleGenerativeAIEmbeddings")
    def test_embedding_initialization_failure(self, mock_embeddings):
        """Test failure when embeddings initialization fails"""
        mock_embeddings.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            VectorStoreUploader(MagicMock(), MagicMock())

if __name__ == "__main__":
    unittest.main()
