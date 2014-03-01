# -*- coding: utf-8 -*-
import json
import urllib
import yaml

import alp
import png
import requests

import color_picker
import rgb_cie
from presets_filter import HuePresetsFilter


ITEMS = '''
bridge_failed:
  title: Bridge connection failed.
  subtitle: Try running "setup-hue"
  valid: false

all_lights:
  title: All lights
  subtitle: Set state for all Hue lights in the set group.
  valid: false
  autocomplete: 'lights:all:'

light_off:
  title: Turn OFF

light_on:
  title: Turn ON

set_color:
  title: Set color to…
  subtitle: Accepts 6-digit hex colors or CSS literal color names (e.g. "blue")
  valid: false

color_picker:
  title: Use color picker…
  valid: false

set_effect:
  title: Set effect…
  valid: false

effect_none:
  title: None
  subtitle: 'Cancel any ongoing effects, such as a color loop.'

color_loop:
  title: Color loop

set_brightness:
  title: Set brightness…
  subtitle: 'Set on a scale from 0 to 255, where 0 is off.'
  valid: false

set_reminder:
  title: Set reminder…
  subtitle: This will cause the light(s) to blink after the specified interval.
  valid: false

alert_none:
  title: None
  subtitle: Turn off any ongoing alerts.

alert_blink_once:
  title: Blink once

alert_blink_30_secs:
  title: Blink for 30 seconds

light_rename:
  title: Set light name to…
  valid: false

presets:
  title: Presets
  subtitle: Save the current group state or set group to a previous state.
  valid: false
  autocomplete: presets
  icon: icons/preset.png
'''


