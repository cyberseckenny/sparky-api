import logging
import configparser
import sentry_sdk
from flask import Flask, json, request, abort, jsonify, render_template
from pymongo import MongoClient
from werkzeug.exceptions import HTTPException 
from sentry_sdk.integrations.flask import FlaskIntegration
from setuptools import setup

config = configparser.ConfigParser()
config.read('config.ini')
devicesSection = config['DEVICES']
maximumBasicDevices = int(devicesSection['BASIC'])
maximumPremiumDevices = int(devicesSection['PREMIUM'])
mongoSection = config['MONGO']
mongoIP = mongoSection['IP']

sentrySection = config['SENTRY']
dsn = sentrySection['DSN']
sentry_sdk.init(
    dsn=dsn,
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)

mongo_client = MongoClient('mongodb://' + mongoIP + ':27017')
db = mongo_client.license
keys = db.keys


# TODO: implement logger

def getDocumentFromKey(key):
    for document in keys.find():
        if document['key'] == key:
            return document
    return None

def getDataFromKey(key):
    if keys.count_documents({}) > 0:
        for document in keys.find():
            if document['key'] == key:
                devices = document['devices']
                membership = document['membership']
                return {'devices': devices, 'membership': membership}
                break
        return None
    else:
        # TODO: error logging
        return None

def addDevice(key):
    document = getDocumentFromKey(key) 
    id = document['_id']
    devices = int(document['devices'])
    jsonId = {"_id": id}
    updatedValues = {"$set": {"devices": devices + 1}}
    keys.update_one(jsonId, updatedValues)

class PaymentRequired(HTTPException):
    code = 402
    description = 'Payment required.'

# we import other files down here to prevent circular imports
app = Flask(__name__)
import api.validate_endpoint

@app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    error = 'UNKNOWN'
    
    if e.code == 400:
        error = "MALFORMED_REQUEST"
    elif e.code == 401:
        error = "INVALID_KEY"
    elif e.code == 402:
        error = "MAXIMUM_DEVICES"
    elif e.code == 404:
        return render_template('page_not_found.html') 
    elif e.code == 429:
        error = "RATE_LIMIT"
    elif e.code == 500:
        error = "INTERNAL_SERVER_ERROR"

    respons.data = json.dumps({
        "error": error
    })
    response.content_type = "application/json"

    return response

@app.route('/')
def post_root():
    return render_template('root.html') 

app.register_error_handler(400, handle_exception)
app.register_error_handler(401, handle_exception)
app.register_error_handler(PaymentRequired, handle_exception)
app.register_error_handler(400, handle_exception)
app.register_error_handler(429, handle_exception)
app.register_error_handler(500, handle_exception)
