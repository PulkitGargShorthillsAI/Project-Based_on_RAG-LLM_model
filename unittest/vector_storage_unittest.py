import unittest
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from vector_storage import PineconeHandler, TextProcessor, VectorStoreUploader

class TestPineconeHandler(unittest.TestCase):
    @patch("vector_storage.Pinecone")
    def test_initialize_index(self, MockPinecone):
        mock_pc_instance = MockPinecone.return_value
        mock_pc_instance.list_indexes.return_value = [{'name': 'chatbot2'}]

        handler = PineconeHandler(index_name="chatbot2")
        mock_pc_instance.list_indexes.assert_called_once()
        mock_pc_instance.create_index.assert_not_called()
        self.assertEqual(handler.index_name, "chatbot2")

    @patch("vector_storage.Pinecone")
    def test_create_index_if_not_exists(self, MockPinecone):
        mock_pc_instance = MockPinecone.return_value
        mock_pc_instance.list_indexes.return_value = []

        handler = PineconeHandler(index_name="new_index")
        mock_pc_instance.create_index.assert_called_once()

class TestTextProcessor(unittest.TestCase):
    @patch("vector_storage.DirectoryLoader")
    @patch("vector_storage.TextLoader")
    @patch("vector_storage.RecursiveCharacterTextSplitter")
    def test_process_text_files(self, MockTextSplitter, MockTextLoader, MockDirectoryLoader):
        mock_loader_instance = MockDirectoryLoader.return_value
        mock_loader_instance.load.return_value = [MagicMock()]
        mock_text_splitter_instance = MockTextSplitter.return_value
        mock_text_splitter_instance.split_documents.return_value = [MagicMock()]
        
        processor = TextProcessor("/fake/path")
        self.assertTrue(processor.text_chunks)
        MockDirectoryLoader.assert_called_once_with("/fake/path", glob="*.txt", loader_cls=MockTextLoader)
        MockTextSplitter.assert_called_once()

class TestVectorStoreUploader(unittest.TestCase):
    @patch("vector_storage.PineconeVectorStore.from_documents")
    @patch("vector_storage.GoogleGenerativeAIEmbeddings")
    def test_upload_to_pinecone(self, MockEmbeddings, MockVectorStore):
        mock_pinecone_handler = MagicMock()
        mock_text_processor = MagicMock()
        mock_text_processor.text_chunks = [MagicMock()]
        
        uploader = VectorStoreUploader(mock_pinecone_handler, mock_text_processor)
        MockVectorStore.assert_called_once_with(
            documents=mock_text_processor.text_chunks,
            index_name=mock_pinecone_handler.index_name,
            embedding=MockEmbeddings.return_value
        )

if __name__ == "__main__":
    unittest.main()