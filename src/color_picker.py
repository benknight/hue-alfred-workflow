import os


class OSXColorPicker:

    @staticmethod
    def color_picker(lid):
        rgba = os.system(r"""osascript -e 'tell application "Alfred 2"' -e 'activate' -e 'choose color default color {65535, 65535, 65535}' -e 'end tell'""")
        if not rgba:
            return False
        rgba = rgba.split(',')
        rgb = rgba[0:3]
        hexColor = color.rgbToHex(rgb[0], rgb[1], rgb[2])
        os.system(r"""osascript -e 'tell application "Alfred 2" to search "hue {0}:color:{1}"'""".format(lid, hexColor))
