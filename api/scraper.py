import re
import undetected_chromedriver as uc
from datetime import datetime, timezone
from bs4 import BeautifulSoup

chrome_binary_location = '/home/kenny/Builds/google-chrome/pkg/google-chrome/usr/bin/google-chrome-stable'        
chrome_executable_path='/home/kenny/Builds/chromedriver/src/chromedriver'

# uses chrome driver to scrape the elements of a page 
def get_request(url):
    driver = get_chromedriver()

    with driver:
        driver.get(url)
        parsed_text = parse(driver.page_source)
        driver.quit()
        return parsed_text
    
   
# returns the soup (beautifulsoup) of an html response
def parse(html):
    return BeautifulSoup(html, 'html.parser')
    
def scrape_name_mc():
    def scrape(url):
        soup = get_request(url)
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
                
            json_data = {'username': player_name, 'searches': searches, 'unixdropTime': unix_drop_time, 'utcDropTime': utc_drop_time}  
            json_data_array.append(json_data)

        return json_data_array

    i = 0
    while True:
        if i == 0:
            scrape('https://namemc.com/minecraft-names?sort=asc&length_op=eq&length=3&lang=&searches=0')
        elif i == 20: # checks for three letter names after every 20 scrapes 
            i = 0
            continue 
        else:
            scrape('https://namemc.com/minecraft-names')
        i = i + 1
            
# converts datetime into unix time
def parse_time(drop_time):
    time = datetime.strptime(drop_time, '%Y-%m-%dT%H:%M:%S.%fZ') 
    unix_time = int(time.replace(tzinfo=timezone.utc).timestamp())
    return unix_time

def get_chromedriver():
    chrome_options = uc.ChromeOptions()
    
    # binary locations
    chrome_options.binary_location = chrome_binary_location 
    chrome_options.headless = True
    chrome_options.add_argument('--headless')

    prefs = {'profile.managed_default_content_settings.images': 2,
             'profile.managed_default_content_settings.javascript': 2,
             'profile.managed_default_content_settings.stylesheet': 2,
             'profile.managed_default_content_settings.css': 2}
    chrome_options.add_experimental_option('prefs', prefs)

    # binary location
    driver = uc.Chrome(executable_path=chrome_executable_path,
                       chrome_options=chrome_options)
    return driver
            
def start():
    print('Scraping NameMC...')
    scrape_name_mc()
