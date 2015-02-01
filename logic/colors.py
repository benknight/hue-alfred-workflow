# -*- coding: utf-8 -*-
import math
import random
from collections import namedtuple


# color literals
CSS_LITERALS = {
    'aliceblue': '#f0f8ff',
    'antiquewhite': '#faebd7',
    'aqua': '#00ffff',
    'aquamarine': '#7fffd4',
    'azure': '#f0ffff',
    'beige': '#f5f5dc',
    'bisque': '#ffe4c4',
    'black': '#000000',
    'blanchedalmond': '#ffebcd',
    'blue': '#0000ff',
    'blueviolet': '#8a2be2',
    'brown': '#a52a2a',
    'burlywood': '#deb887',
    'cadetblue': '#5f9ea0',
    'chartreuse': '#7fff00',
    'chocolate': '#d2691e',
    'coral': '#ff7f50',
    'cornflowerblue': '#6495ed',
    'cornsilk': '#fff8dc',
    'crimson': '#dc143c',
    'cyan': '#00ffff',
    'darkblue': '#00008b',
    'darkcyan': '#008b8b',
    'darkgoldenrod': '#b8860b',
    'darkgray': '#a9a9a9',
    'darkgreen': '#006400',
    'darkkhaki': '#bdb76b',
    'darkmagenta': '#8b008b',
    'darkolivegreen': '#556b2f',
    'darkorange': '#ff8c00',
    'darkorchid': '#9932cc',
    'darkred': '#8b0000',
    'darksalmon': '#e9967a',
    'darkseagreen': '#8fbc8f',
    'darkslateblue': '#483d8b',
    'darkslategray': '#2f4f4f',
    'darkturquoise': '#00ced1',
    'darkviolet': '#9400d3',
    'deeppink': '#ff1493',
    'deepskyblue': '#00bfff',
    'dimgray': '#696969',
    'dodgerblue': '#1e90ff',
    'firebrick': '#b22222',
    'floralwhite': '#fffaf0',
    'forestgreen': '#228b22',
    'fuchsia': '#ff00ff',
    'gainsboro': '#dcdcdc',
    'ghostwhite': '#f8f8ff',
    'gold': '#ffd700',
    'goldenrod': '#daa520',
    'gray': '#808080',
    'green': '#008000',
    'greenyellow': '#adff2f',
    'honeydew': '#f0fff0',
    'hotpink': '#ff69b4',
    'indianred': '#cd5c5c',
    'indigo': '#4b0082',
    'ivory': '#fffff0',
    'khaki': '#f0e68c',
    'lavender': '#e6e6fa',
    'lavenderblush': '#fff0f5',
    'lawngreen': '#7cfc00',
    'lemonchiffon': '#fffacd',
    'lightblue': '#add8e6',
    'lightcoral': '#f08080',
    'lightcyan': '#e0ffff',
    'lightgoldenrodyellow': '#fafad2',
    'lightgreen': '#90ee90',
    'lightgrey': '#d3d3d3',
    'lightpink': '#ffb6c1',
    'lightsalmon': '#ffa07a',
    'lightseagreen': '#20b2aa',
    'lightskyblue': '#87cefa',
    'lightslategray': '#778899',
    'lightsteelblue': '#b0c4de',
    'lightyellow': '#ffffe0',
    'lime': '#00ff00',
    'limegreen': '#32cd32',
    'linen': '#faf0e6',
    'magenta': '#ff00ff',
    'maroon': '#800000',
    'mediumaquamarine': '#66cdaa',
    'mediumblue': '#0000cd',
    'mediumorchid': '#ba55d3',
    'mediumpurple': '#9370db',
    'mediumseagreen': '#3cb371',
    'mediumslateblue': '#7b68ee',
    'mediumspringgreen': '#00fa9a',
    'mediumturquoise': '#48d1cc',
    'mediumvioletred': '#c71585',
    'midnightblue': '#191970',
    'mintcream': '#f5fffa',
    'mistyrose': '#ffe4e1',
    'moccasin': '#ffe4b5',
    'navajowhite': '#ffdead',
    'navy': '#000080',
    'oldlace': '#fdf5e6',
    'olive': '#808000',
    'olivedrab': '#6b8e23',
    'orange': '#ffa500',
    'orangered': '#ff4500',
    'orchid': '#da70d6',
    'palegoldenrod': '#eee8aa',
    'palegreen': '#98fb98',
    'paleturquoise': '#afeeee',
    'palevioletred': '#db7093',
    'papayawhip': '#ffefd5',
    'peachpuff': '#ffdab9',
    'peru': '#cd853f',
    'pink': '#ffc0cb',
    'plum': '#dda0dd',
    'powderblue': '#b0e0e6',
    'purple': '#800080',
    'red': '#ff0000',
    'rosybrown': '#bc8f8f',
    'royalblue': '#4169e1',
    'saddlebrown': '#8b4513',
    'salmon': '#fa8072',
    'sandybrown': '#f4a460',
    'seagreen': '#2e8b57',
    'seashell': '#fff5ee',
    'sienna': '#a0522d',
    'silver': '#c0c0c0',
    'skyblue': '#87ceeb',
    'slateblue': '#6a5acd',
    'slategray': '#708090',
    'snow': '#fffafa',
    'springgreen': '#00ff7f',
    'steelblue': '#4682b4',
    'tan': '#d2b48c',
    'teal': '#008080',
    'thistle': '#d8bfd8',
    'tomato': '#ff6347',
    'turquoise': '#40e0d0',
    'violet': '#ee82ee',
    'wheat': '#f5deb3',
    'white': '#ffffff',
    'whitesmoke': '#f5f5f5',
    'yellow': '#ffff00',
    'yellowgreen': '#9acd32'
}


