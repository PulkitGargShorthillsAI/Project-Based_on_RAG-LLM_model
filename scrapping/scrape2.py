import requests
from bs4 import BeautifulSoup
import os

class TravelScraper:
    """Scrapes travel destination data from a given blog URL."""
    
    def __init__(self, base_url: str, output_dir: str = "scraped_city_data"):
        self.base_url = base_url
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def fetch_content(self) -> str:
        """Fetches and extracts relevant travel destination content."""
        try:
            response = requests.get(self.base_url, timeout=10)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx and 5xx)
        except requests.exceptions.RequestException as e:
            print(f"⚠ Network error while fetching content: {e}")
            return ""

        try:
            soup = BeautifulSoup(response.text, "lxml")
            text = ""
            content = soup.find("div", {"class": "blog-excerpt fb-heart"})
            
            if content:
                website_text = content.find_all(["p", "h3"])
                for location in website_text:
                    if location:
                        text += location.text.strip() + "\n"
            
            return text
        except Exception as e:
            print(f"⚠ Error while parsing HTML content: {e}")
            return ""

    def save_to_file(self, filename: str, text: str):
        """Saves scraped content to a text file."""
        try:
            file_path = os.path.join(self.output_dir, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"✅ Data saved in: {file_path}")
        except IOError as e:
            print(f"⚠ Error writing to file: {e}")

    def start_scraping(self):
        """Main method to start the scraping process."""
        print("🔍 Starting web scraping...")
        text_data = self.fetch_content()
        
        if text_data:
            self.save_to_file("108_famous_locations_in_india.txt", text_data)
        else:
            print("⚠ No data found to scrape!")
