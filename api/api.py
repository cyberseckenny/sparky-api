import configparser
import sentry_sdk
import json
from flask import Flask, render_template, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pymongo import MongoClient
from sentry_sdk.integrations.flask import FlaskIntegration
from bson import json_util
from datetime import datetime

config = configparser.ConfigParser()
config.read('config.ini')
mongoSection = config['MONGO']
MONGO_IP = mongoSection['IP']

ratelimitSection = config['RATELIMIT']
MAX_REQUESTS_PER_MINUTE = ratelimitSection['MAXPERMINUTE']

sentrySection = config['SENTRY']
dsn = sentrySection['DSN']
sentry_sdk.init(
    dsn=dsn,
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)

mongo_client = MongoClient('mongodb://' + MONGO_IP + ':27017')
db = mongo_client.upcoming_names
UPCOMING = db.upcoming
UPCOMING_THREE = db.upcoming_three

# the 'three' boolean indicates if the json_data is three letter names
def addUpcomingNames(json_data, three, i):
    data = json_util.loads(json_data)
    now = datetime.now()
    if three:
        UPCOMING_THREE.drop()
        UPCOMING_THREE.insert_many(data)
        print('[' + str(i) + '] ' + 'Updated upcoming three letter names at ' + str(now))
    else:
        UPCOMING.drop()
        UPCOMING.insert_many(data)
        print('[' + str(i) + '] ' + 'Updated upcoming names at ' + str(now))

# the 'three' boolean indicates if the json_data is three letter names
def getUpcomingNames(three):
    if three:
        cursor = UPCOMING_THREE.find({}, {'_id': False})
    else:
        cursor = UPCOMING.find({}, {'_id': False})
        
    json_data = [] 
    for doc in cursor:
       json_data.append(doc)

    return json_data 

app = Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=[MAX_REQUESTS_PER_MINUTE + " per minute"]
)
# import here to prevent circular imports
import scraper

@app.errorhandler(429)
def rate_limit(e):
    return 'You are being rate limited.'

# acts a 'missing handler', or a fallback route if none of the others work
@app.route('/<path:path>')
def page_not_found(path):
    return render_template('page_not_found.html')

@app.errorhandler(500)
def internal_server_error(e):
    return 'INTERNAL_SERVER_ERROR'

@app.route('/')
def site_root():
    return render_template('root.html') 

@app.route('/docs')
def site_docs():
    return render_template('docs.html')

@app.route('/upcoming')
def endpoint_upcoming():
    three = request.args.get('three_letter')
    if three == 'true':
        return jsonify(getUpcomingNames(True))
    else:
        return jsonify(getUpcomingNames(False))

@app.route('/droptime/<name>')
def endpoint_droptime(name):
    print(name)
    if name == ' ':
        return jsonify({"error": "INVALID_NAME"})
    else:
        json_data = scraper.scrape_name_droptime(name)
        return jsonify(json_data)
    

