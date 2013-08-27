import os
import bpy
from CodeGenerator import CodeGenerator
from PIL import Image as pil_image

class Stitcher():

    def __init__(self, animation_name):
        self.code_gen = CodeGenerator(animation_name)
        self.animation_name = animation_name
        self.sheet = pil_image.new('RGBA', (1024,1024))
        self.frame_index = 0
        self.frame_count = 20

    def add_to_sheet(self, action, direction):
        start_frame = self.frame_index
        step = bpy.data.scenes[0].frame_step
        start, finish = bpy.data.actions[action].frame_range

        for frame_id in range(int(start), int(finish), int(step)):
            filepath = 'tmp/' + action + '_' + direction + '_' + str(frame_id).zfill(4) + '.png'
            frame = pil_image.open(filepath, "r")
            x = self.frame_index%16 * 64
            y = int(self.frame_index/16) * 64
            x2 = x + 64
            y2 = y + 64
            self.sheet.paste(frame, (x,y,x2,y2))
            self.frame_index += 1

        self.code_gen.add_frames(action, direction, start_frame, self.frame_index)

    def get_step_count(self, action, direction):
        max_steps = 10
        if os.path.exists('tmp/' + action + '_' + direction + '_0001.png'):
            step_count = 1
            while step_count < max_steps:
                if os.path.exists('tmp/' + action + '_' + direction + '_' + str(step_count).zfill(4) + '.png'):
                    break
                step_count += 1
            return step_count - 1

    def save(self):
        self.sheet.save('output/images/' + self.animation_name + '.png', 'PNG')
        self.code_gen.save()


