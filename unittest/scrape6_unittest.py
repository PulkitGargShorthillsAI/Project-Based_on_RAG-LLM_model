import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
import os
import json
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

from scrapping.scrape6  import DookInternationalScraper  # Ensure this matches your actual file name

class TestDookInternationalScraper(unittest.TestCase):

    def setUp(self):
        """Initialize the scraper before each test"""
        self.scraper = DookInternationalScraper(output_folder="test_output", total_pages=2)

    @patch("scrapping.scrape6.requests.get")
    def test_fetch_soup(self, mock_get):
        """Test if fetch_soup correctly returns a BeautifulSoup object"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "<html><body><div>Test</div></body></html>"

        soup = self.scraper.fetch_soup("https://fake-url.com")
        self.assertIsInstance(soup, BeautifulSoup)
        self.assertEqual(soup.find("div").text, "Test")

    @patch("scrapping.scrape6.requests.get")
    def test_get_data(self, mock_get):
        """Test extracting country data from a country page"""
        mock_html = '''
        <div class="col-12 mb-3">Country Overview</div>
        <div class="brick">
            <h3>Attraction</h3>
            <p>Beautiful place to visit.</p>
        </div>
        '''
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = mock_html

        text = self.scraper.get_data("https://fake-country-url.com")
        expected_text = "Country Overview\nAttraction\nBeautiful place to visit.\n"
        self.assertEqual(text, expected_text)

    @patch("scrapping.scrape6.requests.get")
    def test_scrape_countries(self, mock_get):
        """Test country list scraping from the main page"""
        mock_html = '''
        <div class="col-md-4 col-lg-4 col-sm-6 col-xs-12">
            <h6>Country A</h6>
            <a class="package-slider-attraction" href="https://fake-country-url.com"></a>
        </div>
        '''
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = mock_html

        self.scraper.scrape_countries()
        self.assertIn("Country A", self.scraper.text)

    @patch("scrapping.scrape6.requests.get")
    def test_scrape_pagination(self, mock_get):
        """Test pagination scraping and handling JSON responses"""
        mock_html = '''
        <div class="col-md-4 col-lg-4 col-sm-6 col-xs-12">
            <h6>Country B</h6>
            <a class="package-slider-attraction" href="https://fake-country-url.com"></a>
        </div>
        '''
        json_mock = {"view": mock_html}
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = json.dumps(json_mock)

        self.scraper.scrape_pagination()
        self.assertIn("Country B", self.scraper.text)

    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_save_to_file(self, mock_open):
        """Test if the scraped data is correctly saved to a file"""
        self.scraper.text = "Sample scraped data"
        self.scraper.save_to_file("test_file.txt")
        mock_open.assert_called_with(os.path.join("test_output", "test_file.txt"), "w", encoding="utf-8")

    @patch("scrapping.scrape6.requests.get")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_start_scraping(self, mock_open, mock_get):
        """Test the full scraping process"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "<div class='col-md-4'><h6>Test Country</h6></div>"

        self.scraper.start_scraping()
        mock_open.assert_called()

if __name__ == "__main__":
    unittest.main()