# Represents a CIE 1931 XY coordinate pair.
XYPoint = namedtuple('XYPoint', ['x', 'y'])


class ColorHelper:

    Red = XYPoint(0.675, 0.322)
    Lime = XYPoint(0.4091, 0.518)
    Blue = XYPoint(0.167, 0.04)

    def hexToRed(self, hex):
        """Parses a valid hex color string and returns the Red RGB integer value."""
        return int(hex[0:2], 16)

    def hexToGreen(self, hex):
        """Parses a valid hex color string and returns the Green RGB integer value."""
        return int(hex[2:4], 16)

    def hexToBlue(self, hex):
        """Parses a valid hex color string and returns the Blue RGB integer value."""
        return int(hex[4:6], 16)

    def hexToRGB(self, h):
        """Converts a valid hex color string to an RGB array."""
        rgb = (self.hexToRed(h), self.hexToGreen(h), self.hexToBlue(h))
        return rgb

    def rgbToHex(self, r, g, b):
        """Converts RGB to hex."""
        return '%02x%02x%02x' % (r, g, b)

    def randomRGBValue(self):
        """Return a random Integer in the range of 0 to 255, representing an RGB color value."""
        return random.randrange(0, 256)

    def crossProduct(self, p1, p2):
        """Returns the cross product of two XYPoints."""
        return (p1.x * p2.y - p1.y * p2.x)

    def checkPointInLampsReach(self, p):
        """Check if the provided XYPoint can be recreated by a Hue lamp."""
        v1 = XYPoint(self.Lime.x - self.Red.x, self.Lime.y - self.Red.y)
        v2 = XYPoint(self.Blue.x - self.Red.x, self.Blue.y - self.Red.y)

        q = XYPoint(p.x - self.Red.x, p.y - self.Red.y)
        s = self.crossProduct(q, v2) / self.crossProduct(v1, v2)
        t = self.crossProduct(v1, q) / self.crossProduct(v1, v2)

        return (s >= 0.0) and (t >= 0.0) and (s + t <= 1.0)

    def getClosestPointToLine(self, A, B, P):
        """Find the closest point on a line. This point will be reproducible by a Hue lamp."""
        AP = XYPoint(P.x - A.x, P.y - A.y)
        AB = XYPoint(B.x - A.x, B.y - A.y)
        ab2 = AB.x * AB.x + AB.y * AB.y
        ap_ab = AP.x * AB.x + AP.y * AB.y
        t = ap_ab / ab2

        if t < 0.0:
            t = 0.0
        elif t > 1.0:
            t = 1.0

        return XYPoint(A.x + AB.x * t, A.y + AB.y * t)

    def getClosestPointToPoint(self, xyPoint):
        # Color is unreproducible, find the closest point on each line in the CIE 1931 'triangle'.
        pAB = self.getClosestPointToLine(self.Red, self.Lime, xyPoint)
        pAC = self.getClosestPointToLine(self.Blue, self.Red, xyPoint)
        pBC = self.getClosestPointToLine(self.Lime, self.Blue, xyPoint)

        # Get the distances per point and see which point is closer to our Point.
        dAB = self.getDistanceBetweenTwoPoints(xyPoint, pAB)
        dAC = self.getDistanceBetweenTwoPoints(xyPoint, pAC)
        dBC = self.getDistanceBetweenTwoPoints(xyPoint, pBC)

        lowest = dAB
        closestPoint = pAB

        if (dAC < lowest):
            lowest = dAC
            closestPoint = pAC

        if (dBC < lowest):
            lowest = dBC
            closestPoint = pBC

        # Change the xy value to a value which is within the reach of the lamp.
        cx = closestPoint.x
        cy = closestPoint.y

        return XYPoint(cx, cy)

    def getDistanceBetweenTwoPoints(self, one, two):
        """Returns the distance between two XYPoints."""
        dx = one.x - two.x
        dy = one.y - two.y
        return math.sqrt(dx * dx + dy * dy)

    def getXYPointFromRGB(self, red, green, blue):
        """Returns an XYPoint object containing the closest available CIE 1931 coordinates
        based on the RGB input values."""

        r = ((red + 0.055) / (1.0 + 0.055))**2.4 if (red > 0.04045) else (red / 12.92)
        g = ((green + 0.055) / (1.0 + 0.055))**2.4 if (green > 0.04045) else (green / 12.92)
        b = ((blue + 0.055) / (1.0 + 0.055))**2.4 if (blue > 0.04045) else (blue / 12.92)

        X = r * 0.4360747 + g * 0.3850649 + b * 0.0930804
        Y = r * 0.2225045 + g * 0.7168786 + b * 0.0406169
        Z = r * 0.0139322 + g * 0.0971045 + b * 0.7141733

        cx = X / (X + Y + Z)
        cy = Y / (X + Y + Z)

        # Check if the given XY value is within the colourreach of our lamps.
        xyPoint = XYPoint(cx, cy)
        inReachOfLamps = self.checkPointInLampsReach(xyPoint)

        if not inReachOfLamps:
            xyPoint = self.getClosestPointToPoint(xyPoint)

        return xyPoint

    def getRGBFromXYAndBrightness(self, x, y, bri=1):
        """Inverse of `getXYPointFromRGB`. Returns (r, g, b) for given x, y values.
        Implementation of the instructions found on the Philips Hue iOS SDK docs: http://goo.gl/kWKXKl
        """
        # The xy to color conversion is almost the same, but in reverse order.
        # Check if the xy value is within the color gamut of the lamp.
        # If not continue with step 2, otherwise step 3.
        # We do this to calculate the most accurate color the given light can actually do.
        xyPoint = XYPoint(x, y)

        if not self.checkPointInLampsReach(xyPoint):
            # Calculate the closest point on the color gamut triangle
            # and use that as xy value See step 6 of color to xy.
            xyPoint = self.getClosestPointToPoint(xyPoint)

        # Calculate XYZ values Convert using the following formulas:
        Y = bri
        X = (Y / xyPoint.y) * xyPoint.x
        Z = (Y / xyPoint.y) * (1 - xyPoint.x - xyPoint.y)

        # Convert to RGB using Wide RGB D65 conversion
        r =  X * 1.612 - Y * 0.203 - Z * 0.302
        g = -X * 0.509 + Y * 1.412 + Z * 0.066
        b =  X * 0.026 - Y * 0.072 + Z * 0.962

        # Apply reverse gamma correction
        r, g, b = map(
            lambda x: (12.92 * x) if (x <= 0.0031308) else ((1.0 + 0.055) * pow(x, (1.0 / 2.4)) - 0.055),
            [r, g, b]
        )

        # Bring all negative components to zero
        r, g, b = map(lambda x: max(0, x), [r, g, b])

        # If one component is greater than 1, weight components by that value.
        max_component = max(r, g, b)
        if max_component > 1:
            r, g, b = map(lambda x: x / max_component, [r, g, b])

        r, g, b = map(lambda x: int(x * 255), [r, g, b])

        # Convert the RGB values to your color object The rgb values from the above formulas are between 0.0 and 1.0.
        return (r, g, b)


