import requests
from bs4 import BeautifulSoup
import os

class FoodCityScraper:
    """Scrapes food-related travel data from Club Mahindra's blog."""

    def __init__(self, url, output_dir="scraped_city_data"):
        self.url = url
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def fetch_content(self):
        """Fetches and extracts food-related city content from the given URL."""
        try:
            response = requests.get(self.url)
            response.raise_for_status()  # Raise an error for bad responses
            soup = BeautifulSoup(response.text, "lxml")

            text = "\n"
            content = soup.find("div", {"class": "lt-side"})

            if content:
                locations = content.find_all(["h2", "p"])
                for location in locations:
                    if location:
                        text += location.text.strip() + "\n"

            return text

        except requests.exceptions.RequestException as e:
            print(f"⚠ Error fetching {self.url}: {e}")
            return ""

    def save_to_file(self, filename, text):
        """Saves the scraped content to a text file."""
        file_path = os.path.join(self.output_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"✅ Data saved in: {file_path}")

    def start_scraping(self):
        """Starts the scraping process."""
        print(f"🔍 Scraping: {self.url}")
        scraped_text = self.fetch_content()

        if scraped_text:
            filename = "32_cities_for_food_in_india.txt"
            self.save_to_file(filename, scraped_text)
        else:
            print("⚠ No data found!")


if __name__ == "__main__":
    url = "https://www.clubmahindra.com/blog/experience/indian-cities-for-food-lovers-across-india"
    scraper = FoodCityScraper(url)
    scraper.start_scraping()
