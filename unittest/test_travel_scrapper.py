import unittest
from unittest.mock import patch, Mock
import os
import shutil
import requests
from bs4 import BeautifulSoup
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from scrapping.travel_scrapper import TravelScraper

class TestTravelScraper(unittest.TestCase):

    def setUp(self):
        self.base_url = "https://www.example.com/travel-blog"
        self.output_dir = "test_scraped_data"
        self.scraper = TravelScraper(self.base_url, self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.output_dir, ignore_errors=True)

    @patch('requests.get')
    def test_fetch_content_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><div class="blog-excerpt fb-heart"><p>Location 1</p><h3>Location 2</h3><p>Location 3</p></div></body></html>'
        mock_get.return_value = mock_response

        content = self.scraper.fetch_content()
        self.assertEqual(content, "Location 1\nLocation 2\nLocation 3\n")

    @patch('requests.get')
    def test_fetch_content_request_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Request failed")
        content = self.scraper.fetch_content()
        self.assertEqual(content, "")

    @patch('requests.get')
    def test_fetch_content_http_error(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("HTTP Error")
        mock_get.return_value = mock_response
        content = self.scraper.fetch_content()
        self.assertEqual(content, "")

    @patch('requests.get')
    def test_fetch_content_no_content_div(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><div class="wrong-class">No content here</div></body></html>'
        mock_get.return_value = mock_response
        content = self.scraper.fetch_content()
        self.assertEqual(content, "")

    @patch('requests.get')
    def test_fetch_content_empty_p_h3(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><div class="blog-excerpt fb-heart"><p></p><h3></h3></div></body></html>'
        mock_get.return_value = mock_response
        content = self.scraper.fetch_content()
        self.assertEqual(content, "\n\n")

    @patch('requests.get')
    def test_fetch_content_parsing_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><div class="blog-excerpt fb-heart"><p>Location 1</p><h3>Location 2' # invalid HTML
        mock_get.return_value = mock_response
        content = self.scraper.fetch_content()
        self.assertEqual(content, "Location 1\nLocation 2\n")

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
        filename = "/invalid/path/test_file.txt" # This will cause an IOError
        text = "Test data."
        with patch("builtins.open", side_effect=IOError("Mocked IOError")):
            self.scraper.save_to_file(filename, text)
        # Check that no file was created (in a real scenario, it wouldn't be)
        self.assertFalse(os.path.exists(os.path.join(self.output_dir, filename)))

    @patch('requests.get')
    def test_start_scraping_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><div class="blog-excerpt fb-heart"><p>Location 1</p></div></body></html>'
        mock_get.return_value = mock_response

        self.scraper.start_scraping()
        file_path = os.path.join(self.output_dir, "108_famous_locations_in_india.txt")
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, "r", encoding="utf-8") as f:
            saved_content = f.read()
        self.assertEqual(saved_content, "Location 1\n")

    @patch('requests.get')
    def test_start_scraping_no_data(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><div class="wrong-class">No data</div></body></html>'
        mock_get.return_value = mock_response

        self.scraper.start_scraping()
        file_path = os.path.join(self.output_dir, "108_famous_locations_in_india.txt")
        self.assertFalse(os.path.exists(file_path))

if __name__ == '__main__':
    unittest.main()