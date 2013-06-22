# Hue Alfred 2 Workflow

Trigger:

	hue [<command> | <light>:<function>:<query>]

## Examples

	hue off
	hue on
	hue party
	hue concentrate|relax|energize*
	hue lights
	hue 2:off
	hue 1:effect:colorloop
	hue 1:effect:none
	hue 3:color:red

`*` = Not Implemented.

## TODO

* Implement color picker option.
* Support short hex colors? e.g. `#f00`. Eh, who cares.
* Allow users to save current state as a preset.
