#!/usr/bin/python3

from flask import Flask, json, request, abort, jsonify
from pymongo import MongoClient
from werkzeug.exceptions import BadRequest
import logging

# TODO: implement logger

app = Flask(__name__)

mongo_client = MongoClient('mongodb://localhost:27017')
db = mongo_client.license
keys = db.keys

def getDevicesFromKey(key):
    if keys.count_documents({}) > 0:
        for document in keys.find():
            if document['key'] == key:
                return document['devices']
                break
        return None
    else:
        # TODO: error logging
        return None

@app.errorhandler(BadRequest)
def handle_exception(e):
    response = e.get_response()
    error = ''
    
    if e.code == 400:
        error = "MALFORMED_REQUEST"
    elif e.code == 401:
        error = "INVALID_KEY"
    elif e.code == 429:
        error = "RATE_LIMIT"

    response.data = json.dumps({
        "error": error
    })
    response.content_type = "application/json"

    return response

app.register_error_handler(400, handle_exception)
app.register_error_handler(401, handle_exception)
app.register_error_handler(429, handle_exception)

@app.route('/validate', methods=['POST'])
def post_validate():
    data = request.get_json()
    try:
        key = data['key']
    except KeyError:
        abort(400)

    devices  = getDevicesFromKey(key) 
    if devices is None:
        # TODO: error logging
        abort(500)
    else:
        return {"devices": devices} 

    # TODO: ratelimit
    abort(401) 

if __name__ == '__main__':
    app.run(host='0.0.0.0')
