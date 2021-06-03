import asyncio
import aiohttp

# TODO: before performing a complete scrape of NameMC, check the upcoming names to ensure that you have enough time to do it.
#       otherwise, you may miss out on some names, b/c NameMC will update and your offsets will be incorrect

# maximum amount of milliseconds a proxy is allowed to take to connect
proxy_timeout = 5000
# location of proxy file
proxy_location = 'proxies'

# returns the ip of a proxy; if 
async def check_proxy(authentication_ip, username, password):
    try:
        async with aiohttp.ClientSession() as session:
            proxy = 'http://' + username + ':' + password + '@' + authentication_ip
            async with session.get('https://check-host.net/ip', proxy=proxy) as response:
                ip = await(response.text)
                print(ip)
                return ip
    except Exception:
        return

async def check_proxies():
    proxies = open(proxy_location, 'r')
    lines = proxies.readlines()
    proxies_line_count = len(lines) 
    proxies.close()

    async def check(i):
        line = lines[i].strip()
        split = line.split(':')

        authentication_ip = split[0] + ':' + split[1]
        username = split[2]
        password = split[3]
        await check_proxy(authentication_ip, username, password)

    coroutines = [check(i) for i in range(proxies_line_count)]
    await asyncio.gather(*coroutines)
    
# automatically rotate through valid proxies
async def request():
    pass

async def main():
    await check_proxies() 

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
