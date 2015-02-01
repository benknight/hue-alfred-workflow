# -*- coding: utf-8 -*-
from .packages import alp
from .packages import png

from . import colors


def _load_lights_data_from_api(timeout=6):
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
        _create_light_icon(lid, light_data)

def _create_light_icon(lid, light_data):
    """Creates a 1x1 PNG icon of light's RGB color and saves it to the local dir.
    """
    # Create a color converter & helper
    converter = colors.Converter()
    color_helper = colors.ColorHelper()

    hex_color = converter.xyToHEX(
        light_data['state']['xy'][0],
        light_data['state']['xy'][1],
    )
    f = open(alp.local('icons/%s.png' % lid), 'wb')
    w = png.Writer(1, 1)
    w.write(f, [color_helper.hexToRGB(hex_color)])
    f.close()

def get_lights(from_cache=False):
    """Returns a dictionary of lid => data, or None if no lights data is in the cache.

    Options:
        from_cache - Read data from cached json files instead of querying the API.
    """
    output = dict()

    if not from_cache:
        from requests.exceptions import RequestException
        try:
            _load_lights_data_from_api()
        except RequestException:
            return None

    lights = alp.jsonLoad(alp.cache('lights.json'))

    return lights
