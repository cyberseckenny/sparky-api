from app import app # type: ignore

import configparser

from flask import jsonify, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pymongo import MongoClient
from pymongo.cursor import Cursor
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


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

def getUpcomingNames(three: bool) -> list[str]:
    cursor: Cursor = UPCOMING.find({}, {'_id': False})
    if three:
        cursor = UPCOMING_THREE.find({}, {'_id': False})

    json_data: list[str] = list()
    for doc in cursor:
        json_data.append(doc)  # type: ignore

    return json_data


limiter: Limiter = Limiter(
    app, # type: ignore
    key_func=get_remote_address,
    default_limits=[MAX_REQUESTS_PER_MINUTE + " per minute"]
)


@app.errorhandler(429)
def rate_limit(e):  # type ignore
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


@app.route('/docs/')
def site_docs():
    return render_template('docs.html')


@app.route('/upcoming/')
def endpoint_upcoming():
    three = request.args.get('three_letter')
    if three == 'true':
        return jsonify(getUpcomingNames(True))
    else:
        return jsonify(getUpcomingNames(False))


@app.route('/droptime/<name>')
def endpoint_droptime(name: str):
    print(name)
    if name == ' ':
        return jsonify({"error": "INVALID_NAME"})
    else:
        return ''
        # TODO: fix me
        # return jsonify(json_data)
