import requests
from bs4 import BeautifulSoup
import os

base_url = ["https://www.holidify.com/collections/monuments-of-india","https://www.holidify.com/collections/one-places-from-each-state"]
folder = "scraped_city_data"
os.makedirs(folder,exist_ok=True)

def scrapper(base_url):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, "lxml")

    text = ""
    content = soup.find_all("div",{"class":"col-12 col-md-6 pr-md-3"})
    for location in content:
        if location:
            text += location.find("h3",{"class":"card-heading"}).text.strip()
            text += location.find("p",{"class","card-text"}).text.strip() + '\n'

    return text


for url in base_url:
    text = scrapper(url)
    file_path = os.path.join(folder,f"{url.split('/')[-1]}.txt")
    with open(file_path,'w',encoding="utf-8") as f:
        f.write(text)