# Philips Hue Controller for Alfred 2

> Quickly and easily control Philips Hue lights with Alfred.

![Index](/screenshots/index.png)

## Installation

1. **[Download the workflow](http://goo.gl/Ofxh2A)**

2. After adding the workflow to Alfred, press the button on top of the Hue bridge and then run this command within 30 seconds:

```
-hue set-bridge
```

*Note: Unfortunately, Alfred has only made workflows available to users who have purchased [Powerpack](http://www.alfredapp.com/powerpack/).*

## Features

For convenience basic light control is available using the `hue` keyword, while all admin features are accessed using `-hue` keyword.

### Light control

Control the on/off state, color, and brightness for any individual light, or all lights at once.

![Light Control](/screenshots/light.png)

### Presets

Quickly save the current state as a named preset.

![Save Preset](/screenshots/save.png)

Then load them:

![Presets](/screenshots/presets.png)

### Easy light groups

Control or save the state of just subset of lights so that you can have group presets or avoid turning your roommate's light off by accident.

![Set Group](/screenshots/group.png)

This affects which lights will be changed when setting the state for "All lights" using the workflow.

To reset the group to all lamps again, use `-hue set-group 0`

### Hotkeys

![Hotkeys](/screenshots/hotkeys.png)

After installing the workflow you can edit it within the "Workflows" tab in the Alfred Preferences to set hotkey shortcuts for the following actions:

1. Toggle all lights on
2. Toggle all lights off
3. Set lamps to random colors.

These have to be set by the user.  Personally I use `Control+O`, `Control+Shift+O`, and `Control+R` for each, respectively, as I find there are no collisions here with existing shortcuts.

## Changelog

#### 2.2
* Adds hotkeys for toggling all lights on and off, and setting all lights to random color.
* Adds help item to `hue` and `-hue` commands.
* Adds more helpful feedback text for light actions.
* Adds mechanism for checking if a new version exists.
* New icons & style tweaks.
* Made it possible to specify bridge IP as an argument to `-hue set-bridge`
* Download link: http://goo.gl/Ofxh2A

#### 2.1.1
* Bugfix: workflow didn't work when there were things on the bridge that don't have color state (xy), such as dimmable plug-in units.
* Old download link: http://goo.gl/aot0aU

#### 2.1
* Using full state/datastore API for getting lights state instead of getting and storing every light individually.  This is backwards incompatible and won't work with old presets since it saves data differently.
* Old download link: http://goo.gl/o49DeD

#### 2.0
* Ported all workflow code to Python, built on top of alp.
* 'Lights' is now the index result set.
* New 'All Lights' option for setting the state for all lights in one command.
* Lights icons are now the actual current light color!
* Save presets states for all lights.
* Set which lights the workflow controls using easy group management via `-hue set-group`
* Set reminders (blink lights after some time delta).
* Old download link: http://goo.gl/6oZwOZ

#### 1.0
* Speed improvements
* Old download link: http://goo.gl/L3swBq

#### 0.9
* Initial Release
* Old download link: http://goo.gl/H26W2

## Thanks

Thanks to my testers & feature suggesters [Danny Ricciotti](https://github.com/objectiveSee) and [James Taylor](https://twitter.com/JamesCMTaylor)

Thanks to [Daniel Shannon](https://github.com/phyllisstein) for creating [alp](https://github.com/phyllisstein/alp), which removed all the grunt work in creating a Workflow.
