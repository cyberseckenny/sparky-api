import asyncio
import aiohttp
import uvloop
import driver_helper 
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options

# TODO: before performing a complete scrape of NameMC, check the upcoming names to ensure that you have enough time to do it.
#       otherwise, you may miss out on some names, b/c NameMC will update and your offsets will be incorrect

# maximum amount of seconds a proxy is allowed to take to connect
proxy_timeout = 15
# location of proxy file
proxy_location = 'proxies'

# stores a proxy ip as well as its credentials
class Proxy:
    def __init__(self, authentication_proxy, proxy_host, proxy_port, proxy_username, proxy_password, ip):
        self.authentication_proxy = authentication_proxy
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password
        self.ip = ip

# returns the ip and authentication ip of a proxy; authentication ip is the ip used to login into the proxy 
async def check_proxy(authentication_ip, username, password):
    try:
        client_timeout = aiohttp.ClientTimeout(total=proxy_timeout)
        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            proxy = 'http://' + username + ':' + password + '@' + authentication_ip
            async with session.get('https://check-host.net/ip', proxy=proxy) as response:
                ip = await(response.text())
                return [ip, proxy]
    except Exception:
        return None

async def check_proxies():
    proxies_file = open(proxy_location, 'r')
    lines = proxies_file.readlines()
    proxies_line_count = len(lines) 
    proxies_file.close()
    valid_proxies = []

    async def check(i):
        line = lines[i].strip()
        split = line.split(':')

        authentication_ip = split[0] + ':' + split[1]
        username = split[2]
        password = split[3]
        proxy = await check_proxy(authentication_ip, username, password)
        if proxy is not None:
            valid_proxies.append(Proxy(proxy[1], split[0], split[1], split[2], split[3], proxy[0]))

    coroutines = [check(i) for i in range(proxies_line_count)]
    await asyncio.gather(*coroutines)
    
    # loops through all proxies and removes duplicate
    for x in valid_proxies:
        for y in valid_proxies:
            if x == y: # important check to make sure we don't remove every proxy
                continue
            if x.ip == y.ip:
                valid_proxies = remove_proxy(valid_proxies, y)

    return valid_proxies

# removes a proxy from a proxy array and returns the modified version
def remove_proxy(proxies, to_remove):
    for i in range(0, len(proxies)):
        proxy = proxies[i]
        if proxy == to_remove:
            proxies.pop(i)
            break

    return proxies

# automatically rotate throughs valid proxies and does a get request
def get_request(proxies, url):
    proxy = proxies[0]
    popped_proxy = proxies.pop(0)
    proxies.append(popped_proxy)
     
    chrome_driver = driver_helper.Driver(proxy.proxy_host, proxy.proxy_port, proxy.proxy_username, proxy.proxy_password)
    driver = chrome_driver.get_chromedriver()

    with driver:
        driver.get(url)
        parsed_text = parse(driver.page_source)
        return parsed_text
   
# returns the soup (beautifulsoup) of an html response
def parse(html):
    return BeautifulSoup(html, 'html.parser')
    
def scrape_name_mc(proxies):
    for i in range(0, len(proxies)):
        get_request(proxies, 'https://namemc.com/minecraft-names')

async def main():
    proxies = await check_proxies() 
    scrape_name_mc(proxies)
    
if __name__ == '__main__':
    uvloop.install()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
