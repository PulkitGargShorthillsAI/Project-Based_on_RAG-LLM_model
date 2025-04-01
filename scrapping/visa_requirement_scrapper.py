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
        try:
            response = requests.get(self.BASE_URL, timeout=10)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
            return BeautifulSoup(response.text, "lxml")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page: {e}")
            return None

    def scrape_data(self):
        """Extracts visa-related data from the webpage."""
        soup = self.fetch_soup()
        if soup is None:
            print("Skipping scraping due to fetch error.")
            return
        
        try:
            content = soup.find("div", {"class": "mw-content-ltr mw-parser-output"}).find_all('table')
            if not content:
                print("No visa requirement data found.")
                return
            
            for table in content:
                rows = table.find_all("tr")
                for row in rows:
                    for td in row.find_all("td"):
                        self.text += td.text.strip() + " "
                    self.text += '\n'
        except AttributeError as e:
            print(f"Error parsing the HTML structure: {e}")

    def save_to_file(self):
        """Saves the scraped data into a text file."""
        if not self.text:
            print("No data to save.")
            return
        
        try:
            file_path = os.path.join(self.output_dir, self.output_filename)
            with open(file_path, 'w', encoding="utf-8") as f:
                f.write(self.text)
            print(f"Data saved in: {file_path}")
        except OSError as e:
            print(f"Error saving file: {e}")

    def start_scraping(self):
        """Runs the entire scraping process."""
        self.scrape_data()
        self.save_to_file()

