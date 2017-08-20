# encoding: utf-8
from __future__ import unicode_literals

import json
from os import system

from packages import requests
from packages.workflow import Workflow3 as Workflow

import request
import utils


def set_bridge(bridge_ip=None):
    try:
        if not bridge_ip:
            bridge_ip = utils.search_for_bridge()

            if not bridge_ip:
                print('No bridges found on your network. Try specifying the IP address.'.encode('utf-8'))
                return None

        workflow = Workflow()

        # Create API user for the workflow
        r = requests.post(
            'http://{bridge_ip}/api'.format(bridge_ip=bridge_ip),
            data=json.dumps({'devicetype': 'Alfred 2'}),
            timeout=3
        )

        resp = r.json()[0]

        if resp.get('error'):
            print('Setup Error: %s' % resp['error'].get('description').encode('utf-8'))
        else:
            workflow.settings['bridge_ip'] = bridge_ip
            workflow.settings['username'] = resp['success']['username']

            print('Success! You can now control your lights by using the "hue" keyword.'.encode('utf-8'))

    except requests.exceptions.RequestException:
        print('Connection error.'.encode('utf-8'))
