# -*- coding: utf-8 -*-
import json
import os
import re
import sys

import alp
import requests

import css_colors
import rgb_cie


class HueAlfredAction:

    def __init__(self):
        self.settings = alp.Settings()
        self.request_base_path = 'http://{bridge_ip}/api/{username}'.format(
            bridge_ip=self.settings.get('bridge_ip'),
            username=self.settings.get('username'),
        )

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

    def _save_current_state_as_preset(self, name):
        lights = alp.jsonLoad(alp.cache('lights.json'))

        # Create dir
        preset_dir = alp.storage(join='presets/' + name)
        os.makedirs(preset_dir)

        # Dump lights.json
        alp.jsonDump(lights, preset_dir + '/lights.json')

        # for each light do this
        for lid in lights:
            light = alp.jsonLoad(alp.cache('%s.json' % lid))
            alp.jsonDump(light, preset_dir + ('/%s.json' % lid))

    def _load_preset(self, preset_name):
        lights = alp.jsonLoad('presets/%s/lights.json' % preset_name)

        for lid in lights:
            light = alp.jsonLoad('presets/{0}/{1}.json'.format(preset_name, lid))
            requests.put(
                self.request_base_path + ('/lights/%s/state' % lid),
                json.dumps({
                     'xy': light['state']['xy'],
                     'on': light['state']['on'],
                    'bri': light['state']['bri'],
                }),
            )

    def send_filter_query(self, json_query):
        """Decodes a json query sent by the script filter and makes the API call.
        This whole system is rather inelegant, with complicated, hard-to-understand logic.
        Right now I'm too lazy to come up with a better way, so deal with it. :D
        """
        query = json.loads(json_query)

        if query.get('action') == 'load_preset':
            self._load_preset(query['preset_name'])

        elif query.get('action') == 'save_preset':
            self._save_current_state_as_preset(query['preset_name'])

        elif query.get('action') == 'rename':
            endoint = '/lights/%s' % query['lid']
            data = json.dumps(query['data'])

        else:
            if query.get('action') == 'set_color':
                try:
                    data = json.dumps({'xy': self._get_xy_color(query['color'])})
                except ValueError:
                    print 'Invalid color. Please use a 6-digit hex color.'
                    return None
            else:
                data = json.dumps(query['data'])

            if query['lid'] == 'all':
                group_id = self.settings.get('group_id') if self.settings.get('group') else '/groups/0'
                endpoint = '%s/action' % group_id
            else:
                endpoint = '/lights/%s/state' % query['lid']

        requests.put(self.request_base_path + endpoint, data)


if __name__ == '__main__':
    hue_action = HueAlfredAction()
    hue_action.send_filter_query(sys.argv[0])
