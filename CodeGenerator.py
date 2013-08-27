__author__ = 'jkersey'
import json

class CodeGenerator():

    def __init__(self, animation_name):
        self.frames = {}
        self.animation_name = animation_name
        self.output_file = 'build/js/' + self.animation_name + ".js"

    def add_frames(self, action, direction, start_frame, end_frame):

        frame_numbers = []

        for number in range(start_frame, end_frame):
            frame_numbers.append(number)

        if not action in self.frames:
            self.frames[action] = {}

        self.frames[action][direction] = frame_numbers

    def save(self):

        model = {self.animation_name:self.frames}

        file = open(self.output_file, "w")
        file.write(json.dumps(model, sort_keys=True, separators=(',', ': ')))
        file.close()
