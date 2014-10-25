# -*- coding: utf-8 -*-
import json
import os

import alp
import rgb_cie
import yaml

import helpers


class HueFilterBase:

    items_yaml = ''

    # A list of alp.Item
    results = []

    # For filtering results at the end to add a simple autocomplete
    partial_query = None

    def __init__(self):
        self.items = yaml.load(self.items_yaml)

    def _add_item(self, string_key=None, **kwargs):
        """A convenient way of adding items based on the yaml data."""
        if string_key and self.items.get(string_key):
            for k, v in self.items[string_key].items():
                kwargs.setdefault(k, v)

        self.results.append(alp.Item(**kwargs))

    def _partial_query_filter(self, result):
        """Returns True if the result is valid match for the partial query, else False.

            Args:
                result - an instance of alp.Item
        """
        if self.partial_query:
            return (self.partial_query.lower() in result.autocomplete.lower())
        else:
            return True

    def _filter_results(self):
        self.results = [r for r in self.results if self._partial_query_filter(r)]


class HueFilter(HueFilterBase):

    items_yaml = '''
help:
  title: Help
  subtitle: Get general info about how to use this workflow.
  valid: true
  arg: help
  autocomplete: help
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
                        subtitle = u'hue: {hue}, brightness: {bri}'.format(
                            bri=u'{0:.0f}%'.format(float(light['state']['bri']) / 255 * 100),
                            hue=u'{0:.0f}°'.format(float(light['state']['hue']) / 65535 * 360))
                        icon = 'icons/%s.png' % lid
                    else:
                        subtitle = 'off' if light['state']['reachable'] else 'not reachable'
                        icon = 'icons/off.png'

                    self.results.append(alp.Item(
                        title=light['name'],
                        subtitle=u'({lid}) {subtitle}'.format(
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


class HueLightFilter(HueFilterBase):

    items_yaml = '''
set_color:
  title: Set color to…
  subtitle: Accepts 6-digit hex colors or CSS literal color names (e.g. "blue")
  valid: false

color_picker:
  title: Use color picker…
  valid: true

set_effect:
  title: Set effect…
  valid: false

effect_none:
  title: None
  subtitle: Cancel any ongoing effects, such as a color loop.

color_loop:
  title: Color loop

set_brightness:
  title: Set brightness…
  subtitle: Set on a scale from 0 to 100. Note that 0 is not off.
  valid: false

set_reminder:
  title: Set reminder…
  valid: false

light_rename:
  title: Set light name to…
  valid: false
