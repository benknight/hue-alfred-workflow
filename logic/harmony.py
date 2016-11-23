from __future__ import division

import math

from .packages.colour import Color


MODES = (
    'analogous',
    'complementary',
    'split_complementary',
    'triad',
    'tetrad',
)


def map_range(value, from_lower, from_upper, to_lower, to_upper):
    return (to_lower + (value - from_lower) * ((to_upper - to_lower) / (from_upper - from_lower)))


def artistic_to_scientific_smooth(hue):
    return (
        hue * (35 / 60) if hue < 60
        else map_range(hue, 60, 122, 35, 60) if hue < 122
        else map_range(hue, 122, 165, 60, 120) if hue < 165
        else map_range(hue, 165, 218, 120, 180) if hue < 218
        else map_range(hue, 218, 275, 180, 240) if hue < 275
        else map_range(hue, 275, 330, 240, 300) if hue < 330
        else map_range(hue, 330, 360, 300, 360))


def scientific_to_artistic_smooth(hue):
    return (
        hue * (60 / 35) if hue < 35
        else map_range(hue, 35, 60, 60, 122) if hue < 60
        else map_range(hue, 60, 120, 122, 165) if hue < 120
        else map_range(hue, 120, 180, 165, 218) if hue < 180
        else map_range(hue, 180, 240, 218, 275) if hue < 240
        else map_range(hue, 240, 300, 275, 330) if hue < 300
        else map_range(hue, 300, 360, 330, 360))


def analogous(count, root='red', slices=8):
    part = 360 / slices
    c = Color(root)
    result = [c.hex_l]
    root_artistic_hue = scientific_to_artistic_smooth(c.hue * 360)
    for i in range(1, count):
        x = Color(root)
        distance = math.ceil(i / 2) * math.pow(-1, i + 1)
        new_hue = ((root_artistic_hue + distance * part + 720) % 360)
        x.hue = artistic_to_scientific_smooth(new_hue) / 360
        result.append(x.hex_l)
    return result


def complementary(count, root='red'):
    result = []
    c = Color(root)
    c.hue = artistic_to_scientific_smooth((scientific_to_artistic_smooth(c.hue * 360) + 180) % 360) / 360
    for i in range(count):
        result.append(c.hex_l if i % 2 else Color(root).hex_l)
    return result


def split_complementary(count, root='red'):
    result = []
    complement = complementary(2, root)[1]
    return [Color(root).hex_l] + analogous(count, complement, 12)[1:]


def triad(count, root='red'):
    result = [Color(root).hex_l]
    root_artistic_hue = scientific_to_artistic_smooth(Color(root).hue * 360)
    for i in range(1, count):
        c = Color(root)
        c.hue = artistic_to_scientific_smooth(((root_artistic_hue + (i % 3) * 120) % 360)) / 360
        result.append(c.hex_l)
    return result


def tetrad(count, root='red'):
    result = [Color(root).hex_l]
    root_artistic_hue = scientific_to_artistic_smooth(Color(root).hue * 360)
    for i in range(1, count):
        c = Color(root)
        c.hue = artistic_to_scientific_smooth(((root_artistic_hue + (i % 4) * 90) % 360)) / 360
        result.append(c.hex_l)
    return result
