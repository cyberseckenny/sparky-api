import asyncio
import aiohttp

# maximum amount of milliseconds a proxy is allowed to take to connect
proxy_timeout = 5000

# returns the ip of a proxy; if 
async def check_proxy(authentication_ip, username, password):
    try:
        async with aiohttp.ClientSession() as session:
            proxy = 'http://' + username + ':' + password + '@' + authentication_ip
            async with session.get('https://check-host.net/ip', proxy=proxy) as response:
                ip = await(response.text)
                return ip
    except Exception:
        return
    

# automatically rotate through valid proxies
async def request():
    pass
