# Alfred 2 Workflow for Philips Hue

Trigger:

	hue [<command> | <light>:<function>:<query>]

## Examples

	hue off
	hue on
	hue party
	hue lights
	hue 2:off
	hue 1:effect:colorloop
	hue 1:effect:none
	hue 3:color:red

## Download

Download the extension here: http://goo.gl/H26W2

## Setup

![Setup](/screenshots/setup.png)

Press the link button on the top of the bridge and use the `setup-hue` Alfred keyword within 30 seconds to automatically configure the workflow to work with the Hue bridge on the local network.

A group id can optionally be specified, e.g. `setup-hue 1` (defaults to `0`, which is all of the Hue bulbs).  Check out the docs for the [Groups API](http://developers.meethue.com/2_groupsapi.html).

## Screenshots

Home (blank query):

![Home](/screenshots/home.png)

Lights:

![Lights](/screenshots/lights.png)

Light controls:

![Control](/screenshots/control.png)

Setting the color:

![Color](/screenshots/color.png)

## Roadmap

* Add the ability to save current state as a preset.
