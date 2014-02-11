import httplib
import json
import plistlib
import re
import sys

import rgb_cie
from css_colors import CSS_LITERALS


class HueAlfredAction:

    def _get_xy_color(self, color):
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

    def send_query(self, query):
	"""Simply decodes json query and makes the API call."""

	query = json.loads(query)
	settings = plistlib.readPlist('settings.plist')
	base_path = '/api/' + settings['api.username']
	method = 'PUT'

	# Set url
	if query.get('rename'):
	    url = base_path + '/lights/' + query['lid']
	else:
	    if query['lid'] == 'all':
		url = base_path + '/groups/' + settings['api.group'] + '/action'
	    else:
		url = base_path + '/lights/' + query['lid'] + '/state'

	# Set data
	if query.get('color'):
	    data = json.dumps({'xy': self._get_xy_color(query['color'])})
	else:
	    data = json.dumps(query['data'])

	conn = httplib.HTTPConnection(settings['api.bridge_ip'])

	conn.request(method, url, data)


if __name__ == '__main__':
    hue_action = HueAlfredAction()
    hue_action.send_query(sys.argv[0])
