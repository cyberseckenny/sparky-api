import asyncio
import aiohttp

# TODO: before performing a complete scrape of NameMC, check the upcoming names to ensure that you have enough time to do it.
#       otherwise, you may miss out on some names, b/c NameMC will update and your offsets will be incorrect

# maximum amount of milliseconds a proxy is allowed to take to connect
proxy_timeout = 5000

# returns the ip of a proxy; if 
async def check_proxy(authentication_ip, username, password):
    try:
        session_timeout = aiohttp.ClientTimeout(total=None, sock_connect=proxy_timeout,sock_read=timeout_seconds)
        async with aiohttp.ClientSession(timeout=session_timeout) as session:
            proxy = 'http://' + username + ':' + password + '@' + authentication_ip
            async with session.get('https://check-host.net/ip', proxy=proxy) as response:
                ip = await(response.text)
                return ip
    except Exception:
        return

# automatically rotate through valid proxies
async def request():
    pass
