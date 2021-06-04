import asyncio
import aiohttp
import uvloop
from bs4 import BeautifulSoup

# TODO: before performing a complete scrape of NameMC, check the upcoming names to ensure that you have enough time to do it.
#       otherwise, you may miss out on some names, b/c NameMC will update and your offsets will be incorrect

# maximum amount of seconds a proxy is allowed to take to connect
proxy_timeout = 15
# location of proxy file
proxy_location = 'proxies'

# stores a proxy ip as well as its credentials
class Proxy:
    def __init__(self, authentication_proxy, ip):
        self.authentication_proxy = authentication_proxy
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
            valid_proxies.append(Proxy(proxy[1], proxy[0]))

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
async def get_request(proxies, url):
    proxy = proxies[0]
    popped_proxy = proxies.pop(0)    
    proxies.append(popped_proxy)
       
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0', 
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Accept-Language': 'en-US,en;q=0.5',
               'Accept-Encoding': 'gzip, deflate, br',
               'DNT': 1,
               'Connection': 'keep-alive'}

    try: 
         async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, proxy=proxy.authentication_proxy) as response:
                text = await(response.text())
                parsed_text = parse(text)
                return parsed_text

    except Exception as e:
        # TODO: implement checks here, we might need to know why are requests aren't sending
        return None
   
# returns the soup (beautifulsoup) of an html response
def parse(html):
    return BeautifulSoup(html, 'html.parser')
    
async def scrape_name_mc(proxies):
    coroutines = [get_request(proxies, 'https://namemc.com') for i in range(0, len(proxies))]
    await asyncio.gather(*coroutines)

async def main():
    proxies = await check_proxies() 
    await scrape_name_mc(proxies)
    
if __name__ == '__main__':
    uvloop.install()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
