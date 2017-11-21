# Philips Hue Controller for Alfred

> Quickly and easily control Philips Hue lights with Alfred.

<img src=/screenshots/index.png width=577 alt=Index>

## Installation

1. **[Download the workflow](https://github.com/benknight/hue-alfred-workflow/releases/latest)**

2. The first time you run the workflow it will ask you to press the button on top of the Hue bridge then action the item to authorize the workflow to control your Hue lights.  The workflow automatically attempts to find the bridge on your local network.  You can also manually specify the bridge's IP address.  For example, if your bridge's IP is `192.168.1.103`:

```
hue 192.168.1.103
```

## Features

### Control the state of lights and rooms

<img src=/screenshots/light.png width=577 alt="Control lights">

<img src=/screenshots/group.png width=577 alt="Control rooms">

### Color Harmonies

Use color wheel relationships such as analogous, complementary, triad, etc. to set room colors:

<img src=/screenshots/harmony.png width=577 alt="Color Harmony">

### Hotkeys

This workflow uses a special action string format that you can use to create a hotkey for any action you could otherwise perform using the `hue` keyword:

```
<lights|groups>:<id>:<function>:<value>
```

Examples:

```
groups:0:on                    # Group "0" refers to all lights
groups:0:off
groups:0:color:random
groups:0:color:red
groups:1:set:<preset id>       # Set a scene
lights:1:color:random
lights:1:color:bada55
lights:1:reminder:180          # 180 seconds
lights:1:bri:50                # 50 percent
lights:2:rename:Kitchen
lights:3:effect:colorloop
```

You can combine multiple commands into one hotkey by joining action strings with `|`, for example:

```
groups:0:on|lights:1:color:random
```

To create a new hotkey, open Alfred Preferences.app, go to Workflows and select the Philips Hue Controller workflow in the sidebar. In the main panel right click and select Triggers > Hotkey.  Set the text argument to the action string, then connect that to the same block as the other preloaded hotkeys.

To make this even easier, open `history.txt` inside of the Workflow's directory (right click Philips Hue Controller, select "Open in Finder") and there you can see history of all commands.  This makes creating a hotkey for setting a scene easier, for example, since scenes have long ID strings e.g. `ESyAHbZCG8RJTxi`.

# Credits

Thanks to iconsphere, To Uyen, Setyo Ari Wibowo, Austin Condiff, H Alberto Gongora, Andreis Kirma, and Ananth from the Noun Project for icons.
