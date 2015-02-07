# -*- coding: utf-8 -*-
import json
import os

from .packages import alp
from .packages import yaml

from . import colors
from . import utils


class HueFilterBase:

    items_yaml = ''

    # A list of alp.Item
    results = []

    # For filtering results at the end to add a simple autocomplete
    partial_query = None

    # A default icon
    icon = 'icon.png'

    def __init__(self):
        self.items = yaml.load(self.items_yaml)

    def _add_item(self, string_key=None, **kwargs):
        """A convenient way of adding items based on the yaml data."""
        if string_key and self.items.get(string_key):
            for k, v in self.items[string_key].items():
                kwargs.setdefault(k, v)

        if not kwargs.get('icon'):
            kwargs['icon'] = self.icon

        self.results.append(alp.Item(**kwargs))

    def _partial_query_filter(self, result):
        """Returns True if the result is valid match for the partial query, else False.

            Args:
                result - an instance of alp.Item
        """
        if self.partial_query:
            if result.autocomplete is not None:
                return (self.partial_query.lower() in result.autocomplete.lower())
            else:
                return False
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
            lights = utils.get_lights(from_cache=True)
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
            lights = utils.get_lights()

            if not lights:
                self._add_item('bridge_failed')
            else:
                self._add_item('all_lights')

                if query.startswith('lights:'):
                    self.partial_query = query.split(':')[1]

                for lid, light in lights.items():
                    title = light['name']

                    if light['state']['on']:
                        subtitle = []
                        if light['state'].get('hue'):
                            subtitle.append(u'hue: {hue}'.format(
                                hue=u'{0:.0f}°'.format(float(light['state']['hue']) / 65535 * 360)))
                        if light['state'].get('bri') is not None:
                            subtitle.append(u'bri: {bri}'.format(
                                bri=u'{0:.0f}%'.format(float(light['state']['bri']) / 255 * 100)))
                        if light['state'].get('sat') is not None:
                            subtitle.append(u'sat: {sat}'.format(
                                sat=u'{0:.0f}%'.format(float(light['state']['sat']) / 255 * 100)))
                        subtitle = ', '.join(subtitle) or 'on'
                        icon = 'icons/%s.png' % lid
                    else:
                        subtitle = 'off'
                        icon = 'icons/off.png'

                    if not light['state'].get('reachable'):
                        title += u' **'
                        subtitle += u' — may not be reachable'

                    self.results.append(alp.Item(
                        title=title,
                        subtitle=u'({lid}) {subtitle}'.format(
                            lid=lid,
                            subtitle=subtitle,
                        ),
                        valid=False,
                        icon=icon,
                        autocomplete='lights:%s:' % lid))

                self._add_item('presets')
                self._add_item('help')

        self._filter_results()
        return self.results


class HuePresetsFilter(HueFilterBase):

    items_yaml = '''
no_presets:
    title: You have no saved presets!
    subtitle: Use "-hue save-preset" to save the current lights state as a preset.
    valid: false
'''

    icon = 'icons/preset.png'

    def get_results(self, query):
        self.partial_query = query

        for _, dirnames, __ in os.walk(alp.storage(join='presets')):
            for subdirname in dirnames:
                self._add_item(
                    title=subdirname,
                    autocomplete=subdirname,
                    arg='presets:load:%s' % subdirname
                )

        if not self.results:
            self._add_item('no_presets')

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

random_color:
  title: Random color
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
  title: Rename to…
  valid: false
'''

    def get_results(self, lid, light, query):
        control = query.split(':')
        is_on = light and light['state']['on']
        light_name = light['name'] if lid != 'all' else 'all lights'

        if lid != 'all':
            self.icon = ('icons/%s.png' % lid) if is_on else 'icons/off.png'

        if len(control) is 1:
            self.partial_query = control[0]

            if is_on or lid == 'all':
                self._add_item('light_off',
                    title='Turn %s off' % light_name,
                    arg='lights:%s:off' % lid)

            if not is_on or lid == 'all':
                self._add_item(
                    title='Turn %s on' % light_name,
                    arg='lights:%s:on' % lid)

            if is_on or lid == 'all':
                if lid == 'all' or light['state'].get('xy'):
                    self._add_item('set_color',
                        subtitle='',
                        autocomplete='lights:%s:color:' % lid)

                if lid == 'all' or light['state'].get('effect') is not None:
                    self._add_item('set_effect',
                        subtitle='',
                        autocomplete='lights:%s:effect:' % lid)

                self._add_item('set_brightness',
                    subtitle='',
                    autocomplete='lights:%s:bri:' % lid)

                self._add_item('set_reminder',
                    autocomplete='lights:%s:reminder:' % lid)

            if lid != 'all':
                self._add_item('light_rename',
                    autocomplete='lights:%s:rename:' % lid)

        elif len(control) >= 2:
            function = control[0]
            value = control[1]

            if function == 'color':
                converter = colors.Converter()

                if lid == 'all':
                    current_hex = 'ffffff'
                else:
                    current_hex = converter.xyToHEX(
                        light['state']['xy'][0],
                        light['state']['xy'][1],
                        light['state']['bri'])

                self._add_item('set_color', valid=True, arg='lights:%s:color:%s' % (lid, value))
                self._add_item('random_color', arg='lights:%s:color:random' % lid)
                self._add_item('color_picker', arg='colorpicker:%s:%s' % (lid, current_hex))

            elif function == 'bri':
                self._add_item('set_brightness',
                    title='Set brightness to %s' % (value + '%' if value else u'…'),
                    valid=True if value else False,
                    arg='lights:%s:bri:%s' % (lid, value))

            elif function == 'effect':
                self._add_item('effect_none', arg='lights:%s:effect:none' % lid)
                self._add_item('color_loop', arg='lights:%s:effect:colorloop' % lid)

            elif function == 'reminder':
                def reminder_title(suffix):
                    return u'Blink {light_name} in {time} {suffix}'.format(
                        light_name=light_name,
                        time=(int_value or u'…'),
                        suffix=suffix)

                try:
                    int_value = int(value)
                except ValueError:
                    int_value = 0

                self._add_item(
                    title=reminder_title('seconds'),
                    subtitle='',
                    valid=True if int_value else False,
                    arg='lights:%s:reminder:%s' % (lid, int_value))

                self._add_item(
                    title=reminder_title('minutes'),
                    subtitle='',
                    valid=True if int_value else False,
                    arg='lights:%s:reminder:%s' % (lid, int_value * 60))

                self._add_item(
                    title=reminder_title('hours'),
                    subtitle='',
                    valid=True if int_value else False,
                    arg='lights:%s:reminder:%s' % (lid, int_value * 60 * 60))

            elif function == 'rename':
                self._add_item('light_rename',
                    title='Rename to %s' % value,
                    valid=True,
                    arg='lights:%s:rename:%s' % (lid, value))

        self._filter_results()
        return self.results


if __name__ == '__main__':
    hue_filter = HueFilter()
    results = hue_filter.get_results(alp.args())
    alp.feedback(results)
