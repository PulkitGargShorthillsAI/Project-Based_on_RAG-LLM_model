import unittest
from unittest.mock import patch, Mock
import os
import shutil
import requests
from bs4 import BeautifulSoup
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from scrapping.visa_requirement_scrapper import VisaRequirementScraper

class TestVisaRequirementScraper(unittest.TestCase):

    def setUp(self):
        self.output_dir = "test_scraped_data"
        self.output_filename = "visa_requirements.txt"
        self.scraper = VisaRequirementScraper(self.output_dir, self.output_filename)
        os.makedirs(self.output_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.output_dir, ignore_errors=True)

    @patch('requests.get')
    def test_fetch_soup_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body>Test Content</body></html>'
        mock_get.return_value = mock_response

        soup = self.scraper.fetch_soup()
        self.assertIsInstance(soup, BeautifulSoup)

    @patch('requests.get')
    def test_fetch_soup_request_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Request failed")
        soup = self.scraper.fetch_soup()
        self.assertIsNone(soup)

    @patch('requests.get')
    def test_scrape_data_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><div class="mw-content-ltr mw-parser-output"><table><tr><td>Country</td><td>Visa Info</td></tr><tr><td>USA</td><td>Visa required</td></tr></table></div></body></html>'
        mock_get.return_value = mock_response

        self.scraper.scrape_data()
        self.assertIn("Country Visa Info \nUSA Visa required \n", self.scraper.text)

    @patch('requests.get')
    def test_scrape_data_fetch_soup_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Request failed")
        self.scraper.scrape_data()
        self.assertEqual(self.scraper.text, "")

    @patch('requests.get')
    def test_scrape_data_no_content(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><div class="mw-content-ltr mw-parser-output"></div></body></html>'
        mock_get.return_value = mock_response

        self.scraper.scrape_data()
        self.assertEqual(self.scraper.text, "")

    @patch('requests.get')
    def test_scrape_data_attribute_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><div>Test</div></body></html>'
        mock_get.return_value = mock_response

        self.scraper.scrape_data()
        self.assertEqual(self.scraper.text, "")

    def test_save_to_file_success(self):
        self.scraper.text = "Test data"
        self.scraper.save_to_file()
        file_path = os.path.join(self.output_dir, self.output_filename)
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, "r", encoding="utf-8") as f:
            saved_content = f.read()
        self.assertEqual(saved_content, "Test data")

    def test_save_to_file_no_data(self):
        self.scraper.text = ""
        self.scraper.save_to_file()
        file_path = os.path.join(self.output_dir, self.output_filename)
        self.assertFalse(os.path.exists(file_path))

    def test_save_to_file_os_error(self):
        self.scraper.text = "Test data"
        with patch("builtins.open", side_effect=OSError("Mocked OSError")):
            self.scraper.save_to_file()
        file_path = os.path.join(self.output_dir, self.output_filename)
        self.assertFalse(os.path.exists(file_path))

    @patch('scrapping.visa_requirement_scrapper.VisaRequirementScraper.scrape_data')
    def test_start_scraping_success(self, mock_scrape):
        mock_scrape.return_value = None
        self.scraper.text = "Test data"
        self.scraper.start_scraping()
        file_path = os.path.join(self.output_dir, self.output_filename)
        self.assertTrue(os.path.exists(file_path))

    @patch('scrapping.visa_requirement_scrapper.VisaRequirementScraper.scrape_data')
    def test_start_scraping_no_data(self, mock_scrape):
        mock_scrape.return_value = None
        self.scraper.text = ""
        self.scraper.start_scraping()
        file_path = os.path.join(self.output_dir, self.output_filename)
        self.assertFalse(os.path.exists(file_path))


if __name__ == '__main__':
    unittest.main()