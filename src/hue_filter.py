# -*- coding: utf-8 -*-
import json

import alp

import helpers
from base_filter import HueFilterBase
from light_filter import HueLightFilter
from presets_filter import HuePresetsFilter


class HueFilter(HueFilterBase):

    items_yaml = '''
help:
  title: Help
  subtitle: Get general info about how to use this workflow.
  valid: true
  arg: help
  icon: icons/help.png

bridge_failed:
  title: Bridge connection failed.
  subtitle: Try running "-hue set-bridge"
  valid: false

all_lights:
  title: All lights
  subtitle: Set state for all Hue lights in the set group.
  valid: false
  autocomplete: 'lights:all:'
  icon: icons/light-alt.png

presets:
  title: Presets
  subtitle: To save a preset enter "-hue save-preset <name>"
  valid: false
  autocomplete: presets
  icon: icons/preset.png
'''

    def get_results(self, args):
        """Returns Alfred XML based on the args query.

        Args:
            args - a string such as: 1, 1:bri, 1:color:red
        """
        query = args[0]

        if (query.startswith('lights') and len(query.split(':')) >= 3):
            light_filter = HueLightFilter()
            control = query.split(':')
            lights = helpers.get_lights(from_cache=True)
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
            lights = helpers.get_lights()

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

        self._add_item('help')
        self._filter_results()
        return self.results


if __name__ == '__main__':
    hue_filter = HueFilter()
    results = hue_filter.get_results(alp.args())
    alp.feedback(results)