'''

    def get_results(self, lid, light, query):
        control = query.split(':')
        is_on = light and light['state']['on']
        is_reachable = light and light['state']['reachable']
        light_name = light['name'] if lid != 'all' else 'All lights'

        if lid != 'all':
            icon = ('icons/%s.png' % lid) if is_on and is_reachable else 'icons/off.png'
        else:
            icon = 'icon.png'

        if lid != 'all' and not is_reachable:
            self._add_item(
                title='%s is not reachable.' % light_name,
                subtitle='Try turning on the light switch.',
                valid=False,
                icon=icon,
            )

        elif len(control) is 1:
            self.partial_query = control[0]

            if lid == 'all':
                self._add_item(
                    title='ALL OFF',
                    icon=icon,
                    arg=json.dumps({
                        'data': {'on': False},
                        'lid': 'all',
                        'feedback': 'All lights toggled off.'
                    }),
                )

                self._add_item(
                    title='ALL ON',
                    icon=icon,
                    arg=json.dumps({
                        'data': {'on': True},
                        'lid': 'all',
                        'feedback': 'All lights toggled on.'
                    }),
                )

            if is_on:
                self._add_item('light_off',
                    title='Turn %s off' % light_name,
                    autocomplete='lights:%s:off' % lid,
                    icon=icon,
                    arg=json.dumps({
                        'lid': lid,
                        'data': {'on': False},
                        'feedback': '%s turned off.' % light_name,
                    }))

            elif is_on is not None:
                self._add_item(
                    title='Turn %s on' % light_name,
                    autocomplete='lights:%s:on' % lid,
                    icon=icon,
                    arg=json.dumps({
                        'lid': lid,
                        'data': {'on': True},
                        'feedback': '%s turned on.' % light_name,
                    }))

            if is_on or lid == 'all':
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

            if lid != 'all':
                self._add_item('light_rename',
                    icon=icon,
                    autocomplete='lights:%s:rename:' % lid)

        elif len(control) >= 2:
            function = control[0]
            value = control[1]

            if function == 'color':
                converter = rgb_cie.Converter()
                current_hex = converter.xyToHEX(
                    light['state']['xy'][0],
                    light['state']['xy'][1],
                    light['state']['bri'],
                )

                self._add_item('set_color',
                    valid=True,
                    icon=icon,
                    arg=json.dumps({
                        'action': 'set_color',
                        'lid': lid,
                        'color': value,
                        'feedback': '%s color set to %s.' % (light_name, value),
                    }))

                self._add_item('color_picker',
                    icon=icon,
                    arg='colorpicker:%s:%s' % (lid, current_hex))

            elif function == 'bri':
                self._add_item('set_brightness',
                    title='Set brightness to %s' % (value + '%' if value else u'…'),
                    icon=icon,
                    valid=True if value else False,
                    arg=json.dumps({
                        'lid': lid,
                        'data': { 'bri': int((float(value) / 100) * 255) if value else 255 },
                        'feedback': '%s brigtness set to %s%%.' % (light_name, value),
                    }))

            elif function == 'effect':
                self._add_item('effect_none',
                    icon=icon,
                    arg=json.dumps({
                        'lid': lid,
                        'data': {'effect': 'none'},
                        'feedback': '%s effect set to none.' % light_name,
                    }))

                self._add_item('color_loop',
                    icon=icon,
                    arg=json.dumps({
                        'lid': lid,
                        'data': {'effect': 'colorloop'},
                        'feedback': '%s effect set to colorloop.' % light_name,
                    }))

            elif function == 'reminder':
                try:
                    int_value = int(value)
                except ValueError:
                    int_value = False

                def reminder_title(suffix):
                    return u'Blink {light_name} in {time} {suffix}'.format(
                        light_name=light_name,
                        time=(int_value or u'…'),
                        suffix=suffix,
                    )

                self._add_item(
                    title=reminder_title('seconds'),
                    subtitle='',
                    icon=icon,
                    valid=True if int_value else False,
                    arg=json.dumps({
                        'lid': lid,
                        'action': 'reminder',
                        'time_delta': int_value,
                        'feedback': 'Reminder set for %s seconds.' % int_value,
                    }))

                self._add_item(
                    title=reminder_title('minutes'),
                    subtitle='',
                    icon=icon,
                    valid=True if int_value else False,
                    arg=json.dumps({
                        'lid': lid,
                        'action': 'reminder',
                        'time_delta': (int_value * 60) if int_value else 0,
                        'feedback': 'Reminder set for %s minute(s).' % int_value,
                    }))

                self._add_item(
                    title=reminder_title('hours'),
                    subtitle='',
                    icon=icon,
                    valid=True if int_value else False,
                    arg=json.dumps({
                        'lid': lid,
                        'action': 'reminder',
                        'time_delta': (int_value * 60 * 60) if int_value else 0,
                        'feedback': 'Reminder set for %s hour(s).' % int_value,
                    }))

            elif function == 'rename':
                self._add_item('light_rename',
                    icon=icon,
                    valid=True,
                    arg=json.dumps({
                        'action': 'rename',
                        'lid': lid,
                        'data': {'name': value},
                        'feedback': '%s renamed to %s.' % (light_name, value),
                    }))

        self._filter_results()
        return self.results


class HuePresetsFilter(HueFilterBase):

    ICON = 'icons/preset.png'

    def get_results(self, query):
        self.partial_query = query

        for _, dirnames, __ in os.walk(alp.storage(join='presets')):
            for subdirname in dirnames:
                self._add_item(
                    title=subdirname,
                    icon=self.ICON,
                    autocomplete=subdirname,
                    arg=json.dumps({
                        'action': 'load_preset',
                        'preset_name': subdirname,
                    }),
                )

        if not self.results:
            self._add_item(
                title='You have no saved presets!',
                subtitle='Use "-hue save-preset" to save the current lights state as a preset.',
                icon=self.ICON,
                valid=False,
            )

        self._filter_results()
        return self.results


if __name__ == '__main__':
    hue_filter = HueFilter()
    results = hue_filter.get_results(alp.args())
    alp.feedback(results)
