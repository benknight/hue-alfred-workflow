# -*- coding: utf-8 -*-
from distutils.version import LooseVersion

from .packages import alp
from .packages import requests


REMOTE_VERSION_URI = 'https://raw.githubusercontent.com/benknight/hue-alfred-workflow/master/VERSION'
DOWNLOAD_URI = 'https://github.com/benknight/hue-alfred-workflow'

results = []


def check_version(remote_version):
    # Get local version
    with open('VERSION', 'r') as f: local_version = f.read()

    if LooseVersion(local_version.rstrip()) < LooseVersion(remote_version.rstrip()):
        results.append(alp.Item(
            title='New version available! (%s)' % remote_version,
            subtitle='Press enter to download.  You are currently using version %s' % local_version,
            valid=True,
            arg=DOWNLOAD_URI,
        ))
    else:
        results.append(alp.Item(
            title='Congrats! You are using the latest version (%s).' % local_version,
            valid=False,
        ))


try:
    r = requests.get(REMOTE_VERSION_URI)
    remote_version = r.text
    check_version(remote_version)
except requests.exceptions.RequestException:
    results.append(alp.Item(
        title='Unable to determine latest version.',
        subtitle='You must be connected to the Internet for this to work.',
        valid=False,
    ))

alp.feedback(results)
