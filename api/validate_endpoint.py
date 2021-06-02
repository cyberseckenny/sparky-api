import logging
import configparser
from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from api import app, config, getDataFromKey, addDevice, maxRequestsPerMinute

devicesSection = config['DEVICES']
maximumBasicDevices = int(devicesSection['BASIC'])
maximumPremiumDevices = int(devicesSection['PREMIUM'])
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=[maxRequestsPerMinute + " per minute"]
)

@app.route('/validate', methods=['POST'])
def post_validate():
    data = request.get_json()
    try:
        key = data['key']
    except KeyError:
        abort(400)

    keyData = getDataFromKey(key)
    if keyData is None:
        abort(401)
    else:
        devices = keyData['devices']
        membership = keyData['membership']

        if membership == 'BASIC' or membership == 'PREMIUM' or membership == 'ENTERPRISE':
            if membership == 'BASIC' and devices >= maximumBasicDevices:
                raise PaymentRequired()
            elif membership == 'PREMIUM' and devices >= maximumPremiumDevices:
                raise PaymentRequired()
        else:
            app.logger.info("Key does not have a valid membership")
            abort(500)

    # logging
    addDevice(key)
    # updates devices by 1 to include the current device
    keyData['devices'] = keyData['devices'] + 1
    return keyData


