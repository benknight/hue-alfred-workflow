# -*- coding: utf-8 -*-
import json
from os import system

from packages import requests
from packages.workflow import Workflow3 as Workflow

import request
import utils


POST_SETUP_FORM_URL = 'http://goo.gl/forms/ep0OuA2Mh2'


def set_bridge(bridge_ip=None):
    try:
        if not bridge_ip:
            bridge_ip = utils.search_for_bridge()

            if not bridge_ip:
                print 'No bridges found on your network. Try specifying the IP address.'
                return None

        workflow = Workflow()

        prev_username = workflow.settings.get('username')

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
            workflow.settings['bridge_ip'] = bridge_ip
            workflow.settings['username'] = resp['success']['username']

            print 'Success! You can now control your lights by using the "hue" keyword.'

            # TODO: Test that this only happens on first install
            if not prev_username:
                system('open ' + POST_SETUP_FORM_URL)

    except requests.exceptions.RequestException:
        print 'Connection error.'
