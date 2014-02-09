import urllib
import yaml

import alp
import color_picker
import rgb_cie


class HueAlfredFilter:

    results = []

    def __init__(self):
	self.strings = yaml.load(file(alp.local('result_strings.yaml'), 'r'))

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
	    settings['api.username'],)

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
		float(light_data['state']['bri']) / 255)

	    urllib.urlretrieve(
		'http://placehold.it/128.png/{0}/{0}'.format(hex_color),
		alp.local('%s.png' % lid))


    def _get_lights(self, get_cached=False):
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

    def _show_preset_items(self):
	raise NotImplementedError()

    def _add_item(self, string_key, **kwargs):

	for k, v in self.strings[string_key]:
	    kwargs.setdefault(k, v)

	self.results.append(alp.Item(**kwargs))

    def get_results(self, args):
	query = args[0]
	control = query.split(':')

	# Query API at the beginning when the query is blank, otherwise use cache.
	if not query.strip():
	    lights = self._get_lights()
	else:
	    lights = self._get_lights(get_cached=True)

	if not lights:
	    self._add_item('bridge_failed')

	elif len(control) > 1:
	    lid = control[0]

	    if len(control) is 2:
		self._add_item('light_off',
		    autocomplete='%s:off' % lid,
		    arg=json.dumps({
			'lid': lid,
			'data': {'on': False},
		    }))
		self._add_item('light_on',
		    autocomplete='%s:on' % lid,
		    arg=json.dumps({
			'lid': lid,
			'data': {'on': True},
		    }))
		self._add_item('set_color',
		    autocomplete='%s:color:' % lid)
		self._add_item('set_effect',
		    autocomplete='%s:effect:' % lid)
		self._add_item('set_brightness',
		    autocomplete='%s:bri:'    % lid)
		self._add_item('set_alert',
		    autocomplete='%s:alert:'  % lid)
		self._add_item('light_rename',
		    autocomplete='%s:rename'  % lid)

	    elif len(control) >= 3:
		function = control[1]
		value = control[2]

		if function is 'color':
		    if value is 'colorpicker':
			color_picker.ColorPicker.color_picker()

		    self._add_item('set_color',
			arg=json.dumps({
			    'lid': lid,
			    'color': value,
			}))
		    self._add_item('color_picker',
			autocomplete='%s:color:colorpicker' % lid)

		elif function is 'bri':
		    self._add_item('set_brightness',
			arg=json.dumps({
			    'lid': lid,
			    'data': { 'bri': int(value) }
			}))

		elif function is 'effect':
		elif function is 'alert':
		elif function is 'rename':

	else:

	    if query is 'presets':
		self._add_item('save_preset')
		self._preset_items()

	    else:
		self._add_item('all_lights')

		for light in lights:
		    self.results.append(alp.Item(
			title=light['data']['name'],
			subtitle='ID: {lid}, Brightness: {bri}, Hue: {hue}'.format(
			    lid=light['lid'],
			    bri='{0:.0f}%'.format(float(light['data']['state']['bri']) / 255 * 100),
			    hue=light['data']['state']['hue'],
			),
			valid=False,
			icon=('%s.png' % light['lid'] if light['state'] is 'on' else 'icons/off.png'),
			autocomplete='%s:' % light['lid']
		    ))

		self._add_item('presets')

	return alp.feedback(self.results)


if __name__ == '__main__':
    hue_filter = HueAlfredFilter()
    hue_filter.get_results(alp.args())