class HueLightsFilter:

    results = []

    def __init__(self):
        self.items = yaml.load(ITEMS)

    def _load_lights_data_from_api(self, timeout=6):
        """Downloads lights data and caches it locally."""
        settings = alp.Settings()
        request_base_uri = 'http://{0}/api/{1}'.format(
            settings.get('bridge_ip'),
            settings.get('username'),
        )

        r = requests.get(request_base_uri + '/lights', timeout=timeout)
        lights = r.json()

        if settings.get('group'):
            lights = {lid: lights[lid] for lid in settings.get('group')}

        alp.jsonDump(lights, alp.cache('lights.json'))

        for lid in lights.keys():
            r = requests.get('{0}/lights/{1}'.format(request_base_uri, lid), timeout=timeout)
            light_data = r.json()

            # Create icon for light
            self._create_light_icon(lid, light_data)

            # Cache light data
            alp.jsonDump(light_data, alp.cache('%s.json' % lid))

    def _create_light_icon(self, lid, light_data):
        """Creates a 1x1 PNG icon of light's RGB color and saves it to the local dir.
        """
        # Create a color converter & helper
        converter = rgb_cie.Converter()
        color_helper = rgb_cie.ColorHelper()

        hex_color = converter.xyToHEX(
            light_data['state']['xy'][0],
            light_data['state']['xy'][1],
            float(light_data['state']['bri']) / 255
        )
        f = open(alp.local('icons/%s.png' % lid), 'wb')
        w = png.Writer(1, 1)
        w.write(f, [color_helper.hexToRGB(hex_color)])
        f.close()

    def _get_lights(self, from_cache=False):
        """Returns a dictionary of lid => data, or None if no lights data is in the cache.

        Options:
            from_cache - Read data from cached json files instead of querying the API.
        """
        output = dict()

        if not from_cache:
            try:
                self._load_lights_data_from_api()
            except requests.exceptions.RequestException:
                return None

        lights = alp.jsonLoad(alp.cache('lights.json'))

        if lights is not None:
            for lid in lights.keys():
                light_data = alp.jsonLoad(alp.cache('%s.json' % lid))
                output[lid] = light_data

        return output

    def _add_item(self, string_key, **kwargs):
        """A convenient way of adding items based on the yaml data."""
        if self.items.get(string_key):
            for k, v in self.items[string_key].items():
                kwargs.setdefault(k, v)

        self.results.append(alp.Item(**kwargs))

    def get_results(self, args):
        """Returns Alfred XML based on the args query.

        Args:
            args - a string such as: 1, 1:bri, 1:color:red
        """
        query = args[0]

        # For filtering results at the end to add a simple autocomplete
        partial_query = None

        if (query.startswith('lights') and len(query.split(':')) > 2):

            lights = self._get_lights(from_cache=True)
            control = query.split(':')[1:]
            lid = control[0]
            icon = ('icon.png' if lid == 'all' else 'icons/%s.png' % lid)

            if len(control) is 2:
                partial_query = control[1]

                if lid == 'all' or lights[lid]['state']['on']:
                    self._add_item('light_off',
                        autocomplete='lights:%s:off' % lid,
                        icon=icon,
                        arg=json.dumps({
                            'lid': lid,
                            'data': {'on': False},
                        }))

                if lid == 'all' or not lights[lid]['state']['on']:
                    self._add_item('light_on',
                        autocomplete='lights:%s:on' % lid,
                        icon=icon,
                        arg=json.dumps({
                            'lid': lid,
                            'data': {'on': True},
                        }))

                self._add_item('set_color',
                    subtitle='',
                    icon=icon,
                    autocomplete='lights:%s:color:' % lid)

                self._add_item('set_effect',
                    subtitle='',
                    icon=icon,
                    autocomplete='lights:%s:effect:' % lid)

                self._add_item('set_brightness',
                    subtitle='',
                    icon=icon,
                    autocomplete='lights:%s:bri:' % lid)

                self._add_item('set_reminder',
                    icon=icon,
                    autocomplete='lights:%s:reminder:' % lid)

                self._add_item('light_rename',
                    icon=icon,
                    autocomplete='lights:%s:rename:' % lid)

            elif len(control) >= 3:
                function = control[1]
                value = control[2]

                if function == 'color':
                    if value == 'colorpicker':
                        # TODO: This doesn't work.
                        color_picker.OSXColorPicker.color_picker(lid)

                    self._add_item('set_color',
                        valid=True,
                        icon=icon,
                        arg=json.dumps({
                            'action': 'set_color',
                            'lid': lid,
                            'color': value,
                        }))
                    self._add_item('color_picker',
                        icon=icon,
                        autocomplete='%s:color:colorpicker' % lid)

                elif function == 'bri':
                    self._add_item('set_brightness',
                        title='Set brightness to %s' % (value or u'…'),
                        icon=icon,
                        valid=True if value else False,
                        arg=json.dumps({
                            'lid': lid,
                            'data': { 'bri': int(value) if value else 1 },
                        }))

                elif function == 'effect':
                    self._add_item('effect_none',
                        icon=icon,
                        arg=json.dumps({
                            'lid': lid,
                            'data': {'effect': 'none'},
                        }))
                    self._add_item('color_loop',
                        icon=icon,
                        arg=json.dumps({
                            'lid': lid,
                            'data': {'effect': 'colorloop'},
                        }))

                elif function == 'reminder':
                    self._add_item('set_reminder',
                        title='Blink in %s seconds' % (value or u'…'),
                        subtitle='',
                        icon=icon,
                        valid=True if value else False,
                        arg=json.dumps({
                            'lid': lid,
                            'action': 'reminder',
                            'time_delta': value,
                        }))
                    self._add_item('set_reminder',
                        title='Blink in %s minutes' % (value or u'…'),
                        subtitle='',
                        icon=icon,
                        valid=True if value else False,
                        arg=json.dumps({
                            'lid': lid,
                            'action': 'reminder',
                            'time_delta': (int(value) * 60) if value else 0,
                        }))
                    self._add_item('set_reminder',
                        title='Blink in %s hours' % (value or u'…'),
                        subtitle='',
                        icon=icon,
                        valid=True if value else False,
                        arg=json.dumps({
                            'lid': lid,
                            'action': 'reminder',
                            'time_delta': (int(value) * 60 * 60) if value else 0,
                        }))


                elif function == 'rename':
                    self._add_item('light_rename',
                        icon=icon,
                        arg=json.dumps({
                            'action': 'rename',
                            'lid': lid,
                            'data': {'name': value},
                        }))

        elif query.startswith('presets'):
            control = query.split(' ')

            if len(control) > 1:
                presets_query = ' '.join(control[1:])
            else:
                presets_query = ''

            presets_filter = HuePresetsFilter()
            self.results = presets_filter.get_results(presets_query)

        else: # Show index
            lights = self._get_lights()

            if not lights:
                self._add_item('bridge_failed')
            else:
                self._add_item('all_lights')

                if query.startswith('lights:'):
                    partial_query = query.split(':')[1]

                for lid, light in lights.items():
                    if light['state']['on']:
                        subtitle = 'Hue: {hue}, Brightness: {bri}'.format(
                            bri='{0:.0f}%'.format(float(light['state']['bri']) / 255 * 100),
                            hue='{0:.0f}deg'.format(float(light['state']['hue']) / 65535 * 360))
                        icon = 'icons/%s.png' % lid
                    else:
                        subtitle = 'OFF'
                        icon = 'icons/off.png'

                    self.results.append(alp.Item(
                        title=light['name'],
                        subtitle=u'#{lid} — {subtitle}'.format(
                            lid=lid,
                            subtitle=subtitle,
                        ),
                        valid=False,
                        icon=icon,
                        autocomplete='lights:%s:' % lid,))

                self._add_item('presets')

        if partial_query:
            def partial_query_filter(result):
                if result.autocomplete:
                    return partial_query in result.autocomplete
                else:
                    return True

            self.results = [result for result in self.results if partial_query_filter(result)]

        return self.results


if __name__ == '__main__':
    hue_lights_filter = HueLightsFilter()
    results = hue_lights_filter.get_results(alp.args())
    alp.feedback(results)
