import requests
from bs4 import BeautifulSoup
import os
import json

base_url = "https://en.wikipedia.org/wiki/Visa_requirements_for_Indian_citizens"
response = requests.get(base_url)
soup = BeautifulSoup(response.text, "lxml")


folder = "scraped_city_data"
os.makedirs(folder,exist_ok=True)


text = ""


content = soup.find("div",{"class":"mw-content-ltr mw-parser-output"}).find_all('table')
print(content)
if content:
    for c in content:
        rows = c.find_all("tr")

        for row in rows:
            for td in row.find_all("td"):
                text += td.text + " "
        text += '\n'


file_path = os.path.join(folder,"visa_requirements.txt")
with open(file_path,'w',encoding="utf-8") as f:
    f.write(text)