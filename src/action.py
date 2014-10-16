# -*- coding: utf-8 -*-
import datetime
import json
import os
import re
import sys
import time

import alp

import css_colors
import rgb_cie
from hue_request import HueRequest


class HueAlfredAction:

    def __init__(self):
        self.settings = alp.Settings()
        self.group_id = self.settings.get('group_id') if self.settings.get('group') else '/groups/0'
        self.hue_request = HueRequest()

    def _get_xy_color(self, color):
        """Validate and convert hex color to XY space."""
        converter = rgb_cie.Converter()
        hex_color_re = re.compile(
            r'(?<!\w)([a-f0-9]){2}([a-f0-9]){2}([a-f0-9]){2}\b',
            re.IGNORECASE
        )

        if color in css_colors.CSS_LITERALS:
            color = css_colors.CSS_LITERALS[color]

        color = color.lstrip('#')

        if not hex_color_re.match(color):
            raise ValueError()

        return converter.hexToCIE1931(color)

    def _load_preset(self, preset_name):
        lights = alp.jsonLoad('presets/%s/lights.json' % preset_name)

        for lid, light_data in lights.iteritems():
            self.hue_request.request(
                'put',
                '/lights/%s/state' % lid,
                json.dumps({
                     'xy': light_data['state']['xy'],
                     'on': light_data['state']['on'],
                    'bri': light_data['state']['bri'],
                }),
            )

    def send_filter_query(self, json_query):
        """Decodes a json query sent by the script filter and makes the API call.
        This whole system is rather inelegant, but right now I'm too lazy to come
        up with a better way, so deal with it. :D
        """
        query = json.loads(json_query)

        if query.get('action') == 'load_preset':
            self._load_preset(query['preset_name'])

        elif query.get('action') == 'save_preset':
            self._save_current_state_as_preset(query['preset_name'])

        elif query.get('action') == 'rename':
            self.hue_request.request(
                'put',
                '/lights/%s' % query['lid'],
                json.dumps(query['data']),
            )

        elif query.get('action') == 'reminder':
            if query['lid'] == 'all':
                address = self.hue_request.api_path + ('%s/action' % self.group_id)
            else:
                address = self.hue_request.api_path + ('/lights/%s/state' % query['lid'])

            try:
                time_delta_int = int(query['time_delta'])
            except ValueError:
                print 'Invalid time delta for reminder.'
                return None

            reminder_time = datetime.datetime.utcfromtimestamp(time.time() + time_delta_int)

            data = json.dumps({
                'name': 'Alfred Hue Reminder',
                'command': {
                    'address': address,
                    'method': 'PUT',
                    'body': {'alert': 'lselect'},
                },
                'time': reminder_time.replace(microsecond=0).isoformat(),
            })
            self.hue_request.request('post', '/schedules', data)

        else:
            if query.get('action') == 'set_color':
                try:
                    data = {'xy': self._get_xy_color(query['color'])}
                except ValueError:
                    print 'Invalid color. Please use a 6-digit hex color.'
                    return None
            else:
                data = query['data']

            if query['lid'] == 'all':
                endpoint = '%s/action' % self.group_id
            else:
                endpoint = '/lights/%s/state' % query['lid']

            self.hue_request.request('put', endpoint, json.dumps(data))

        if query.get('feedback'):
            print query['feedback'].encode('utf8')


if __name__ == '__main__':
    hue_action = HueAlfredAction()
    hue_action.send_filter_query(sys.argv[0])
