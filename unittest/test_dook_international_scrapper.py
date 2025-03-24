import unittest
from unittest.mock import patch, Mock
import os
import shutil
import requests
from bs4 import BeautifulSoup
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from scrapping.dook_international_scrapper import DookInternationalScraper

class TestDookInternationalScraper(unittest.TestCase):

    def setUp(self):
        self.output_folder = "test_scraped_data"
        self.scraper = DookInternationalScraper(self.output_folder)
        os.makedirs(self.output_folder, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.output_folder, ignore_errors=True)

    @patch('requests.get')
    def test_fetch_soup_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body>Test Content</body></html>'
        mock_get.return_value = mock_response

        soup = self.scraper.fetch_soup("https://www.example.com")
        self.assertIsInstance(soup, BeautifulSoup)

    @patch('requests.get')
    def test_fetch_soup_request_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Request failed")
        soup = self.scraper.fetch_soup("https://www.example.com")
        self.assertIsNone(soup)

    @patch('requests.get')
    def test_get_data_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><div class="col-12 mb-3">Overview</div><div class="brick"><h3>Title</h3><p>Description</p></div></body></html>'
        mock_get.return_value = mock_response

        data = self.scraper.get_data("https://www.example.com/country")
        self.assertEqual(data, "Overview\nTitle\nDescription\n")

    @patch('requests.get')
    def test_get_data_fetch_soup_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Request failed")
        data = self.scraper.get_data("https://www.example.com/country")
        self.assertEqual(data, "")

    @patch('requests.get')
    def test_get_data_no_content(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body></body></html>'
        mock_get.return_value = mock_response

        data = self.scraper.get_data("https://www.example.com/country")
        self.assertEqual(data, "")

    @patch('requests.get')
    def test_scrape_countries_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><div class="col-md-4 col-lg-4 col-sm-6 col-xs-12"><h6>Country Name</h6><a href="/country" class="package-slider-attraction">Link</a></div><div class="col-12 mb-3">Overview</div><div class="brick"><h3>Title</h3><p>Description</p></div></body></html>'
        mock_get.side_effect = [mock_response, mock_response]

        self.scraper.scrape_countries()
        self.assertIn("Country Name\nOverview\nTitle\nDescription\n", self.scraper.text)

    @patch('requests.get')
    def test_scrape_countries_fetch_soup_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Request failed")
        self.scraper.scrape_countries()
        self.assertEqual(self.scraper.text, "")

    @patch('requests.get')
    @patch('scrapping.dook_international_scrapper.DookInternationalScraper.get_data')
    def test_scrape_pagination_success(self, mock_get_data, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({'view': '<html><body><div class="col-md-4 col-lg-4 col-sm-6 col-xs-12"><h6>Country Name</h6><a href="/country" class="package-slider-attraction">Link</a></div></body></html>'})
        mock_get.return_value = mock_response

        mock_get_data.return_value = "Overview\nTitle\nDescription\n" # added return value

        self.scraper.scrape_pagination()
        self.assertIn("Country Name\nOverview\nTitle\nDescription\n", self.scraper.text)

    @patch('requests.get')
    def test_scrape_pagination_exception(self, mock_get):
        mock_get.side_effect = Exception("Page error")
        self.scraper.scrape_pagination()
        self.assertEqual(self.scraper.text, "")

    def test_save_to_file_success(self):
        self.scraper.text = "Test data"
        self.scraper.save_to_file()
        file_path = os.path.join(self.output_folder, "120_countries_data.txt")
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, "r", encoding="utf-8") as f:
            saved_content = f.read()
        self.assertEqual(saved_content, "Test data")

    @patch('scrapping.dook_international_scrapper.DookInternationalScraper.scrape_countries')
    @patch('scrapping.dook_international_scrapper.DookInternationalScraper.scrape_pagination')
    def test_start_scraping_success(self, mock_pagination, mock_countries):
        mock_countries.return_value = None
        mock_pagination.return_value = None
        self.scraper.text = "Test data"
        self.scraper.start_scraping()
        file_path = os.path.join(self.output_folder, "120_countries_data.txt")
        self.assertTrue(os.path.exists(file_path))

if __name__ == '__main__':
    unittest.main()