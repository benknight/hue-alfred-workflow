# encoding: utf-8
from __future__ import unicode_literals

import colorsys
import re

from packages import png
from packages.workflow import Workflow3 as Workflow

import colors
from css_colors import CSS_LITERALS as css_colors

workflow = Workflow()


def search_for_bridge(timeout=3):
    """Searches for a bridge on the local network and returns the IP if it
    finds one."""
    from packages import requests

    r = requests.get('http://www.meethue.com/api/nupnp', timeout=timeout)
    bridges = r.json()

    if len(bridges) > 0:
        return bridges[0]['internalipaddress']
    else:
        return None


def load_full_state(timeout=3):
    """Downloads full state and caches it locally."""
    # Requests is an expensive import so we only do it when necessary.
    from packages import requests

    r = requests.get(
        'http://{0}/api/{1}'.format(
            workflow.settings['bridge_ip'],
            workflow.settings['username'],
        ),
        timeout=timeout,
    )

    data = r.json()

    # Create icon for light
    for lid, light_data in data['lights'].iteritems():
        create_light_icon(lid, light_data)

    workflow.store_data('full_state', data)


def create_light_icon(lid, light_data):
    """Creates a 1x1 PNG icon of light's RGB color and saves it to the local dir.
    """
    # Create a color converter & helper
    converter = colors.Converter()

    # Set color based on the type of light
    # See: http://www.developers.meethue.com/documentation/supported-lights
    if light_data['state'].get('xy'):
        rgb_value = converter.xy_to_rgb(light_data['state']['xy'][0], light_data['state']['xy'][1])
    elif light_data['state'].get('bri'):
        rgb_value = colorsys.hsv_to_rgb(0, 0, float(light_data['state']['bri']) / 255)
        rgb_value = tuple([255 * x for x in rgb_value])
    else:
        rgb_value = (255, 255, 255) if light_data['state']['on'] else (0, 0, 0)

    f = open('icons/%s.png' % lid, 'wb')
    w = png.Writer(1, 1)
    w.write(f, [rgb_value])
    f.close()


def get_lights(from_cache=False):
    """Returns a dictionary of lid => data, or None if no lights data is in the cache.
    Returns None if there are issues connecting to the bridge.

    Options:
        from_cache - Read data from cached json files instead of querying the API.
    """
    if not from_cache:
        from .packages.requests.exceptions import RequestException
        try:
            try:
                load_full_state()
            except RequestException:
                try:
                    bridge_ip = search_for_bridge()
                    if not bridge_ip:
                        return None
                    workflow.settings['bridge_ip'] = bridge_ip
                    load_full_state()
                except RequestException:
                    return None
        except TypeError:
            return None

    data = workflow.stored_data('full_state')
    return data['lights']


def get_groups():
    data = workflow.stored_data('full_state')

    try:
        groups = data['groups']
        return {id: group for id, group in groups.iteritems()}
    except TypeError:
        return None


def get_group_lids(group_id):
    if group_id == '0':
        lids = get_lights(from_cache=True).keys()
    else:
        group = get_groups().get(group_id)
        lids = group['lights']
    return lids


def get_scenes(group_id):
    data = workflow.stored_data('full_state')
    scenes = data['scenes']
    lids = get_group_lids(group_id)
    return {id: scene for id, scene in scenes.iteritems() if (
            set(scene['lights']) == set(lids) and
            scene['name'] != 'Off') and
            scene['version'] >= 2}


def get_color_value(color):
    """Processes and returns a valid hex color value.
    Raises error if 'color' is invalid.
    """
    hex_color_re = re.compile(
        r'(?<!\w)([a-f0-9]){2}([a-f0-9]){2}([a-f0-9]){2}\b',
        re.IGNORECASE
    )

    if color in css_colors:
        color = css_colors[color]

    color = color.lstrip('#')

    if not hex_color_re.match(color):
        raise ValueError

    return color


def is_valid_color(color):
    try:
        get_color_value(color)
        return True
    except ValueError:
        return False
