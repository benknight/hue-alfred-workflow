# Philips Hue Controller for Alfred 2

> Quickly and easily control Philips Hue lights with Alfred.

![Index](/screenshots/index.png)

## Installation

*NOTE:* Unfortunately, Alfred Workflows require Powerpack (a paid feature).

Download the workflow here: http://goo.gl/7DI6GU

Press the button on top of the Hue bridge and then run this command within 30 seconds:

    -hue set-bridge

## Features

For convenience basic light control is available using the `hue` keyword, while all admin features are accessed using `-hue` keyword.

### Light control

Control the on/off state, color, and brightness for any individual light, or all lights at once.

![Light Control](/screenshots/light_control.png)

### Presets

Quickly save the current state as a named preset.

![Save Preset](/screenshots/save_preset.png)

Then load them:

![Presets](/screenshots/presets.png)

### Easy light groups

Control or save the state of just subset of lights so that you can have group presets or avoid turning your roommate's light off by accident.

![Set Group](/screenshots/set_group.png)

This affects which lights will be changed when setting the state for "All lights" using the workflow.

To reset the group to all lamps again, use `-hue set-group 0`

## Changelog

    2.0
    * Ported all workflow code to Python, built on top of alp.
    * 'Lights' is now the index result set.
    * New 'All Lights' option for setting the state for all lights in one command.
    * Lights icons are now the actual current light color!
    * Save presets states for all lights.
    * Set which lights the workflow controls using easy group management via `-hue set-group`
    * Set reminders (blink lights after some time delta).

    1.0
     * Speed improvements
     * Download link: http://goo.gl/L3swBq

    0.9
     * Initial Release
     * Download link: http://goo.gl/H26W2
     
## Thanks

Thanks to my testers & feature suggesters [Danny Ricciotti](https://github.com/objectiveSee) and [James Taylor](https://twitter.com/JamesCMTaylor)

Thanks to [Daniel Shannon](https://github.com/phyllisstein) for creating [alp](https://github.com/phyllisstein/alp), which removed all the grunt work in creating a Workflow.
