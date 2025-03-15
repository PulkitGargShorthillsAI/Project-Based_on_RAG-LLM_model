import requests
from bs4 import BeautifulSoup
import os

base_url = "https://www.bucketlisttravels.com/round-up/100-bucket-list-destinations"
response = requests.get(base_url)
soup = BeautifulSoup(response.text, "lxml")


def get_country_details(base_url):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, "lxml")
    text = ""

    articles = soup.find_all("article",{"class":"listing-card bg-white shadow-listing"})
    for article in articles:
        if article:
            text += article.find("h2").text.strip() + '\n'
            for p in article.find_all("p"):
                text += p.text.strip() + "\n"
            text += '\n'
    return text


def get_destination_details(base_url):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, "lxml")
    text = ""

    div = soup.find("div",{"class":"our-review"})
    if div:
        for p in div.find_all('p'):
            if p:
                text += p.text.strip() + "\n"
            text += '\n'
        return text
folder = "scraped_city_data"
os.makedirs(folder,exist_ok=True)


text = ""
web_pages = 0

content = soup.find("div",{"class":"flex flex-col gap-8"})

if content:
    locations = content.find_all("article",{"class":"listing-card bg-white shadow-listing"})
    print(len(locations))


    for location in locations:
        if location:
            text += location.find("h2").text.strip() + '\n'
            for p in location.find_all("p"):
                text += p.text.strip() + "\n"
            text += '\n'

            url = location.find('a',{"class":"button smooth focus:outline-none border-2 flex items-center justify-center gap-x-1 rounded-sm bg-theme-action hover:bg-theme-lightskyblue tracking-wider focus:bg-theme-lightskyblue border-theme-action normal px-2 py-1 font-semibold uppercase"})
            if url:
                web_pages += 1
                print(url['href'])
                if (url['href'].split('/')[1] == 'experience'):
                    text += get_destination_details("https://www.bucketlisttravels.com" + url['href'])
                elif (url['href'].split('/')[1] == 'destination'):
                    text += get_destination_details("https://www.bucketlisttravels.com" + url['href'])
                else:
                    text += get_country_details(url['href'])


print(web_pages)
file_path = os.path.join(folder,"international_locations.txt")
with open(file_path,'w',encoding="utf-8") as f:
    f.write(text)