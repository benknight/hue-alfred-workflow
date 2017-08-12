# -*- coding: utf-8 -*-
import colorsys
import datetime
import json
import os
import random
import sys
import time

from packages.workflow import Workflow3 as Workflow

import colors
import harmony
import request
import setup
import utils


class HueAction:

    def __init__(self):
        self.hue_request = request.HueRequest()

    def _get_xy_color(self, color, gamut):
        """Validate and convert hex color to XY space."""
        return colors.Converter(gamut).hex_to_xy(utils.get_color_value(color))

    def _get_random_xy_color(self, gamut):
        random_color = colorsys.hsv_to_rgb(random.random(), 1, 1)
        random_color = tuple([255 * x for x in random_color])
        return colors.Converter(gamut).rgb_to_xy(*random_color)

    def _set_palette(self, lids, palette):
        for index, lid in enumerate(lids):
            self.hue_request.request(
                'put',
                '/lights/%s/state' % lid,
                json.dumps({'xy': palette[index]})
            )

    def _shuffle_group(self, group_id):
        lights = utils.get_lights()
        lids = utils.get_group_lids(group_id)

        # Only shuffle the lights that are on
        on_lids = [lid for lid in lids if lights[lid]['state']['on']]
        on_xy = [lights[lid]['state']['xy'] for lid in on_lids]
        shuffled = list(on_xy)

        # Shuffle until all indexes are different (generate a derangement)
        while not all([on_xy[i] != shuffled[i] for i in range(len(on_xy))]):
            random.shuffle(shuffled)

        self._set_palette(on_lids, shuffled)

    def _set_harmony(self, group_id, mode, root):
        lights = utils.get_lights()
        lids = utils.get_group_lids(group_id)
        palette = []

        on_lids = [lid for lid in lids if lights[lid]['state']['on']]
        args = (len(on_lids), '#%s' % utils.get_color_value(root))
        harmony_colors = getattr(harmony, mode)(*args)

        for lid in on_lids:
            gamut = colors.get_light_gamut(lights[lid]['modelid'])
            xy = self._get_xy_color(harmony_colors.pop(), gamut)
            palette.append(xy)

        self._set_palette(on_lids, palette)

    # Returns True when an action is completed succesfully, False if not.
    def _action(self, action):
        is_setup = action[0] == 'set_bridge'
        is_light = action[0] == 'lights'
        is_group = action[0] == 'groups'

        if is_setup:
            bridge_ip = action[1]
            setup.set_bridge(bridge_ip)
            return False

        if is_light or is_group:
            rid = action[1]
            function = action[2]
            value = action[3] if len(action) > 3 else None
            lights = utils.get_lights()
            groups = utils.get_groups()

            # Default API request parameters
            method = 'put'
            endpoint = '/groups/%s/action' % rid if is_group else '/lights/%s/state' % rid

            if function == 'off':
                data = {'on': False}

            elif function == 'on':
                data = {'on': True}

            elif function == 'bri':
                value = int((float(value) / 100) * 255) if value else 255
                data = {'bri': value}

            elif function == 'shuffle':
                if not is_group:
                    print 'Shuffle can only be called on groups.'
                    return False

                self._shuffle_group(rid)
                return True

            elif function == 'rename':
                endpoint = '/lights/%s' % rid
                data = {'name': value}

            elif function == 'effect':
                data = {'effect': value}

            elif function == 'color':
                if value == 'random':
                    if is_group:
                        gamut = colors.GamutA
                        data = {'xy': self._get_random_xy_color(gamut)}
                    else:
                        gamut = colors.get_light_gamut(lights[rid]['modelid'])
                        data = {'xy': self._get_random_xy_color(gamut)}
                else:
                    try:
                        if is_group:
                            gamut = colors.GamutA
                        else:
                            gamut = colors.get_light_gamut(lights[rid]['modelid'])
                        data = {'xy': self._get_xy_color(value, gamut)}
                    except ValueError:
                        print 'Error: Invalid color. Please use a 6-digit hex color.'
                        return False

            elif function == 'harmony':
                if not is_group:
                    print 'Color harmonies can only be set on groups.'
                    return False

                root = action[4] if len(action) > 3 else None

                if value not in harmony.MODES:
                    print 'Invalid harmony mode.'
                    return False

                self._set_harmony(rid, value, root)
                return True

            elif function == 'reminder':
                try:
                    time_delta_int = int(value)
                except ValueError:
                    print 'Error: Invalid time delta for reminder.'
                    return False

                reminder_time = datetime.datetime.utcfromtimestamp(time.time() + time_delta_int)

                method = 'post'
                data = {
                    'name': 'Alfred Hue Reminder',
                    'command': {
                        'address': self.hue_request.api_path + endpoint,
                        'method': 'PUT',
                        'body': {'alert': 'lselect'},
                    },
                    'time': reminder_time.replace(microsecond=0).isoformat(),
                }
                endpoint = '/schedules'

            elif function == 'set':
                data = {'scene': value}

            elif function == 'save':
                lids = utils.get_group_lids(rid)
                method = 'post'
                endpoint = '/scenes'
                data = {'name': value, 'lights': lids, 'recycle': False}

            else:
                return False

            # Make the request
            self.hue_request.request(method, endpoint, json.dumps(data))

        # end is_light or is_group check
        return True

    def execute(self, action_string):
        action = action_string.split(':')
        try:
            show_result = self._action(action)
            if show_result:
                print 'Action completed! <%s>' % action_string
        except ValueError:
            pass


def main(workflow):
    query = workflow.args[0]
    action = HueAction()
    action.execute(query)


if __name__ == '__main__':
    workflow = Workflow()
    sys.exit(workflow.run(main))
