# -*- coding: utf-8 -*-
import json
from os import system

from .packages import alp
from .packages import requests

from . import request
from . import utils


POST_SETUP_FORM_URL = 'http://goo.gl/forms/ep0OuA2Mh2'


def setup(bridge_ip=None):
    try:
        if not bridge_ip:
            bridge_ip = utils.search_for_bridge()

            if not bridge_ip:
                print 'No bridges found on your network.  Try specifying the IP if you know it.'
                return None

        settings = alp.Settings()

        # Create API user for the workflow
        r = requests.post(
            'http://{bridge_ip}/api'.format(bridge_ip=bridge_ip),
            data=json.dumps({'devicetype': 'Alfred 2'}),
            timeout=6
        )

        resp = r.json()[0]

        if resp.get('error'):
            print 'Setup Error: %s' % resp['error'].get('description')
        else:
            settings.set(bridge_ip=bridge_ip, group='')
            settings.set(username=resp['success']['username'])
            print 'Success! You can now control your lights by using the "hue" keyword.'
            system('open ' + POST_SETUP_FORM_URL)

    except requests.exceptions.RequestException:
        print 'Connection error.'

def set_group(group):
    try:
        settings = alp.Settings()
        hue_request = request.HueRequest()

        if group == '0':
            settings.set(group='')
        else:
            lights = group.split(',')

            if not settings.get('group_id'):
                # Create a custom group for the workflow to use
                r = hue_request.request('post', '/groups', json.dumps({
                    'name': 'Afred Hue Group',
                    'lights': lights,
                }))

                resp = r.json()

                if len(resp) > 0:
                    if resp[0].get('error'):
                        print 'Setup Error: %s' % resp[0]['error'].get('description')
                    else:
                        settings.set(group_id=resp[0]['success']['id'])
            else:
                r = hue_request.request(
                    'put',
                    '/groups/%s' % settings.get('group_id'),
                    data=json.dumps({'lights': lights})
                )

            settings.set(group=lights)

        print 'Group settings saved!'

    except requests.exceptions.RequestException:
        print 'Connection error.'
