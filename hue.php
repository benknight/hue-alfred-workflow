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
// if ( ! $query ):
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
	// else:
	// 	$w->write($lights, 'lights');
	endif;
// else:
// 		$lights = $w->read('lights');
// endif;


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
		'arg' => api_arg(array(
			'url' => "/lights/$id/state",
			'data' => '{"on": false}'
		))
	));
	result(array(
		'title' => 'Turn On',
		'arg' => api_arg(array(
			'url' => "/lights/$id/state",
			'data' => '{"on": true}'
		))
	));
	result(array(
		'title' => 'Set Effect...',
		'valid' => 'no',
		'autocomplete' => "$id:effect:"
	));
	result(array(
		'title' => 'Set Brightness...',
		'valid' => 'no',
		'autocomplete' => "$id:bri:"
	));
	result(array(
		'title' => 'Set Color...',
		'valid' => 'no',
		'autocomplete' => "$id:color:"
	));
	result(array(
		'title' => 'Set Alert...',
		'valid' => 'no',
		'autocomplete' => "$id:alert:"
	));

elseif ( count($control) == 3 ):
	$id = $control[0];
	$partial_query = $control[2];
	if ( $control[1] == 'bri' ):
		result(array(
			'title' => "Set Brightness to {$control[2]}",
			'subtitle' => 'Set on a scale from 0 to 255, where 0 is off.',
			'arg' => api_arg(array(
				'url' => "/lights/$id/state",
				'data' => sprintf('{"bri": %d}', $control[2])
			))
		));
	elseif ( $control[1] == 'color' ):
		result(array('title' => 'Set Color to...'));
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

	endif;

else:
	$partial_query = $query;
	result(array(
		'title' => 'Lights',
		'subtitle' => 'Set the state for a specific bulb.',
		'valid' => 'no',
		'autocomplete' => 'lights'
	));
	result(array(
		'title' => 'Turn all lights off',
		'arg' => api_arg(array(
			'url' => "/groups/$group/action",
			'data' => '{"on": false}'
		))
	));
	result(array(
		'title' =>'Turn all lights on',
		'arg' => api_arg(array(
			'url' => "/groups/$group/action",
			'data' => '{"on": true}'
		))
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
		'icon' => 'icons/popcorn.png'
	));
	result(array(
		'title' => 'Concentrate',
		'valid' => 'no'
	));
	result(array(
		'title' => 'Energize',
		'valid' => 'no'
	));
	result(array(
		'title' => 'Relax',
		'valid' => 'no'
	));
endif;

// TODO: Filter by partial query.

echo $w->toxml($results);
return;
