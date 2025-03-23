import unittest
from unittest.mock import patch, Mock
import os
import shutil
import requests
from bs4 import BeautifulSoup
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from scrapping.holidify_scrapper import HolidifyScraper

class TestHolidifyScraper(unittest.TestCase):

    def setUp(self):
        self.urls = ["https://www.example.com/city1", "https://www.example.com/city2"]
        self.output_dir = "test_scraped_data"
        self.scraper = HolidifyScraper(self.urls, self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.output_dir, ignore_errors=True)

    @patch('requests.get')
    def test_fetch_content_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><div class="col-12 col-md-6 pr-md-3"><h3 class="card-heading">Heading 1</h3><p class="card-text">Description 1</p></div><div class="col-12 col-md-6 pr-md-3"><h3 class="card-heading">Heading 2</h3><p class="card-text">Description 2</p></div></body></html>'
        mock_get.return_value = mock_response

        content = self.scraper.fetch_content(self.urls[0])
        self.assertEqual(content, "Heading 1\nDescription 1\n\nHeading 2\nDescription 2\n\n")

    @patch('requests.get')
    def test_fetch_content_request_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Request failed")
        content = self.scraper.fetch_content(self.urls[0])
        self.assertEqual(content, "")

    @patch('requests.get')
    def test_fetch_content_http_error(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("HTTP Error")
        mock_get.return_value = mock_response
        content = self.scraper.fetch_content(self.urls[0])
        self.assertEqual(content, "")

    @patch('requests.get')
    def test_fetch_content_empty_response(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = ""
        mock_get.return_value = mock_response
        content = self.scraper.fetch_content(self.urls[0])
        self.assertEqual(content, "")

    @patch('requests.get')
    def test_fetch_content_no_content_div(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><div class="wrong-class">No content here</div></body></html>'
        mock_get.return_value = mock_response
        content = self.scraper.fetch_content(self.urls[0])
        self.assertEqual(content, "")

    @patch('requests.get')
    def test_fetch_content_missing_heading_or_description(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><div class="col-12 col-md-6 pr-md-3"><p class="card-text">Description 1</p></div></body></html>'
        mock_get.return_value = mock_response
        content = self.scraper.fetch_content(self.urls[0])
        self.assertEqual(content, "")

    @patch('requests.get')
    def test_fetch_content_retries_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><div class="col-12 col-md-6 pr-md-3"><h3 class="card-heading">Heading 1</h3><p class="card-text">Description 1</p></div></body></html>'
        mock_get.return_value = mock_response

        mock_get.side_effect = [requests.exceptions.RequestException("Request failed"), mock_response]
        content = self.scraper.fetch_content(self.urls[0])
        self.assertEqual(content, "Heading 1\nDescription 1\n\n")

    @patch('requests.get')
    def test_fetch_content_retries_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Request failed")
        content = self.scraper.fetch_content(self.urls[0])
        self.assertEqual(content, "")

    def test_save_to_file_success(self):
        filename = "test_file.txt"
        text = "Test data to be saved."
        self.scraper.save_to_file(filename, text)
        file_path = os.path.join(self.output_dir, filename)
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, "r", encoding="utf-8") as f:
            saved_content = f.read()
        self.assertEqual(saved_content, text)

    def test_save_to_file_io_error(self):
        filename = "/invalid/path/test_file.txt"
        text = "Test data."
        with patch("builtins.open", side_effect=OSError("Mocked OSError")):
            self.scraper.save_to_file(filename, text)
        self.assertFalse(os.path.exists(os.path.join(self.output_dir, filename)))

    @patch('scrapping.holidify_scrapper.HolidifyScraper.fetch_content')
    def test_start_scraping_success(self, mock_fetch):
        mock_fetch.return_value = "Heading 1\nDescription 1\n\n"
        self.scraper.start_scraping()
        file_path1 = os.path.join(self.output_dir, "city1.txt")
        file_path2 = os.path.join(self.output_dir, "city2.txt")
        self.assertTrue(os.path.exists(file_path1))
        self.assertTrue(os.path.exists(file_path2))

    @patch('scrapping.holidify_scrapper.HolidifyScraper.fetch_content')
    def test_start_scraping_no_data(self, mock_fetch):
        mock_fetch.return_value = ""
        self.scraper.start_scraping()
        file_path1 = os.path.join(self.output_dir, "city1.txt")
        file_path2 = os.path.join(self.output_dir, "city2.txt")
        self.assertFalse(os.path.exists(file_path1))
        self.assertFalse(os.path.exists(file_path2))


if __name__ == '__main__':
    unittest.main()