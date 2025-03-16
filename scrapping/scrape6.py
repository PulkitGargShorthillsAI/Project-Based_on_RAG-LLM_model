import requests
from bs4 import BeautifulSoup
import os
import json

base_url = "https://www.dookinternational.com/countries"
response = requests.get(base_url)
soup = BeautifulSoup(response.text, "lxml")




folder = "scraped_city_data"
os.makedirs(folder,exist_ok=True)


text = ""

def get_data(base_url):
    text = ""
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, "lxml")

    text += soup.find('div',{"class":"col-12 mb-3"}).text.strip()

    content = soup.find_all('div',{"class":"brick"})

    for c in content:
        text += '\n' + c.find('h3').text.strip() + '\n'
        text += c.find('p').text.strip() + '\n'

    return text

content = soup.find_all("div",{"class":"col-md-4 col-lg-4 col-sm-6 col-xs-12"})
if content:
    for location in content:
        if location:
            text += location.find('h6').text + '\n'
            
            # url = location.find('a',{"class":"package-slider-attraction"})
            # if(url):
            #     text += get_data(url['href'])


for i in range(2,16):
    try:
        base_url = f"https://www.dookinternational.com/countries/?page={i}"
        response = requests.get(base_url)
        obj= json.loads(response.text)
        soup = BeautifulSoup(obj['view'], "lxml")
        content = soup.find_all("div",{"class":"col-md-4 col-lg-4 col-sm-6 col-xs-12"})
        if content:
            for location in content:
                if location:
                    text += location.find('h6').text + '\n'
                    
                    # url = location.find('a',{"class":"package-slider-attraction"})
                    # if(url):
                    #     text += get_data(url['href'])
    except:
        print("something went wrong")

print(text)


# file_path = os.path.join(folder,"120_countries_data.txt")
# with open(file_path,'w',encoding="utf-8") as f:
#     f.write(text)