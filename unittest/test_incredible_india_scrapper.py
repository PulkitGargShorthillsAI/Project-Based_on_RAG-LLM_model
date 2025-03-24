import unittest
from unittest.mock import patch, Mock
import os
import shutil
import requests
from bs4 import BeautifulSoup
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

from scrapping.incredible_india_scrapper import IncredibleIndiaScraper  # Replace 'your_module' with the actual module name

class TestIncredibleIndiaScraper(unittest.TestCase):

    def setUp(self):
        self.base_url = "https://www.example.com/"
        self.output_dir = "test_scraped_data"
        self.scraper = IncredibleIndiaScraper(self.base_url, self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.output_dir, ignore_errors=True)

    @patch('requests.get')
    def test_get_location_urls_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><a href="/city1" class="btn btn-primary">City 1</a><a href="/city2" class="btn btn-primary">City 2</a></body></html>'
        mock_get.return_value = mock_response

        urls = self.scraper.get_location_urls()
        self.assertEqual(urls, ["/city1", "/city2"])

    @patch('requests.get')
    def test_get_location_urls_request_error(self, mock_get):
        mock_get.side_effect = requests.RequestException("Request failed")
        urls = self.scraper.get_location_urls()
        self.assertEqual(urls, [])

    @patch('requests.get')
    def test_get_location_urls_parsing_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><a href="/city1" class="wrong_class">City 1</a></body></html>'
        mock_get.return_value = mock_response

        urls = self.scraper.get_location_urls()
        self.assertEqual(urls, [])

    @patch('requests.get')
    def test_scrape_city_data_success(self, mock_get):
        mock_response_city = Mock()
        mock_response_city.status_code = 200
        mock_response_city.text = '<html><body><div class="col-sm-12 col-md-7 col-lg-7 inc-tilemap__right"><h2>City Name</h2><p>City Description</p></div><div class="container responsivegrid inc-container pb-5 aem-GridColumn aem-GridColumn--default--12"><a href="/location1">Location 1</a></div></body></html>'

        mock_response_location = Mock()
        mock_response_location.status_code = 200
        mock_response_location.text = '<html><body><div class="col-sm-12 col-md-7 col-lg-7 inc-tilemap__right"><h2>Location Name</h2><p>Location Description</p></div></body></html>'

        mock_get.side_effect = [mock_response_city, mock_response_location]

        self.scraper.scrape_city_data(self.base_url + "city_name")
        file_path = os.path.join(self.output_dir, "city_name.txt")
        self.assertTrue(os.path.exists(file_path))

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Corrected assertion:
            self.assertIn("CITY_NAME", content)
            self.assertIn("City Description", content)
            self.assertIn("Location Name", content)
            self.assertIn("Location Description", content)

    @patch('requests.get')
    def test_scrape_city_data_request_error(self, mock_get):
        mock_get.side_effect = requests.RequestException("Request failed")
        self.scraper.scrape_city_data(self.base_url + "city_name")
        file_path = os.path.join(self.output_dir, "city_name.txt")
        self.assertFalse(os.path.exists(file_path))

    @patch('requests.get')
    def test_get_location_links_success(self, mock_get):
        html = '<html><body><div class="container responsivegrid inc-container pb-5 aem-GridColumn aem-GridColumn--default--12"><a href="/loc1">Loc1</a><a href="/loc2">Loc2</a></div></body></html>'
        soup = BeautifulSoup(html, "lxml")
        links = self.scraper.get_location_links(soup)
        self.assertEqual(links, {"/loc1", "/loc2"})

    @patch('requests.get')
    def test_get_location_links_no_container(self, mock_get):
        html = '<html><body></body></html>'
        soup = BeautifulSoup(html, "lxml")
        links = self.scraper.get_location_links(soup)
        self.assertEqual(links, set())

    @patch('requests.get')
    def test_scrape_location_data_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><div class="col-sm-12 col-md-7 col-lg-7 inc-tilemap__right"><h2>Location Name</h2><p>Location Description</p></div></body></html>'
        mock_get.return_value = mock_response

        data = self.scraper.scrape_location_data(self.base_url + "location_name")
        # Corrected assertion:
        self.assertIn("LOCATION_NAME", data)
        self.assertIn("Location Description", data)

    @patch('requests.get')
    def test_scrape_location_data_request_error(self, mock_get):
        mock_get.side_effect = requests.RequestException("Request failed")
        data = self.scraper.scrape_location_data(self.base_url + "location_name")
        self.assertEqual(data, "")

    @patch('requests.get')
    def test_scrape_location_data_attractions(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><div class="col-sm-12 col-md-7 col-lg-7 inc-tilemap__right"><h2>Location Name</h2><p>Location Description</p></div></body></html>'
        mock_get.return_value = mock_response

        data = self.scraper.scrape_location_data(self.base_url + "attractions")
        self.assertEqual(data, "")

    @patch('requests.get')
    def test_start_scraping_integration(self, mock_get):
        mock_response_main = Mock()
        mock_response_main.status_code = 200
        mock_response_main.text = '<html><body><a href="/city1" class="btn btn-primary">City 1</a></body></html>'

        mock_response_city = Mock()
        mock_response_city.status_code = 200
        mock_response_city.text = '<html><body><div class="col-sm-12 col-md-7 col-lg-7 inc-tilemap__right"><h2>City Name</h2><p>City Description</p></div><div class="container responsivegrid inc-container pb-5 aem-GridColumn aem-GridColumn--default--12"><a href="/location1">Location 1</a></div></body></html>'

        mock_response_location = Mock()
        mock_response_location.status_code = 200
        mock_response_location.text = '<html><body><div class="col-sm-12 col-md-7 col-lg-7 inc-tilemap__right"><h2>Location Name</h2><p>Location Description</p></div></body></html>'

        mock_get.side_effect = [mock_response_main, mock_response_city, mock_response_location]

        self.scraper.start_scraping()
        file_path = os.path.join(self.output_dir, "city1.txt")
        self.assertTrue(os.path.exists(file_path))

if __name__ == '__main__':
    unittest.main()