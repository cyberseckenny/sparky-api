import logging
import configparser
from api import app, config

devicesSection = config['DEVICES']
maximumBasicDevices = int(devicesSection['BASIC'])
maximumPremiumDevices = int(devicesSection['PREMIUM'])

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


