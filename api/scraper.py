import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from api import addUpcomingNames
import json
import cloudscraper
import time
from datetime import datetime

SCRAPER = cloudscraper.create_scraper() 
SCRAPER_COUNT = 0
SCRAPER_HEADERS = {}
SCRAPER_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0'
REQUEST_DISTANCE = 3

# cloud scraper used here to scrape the page
def get_request(url):
    global SCRAPER
    global SCRAPER_COUNT
    global SCRAPER_HEADERS

    if SCRAPER_HEADERS is None:
        get_new_headers(url)

    # if cloudflare denies our request, we keep on trying for a new session id until they don't
    while True:
        response = SCRAPER.get(url, headers=SCRAPER_HEADERS)
        time.sleep(REQUEST_DISTANCE)
        if response.headers['Connection'] == 'close':
            get_new_headers(url)
        else:
            break

    SCRAPER_COUNT = SCRAPER_COUNT + 1
    return [parse(response.text), SCRAPER_COUNT]

def get_new_headers(url):
    global SCRAPER
    global SCRAPER_COUNT
    global SCRAPER_HEADERS
    # we will keep increasing this, giving cloudflare more time to let us in
    scaling_request_distance = REQUEST_DISTANCE

    # we don't stop trying for new headers until cloudflare lets us through
    while True:
        now = datetime.now()
        headers = {'User-Agent': SCRAPER_USER_AGENT}
        SCRAPER = cloudscraper.create_scraper()
        response = SCRAPER.get(url, stream=True, headers=headers)
        time.sleep(REQUEST_DISTANCE)
        if (response.headers['Connection'] == 'close'):
            print('New session creation failed. Trying again momentarily... ' + str(now))
        else:
            print('Succesfully created new session.')
            break
        scaling_request_distance = scaling_request_distance * 1.2
        time.sleep(scaling_request_distance)

    SCRAPER_HEADERS = {'User-Agent': SCRAPER_USER_AGENT,
                       'Referer': 'https://namemc.com',
                       'Alt-Used': 'namemc.com',
                       'Connection': 'keep-alive',
                       'Upgrade-Insecure-Requests': '1',
                       'Sec-GPC': '1',
                       'TE': 'Trailers'}

    SCRAPER_COUNT = 0
 
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

    i = 0
    while True:
        if i == 0:
            json_data, scraper_count = scrape('https://namemc.com/minecraft-names?sort=asc&length_op=eq&length=3&lang=&searches=0')
            addUpcomingNames(json_data, True, scraper_count)
        elif i == 10: # when to check for 3 letter names again 
            i = 0
            continue 
        else:
            json_data, scraper_count = scrape('https://namemc.com/minecraft-names')
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
