#!/usr/bin/env python3
# encoding: utf-8

import json

import utils
from libs import requests
from workflow import Workflow


def set_bridge(bridge_ip=None):
    try:
        if not bridge_ip:
            bridge_ip = utils.search_for_bridge()

            if not bridge_ip:
                print('No bridges found on your network. Try specifying the IP address.')
                return None

        workflow = Workflow()

        # Create API user for the workflow
        r = requests.post(
            'http://{bridge_ip}/api'.format(bridge_ip=bridge_ip),
            data=json.dumps({'devicetype': 'Alfred Workflow'}),
            timeout=3
        )

        resp = r.json()[0]

        if resp.get('error'):
            print('Setup Error: %s' % resp['error'].get('description'))
        else:
            workflow.settings['bridge_ip'] = bridge_ip
            workflow.settings['username'] = resp['success']['username']

            print('Success! You can now control your lights by using the "hue" keyword.')

    except requests.exceptions.RequestException:
        print('Connection error.')
