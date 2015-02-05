# -*- coding: utf-8 -*-
import colorsys
import datetime
import json
import os
import random
import re
import sys
import time

from .packages import alp

from . import colors
from . import request
from . import utils


class HueAPI:

    def __init__(self):
        self.settings = alp.Settings()
        self.group_id = self.settings.get('group_id') if self.settings.get('group') else '0'
        self.hue_request = request.HueRequest()
        self.converter = colors.Converter()

    def _get_xy_color(self, color):
        """Validate and convert hex color to XY space."""
        hex_color_re = re.compile(
            r'(?<!\w)([a-f0-9]){2}([a-f0-9]){2}([a-f0-9]){2}\b',
            re.IGNORECASE
        )

        if color in colors.CSS_LITERALS:
            color = colors.CSS_LITERALS[color]

        color = color.lstrip('#')

        if not hex_color_re.match(color):
            raise ValueError()

        return self.converter.hexToCIE1931(color)

    def _get_random_xy_color(self):
        random_color = colorsys.hsv_to_rgb(random.random(), 1, 1)
        random_color = tuple([255*x for x in random_color])
        return self.converter.rgbToCIE1931(*random_color)

    def _load_preset(self, preset_name):
        lights = alp.jsonLoad('presets/%s/lights.json' % preset_name)
        wanted_keys = ['xy', 'on', 'bri']

        for lid, light_data in lights.iteritems():
            light_state = dict((k, v) for k, v in light_data['state'].iteritems() if k in wanted_keys)
            self.hue_request.request('put', '/lights/%s/state' % lid, json.dumps(light_state))

    def _set_all_random(self):
        lights = utils.get_lights()

        if not lights:
            print 'No Hue lights found. Try -hue set-bridge.'
            return None

        for lid in lights:
            self.hue_request.request(
                'put',
                '/lights/%s/state' % lid,
                json.dumps({'xy': self._get_random_xy_color()}))

    def _switch(self, control):
        if control[0] == 'lights':
            lid = control[1]
            function = control[2]
            value = control[3] if len(control) > 3 else None

            # Default API request parameters
            method = 'put'
            endpoint = '/groups/%s/action' % self.group_id if lid == 'all' else '/lights/%s/state' % lid

            if function == 'off':
                data = {'on': False}

            if function == 'on':
                data = {'on': True}

            if function == 'bri':
                value = int((float(value) / 100) * 255) if value else 255
                data = {'bri': value}

            if function == 'rename':
                endpoint = '/lights/%s' % lid
                data = {'name': value}

            if function == 'effect':
                data = {'effect': value}

            if function == 'color':
                if value == 'random':
                    if lid == 'all':
                        return self._set_all_random()
                    else:
                        data = {'xy': self._get_random_xy_color()}
                else:
                    try:
                        data = {'xy': self._get_xy_color(value)}
                    except ValueError:
                        print 'Error: Invalid color. Please use a 6-digit hex color.'
                        raise

            if function == 'reminder':
                try:
                    time_delta_int = int(value)
                except ValueError:
                    print 'Error: Invalid time delta for reminder.'
                    raise

                if lid == 'all':
                    address = self.hue_request.api_path + ('/groups/%s/action' % self.group_id)
                else:
                    address = self.hue_request.api_path + ('/lights/%s/state' % lid)

                reminder_time = datetime.datetime.utcfromtimestamp(time.time() + time_delta_int)

                method = 'post'
                endpoint = '/schedules'
                data = {
                    'name': 'Alfred Hue Reminder',
                    'command': {
                        'address': address,
                        'method': 'PUT',
                        'body': {'alert': 'lselect'},
                    },
                    'time': reminder_time.replace(microsecond=0).isoformat(),
                }

            # Make the request
            self.hue_request.request(method, endpoint, json.dumps(data))

        if control[0] == 'presets':
            function = control[1]
            preset_name = control[2]

            if function == 'load':
                self._load_preset(preset_name)

        return None

    def execute(self, action):
        control = action.split(':')
        try:
            self._switch(control)
            print 'Action completed! <%s>' % action
        except ValueError:
            pass


if __name__ == '__main__':
    api = HueAPI()
    api.execute(sys.argv[1])
