import requests
from bs4 import BeautifulSoup
import os
import json

class DookInternationalScraper:
    """Scrapes country travel data from Dook International"""

    BASE_URL = "https://www.dookinternational.com/countries"

    def __init__(self, output_folder="scraped_city_data", total_pages=15):
        self.output_folder = output_folder
        self.total_pages = total_pages
        os.makedirs(self.output_folder, exist_ok=True)
        self.text = ""

    def fetch_soup(self, url):
        """Fetches and parses HTML content using BeautifulSoup"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, "lxml")
        except requests.exceptions.RequestException as e:
            print(f"⚠ Error fetching {url}: {e}")
            return None

    def get_data(self, base_url):
        """Scrapes country details from a given URL"""
        soup = self.fetch_soup(base_url)
        if not soup:
            return ""
        text = ""
        if soup.find('div', {"class": "col-12 mb-3"}):
            text = soup.find('div', {"class": "col-12 mb-3"}).text.strip()
            content = soup.find_all('div', {"class": "brick"})

            for c in content:
                title = c.find('h3')
                desc = c.find('p')
                if title and desc:
                    text += f"\n{title.text.strip()}\n{desc.text.strip()}\n"

        return text

    def scrape_countries(self):
        """Scrapes the country list and their details"""
        soup = self.fetch_soup(self.BASE_URL)
        if not soup:
            return

        content = soup.find_all("div", {"class": "col-md-4 col-lg-4 col-sm-6 col-xs-12"})
        for location in content:
            country_name = location.find('h6')
            country_url = location.find('a', {"class": "package-slider-attraction"})

            if country_name:
                self.text += country_name.text.strip() + "\n"

            if country_url:
                self.text += self.get_data(country_url['href'])

    def scrape_pagination(self):
        """Handles pagination and scrapes additional pages"""
        for i in range(2, self.total_pages + 1):
            try:
                page_url = f"{self.BASE_URL}/?page={i}"
                response = requests.get(page_url)
                obj = json.loads(response.text)
                soup = BeautifulSoup(obj['view'], "lxml")

                content = soup.find_all("div", {"class": "col-md-4 col-lg-4 col-sm-6 col-xs-12"})
                for location in content:
                    country_name = location.find('h6')
                    country_url = location.find('a', {"class": "package-slider-attraction"})

                    if country_name:
                        self.text += country_name.text.strip() + "\n"

                    if country_url:
                        self.text += self.get_data(country_url['href'])

            except Exception as e:
                print(f"⚠ Error scraping page {i}: {e}")

    def save_to_file(self, filename="120_countries_data.txt"):
        """Saves scraped data to a file"""
        file_path = os.path.join(self.output_folder, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.text)
        print(f"✅ Data saved at: {file_path}")

    def start_scraping(self):
        """Main function to start scraping"""
        print(f"Starting to scrape {self.BASE_URL}")
        self.scrape_countries()
        self.scrape_pagination()
        self.save_to_file()