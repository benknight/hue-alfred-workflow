<?php

require_once('workflows.php');
$w = new Workflows();

// Make sure settings file exists.
exec('touch settings.plist');

// Send request to Portal API to discover bridges on the local network.
$bridges = $w->request('http://www.meethue.com/api/nupnp');
$bridges = json_decode($bridges, true);

if ( empty($bridges) ):
	die('No bridge found on your network.');
endif;

$bridge_ip = $bridges[0]['internalipaddress'];
$w->set('api.bridge_ip', $bridge_ip, 'settings.plist');

// Create API user for this workflow.
$resp = $w->request("http://$bridge_ip/api", array(
	CURLOPT_POST => true,
	CURLOPT_POSTFIELDS => array('devicetype' => 'Alfred')
));

$resp = json_decode($resp, true);

if ( isset($resp[0]['error']) ):
	die('API access denied. The link button on the bridge must be pressed and this command executed within 30 seconds.');
endif;

$username = $resp[0]['success']['username'];

$w->set('api.username', $username, 'settings.plist');

echo 'Success!';