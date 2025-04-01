import requests
from bs4 import BeautifulSoup
import os

class IncredibleIndiaScraper:
    """Scrapes data from the Incredible India website about famous cities in India."""
    
    def __init__(self, base_url: str, output_dir: str = "scraped_city_data"):
        self.base_url = base_url
        self.output_dir = output_dir
        self.web_pages = 0  # Counter for pages visited
        os.makedirs(self.output_dir, exist_ok=True)

    def get_location_urls(self) -> list:
        """Fetches all city URLs from the main page."""
        try:
            response = requests.get(self.base_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching main page: {e}")
            return []

        try:
            soup = BeautifulSoup(response.text, "lxml")
            return [a['href'] for a in soup.find_all("a", {"class": "btn btn-primary"})]
        except Exception as e:
            print(f"Error parsing main page HTML: {e}")
            return []

    def scrape_city_data(self, city_url: str):
        """Scrapes main city data along with its locations and saves it to a file."""
        self.web_pages += 1
        try:
            response = requests.get(city_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching city page {city_url}: {e}")
            return

        try:
            soup = BeautifulSoup(response.text, "lxml")
            city_name = city_url.rstrip("/").split("/")[-1]
            city_file = os.path.join(self.output_dir, f"{city_name}.txt")

            text = f"\n\n{city_name.upper()}\n"
            contents = soup.find("div", {"class": "col-sm-12 col-md-7 col-lg-7 inc-tilemap__right"})

            if contents:
                for content in contents.find_all(["h2", "p"]):
                    text += content.text.strip() + "\n"

            # Extract and scrape location pages
            location_links = self.get_location_links(soup)
            for loc_url in location_links:
                full_loc_url = loc_url if loc_url.startswith("http") else self.base_url + loc_url
                text += self.scrape_location_data(full_loc_url)

            # Save content
            try:
                with open(city_file, "w", encoding="utf-8") as f:
                    f.write(text)

                print(f"Saved: {city_file}")
            except Exception as e:
                print(f"Error saving city data for {city_url}: {e}")
        except Exception as e:
            print(f"Error processing city data for {city_url}: {e}")

    def get_location_links(self, soup) -> set:
        """Extracts location-specific URLs within a city page."""
        location_links = set()
        try:
            location_container = soup.find("div", {"class": "container responsivegrid inc-container pb-5 aem-GridColumn aem-GridColumn--default--12"})
            if location_container:
                for a in location_container.find_all("a", href=True):
                    location_links.add(a["href"])
        except Exception as e:
            print(f"Error extracting location links: {e}")
        return location_links

    def scrape_location_data(self, url: str) -> str:
        """Scrapes location-specific content from a given URL."""
        self.web_pages += 1
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching location page {url}: {e}")
            return ""

        try:
            soup = BeautifulSoup(response.text, "lxml")
            location_name = url.rstrip("/").split("/")[-1]

            if location_name == "attractions":
                return ""

            text = f"\n\n\n{location_name.upper()}\n"
            contents = soup.find("div", {"class": "col-sm-12 col-md-7 col-lg-7 inc-tilemap__right"})

            if contents:
                for content in contents.find_all(["h2", "p"]):
                    text += content.text.strip() + "\n"

            return text
        except Exception as e:
            print(f"Error processing location data for {url}: {e}")
            return ""

    def start_scraping(self):
        """Loops through all city URLs and scrapes data."""
        location_urls = self.get_location_urls()
        for city in location_urls:
            full_city_url = city if city.startswith("http") else self.base_url + city
            self.scrape_city_data(full_city_url)

        print(f"\nTotal locations scraped: {len(location_urls)}")
        print(f"Total web pages visited: {self.web_pages}")
