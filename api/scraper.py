import asyncio
import aiohttp
import uvloop

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

# automatically rotate through valid proxies
async def request(proxies, url, post_data):
    proxy = proxies[0]
    popped_proxy = proxies.pop(0)    
    proxies.append(popped_proxy)
       
    try: 
         async with aiohttp.ClientSession(timeout=client_timeout) as session:
            async with session.post(url, data=post_data, proxy=proxy.authentication_ip) as response:
                text = await(response.text())
                return text 
    except Exception:
        return None
   

async def main():
    proxies = await check_proxies() 
    
    coroutines = [request(proxies) for i in range(500)]
    await asyncio.gather(*coroutines)

if __name__ == '__main__':
    uvloop.install()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
