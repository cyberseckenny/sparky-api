import asyncio
import aiohttp
import uvloop
import undetected_chromedriver as uc
import re
import os
import zipfile
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options

chrome_binary_location = '/home/kenny/Builds/google-chrome/pkg/google-chrome/usr/bin/google-chrome-stable'        
chrome_executable_path='/home/kenny/Builds/chromedriver/src/chromedriver'

# uses chrome driver to scrape the elements of a page 
def get_request(url):
    driver = get_chromedriver()

    with driver:
        driver.get(url)
        parsed_text = parse(driver.page_source)
        return parsed_text
    
    driver.quit()
   
# returns the soup (beautifulsoup) of an html response
def parse(html):
    return BeautifulSoup(html, 'html.parser')
    
def scrape_name_mc():
    for i in range(0, 1000):
        soup = get_request('https://namemc.com/minecraft-names')
        name_containers = soup.find_all('div', class_ = re.compile('^row no-gutters py-1 px-3'))
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
            print(json_data)
            
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
            
async def main():
    print('Scraping NameMC...')
    scrape_name_mc()
    
if __name__ == '__main__':
    uvloop.install()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
