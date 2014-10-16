import json
import random

import alp

import helpers
from hue_request import HueRequest


q = alp.args()[0]
lights = helpers.get_lights()

if not lights:
    print 'No Hue lights found. Try -hue set-bridge.'
else:
    hue_request = HueRequest()
    settings = alp.Settings()

    if settings.get('group'):
        group_id = settings.get('group_id')
    else:
        group_id = '/groups/0'

    if q == 'All Off':
        hue_request.request(
            'put',
            '%s/action' % group_id,
            json.dumps({'on': False})
        )
        print 'All lights toggled off.'

    elif q == 'All On':
        hue_request.request(
            'put',
            '%s/action' % group_id,
            json.dumps({'on': True})
        )
        print 'All lights toggled on.'

    elif q == 'Random':
        for lid in lights:
            hue_request.request(
                'put',
                '/lights/%s/state' % lid,
                json.dumps({
                    'hue': random.randrange(0, 65535),
                    'sat': 255,
                })
            )
        print 'Lights set to random hues.'

