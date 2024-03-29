from datetime import datetime, timezone
from datetime import datetime
import json
import re
from stem import Signal
from stem.control import Controller

from bs4 import BeautifulSoup
from bson import json_util
import requests

import configparser
from pymongo import MongoClient

config = configparser.ConfigParser()
config.read('config.ini')

mongo_section = config['MONGO']
MONGO_IP = mongo_section['IP']

scraper_section = config['SCRAPER']
FLARE_SOLVER_IP = scraper_section['FLARE_SOLVER_IP']
TOR_IP = scraper_section['TOR_IP']

mongo_client = MongoClient('mongodb://' + MONGO_IP + ':27017')
db = mongo_client.upcoming_names
UPCOMING = db.upcoming
UPCOMING_THREE = db.upcoming_three


# adds names to Mongo


def addUpcomingNames(json_data: str, three: bool):
    data = json_util.loads(json_data)
    now = datetime.now()
    if three:
        UPCOMING_THREE.drop()
        UPCOMING_THREE.insert_many(data)
        print(
            'Updated upcoming three letter names at ' + str(now))
    else:
        UPCOMING.drop()
        UPCOMING.insert_many(data)
        print(
            'Updated upcoming names at ' + str(now))

# web driver scrapes page and returns text


def get_request(url: str):
    payload = {    
        "cmd": "request.get",
        "url":"http://www.google.com/",
        "maxTimeout": 60000,
    }

    r = requests.get(FLARE_SOLVER_IP, params=payload)    

    # renew TOR ip
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate(password="QNZX0193")
        controller.signal(Signal.NEWNYM) # type: ignore

    return parse(r.text)


# returns the soup (beautifulsoup) of an html response


def parse(html: str):
    return BeautifulSoup(html, 'html.parser')


def scrape_name_mc():
    def scrape(url: str) -> str:
        soup = get_request(url)
        name_containers: list[str] = soup.find_all(
            'div', class_=re.compile('^row no-gutters py-1 px-3'))

        json_data_array = []
        for name in name_containers:
            player_name: str = name.find('a').text
            drop_time: str = name.find('time')['datetime']
            unix_drop_time = parse_time(drop_time)
            utc_drop_time = drop_time
            searches: str = name.find(
                'div', class_='col-auto col-lg order-lg-3 text-right tabular').text
            # set the searches to 0 if it's not a number, most likely a '-'

            if not searches.isnumeric():
                real_searches = 0
            else:
                real_searches = int(searches)

            json_data = {"name": player_name, "searches": real_searches,
                         "unixDropTime": unix_drop_time, "utcDropTime": utc_drop_time}
            json_data_array.append(json_data)

        return json.dumps(json_data_array)

    # checks if json data is correct
    def check_json_validity(json_data: str):
        data = json_util.loads(json_data)
        if len(data) != 50:
            print('Scraper returned an invalid list, trying to scrape again...')
            return False
        return True

    i = 0
    while True:
        if i == 0:
            json_data = scrape(
                'https://namemc.com/minecraft-names?sort=asc&length_op=eq&length=3&lang=&searches=0')
            # json data was empty so we just try to scrape again
            if not check_json_validity(json_data):
                continue
            addUpcomingNames(json_data, True)
        elif i == 10:  # when to check for 3 letter names again
            i = 0
            continue
        else:
            json_data = scrape(
                'https://namemc.com/minecraft-names')
            # json data was empty so we just try to scrape again
            if not check_json_validity(json_data):
                continue
            addUpcomingNames(json_data, False)
        i = i + 1

# converts datetime into unix time


def parse_time(drop_time: str):
    time = datetime.strptime(drop_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    unix_time = int(time.replace(tzinfo=timezone.utc).timestamp())
    return unix_time


def main():
    print('Scraping NameMC...')
    scrape_name_mc()


if __name__ == '__main__':
    main()
