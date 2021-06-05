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

@app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    error = 'UNKNOWN'
    
    if e.code == 400:
        error = "MALFORMED_REQUEST"
    elif e.code == 404:
        return render_template('page_not_found.html') 
        error = "PAGE_NOT_FOUND"
    elif e.code == 429:
        return 'You are being rate limited.' 
    elif e.code == 500:
        error = "INTERNAL_SERVER_ERROR"

    response.data = json.dumps({
        "error": error
    })
    response.content_type = "application/json"

    return response

@app.route('/')
def post_root():
    return render_template('root.html') 

app.register_error_handler(400, handle_exception)
app.register_error_handler(404, handle_exception)
app.register_error_handler(429, handle_exception)
app.register_error_handler(500, handle_exception)
