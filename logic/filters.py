# encoding: utf-8
from __future__ import unicode_literals

import json
import os
import sys

from packages.workflow import Workflow3 as Workflow
from packages import yaml

import colors
import utils


class HueFilterBase:

    # Templates YAML
    templates_yaml = ''

    # For filtering results at the end to add a simple autocomplete
    partial_query = None

    # A default icon
    icon = 'default.png'

    # The query string
    query = None

    # List of items
    items = []

    # Workflow instance
    workflow = None

    def __init__(self, workflow):
        self.query = workflow.args[0]
        self.workflow = workflow
        self.templates = yaml.load(self.templates_yaml)

    def _add_item(self, string_key=None, **item):
        if string_key and self.templates.get(string_key):
            for k, v in self.templates[string_key].items():
                item.setdefault(k, v)

        item['icon'] = 'icons/%s' % (item['icon'] if item.get('icon') else self.icon)
        item['autocomplete'] = (
            '|'.join(self.query.split('|')[:-1] + [item['autocomplete']])
            if item.get('autocomplete') else None
        )

        self.items.append(item)

    def _filter_items(self):
        if self.partial_query:
            self.items = self.workflow.filter(
                self.partial_query,
                self.items,
                lambda item: item.get('title'))

    def _get_active_query(self):
        return self.query.split('|')[-1]


class HueIndexFilter(HueFilterBase):

    templates_yaml = '''
bridge_failed:
  title: Failed to connect to bridge.
  subtitle: Press the button on the bridge then press enter to enable the workflow. Optionally specify the bridge's IP.
  icon: bridge.png

all_lights:
  title: All lights
  autocomplete: 'groups:0:'
'''

    def get_items(self):
        query = self._get_active_query()

        if ((query.startswith('lights') or query.startswith('groups')) and len(query.split(':')) >= 3):
            action_filter = HueActionFilter(self.workflow)
            control = query.split(':')
            lights = utils.get_lights(from_cache=True)
            groups = utils.get_groups()
            rid = control[1]

            self.items = action_filter.get_items(
                query=':'.join(control[2:]),  # lights:1:<light_query>
                id=rid,
                type=HueActionFilter.LIGHT_TYPE if query.startswith('lights') else HueActionFilter.GROUP_TYPE,
                resource=lights.get(rid, None) if query.startswith('lights') else groups.get(rid, None))

        else:  # Show index
            if not self.workflow.settings.get('username'):
                self._add_item(
                    'bridge_failed',
                    valid=True,
                    title='Link with Hue bridge',
                    arg='set_bridge:%s' % query)

            else:
                lights = utils.get_lights()
                groups = utils.get_groups()

                if not lights:
                    self._add_item(
                        'bridge_failed',
                        valid=True,
                        arg='set_bridge:%s' % query)

                else:
                    self._add_item('all_lights')

                    for rid, room in groups.items():
                        self._add_item(
                            title=room['name'],
                            autocomplete='groups:%s:' % rid)

                    if query.startswith('lights:') or query.startswith('groups:'):
                        self.partial_query = query.split(':')[1]

                    for lid, light in lights.items():
                        title = light['name']

                        if light['state']['on']:
                            subtitle = []
                            if light['state'].get('hue'):
                                subtitle.append('hue: {hue}'.format(
                                    hue='{0:.0f}°'.format(float(light['state']['hue']) / 65535 * 360)))
                            if light['state'].get('bri') is not None:
                                subtitle.append('bri: {bri}'.format(
                                    bri='{0:.0f}%'.format(float(light['state']['bri']) / 255 * 100)))
                            if light['state'].get('sat') is not None:
                                subtitle.append('sat: {sat}'.format(
                                    sat='{0:.0f}%'.format(float(light['state']['sat']) / 255 * 100)))
                            subtitle = ', '.join(subtitle) or 'on'
                            icon = '%s.png' % lid
                        else:
                            subtitle = 'off'
                            icon = 'off.png'

                        if not light['state'].get('reachable'):
                            title += ' **'
                            subtitle += ' — may not be reachable'

                        self._add_item(
                            title=title,
                            subtitle='({lid}) {subtitle}'.format(
                                lid=lid,
                                subtitle=subtitle,
                            ),
                            icon=icon,
                            autocomplete='lights:%s:' % lid)

                    # self._add_item('help')

        self._filter_items()
        return self.items


