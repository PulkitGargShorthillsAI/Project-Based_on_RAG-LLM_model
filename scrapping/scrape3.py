import requests
from bs4 import BeautifulSoup
import os

class TravelScraper:
    """Scrapes travel destination data from multiple Holidify URLs."""
    
    def __init__(self, urls, output_dir="scraped_city_data"):
        self.urls = urls
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def fetch_content(self, url):
        """Fetches and extracts travel-related content from a given URL."""
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            soup = BeautifulSoup(response.text, "lxml")

            text = ""
            content = soup.find_all("div", {"class": "col-12 col-md-6 pr-md-3"})

            for location in content:
                heading = location.find("h3", {"class": "card-heading"})
                description = location.find("p", {"class": "card-text"})
                
                if heading and description:
                    text += heading.text.strip() + "\n"
                    text += description.text.strip() + "\n\n"

            return text

        except requests.exceptions.RequestException as e:
            print(f"⚠ Error fetching {url}: {e}")
            return ""

    def save_to_file(self, filename, text):
        """Saves the scraped content to a text file."""
        file_path = os.path.join(self.output_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"✅ Data saved in: {file_path}")

    def start_scraping(self):
        """Loops through all URLs and starts the scraping process."""
        for url in self.urls:
            print(f"🔍 Scraping: {url}")
            scraped_text = self.fetch_content(url)

            if scraped_text:
                filename = f"{url.split('/')[-1]}.txt"
                self.save_to_file(filename, scraped_text)
            else:
                print(f"⚠ No data found for {url}")


if __name__ == "__main__":
    urls = [
        "https://www.holidify.com/collections/monuments-of-india",
        "https://www.holidify.com/collections/one-places-from-each-state"
    ]
    scraper = TravelScraper(urls)
    scraper.start_scraping()
