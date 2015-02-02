## Changelog

#### 2.4:
* Support for dimmables and on/off lights: #10
* "Set color" how has "Random" option
* Hotkeys for any workflow action e.g. <lights:all:color:random>
* Code cleanup & refactors. All workflow logic moved into a logic package.

#### 2.3
* Bugfix: #17
* Adds the ability to set Hotkeys for user-created presets.
* Download link: http://goo.gl/85imtI
* Download link 2: http://goo.gl/O0Pk0f

#### 2.2
* Adds hotkeys for toggling all lights on and off, and setting all lights to random color.
* Adds help item to `hue` and `-hue` commands.
* Adds more helpful feedback text for light actions.
* Adds mechanism for checking if a new version exists.
* New icons & style tweaks.
* Made it possible to specify bridge IP as an argument to `-hue set-bridge`

<!-- 2.2 Download Link: http://goo.gl/aot0aU (Don't use! Has bugs! #17) -->

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