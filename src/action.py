# -*- coding: utf-8 -*-
import datetime
import json
import os
import random
import re
import sys
import time

import alp

import css_colors
import rgb_cie
import helpers
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

    def execute(self, action):
        control = action.split(':')

        if control[0] == 'lights':
            lid = control[1]
            function = control[2]
            value = control[3] if len(control) > 3 else None

            # Default API request parameters
            method = 'put'
            endpoint = '%s/action' % self.group_id if lid == 'all' else '/lights/%s/state' % lid

            if function == 'off':
                data = {'on': False}

            if function == 'on':
                data = {'on': True}

            if function == 'bri':
                data = {'bri': value}

            if function == 'rename':
                endpoint = '/lights/%s' % lid
                data = {'name': value}

            if function == 'effect':
                data = {'effect': value}

            if function == 'color':
                try:
                    data = {'xy': self._get_xy_color(value)}
                except ValueError:
                    print 'Invalid color. Please use a 6-digit hex color.'
                    return None

            if function == 'reminder':
                try:
                    time_delta_int = int(value)
                except ValueError:
                    print 'Invalid time delta for reminder.'
                    return None

                if lid == 'all':
                    address = self.hue_request.api_path + ('%s/action' % self.group_id)
                else:
                    address = self.hue_request.api_path + ('/lights/%s/state' % lid)

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

            # Make the request
            self.hue_request.request(method, endpoint, json.dumps(data))
            print 'Action completed: %s' % action

        if control[0] == 'presets':
            # Load or save
            action = control[1]
            preset_name = control[2]

            if action == 'load':
                self._load_preset(preset_name)

        if control[0] == 'random':
            lights = helpers.get_lights()

            if not lights:
                print 'No Hue lights found. Try -hue set-bridge.'
                return None

            for lid in lights:
                self.hue_request.request(
                    'put',
                    '/lights/%s/state' % lid,
                    json.dumps({
                        'hue': random.randrange(0, 65535),
                        'sat': 255,
                    })
                )
            print 'Lights set to random hues.'



if __name__ == '__main__':
    hue_action = HueAlfredAction()
    hue_action.send_filter_query(sys.argv[0])
