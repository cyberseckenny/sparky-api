import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from api import addUpcomingNames
import json
import cloudscraper
import time
from datetime import datetime
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import HardwareType, Popularity, SoftwareName, OperatingSystem, SoftwareType
from bson import json_util

SCRAPER = cloudscraper.create_scraper() 
SCRAPER_COUNT = 0
SCRAPER_HEADERS = {}
SCRAPER_USER_AGENT = None

software_names = [SoftwareName.CHROME.value, SoftwareName.CHROMIUM.value, SoftwareName.FIREFOX.value, SoftwareName.ANDROID.value]
operating_systems = [OperatingSystem.LINUX.value, OperatingSystem.WINDOWS.value, OperatingSystem.MAC.value]
popularity = [Popularity.POPULAR.value]
hardware_types = [HardwareType.MOBILE.value, HardwareType.COMPUTER.value]
software_types = [SoftwareType.WEB_BROWSER.value]
USER_AGENT_ROTATOR = UserAgent(software_names=software_names, operating_systems=operating_systems, hardware_types=hardware_types, popularity=popularity, software_types=software_types)

REQUEST_DISTANCE = 3

# cloud scraper used here to scrape the page
def get_request(url):
    global SCRAPER
    global SCRAPER_COUNT
    global SCRAPER_HEADERS

    if SCRAPER_HEADERS is None:
        get_new_headers(url)

    # if cloudflare denies our request, we keep on trying for a new session id until they don't
    response = SCRAPER.get(url, headers=SCRAPER_HEADERS)
    if response.headers['Connection'] == 'close':
         response = get_new_headers(url)

    SCRAPER_COUNT = SCRAPER_COUNT + 1
    return [parse(response.text), SCRAPER_COUNT]

def get_new_headers(url):
    global SCRAPER
    global SCRAPER_COUNT
    global SCRAPER_HEADERS

    # we don't stop trying for new headers until cloudflare lets us through
    while True:
        time.sleep(REQUEST_DISTANCE)

        now = datetime.now()
        SCRAPER_USER_AGENT = USER_AGENT_ROTATOR.get_random_user_agent() 
        headers = {'User-Agent': SCRAPER_USER_AGENT}
        SCRAPER = cloudscraper.create_scraper()
        response = SCRAPER.get(url, stream=True, headers=headers)
        if (response.headers['Connection'] == 'close'):
            print('Session creation failed. Trying again momentarily... ' + str(now))
        else:
            print('Succesfully created new session.')
            break
        
    SCRAPER_HEADERS = {'User-Agent': SCRAPER_USER_AGENT,
                       'Referer': 'https://namemc.com',
                       'Alt-Used': 'namemc.com',
                       'Connection': 'keep-alive',
                       'Upgrade-Insecure-Requests': '1',
                       'Sec-GPC': '1',
                       'TE': 'Trailers'}

    time.sleep(REQUEST_DISTANCE)
    SCRAPER_COUNT = 0
    return SCRAPER.get(url, headers=SCRAPER_HEADERS)
     
# returns the soup (beautifulsoup) of an html response
def parse(html):
    return BeautifulSoup(html, 'html.parser')
    
def scrape_name_droptime(name):
    url = 'https://namemc.com/search?q=' + name

    scraper = cloudscraper.create_scraper()
    text = scraper.get(url).text
    soup = parse(text)

    containers = soup.find_all('div', class_ = re.compile('^col-sm-6 my-1'))
    if len(containers) == 4:
        time = soup.find('time', class_ = 'text-nowrap')
        utc_drop_time = time['datetime']
        unix_drop_time = parse_time(utc_drop_time)
        json_data = {"name": name, "unixDropTime": unix_drop_time, "utcDropTime": utc_drop_time}
    else:
        json_data = {"error": "INVALID_NAME"}

    return json_data

def scrape_name_mc():
    def scrape(url):
        time.sleep(REQUEST_DISTANCE)
        soup, scraper_count = get_request(url)
        name_containers = soup.find_all('div', class_ = re.compile('^row no-gutters py-1 px-3'))
        json_data_array = []
        for name in name_containers:    
            player_name = name.find('a').text
            drop_time = name.find('time')['datetime']
            unix_drop_time = parse_time(drop_time)
            utc_drop_time = drop_time
            searches = name.find('div', class_ = 'col-auto col-lg order-lg-3 text-right tabular').text
            # set the searches to 0 if it's not a number, most likely a '-'
            if not searches.isnumeric():
                searches = 0 
            searches = int(searches)
                
            json_data = {"name": player_name, "searches": searches, "unixDropTime": unix_drop_time, "utcDropTime": utc_drop_time}  
            json_data_array.append(json_data)

        return [json.dumps(json_data_array), scraper_count]

    # checks if json data is correct
    def check_json_validity(json_data):
        data = json_util.loads(json_data)
        if len(data) != 50:
            print('Scraper returned an invalid list, trying to scrape again...')
            time.sleep(REQUEST_DISTANCE)
            return False 
        return True 

    i = 0
    while True:
        if i == 0:
            json_data, scraper_count = scrape('https://namemc.com/minecraft-names?sort=asc&length_op=eq&length=3&lang=&searches=0')
            # json data was empty so we just try to scrape again
            if not check_json_validity(json_data):
                continue 
            addUpcomingNames(json_data, True, scraper_count)
        elif i == 10: # when to check for 3 letter names again 
            i = 0
            continue 
        else:
            json_data, scraper_count = scrape('https://namemc.com/minecraft-names')
            # json data was empty so we just try to scrape again
            if not check_json_validity(json_data):
                continue
            addUpcomingNames(json_data, False, scraper_count)
        i = i + 1
            
# converts datetime into unix time
def parse_time(drop_time):
    time = datetime.strptime(drop_time, '%Y-%m-%dT%H:%M:%S.%fZ') 
    unix_time = int(time.replace(tzinfo=timezone.utc).timestamp())
    return unix_time

def main():
    print('Scraping NameMC...')
    scrape_name_mc()

if __name__ == '__main__':
    main()
