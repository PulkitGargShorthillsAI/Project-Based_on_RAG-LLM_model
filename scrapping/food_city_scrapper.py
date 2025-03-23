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
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()  # Raise an error for bad responses
            soup = BeautifulSoup(response.text, "lxml")

            text = "\n"
            content = soup.find("div", {"class": "lt-side"})

            if not content:
                print("⚠ No relevant content found on the page.")
                return ""

            locations = content.find_all(["h2", "p"])
            for location in locations:
                if location:
                    text += location.text.strip() + "\n"

            return text

        except requests.exceptions.Timeout:
            print("⚠ Error: Request timed out.")
        except requests.exceptions.HTTPError as http_err:
            print(f"⚠ HTTP error occurred: {http_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"⚠ Error fetching {self.url}: {req_err}")
        except Exception as e:
            print(f"⚠ Unexpected error: {e}")
        
        return ""

    def save_to_file(self, filename, text):
        """Saves the scraped content to a text file."""
        try:
            file_path = os.path.join(self.output_dir, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"✅ Data saved in: {file_path}")
        except IOError as io_err:
            print(f"⚠ File writing error: {io_err}")
        except Exception as e:
            print(f"⚠ Unexpected error while saving file: {e}")

    def start_scraping(self):
        """Starts the scraping process."""
        print(f"🔍 Scraping: {self.url}")
        scraped_text = self.fetch_content()

        if scraped_text:
            filename = "32_cities_for_food_in_india.txt"
            self.save_to_file(filename, scraped_text)
        else:
            print("⚠ No data found!")
