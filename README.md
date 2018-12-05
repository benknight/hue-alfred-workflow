# [Philips Hue][philips-hue] Controller for [Alfred][alfred]

> Quickly and easily control Philips Hue lights with Alfred. **[Download the workflow][download]**

<img src=/screenshots/index.png width=577 alt=Index>

## Features

### Control the state of lights and rooms

* Set brightness for lights or groups
* Set color for lights or groups (using CSS color names or HEX codes)
* Set colorloop effect on lights or groups
* Set reminders
* Set groups to custom scenes you've configured in the Philips Hue app
* Rename lights

|Light control|
|---|
|<img src=/screenshots/light.png width=577 alt="Control lights" border=1>|

|Group control|
|---|
|<img src=/screenshots/group.png width=577 alt="Control groups">|

_Note: `groups:0` as seen above is autocompleted by the workflow after selecting room name, or in this case "All lights".  Group '0' always refers to all lights. Each room name is associated with a specific group ID on the bridge.  Remember this ID if you wish to create hotkeys for rooms (see below)._

### Color Harmonies

This workflow has some bonus custom color science logic built in that let's you use color wheel relationships such as analogous, complementary, triad, etc. to set group colors.  Give it a try to see how it works:

|Set harmony|
|---|
|<img src=/screenshots/harmony.png width=577 alt="Color Harmony">|

### Hotkeys API

This workflow uses a special action string format that you can use to create a hotkey for any action you could otherwise perform using the `hue` keyword, which follows the following pattern:

```
<lights|groups>:<id>:<function>:<value>
```

Some example valid action strings are:

```
groups:0:on                    # Turn on all lights (note: Group "0" refers to all lights)
groups:0:off
groups:0:color:random          # Set all lights to a random color
groups:0:color:red
groups:1:set:<scene_name>      # Set a scene on group with ID "1"
lights:1:color:random
lights:1:color:bada55
lights:1:reminder:180          # 180 seconds
lights:1:bri:50                # 50 percent
lights:2:rename:Kitchen
lights:3:effect:colorloop      # Turn on colorloop effect on light with id "3"
```

#### Combine multiple commands into one hotkey

You can combine multiple commands into one hotkey by joining action strings with `|`, for example:

```
groups:0:on|lights:1:color:random
```

To create a new hotkey, open Alfred Preferences.app, go to Workflows and select the Philips Hue Controller workflow in the sidebar. In the main panel right click and select Triggers > Hotkey.  Set the text argument to the action string, then connect that to the same block as the other preloaded hotkeys.

To make this even easier, open `history.txt` inside of the Workflow's directory (right click Philips Hue Controller, select "Open in Finder") and there you can see history of all commands.  This makes creating a hotkey for setting a scene easier, for example, since scenes have long ID strings e.g. `ESyAHbZCG8RJTxi`.

## Setup & Installation

1. **[Download the workflow][download]**

2. The first time you run the workflow it will ask you to press the button on top of the Hue bridge then action the item to authorize the workflow to control your Hue lights:

|Setup|
|---|
|<img src=/screenshots/setup.png width=577 alt="Setup">|

The workflow automatically attempts to find the bridge on your local network.  You can also manually specify the bridge's IP address.  For example, if your bridge's IP is `192.168.1.103`:

```
hue 192.168.1.103
```

## Credits

Thanks to iconsphere, To Uyen, Setyo Ari Wibowo, Austin Condiff, H Alberto Gongora, Andreis Kirma, and Ananth from the Noun Project for icons.


[download]: https://github.com/benknight/hue-alfred-workflow/releases/download/v3.0/Philips.Hue.Controller.v3.0.alfredworkflow
[philips-hue]: https://www2.meethue.com/en-us
[alfred]: http://www.alfredapp.com
