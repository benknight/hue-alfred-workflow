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

        try:
            response_data = r.json()
        except ValueError as e:
            print('Setup Error: Bridge returned invalid JSON response')
            return None

        # Handle different response formats
        if isinstance(response_data, list) and len(response_data) > 0:
            resp = response_data[0]
        elif isinstance(response_data, dict):
            resp = response_data
        else:
            print('Setup Error: Bridge returned unexpected response format')
            return None

        if resp.get('error'):
            error_desc = resp['error'].get('description', 'Unknown error')
            error_type = resp['error'].get('type', 'Unknown type')
            
            if error_type == 101:
                print('Setup Error: Press the button on your Hue bridge and try again within 30 seconds.')
            else:
                print('Setup Error: %s' % error_desc)
        elif resp.get('success'):
            workflow.settings['bridge_ip'] = bridge_ip
            workflow.settings['username'] = resp['success']['username']

            print('Success! You can now control your lights by using the "hue" keyword.')
        else:
            print('Setup Error: Bridge returned unexpected response structure')

    except requests.exceptions.RequestException as e:
        print('Connection error: %s' % str(e))
    except Exception as e:
        print('Setup Error: %s' % str(e))
