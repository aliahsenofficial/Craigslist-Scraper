import time
import requests
from csv import writer
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from playwright.sync_api import Playwright, sync_playwright, expect

header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }

keywords = ['Apartment building', 'Plex', 'Multi', 'Apartment Complex']

states = ['https://geo.craigslist.org/iso/us/tx', 'https://geo.craigslist.org/iso/us/tn', 
          'https://geo.craigslist.org/iso/us/sc', 'https://geo.craigslist.org/iso/us/nc', 
          'https://geo.craigslist.org/iso/us/MO', 'https://geo.craigslist.org/iso/us/in', 
          'https://geo.craigslist.org/iso/us/GA', 'https://geo.craigslist.org/iso/us/IN'
          ]

postIds = []      
titles = [] 

# Function to get listing details
def get_details(url, Keyword, State, page):
    page.goto(url=url)
    page.wait_for_timeout(2000)
    soup = BeautifulSoup(page.content(), 'html.parser')

    Post_ID = soup.select('p.postinginfo')[1].text.replace('post id: ', '')
    Title = soup.find('span', {'id': 'titletextonly'}).text.strip()
    try: 
        Title += str(soup.find('small').text)
    except:
        Title += ''
    if Post_ID not in postIds and Title not in titles:
        postIds.append(Post_ID)
        titles.append(Title)
        
        try:
            Price = soup.find('span', 'price').text
        except:
            Price = 'N/A'
        try:
            Description = soup.find('section', {'id': 'postingbody'}).text.strip().replace('\n', ' ').strip('QR Code Link to This Post   ')
        except:
            Description = 'N/A'

        Days_Posted = soup.find('p', 'postinginfo').text.replace('Posted\n', '').replace('\n', '').strip().replace(' days ago', '')
        # try:
        #     Date = datetime.today() - timedelta(days=int(Days_Posted))
        # except:
        #     Date = 'N/A'
        try:
            Location = soup.find('div', 'mapaddress').text
        except:
            Location = 'N/A'

        listing_info = [url, Post_ID, Title, Price,  Description, Days_Posted, Location, State, Keyword]
        thewriter.writerow(listing_info)


# Function to get city URLs from states 
def get_cities(state):
    response = requests.get(state, headers=header)

    soup = BeautifulSoup(response.text, 'html.parser')
    soup = soup.find('ul', 'geo-site-list')
    cities = soup.find_all('li')
    i = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for city in cities[:1]:
            for keyword in keywords:
                url = city.find('a')['href']
                url += f'/search/rea?query={keyword}#search=1~gallery~0~0'
                print('\n')
                print(url)

                page.goto(url=url)
                page.wait_for_timeout(5000)
                soup = BeautifulSoup(page.content(), 'html.parser')

                listings = soup.find_all('div', 'gallery-card')
                for listing in listings:
                    try:
                        url = listing.find('a', 'titlestring')['href']
                        print(f"Listing # {i+1}: ", url)
                        get_details(url, keyword, state, page)
                        i += 1
                    except:
                        pass
        browser.close()
    return i


if __name__ == '__main__':
    with open('listing.csv', 'w', newline='', encoding='utf8') as f:
        thewriter = writer(f)
        csv_header = ['URL', 'Post ID', 'Title', 'Price',  'Description', 'Days Posted', 'Location', 'State', 'Keyword']
        thewriter.writerow(csv_header)
        
        listings_scraped = 0
        for state in states[:1]:
            listings_scraped += get_cities(state)