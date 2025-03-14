import requests
from bs4 import BeautifulSoup
import os

base_url = "https://traveltriangle.com/blog/places-to-visit-in-india-before-you-turn-30/"
response = requests.get(base_url)
soup = BeautifulSoup(response.text, "lxml")


folder = "scraped_city_data"
os.makedirs(folder,exist_ok=True)


text = ""


content = soup.find("div",{"class":"blog-excerpt fb-heart"})

if content:
    website_text = content.find_all(["p","h3"])

for location in website_text:
    if location:
        text += location.text.strip() + '\n'

print(text)


file_path = os.path.join(folder,"108_famous_locations_in_india.txt")
with open(file_path,'w',encoding="utf-8") as f:
    f.write(text)