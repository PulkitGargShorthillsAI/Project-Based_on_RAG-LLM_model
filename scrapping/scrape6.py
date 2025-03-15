import requests
from bs4 import BeautifulSoup
import os

base_url = "https://en.wikipedia.org/wiki/Tourism_in_India_by_state#References"
response = requests.get(base_url)
soup = BeautifulSoup(response.text, "lxml")


folder = "scraped_city_data"
os.makedirs(folder,exist_ok=True)


text = ""


content = soup.find_all("div",{"class":"navbox","role":"navigation"})
if content:
    for location in content:
        if location:
            table = location.find("table")
            if table:
                for link in table.find_all('a'):
                    try:
                        if link:
                            print(link['href'])
                    except:
                        print()
                # text += location.find('h3').text.strip() + '\n'
                # for i in location.find_all('p'):
                #     text += i.text.strip() + '\n'

# print(text)


# file_path = os.path.join(folder,"best_locations_in_india.txt")
# with open(file_path,'w',encoding="utf-8") as f:
#     f.write(text)