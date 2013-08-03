import bpy
import sys
from Stitcher import Stitcher
import time
import shutil
from configparser import ConfigParser
from math import pi # don't remove -- needed in direction evaluation

#todo: untangle this
#todo: make a javascript app that has selectable animations and directions
#todo: 'shadow only' plane in blend file

class RenderScript():

    def __init__(self):

        bpy.ops.wm.open_mainfile(filepath="blend_files/player.blend")

        # has to be saved in the blender file
        # check to make sure it's not set to the default
        self.animation_name = bpy.data.scenes[0].name

        self.stitcher = Stitcher(self.animation_name)

        config = ConfigParser()
        config.read('config.ini')

        result = config.read('animation_config/' + self.animation_name + ".cfg")
        if ''.join(result) == '':
            sys.stderr.write("** could not read " + self.animation_name + ".cfg")
            self.animations = {}
        else:
            self.animations = config._sections['animations']

        self.ignored_actions = config.get('config', 'ignored_actions')

        self.directions = config._sections['directions']
        use_antialiasing = eval(config.get('output', 'use_antialiasing'))
        self.frame_step = int(config.get('output', 'frame_step'))

        self.grip = bpy.data.objects['Grip']
        self.grip.rotation_mode = 'XYZ'
        self.target = bpy.data.objects['Armature']
        bpy.data.scenes[0].render.use_antialiasing=use_antialiasing


    def render_position(self, action, direction, rotation, grip):

        grip.rotation_euler[2] = rotation
        filepath = 'tmp/' + action + '_' + direction + '_'
        bpy.data.scenes[0].render.filepath = filepath
        bpy.ops.render.render(animation=True)


    def main(self):

        start_time = time.time()
        for action in bpy.data.actions.keys():
            self.render(action)

        self.stitcher.save()
        shutil.rmtree('tmp')

        end = time.time()
        return end - start_time

    def render(self, action):

        if action in self.ignored_actions:
            return

        start, finish = bpy.data.actions[action].frame_range
        self.target.animation_data.action = bpy.data.actions[action]

        bpy.data.scenes[0].frame_start = start
        bpy.data.scenes[0].frame_end = finish - 1 # finish frame should be dupe of start frame
        bpy.data.scenes[0].frame_step = self.frame_step

        if self.animations[action]:
            keys = self.animations[action].split(",")
        else:
            keys = self.directions.keys()

        for key in keys:
            self.render_position(action, key, eval(self.directions[key]), self.grip)
            self.stitcher.add_to_sheet(action, key)


if __name__ == '__main__':
    renderScript = RenderScript()
    elapsed = renderScript.main()
    print("** finished in " + str(elapsed) + " seconds.")
