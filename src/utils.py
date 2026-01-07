#!/usr/bin/env python3
# encoding: utf-8

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

import colorsys
import re

import png
import requests
import urllib3

import colors
from css_colors import CSS_LITERALS as css_colors
from workflow import Workflow

# Suppress SSL warnings for self-signed Hue bridge certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

workflow = Workflow()


def search_for_bridge(timeout=3):
    """Searches for a bridge on the local network and returns the IP if it
    finds one."""
    try:
        r = requests.get('https://discovery.meethue.com', timeout=timeout)
        r.raise_for_status()  # Raise an exception for bad status codes
        bridges = r.json()

        if not isinstance(bridges, list):
            workflow.logger.error('Discovery service returned unexpected format: %s', type(bridges))
            return None

        if len(bridges) > 0:
            # Log all discovered bridges for debugging
            workflow.logger.info('Found %d bridge(s): %s', len(bridges), [b.get('internalipaddress', 'Unknown IP') for b in bridges if isinstance(b, dict)])

            # Return the first bridge's IP
            first_bridge = bridges[0]
            if isinstance(first_bridge, dict) and 'internalipaddress' in first_bridge:
                return first_bridge['internalipaddress']
            else:
                workflow.logger.error('First bridge entry missing internalipaddress: %s', first_bridge)
                return None
        else:
            workflow.logger.info('No bridges found via discovery service')
            return None
    except requests.exceptions.RequestException as e:
        workflow.logger.error('Failed to contact discovery service: %s', str(e))
        return None
    except (ValueError, KeyError) as e:
        workflow.logger.error('Failed to parse discovery response: %s', str(e))
        return None


def load_full_state(timeout=3):
    """Downloads full state and caches it locally."""
    # Requests is an expensive import so we only do it when necessary.
    # Use HTTPS with verify=False for Hue Bridge Pro compatibility (self-signed cert)
    r = requests.get(
        'https://{0}/api/{1}'.format(
            workflow.settings['bridge_ip'],
            workflow.settings['username'],
        ),
        timeout=timeout,
        verify=False,
    )

    data = r.json()

    # Handle cases where API returns error response as list instead of dict
    if isinstance(data, list) and len(data) > 0:
        # Check if this is an error response
        if isinstance(data[0], dict) and 'error' in data[0]:
            # Log the error for debugging
            workflow.logger.error('Bridge API error: %s', data[0]['error'].get('description', 'Unknown error'))
            raise Exception('Bridge returned error: {}'.format(data[0]['error'].get('description', 'Unknown error')))
        # If it's a list but not an error, this might be an unexpected format
        workflow.logger.warning('Bridge returned unexpected list format, attempting to use first element')
        data = data[0] if data else {}

    # Validate that we have the expected structure
    if not isinstance(data, dict):
        workflow.logger.error('Bridge returned unexpected data format: %s', type(data))
        raise Exception('Bridge returned unexpected data format')

    if 'lights' not in data:
        workflow.logger.error('Bridge response missing lights data. Response keys: %s', list(data.keys()))
        raise Exception('Bridge response missing lights data')

    workflow.store_data('full_state', data)


def create_light_icon(lid, light_data):
    """Creates a 1x1 PNG icon of light's RGB color and saves it to the local dir.
    """
    # Create a color converter & helper
    converter = colors.Converter()

    # Set color based on the type of light
    # See: http://www.developers.meethue.com/documentation/supported-lights
    if light_data['state'].get('xy'):
        rgb_value = converter.xy_to_rgb(light_data['state']['xy'][0], light_data['state']['xy'][1])
    elif light_data['state'].get('bri'):
        rgb_value = colorsys.hsv_to_rgb(0, 0, float(light_data['state']['bri']) / 255)
        rgb_value = tuple([int(255 * x) for x in rgb_value])
    else:
        rgb_value = (255, 255, 255) if light_data['state']['on'] else (0, 0, 0)

    f = open('icons/%s.png' % lid, 'wb')
    w = png.Writer(1, 1, greyscale=False)
    w.write(f, [rgb_value])
    f.close()


