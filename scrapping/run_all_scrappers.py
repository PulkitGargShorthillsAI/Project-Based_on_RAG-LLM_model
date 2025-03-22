from scrape1 import IncredibleIndiaScraper
from scrape2 import TravelScraper
from scrape3 import HolidifyScraper
from scrape4 import FoodCityScraper
from scrape5 import BucketListScraper
from scrape6 import DookInternationalScraper
from scrape7 import VisaRequirementScraper

def safe_scrape(scraper, name):
    try:
        print(f"Starting scraper: {name}")
        scraper.start_scraping()
        print(f"Completed scraper: {name}")
    except Exception as e:
        print(f"Error in {name}: {e}")

# Scraper 1
scraper = IncredibleIndiaScraper(base_url="https://www.incredibleindia.gov.in/en")
safe_scrape(scraper, "IncredibleIndiaScraper")

# Scraper 2
scraper = TravelScraper("https://traveltriangle.com/blog/places-to-visit-in-india-before-you-turn-30/")
safe_scrape(scraper, "TravelScraper")

# Scraper 3
urls = [
    "https://www.holidify.com/collections/monuments-of-india",
    "https://www.holidify.com/collections/one-places-from-each-state"
]
scraper = HolidifyScraper(urls)
safe_scrape(scraper, "HolidifyScraper")

# Scraper 4
url = "https://www.clubmahindra.com/blog/experience/indian-cities-for-food-lovers-across-india"
scraper = FoodCityScraper(url)
safe_scrape(scraper, "FoodCityScraper")

# Scraper 5
scraper = BucketListScraper()
safe_scrape(scraper, "BucketListScraper")

# Scraper 6
scraper = DookInternationalScraper()
safe_scrape(scraper, "DookInternationalScraper")

# Scraper 7
scraper = VisaRequirementScraper()
safe_scrape(scraper, "VisaRequirementScraper")
