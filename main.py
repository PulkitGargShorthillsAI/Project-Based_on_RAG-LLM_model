import requests
from bs4 import BeautifulSoup
import os






web_pages = 0  # Counter for pages visited
# Base URL
base_url = "https://www.incredibleindia.gov.in/en"


# Directory to store scraped data
output_dir = "scraped_city_data"
os.makedirs(output_dir, exist_ok=True)

# Fetch the main page
response = requests.get(base_url)
soup = BeautifulSoup(response.text, "lxml")

# Extract URLs of all famous cities in India
location_urls = [a['href'] for a in soup.find_all("a", {"class": "btn btn-primary"})]

def scrape_city_location_data(url: str):
    """Scrapes location-specific content from a given URL."""
    global web_pages
    web_pages += 1

    response = requests.get(url)
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


def scrape_city_data(city_url):
    """Scrapes main city data along with its locations and saves it to a file."""
    global web_pages
    web_pages += 1

    response = requests.get(city_url)
    soup = BeautifulSoup(response.text, "lxml")

    city_name = city_url.rstrip("/").split("/")[-1]
    city_file = os.path.join(output_dir, f"{city_name}.txt")

    text = f"\n\n{city_name.upper()}\n"
    contents = soup.find("div", {"class": "col-sm-12 col-md-7 col-lg-7 inc-tilemap__right"})

    if contents:
        for content in contents.find_all(["h2", "p"]):
            text += content.text.strip() + "\n"

    # Extract location-specific URLs within the city page
    location_links = set()
    location_container = soup.find("div", {"class": "container responsivegrid inc-container pb-5 aem-GridColumn aem-GridColumn--default--12"})

    if location_container:
        for a in location_container.find_all("a", href=True):
            location_links.add(a["href"])

    # Scrape location pages and append content to the same city file
    for loc_url in location_links:
        full_loc_url = loc_url if loc_url.startswith("http") else base_url + loc_url
        text += scrape_city_location_data(full_loc_url)

    # Save scraped content to a text file
    with open(city_file, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"✅ Saved: {city_file}")

# Loop through city URLs and scrape data
for city in location_urls:
    full_city_url = city if city.startswith("http") else base_url + city
    scrape_city_data(full_city_url)

print(f"\n🔹 Total locations scraped: {len(location_urls)}")
print(f"🔹 Total web pages visited: {web_pages}")
