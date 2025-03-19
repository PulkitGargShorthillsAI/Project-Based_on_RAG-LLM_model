import unittest
from unittest.mock import patch, MagicMock
import os
from vector_storage import PineconeHandler, TextProcessor, VectorStoreUploader  # Replace 'vector_storage' with your actual module name

class TestPineconeHandler(unittest.TestCase):
    
    @patch("vector_storage.Pinecone")
    def test_initialize_index(self, mock_pinecone):
        mock_pinecone.return_value.list_indexes.return_value = [{"name": "chatbot1"}]
        handler = PineconeHandler(index_name="chatbot1")
        self.assertEqual(handler.index_name, "chatbot1")
        mock_pinecone.return_value.list_indexes.assert_called_once()
    
    @patch("vector_storage.Pinecone")
    def test_create_index_if_not_exists(self, mock_pinecone):
        mock_pinecone.return_value.list_indexes.return_value = []
        handler = PineconeHandler(index_name="new_index")
        mock_pinecone.return_value.create_index.assert_called_once()

class TestTextProcessor(unittest.TestCase):
    
    @patch("vector_storage.DirectoryLoader")
    @patch("vector_storage.Document")
    def test_text_splitting(self, mock_document, mock_loader):
        mock_doc_instance = MagicMock()
        mock_doc_instance.page_content = "Sample text data"
        mock_document.return_value = mock_doc_instance
        
        mock_loader.return_value.load.return_value = [mock_doc_instance]
        processor = TextProcessor("/fake/path")
        self.assertGreater(len(processor.text_chunks), 0)  # Ensuring text was processed

class TestVectorStoreUploader(unittest.TestCase):
    
    @patch("vector_storage.PineconeVectorStore.from_documents")
    @patch("vector_storage.GoogleGenerativeAIEmbeddings")
    def test_upload_to_pinecone(self, mock_embeddings, mock_pinecone_vs):
        mock_handler = MagicMock()
        mock_processor = MagicMock()
        mock_processor.text_chunks = [MagicMock(page_content="Chunk 1"), MagicMock(page_content="Chunk 2")]
        
        VectorStoreUploader(mock_handler, mock_processor)
        mock_pinecone_vs.assert_called_once()

if __name__ == "__main__":
    unittest.main()
