# Philips Hue Controller for Alfred 2

> Quickly and easily control Philips Hue lights with Alfred.

![Index](/screenshots/index.png)
![Admin](/screenshots/admin.png)

## Installation

1. **[Download the workflow](http://goo.gl/85imtI)**

2. After adding the workflow to Alfred, press the button on top of the Hue bridge and then run this command within 30 seconds:

```
-hue set-bridge
```

This command attempts to find the bridge on your local network.  If it fails, you can specify the bridge's IP address.  For example, if your bridge's IP is `192.168.42.126`:

```
-hue set-bridge 192.168.42.126
```

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

This workflow uses a special action string format that you can use to create a hotkey for any action you can perform using the "hue" keyword.

Examples:

```
lights:all:off
lights:all:color:random
lights:1:reminder:180
presets:load:Red
```

You can turn any one of these into a hotkey by going to Alfred Preferences > Workflows, selecting the Philips Hue Controller workflow, and then adding a hotkey action from the dropdown (click the + icon and select Triggers > Hotkey).  You then set the text argument to the action string, and then connect that to the same block as the other preloaded hotkeys.

## Issues

If you're having issues feel free to contact me via Twitter at @babylemurman, email me at ben@benknight.me, or open an issue on this Github page.  I will try to get back to you within a day!

## Thanks

Thanks to [Daniel Shannon](https://github.com/phyllisstein) for creating [alp](https://github.com/phyllisstein/alp), which removed all the grunt work in creating a Workflow.
