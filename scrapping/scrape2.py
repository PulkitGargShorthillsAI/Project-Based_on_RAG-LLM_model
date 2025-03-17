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
        response = requests.get(self.base_url)
        soup = BeautifulSoup(response.text, "lxml")

        text = ""
        content = soup.find("div", {"class": "blog-excerpt fb-heart"})
        
        if content:
            website_text = content.find_all(["p", "h3"])
            for location in website_text:
                if location:
                    text += location.text.strip() + "\n"

        return text

    def save_to_file(self, filename: str, text: str):
        """Saves scraped content to a text file."""
        file_path = os.path.join(self.output_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"✅ Data saved in: {file_path}")

    def start_scraping(self):
        """Main method to start the scraping process."""
        text_data = self.fetch_content()
        if text_data:
            self.save_to_file("108_famous_locations_in_india.txt", text_data)
        else:
            print("⚠ No data found to scrape!")


if __name__ == "__main__":
    scraper = TravelScraper("https://traveltriangle.com/blog/places-to-visit-in-india-before-you-turn-30/")
    scraper.start_scraping()
