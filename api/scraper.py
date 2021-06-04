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
    proxies = open(proxy_location, 'r')
    lines = proxies.readlines()
    proxies_line_count = len(lines) 
    proxies.close()
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
    return valid_proxies

# automatically rotate through valid proxies
async def request():
    

async def main():
    proxies = await check_proxies() 

if __name__ == '__main__':
    uvloop.install()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
