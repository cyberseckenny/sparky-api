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
mongoIP = mongoSection['IP']
ratelimitSection = config['RATELIMIT']
maxRequestsPerMinute = ratelimitSection['MAXPERMINUTE']

sentrySection = config['SENTRY']
dsn = sentrySection['DSN']
sentry_sdk.init(
    dsn=dsn,
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)

mongo_client = MongoClient('mongodb://' + mongoIP + ':27017')
db = mongo_client.upcoming_names
upcoming = db.upcoming
upcoming_three = db.upcoming_three

# the 'three' boolean indicates if the json_data is three letter names
def addUpcomingNames(json_data, three):
    data = json_util.loads(json_data)
    now = datetime.now()
    if three:
        upcoming_three.drop()
        upcoming_three.insert_many(data)
        print('Updated upcoming three letter names at ' + str(now))
    else:
        upcoming.drop()
        upcoming.insert_many(data)
        print('Updated upcoming names at ' + str(now))

# the 'three' boolean indicates if the json_data is three letter names
def getUpcomingNames(three):
    if three:
        cursor = upcoming_three.find({}, {'_id': False})
    else:
        cursor = upcoming.find({}, {'_id': False})
        
    json_data = [] 
    for doc in cursor:
       json_data.append(doc)

    return json_data 

app = Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=[maxRequestsPerMinute + " per minute"]
)

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