class Converter:

    color = ColorHelper()

    def hexToCIE1931(self, h):
        """Converts hexadecimal colors represented as a String to approximate CIE
        1931 coordinates. May not produce accurate values."""
        rgb = self.color.hexToRGB(h)
        return self.rgbToCIE1931(rgb[0], rgb[1], rgb[2])

    def rgbToCIE1931(self, red, green, blue):
        """Converts red, green and blue integer values to approximate CIE 1931
        x and y coordinates. Algorithm from:
        http://www.easyrgb.com/index.php?X=MATH&H=02#text2. May not produce
        accurate values.
        """
        point = self.color.getXYPointFromRGB(red, green, blue)
        return [point.x, point.y]

    def getCIEColor(self, hexColor=None):
        """Returns the approximate CIE 1931 x,y coordinates represented by the
        supplied hexColor parameter, or of a random color if the parameter
        is not passed. The point of this function is to let people set a lamp's
        color to any random color. Arguably this should be implemented elsewhere."""
        xy = []

        if hexColor:
            xy = self.hexToCIE1931(hexColor)

        else:
            r = self.color.randomRGBValue()
            g = self.color.randomRGBValue()
            b = self.color.randomRGBValue()
            xy = self.rgbToCIE1931(r, g, b)

        return xy

    def xyToHEX(self, x, y, bri=1):
        """Converts CIE 1931 x and y coordinates and brightness value from 0 to 1
        to a CSS hex color."""
        r, g, b = self.color.getRGBFromXYAndBrightness(x, y, bri)
        return self.color.rgbToHex(r, g, b)

    def xyToRGB(self, x, y, bri=1):
        """Converts CIE 1931 x and y coordinates and brightness value from 0 to 1
        to a CSS hex color."""
        r, g, b = self.color.getRGBFromXYAndBrightness(x, y, bri)
        return (r, g, b)
