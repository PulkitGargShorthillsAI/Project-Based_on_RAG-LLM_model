import requests
from bs4 import BeautifulSoup
import os

base_url = "https://www.clubmahindra.com/blog/experience/indian-cities-for-food-lovers-across-india"
response = requests.get(base_url)
soup = BeautifulSoup(response.text, "lxml")


folder = "scraped_city_data"
os.makedirs(folder,exist_ok=True)


text = ""


content = soup.find("div",{"class":"lt-side"})

if content:
    text += '\n'
    locations = content.find_all(["h2","p"])


    for location in locations:
        if location:
            text += location.text.strip() + '\n'

print(text)


file_path = os.path.join(folder,"32_cities_for_food_in_india.txt")
with open(file_path,'w',encoding="utf-8") as f:
    f.write(text)