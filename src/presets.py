# -*- coding: utf-8 -*-
import os
import shutil

from .packages import alp


def save(preset_name):
    settings = alp.Settings()
    if not settings.get('username'):
        print 'To save presets please use "-hue set-bridge" to enable this workflow.'
    else:
        preset_dir = alp.storage(join='presets/%s/' % preset_name)
        os.makedirs(preset_dir)
        shutil.copy2(alp.cache('lights.json'), preset_dir)
        print 'Preset saved: %s' % preset_name