class HueActionFilter(HueFilterBase):

    templates_yaml = '''
set_color:
  title: Set color…
  subtitle: Accepts 6-digit hex colors or CSS literal color names (e.g. "blue")
  icon: color.png

color_picker:
  title: Use color picker…

random_color:
  title: Random color

set_effect:
  title: Set effect…
  icon: effect.png

effect_none:
  title: None
  subtitle: Cancel any ongoing effects, such as a color loop.

color_loop:
  title: Color loop

set_brightness:
  title: Set brightness…
  subtitle: Set on a scale from 0 to 100. Note that 0 is not off.
  icon: brightness.png

set_reminder:
  title: Set reminder…
  subtitle: Blink after a specified interval.
  icon: reminder.png

rename:
  title: Rename to…
  icon: rename.png

set_harmony:
  title: Set harmony…
  subtitle: Use color wheel relationships such as analogous, complementary, triad, etc.
  icon: harmony.png

shuffle:
  title: Shuffle
  subtitle: Shuffle to change each light to a new color, maintaining the same colors.
  icon: shuffle.png

set_scene:
  title: Set scene…
  icon: scene.png

save_scene:
  title: Create scene…
  icon: scene.png
'''

    LIGHT_TYPE = 'lights'
    GROUP_TYPE = 'groups'

    def get_items(self, query, id, type, resource):
        control = query.split(':')
        is_on = (type == self.LIGHT_TYPE and resource['state']['on'])
        name = resource['name'] if resource else 'All lights'

        if type == self.LIGHT_TYPE:
            self.icon = ('%s.png' % id) if is_on else 'off.png'

        if len(control) is 1:
            self.partial_query = control[0]

            if type == self.GROUP_TYPE or is_on:
                self._add_item(
                    title='Turn %s off' % name,
                    icon='%s.png' % id if type == self.LIGHT_TYPE else 'off.png',
                    arg='%s:%s:off' % (type, id),
                    autocomplete='%s:%s:off' % (type, id),
                    valid=True)

            if type == self.GROUP_TYPE or not is_on:
                self._add_item(
                    'light_on',
                    icon='on.png',
                    title='Turn %s on' % name,
                    arg='%s:%s:on' % (type, id),
                    valid=True)

            if type == self.GROUP_TYPE or is_on:
                if type == self.GROUP_TYPE:
                    self._add_item(
                        'shuffle',
                        arg='%s:%s:shuffle' % (type, id),
                        valid=True)

                if type == self.GROUP_TYPE:
                    # maybe settings scenes should be disabled for "All lights"
                    # if the bridge is deconz
                    self._add_item(
                        'set_scene',
                        autocomplete='groups:%s:set:' % id)

                # Sadly the Hue app will only show scenes that *IT* created,
                # meaning scenes saved by this workflow do not show up in the
                # Hue app. So to keep scene CRUD more simple, this has been
                # disabled.

                # if type == self.GROUP_TYPE:
                #     self._add_item('save_scene', autocomplete='groups:%s:save:' % id)

                if type == self.GROUP_TYPE or (type == self.LIGHT_TYPE and resource['state'].get('xy')):
                    self._add_item(
                        'set_color',
                        subtitle='',
                        autocomplete='%s:%s:color:' % (type, id))

                self._add_item(
                    'set_brightness',
                    subtitle='',
                    autocomplete='%s:%s:bri:' % (type, id))

                if type == self.GROUP_TYPE:
                    self._add_item('set_harmony', autocomplete='groups:%s:harmony:' % id)

                if type == self.GROUP_TYPE or resource['state'].get('effect') is not None:
                    self._add_item(
                        'set_effect',
                        subtitle='',
                        autocomplete='%s:%s:effect:' % (type, id))

                self._add_item('set_reminder', autocomplete='%s:%s:reminder:' % (type, id))

            self._add_item('rename', autocomplete='%s:%s:rename:' % (type, id))

        elif len(control) >= 2:
            function = control[0]
            value = control[1]

            if function == 'set':
                self.icon = 'scene.png'
                self.partial_query = value
                scenes = utils.get_scenes(id)
                items = sorted(scenes.items(), key=lambda (k, v): v.get('lastupdated'))
                for sid, scene in items:
                    self._add_item(
                        title=scene['name'],
                        arg='groups:%s:set:%s' % (id, sid),
                        valid=True)

            # if function == 'save':
            #     self._add_item(
            #         icon='scene.png',
            #         title='Save current state as %s' % (value or '…'),
            #         valid=True,
            #         arg='groups:%s:save:%s' % (id, value))

            if function == 'color':
                self.icon = 'color.png'
                converter = colors.Converter()

                if type == self.GROUP_TYPE:
                    current_hex = 'ffffff'
                else:
                    current_hex = converter.xy_to_hex(
                        resource['state']['xy'][0],
                        resource['state']['xy'][1],
                        resource['state']['bri'])

                self._add_item(
                    'set_color',
                    valid=utils.is_valid_color(value),
                    arg='%s:%s:color:%s' % (type, id, value))

                self._add_item(
                    'random_color',
                    valid=True,
                    arg='%s:%s:color:random' % (type, id))

                self._add_item(
                    'color_picker',
                    valid=True,
                    arg='colorpicker %s:%s:color:<color>' % (type, id))

            elif function == 'bri':
                self._add_item(
                    'set_brightness',
                    title='Set brightness to %s' % (value + '%' if value else '…'),
                    valid=True if value else False,
                    arg='%s:%s:bri:%s' % (type, id, value))

            elif function == 'effect':
                self.icon = 'effect.png'
                self.partial_query = value

                self._add_item(
                    'effect_none',
                    valid=True,
                    arg='%s:%s:effect:none' % (type, id))

                self._add_item(
                    'color_loop',
                    valid=True,
                    arg='%s:%s:effect:colorloop' % (type, id))

            elif function == 'reminder':
                self.icon = 'reminder.png'

                def reminder_title(suffix):
                    return 'Blink {name} in {time} {suffix}'.format(
                        name=name,
                        time=(int_value or '…'),
                        suffix=suffix)

                try:
                    int_value = int(value)
                except ValueError:
                    int_value = 0

                self._add_item(
                    title=reminder_title('minutes'),
                    subtitle='',
                    valid=True if int_value else False,
                    arg='%s:%s:reminder:%s' % (type, id, int_value * 60))

                self._add_item(
                    title=reminder_title('hours'),
                    subtitle='',
                    valid=True if int_value else False,
                    arg='%s:%s:reminder:%s' % (type, id, int_value * 60 * 60))

            elif function == 'rename':
                self._add_item(
                    'rename',
                    title='Rename to %s' % value,
                    valid=True,
                    arg='%s:%s:rename:%s' % (type, id, value))

            elif function == 'harmony':
                mode = value

                if mode:
                    root_color = control[2]
                    is_valid_color = utils.is_valid_color(root_color)

                    self._add_item(
                        'set_color',
                        title='Set harmony root color…',
                        icon='%s.png' % mode,
                        valid=is_valid_color,
                        arg='groups:%s:harmony:%s:%s' % (id, mode, root_color))

                    self._add_item(
                        'color_picker',
                        icon='%s.png' % mode,
                        valid=True,
                        arg='colorpicker groups:%s:harmony:%s:<color>' % (id, mode))

                else:
                    self._add_item(
                        title='Analogous',
                        subtitle='Colors that are adjacent to each other. Recommended!',
                        icon='analogous.png',
                        autocomplete='groups:%s:harmony:analogous:' % id)

                    self._add_item(
                        title='Complementary',
                        subtitle='Colors that are opposite each other.',
                        icon='complementary.png',
                        autocomplete='groups:%s:harmony:complementary:' % id)

                    self._add_item(
                        title='Triad',
                        subtitle='Colors that are evenly spaced by thirds.',
                        icon='triad.png',
                        autocomplete='groups:%s:harmony:triad:' % id)

                    self._add_item(
                        title='Tetrad',
                        subtitle='Colors that are evenly spaced by quarters.',
                        icon='tetrad.png',
                        autocomplete='groups:%s:harmony:tetrad:' % id)

                    self._add_item(
                        title='Split Complementary',
                        subtitle='Colors that are opposite and adjacent.',
                        icon='split_complementary.png',
                        autocomplete='groups:%s:harmony:split_complementary:' % id)

        self._filter_items()
        return self.items


def main(workflow):
    if workflow.update_available:
        workflow.add_item(
            'New version available!',
            'Press enter to install the update.',
            autocomplete='workflow:update')
    hue_index_filter = HueIndexFilter(workflow)
    items = hue_index_filter.get_items()
    for item in items:
        i = workflow.add_item(**item)
    workflow.send_feedback()


if __name__ == '__main__':
    workflow = Workflow(update_settings={
        'github_slug': 'benknight/hue-alfred-workflow',
    })
    sys.exit(workflow.run(main))
