import requests
from bs4 import BeautifulSoup
import os

class VisaRequirementScraper:
    """Scrapes visa requirements for Indian citizens from Wikipedia."""
    
    BASE_URL = "https://en.wikipedia.org/wiki/Visa_requirements_for_Indian_citizens"

    def __init__(self, output_dir="scraped_city_data", output_filename="visa_requirements.txt"):
        self.output_dir = output_dir
        self.output_filename = output_filename
        os.makedirs(self.output_dir, exist_ok=True)
        self.text = ""

    def fetch_soup(self):
        """Fetches and parses the Wikipedia page."""
        response = requests.get(self.BASE_URL)
        soup = BeautifulSoup(response.text, "lxml")
        return soup

    def scrape_data(self):
        """Extracts visa-related data from the webpage."""
        soup = self.fetch_soup()
        content = soup.find("div", {"class": "mw-content-ltr mw-parser-output"}).find_all('table')

        print(content)  # Debugging statement

        if content:
            for table in content:
                rows = table.find_all("tr")
                for row in rows:
                    for td in row.find_all("td"):
                        self.text += td.text + " "
                    self.text += '\n'

    def save_to_file(self):
        """Saves the scraped data into a text file."""
        file_path = os.path.join(self.output_dir, self.output_filename)
        with open(file_path, 'w', encoding="utf-8") as f:
            f.write(self.text)
        print(f"✅ Data saved in: {file_path}")

    def start_scraping(self):
        """Runs the entire scraping process."""
        self.scrape_data()
        self.save_to_file()


if __name__ == "__main__":
    scraper = VisaRequirementScraper()
    scraper.start_scraping()
