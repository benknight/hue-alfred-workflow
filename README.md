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

## Setup

Press the link button on the top of the bridge and use the `setup-hue` Alfred keyword within 30 seconds to automatically configure the workflow to work with the Hue bridge on the local network.

A group number can optionally be specified, e.g. `setup-hue 1` (defaults to `0`, which is all of the Hue bulbs).  Although much of the [Groups API](http://developers.meethue.com/2_groupsapi.html) remains undocumented, some developers have figured out [how to add and configure groups](http://www.everyhue.com/vanilla/discussion/57/api-groups/p1).

## TODO

* Allow users to save current state as a preset.
* Implement alert
