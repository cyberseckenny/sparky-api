#!/usr/bin/python3

import logging
import configparser
import sentry_sdk
from flask import Flask, json, request, abort, jsonify
from pymongo import MongoClient
from werkzeug.exceptions import HTTPException 
from sentry_sdk.integrations.flask import FlaskIntegration

config = configparser.ConfigParser()
config.read('config.ini')
devicesSection = config['DEVICES']
maximumBasicDevices = int(devicesSection['BASIC'])
maximumPremiumDevices = int(devicesSection['PREMIUM'])

sentrySection = config['SENTRY']
dsn = sentrySection['DSN']

mongo_client = MongoClient('mongodb://localhost:27017')
db = mongo_client.license
keys = db.keys

sentry_sdk.init(
        dsn=dsn,
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0
)

app = Flask(__name__)

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
        error = "PAGE_NOT_FOUND"
    elif e.code == 429:
        error = "RATE_LIMIT"
    elif e.code == 500:
        error = "INTERNAL_SERVER_ERROR"

    response.data = json.dumps({
        "error": error
    })
    response.content_type = "application/json"

    return response

app.register_error_handler(400, handle_exception)
app.register_error_handler(401, handle_exception)
app.register_error_handler(PaymentRequired, handle_exception)
app.register_error_handler(400, handle_exception)
app.register_error_handler(429, handle_exception)
app.register_error_handler(500, handle_exception)

@app.route('/validate', methods=['POST'])
def post_validate():
    data = request.get_json()
    try:
        key = data['key']
    except KeyError:
        abort(400)

    # TOOD: ratelimit

    keyData = getDataFromKey(key) 
    if keyData is None:
        # TODO: error logging
        abort(401)
    else:
        devices = keyData['devices']
        membership = keyData['membership']

        if membership == 'BASIC' or membership == 'PREMIUM' or membership == 'ENTERPRISE':
            if membership == 'BASIC' and devices >= maximumBasicDevices:
                # error logging
                raise PaymentRequired() 
            elif membership == 'PREMIUM' and devices >= maximumPremiumDevices:
                # error loggin
                raise PaymentRequired() 
        else:
            # error logging
            abort(500)

    # logging
    addDevice(key)
    # updates devices by 1 to include the current device
    keyData['devices'] = keyData['devices'] + 1
    return keyData

if __name__ == '__main__':
    app.run(host='0.0.0.0')
