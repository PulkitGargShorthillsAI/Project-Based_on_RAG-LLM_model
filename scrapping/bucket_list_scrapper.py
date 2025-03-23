import requests
from bs4 import BeautifulSoup
import os

class BucketListScraper:
    """Scrapes bucket list destinations from BucketListTravels."""

    BASE_URL = "https://www.bucketlisttravels.com/round-up/100-bucket-list-destinations"

    def __init__(self, output_dir="scraped_city_data"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.text = ""
        self.web_pages = 0

    def fetch_soup(self, url):
        """Fetches and parses HTML content using BeautifulSoup."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, "lxml")
        except requests.exceptions.RequestException as e:
            print(f"⚠ Error fetching {url}: {e}")
            return None

    def get_country_details(self, country_url):
        """Extracts country details from its page."""
        soup = self.fetch_soup(country_url)
        if not soup:
            return ""

        text = ""
        articles = soup.find_all("article", {"class": "listing-card bg-white shadow-listing"})
        for article in articles:
            if article:
                text += article.find("h2").text.strip() + '\n'
                for p in article.find_all("p"):
                    text += p.text.strip() + "\n"
                text += '\n'
        return text

    def get_destination_details(self, destination_url):
        """Extracts destination details from its page."""
        soup = self.fetch_soup(destination_url)
        if not soup:
            return ""

        text = ""
        div = soup.find("div", {"class": "our-review"})
        if div:
            for p in div.find_all("p"):
                if p:
                    text += p.text.strip() + "\n"
                text += '\n'
        return text

    def scrape_bucket_list(self):
        """Scrapes the main page for bucket list destinations."""
        print(f"🚀 Scraping {self.BASE_URL}...")
        soup = self.fetch_soup(self.BASE_URL)
        if not soup:
            return

        content = soup.find("div", {"class": "flex flex-col gap-8"})
        if content:
            locations = content.find_all("article", {"class": "listing-card bg-white shadow-listing"})
            print(f"📌 Found {len(locations)} locations.")

            for location in locations:
                if location:
                    self.text += location.find("h2").text.strip() + '\n'
                    for p in location.find_all("p"):
                        self.text += p.text.strip() + "\n"
                    self.text += '\n'

                    url = location.find('a', {
                        "class": "button smooth focus:outline-none border-2 flex items-center "
                                 "justify-center gap-x-1 rounded-sm bg-theme-action "
                                 "hover:bg-theme-lightskyblue tracking-wider "
                                 "focus:bg-theme-lightskyblue border-theme-action "
                                 "normal px-2 py-1 font-semibold uppercase"
                    })
                    if url:
                        self.web_pages += 1
                        print(f"🔗 Scraping: {url['href']}")
                        if url['href'].split('/')[1] == 'experience':
                            self.text += self.get_destination_details("https://www.bucketlisttravels.com" + url['href'])
                        elif url['href'].split('/')[1] == 'destination':
                            self.text += self.get_destination_details("https://www.bucketlisttravels.com" + url['href'])
                        else:
                            self.text += self.get_country_details(url['href'])

    def save_to_file(self, filename="international_locations.txt"):
        """Saves the scraped content to a text file."""
        file_path = os.path.join(self.output_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.text)
        print(f"✅ Data saved in: {file_path}")

    def start_scraping(self):
        """Initiates the scraping process."""
        self.scrape_bucket_list()
        print(f"🌍 Scraped {self.web_pages} pages.")
        if self.text:
            self.save_to_file()
        else:
            print("⚠ No data scraped!")


