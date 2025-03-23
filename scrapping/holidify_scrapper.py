import requests
from bs4 import BeautifulSoup
import os
import time

class HolidifyScraper:
    """Scrapes travel destination data from multiple Holidify URLs with error handling."""
    
    def __init__(self, urls, output_dir="scraped_city_data", max_retries=3, retry_delay=5):
        self.urls = urls
        self.output_dir = output_dir
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        os.makedirs(self.output_dir, exist_ok=True)

    def fetch_content(self, url):
        """Fetches and extracts travel-related content from a given URL with retries and error handling."""
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()  # Raise an error for bad responses
                
                if not response.text.strip():
                    print(f"⚠ Empty response received from {url}")
                    return ""
                
                soup = BeautifulSoup(response.text, "lxml")
                text = ""
                content = soup.find_all("div", {"class": "col-12 col-md-6 pr-md-3"})

                if not content:
                    print(f"⚠ No content found on {url}")
                    return ""
                
                for location in content:
                    heading = location.find("h3", {"class": "card-heading"})
                    description = location.find("p", {"class": "card-text"})
                    
                    if heading and description:
                        text += heading.text.strip() + "\n"
                        text += description.text.strip() + "\n\n"
                
                return text
            
            except requests.exceptions.RequestException as e:
                print(f"⚠ Error fetching {url} (Attempt {attempt + 1}/{self.max_retries}): {e}")
                time.sleep(self.retry_delay)
        
        print(f"❌ Failed to fetch {url} after {self.max_retries} attempts.")
        return ""

    def save_to_file(self, filename, text):
        """Saves the scraped content to a text file, handling file errors."""
        try:
            file_path = os.path.join(self.output_dir, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"✅ Data saved in: {file_path}")
        except OSError as e:
            print(f"❌ Error writing to file {filename}: {e}")

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
