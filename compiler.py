import getopt
import json
import os
import sys
from pathlib import Path
from pprint import pprint
import binascii
from configparser import ConfigParser

from PIL import Image
from PIL.Image import Resampling
from PIL.ImageDraw import ImageDraw, Draw

from constants import *

# TODO: Increment spritesheets
# TODO: Create a data structure for the image data
# TODO: Write exporters for that data structure (text, json, binary)
from skins import skin_encoding, animation_encoding, \
    direction_encoding


def ensure_output_dir(path):
    """Create output directory or exit with helpful message on permission failure."""
    try:
        os.makedirs(path, exist_ok=True)
    except PermissionError:
        print(f"Error: Cannot create output directory: {path}")
        print("Check that you have write permission to this location.")
        sys.exit(1)


class Compiler:

    def __init__(self, input_dir, output_dir, format='aseprite', mode=None):

        self.format = format
        self.mode = mode
        self.meta_hex = ""
        self.meta_csv = "id, skin, animation, direction, sheet id, x, y, w, h\n"
        self.meta_dict = {}
        self.aseprite_data = {}

        self.input_dir = input_dir
        self.output_dir = output_dir

        self.sheet_id = 1

        if self.format == 'json':
            self.sheet = Image.new(
                mode="RGBA",
                size=(int(SHEET_WIDTH), int(SHEET_HEIGHT))
            )
        print(f"reading from {input_dir}, writing to {output_dir}")

        self.process_images()

    def process_images(self):

        print("Processing images...")

        ensure_output_dir(self.output_dir)

        files = self.get_image_list()
        self.splice_all_images(files)

        if self.mode != 'godot':
            with open(os.path.join(self.output_dir, "file.bin"), "wb") as output_file:
                output_file.write(binascii.unhexlify(self.meta_hex))

            with open(os.path.join(self.output_dir, "file.csv"), "w") as csv_file:
                csv_file.write(self.meta_csv)

        if self.format == 'json':
            self.save_sheet()
            with open(os.path.join(self.output_dir, "file.json"), "w") as json_file:
                json_file.write(json.dumps(self.meta_dict))
        else:
            self.save_aseprite()

        print("Done.")

    def increment_sheet(self):
        self.save_sheet()
        draw = Draw(self.sheet)
        draw.rectangle((0, 0, SHEET_WIDTH, SHEET_HEIGHT), fill=(0, 0, 0, 0))
        self.sheet_id += 1

    def save_sheet(self):

        self.sheet.save(
            self.output_dir
            + os.sep
            + "spritesheet_"
            + str(self.sheet_id)
            + ".png"
        )

    def splice_all_images(self, files):
        for skin, stations in files.items():
            if self.format == 'aseprite':
                self.sheet = Image.new(mode="RGBA", size=(int(SHEET_WIDTH), int(SHEET_HEIGHT)))

            x = 0
            y = 0
            prev_max_y = 0
            max_y = 0

            for station, animations in stations.items():
                for anim, directions in animations.items():
                    for d, images in directions.items():
                        for image_path in images:
                            sprite = Image.open(image_path)
                            max_y = max(max_y, sprite.height)

                            if x + sprite.width > SHEET_WIDTH:
                                x = 0
                                y += prev_max_y

                            if y + sprite.height > SHEET_HEIGHT:
                                if self.format == 'json':
                                    self.increment_sheet()
                                x = 0
                                y = 0

                            self.place_image(sprite, x, y)
                            self.store_meta(skin, anim, d, x, y, sprite.width, sprite.height)
                            x = x + sprite.width

                        prev_max_y = max_y
                        max_y = 0

            if self.format == 'aseprite':
                self.sheet.save(os.path.join(self.output_dir, f'{skin}.png'))

    def store_meta(self, skin, anim, direction, x, y, w, h):
        if self.mode != 'godot':
            self.store_csv(skin, anim, direction, x, y, w, h)
            self.store_hex(skin, anim, direction, x, y, w, h)
        if self.format == 'json':
            self.store_dict(skin, anim, direction, x, y, w, h)
        else:
            self.store_aseprite(skin, anim, direction, x, y, w, h)

    def store_aseprite(self, skin, anim, direction, x, y, w, h):
        if skin not in self.aseprite_data:
            self.aseprite_data[skin] = {
                'frames': {},
                'frame_count': 0,
                'tags': [],
                'current_tag_name': None,
                'current_tag_from': 0,
            }

        data = self.aseprite_data[skin]
        tag_name = f"{anim}_{direction}"

        if data['current_tag_name'] is not None and data['current_tag_name'] != tag_name:
            data['tags'].append({
                'name': data['current_tag_name'],
                'from': data['current_tag_from'],
                'to': data['frame_count'] - 1,
                'direction': 'forward',
            })
            data['current_tag_from'] = data['frame_count']

        data['current_tag_name'] = tag_name

        frame_name = f"{skin}_{anim}_{direction}_{data['frame_count']}"
        data['frames'][frame_name] = {
            'frame': {'x': x, 'y': y, 'w': w, 'h': h},
            'rotated': False,
            'trimmed': False,
            'spriteSourceSize': {'x': 0, 'y': 0, 'w': w, 'h': h},
            'sourceSize': {'w': w, 'h': h},
            'duration': 100,
        }
        data['frame_count'] += 1

    def save_aseprite(self):
        for skin, data in self.aseprite_data.items():
            if data['current_tag_name'] is not None:
                data['tags'].append({
                    'name': data['current_tag_name'],
                    'from': data['current_tag_from'],
                    'to': data['frame_count'] - 1,
                    'direction': 'forward',
                })
                data['current_tag_name'] = None  # prevent double-close if called again

            aseprite_json = {
                'frames': data['frames'],
                'meta': {
                    'app': 'adventur_compiler',
                    'version': '1.0',
                    'image': f'{skin}.png',
                    'format': 'RGBA8888',
                    'size': {'w': SHEET_WIDTH, 'h': SHEET_HEIGHT},
                    'scale': '1',
                    'frameTags': data['tags'],
                    'layers': [],
                    'slices': [],
                },
            }

            out_path = os.path.join(self.output_dir, f'{skin}.jssn')
            with open(out_path, 'w') as f:
                json.dump(aseprite_json, f, indent=2)

    def store_csv(self, skin, anim, direction, x, y, w, h):
        id = str(skin_encoding.get(skin))
        self.meta_csv += ",".join([id, skin, anim, direction, str(self.sheet_id), str(x), str(y), str(w), str(h)]) + "\n"

    def store_dict(self, skin, anim, direction, x, y, w, h):
        id = skin_encoding.get(skin)
        if not self.meta_dict.get(skin):
            self.meta_dict[skin] = {}
            self.meta_dict[skin]["id"] = id
        if not self.meta_dict[skin].get(anim):
            self.meta_dict[skin][anim] = {}
        if not self.meta_dict[skin][anim].get(direction):
            self.meta_dict[skin][anim][direction] = []

        self.meta_dict[skin][anim][direction].append({
            "sheet_id": self.sheet_id,
            "x": x,
            "y": y,
            "w": w,
            "h": h,
        })

    def store_hex(self, skin, anim, direction, x, y, w, h):

        if "." in anim:
            return

        skin_id = skin_encoding.get(skin)
        anim_id = animation_encoding.get(anim)
        dir_id = direction_encoding.get(direction)

        if skin_id is None or anim_id is None or dir_id is None:
            print(f"WARNING: skipping unknown encoding for skin={skin!r} anim={anim!r} direction={direction!r}")
            return

        print(f"{skin} {anim} {direction} {self.sheet_id}")

        output = ""
        output += f'{skin_id:0{2}X}'
        output += f'{anim_id:0{2}X}'
        output += f'{dir_id:0{2}X}'
        output += f'{self.sheet_id:0{2}X}'

        # Swapping AABB to BBAA, the engine wants it that way?
        # Not sure if this will cause issues going to Windows
        output += f'{x:0{4}X}'[-2:] + f'{x:0{4}X}'[:2]
        output += f'{y:0{4}X}'[-2:] + f'{y:0{4}X}'[:2]

        output += f'{w:0{2}X}'
        output += f'{h:0{2}X}'

        self.meta_hex += output

    def get_image_list(self):
        page_path = self.input_dir

        images = {}

        skins = [f.path for f in os.scandir(page_path) if f.is_dir()]

        print(f"Got {len(skins)} skins.")

        for skin in skins:
            label = str(skin.split(os.sep)[-1])
            images[label] = {}
            print("SKIN:" + label)

            stations = [f.path for f in os.scandir(skin) if f.is_dir()]

            for station in stations:
                images[label][station] = {}
                print("STATION: " + station)

                animations = [f.path for f in os.scandir(station) if f.is_dir()]

                for animation in animations:
                    print("ANIMATION: " + animation)
                    images[label][station][animation.split(os.sep)[-1]] = {}
                    # print(animation.split(os.sep)[-1])
                    directions = [f.path for f in os.scandir(animation) if f.is_dir()]
                    # print("directions: " + ",".join([d.split(os.sep)[-1] for d in directions]))

                    for direction in directions:
                        print("DIRECTION: " + direction)
                        images[label][station][animation.split(os.sep)[-1]][direction.split(os.sep)[-1]] = sorted([f.path for f in os.scandir(direction) if f.is_file() and f.path.endswith("png")])

        return images

    def put_image(self, image_path, x, y, width, height):
        sprite = Image.open(image_path).convert("RGBA")
        sprite = sprite.resize((width, height), resample=Resampling.LANCZOS)
        self.sheet.paste(im=sprite, box=(x, y), mask=sprite)

    def place_image(self, image, x, y):
        image = image.convert("RGBA")
        self.sheet.paste(im=image, box=(x, y), mask=image)


def main(argv):
    config = ConfigParser()
    config.read('config.ini')

    input_dir = config.get('compiler', 'input_path')
    output_dir = config.get('compiler', 'output_path')
    mode = config.get('compiler', 'mode', fallback=None)

    fmt = 'aseprite'
    opts, _ = getopt.getopt(argv, 'f:', ['format='])
    for opt, arg in opts:
        if opt in ('-f', '--format'):
            fmt = arg

    if fmt not in ('aseprite', 'json'):
        print(f"Error: unknown format '{fmt}'. Valid values: aseprite, json", file=sys.stderr)
        sys.exit(1)

    Compiler(input_dir, output_dir, format=fmt, mode=mode)


if __name__ == "__main__":
    main(sys.argv[1:])
