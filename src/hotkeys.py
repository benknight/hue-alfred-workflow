import json

import alp

import helpers
import rgb_cie
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
            json.dumps({'on': True})
        )
        print 'All lights toggled off.'

    elif q == 'All On':
        hue_request.request(
            'put',
            '%s/action' % group_id,
            json.dumps({'on': False})
        )
        print 'All lights toggled on.'

    elif q == 'Random':
        converter = rgb_cie.Converter()
        for lid in lights:
            hue_request.request(
                'put',
                '/lights/%s/state' % lid,
                json.dumps({'xy': converter.getCIEColor()})
            )

