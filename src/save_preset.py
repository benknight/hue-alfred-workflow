# -*- coding: utf-8 -*-
import os

import alp


def save_preset(preset_name):
    lights = alp.jsonLoad(alp.cache('lights.json'))

    # Create dir
    preset_dir = alp.storage(join='presets/' + preset_name)
    os.makedirs(preset_dir)

    # Dump lights.json
    alp.jsonDump(lights, preset_dir + '/lights.json')

    # for each light do this
    for lid in lights:
        light = alp.jsonLoad(alp.cache('%s.json' % lid))
        alp.jsonDump(light, preset_dir + ('/%s.json' % lid))

    print 'Preset saved: %s' % preset_name


if __name__ == '__main__':
    settings = alp.Settings()
    if settings.get('username'):
        save_preset(alp.args()[0])
    else:
        print 'To save presets please use "-hue set-bridge" to enable this workflow.'
