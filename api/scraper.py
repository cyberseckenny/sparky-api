import asyncio
import uvloop
import socket
import re
import os
import ssl
from datetime import datetime, timezone
from bs4 import BeautifulSoup

def socket_get_request():

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.create_default_context()
    sock = context.wrap_socket(sock, server_hostname='namemc.com')
    sock.connect(('namemc.com', 443))

    request = '\r\n'.join(('GET /minecraft-names HTTP/1.1',
                'Host: namemc.com',
                'User-Agent: Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0',
                '\r\n'))
    sock.send(request.encode())

    while True:
        new = sock.recv(4096)
        if not new:
            sock.close()
            break
        print(new)

# returns the soup (beautifulsoup) of an html response
def parse(html):
    return BeautifulSoup(html, 'html.parser')
    
def scrape_name_mc():
    for i in range(0, 1000):
        soup = None
        name_containers = soup.find_all('div', class_ =ere.compile('^row no-gutters py-1 px-3'))
        for name in name_containers:    
            player_name = name.find('a').text
            drop_time = name.find('time')['datetime']
            unix_drop_time = parse_time(drop_time)
            searches = name.find('div', class_ = 'col-auto col-lg order-lg-3 text-right tabular').text
            # set the searches to 0 if it's not a number, most likely a '-'
            if not searches.isnumeric():
                searches = 0 
            searches = int(searches)
                
            json_data = {'username': player_name, 'searches': searches, 'dropTime': unix_drop_time}  
            print(json_data)
            
# converts datetime into unix time
def parse_time(drop_time):
    time = datetime.strptime(drop_time, '%Y-%m-%dT%H:%M:%S.%fZ') 
    unix_time = int(time.replace(tzinfo=timezone.utc).timestamp())
    return unix_time

async def main():
    print('Scraping NameMC...')
    socket_get_request()
    return
    scrape_name_mc()
    
if __name__ == '__main__':
    uvloop.install()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