def get_lights(from_cache=False):
    """Returns a dictionary of lid => data, or None if no lights data is in the cache.
    Returns None if there are issues connecting to the bridge.

    Options:
        from_cache - Read data from cached json files instead of querying the API.
    """
    if not from_cache:
        try:
            try:
                load_full_state()
            except Exception:
                try:
                    bridge_ip = search_for_bridge()
                    if not bridge_ip:
                        return None
                    workflow.settings['bridge_ip'] = bridge_ip
                    load_full_state()
                except Exception:
                    return None
        except TypeError:
            return None

    data = workflow.stored_data('full_state')

    # Additional safety check for data structure
    if not isinstance(data, dict):
        workflow.logger.error('Stored full_state data is not a dictionary: %s', type(data))
        return None

    if 'lights' not in data:
        workflow.logger.error('Stored full_state data missing lights key. Available keys: %s', list(data.keys()) if isinstance(data, dict) else 'Not a dict')
        return None

    lights = data['lights']

    if not isinstance(lights, dict):
        workflow.logger.error('Lights data is not a dictionary: %s', type(lights))
        return None

    # Filter only lights that have a on/off state
    # This prevents issues with Deconz and Homekit hue bridges which set their config on a light
    filtered_lights = {
        lid: light for lid, light in lights.items()
        if 'state' in lights[lid] and 'on' in lights[lid]['state']
    }

    if not from_cache:
        # Create icon for lights
        for lid, light_data in filtered_lights.items():
            create_light_icon(lid, light_data)

    return filtered_lights


def get_groups():
    data = workflow.stored_data('full_state')

    # Additional safety check for data structure
    if not isinstance(data, dict):
        workflow.logger.error('Stored full_state data is not a dictionary: %s', type(data))
        return None

    if 'groups' not in data:
        workflow.logger.error('Stored full_state data missing groups key. Available keys: %s', list(data.keys()) if isinstance(data, dict) else 'Not a dict')
        return None

    try:
        groups = data['groups']
        if not isinstance(groups, dict):
            workflow.logger.error('Groups data is not a dictionary: %s', type(groups))
            return None
        return {gid: group for gid, group in groups.items()}
    except (TypeError, AttributeError) as e:
        workflow.logger.error('Error processing groups data: %s', str(e))
        return None


def get_group_lids(group_id):
    if group_id == '0':
        lights = get_lights(from_cache=True)
        if lights is None:
            return []
        return list(lights.keys())
    else:
        groups = get_groups()
        if groups is None:
            return []
        group = groups.get(group_id)
        if group is None or not isinstance(group, dict) or 'lights' not in group:
            workflow.logger.error('Group %s not found or missing lights data', group_id)
            return []
        return group['lights']


def get_scenes(group_id):
    data = workflow.stored_data("full_state")

    # Additional safety check for data structure
    if not isinstance(data, dict):
        workflow.logger.error('Stored full_state data is not a dictionary: %s', type(data))
        return {}

    # check if this is deconz, scenes are stored per group
    # can this be done elsewhere?
    is_deconz = False
    try:
        if data.get("config", {}).get("modelid") == "deCONZ":
            is_deconz = True
    except:
        # not sure if hue also returns config/modelid
        pass

    if is_deconz:
        workflow.logger.debug("This is deconz")
        # Not sure if "All lights" always has id 0
        if group_id == "0":
            return {}

        # Safety check for groups data
        if "groups" not in data or group_id not in data["groups"]:
            workflow.logger.error('Group %s not found in deconz bridge data', group_id)
            return {}

        group_data = data["groups"][group_id]
        if not isinstance(group_data, dict) or "scenes" not in group_data:
            workflow.logger.error('Group %s missing scenes data in deconz bridge', group_id)
            return {}

        scenes = group_data["scenes"]
        workflow.logger.debug(scenes)
        # in deconz, scenes are stored a list, convert to dict
        if isinstance(scenes, list):
            return {scene["id"]: scene for scene in scenes if isinstance(scene, dict) and "id" in scene}
        else:
            workflow.logger.error('deconz scenes data is not a list: %s', type(scenes))
            return {}
    else:
        # it's probably a hue
        if "scenes" not in data:
            workflow.logger.error('Hue bridge data missing scenes key')
            return {}

        scenes = data["scenes"]
        if not isinstance(scenes, dict):
            workflow.logger.error('Hue scenes data is not a dictionary: %s', type(scenes))
            return {}

        try:
            lids = get_group_lids(group_id)
            if lids is None:
                return {}

            return {
                id: scene
                for id, scene in scenes.items()
                if isinstance(scene, dict) and
                   "lights" in scene and "name" in scene and "version" in scene and
                   (set(scene["lights"]) == set(lids) and scene["name"] != "Off")
                   and scene["version"] >= 2
            }
        except Exception as e:
            workflow.logger.error('Error processing hue scenes: %s', str(e))
            return {}


def get_color_value(color):
    """Processes and returns a valid hex color value.
    Raises error if 'color' is invalid.
    """
    hex_color_re = re.compile(
        r'(?<!\w)([a-f0-9]){2}([a-f0-9]){2}([a-f0-9]){2}\b',
        re.IGNORECASE
    )

    if color in css_colors:
        color = css_colors[color]

    color = color.lstrip('#')

    if not hex_color_re.match(color):
        raise ValueError

    return color


def is_valid_color(color):
    try:
        get_color_value(color)
        return True
    except ValueError:
        return False
