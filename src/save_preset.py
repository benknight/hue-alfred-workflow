# -*- coding: utf-8 -*-
import os
import shutil

import alp


def save_preset(preset_name):
    preset_dir = alp.storage(join='presets/%s/' % preset_name)
    os.makedirs(preset_dir)
    shutil.copy2(alp.cache('lights.json'), preset_dir)
    print 'Preset saved: %s' % preset_name


if __name__ == '__main__':
    settings = alp.Settings()
    if settings.get('username'):
        save_preset(alp.args()[0])
    else:
        print 'To save presets please use "-hue set-bridge" to enable this workflow.'
