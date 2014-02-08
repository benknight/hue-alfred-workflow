import urllib

import alp
import color_picker
import rgb_cie


class HueAlfredFilter:

    results = []

    def _load_lights_data_from_api(self):
	"""Downloads lights data and caches it locally.
	Also creates icon representations of each light's color.
	"""
	# Get settings
	settings = alp.readPlist('settings.plist')

	# Create a color converter
	converter = rgb_cie.Converter()

	# Build base uri for requests.
	request_base_uri = 'http://{0}/api/{1}'.format(
	    settings['api.bridge_ip'],
	    settings['api.username'],
	)

	r = alp.Request(request_base_uri + '/lights')
	r.download()
	lights = r.request.json()

	if settings.get('group') and settings['group'] is not 0:
	    lights = {lid: lights[lid] for lid in settings['group'].split(',')}

	alp.jsonDump(lights, alp.cache('lights.json'))

	for lid in lights.keys():
	    r = alp.Request('{0}/lights/{1}'.format(request_base_uri, lid))
	    r.download()
	    light_data = r.request.json()

	    alp.jsonDump(light_data, alp.cache('%s.json' % lid))

	    # Get icons
	    hex_color = converter.xyToHEX(
		light_data['state']['xy'][0],
		light_data['state']['xy'][1],
		float(light_data['state']['bri']) / 255
	    )

	    urllib.urlretrieve(
		'http://placehold.it/128.png/{0}/{0}'.format(hex_color),
		alp.local('%s.png' % lid)
	    )


    def get_lights(self, get_cached=False):
	"""Returns a list of light dictionaries containing light attributes and state, or None.

	Options:
	    get_cached - Read data from cached json files instead of querying the API.
	"""

	output = []

	if not get_cached:
	    self._load_lights_data_from_api()

	lights = alp.jsonLoad(alp.cache('lights.json'))

	if lights:
	    for lid in lights.keys():
		data = alp.jsonLoad(alp.cache('%s.json' % lid))
		output.append(dict(lid=lid, data=data))
	else:
	    output = None

	return output

    def show_preset_items(self):
	raise NotImplementedError()

    def get_results(self, args):
	query = args[0]
	control = query.split(':')

	# Query API at the beginning when the query is blank, otherwise use cache.
	if not query.strip():
	    lights = self.get_lights()
	else:
	    lights = self.get_lights(get_cached=True)

	if not lights:
	    self.results.append(alp.Item(
		title='Bridge connection failed.',
		subtitle='Try running "setup-hue"',
		valid=False,
	    ))

	elif len(control) > 1:

	    if len(control) is 2:
		pass
	    elif len(control) > 2:
		pass

	else:
	    if query is 'presets':
		self.results.append(alp.Item(
		    title='Save current state as preset...',
		    subtitle='',
		))
		self.show_preset_items()
	    else:
		self.results.append(alp.Item(
		    title='All lights',
		    subtitle='Set state for all Hue lights in the set group.',
		    valid=False,
		    icon='all.png',
		    autocomplete='all:',
		))
		for light in lights:
		    self.results.append(alt.Item(
			title=light['data']['name'],
			subtitle='ID: {lid}, Brightness: {bri}, Hue: {hue}'.format(
			    lid=light['lid'],
			    bri=light['data']['bri'],
			    hue=light['data']['hue'],
			),
			valid=False,
			icon='%s.png' % light['lid'],
			autocomplete='%s:' % light['lid'],
		    ))

	return alp.feedback(self.results)


if __name__ == '__main__':
    hue_filter = HueAlfredFilter()
    hue_filter.get_results(alp.args())
