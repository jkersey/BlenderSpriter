from pathlib import Path

import bpy
import os
import json
import shutil
import sys

# "from math import pi" is needed for direction evaluation
from math import pi

import time
from configparser import ConfigParser


def check_blender():
    """
    Verify blender is on PATH. Exit with helpful message if not.

    NOTE: Call this from a launcher script *before* invoking Blender.
    Do not call from render.py's __main__ block — by the time Blender
    runs this script, the blender binary is already executing.
    """
    if shutil.which("blender") is None:
        print("Error: 'blender' not found on PATH.")
        print("Install Blender and make sure it's accessible from the terminal.")
        print("Download: https://www.blender.org/download/")
        sys.exit(1)


def load_config(config_path="config.ini"):
    """Load config file. Exit with helpful message if missing."""
    if not os.path.exists(config_path):
        print(f"Error: Config file not found: {config_path}")
        print("Copy config.ini.example to config.ini and edit it for your project.")
        sys.exit(1)
    config = ConfigParser()
    config.read(config_path)
    return config

# to run this:
# <blender> <file.blend> --background --python RenderScript.py

# expects to find an Armature object in the scene

# TODO: Add the name of the empty to the name of the rendered file
# TODO: Add a turnaround animation for the editor to use
# TODO: how does the Blender logging system work? Can I reduce the log level?


class RenderScript:

    def __init__(self):

        self._grip = None

        config = ConfigParser()
        config.read('config.ini')

        self.log = []

        # self.objs: bpy.types.bpy_prop_collection = bpy.data.objects
        self.objs = bpy.data.objects

        # For when we're dumping everything into one directory
        self.file_increment = 0

        # Locations within the file that have things to render
        self.stations = self.get_stations()

        self.ignore_actions = config.get('config', 'ignore_actions').split(",")

        self.directions = dict(config.items('directions'))
        self.frame_step = int(config.get('output', 'frame_step'))
        self.output_path = str(config.get('output', 'output_path'))

        self.target = self.objs.get('Armature')

        filename = bpy.path.display_name_from_filepath(bpy.context.blend_data.filepath)
        if os.path.isfile(bpy.path.abspath("//") + "/" + filename + ".json"):
            print("***** Config file exists")
        else:
            print("***** no config file exists")

        self.skins = [f for f in os.listdir(bpy.path.abspath("//")) if f.endswith(".png")]
        print(bpy.path.abspath("//"))
        print(self.skins)

    @property
    def grip(self):
        if not self._grip:
            self._grip = self.objs.get("Grip")

        if not self._grip:
            self._grip = self.add_grip()
            self.parent_lamps(self._grip)
            self.parent_cameras(self._grip)

            self._grip.rotation_mode = 'XYZ'

        return self._grip

    def add_grip(self):
        print("Making a grip")
        grip = self.objs.new("Grip", None)
        bpy.context.scene.objects.link(grip)
        return grip

    def parent_lamps(self, grip):
        lamps = [x for x in self.objs if (x.type == 'LAMP')]

        for lamp in lamps:
            print("Parenting a lamp.")
            print("Type:" + str(lamp.data.type))
            print("Location: " + str(lamp.location))
            print("Rotation: " + str(lamp.rotation_euler))
            print("Scale: " + str(lamp.scale))
            # intensity is different per renderer
            lamp.parent = grip

    def parent_cameras(self, grip):
        cameras = [x for x in self.objs if (x.type == 'CAMERA')]
        for camera in cameras:
            print("Parenting a camera")
            print("Type:" + str(camera.data.type))
            print("Location: " + str(camera.location))
            print("Rotation: " + str(camera.rotation_euler))
            print("Scale: " + str(camera.scale))
            camera.parent = grip

    def get_stations(self):

        # Get all of the 'EMPTY' objects except for the Grip
        stations = [x for x in self.objs if (x.type == 'EMPTY' and x.name != 'Grip')]

        stations.sort(key=lambda x: x.name)

        # Look for an empty at the origin.
        # If there isn't one, add the grip to the list of stuff to render
        for station in stations:
            if station.location.x == 0 and station.location.y == 0:
                return stations

        return [self.grip] + stations

    def render_position(self, action, direction, rotation, grip, output_path, station_name, skin_name):

        filename = bpy.path.display_name_from_filepath(bpy.context.blend_data.filepath) + "_" + skin_name

        grip.rotation_euler[2] = rotation

        if grip.location.x == 0 and grip.location.y == 0:
            loc_string = "origin"
        else:
            loc_string = station_name

        suffix = ""

        if action == 'static':
            full_path = output_path + os.sep + filename + os.sep
            suffix = str(self.file_increment).zfill(2)
            self.file_increment += 1
        else:
            full_path = output_path + os.sep + filename + os.sep + loc_string + os.sep + action + os.sep + direction + os.sep

        # self.log.append("Full path: " + full_path)

        if not os.path.exists(full_path):
            # self.log.append("Path does not exist, creating...")
            os.makedirs(full_path)

        for f in Path(full_path).glob('*.png'):
            f.unlink()

        bpy.data.scenes[0].render.filepath = full_path + suffix
        bpy.ops.render.render(animation=True)

    def dump_log(self):
        for line in self.log:
            print(line)

    def main(self):

        start_time = time.time()
        print(bpy.data.images.keys())
        for skin in self.skins:
            bpy.data.images["default.png"].filepath = "//" + skin
            skin_name = skin.split(".")[0]

            for station in self.stations:
                self.log.append(":: Rendering " + station.name)
                self.grip.location.x = station.location.x
                self.grip.location.y = station.location.y
                self.log.append(":: Actions: " + str(bpy.data.actions.keys()))
                for action in bpy.data.actions.keys():
                    self.log.append(":: Rendering: " + action)
                    self.render(action, station.name, skin_name)

        end = time.time()
        return end - start_time

    def render(self, action, station_name, skin_name):

        if action in self.ignore_actions:
            self.log.append("Ignoring " + action + " by rule in config.ini.")
            return

        if "." in action:
            self.log.append("Ignoring " + action + " because it should've been deleted.")
            return

        start, finish = bpy.data.actions[action].frame_range
        if self.target:
            self.target.animation_data.action = bpy.data.actions[action]
        bpy.data.scenes[0].frame_start = int(start)
        bpy.data.scenes[0].frame_end = int(finish) - 1  # finish frame should be dupe of start frame
        bpy.data.scenes[0].frame_step = self.frame_step

        direction_overrides = station_name.split("_")[1:]

        if direction_overrides:
            directions = direction_overrides
        else:
            directions = self.directions.keys()

        self.log.append("Got : " + str(directions) + ".")
        for key in directions:
            self.log.append("Rendering " + key + ".")
            self.render_position(action, key, eval(self.directions[key]), self.grip, self.output_path, station_name, skin_name)


if __name__ == '__main__':
    renderScript = RenderScript()
    elapsed = renderScript.main()
    renderScript.dump_log()
    print("finished in " + str(elapsed) + " seconds.")
