<?php

require_once('workflows.php');
$w = new Workflows();

$query = $argv[1];
$control = explode(':', $query);
$results = array();


/** Convenience Functions */

function result($r) {
    global $results;
    if ( ! isset($r['icon']) ):
        $r['icon'] = 'icon.png';
    endif;
    array_push($results, $r);
}

function color_picker($lid) {
    $rgba = `osascript -e 'tell application "Alfred 2"' -e 'activate' -e 'choose color default color {65535, 65535, 65535}' -e 'end tell'`;
    $hex = '';
    if ( $rgba ):
        $rgba = explode(',', $rgba);
        $rgb = array_slice($rgba, 0, 3);
        // Convert to hex
        foreach ( $rgb as $c ):
            $hex .= substr('0' . dechex(($c / 65535) * 255), -2);
        endforeach;
    endif;
    return `osascript -e 'tell application "Alfred 2" to search "hue $lid:color:$hex"'`;
}


/**
 * Cache a reference to lights.
 * This should be the only case when the settings file is read.
 */

if ( trim($query) === '' ):
    $username  = $w->get('api.username', 'settings.plist');
    $bridge_ip = $w->get('api.bridge_ip', 'settings.plist');
    $base_path = "/api/$username";

    // clear cache
    $lights = $w->write('', 'lights');
    $lights = $w->request(
        "http://$bridge_ip" . $base_path . '/lights',
        array(CURLOPT_CONNECTTIMEOUT => 3)
    );
    $lights = json_decode($lights, true);
    if ( $lights ):
        $w->write($lights, 'lights');
    endif;
else:
    $lights = $w->read('lights', true);
endif;

if ( ! $lights ):
    result(array(
        'title' => 'Bridge connection failed.',
        'subtitle' => 'Try running "setup-hue".',
        'valid' => 'no'
    ));
    echo $w->toxml($results);
    exit;
endif;


/** Generate Results */

if ( isset($lights[$query]) ):
    $lid = $query;
    $light = $lights[$lid];
    result(array(
        'uid' => "light_$lid",
        'title' => $light['name'],
        'subtitle'=> "blah",
        'valid' => 'no',
        'autocomplete' => "$lid:"
    ));

elseif ( count($control) == 2 ): // Light control index
    $lid = $control[0];
    $partial_query = $control[1];
    result(array(
        'title' => 'Turn off',
        'icon' => 'icons/switch.png',
        'autocomplete' => "$lid:off",
        'arg' => json_encode(array(
            'lid' => "$lid",
            'data' => array('on' => false)
        ))
    ));
    result(array(
        'title' => 'Turn on',
        'icon' => 'icons/switch.png',
        'autocomplete' => "$lid:on",
        'arg' => json_encode(array(
            'lid' => "$lid",
            'data' => array('on' => true)
        ))
    ));
    result(array(
        'title' => 'Set color...',
        'icon' => 'icons/colors.png',
        'valid' => 'no',
        'autocomplete' => "$lid:color:"
    ));
    result(array(
        'title' => 'Set effect...',
        'icon' => 'icons/effect.png',
        'valid' => 'no',
        'autocomplete' => "$lid:effect:"
    ));
    result(array(
        'title' => 'Set brightness...',
        'icon' => 'icons/sun.png',
        'valid' => 'no',
        'autocomplete' => "$lid:bri:"
    ));
    result(array(
        'title' => 'Set alert...',
        'icon' => 'icons/siren.png',
        'valid' => 'no',
        'autocomplete' => "$lid:alert:"
    ));
    if ( $lid !== 'all'):
        result(array(
            'title' => 'Rename...',
            'icon' => 'icons/cog.png',
            'valid' => 'no',
            'autocomplete' => "$lid:rename:"
        ));
    endif;

elseif ( count($control) == 3 ): // Specific light functions
    $lid = $control[0];
    $value = $control[2];

    if ( $control[1] == 'bri' ):
        result(array(
            'title' => "Set brightness to $value",
            'subtitle' => 'Set on a scale from 0 to 255, where 0 is off.',
            'icon' => 'icons/sun.png',
            'arg' => json_encode(array(
                'lid' => "$lid",
                'data' => array('bri' => (int) $value)
            ))
        ));
    elseif ( $control[1] == 'color' ):
        if ( $value == 'colorpicker' ):
            color_picker($lid);
        endif;
        result(array(
            'title' => "Set color to $value",
            'subtitle' => 'Accepts 6-digit hex colors or CSS literal color names (e.g. "blue")',
            'icon' => 'icons/colors.png',
            'arg' => json_encode(array(
                'lid' => "$lid",
                'color' => $value
            ))
        ));
        result(array(
            'title' => "Use color picker...",
            'valid' => 'no',
            'icon' => 'icons/eyedropper.png',
            'autocomplete' => "$lid:color:colorpicker"
        ));

    elseif ( $control[1] == 'effect' ):
        result(array(
            'title' => 'None',
            'icon' => 'icons/effect.png',
            'arg' => json_encode(array(
                'lid' => "$lid",
                'data' => array('effect' => 'none')
            ))
        ));
        result(array(
            'title' => 'Color loop',
            'icon' => 'icons/effect.png',
            'arg' => json_encode(array(
                'lid' => "$lid",
                'data' => array('effect' => 'colorloop')
            ))
        ));
    elseif ( $control[1] == 'alert' ):
        result(array(
            'title' => 'None',
            'subtitle' => 'Turn off any ongoing alerts',
            'icon' => 'icons/siren.png',
            'arg' => json_encode(array(
                'lid' => "$lid",
                'data' => array('alert' => 'none')
            ))
        ));
        result(array(
            'title' => 'Blink once',
            'icon' => 'icons/siren.png',
            'arg' => json_encode(array(
                'lid' => "$lid",
                'data' => array('alert' => 'select')
            ))
        ));
        result(array(
            'title' => 'Blink for 30 seconds',
            'icon' => 'icons/siren.png',
            'arg' => json_encode(array(
                'lid' => "$lid",
                'data' => array('alert' => 'lselect')
            ))
        ));

    elseif ( $control[1] == 'rename'):
        result(array(
            'title' => "Set light name to $value",
            'arg' => json_encode(array(
                'lid' => "$lid",
                'rename' => true,
                'data' => array('name' => $value)
            ))
        ));
    endif;

else: // Index
    $partial_query = $query;

    result(array(
        'uid' => "all_lights",
        'title' => 'All Lights',
        'subtitle' => 'Set state for all Hue lights in the set group.',
        'valid' => 'no',
        'autocomplete' => "all:"
    ));

    foreach ( $lights as $lid => $light ):
        result(array(
            'uid' => "light_$lid",
            'title' => $light['name'],
            'subtitle' => "ID: $lid, Brightness: 10%, Hue: 100deg",
            'valid' => 'no',
            'autocomplete' => "$lid:",
            'icon' => "$lid.png"
        ));
    endforeach;
endif;

function filter_by_partial_query($result) {
    global $partial_query;
    if ( isset($result['autocomplete']) ):
        return stripos($result['autocomplete'], $partial_query) !== false;
    endif;
    return false;
}

if ( ! empty($partial_query) ):
    $results = array_filter($results, 'filter_by_partial_query');
endif;

echo $w->toxml($results);
exit;
