# -*- coding: utf-8 -*-
import colorsys
import datetime
import json
import os
import random
import sys
import time

from .packages import alp

from . import colors
from . import harmony
from . import request
from . import utils


class HueAPI:

    def __init__(self):
        self.settings = alp.Settings()
        self.group_id = self.settings.get('group_id') if self.settings.get('group') else '0'
        self.hue_request = request.HueRequest()

    def _get_xy_color(self, color, gamut):
        """Validate and convert hex color to XY space."""
        return colors.Converter(gamut).hex_to_xy(utils.get_color_value(color))

    def _get_random_xy_color(self, gamut):
        random_color = colorsys.hsv_to_rgb(random.random(), 1, 1)
        random_color = tuple([255 * x for x in random_color])
        return colors.Converter(gamut).rgb_to_xy(*random_color)

    def _load_preset(self, preset_name):
        lights = alp.jsonLoad('presets/%s/lights.json' % preset_name)
        wanted_keys = ['xy', 'on', 'bri']

        for lid, light_data in lights.iteritems():
            light_state = dict((k, v) for k, v in light_data['state'].iteritems() if k in wanted_keys)
            self.hue_request.request('put', '/lights/%s/state' % lid, json.dumps(light_state))

    def _set_all(self, palette):
        lights = utils.get_lights()

        if not lights:
            print 'No Hue lights found. Try -hue set-bridge.'
            return None

        for index, lid in enumerate(lights):
            self.hue_request.request(
                'put',
                '/lights/%s/state' % lid,
                json.dumps({'xy': palette[index]})
            )

    def _switch(self, control):
        if control[0] == 'lights':
            lid = control[1]
            function = control[2]
            value = control[3] if len(control) > 3 else None
            lights = utils.get_lights()

            # Default API request parameters
            method = 'put'
            endpoint = '/groups/%s/action' % self.group_id if lid == 'all' else '/lights/%s/state' % lid

            if function == 'off':
                data = {'on': False}

            elif function == 'on':
                data = {'on': True}

            elif function == 'bri':
                value = int((float(value) / 100) * 255) if value else 255
                data = {'bri': value}

            elif function == 'shuffle':
                palette = [lights[_lid]['state']['xy'] for _lid in lights]

                # Only shuffle the lights that are on
                on_indexes = [i for i, _lid in enumerate(lights) if lights[_lid]['state']['on']]
                on_xy = [xy for index, xy in enumerate(palette) if index in on_indexes]
                random.shuffle(on_xy)
                for index, _ in enumerate(palette):
                    if (index in on_indexes):
                        palette[index] = on_xy.pop()

                return self._set_all(palette)

            elif function == 'rename':
                endpoint = '/lights/%s' % lid
                data = {'name': value}

            elif function == 'effect':
                data = {'effect': value}

            elif function == 'color':
                if value == 'random':
                    if lid == 'all':
                        palette = []
                        for _lid in lights:
                            gamut = colors.get_light_gamut(lights[_lid]['modelid'])
                            palette.append(self._get_random_xy_color(gamut))
                        return self._set_all(palette)
                    else:
                        gamut = colors.get_light_gamut(lights[lid]['modelid'])
                        data = {'xy': self._get_random_xy_color(gamut)}
                else:
                    try:
                        if lid == 'all':
                            gamut = colors.GamutA
                        else:
                            gamut = colors.get_light_gamut(lights[lid]['modelid'])
                        data = {'xy': self._get_xy_color(value, gamut)}
                    except ValueError:
                        print 'Error: Invalid color. Please use a 6-digit hex color.'
                        raise

            elif function == 'harmony':
                if lid != 'all':
                    print 'Color harmonies can only be set on the "all" group.'
                    raise ValueError()

                mode = control[4] if len(control) > 3 else None

                if mode not in harmony.MODES:
                    raise ValueError()

                palette = []
                on_indexes = [i for i, _lid in enumerate(lights) if lights[_lid]['state']['on']]
                args = (len(on_indexes), value)
                harmony_colors = getattr(harmony, mode)(*args)
                for index, _lid in enumerate(lights):
                    if index in on_indexes:
                        gamut = colors.get_light_gamut(lights[_lid]['modelid'])
                        palette.append(self._get_xy_color(harmony_colors.pop(), gamut))
                    else:
                        palette.append(lights[_lid]['state']['xy'])
                return self._set_all(palette)

            elif function == 'reminder':
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

            else:
                raise ValueError()

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
