<?php

require_once('workflows.php');
$w = new Workflows();

$user      = $w->get('api.user',   'settings.plist');
$group     = $w->get('api.group',  'settings.plist');
$bridge_ip = $w->get('api.server', 'settings.plist');
$base_path = "/api/$user";

$query = "{query}";
$control = explode(':', $query);
$results = array();

// Cache a reference to lights.
if ( trim($query) == '' ):
	$lights = $w->write('', 'lights');
	$lights = $w->request(
		"http://$bridge_ip" . $base_path . '/lights',
		array(CURLOPT_CONNECTTIMEOUT => 3)
	);
	$lights = json_decode($lights, true);
	if ( ! $lights ):
		result(array(
			'title' => 'Bridge connection failed.',
			'subtitle' => 'Use "set-hue-server" to set your bridge’s IP address.',
			'valid' => 'no'
		));
		echo $w->toxml($results);
		return;
	else:
		$w->write($lights, 'lights');
	endif;
else:
	$lights = $w->read('lights', true);
endif;


function result($r) {
	global $results;
	if ( ! isset($r['icon']) ):
		$r['icon'] = 'icon.png';
	endif;
	array_push($results, $r);
}

function api_arg($args) {
	global $bridge_ip, $base_path;
	$args['host'] = $bridge_ip;
	// PUT is the default HTTP method since most API calls use this.
	if ( ! isset($args['method']) ):
		$args['method'] = 'PUT';
	endif;
	$args['url'] = $base_path . $args['url'];
	return json_encode($args);
}

if ( $query == 'lights' ):
	foreach ( $lights as $id => $light ):
		result(array(
			'uid' => "light_$id",
			'title' => $light['name'],
			'valid' => 'no',
			'autocomplete' => "$id:"
		));
	endforeach;

elseif ( count($control) == 2 ):
	$id = $control[0];
	$partial_query = $control[1];
	result(array(
		'title' => 'Turn Off',
		'icon' => 'icons/switch.png',
		'arg' => api_arg(array(
			'url' => "/lights/$id/state",
			'data' => '{"on": false}'
		))
	));
	result(array(
		'title' => 'Turn On',
		'icon' => 'icons/switch.png',
		'arg' => api_arg(array(
			'url' => "/lights/$id/state",
			'data' => '{"on": true}'
		))
	));
	result(array(
		'title' => 'Set Color...',
		'icon' => 'icons/colors.png',
		'valid' => 'no',
		'autocomplete' => "$id:color:"
	));
	result(array(
		'title' => 'Set Effect...',
		'icon' => 'icons/effect.png',
		'valid' => 'no',
		'autocomplete' => "$id:effect:"
	));
	result(array(
		'title' => 'Set Brightness...',
		'icon' => 'icons/sun.png',
		'valid' => 'no',
		'autocomplete' => "$id:bri:"
	));
	result(array(
		'title' => 'Set Alert...',
		'icon' => 'icons/siren.png',
		'valid' => 'no',
		'autocomplete' => "$id:alert:"
	));
	result(array(
		'title' => 'Rename...',
		'icon' => 'icons/cog.png',
		'valid' => 'no',
		'autocomplete' => "$id:rename:"
	));

elseif ( count($control) == 3 ):
	$id = $control[0];
	$partial_query = $control[2];
	if ( $control[1] == 'bri' ):
		result(array(
			'title' => "Set Brightness to $partial_query",
			'subtitle' => 'Set on a scale from 0 to 255, where 0 is off.',
			'arg' => api_arg(array(
				'url' => "/lights/$id/state",
				'data' => sprintf('{"bri": %d}', $partial_query)
			))
		));
	elseif ( $control[1] == 'color' ):
		result(array(
			'title' => "Set Color to $partial_query",
			'arg' => api_arg(array(
				'url' => "/lights/$id/state",
				'data' => '',
				'_color' => $partial_query
			))
		));
	elseif ( $control[1] == 'effect' ):
		result(array(
			'title' => 'None',
			'arg' => api_arg(array(
				'url' => "/lights/$id/state",
				'data' => '{"effect": "none"}'
			))
		));
		result(array(
			'title' => 'Color Loop',
			'arg' => api_arg(array(
				'url' => "/lights/$id/state",
				'data' => '{"effect": "colorloop"}'
			))
		));
	elseif ( $control[1] == 'alert' ):

	elseif ( $control[1] == 'rename' ):
		result(array(
			'title' => "Set light name to $partial_query",
			'arg' => api_arg(array(
				'url' => "/lights/$id",
				'data' => sprintf('{"name": "%s"}', $partial_query)
			))
		));
	endif;

else:
	$partial_query = $query;
	result(array(
		'title' => 'Lights',
		'valid' => 'no',
		'autocomplete' => 'lights'
	));
	result(array(
		'title' => 'Turn all lights off',
		'icon' => 'icons/switch.png',
		'arg' => api_arg(array(
			'url' => "/groups/$group/action",
			'data' => '{"on": false}'
		))
	));
	result(array(
		'title' =>'Turn all lights on',
		'icon' => 'icons/switch.png',
		'arg' => api_arg(array(
			'url' => "/groups/$group/action",
			'data' => '{"on": true}'
		))
	));
	result(array(
		'title' => 'Concentrate',
		'valid' => 'no',
		'icon' => 'icons/yinyang.png'
	));
	result(array(
		'title' => 'Energize',
		'valid' => 'no',
		'icon' => 'icons/yinyang.png'
	));
	result(array(
		'title' => 'Relax',
		'valid' => 'no',
		'icon' => 'icons/yinyang.png'
	));
	result(array(
		'title' => 'Party',
		'subtitle' => 'Set all lights to color loop.',
		'icon' => 'icons/colors.png',
		'arg' => api_arg(array(
			'url' => "/groups/$group/action",
			'data' => '{"effect": "colorloop"}'
		))
	));
	result(array(
		'title' => 'Movie',
		'valid' => 'no',
		'icon' => 'icons/popcorn.png',
		'subtitle' => 'Set the lights to the minimum brightness.'
	));
endif;

// TODO: Filter by partial query.
// function filter_by_query($result) {
// 	return isset($result['autocomplete']) && stripos($result['autocomplete'], $partial_query) === 0;
// }

// if ( $partial_query ) {
// 	$results = array_filter($results, 'filter_by_query');
// }

echo $w->toxml($results);
return;
