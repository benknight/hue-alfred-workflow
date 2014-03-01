# -*- coding: utf-8 -*-
import json

import alp
import requests


class HueAlfredSetup:

    def setup(self):
        r = requests.get('http://www.meethue.com/api/nupnp')
        bridges = r.json()

        if not bridges:
            print 'No bridges found on your network.'
        else:
            bridge_ip = bridges[0]['internalipaddress']
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

        return None

    def set_group(self, arg):
        settings = alp.Settings()

        if arg == '0':
            settings.set(group='')
        else:
            lights = arg.split(',')

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

        return None


if __name__ == '__main__':
    hue_setup = HueAlfredSetup()
    args = alp.args()

    if args:
        hue_setup.set_group(args[0])
    else:
        try:
            hue_setup.setup()
        except requests.exceptions.RequestException:
            print 'Connection error.'
