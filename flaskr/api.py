#!/usr/bin/python3

from flask import Flask, json, request, abort
from werkzeug.exceptions import BadRequest, Unauthorized, TooManyRequests 
import logging

# TODO: implement logger
# TODO: mongoDB

keys = {"key": "fa4c8c97-a7a0-4c14-9876-6943ab50a87c"}
devices = {"devices": 4}

app = Flask(__name__)

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

    if key == keys['key']:
        return devices

    # TODO: ratelimit
    abort(401) 

if __name__ == '__main__':
    app.run(host='0.0.0.0')
