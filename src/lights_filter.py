# -*- coding: utf-8 -*-

# system
import json
import urllib
import yaml

# vendor
import alp
import png
import requests

# workflow components
import color_picker
import rgb_cie


class HueAlfredFilter:

    results = []

    def __init__(self):
        self.strings = yaml.load(file(alp.local('result_strings.yaml'), 'r'))

    def _load_lights_data_from_api(self, timeout=6):
        """Downloads lights data and caches it locally. Returns None."""
        settings = alp.readPlist(alp.local('settings.plist'))
        request_base_uri = 'http://{0}/api/{1}'.format(
            settings['api.bridge_ip'],
            settings['api.username'])

        r = requests.get(request_base_uri + '/lights', timeout=timeout)
        lights = r.json()

        if settings.get('group') and settings['group'] is not 0:
            lights = {lid: lights[lid] for lid in settings['group'].split(',')}

        alp.jsonDump(lights, alp.cache('lights.json'))

        for lid in lights.keys():
            r = requests.get('{0}/lights/{1}'.format(request_base_uri, lid), timeout=timeout)
            light_data = r.json()

            # Create icon for light
            self._create_light_icon(lid, light_data)

            # Cache light data
            alp.jsonDump(light_data, alp.cache('%s.json' % lid))

        return None

    def _create_light_icon(self, lid, light_data):
        """Creates a 1x1 PNG icon of light's RGB color and saves it to the local dir.
        Returns None.
        """
        # Create a color converter & helper
        converter = rgb_cie.Converter()
        color_helper = rgb_cie.ColorHelper()

        hex_color = converter.xyToHEX(
            light_data['state']['xy'][0],
            light_data['state']['xy'][1],
            float(light_data['state']['bri']) / 255
        )
        f = open(alp.local('%s.png' % lid), 'wb')
        w = png.Writer(1, 1)
        w.write(f, [color_helper.hexToRGB(hex_color)])
        f.close()

        return None

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

    def _show_preset_items(self):
        raise NotImplementedError()

    def _add_item(self, string_key, **kwargs):
        """A convenient way of adding items based on the yaml data. Returns None."""
        if self.strings.get(string_key):
            for k, v in self.strings[string_key].items():
                kwargs.setdefault(k, v)

        self.results.append(alp.Item(**kwargs))
        return None

    def get_results(self, args):
        """Returns Alfred XML based on the args query.

        Args:
            args - a string such as: 1, 1:bri, 1:color:red, presets
        """
        query = args[0]
        control = query.split(':')

        # For filtering results at the end to add a simple autocomplete
        partial_query = None

        if len(control) > 1:
            lights = self._get_lights(from_cache=True)
            lid = control[0]
            icon = ('icon.png' if lid == 'all' else '%s.png' % lid)

            if len(control) is 2:
                partial_query = control[1]

                if lid == 'all' or lights[lid]['state']['on']:
                    self._add_item('light_off',
                        autocomplete='%s:off' % lid,
                        icon=icon,
                        arg=json.dumps({
                            'lid': lid,
                            'data': {'on': False},
                        }))
                if lid == 'all' or not lights[lid]['state']['on']:
                    self._add_item('light_on',
                        autocomplete='%s:on' % lid,
                        icon=icon,
                        arg=json.dumps({
                            'lid': lid,
                            'data': {'on': True},
                        }))
                self._add_item('set_color',
                    subtitle='',
                    icon=icon,
                    autocomplete='%s:color:' % lid)
                self._add_item('set_effect',
                    subtitle='',
                    icon=icon,
                    autocomplete='%s:effect:' % lid)
                self._add_item('set_brightness',
                    subtitle='',
                    icon=icon,
                    autocomplete='%s:bri:' % lid)
                self._add_item('set_alert',
                    icon=icon,
                    autocomplete='%s:alert:' % lid)
                self._add_item('light_rename',
                    icon=icon,
                    autocomplete='%s:rename:' % lid)

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
                            'lid': lid,
                            'color': value,
                        }))
                    self._add_item('color_picker',
                        icon=icon,
                        autocomplete='%s:color:colorpicker' % lid)

                elif function == 'bri':
                    self._add_item('set_brightness',
                        icon=icon,
                        valid=True,
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

                elif function == 'alert':
                    self._add_item('alert_none',
                        icon=icon,
                        arg=json.dumps({
                            'lid': lid,
                            'data': {'alert': 'none'},
                        }))
                    self._add_item('alert_blink_once',
                        icon=icon,
                        arg=json.dumps({
                            'lid': lid,
                            'data': {'alert': 'select'},
                        }))
                    self._add_item('alert_blink_30_secs',
                        icon=icon,
                        arg=json.dumps({
                            'lid': lid,
                            'data': {'alert': 'lselect'},
                        }))

                elif function == 'rename':
                    self._add_item('light_rename',
                        icon=icon,
                        arg=json.dumps({
                            'lid': lid,
                            'rename': True,
                            'data': {'name': value},
                        }))

        else:
            lights = self._get_lights()

            if not lights:
                self._add_item('bridge_failed')

            elif query == 'presets':
                self._add_item('save_preset')
                self._preset_items()

            else:
                self._add_item('all_lights')

                for lid, light in lights.items():
                    if light['state']['on']:
                        subtitle = 'Hue: {hue}, Brightness: {bri}'.format(
                            bri='{0:.0f}%'.format(float(light['state']['bri']) / 255 * 100),
                            hue='{0:.0f}deg'.format(float(light['state']['hue']) / 65535 * 360))
                    else:
                        subtitle = 'OFF'

                    self.results.append(alp.Item(
                        title=light['name'],
                        subtitle=u'#{lid} — {subtitle}'.format(
                            lid=lid,
                            subtitle=subtitle,
                        ),
                        valid=False,
                        icon='%s.png' % lid,
                        autocomplete='%s:' % lid,))

                self._add_item('presets')

        if partial_query:
            self.results = [result for result in self.results if partial_query in result.autocomplete]

        return alp.feedback(self.results)


if __name__ == '__main__':
    hue_filter = HueAlfredFilter()
    hue_filter.get_results(alp.args())
