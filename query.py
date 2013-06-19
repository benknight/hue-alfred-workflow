import css_colors
import httplib
import json
import re
import rgb_cie

query = r'{query}'
rgb_cie_converter = rgb_cie.Converter()

short_color_re = re.compile(
	r'(?<!\w)([a-f0-9])([a-f0-9])([a-f0-9])', re.IGNORECASE)
long_color_re = re.compile(
	r'(?<!\w)([a-f0-9]){2}([a-f0-9]){2}([a-f0-9]){2}\b', re.IGNORECASE)

query = json.loads(query)

if query.get('_color'):
	color = query['_color']

	if css_colors.literals.get(color):
		color = css_colors.literals[color]

	color = color.lstrip('#')

	if not long_color_re.match(color):
		print 'Invalid color. Please use a 6-digit hex color.'

	query['data'] = json.dumps(
		{'xy': rgb_cie_converter.hexToCIE1931(color)}
	)

conn = httplib.HTTPConnection(query.get('host'))
conn.request(query.get('method'), query.get('url'), query.get('data'))