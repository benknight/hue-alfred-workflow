# -*- coding: utf-8 -*-
import json

import alp
import requests


class HueAlfredSetup:

    def setup(self, bridge_ip=None):
        if not bridge_ip:
            r = requests.get('http://www.meethue.com/api/nupnp')
            bridges = r.json()

            if not bridges:
                print 'No bridges found on your network.  Try specifying the IP if you know it.'
            else:
                bridge_ip = bridges[0]['internalipaddress']

        if bridge_ip:
            settings = alp.Settings()

            # Create API user for the workflow
            r = requests.post(
                'http://{bridge_ip}/api'.format(bridge_ip=bridge_ip),
                data=json.dumps({'devicetype': 'Alfred 2'}))

            resp = r.json()[0]

            if resp.get('error'):
                print 'Setup Error: %s' % resp['error'].get('description')
            else:
                settings.set(bridge_ip=bridge_ip, group='')
                settings.set(username=resp['success']['username'])
                print 'Success! You can now control your lights by using the "hue" keyword.'

    def set_group(self, group):
        settings = alp.Settings()

        if group == '0':
            settings.set(group='')
        else:
            lights = group.split(',')

            if not settings.get('group_id'):
                # Create a custom group for the workflow to use
                r = requests.post(
                    'http://{bridge_ip}/api/{user}/groups'.format(
                        bridge_ip=settings.get('bridge_ip'),
                        user=settings.get('username')
                    ),
                    data=json.dumps({
                        'name': 'Afred Hue Group',
                        'lights': lights,
                    })
                )

                resp = r.json()

                if len(resp) > 0:
                    if resp[0].get('error'):
                        print 'Setup Error: %s' % resp[0]['error'].get('description')
                    else:
                        settings.set(group_id=resp[0]['success']['id'])
            else:
                r = requests.put(
                    'http://{bridge_ip}/api/{user}{group_id}'.format(
                        bridge_ip=settings.get('bridge_ip'),
                        user=settings.get('username'),
                        group_id=settings.get('group_id'),
                    ),
                    data=json.dumps({
                        'lights': lights,
                    })
                )

            settings.set(group=lights)
