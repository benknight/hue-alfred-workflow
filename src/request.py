#!/usr/bin/env python3
# encoding: utf-8

from libs import requests
from libs import urllib3
from workflow import Workflow

# Suppress SSL warnings for self-signed Hue bridge certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class HueRequest():
    """Handles Philips Hue API path strings and logs every request for debugging."""

    def __init__(self):
        self.workflow = Workflow()
        self.api_path = '/api/%s' % self.workflow.settings['username']
        # Use HTTPS for Hue Bridge Pro compatibility
        self.api_path_full = 'https://{bridge_ip}{api_path}'.format(
            bridge_ip=self.workflow.settings['bridge_ip'],
            api_path=self.api_path,
        )

    def request(self, method, endpoint, data=None):
        self.workflow.logger.info('request({method}, {endpoint}, {data})'.format(
            method=method, endpoint=endpoint, data=data,
        ))
        # Use verify=False for self-signed Hue bridge certificates
        return requests.request(method, self.api_path_full + endpoint, data=data, verify=False)
