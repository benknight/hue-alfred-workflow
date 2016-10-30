# -*- coding: utf-8 -*-
import colorsys
from collections import OrderedDict

from .packages import alp
from .packages import png
from .packages import requests

from . import colors


def search_for_bridge(timeout=3):
    """Searches for a bridge on the local network and returns the IP if it
    finds one."""
    r = requests.get('http://www.meethue.com/api/nupnp', timeout=timeout)
    bridges = r.json()
    if len(bridges) > 0:
        return bridges[0]['internalipaddress']
    else:
        return None

def load_lights_data_from_api(timeout=3):
    """Downloads lights data and caches it locally."""

    # Requests is an expensive import so we only do it when necessary.
    from .packages import requests

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

    alp.jsonDump(lights, alp.cache('lights.json'))

    # Create icon for light
    for lid, light_data in lights.iteritems():
        create_light_icon(lid, light_data)

def create_light_icon(lid, light_data):
    """Creates a 1x1 PNG icon of light's RGB color and saves it to the local dir.
    """
    # Create a color converter & helper
    converter = colors.Converter()

    # Set color based on the type of light
    # See: http://www.developers.meethue.com/documentation/supported-lights
    if light_data['state'].get('xy'):
        rgb_value = converter.xyToRGB(light_data['state']['xy'][0], light_data['state']['xy'][1])
    elif light_data['state'].get('bri'):
        rgb_value = colorsys.hsv_to_rgb(0, 0, float(light_data['state']['bri']) / 255)
        rgb_value = tuple([255 * x for x in rgb_value])
    else:
        rgb_value = (255, 255, 255) if light_data['state']['on'] else (0, 0, 0)

    f = open(alp.local('icons/%s.png' % lid), 'wb')
    w = png.Writer(1, 1)
    w.write(f, [rgb_value])
    f.close()

def get_lights(from_cache=False):
    """Returns a dictionary of lid => data, or None if no lights data is in the cache.
    Returns None if there are issues connecting to the bridge.

    Options:
        from_cache - Read data from cached json files instead of querying the API.
    """
    output = dict()

    if not from_cache:
        from .packages.requests.exceptions import RequestException
        try:
            try:
                load_lights_data_from_api()
            except RequestException:
                try:
                    bridge_ip = search_for_bridge()
                    if not bridge_ip:
                        return None
                    settings = alp.Settings()
                    settings.set(bridge_ip=bridge_ip)
                    load_lights_data_from_api()
                except RequestException:
                    return None
        except TypeError:
            return None

    lights = alp.jsonLoad(alp.cache('lights.json'))

    return OrderedDict(sorted(lights.items()))
