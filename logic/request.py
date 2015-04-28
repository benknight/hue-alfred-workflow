# -*- coding: utf-8 -*-
from .packages import alp
from .packages import requests


class HueRequest():
    """Handles Philips Hue API path strings and logs every request for debugging."""

    def __init__(self):
        self.settings = alp.Settings()
        self.api_path = '/api/%s' % self.settings.get('username')
        self.api_path_full = 'http://{bridge_ip}{api_path}'.format(
            bridge_ip=self.settings.get('bridge_ip'),
            api_path=self.api_path,
        )

    def request(self, method, endpoint, data=None):
        alp.log('request({method}, {endpoint}, {data})'.format(
            method=method, endpoint=endpoint, data=data,
        ))
        return requests.request(method, self.api_path_full + endpoint, data=data)