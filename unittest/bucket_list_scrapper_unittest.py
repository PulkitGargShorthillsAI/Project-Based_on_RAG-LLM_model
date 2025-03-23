import unittest
from unittest.mock import patch, Mock
import os
import shutil
import requests
from bs4 import BeautifulSoup
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from scrapping.bucket_list_scrapper import BucketListScraper

class TestBucketListScraper(unittest.TestCase):

    def setUp(self):
        self.output_dir = "test_scraped_data"
        self.scraper = BucketListScraper(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.output_dir, ignore_errors=True)

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
    def test_get_country_details_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><article class="listing-card bg-white shadow-listing"><h2>Country Name</h2><p>Detail 1</p><p>Detail 2</p></article></body></html>'
        mock_get.return_value = mock_response

        details = self.scraper.get_country_details("https://www.example.com/country")
        self.assertEqual(details, "Country Name\nDetail 1\nDetail 2\n\n")

    @patch('requests.get')
    def test_get_country_details_fetch_soup_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Request failed")
        details = self.scraper.get_country_details("https://www.example.com/country")
        self.assertEqual(details, "")

    @patch('requests.get')
    def test_get_destination_details_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><div class="our-review"><p>Destination detail 1</p><p>Destination detail 2</p></div></body></html>'
        mock_get.return_value = mock_response

        details = self.scraper.get_destination_details("https://www.example.com/destination")
        self.assertEqual(details, "Destination detail 1\n\nDestination detail 2\n\n")

    @patch('requests.get')
    def test_get_destination_details_fetch_soup_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Request failed")
        details = self.scraper.get_destination_details("https://www.example.com/destination")
        self.assertEqual(details, "")

    @patch('requests.get')
    def test_scrape_bucket_list_success(self, mock_get):
        main_response = Mock()
        main_response.status_code = 200
        main_response.text = '<html><body><div class="flex flex-col gap-8"><article class="listing-card bg-white shadow-listing"><h2>Location 1</h2><p>Location detail</p><a href="/destination/loc1" class="button smooth focus:outline-none border-2 flex items-center justify-center gap-x-1 rounded-sm bg-theme-action hover:bg-theme-lightskyblue tracking-wider focus:bg-theme-lightskyblue border-theme-action normal px-2 py-1 font-semibold uppercase">Link</a></article></div></body></html>'
        dest_response = Mock()
        dest_response.status_code = 200
        dest_response.text = '<html><body><div class="our-review"><p>Destination detail</p></div></body></html>'
        mock_get.side_effect = [main_response, dest_response]

        self.scraper.scrape_bucket_list()
        self.assertIn("Location 1", self.scraper.text)
        self.assertIn("Destination detail", self.scraper.text)
        self.assertEqual(self.scraper.web_pages, 1)

    @patch('requests.get')
    def test_scrape_bucket_list_no_content(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body></body></html>'
        mock_get.return_value = mock_response

        self.scraper.scrape_bucket_list()
        self.assertEqual(self.scraper.text, "")

    @patch('requests.get')
    def test_scrape_bucket_list_fetch_soup_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Request failed")
        self.scraper.scrape_bucket_list()
        self.assertEqual(self.scraper.text, "")

    def test_save_to_file_success(self):
        self.scraper.text = "Test data"
        self.scraper.save_to_file()
        file_path = os.path.join(self.output_dir, "international_locations.txt")
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, "r", encoding="utf-8") as f:
            saved_content = f.read()
        self.assertEqual(saved_content, "Test data")

    @patch('scrapping.bucket_list_scrapper.BucketListScraper.scrape_bucket_list')
    def test_start_scraping_success(self, mock_scrape):
        mock_scrape.return_value = None
        self.scraper.text = "Test data"
        self.scraper.start_scraping()
        file_path = os.path.join(self.output_dir, "international_locations.txt")
        self.assertTrue(os.path.exists(file_path))

    @patch('scrapping.bucket_list_scrapper.BucketListScraper.scrape_bucket_list')
    def test_start_scraping_no_data(self, mock_scrape):
        mock_scrape.return_value = None
        self.scraper.text = ""
        self.scraper.start_scraping()
        file_path = os.path.join(self.output_dir, "international_locations.txt")
        self.assertFalse(os.path.exists(file_path))

if __name__ == '__main__':
    unittest.main()