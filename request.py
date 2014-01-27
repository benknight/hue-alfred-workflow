import httplib
import json
import plistlib
import re
import sys

import rgb_cie
from css_colors import CSS_LITERALS


def xy_color(color):
	"""Validate and convert hex color to XY space."""
	rgb_cie_converter = rgb_cie.Converter()
	hex_color_re = re.compile(r'(?<!\w)([a-f0-9]){2}([a-f0-9]){2}([a-f0-9]){2}\b', re.IGNORECASE)

	if color in CSS_LITERALS:
		color = CSS_LITERALS[color]

	color = color.lstrip('#')

	if not hex_color_re.match(color):
		print 'Invalid color. Please use a 6-digit hex color.'
		sys.exit()

	return rgb_cie_converter.hexToCIE1931(color)

def send(query):
	"""Simply decodes json query and makes the API call."""

	query = json.loads(query)
	settings = plistlib.readPlist('settings.plist')
	base_path = '/api/' + settings['api.username']
	method = 'PUT'

	if query.get('_color'):
		data = json.dumps({'xy': xy_color(query['_color'])})
	else:
		data = json.dumps(query['data'])

	if query.get('_group'):
		url = base_path + '/groups/' + settings['api.group'] + '/action'
	else:
		url = base_path + query['url']

	conn = httplib.HTTPConnection(settings['api.bridge_ip'])

	# import ipdb; ipdb.set_trace()
	conn.request(method, url, data)
