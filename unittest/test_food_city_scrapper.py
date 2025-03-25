import unittest
from unittest.mock import patch, Mock
import os
import shutil
import requests
from bs4 import BeautifulSoup
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from scrapping.food_city_scrapper import FoodCityScraper

class TestFoodCityScraper(unittest.TestCase):

    def setUp(self):
        self.url = "https://www.example.com/food-blog"
        self.output_dir = "test_scraped_data"
        self.scraper = FoodCityScraper(self.url, self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.output_dir, ignore_errors=True)

    @patch('requests.get')
    def test_fetch_content_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><div class="lt-side"><h2>City 1</h2><p>Food description 1</p><h2>City 2</h2><p>Food description 2</p></div></body></html>'
        mock_get.return_value = mock_response

        content = self.scraper.fetch_content()
        self.assertEqual(content, "\nCity 1\nFood description 1\nCity 2\nFood description 2\n")

    @patch('requests.get')
    def test_fetch_content_request_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Request failed")
        content = self.scraper.fetch_content()
        self.assertEqual(content, "")

    @patch('requests.get')
    def test_fetch_content_timeout(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")
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
    def test_fetch_content_no_lt_side(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><div class="wrong-class">No content here</div></body></html>'
        mock_get.return_value = mock_response
        content = self.scraper.fetch_content()
        self.assertEqual(content, "")

    @patch('requests.get')
    def test_fetch_content_no_h2_p(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><div class="lt-side"></div></body></html>'
        mock_get.return_value = mock_response
        content = self.scraper.fetch_content()
        self.assertEqual(content, "\n")

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
        with patch("builtins.open", side_effect=IOError("Mocked IOError")):
            self.scraper.save_to_file(filename, text)
        self.assertFalse(os.path.exists(os.path.join(self.output_dir, filename)))

    @patch('scrapping.food_city_scrapper.FoodCityScraper.fetch_content')
    def test_start_scraping_success(self, mock_fetch):
        mock_fetch.return_value = "City 1\nFood 1\n"
        self.scraper.start_scraping()
        file_path = os.path.join(self.output_dir, "32_cities_for_food_in_india.txt")
        self.assertTrue(os.path.exists(file_path))

    @patch('scrapping.food_city_scrapper.FoodCityScraper.fetch_content')
    def test_start_scraping_no_data(self, mock_fetch):
        mock_fetch.return_value = ""
        self.scraper.start_scraping()
        file_path = os.path.join(self.output_dir, "32_cities_for_food_in_india.txt")
        self.assertFalse(os.path.exists(file_path))


if __name__ == '__main__':
    unittest.main()