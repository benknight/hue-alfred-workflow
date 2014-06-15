# -*- coding: utf-8 -*-
import json

import alp
import png
import rgb_cie

from base_filter import HueFilterBase
from light_filter import HueLightFilter
from presets_filter import HuePresetsFilter


ITEMS = '''
bridge_failed:
  title: Bridge connection failed.
  subtitle: Try running "-hue set-bridge"
  valid: false

all_lights:
  title: All lights
  subtitle: Set state for all Hue lights in the set group.
  valid: false
  autocomplete: 'lights:all:'

presets:
  title: Presets
  subtitle: To save a preset enter "-hue save-preset <name>"
  valid: false
  autocomplete: presets
  icon: icons/preset.png
'''


class HueFilter(HueFilterBase):

    items_yaml = ITEMS

    def _load_lights_data_from_api(self, timeout=6):
        """Downloads lights data and caches it locally."""

        # Requests is an expensive import so we only do it when necessary.
        import requests

        settings = alp.Settings()

        r = requests.get(
            'http://{0}/api/{1}'.format(
                settings.get('bridge_ip'),
                settings.get('username'),
            ),
            timeout=timeout,
        )
        data = r.json()
        lights = data['lights']

        if settings.get('group'):
            lights = {lid: lights[lid] for lid in settings.get('group')}

        # Filter out anything that doesn't have an "xy" key in its state
        # e.g. "Dimmable plug-in unit", see: http://goo.gl/a5P7yN
        lights = {lid: lights[lid] for lid in lights if lights[lid]['state'].get('xy')}

        alp.jsonDump(lights, alp.cache('lights.json'))

        # Create icon for light
        for lid, light_data in lights.iteritems():
            self._create_light_icon(lid, light_data)

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
            from requests.exceptions import RequestException
            try:
                self._load_lights_data_from_api()
            except RequestException:
                return None

        lights = alp.jsonLoad(alp.cache('lights.json'))

        return lights

    def get_results(self, args):
        """Returns Alfred XML based on the args query.

        Args:
            args - a string such as: 1, 1:bri, 1:color:red
        """
        query = args[0]

        if (query.startswith('lights') and len(query.split(':')) >= 3):
            light_filter = HueLightFilter()
            control = query.split(':')
            lights = self._get_lights(from_cache=True)
            lid = control[1]

            self.results = light_filter.get_results(
                lid=lid,
                light=lights.get(lid, None),
                query=':'.join(control[2:]), # lights:1:<light_query>
            )

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
                    self.partial_query = query.split(':')[1]

                for lid, light in lights.items():
                    if light['state']['on'] and light['state']['reachable']:
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

        self._filter_results()
        return self.results


if __name__ == '__main__':
    hue_filter = HueFilter()
    results = hue_filter.get_results(alp.args())
    alp.feedback(results)
