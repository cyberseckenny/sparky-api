import logging
import configparser
import sentry_sdk
from flask import Flask, json, request, abort, jsonify, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pymongo import MongoClient
from werkzeug.exceptions import HTTPException 
from sentry_sdk.integrations.flask import FlaskIntegration
from setuptools import setup

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

# we import other files down here to prevent circular imports
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
