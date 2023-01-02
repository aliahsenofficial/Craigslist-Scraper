import time
import requests
from csv import writer
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime, timedelta

# driver = webdriver.Chrome()
driver = webdriver.Chrome(executable_path="C:/Users/AliAhsen/Desktop/craiglist/chromedriver.exe")


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
def get_details(url, Keyword, State):
    driver.get(url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

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
        try:
            Date = datetime.today() - timedelta(days=int(Days_Posted))
        except:
            Date = 'N/A'
        try:
            Location = soup.find('div', 'mapaddress').text
        except:
            Location = 'N/A'

        listing_info = [url, Post_ID, Title, Price,  Description, Days_Posted, Date, Location, State, Keyword]
        thewriter.writerow(listing_info)


# Function to get city URLs from states 
def get_cities(state):
    response = requests.get(state, headers=header)

    soup = BeautifulSoup(response.text, 'html.parser')
    soup = soup.find('ul', 'geo-site-list')
    cities = soup.find_all('li')
    i = 0
    for city in cities[:]:
        for keyword in keywords:
            url = city.find('a')['href']
            url += f'/search/rea?query={keyword}#search=1~gallery~0~0'

            driver.get(url)
            time.sleep(5)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            listings = soup.find_all('div', 'gallery-card')
            for listing in listings:
                url = listing.find('a', 'titlestring')['href']
                print(f"Listing # {i}: ", url)
                get_details(url, keyword, state)
                i += 1
    return i


if __name__ == '__main__':
    with open('listing.csv', 'w', newline='', encoding='utf8') as f:
        thewriter = writer(f)
        csv_header = ['URL', 'Post ID', 'Title', 'Price',  'Description', 'Days Posted', 'Date', 'Location', 'State', 'Keyword']
        thewriter.writerow(csv_header)

        listings_scraped = 0
        for state in states[:]:
            listings_scraped += get_cities(state)

# all_city_urls = ['https://abilene.craigslist.org', 'https://amarillo.craigslist.org', 'https://austin.craigslist.org', 'https://beaumont.craigslist.org', 'https://brownsville.craigslist.org', 'https://collegestation.craigslist.org', 'https://corpuschristi.craigslist.org', 'https://dallas.craigslist.org', 'https://nacogdoches.craigslist.org', 'https://delrio.craigslist.org', 'https://elpaso.craigslist.org', 'https://galveston.craigslist.org', 'https://houston.craigslist.org', 'https://killeen.craigslist.org', 'https://laredo.craigslist.org', 'https://lubbock.craigslist.org', 'https://mcallen.craigslist.org', 'https://odessa.craigslist.org', 'https://sanangelo.craigslist.org', 'https://sanantonio.craigslist.org', 'https://sanmarcos.craigslist.org', 'https://bigbend.craigslist.org', 'https://texarkana.craigslist.org', 'https://texoma.craigslist.org', 'https://easttexas.craigslist.org', 'https://victoriatx.craigslist.org', 'https://waco.craigslist.org', 'https://wichitafalls.craigslist.org', 'https://chattanooga.craigslist.org', 'https://clarksville.craigslist.org', 'https://cookeville.craigslist.org', 'https://jacksontn.craigslist.org', 'https://knoxville.craigslist.org', 'https://memphis.craigslist.org', 'https://nashville.craigslist.org', 'https://tricities.craigslist.org', 'https://charleston.craigslist.org', 'https://columbia.craigslist.org', 'https://florencesc.craigslist.org', 'https://greenville.craigslist.org', 'https://hiltonhead.craigslist.org', 'https://myrtlebeach.craigslist.org', 'https://asheville.craigslist.org', 'https://boone.craigslist.org', 'https://charlotte.craigslist.org', 'https://eastnc.craigslist.org', 'https://fayetteville.craigslist.org', 'https://greensboro.craigslist.org', 'https://hickory.craigslist.org', 'https://onslow.craigslist.org', 'https://outerbanks.craigslist.org', 'https://raleigh.craigslist.org', 'https://wilmington.craigslist.org', 'https://winstonsalem.craigslist.org', 'https://columbiamo.craigslist.org', 'https://joplin.craigslist.org', 'https://kansascity.craigslist.org', 'https://kirksville.craigslist.org', 'https://loz.craigslist.org', 'https://semo.craigslist.org', 'https://springfield.craigslist.org', 'https://stjoseph.craigslist.org', 'https://stlouis.craigslist.org', 'https://bloomington.craigslist.org', 'https://evansville.craigslist.org', 'https://fortwayne.craigslist.org', 'https://indianapolis.craigslist.org', 'https://kokomo.craigslist.org', 'https://tippecanoe.craigslist.org', 'https://muncie.craigslist.org', 'https://richmondin.craigslist.org', 'https://southbend.craigslist.org', 'https://terrehaute.craigslist.org', 'chicago.craigslist.org/nwi/', 'https://bgky.craigslist.org', 'https://cincinnati.craigslist.org', 'https://eastky.craigslist.org', 'https://huntington.craigslist.org', 'https://lexington.craigslist.org', 'https://louisville.craigslist.org', 'https://owensboro.craigslist.org', 'https://westky.craigslist.org', 
#             'https://gulfport.craigslist.org', 'https://hattiesburg.craigslist.org', 'https://jackson.craigslist.org', 'https://memphis.craigslist.org', 'https://meridian.craigslist.org', 'https://northmiss.craigslist.org', 'https://natchez.craigslist.org', 'https://albanyga.craigslist.org', 'https://athensga.craigslist.org', 'https://atlanta.craigslist.org', 'https://augusta.craigslist.org', 'https://brunswick.craigslist.org', 'https://columbusga.craigslist.org', 'https://macon.craigslist.org', 'https://nwga.craigslist.org', 'https://savannah.craigslist.org', 'https://statesboro.craigslist.org', 'https://valdosta.craigslist.org', 'https://fortsmith.craigslist.org', 'https://lawton.craigslist.org', 'https://enid.craigslist.org', 'https://oklahomacity.craigslist.org', 'https://stillwater.craigslist.org', 'https://texoma.craigslist.org', 'https://tulsa.craigslist.org', 'https://daytona.craigslist.org', 'https://keys.craigslist.org', 'https://fortmyers.craigslist.org', 'https://gainesville.craigslist.org', 'https://cfl.craigslist.org', 'https://jacksonville.craigslist.org', 'https://lakeland.craigslist.org', 'https://lakecity.craigslist.org', 'https://ocala.craigslist.org', 'https://okaloosa.craigslist.org', 'https://orlando.craigslist.org', 'https://panamacity.craigslist.org', 'https://pensacola.craigslist.org', 'https://sarasota.craigslist.org', 'https://miami.craigslist.org', 'https://spacecoast.craigslist.org', 'https://staugustine.craigslist.org', 'https://tallahassee.craigslist.org', 'https://tampa.craigslist.org', 'https://treasure.craigslist.org']
# all_keywords = ['Triplex', 'apartment building', 'Fourplex', 'Four plex', '4plex', '4 plex','4-plex','5plex','5 plex','6plex','6 plex',
#             '8 plex','8plex','8-plex','Plex','Qaudplex','Multifamily', 'Multi-family','Multi family','Multiplex','Apartment complex',
#             'Investor Property','Investor Special','Fixer Upper'
#             ]