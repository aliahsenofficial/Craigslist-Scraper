import gspread
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import Playwright, sync_playwright, expect

# Accessing google sheets
gc = gspread.service_account(filename='connor_secret_key.json')
sh = gc.open('Craigslist').sheet1

header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }

keywords = ['Apartment building', 'Plex', 'Multi', 'Apartment Complex']

states = ['https://geo.craigslist.org/iso/us/GA', 'https://geo.craigslist.org/iso/us/nc', 
          'https://geo.craigslist.org/iso/us/oh', 'https://geo.craigslist.org/iso/us/tn', 
          'https://geo.craigslist.org/iso/us/MO', 'https://geo.craigslist.org/iso/us/in',
          'https://geo.craigslist.org/iso/us/sc'
          ]

postIds = []      
titles = [] 

# Function to get listing details
def get_details(listing_url, Keyword, state_name, soup):
    Post_ID = soup.select('p.postinginfo')[1].text.replace('post id: ', '')
    Title = soup.find('span', {'id': 'titletextonly'}).text.strip()
    try: 
        Title += str(soup.find('small').text)
    except:
        Title += ''
    if (Post_ID not in postIds) and (Title not in titles):
        postIds.append(Post_ID)
        titles.append(Title)
        
        Days_Posted = soup.find('p', 'postinginfo').text.strip()
        try:
            Price = soup.find('span', 'price').text
        except:
            Price = 'N/A'
        try:
            Description = soup.find('section', {'id': 'postingbody'}).text.strip().replace('\n', ' ').strip('QR Code Link to This Post   ')
        except:
            Description = 'N/A'
        try:
            Location = soup.find('div', 'mapaddress').text
        except:
            Location = 'N/A'

        # Saving data in google sheets
        sh.append_row([listing_url, Post_ID, Title, Price,  Description, Days_Posted, Location, state_name, Keyword])


# Function to get city URLs from states 
def get_cities(state_url):
    response = requests.get(state_url, headers=header)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Getting the state name
    state_name = soup.find('li', 'crumb').text.strip()

    # Getting all cities
    soup = soup.find('ul', 'geo-site-list')
    cities = soup.find_all('a')
    i = 1

    # Opening brower window
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Vsiting all cities in the state
        for city in cities:
            for keyword in keywords:
                checking_url = city.get('href')

                city_url = checking_url + f'/search/rea?query={keyword}#search=1~gallery~0~0'
                print('\n', city_url)

                page.goto(url=city_url, timeout = 0)
                page.wait_for_timeout(5000)
                soup = BeautifulSoup(page.content(), 'html.parser')

                # Finding listings
                listings = soup.find_all('a', 'main')

                # if len(listings) == 0:
                #     listings = soup.find_all('li', 'result-row')

                for listing in listings:
                        listing_url = listing.get('href')

                        if checking_url in listing_url:
                            print(f"Listing # {i}: ", listing_url)

                            page.goto(url=listing_url)
                            page.wait_for_timeout(2000)
                            listing_soup = BeautifulSoup(page.content(), 'html.parser')
                            
                            # Visiting each listing and getting data using the function
                            get_details(listing_url, keyword, state_name, listing_soup)
                            i += 1
        browser.close()
    return i


if __name__ == '__main__':
    listings_scraped = 0
    for state in states[:3]:
        listings_scraped += get_cities(state)

    print("\n\n\nTotal Listings Scraper: ", listings_scraped)
